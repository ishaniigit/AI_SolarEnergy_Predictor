# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path for imports
src_path = Path(__file__).parent
sys.path.append(str(src_path))

from utils import build_features, get_feature_list

def main():
    # Define paths
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "Processed" / "cleaned_solar_data.csv"
    output_path = project_root / "data" / "interim" / "train.csv"
    
    # Create interim directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Loading data...")
    
    try:
        # Read data with flexible column naming
        df = pd.read_csv(data_path)
        
        # Standardize column names to lowercase with underscores
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        print(f"Original columns: {list(df.columns)}")
        print(f"Data shape: {df.shape}")
        
        # Check for required target
        if 'ac_power' not in df.columns:
            raise ValueError("Required column 'ac_power' not found in dataset")
        
        # Build features
        df = build_features(df)
        
        # Get available features
        available_features = get_feature_list(df)
        print(f"Available features for training: {available_features}")
        
        # Save processed data
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Processed data saved to: {output_path}")
        print(f"Final data shape: {df.shape}")
        
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        print("Please ensure cleaned_solar_data.csv exists in data/Processed/")
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()