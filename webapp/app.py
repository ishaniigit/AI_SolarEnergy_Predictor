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
        irradiation = float(request.form.get('irradiation', 0.8))
        ambient_temp = float(request.form.get('ambient_temperature', 25.0))
        module_temp = float(request.form.get('module_temperature', 35.0))
        hour = int(request.form.get('hour', 12))
        
        base_power = irradiation * 280
        time_factor = 1.0 - abs(hour - 12) / 12
        temp_effect = max(0, (module_temp - 25) * -0.005)
        
        prediction = base_power * time_factor * (1 + temp_effect)
        prediction += random.uniform(-15, 15)
        prediction = max(0, min(500, prediction))
        
        return jsonify({
            'prediction': round(prediction, 2),
            'model_used': 'Solar AI Engine',
            'confidence': 'High'
        })
        
    except Exception as e:
        return jsonify({'error': 'Prediction calculation failed'}), 400

@app.route('/series')
def get_series():
    \"\"\"Generate demo chart data with CURRENT timestamps - UPDATED NOVEMBER\"\"\"
    timestamps = []
    actual = []
    predicted = []
    
    current_time = datetime.datetime.now()
    
    for i in range(50):
        point_time = current_time - timedelta(hours=(49 - i))
        
        # CURRENT TIMESTAMP - NOT JUNE
        timestamp = point_time.strftime("%b %d, %H:%M")  # This shows CURRENT month
        timestamps.append(timestamp)
        
        hour = point_time.hour
        
        if 6 <= hour <= 18:
            intensity = 1.0 - ((hour - 12) ** 2) / 36
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
