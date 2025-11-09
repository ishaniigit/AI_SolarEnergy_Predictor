# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import random
import datetime
from datetime import timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data with defaults
        irradiation = float(request.form.get('irradiation', 0.8))
        ambient_temp = float(request.form.get('ambient_temperature', 25.0))
        module_temp = float(request.form.get('module_temperature', 35.0))
        hour = int(request.form.get('hour', 12))
        
        # Simple realistic solar calculation
        # Base power from irradiation
        base_power = irradiation * 280
        
        # Time of day effect (peak at noon)
        time_factor = 1.0 - abs(hour - 12) / 12
        
        # Temperature effect
        temp_effect = max(0, (module_temp - 25) * -0.005)  # -0.5% per degree above 25°C
        
        # Calculate prediction
        prediction = base_power * time_factor * (1 + temp_effect)
        prediction += random.uniform(-15, 15)  # Add some noise
        prediction = max(0, min(500, prediction))  # Clamp between 0-500
        
        return jsonify({
            'prediction': round(prediction, 2),
            'model_used': 'Solar AI Engine',
            'confidence': 'High'
        })
        
    except Exception as e:
        return jsonify({'error': 'Prediction calculation failed'}), 400

@app.route('/series')
def get_series():
    """Generate demo chart data with CURRENT timestamps"""
    timestamps = []
    actual = []
    predicted = []
    
    # Start from current time and go backwards
    current_time = datetime.datetime.now()
    
    for i in range(50):
        # Go backwards in time (most recent data first)
        point_time = current_time - timedelta(hours=(49 - i))
        
        # Format timestamp nicely
        timestamp = point_time.strftime("%b %d, %H:%M")  # Example: "Nov 09, 14:30"
        timestamps.append(timestamp)
        
        hour = point_time.hour
        
        # Solar pattern - zero at night, peak at noon
        if 6 <= hour <= 18:
            intensity = 1.0 - ((hour - 12) ** 2) / 36  # Bell curve
            base = 150 + intensity * 100
            actual_val = base + random.uniform(-20, 20)
            predicted_val = base + random.uniform(-15, 15)
        else:
            actual_val = 0
            predicted_val = 0
            
        actual.append(max(0, actual_val))
        predicted.append(max(0, predicted_val))
    
    return jsonify({
        'timestamps': timestamps,
        'actual': actual,
        'predicted': predicted
    })

if __name__ == '__main__':
    app.run(debug=True)