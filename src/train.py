# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Add src to path for imports
src_path = Path(__file__).parent
sys.path.append(str(src_path))

from utils import get_feature_list, regression_metrics

def main():
    # Define paths
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "interim" / "train.csv"
    models_dir = project_root / "models"
    
    # Create models directory if it doesn't exist
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading training data...")
    
    try:
        # Check if train.csv exists
        if not data_path.exists():
            print(f"Error: Training data not found at {data_path}")
            print("Please run prepare_data.py first to create train.csv")
            return
        
        df = pd.read_csv(data_path)
        print(f"Data shape: {df.shape}")
        
        # Get features and target
        feature_names = get_feature_list(df)
        X = df[feature_names]
        y = df['ac_power']
        
        print(f"Using features: {feature_names}")
        print(f"Target: ac_power")
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Save scaler
        scaler_path = models_dir / "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        print(f"Scaler saved to: {scaler_path}")
        
        # Train Random Forest
        print("\nTraining Random Forest...")
        rf_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate Random Forest
        y_pred_rf = rf_model.predict(X_test_scaled)
        rf_metrics = regression_metrics(y_test, y_pred_rf)
        
        print("Random Forest Results:")
        for metric, value in rf_metrics.items():
            print(f"  {metric}: {value}")
        
        # Save Random Forest model
        rf_path = models_dir / "rf_model.pkl"
        joblib.dump(rf_model, rf_path)
        print(f"Random Forest model saved to: {rf_path}")
        
        # Try XGBoost
        xgb_model = None
        xgb_metrics = None
        
        try:
            from xgboost import XGBRegressor
            print("\nTraining XGBoost...")
            
            xgb_model = XGBRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            xgb_model.fit(X_train_scaled, y_train)
            
            # Evaluate XGBoost
            y_pred_xgb = xgb_model.predict(X_test_scaled)
            xgb_metrics = regression_metrics(y_test, y_pred_xgb)
            
            print("XGBoost Results:")
            for metric, value in xgb_metrics.items():
                print(f"  {metric}: {value}")
            
            # Save XGBoost model
            xgb_path = models_dir / "xgb_model.pkl"
            joblib.dump(xgb_model, xgb_path)
            print(f"XGBoost model saved to: {xgb_path}")
            
        except ImportError:
            print("\nXGBoost not available, skipping...")
        
        # Save metrics
        metrics_data = {
            'random_forest': rf_metrics
        }
        
        if xgb_metrics:
            metrics_data['xgboost'] = xgb_metrics
        
        metrics_path = models_dir / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        print(f"\nMetrics saved to: {metrics_path}")
        
        # Print best model
        if xgb_metrics and xgb_metrics['R2'] > rf_metrics['R2']:
            print(f"Best model: XGBoost (R2: {xgb_metrics['R2']})")
        else:
            print(f"Best model: Random Forest (R2: {rf_metrics['R2']})")
            
    except Exception as e:
        print(f"Error during training: {e}")
        raise

if __name__ == "__main__":
    main()