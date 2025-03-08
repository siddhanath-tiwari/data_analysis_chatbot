"""
Data analysis functions.
"""
from typing import Dict, Any, List, Union, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import json
from loguru import logger
import traceback

from data_analysis_chatbot.data_analysis.processors import preprocess_data


class DataAnalyzer:
    """
    Data analyzer for performing various data analysis tasks.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the data analyzer.
        
        Args:
            config: Configuration for the analyzer
        """
        self.config = config or {}
        logger.info("Data analyzer initialized")
    
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform basic analysis on a DataFrame.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Basic info
            result = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "null_counts": df.isnull().sum().to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum() / (1024 * 1024),  # in MB
            }
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if numeric_cols:
                result["numeric_analysis"] = {}
                for col in numeric_cols:
                    result["numeric_analysis"][col] = {
                        "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                        "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                        "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                        "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                        "std": float(df[col].std()) if not pd.isna(df[col].std()) else None,
                        "skew": float(df[col].skew()) if not pd.isna(df[col].skew()) else None,
                    }
            
            # Categorical columns analysis
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            if cat_cols:
                result["categorical_analysis"] = {}
                for col in cat_cols:
                    value_counts = df[col].value_counts().head(10).to_dict()
                    result["categorical_analysis"][col] = {
                        "unique_count": df[col].nunique(),
                        "top_values": {str(k): int(v) for k, v in value_counts.items()},
                    }
            
            # Datetime columns analysis
            date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
            if date_cols:
                result["datetime_analysis"] = {}
                for col in date_cols:
                    result["datetime_analysis"][col] = {
                        "min": df[col].min().isoformat() if not pd.isna(df[col].min()) else None,
                        "max": df[col].max().isoformat() if not pd.isna(df[col].max()) else None,
                        "range_days": (df[col].max() - df[col].min()).days if not pd.isna(df[col].min