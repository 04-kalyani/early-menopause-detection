
"""
FastAPI main application for menopause prediction API (Refactored) with XAI.
"""
import sys
import os
from pathlib import Path

# Add the backend directory to sys.path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import joblib
import pandas as pd
import numpy as np
import shap
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from datetime import timedelta

from . import sql_models, database, auth
from models.diet_recommender import DietRecommender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Tables
sql_models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Menopause Detection API", version="2.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models" / "saved_models"
ROOT_MODEL_PATH = MODELS_DIR / "root_model.pkl"
ROOT_COLS_PATH = MODELS_DIR / "root_model_columns.pkl"

root_model = None
root_model_cols = []
explainer = None
recommender = None

def load_root_model():
    global root_model, root_model_cols, explainer, recommender
    try:
        # Initialize Recommender with correct path
        try:
            usda_path = BASE_DIR / "datasets" / "FoodData_Central_foundation_food_csv_2025-04-24"
            recommender = DietRecommender(usda_data_path=str(usda_path))
            logger.info(f"Diet recommender initialized with path: {usda_path}")
        except Exception as e:
            logger.error(f"Failed to initialize recommender: {e}")

        if ROOT_MODEL_PATH.exists():
            root_model = joblib.load(ROOT_MODEL_PATH)
            logger.info("Root model loaded successfully.")
            
            # Initialize KernelExplainer or TreeExplainer if possible
            # Since we don't have the training data easily available here for background distribution,
            # using TreeExplainer is best for RandomForest.
            try:
                explainer = shap.TreeExplainer(root_model)
                logger.info("SHAP explainer initialized.")
            except Exception as e:
                logger.warning(f"Could not initialize SHAP explainer: {e}")

        if ROOT_COLS_PATH.exists():
            root_model_cols = joblib.load(ROOT_COLS_PATH)
            logger.info(f"Root model columns loaded: {len(root_model_cols)}")
    except Exception as e:
        logger.error(f"Error loading models: {e}")

def seed_debug_assessment(user_id: int):
    """Seed a dummy assessment for debugging SHAP and history."""
    db = database.SessionLocal()
    try:
        # Check if user already has assessments
        existing = db.query(sql_models.Assessment).filter(sql_models.Assessment.user_id == user_id).first()
        if not existing:
            dummy_answers = {
                "Age": 52,
                "chronicd": 1,
                "DM": 0,
                "Increase Bp Thyroid gland": 1,
                "hot_flashes": 7,
                "sleep_disturbance": 5,
                "mood_swings": 8
            }
            # Fill other required columns with 0 if needed
            for col in root_model_cols:
                if col not in dummy_answers:
                    dummy_answers[col] = 0
            
            assessment = sql_models.Assessment(
                user_id=user_id,
                answers=dummy_answers,
                prediction="Perimenopause (Irregular)",
                probability=0.85
            )
            db.add(assessment)
            db.commit()
            logger.info(f"Debug assessment seeded for user {user_id}")
    except Exception as e:
        logger.error(f"Error seeding debug assessment: {e}")
    finally:
        db.close()

def seed_test_user():
    """Seed the database with a test user and ensure the password is correct."""
    db = database.SessionLocal()
    try:
        test_email = "test@example.com"
        test_password = "12345678"
        hashed_password = auth.get_password_hash(test_password)
        
        # Check if user already exists
        db_user = db.query(sql_models.User).filter(sql_models.User.email == test_email).first()
        if not db_user:
            new_user = sql_models.User(email=test_email, hashed_password=hashed_password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"Test user {test_email} created successfully on startup.")
            seed_debug_assessment(new_user.id)
        else:
            # Update password to ensure it matches 12345678
            db_user.hashed_password = hashed_password
            db.commit()
            logger.info(f"Test user {test_email} password updated/verified on startup.")
            seed_debug_assessment(db_user.id)
            
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    load_root_model()
    seed_test_user()

# --- Pydantic Models ---

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class QuestionnaireInput(BaseModel):
    answers: Dict[str, Any] 

class AssessmentResult(BaseModel):
    id: int
    prediction: str
    probability: float
    timestamp: str 
    answers: Dict[str, Any]

    class Config:
        orm_mode = True

# --- Auth Routes ---

