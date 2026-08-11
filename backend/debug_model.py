
import joblib
import pandas as pd
import numpy as np

MODELS_DIR = "c:/Users/raash/Desktop/menopause-detection/menopause-detection/models/saved_models"
ROOT_MODEL_PATH = MODELS_DIR + "/root_model.pkl"
ROOT_COLS_PATH = MODELS_DIR + "/root_model_columns.pkl"

def debug_model():
    print(f"Loading model from {ROOT_MODEL_PATH}")
    model = joblib.load(ROOT_MODEL_PATH)
    columns = joblib.load(ROOT_COLS_PATH)
    
    print("\nModel Columns:", columns)
    
    # Test Data Scenarios
    scenarios = {
        "Pre (Healthy)": {
            'Age': 25,
            # Assume 0 for everything else
        },
        "Peri (Irregular)": {
            'Age': 48,
            'Loss menstuartion': 2 # BUT 'Loss menstuartion' is the TARGET, so it won't be in columns!
            # We need to find features that correlate with Peri
        },
        "Post (Stopped)": {
            'Age': 60,
        }
    }
    
    # Based on the user feedback, we need to check what features actually drive the prediction.
    # Let's inspect feature importances if available
    try:
        importances = model.feature_importances_
        feature_importance = list(zip(columns, importances))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        print("\nTop 10 Feature Importances:")
        for f, v in feature_importance[:10]:
            print(f"{f}: {v:.4f}")
            
    except Exception as e:
        print(f"Could not get feature importances: {e}")

    print("\nRunning Test Scenarios:")
    for name, data in scenarios.items():
        input_df = pd.DataFrame(columns=columns)
        input_df.loc[0] = 0.0 # Default all to 0
        
        for k, v in data.items():
            if k in columns:
                input_df.at[0, k] = v
            else:
                print(f"[{name}] Warning: Feature '{k}' not in model columns!")
        
        pred = model.predict(input_df)[0]
        # proba = model.predict_proba(input_df)
        
        label = "Unknown"
        if pred == 1: label = "Pre-Menopause (Regular)"
        elif pred == 2: label = "Perimenopause (Irregular)"
        elif pred == 3: label = "Post-Menopause (Stopped)"
            
        print(f"Scenario: {name} -> Prediction: {pred} ({label})")

if __name__ == "__main__":
    debug_model()
