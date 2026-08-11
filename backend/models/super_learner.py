"""
Super Learner ensemble model for menopause prediction.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
import logging

from .ml_models import MenopausePredictor

logger = logging.getLogger(__name__)


class SuperLearner:
    """
    Super Learner ensemble model.
    Combines base learners (LDA, QDA, Random Forest) with a meta-learner.
    """
    
    def __init__(self, base_models: MenopausePredictor, random_state: int = 42):
        """
        Initialize Super Learner.
        
        Args:
            base_models: Trained MenopausePredictor with base models
            random_state: Random state for reproducibility
        """
        self.base_models = base_models
        self.meta_learner = LogisticRegression(random_state=random_state, max_iter=1000)
        self.trained = False
        self.cv_scores = {}
        
    def fit(self, X: pd.DataFrame, y: pd.Series, cv: int = 5):
        """
        Fit Super Learner using stacking.
        
        Args:
            X: Feature matrix
            y: Target vector
            cv: Number of cross-validation folds
        """
        logger.info("Training Super Learner ensemble...")
        
        # Get base model predictions using cross-validation
        base_predictions = []
        model_names = ['lda', 'qda', 'random_forest']
        
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        
        for model_name in model_names:
            if model_name not in self.base_models.trained_models:
                logger.warning(f"Base model '{model_name}' not found, skipping...")
                continue
            
            model = self.base_models.trained_models[model_name]
            predictions = cross_val_predict(
                model, X, y, cv=skf, method='predict_proba', n_jobs=-1
            )[:, 1]  # Get probability of positive class
            
            base_predictions.append(predictions)
        
        if not base_predictions:
            raise ValueError("No base models available for Super Learner")
        
        # Stack base predictions
        X_meta = np.column_stack(base_predictions)
        
        # Train meta-learner
        self.meta_learner.fit(X_meta, y)
        
        # Cross-validation score for Super Learner
        meta_predictions = cross_val_predict(
            self.meta_learner, X_meta, y, cv=skf, method='predict_proba', n_jobs=-1
        )[:, 1]
        
        self.cv_scores = {
            'roc_auc': roc_auc_score(y, meta_predictions),
            'accuracy': accuracy_score(y, (meta_predictions > 0.5).astype(int)),
            'precision': precision_score(y, (meta_predictions > 0.5).astype(int), zero_division=0),
            'recall': recall_score(y, (meta_predictions > 0.5).astype(int), zero_division=0),
            'f1_score': f1_score(y, (meta_predictions > 0.5).astype(int), zero_division=0)
        }
        
        self.trained = True
        logger.info(f"Super Learner CV ROC-AUC: {self.cv_scores['roc_auc']:.4f}")
        logger.info(f"Super Learner CV Accuracy: {self.cv_scores['accuracy']:.4f}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using Super Learner."""
        if not self.trained:
            raise ValueError("Super Learner must be trained first")
        
        # Get base model predictions
        base_predictions = []
        model_names = ['lda', 'qda', 'random_forest']
        
        for model_name in model_names:
            if model_name in self.base_models.trained_models:
                model = self.base_models.trained_models[model_name]
                pred_proba = model.predict_proba(X)[:, 1]
                base_predictions.append(pred_proba)
        
        # Stack and predict with meta-learner
        X_meta = np.column_stack(base_predictions)
        return self.meta_learner.predict(X_meta)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities."""
        if not self.trained:
            raise ValueError("Super Learner must be trained first")
        
        # Get base model predictions
        base_predictions = []
        model_names = ['lda', 'qda', 'random_forest']
        
        for model_name in model_names:
            if model_name in self.base_models.trained_models:
                model = self.base_models.trained_models[model_name]
                pred_proba = model.predict_proba(X)[:, 1]
                base_predictions.append(pred_proba)
        
        # Stack and predict with meta-learner
        X_meta = np.column_stack(base_predictions)
        return self.meta_learner.predict_proba(X_meta)
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """Evaluate Super Learner on test set."""
        if not self.trained:
            raise ValueError("Super Learner must be trained first")
        
        y_pred = self.predict(X_test)
        y_pred_proba = self.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        return metrics

