"""
Machine learning models for menopause prediction.
"""
import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import logging
import joblib

logger = logging.getLogger(__name__)


class MenopausePredictor:
    """Main class for menopause prediction models."""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models = {}
        self.trained_models = {}
        self.cv_scores = {}
        self.test_results = {}
        
    def initialize_models(self):
        """Initialize all models."""
        logger.info("Initializing ML models...")
        
        self.models = {
            'lda': LinearDiscriminantAnalysis(solver='svd', shrinkage=None),
            'qda': QuadraticDiscriminantAnalysis(),
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1
            )
        }
        
        logger.info(f"Initialized {len(self.models)} models")
    
    def train_lda(self, X: pd.DataFrame, y: pd.Series, cv: int = 5):
        """Train Linear Discriminant Analysis model."""
        logger.info("Training LDA model...")
        
        model = self.models['lda']
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X, y, cv=cv, scoring='roc_auc',
            n_jobs=-1
        )
        
        # Train on full data
        model.fit(X, y)
        
        self.trained_models['lda'] = model
        self.cv_scores['lda'] = {
            'mean': cv_scores.mean(),
            'std': cv_scores.std(),
            'scores': cv_scores
        }
        
        logger.info(f"LDA CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        return model
    
    def train_qda(self, X: pd.DataFrame, y: pd.Series, cv: int = 5):
        """Train Quadratic Discriminant Analysis model."""
        logger.info("Training QDA model...")
        
        model = self.models['qda']
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X, y, cv=cv, scoring='roc_auc',
            n_jobs=-1
        )
        
        # Train on full data
        model.fit(X, y)
        
        self.trained_models['qda'] = model
        self.cv_scores['qda'] = {
            'mean': cv_scores.mean(),
            'std': cv_scores.std(),
            'scores': cv_scores
        }
        
        logger.info(f"QDA CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        return model
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series, cv: int = 5):
        """Train Random Forest model."""
        logger.info("Training Random Forest model...")
        
        model = self.models['random_forest']
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X, y, cv=cv, scoring='roc_auc',
            n_jobs=-1
        )
        
        # Train on full data
        model.fit(X, y)
        
        self.trained_models['random_forest'] = model
        self.cv_scores['random_forest'] = {
            'mean': cv_scores.mean(),
            'std': cv_scores.std(),
            'scores': cv_scores
        }
        
        logger.info(f"Random Forest CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        return model
    
    def train_all(self, X: pd.DataFrame, y: pd.Series, cv: int = 5):
        """Train all models."""
        logger.info("Training all models...")
        
        if not self.models:
            self.initialize_models()
        
        self.train_lda(X, y, cv)
        self.train_qda(X, y, cv)
        self.train_random_forest(X, y, cv)
        
        logger.info("All models trained successfully")
    
    def evaluate_model(self, model_name: str, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """Evaluate a trained model."""
        if model_name not in self.trained_models:
            raise ValueError(f"Model '{model_name}' not found")
        
        model = self.trained_models[model_name]
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
        }
        
        if y_pred_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
        
        metrics['confusion_matrix'] = confusion_matrix(y_test, y_pred).tolist()
        
        self.test_results[model_name] = metrics
        return metrics
    
    def predict(self, model_name: str, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using a trained model."""
        if model_name not in self.trained_models:
            raise ValueError(f"Model '{model_name}' not found")
        
        return self.trained_models[model_name].predict(X)
    
    def predict_proba(self, model_name: str, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities."""
        if model_name not in self.trained_models:
            raise ValueError(f"Model '{model_name}' not found")
        
        model = self.trained_models[model_name]
        if hasattr(model, 'predict_proba'):
            return model.predict_proba(X)
        else:
            raise ValueError(f"Model '{model_name}' does not support probability predictions")
    
    def save_model(self, model_name: str, path: str):
        """Save a trained model."""
        if model_name not in self.trained_models:
            raise ValueError(f"Model '{model_name}' not found")
        
        joblib.dump(self.trained_models[model_name], path)
        logger.info(f"Model '{model_name}' saved to {path}")
    
    def load_model(self, model_name: str, path: str):
        """Load a trained model."""
        self.trained_models[model_name] = joblib.load(path)
        logger.info(f"Model '{model_name}' loaded from {path}")

