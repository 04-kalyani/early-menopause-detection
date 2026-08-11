"""
Data loading utilities for SWAN and NHANES datasets.
"""
import pandas as pd
import numpy as np
import pyreadstat
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and combine SWAN and NHANES datasets."""
    
    def __init__(self, datasets_path: str = "../datasets"):
        self.datasets_path = Path(datasets_path)
        self.swan_path = self.datasets_path / "ICPSR_28762"  # Baseline
        self.nhanes_path = self.datasets_path
        
    def load_swan_baseline(self) -> pd.DataFrame:
        """Load SWAN baseline dataset."""
        logger.info("Loading SWAN baseline dataset...")
        data_file = self.swan_path / "DS0001" / "28762-0001-Data.tsv"
        
        if not data_file.exists():
            raise FileNotFoundError(f"SWAN baseline data not found at {data_file}")
        
        df = pd.read_csv(data_file, sep='\t', low_memory=False)
        logger.info(f"Loaded SWAN baseline: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def load_swan_visits(self) -> Dict[str, pd.DataFrame]:
        """Load all SWAN visit datasets."""
        logger.info("Loading SWAN visit datasets...")
        visits = {}
        
        visit_mapping = {
            "visit_01": "ICPSR_29221",
            "visit_02": "ICPSR_29401",
            "visit_03": "ICPSR_29701",
            "visit_04": "ICPSR_30142",
            "visit_05": "ICPSR_30501",
            "visit_06": "ICPSR_31181",
            "visit_07": "ICPSR_31901",
            "visit_08": "ICPSR_32122",
            "visit_10": "ICPSR_32961",  # Note: Visit 09 missing
        }
        
        for visit_name, icpsr_id in visit_mapping.items():
            visit_path = self.datasets_path / icpsr_id / "DS0001"
            data_files = list(visit_path.glob("*-Data.tsv"))
            
            if data_files:
                df = pd.read_csv(data_files[0], sep='\t', low_memory=False)
                visits[visit_name] = df
                logger.info(f"Loaded {visit_name}: {df.shape[0]} rows")
            else:
                logger.warning(f"No data file found for {visit_name}")
        
        return visits
    
    def load_nhanes_demographics(self) -> pd.DataFrame:
        """Load NHANES demographics data."""
        logger.info("Loading NHANES demographics...")
        file_path = self.nhanes_path / "DEMO_H.xpt"
        
        if not file_path.exists():
            raise FileNotFoundError(f"NHANES demographics not found at {file_path}")
        
        df, meta = pyreadstat.read_xport(str(file_path))
        logger.info(f"Loaded NHANES demographics: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def load_nhanes_hormones(self) -> pd.DataFrame:
        """Load NHANES sex steroid hormone data."""
        logger.info("Loading NHANES hormone data...")
        file_path = self.nhanes_path / "TST_H.xpt"
        
        if not file_path.exists():
            raise FileNotFoundError(f"NHANES hormones not found at {file_path}")
        
        df, meta = pyreadstat.read_xport(str(file_path))
        logger.info(f"Loaded NHANES hormones: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def load_nhanes_body_measures(self) -> pd.DataFrame:
        """Load NHANES body measures (BMI, weight, height)."""
        logger.info("Loading NHANES body measures...")
        file_path = self.nhanes_path / "BMX_H.xpt"
        
        if not file_path.exists():
            raise FileNotFoundError(f"NHANES body measures not found at {file_path}")
        
        df, meta = pyreadstat.read_xport(str(file_path))
        logger.info(f"Loaded NHANES body measures: {df.shape[0]} rows")
        return df
    
    def load_nhanes_questionnaires(self) -> Dict[str, pd.DataFrame]:
        """Load NHANES questionnaire data."""
        logger.info("Loading NHANES questionnaires...")
        questionnaires = {}
        
        q_files = {
            "smoking": "SMQ_H.xpt",
            "physical_activity": "PAQ_H.xpt",
            "womens_health": "WHQ_H.xpt",
        }
        
        for q_name, filename in q_files.items():
            file_path = self.nhanes_path / filename
            if file_path.exists():
                df, meta = pyreadstat.read_xport(str(file_path))
                questionnaires[q_name] = df
                logger.info(f"Loaded {q_name}: {df.shape[0]} rows")
            else:
                logger.warning(f"Questionnaire {q_name} not found at {file_path}")
        
        return questionnaires
    
    def load_nhanes_biochemistry(self) -> pd.DataFrame:
        """Load NHANES biochemistry profile."""
        logger.info("Loading NHANES biochemistry...")
        file_path = self.nhanes_path / "BIOPRO_H.xpt"
        
        if not file_path.exists():
            raise FileNotFoundError(f"NHANES biochemistry not found at {file_path}")
        
        df, meta = pyreadstat.read_xport(str(file_path))
        logger.info(f"Loaded NHANES biochemistry: {df.shape[0]} rows")
        return df
    
    def combine_swan_data(self) -> pd.DataFrame:
        """Combine SWAN baseline with all visits."""
        logger.info("Combining SWAN datasets...")
        
        baseline = self.load_swan_baseline()
        visits = self.load_swan_visits()
        
        # Start with baseline
        combined = baseline.copy()
        
        # Add visit data (stack vertically for longitudinal analysis)
        visit_dataframes = [baseline]
        for visit_name, visit_df in visits.items():
            visit_dataframes.append(visit_df)
        
        # Combine all visits
        combined = pd.concat(visit_dataframes, ignore_index=True)
        
        logger.info(f"Combined SWAN data: {combined.shape[0]} rows, {combined.shape[1]} columns")
        return combined
    
    def combine_nhanes_data(self) -> pd.DataFrame:
        """Combine all NHANES datasets."""
        logger.info("Combining NHANES datasets...")
        
        # Load all components
        demo = self.load_nhanes_demographics()
        hormones = self.load_nhanes_hormones()
        body = self.load_nhanes_body_measures()
        biochem = self.load_nhanes_biochemistry()
        questionnaires = self.load_nhanes_questionnaires()
        
        # Merge on SEQN (NHANES participant ID)
        combined = demo.copy()
        
        # Merge hormones
        if 'SEQN' in hormones.columns:
            combined = combined.merge(hormones, on='SEQN', how='left', suffixes=('', '_horm'))
        
        # Merge body measures
        if 'SEQN' in body.columns:
            combined = combined.merge(body, on='SEQN', how='left', suffixes=('', '_body'))
        
        # Merge biochemistry
        if 'SEQN' in biochem.columns:
            combined = combined.merge(biochem, on='SEQN', how='left', suffixes=('', '_biochem'))
        
        # Merge questionnaires
        for q_name, q_df in questionnaires.items():
            if 'SEQN' in q_df.columns:
                combined = combined.merge(q_df, on='SEQN', how='left', suffixes=('', f'_{q_name}'))
        
        logger.info(f"Combined NHANES data: {combined.shape[0]} rows, {combined.shape[1]} columns")
        return combined