@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(sql_models.User).filter(sql_models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = sql_models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = auth.create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(sql_models.User).filter(sql_models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
def read_users_me(current_user: sql_models.User = Depends(auth.get_current_user)):
    return {"email": current_user.email, "id": current_user.id}

# --- Prediction & History ---

@app.post("/predict_questionnaire")
def predict_questionnaire(
    input_data: QuestionnaireInput, 
    current_user: sql_models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not root_model or not root_model_cols:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    
    # Prepare input vector
    input_df = pd.DataFrame(columns=root_model_cols)
    input_df.loc[0] = 0
    
    # Fill values
    for col in root_model_cols:
        val = input_data.answers.get(col)
        if val is not None:
            try:
                input_df.at[0, col] = float(val)
            except:
                pass 
    
    try:
        prediction = root_model.predict(input_df)[0]
        
        pred_label = "Unknown"
        is_menopausal = False
        
        # 1: Regular, 2: Irregular, 3: Stopped
        if prediction == 1:
            pred_label = "Pre-Menopause (Regular)"
        elif prediction == 2:
            pred_label = "Perimenopause (Irregular)"
            is_menopausal = True
        elif prediction == 3:
            pred_label = "Post-Menopause (Stopped)"
            is_menopausal = True
            
        probability = 0.0
        if hasattr(root_model, "predict_proba"):
            probs = root_model.predict_proba(input_df)
            probability = np.max(probs) 
            
        # Calculate Explanations (SHAP)
        top_features = []
        base_value = 0.0
        if explainer:
            try:
                shap_values = explainer.shap_values(input_df)
                
                # Get the correct class index dynamically
                try:
                    # RandomForestClassifier stores classes in .classes_
                    class_idx = list(root_model.classes_).index(prediction)
                except:
                    # Fallback mapping
                    if prediction == 1: class_idx = 0
                    elif prediction == 2: class_idx = 1
                    elif prediction == 3: class_idx = 2
                    else: class_idx = 0
                
                # Check shape complexity and extract values
                if isinstance(shap_values, list):
                    # For multiclass, shap_values is a list of arrays
                    class_shap = shap_values[class_idx][0]
                    # Capture the base value (expected value) for this class
                    if hasattr(explainer, 'expected_value'):
                        if isinstance(explainer.expected_value, (list, np.ndarray)):
                            base_value = float(explainer.expected_value[class_idx])
                        else:
                            base_value = float(explainer.expected_value)
                else:
                    # For single output models
                    class_shap = shap_values[0]
                    if hasattr(explainer, 'expected_value'):
                        base_value = float(explainer.expected_value)
                
                # Create (feature, importance) pairs
                feature_importance = []
                for i, col in enumerate(root_model_cols):
                    feature_importance.append({
                        "feature": col, 
                        "importance": float(class_shap[i])
                    })
                
                # Sort by absolute importance value
                feature_importance.sort(key=lambda x: abs(x["importance"]), reverse=True)
                
                # Select top 10 for a better graph
                top_features = feature_importance[:10]
                
            except Exception as e:
                logger.warning(f"SHAP calculation failed: {e}")

        # Save to DB
        assessment = sql_models.Assessment(
            user_id=current_user.id,
            answers=input_data.answers,
            prediction=pred_label,
            probability=float(probability)
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        # Generate Recommendations
        recommendations = {}
        if recommender:
            try:
                # Prepare profile for recommender
                user_profile = input_data.answers.copy()
                # Ensure BMI is available if weight/height present
                if 'weight' in user_profile and 'height' in user_profile and 'bmi' not in user_profile:
                    try:
                        w = float(user_profile['weight'])
                        h = float(user_profile['height']) / 100
                        if h > 0:
                            user_profile['bmi'] = w / (h * h)
                    except:
                        pass
                
                pred_result = {
                    "is_menopausal": is_menopausal,
                    "probability": probability
                }
                recommendations = recommender.recommend_personalized(user_profile, pred_result)
            except Exception as e:
                logger.error(f"Recommendation error: {e}")

        return {
            "prediction": pred_label,
            "is_menopausal": is_menopausal,
            "probability": probability,
            "assessment_id": assessment.id,
            "top_features": top_features,
            "base_value": base_value,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history(
    current_user: sql_models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    history = db.query(sql_models.Assessment).filter(sql_models.Assessment.user_id == current_user.id).order_by(sql_models.Assessment.timestamp.desc()).all()
    
    # Enrich history with SHAP and recommendations if missing (for legacy data or deep view)
    enriched_history = []
    for entry in history:
        item = {
            "id": entry.id,
            "timestamp": entry.timestamp,
            "prediction": entry.prediction,
            "probability": entry.probability,
            "answers": entry.answers,
            "is_menopausal": "Pre" not in entry.prediction,
            "top_features": [],
            "base_value": 0.0,
            "recommendations": {}
        }
        
        # Re-run SHAP and Recommendations for historical view
        if explainer:
            try:
                input_df = pd.DataFrame([entry.answers], columns=root_model_cols).fillna(0)
                for col in root_model_cols:
                    input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0)
                
                # SHAP
                shap_values = explainer.shap_values(input_df)
                try:
                    pred_val = root_model.predict(input_df)[0]
                    class_idx = list(root_model.classes_).index(pred_val)
                except:
                    class_idx = 0
                
                if isinstance(shap_values, list):
                    class_shap = shap_values[class_idx][0]
                    item["base_value"] = float(explainer.expected_value[class_idx])
                else:
                    class_shap = shap_values[0]
                    item["base_value"] = float(explainer.expected_value)
                
                feature_importance = []
                for i, col in enumerate(root_model_cols):
                    feature_importance.append({"feature": col, "importance": float(class_shap[i])})
                feature_importance.sort(key=lambda x: abs(x["importance"]), reverse=True)
                item["top_features"] = feature_importance[:10]
            except Exception as e:
                logger.error(f"Error enriching SHAP for history item {entry.id}: {e}")

        if recommender:
            try:
                # Recommendations
                item["recommendations"] = recommender.recommend_personalized(
                    entry.answers, 
                    {"is_menopausal": item["is_menopausal"], "probability": entry.probability}
                )
            except Exception as e:
                logger.error(f"Error enriching recommendations for history item {entry.id}: {e}")
        
        enriched_history.append(item)
        
    return enriched_history

@app.get("/model/columns")
def get_model_columns():
    return {"columns": root_model_cols}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)