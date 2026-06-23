"""
Data Profiler - Statistical profiling for pharmaceutical datasets
Author: MSc Chemistry → Data Engineer
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProfiler:
    """Comprehensive data profiling for lab datasets"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize profiler with dataset
        
        Args:
            df: Input DataFrame
        """
        self.df = df
        self.profile = {}
        
    def generate_profile(self) -> Dict:
        """
        Generate complete data profile
        
        Returns:
            Dictionary with profiling results
        """
        logger.info(f"Profiling dataset: {self.df.shape[0]} rows × {self.df.shape[1]} cols")
        
        self.profile = {
            'overview': self._profile_overview(),
            'columns': self._profile_columns(),
            'missing_values': self._profile_missing_values(),
            'data_types': self._profile_data_types(),
            'statistics': self._profile_statistics()
        }
        
        logger.info("✅ Profiling complete")
        return self.profile
    
    def _profile_overview(self) -> Dict:
        """Generate dataset overview"""
        return {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024:.2f} KB",
            'column_names': list(self.df.columns)
        }
    
    def _profile_columns(self) -> Dict:
        """Profile each column individually"""
        column_profiles = {}
        
        for col in self.df.columns:
            column_profiles[col] = {
                'dtype': str(self.df[col].dtype),
                'non_null': int(self.df[col].count()),
                'null': int(self.df[col].isna().sum()),
                'null_pct': float(self.df[col].isna().sum() / len(self.df) * 100),
                'unique': int(self.df[col].nunique()),
                'unique_pct': float(self.df[col].nunique() / len(self.df) * 100)
            }
            
            # Add numeric stats if applicable
            if pd.api.types.is_numeric_dtype(self.df[col]):
                column_profiles[col].update({
                    'mean': float(self.df[col].mean()) if self.df[col].count() > 0 else None,
                    'median': float(self.df[col].median()) if self.df[col].count() > 0 else None,
                    'std': float(self.df[col].std()) if self.df[col].count() > 1 else None,
                    'min': float(self.df[col].min()) if self.df[col].count() > 0 else None,
                    'max': float(self.df[col].max()) if self.df[col].count() > 0 else None
                })
        
        return column_profiles
    
    def _profile_missing_values(self) -> Dict:
        """Analyze missing values"""
        missing = self.df.isna().sum()
        missing_pct = (missing / len(self.df) * 100).round(2)
        
        return {
            'total_missing': int(missing.sum()),
            'total_cells': int(self.df.size),
            'missing_pct': float(missing.sum() / self.df.size * 100),
            'by_column': {
                col: {
                    'count': int(missing[col]),
                    'percentage': float(missing_pct[col])
                }
                for col in self.df.columns if missing[col] > 0
            }
        }
    
    def _profile_data_types(self) -> Dict:
        """Analyze data types"""
        type_counts = self.df.dtypes.value_counts().to_dict()
        
        return {
            'type_distribution': {str(k): int(v) for k, v in type_counts.items()},
            'numeric_columns': list(self.df.select_dtypes(include=[np.number]).columns),
            'text_columns': list(self.df.select_dtypes(include=['object']).columns),
            'datetime_columns': list(self.df.select_dtypes(include=['datetime64']).columns)
        }
    
    def _profile_statistics(self) -> Dict:
        """Generate statistical summaries"""
        numeric_df = self.df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {'message': 'No numeric columns found'}
        
        return {
            'correlation': numeric_df.corr().to_dict() if len(numeric_df.columns) > 1 else {},
            'describe': numeric_df.describe().to_dict()
        }
    
    def get_summary(self) -> str:
        """
        Get human-readable summary
        
        Returns:
            Formatted summary string
        """
        if not self.profile:
            self.generate_profile()
        
        overview = self.profile['overview']
        missing = self.profile['missing_values']
        
        summary = f"""
╔═══════════════════════════════════════════════════════╗
║             DATA PROFILE SUMMARY                      ║
╠═══════════════════════════════════════════════════════╣
║ Rows:           {overview['rows']:>10}                     ║
║ Columns:        {overview['columns']:>10}                     ║
║ Memory Usage:   {overview['memory_usage']:>10}                ║
║ Missing Values: {missing['total_missing']:>10} ({missing['missing_pct']:.1f}%)          ║
╚═══════════════════════════════════════════════════════╝
"""
        return summary


def demo():
    """Demo the profiler"""
    print("=" * 60)
    print("Data Profiler Demo")
    print("=" * 60)
    
    # Create sample data
    sample_data = {
        'experiment_id': [f'EXP{i:03d}' for i in range(1, 101)],
        'compound_name': ['Aspirin'] * 50 + ['Ibuprofen'] * 50,
        'ph': [7.4, 6.8, 7.2, None, 8.5] * 20,
        'temperature': [25.0, 22.0, 24.0, 20.0, 23.0] * 20,
        'concentration': [100, 50, 75, 200, None] * 20,
        'batch_number': [f'BATCH{i:03d}' for i in range(1, 101)]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Profile the data
    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    
    # Display summary
    print(profiler.get_summary())
    
    # Show column details
    print("\nCOLUMN DETAILS:")
    print("-" * 60)
    for col, details in profile['columns'].items():
        print(f"\n{col}:")
        print(f"  Type: {details['dtype']}")
        print(f"  Non-null: {details['non_null']}/{profile['overview']['rows']}")
        print(f"  Unique: {details['unique']} ({details['unique_pct']:.1f}%)")
        if 'mean' in details and details['mean'] is not None:
            print(f"  Mean: {details['mean']:.2f}")
            print(f"  Range: [{details['min']:.2f}, {details['max']:.2f}]")
    
    print("\n" + "=" * 60)
    print("✅ Profiler Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
