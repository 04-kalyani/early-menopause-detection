"""
Main script to train all models.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import logging
from loguru import logger as loguru_logger

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_processing.preprocessor import DataPreprocessor
from data_processing.feature_selection import LASSOFeatureSelector
from models.ml_models import MenopausePredictor
from models.super_learner import SuperLearner

# Configure logging
logging.basicConfig(level=logging.INFO)
loguru_logger.add("logs/training_{time}.log", rotation="10 MB")


def main():
    """Main training pipeline."""
    loguru_logger.info("Starting model training pipeline...")
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor(datasets_path="../datasets")
    
    # Preprocess data
    loguru_logger.info("Step 1: Preprocessing data...")
    swan_data = preprocessor.preprocess_swan()
    nhanes_data = preprocessor.preprocess_nhanes()
    combined_data = preprocessor.combine_datasets(swan_data, nhanes_data)
    
    # Prepare training data
    loguru_logger.info("Step 2: Preparing training data...")
    X, y = preprocessor.prepare_training_data(combined_data, target_col='is_menopausal')
    
    # Normalize features
    X_normalized = preprocessor.normalize_data(X, fit=True)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_normalized, y, test_size=0.2, random_state=42, stratify=y
    )
    
    loguru_logger.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    loguru_logger.info(f"Available features before selection: {list(X_train.columns)[:20]}...")
    loguru_logger.info(f"Total features: {X_train.shape[1]}")
    
    # Feature selection with LASSO
    loguru_logger.info("Step 3: Performing LASSO feature selection...")
    lasso_selector = LASSOFeatureSelector(cv=5)
    X_train_selected = lasso_selector.fit_transform(X_train, y_train)
    X_test_selected = lasso_selector.transform(X_test)
    
    loguru_logger.info(f"Selected {X_train_selected.shape[1]} features")
    
    # Save feature selector
    import joblib
    joblib.dump(lasso_selector, "../models/saved_models/lasso_selector.pkl")
    loguru_logger.info("Feature selector saved")
    
    # Train base models
    loguru_logger.info("Step 4: Training base models...")
    predictor = MenopausePredictor(random_state=42)
    predictor.initialize_models()
    predictor.train_all(X_train_selected, y_train, cv=5)
    
    # Evaluate base models
    loguru_logger.info("Step 5: Evaluating base models...")
    for model_name in ['lda', 'qda', 'random_forest']:
        metrics = predictor.evaluate_model(model_name, X_test_selected, y_test)
        loguru_logger.info(f"{model_name.upper()} Test Results:")
        loguru_logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
        loguru_logger.info(f"  Precision: {metrics['precision']:.4f}")
        loguru_logger.info(f"  Recall: {metrics['recall']:.4f}")
        loguru_logger.info(f"  F1-Score: {metrics['f1_score']:.4f}")
        if 'roc_auc' in metrics:
            loguru_logger.info(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
    
    # Train Super Learner
    loguru_logger.info("Step 6: Training Super Learner ensemble...")
    super_learner = SuperLearner(predictor, random_state=42)
    super_learner.fit(X_train_selected, y_train, cv=5)
    
    # Evaluate Super Learner
    loguru_logger.info("Step 7: Evaluating Super Learner...")
    sl_metrics = super_learner.evaluate(X_test_selected, y_test)
    loguru_logger.info("Super Learner Test Results:")
    loguru_logger.info(f"  Accuracy: {sl_metrics['accuracy']:.4f}")
    loguru_logger.info(f"  Precision: {sl_metrics['precision']:.4f}")
    loguru_logger.info(f"  Recall: {sl_metrics['recall']:.4f}")
    loguru_logger.info(f"  F1-Score: {sl_metrics['f1_score']:.4f}")
    loguru_logger.info(f"  ROC-AUC: {sl_metrics['roc_auc']:.4f}")
    
    # Save models
    loguru_logger.info("Step 8: Saving models...")
    models_dir = Path("../models/saved_models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    for model_name in ['lda', 'qda', 'random_forest']:
        predictor.save_model(model_name, str(models_dir / f"{model_name}_model.pkl"))
    
    # Save Super Learner
    joblib.dump(super_learner, str(models_dir / "super_learner_model.pkl"))
    
    # Save preprocessor
    preprocessor.save_preprocessor(str(models_dir / "scaler.pkl"))
    
    # Save feature names
    pd.Series(X_train_selected.columns.tolist()).to_csv(
        str(models_dir / "selected_features.csv"), index=False
    )
    
    loguru_logger.info("All models saved successfully!")
    loguru_logger.info("Training pipeline completed!")


if __name__ == "__main__":
    main()

