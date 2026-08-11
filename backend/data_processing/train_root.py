
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import sys

# Define input file path and model output path
# Using relative paths from this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../.."))

DATA_FILE = os.path.join(PROJECT_ROOT, "data set menopause.xlsx")
MODEL_DIR = os.path.join(PROJECT_ROOT, "menopause-detection/models/saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "root_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "root_scaler.pkl")

def train_model():
    print("Loading dataset...")
    try:
        df = pd.read_excel(DATA_FILE)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Target variable: 'Loss menstuartion'
    # 1 -> Pre-menopause (Regular) -> 0
    # 2 -> Perimenopause (Irregular) -> 1
    # 3 -> Post-menopause (Stopped) -> 2 or 1 (depending on binary/multi)
    # The user request implies "is_menopausal" (binary) mostly, but let's check values.
    # Previous check showed values: [nan, 1., 2., 3.]
    # 1: Regual (Pre)
    # 2: Irregular (Peri)
    # 3: Stopped (Post)
    
    # Let's clean the target
    df = df.dropna(subset=['Loss menstuartion'])
    
    # Mapping to Binary for simple 'Is Menopausal' prediction if needed, 
    # or keep multiclass. Let's do Multiclass as it gives more info.
    # But for "Detection" usually means Yes/No. 
    # Let's stick to the column values for now and decide interpretation in API.
    y = df['Loss menstuartion']
    
    # Features
    # We need to drop columns that are not predictive or are the target
    # Based on cols.txt:
    # 'Age', 'City', 'profession working', ...
    # We should exclude 'Unnamed: 3', 'Unnamed: 5', 'Loss menstuartion'
    
    # Also 'Children', 'Pregnancies', 'how do you evaluate knowledge...', 'source of information'
    # might not be symptoms but demographic/knowledge.
    
    # Predictive columns (Symptoms & Health):
    # 'Age', 'Increase Bp Thyroid gland', 'Back pain', 'DM', 'Heart disease', 
    # 'Varcoise', 'Constipation', 'Respiratory', 'Tumors', 'chronicd', 
    # 'Do you examine breast monthly', 'Do you use mamogram', 'Do you use swap',
    # 'Do you apply routine exam', 'preventive', 'Do you use contraceptive'
    # 'agecat' (maybe redundant if Age is there)
    
    # QoL columns (Psychological/Social):
    # 'I could control my important things', ... (Likert scale questions)
    
    # Let's select all numeric-able columns and drop identifiers
    
    # Dropping clearly non-predictive or target
    drop_cols = ['Loss menstuartion', 'City', 'Unnamed: 3', 'Unnamed: 5', 'profession working', 
                 'Who give money', 'Social status', 'Educational degree', 'income',
                 'how do you evaluate knowledge about menopause', 'source of information',
                 # Drop derived/aggregate columns that we can't easily calculate live
                 'agecat', 'emotional', 'sexual', 'health', 'occupational', 
                 'totalqol', 'educationcat', 'finiacialcat'
                 ]
    
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    # Handle object columns if any (Encoding)
    # 'Increase Bp Thyroid gland' might be Yes/No
    # Let's do simple get_dummies or LabelEncoding if needed.
    # For now, let's assume most are numeric or coded.
    # Inspect types:
    
    # Convert all to numeric, errors='coerce' to find non-numeric
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors='coerce')
        
    X = X.fillna(0) # Fill NaNs with 0
    
    print(f"Features shape: {X.shape}")
    print(f"Target distribution (Before SMOTE): \n{y.value_counts()}")
    
    # Handle Class Imbalance with SMOTE
    # Only if we have enough samples (k_neighbors=1 by default needs > 1 sample per class)
    try:
        from imblearn.over_sampling import SMOTE
        smote = SMOTE(random_state=42, k_neighbors=1)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        print(f"Target distribution (After SMOTE): \n{y_resampled.value_counts()}")
        X, y = X_resampled, y_resampled
    except Exception as e:
        print(f"SMOTE failed: {e}. Proceeding with class weights.")
        # Fallback to class weights in RF if SMOTE fails (e.g., extremely rare classes)
        # But here we have 3 samples for class 3, so k=1 should work.

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    print("Training RandomForest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Accuracy: {acc:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, preds))
    
    # Save
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump(model, MODEL_PATH)
    
    # Also save the column names to ensure input matches at inference time
    cols_path = os.path.join(MODEL_DIR, "root_model_columns.pkl")
    joblib.dump(list(X.columns), cols_path)
    
    print(f"Model saved to {MODEL_PATH}")
    print(f"Model columns saved to {cols_path}")

if __name__ == "__main__":
    train_model()
