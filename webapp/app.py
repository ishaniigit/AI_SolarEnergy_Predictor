# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from utils import build_features, get_feature_list

app = Flask(__name__)

# Load models and scaler
def load_models():
    models = {}
    try:
        models_dir = project_root / "models"
        
        # Check if models exist
        scaler_path = models_dir / "scaler.pkl"
        xgb_path = models_dir / "xgb_model.pkl"
        rf_path = models_dir / "rf_model.pkl"
        
        print(f"Looking for models in: {models_dir}")
        print(f"Scaler exists: {scaler_path.exists()}")
        print(f"RF model exists: {rf_path.exists()}")
        print(f"XGB model exists: {xgb_path.exists()}")
        
        if not scaler_path.exists():
            raise FileNotFoundError("Scaler not found - please run train.py first")
        if not rf_path.exists():
            raise FileNotFoundError("Random Forest model not found - please run train.py first")
        
        # Load scaler
        models['scaler'] = joblib.load(scaler_path)
        print("Scaler loaded successfully")
        
        # Try to load XGBoost first, fall back to Random Forest
        try:
            if xgb_path.exists():
                models['model'] = joblib.load(xgb_path)
                models['model_name'] = 'XGBoost'
                print("✓ XGBoost model loaded")
            else:
                raise FileNotFoundError("XGBoost not available")
        except (FileNotFoundError, ImportError):
            # Fall back to Random Forest
            models['model'] = joblib.load(rf_path)
            models['model_name'] = 'Random Forest'
            print("✓ Random Forest model loaded (fallback)")
            
        print(f"✓ Successfully loaded {models['model_name']} model and scaler")
        return models
        
    except Exception as e:
        print(f"Error loading models: {e}")
        return None

# Load models when app starts
models = load_models()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    if models is None:
        return jsonify({'error': 'Models not loaded. Please run train.py first.'}), 500
    
    try:
        # Get form data
        data = {
            'irradiation': float(request.form.get('irradiation', 0)),
            'ambient_temperature': float(request.form.get('ambient_temperature', 0)),
            'module_temperature': float(request.form.get('module_temperature', 0)),
            'hour': int(request.form.get('hour', 12)),
            'day': int(request.form.get('day', 1)),
            'month': int(request.form.get('month', 1))
        }
        
        print(f"Received prediction request: {data}")
        
        # Create feature array in correct order
        feature_names = models['scaler'].feature_names_in_
        feature_vector = np.zeros(len(feature_names))
        
        for i, feature in enumerate(feature_names):
            if feature in data:
                feature_vector[i] = data[feature]
            elif feature == 'dayofyear':
                # Approximate dayofyear from month and day
                feature_vector[i] = (data['month'] - 1) * 30 + data['day']
            elif feature in ['sin_hour', 'cos_hour']:
                # Calculate cyclical features
                if feature == 'sin_hour':
                    feature_vector[i] = np.sin(2 * np.pi * data['hour'] / 24)
                else:
                    feature_vector[i] = np.cos(2 * np.pi * data['hour'] / 24)
        
        print(f"Feature vector: {feature_vector}")
        
        # Scale features and predict
        scaled_features = models['scaler'].transform([feature_vector])
        prediction = models['model'].predict(scaled_features)[0]
        
        print(f"Prediction: {prediction}")
        
        return jsonify({
            'prediction': round(prediction, 2),
            'model_used': models['model_name']
        })
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/series')
def get_series():
    """Return data for chart - actual vs predicted for last 200 rows"""
    try:
        data_path = project_root / "data" / "Processed" / "cleaned_solar_data.csv"
        
        if data_path.exists() and models is not None:
            # Load and process actual data
            df = pd.read_csv(data_path)
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            if 'date_time' in df.columns and 'ac_power' in df.columns:
                df = build_features(df)
                feature_names = get_feature_list(df)
                
                # Get last 200 rows
                df_last = df.tail(200).copy()
                X_last = df_last[feature_names]
                
                # Scale and predict
                X_scaled = models['scaler'].transform(X_last)
                predictions = models['model'].predict(X_scaled)
                
                # Prepare response
                response_data = {
                    'timestamps': df_last['date_time'].tolist(),
                    'actual': df_last['ac_power'].tolist(),
                    'predicted': predictions.tolist()
                }
                return jsonify(response_data)
        
        # Fallback: generate dummy data
        return jsonify(generate_dummy_series())
        
    except Exception as e:
        print(f"Error generating series: {e}")
        return jsonify(generate_dummy_series())

def generate_dummy_series():
    """Generate dummy data for chart when real data is unavailable"""
    import random
    timestamps = [f"2024-01-{i:02d} 12:00" for i in range(1, 201)]
    base = 100
    actual = [base + random.uniform(-20, 20) for _ in range(200)]
    predicted = [val + random.uniform(-10, 10) for val in actual]
    
    return {
        'timestamps': timestamps,
        'actual': actual,
        'predicted': predicted
    }

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Project root: {project_root}")
    app.run(debug=True, host='127.0.0.1', port=5000)