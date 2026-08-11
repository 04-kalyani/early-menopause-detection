"""
Feature engineering for menopause prediction.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Engineer features for menopause prediction."""
    
    def __init__(self):
        self.feature_mapping = self._create_feature_mapping()
    
    def _create_feature_mapping(self) -> Dict[str, List[str]]:
        """Map feature categories to column names."""
        return {
            'demographics': ['AGE0', 'RACE', 'BMI0', 'WEIGHT0', 'HEIGHT0'],
            'hormones': ['FSH0', 'E2AVE0', 'SHBG0', 'T0', 'TSH0'],
            'symptoms': ['HOTFLAS0', 'SLEEP0', 'MOODCHN0', 'MOODCHG0', 'ANXIOUS0', 
                        'TRBLSLE0', 'NITESWE0', 'VAGINDR0', 'FEELBLU0'],
            'lifestyle': ['SMOKERE0', 'SMOKENO0', 'SMOKEYR0', 'PAQ_H', 'PHYSWOR0'],
            'menstrual': ['STATUS0', 'LMPDAY0', 'CYCDAY0', 'FLOWDAY0', 'INTERVA0'],
            'clinical': ['BP0', 'CHOLEST0', 'DIABETES0', 'HEART0']
        }
    
    def extract_swan_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and engineer features from SWAN data."""
        logger.info("Engineering features from SWAN data...")
        
        features_df = pd.DataFrame()
        
        # Demographics
        if 'AGE0' in df.columns:
            features_df['age'] = pd.to_numeric(df['AGE0'], errors='coerce')
        
        if 'BMI0' in df.columns:
            features_df['bmi'] = pd.to_numeric(df['BMI0'], errors='coerce')
        
        if 'WEIGHT0' in df.columns:
            features_df['weight'] = pd.to_numeric(df['WEIGHT0'], errors='coerce')
        
        if 'HEIGHT0' in df.columns:
            features_df['height'] = pd.to_numeric(df['HEIGHT0'], errors='coerce')
        
        # Hormones
        if 'FSH0' in df.columns:
            features_df['fsh'] = pd.to_numeric(df['FSH0'], errors='coerce')
        
        if 'E2AVE0' in df.columns:
            features_df['estradiol'] = pd.to_numeric(df['E2AVE0'], errors='coerce')
        
        if 'SHBG0' in df.columns:
            features_df['shbg'] = pd.to_numeric(df['SHBG0'], errors='coerce')
        
        if 'T0' in df.columns:
            features_df['testosterone'] = pd.to_numeric(df['T0'], errors='coerce')
        
        # Symptoms
        if 'HOTFLAS0' in df.columns:
            features_df['hot_flashes'] = pd.to_numeric(df['HOTFLAS0'], errors='coerce')
        
        if 'SLEEP0' in df.columns or 'TRBLSLE0' in df.columns:
            sleep_col = 'TRBLSLE0' if 'TRBLSLE0' in df.columns else 'SLEEP0'
            features_df['sleep_disturbance'] = pd.to_numeric(df[sleep_col], errors='coerce')
        
        if 'MOODCHN0' in df.columns or 'MOODCHG0' in df.columns:
            mood_col = 'MOODCHG0' if 'MOODCHG0' in df.columns else 'MOODCHN0'
            features_df['mood_swings'] = pd.to_numeric(df[mood_col], errors='coerce')
        
        if 'ANXIOUS0' in df.columns:
            features_df['anxiety'] = pd.to_numeric(df['ANXIOUS0'], errors='coerce')
        
        if 'NITESWE0' in df.columns:
            features_df['night_sweats'] = pd.to_numeric(df['NITESWE0'], errors='coerce')
        
        # Lifestyle
        if 'SMOKERE0' in df.columns:
            features_df['smoking'] = (df['SMOKERE0'] == 1).astype(int)
        
        if 'SMOKEYR0' in df.columns:
            features_df['smoking_years'] = pd.to_numeric(df['SMOKEYR0'], errors='coerce')
        
        # Physical activity (if available)
        if 'PHYSWOR0' in df.columns:
            features_df['physical_activity'] = pd.to_numeric(df['PHYSWOR0'], errors='coerce')
        
        # Menstrual status
        if 'STATUS0' in df.columns:
            # STATUS0: 4=premenopausal, 5=perimenopausal, 7=postmenopausal
            features_df['menopause_status'] = pd.to_numeric(df['STATUS0'], errors='coerce')
            # Create binary target: 0=premenopausal, 1=perimenopausal/postmenopausal
            features_df['is_menopausal'] = (features_df['menopause_status'] >= 5).astype(int)
        
        if 'LMPDAY0' in df.columns:
            features_df['days_since_last_period'] = pd.to_numeric(df['LMPDAY0'], errors='coerce')
        
        # Menstrual cycle
        if 'CYCDAY0' in df.columns:
            features_df['cycle_length'] = pd.to_numeric(df['CYCDAY0'], errors='coerce')
        
        if 'FLOWDAY0' in df.columns:
            features_df['flow_duration'] = pd.to_numeric(df['FLOWDAY0'], errors='coerce')
        
        # Clinical
        if 'BP0' in df.columns:
            features_df['blood_pressure_meds'] = (df['BP0'] == 1).astype(int)
        
        logger.info(f"Engineered {features_df.shape[1]} features from SWAN data")
        return features_df
    
    def extract_nhanes_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and engineer features from NHANES data."""
        logger.info("Engineering features from NHANES data...")
        
        features_df = pd.DataFrame()
        
        # Demographics
        if 'RIDAGEYR' in df.columns:
            features_df['age'] = pd.to_numeric(df['RIDAGEYR'], errors='coerce')
        
        if 'RIAGENDR' in df.columns:
            # Filter for females only (RIAGENDR == 2)
            df = df[df['RIAGENDR'] == 2].copy()
        
        # Body measures
        if 'BMXBMI' in df.columns:
            features_df['bmi'] = pd.to_numeric(df['BMXBMI'], errors='coerce')
        
        if 'BMXWT' in df.columns:
            features_df['weight'] = pd.to_numeric(df['BMXWT'], errors='coerce')
        
        if 'BMXHT' in df.columns:
            features_df['height'] = pd.to_numeric(df['BMXHT'], errors='coerce')
        
        # Hormones (from TST_H)
        hormone_cols = {
            'LBXTST': 'testosterone',
            'LBXEST': 'estradiol',
            'LBXFSH': 'fsh',
            'LBXSHBG': 'shbg'
        }
        
        for nhanes_col, feature_name in hormone_cols.items():
            if nhanes_col in df.columns:
                features_df[feature_name] = pd.to_numeric(df[nhanes_col], errors='coerce')
        
        # Smoking
        if 'SMQ020' in df.columns:
            features_df['smoking'] = (df['SMQ020'] == 1).astype(int)
        
        # Physical activity
        if 'PAQ605' in df.columns:
            features_df['physical_activity'] = pd.to_numeric(df['PAQ605'], errors='coerce')
        
        logger.info(f"Engineered {features_df.shape[1]} features from NHANES data")
        return features_df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features."""
        logger.info("Creating interaction features...")
        
        features_df = df.copy()
        
        # Age-BMI interaction
        if 'age' in features_df.columns and 'bmi' in features_df.columns:
            features_df['age_bmi'] = features_df['age'] * features_df['bmi']
        
        # FSH-Estradiol ratio (important for menopause)
        if 'fsh' in features_df.columns and 'estradiol' in features_df.columns:
            features_df['fsh_estradiol_ratio'] = features_df['fsh'] / (features_df['estradiol'] + 1e-6)
        
        # Hormone ratios
        if 'fsh' in features_df.columns and 'testosterone' in features_df.columns:
            features_df['fsh_testosterone_ratio'] = features_df['fsh'] / (features_df['testosterone'] + 1e-6)
        
        logger.info("Interaction features created")
        return features_df
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame:
        """Handle missing values."""
        logger.info(f"Handling missing values using {strategy} strategy...")
        
        df_clean = df.copy()
        
        # Separate numeric and categorical
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        categorical_cols = df_clean.select_dtypes(exclude=[np.number]).columns
        
        # Fill numeric with median or mean
        if strategy == 'median':
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
        elif strategy == 'mean':
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        elif strategy == 'zero':
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        
        # Fill categorical with mode
        for col in categorical_cols:
            mode_value = df_clean[col].mode()
            if len(mode_value) > 0:
                df_clean[col] = df_clean[col].fillna(mode_value[0])
        
        logger.info(f"Missing values handled. Remaining NaN: {df_clean.isna().sum().sum()}")
        return df_clean
    
    def normalize_features(self, df: pd.DataFrame, method: str = 'standard') -> pd.DataFrame:
        """Normalize features."""
        from sklearn.preprocessing import StandardScaler, MinMaxScaler
        
        logger.info(f"Normalizing features using {method} method...")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            return df
        
        df_normalized = df.copy()
        df_normalized[numeric_cols] = scaler.fit_transform(df[numeric_cols])
        
        return df_normalized, scaler

