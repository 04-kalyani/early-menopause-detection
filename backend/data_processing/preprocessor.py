"""
Main preprocessing pipeline for combining and preparing data.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Optional
import joblib

from .data_loader import DataLoader
from .feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Main data preprocessing pipeline."""
    
    def __init__(self, datasets_path: str = "../datasets"):
        self.loader = DataLoader(datasets_path)
        self.engineer = FeatureEngineer()
        self.scaler = None
        
    def preprocess_swan(self) -> pd.DataFrame:
        """Preprocess SWAN data."""
        logger.info("Preprocessing SWAN data...")
        
        # Load and combine SWAN data
        swan_data = self.loader.combine_swan_data()
        
        # Extract features
        features = self.engineer.extract_swan_features(swan_data)
        
        # Create interaction features
        features = self.engineer.create_interaction_features(features)
        
        # Handle missing values
        features = self.engineer.handle_missing_values(features, strategy='median')
        
        logger.info(f"SWAN preprocessing complete: {features.shape}")
        return features
    
    def preprocess_nhanes(self) -> pd.DataFrame:
        """Preprocess NHANES data."""
        logger.info("Preprocessing NHANES data...")
        
        # Load NHANES data
        nhanes_data = self.loader.combine_nhanes_data()
        
        # Extract features
        features = self.engineer.extract_nhanes_features(nhanes_data)
        
        # Create interaction features
        features = self.engineer.create_interaction_features(features)
        
        # Handle missing values
        features = self.engineer.handle_missing_values(features, strategy='median')
        
        logger.info(f"NHANES preprocessing complete: {features.shape}")
        return features
    
    def combine_datasets(self, swan_df: pd.DataFrame, nhanes_df: pd.DataFrame) -> pd.DataFrame:
        """Combine SWAN and NHANES datasets."""
        logger.info("Combining SWAN and NHANES datasets...")
        
        # Identify critical SWAN-specific features (symptoms, etc.) that should be preserved
        critical_swan_features = [
            'hot_flashes', 'sleep_disturbance', 'mood_swings', 'anxiety', 
            'night_sweats', 'days_since_last_period', 'cycle_length', 
            'flow_duration', 'fsh_estradiol_ratio', 'fsh_testosterone_ratio'
        ]
        
        # Align columns - keep common columns AND critical SWAN features
        common_cols = set(swan_df.columns) & set(nhanes_df.columns)
        swan_specific = [col for col in critical_swan_features if col in swan_df.columns]
        all_cols = list(common_cols) + swan_specific + ['is_menopausal']
        
        logger.info(f"Common columns: {len(common_cols)}")
        logger.info(f"SWAN-specific features preserved: {swan_specific}")
        
        # Use all columns (common + SWAN-specific)
        swan_aligned = swan_df[[col for col in swan_df.columns if col in all_cols]]
        
        # For NHANES, add missing critical features as NaN/0 (they'll be filled later)
        nhanes_aligned = nhanes_df[[col for col in nhanes_df.columns if col in common_cols]].copy()
        for feat in swan_specific:
            if feat not in nhanes_aligned.columns:
                nhanes_aligned[feat] = 0.0  # Fill with 0 for NHANES (no symptom data)
        
        # Add target for NHANES if not present (we'll need to derive it)
        if 'is_menopausal' not in nhanes_aligned.columns:
            # Derive from age (approximate: menopause typically around 51)
            if 'age' in nhanes_aligned.columns:
                nhanes_aligned['is_menopausal'] = (nhanes_aligned['age'] >= 51).astype(int)
        
        # Ensure both have same columns in same order
        all_cols_ordered = [col for col in all_cols if col in swan_aligned.columns or col in nhanes_aligned.columns]
        swan_aligned = swan_aligned[[col for col in all_cols_ordered if col in swan_aligned.columns]]
        nhanes_aligned = nhanes_aligned[[col for col in all_cols_ordered if col in nhanes_aligned.columns]]
        
        # Combine
        combined = pd.concat([swan_aligned, nhanes_aligned], ignore_index=True)
        
        logger.info(f"Combined dataset: {combined.shape}")
        logger.info(f"Combined features: {list(combined.columns)}")
        return combined
    
    def prepare_training_data(self, df: pd.DataFrame, target_col: str = 'is_menopausal') -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for training."""
        logger.info("Preparing training data...")
        
        # Separate features and target
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe")
        
        X = df.drop(columns=[target_col], errors='ignore')
        y = df[target_col]
        
        # Remove any remaining non-numeric columns
        X = X.select_dtypes(include=[np.number])
        
        # Final missing value handling
        X = X.fillna(X.median())
        
        # Remove columns with zero variance
        X = X.loc[:, X.var() != 0]
        
        logger.info(f"Training data prepared: X={X.shape}, y={y.shape}")
        logger.info(f"Class distribution: {y.value_counts().to_dict()}")
        
        return X, y
    
    def normalize_data(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Normalize features."""
        from sklearn.preprocessing import StandardScaler
        
        if fit or self.scaler is None:
            self.scaler = StandardScaler()
            X_normalized = pd.DataFrame(
                self.scaler.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            X_normalized = pd.DataFrame(
                self.scaler.transform(X),
                columns=X.columns,
                index=X.index
            )
        
        return X_normalized
    
    def save_preprocessor(self, path: str):
        """Save preprocessor (scaler) for later use."""
        if self.scaler is not None:
            joblib.dump(self.scaler, path)
            logger.info(f"Preprocessor saved to {path}")
    
    def load_preprocessor(self, path: str):
        """Load preprocessor (scaler)."""
        self.scaler = joblib.load(path)
        logger.info(f"Preprocessor loaded from {path}")

