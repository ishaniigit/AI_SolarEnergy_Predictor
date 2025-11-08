import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import os

def build_features(df):
    """
    Build engineered features from datetime column
    """
    df = df.copy()
    
    
    if 'date_time' in df.columns:
        df['date_time'] = pd.to_datetime(df['date_time'])
        
        # Create basic time features
        if 'dayofyear' not in df.columns:
            df['dayofyear'] = df['date_time'].dt.dayofyear
        if 'hour' not in df.columns:
            df['hour'] = df['date_time'].dt.hour
        if 'day' not in df.columns:
            df['day'] = df['date_time'].dt.day
        if 'month' not in df.columns:
            df['month'] = df['date_time'].dt.month
            
        
        if 'hour' in df.columns:
            if 'sin_hour' not in df.columns:
                df['sin_hour'] = np.sin(2 * np.pi * df['hour'] / 24)
            if 'cos_hour' not in df.columns:
                df['cos_hour'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    return df

def get_feature_list(df):
    """
    Get union of expected features that exist in dataframe
    """
    expected_features = [
        'ambient_temperature', 'module_temperature', 'irradiation', 
        'hour', 'day', 'month', 'dayofyear', 'sin_hour', 'cos_hour'
    ]
    
    available_features = [feat for feat in expected_features if feat in df.columns]
    return available_features

def regression_metrics(y_true, y_pred):
    """
    Calculate regression metrics
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    return {
        'MAE': round(mae, 4),
        'RMSE': round(rmse, 4),
        'R2': round(r2, 4)
    }

def plot_feature_importance(model, feature_names, top_n=10):
    """
    Plot feature importance (for notebook)
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        
        plt.figure(figsize=(10, 6))
        plt.title(f"Top {top_n} Feature Importances")
        plt.bar(range(top_n), importances[indices[:top_n]])
        plt.xticks(range(top_n), [feature_names[i] for i in indices[:top_n]], rotation=45)
        plt.tight_layout()
        return plt.gcf()
