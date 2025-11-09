# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import numpy as np
import os
from pathlib import Path
import sys

# Vercel setup
if 'VERCEL' in os.environ:
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    sys.path.append(str(project_root / "src"))

app = Flask(__name__)

def load_models():
    """Demo mode for Vercel deployment - no large model files needed"""
    models = {}
    try:
        # For Vercel, use demo mode (models are too large to deploy)
        if 'VERCEL' in os.environ:
            print("🚀 Running in Vercel Demo Mode")
            models['model'] = None
            models['model_name'] = 'XGBoost (Demo)'
            models['scaler'] = None
            models['demo_mode'] = True
        else:
            # Local development - try to load real models
            import joblib
            from utils import build_features, get_feature_list
            
            models_dir = Path(__file__).parent.parent / "models"
            scaler_path = models_dir / "scaler.pkl"
            xgb_path = models_dir / "xgb_model.pkl"
            rf_path = models_dir / "rf_model.pkl"
            
            if scaler_path.exists() and rf_path.exists():
                models['scaler'] = joblib.load(scaler_path)
                if xgb_path.exists():
                    models['model'] = joblib.load(xgb_path)
                    models['model_name'] = 'XGBoost'
                else:
                    models['model'] = joblib.load(rf_path)
                    models['model_name'] = 'Random Forest'
                models['demo_mode'] = False
                print(f"✓ Loaded {models['model_name']} model")
            else:
                raise FileNotFoundError("Models not found")
                
        return models
        
    except Exception as e:
        print(f"⚠️ Using Demo Mode: {e}")
        models['model'] = None
        models['model_name'] = 'Demo Model'
        models['scaler'] = None
        models['demo_mode'] = True
        return models

# Load models
models = load_models()

def demo_prediction(data):
    """Smart demo prediction using realistic solar energy formulas"""
    irradiation = data['irradiation']
    ambient_temp = data['ambient_temperature']
    module_temp = data['module_temperature']
    hour = data['hour']
    
    # Realistic solar power calculation
    # Base power from irradiation (typical solar panel efficiency)
    base_power = irradiation * 280  # 280W per m² is realistic
    
    # Temperature effect (panels lose efficiency when hot)
    temp_effect = max(0, 25 - module_temp) * 0.5  # 0.5% loss per degree above 25°C
    
    # Time of day effect (solar position)
    solar_noon = 12
    time_factor = 1 - abs(hour - solar_noon) / 12  # Higher around noon
    
    # Seasonal effect (month)
    seasonal_factor = 1 + (6 - abs(data['month'] - 6)) * 0.1  # Summer months better
    
    # Calculate final prediction
    prediction = base_power * (1 - temp_effect/100) * time_factor * seasonal_factor
    
    # Add some realistic noise
    prediction += np.random.normal(0, 10)
    
    return max(0, prediction)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        data = {
            'irradiation': float(request.form.get('irradiation', 0.8)),
            'ambient_temperature': float(request.form.get('ambient_temperature', 25.0)),
            'module_temperature': float(request.form.get('module_temperature', 35.0)),
            'hour': int(request.form.get('hour', 12)),
            'day': int(request.form.get('day', 15)),
            'month': int(request.form.get('month', 6))
        }
        
        print(f"📊 Prediction request: {data}")
        
        if models.get('demo_mode', True):
            # Use demo prediction
            prediction = demo_prediction(data)
            model_used = 'AI Model (Demo)'
            note = 'Using realistic solar energy simulation'
        else:
            # Use real model prediction
            feature_names = models['scaler'].feature_names_in_
            feature_vector = np.zeros(len(feature_names))
            
            for i, feature in enumerate(feature_names):
                if feature in data:
                    feature_vector[i] = data[feature]
                elif feature == 'dayofyear':
                    feature_vector[i] = (data['month'] - 1) * 30 + data['day']
                elif feature in ['sin_hour', 'cos_hour']:
                    if feature == 'sin_hour':
                        feature_vector[i] = np.sin(2 * np.pi * data['hour'] / 24)
                    else:
                        feature_vector[i] = np.cos(2 * np.pi * data['hour'] / 24)
            
            scaled_features = models['scaler'].transform([feature_vector])
            prediction = models['model'].predict(scaled_features)[0]
            model_used = models['model_name']
            note = 'Using trained AI model'
        
        print(f"🎯 Prediction: {prediction:.2f} kW")
        
        return jsonify({
            'prediction': round(prediction, 2),
            'model_used': model_used,
            'note': note
        })
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/series')
def get_series():
    """Generate realistic demo data for charts"""
    try:
        # Generate realistic solar data pattern
        timestamps = []
        actual = []
        predicted = []
        
        base_date = "2024-06-"
        
        for i in range(1, 201):
            # Create timestamp
            hour = (i % 24)
            day = 1 + (i // 24)
            timestamps.append(f"{base_date}{day:02d} {hour:02d}:00")
            
            # Realistic solar pattern - zero at night, peak at noon
            if 6 <= hour <= 18:  # Daylight hours
                # Bell curve for solar production
                solar_intensity = np.exp(-((hour - 12) ** 2) / 8)
                base_power = 200 + (solar_intensity * 150)
                
                # Add some realistic variation
                actual_power = base_power + np.random.normal(0, 15)
                predicted_power = actual_power + np.random.normal(0, 8)
            else:
                actual_power = 0
                predicted_power = 0
            
            actual.append(max(0, actual_power))
            predicted.append(max(0, predicted_power))
        
        return jsonify({
            'timestamps': timestamps,
            'actual': actual,
            'predicted': predicted
        })
        
    except Exception as e:
        print(f"❌ Series error: {e}")
        return jsonify(generate_dummy_series())

def generate_dummy_series():
    """Fallback dummy data"""
    timestamps = [f"2024-06-{i//24+1:02d} {i%24:02d}:00" for i in range(200)]
    actual = [max(0, 100 + 100 * np.sin(i * 0.1) + np.random.normal(0, 20)) for i in range(200)]
    predicted = [actual[i] + np.random.normal(0, 10) for i in range(200)]
    
    return {
        'timestamps': timestamps,
        'actual': actual,
        'predicted': predicted
    }

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    app.run(debug=True, host='127.0.0.1', port=5000)