"""
LASSO-based feature selection.
"""
import numpy as np
import pandas as pd
from typing import Optional
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class LASSOFeatureSelector:
    """LASSO-based feature selection for menopause prediction."""
    
    def __init__(self, alpha_range: Optional[np.ndarray] = None, cv: int = 5):
        """
        Initialize LASSO feature selector.
        
        Args:
            alpha_range: Range of alpha values for LASSO. If None, uses default.
            cv: Number of cross-validation folds.
        """
        if alpha_range is None:
            # Default: log space from 0.001 to 10
            alpha_range = np.logspace(-3, 1, 50)
        
        self.alpha_range = alpha_range
        self.cv = cv
        self.lasso = None
        self.selected_features = None
        self.scaler = StandardScaler()
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> np.ndarray:
        """
        Fit LASSO and select features.
        
        Args:
            X: Feature matrix
            y: Target vector
            
        Returns:
            Boolean array indicating selected features
        """
        logger.info("Performing LASSO feature selection...")
        logger.info(f"Initial features: {X.shape[1]}")
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit LASSO with cross-validation
        self.lasso = LassoCV(alphas=self.alpha_range, cv=self.cv, random_state=42, max_iter=2000)
        self.lasso.fit(X_scaled, y)
        
        # Get selected features (non-zero coefficients)
        selected_mask = np.abs(self.lasso.coef_) > 1e-5
        lasso_selected = X.columns[selected_mask].tolist()
        
        # Force critical clinical features to be included (even if LASSO doesn't select them)
        # These are essential for menopause prediction
        critical_features = [
            'age', 'hot_flashes', 'sleep_disturbance', 'mood_swings', 'anxiety',
            'fsh', 'estradiol', 'bmi', 'weight', 'height'
        ]
        
        # Add critical features that exist in the data but weren't selected by LASSO
        for feat in critical_features:
            if feat in X.columns and feat not in lasso_selected:
                lasso_selected.append(feat)
                logger.info(f"Force-adding critical feature: {feat}")
        
        self.selected_features = lasso_selected
        
        logger.info(f"Optimal alpha: {self.lasso.alpha_:.6f}")
        lasso_count = np.sum(selected_mask)
        logger.info(f"LASSO selected: {lasso_count} features")
        logger.info(f"Total selected (including critical): {len(self.selected_features)} out of {X.shape[1]}")
        logger.info(f"Selected features: {self.selected_features}")
        
        return selected_mask
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform data to selected features."""
        if self.selected_features is None:
            raise ValueError("Feature selector must be fitted first")
        
        return X[self.selected_features]
    
    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Fit and transform in one step."""
        self.fit(X, y)
        return self.transform(X)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance (absolute coefficients)."""
        if self.lasso is None:
            raise ValueError("Feature selector must be fitted first")
        
        importance_df = pd.DataFrame({
            'feature': self.selected_features,
            'coefficient': self.lasso.coef_[np.abs(self.lasso.coef_) > 1e-5],
            'abs_coefficient': np.abs(self.lasso.coef_[np.abs(self.lasso.coef_) > 1e-5])
        }).sort_values('abs_coefficient', ascending=False)
        
        return importance_df

