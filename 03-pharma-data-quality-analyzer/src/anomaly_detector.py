"""
Anomaly Detector - Statistical outlier detection for pharmaceutical data
Author: MSc Chemistry → Data Engineer
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detect outliers using multiple statistical methods"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize anomaly detector
        
        Args:
            df: Input DataFrame
        """
        self.df = df
        self.anomalies = {}
        
    def detect_all_anomalies(self) -> Dict:
        """
        Run all anomaly detection methods
        
        Returns:
            Dictionary with detected anomalies
        """
        logger.info("Running anomaly detection...")
        
        self.anomalies = {
            'z_score': self._detect_zscore_outliers(),
            'iqr': self._detect_iqr_outliers(),
            'domain_rules': self._detect_domain_violations()
        }
        
        # Count total anomalies
        total = sum(
            len(method['anomalies']) 
            for method in self.anomalies.values()
        )
        
        logger.info(f"✅ Found {total} anomalies across all methods")
        return self.anomalies
    
    def _detect_zscore_outliers(self, threshold: float = 3.0) -> Dict:
        """
        Detect outliers using Z-score method
        Z-score = (value - mean) / std_dev
        Outlier if |Z-score| > threshold (default: 3)
        
        Args:
            threshold: Z-score threshold
            
        Returns:
            Dictionary with Z-score outliers
        """
        outliers = []
        
        # Only check numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            values = self.df[col].dropna()
            
            if len(values) < 3:  # Need at least 3 values
                continue
            
            mean = values.mean()
            std = values.std()
            
            if std == 0:  # All values are the same
                continue
            
            # Calculate Z-scores
            z_scores = np.abs((values - mean) / std)
            
            # Find outliers
            outlier_mask = z_scores > threshold
            outlier_indices = values[outlier_mask].index
            
            for idx in outlier_indices:
                value = self.df.loc[idx, col]
                z_score = z_scores.loc[idx]
                
                outliers.append({
                    'row': int(idx),
                    'column': col,
                    'value': float(value),
                    'z_score': float(z_score),
                    'mean': float(mean),
                    'std': float(std)
                })
        
        return {
            'method': 'Z-Score',
            'threshold': threshold,
            'anomalies': outliers,
            'count': len(outliers)
        }
    
    def _detect_iqr_outliers(self) -> Dict:
        """
        Detect outliers using IQR (Interquartile Range) method
        IQR = Q3 - Q1
        Outlier if value < Q1 - 1.5*IQR or value > Q3 + 1.5*IQR
        
        Returns:
            Dictionary with IQR outliers
        """
        outliers = []
        
        # Only check numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            values = self.df[col].dropna()
            
            if len(values) < 4:  # Need at least 4 values for quartiles
                continue
            
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1
            
            if IQR == 0:  # No variation
                continue
            
            # Define outlier bounds
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Find outliers
            outlier_mask = (values < lower_bound) | (values > upper_bound)
            outlier_indices = values[outlier_mask].index
            
            for idx in outlier_indices:
                value = self.df.loc[idx, col]
                
                outliers.append({
                    'row': int(idx),
                    'column': col,
                    'value': float(value),
                    'Q1': float(Q1),
                    'Q3': float(Q3),
                    'IQR': float(IQR),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'type': 'below' if value < lower_bound else 'above'
                })
        
        return {
            'method': 'IQR',
            'anomalies': outliers,
            'count': len(outliers)
        }
    
    def _detect_domain_violations(self) -> Dict:
        """
        Detect violations of chemistry domain rules
        - pH: 0-14
        - Temperature: > -273.15°C (absolute zero)
        - Concentration: positive values
        
        Returns:
            Dictionary with domain violations
        """
        violations = []
        
        # pH check
        if 'ph' in self.df.columns or 'pH' in self.df.columns:
            col = 'ph' if 'ph' in self.df.columns else 'pH'
            
            if pd.api.types.is_numeric_dtype(self.df[col]):
                invalid = self.df[(self.df[col] < 0) | (self.df[col] > 14)]
                
                for idx, row in invalid.iterrows():
                    violations.append({
                        'row': int(idx),
                        'column': col,
                        'value': float(row[col]),
                        'rule': 'pH must be 0-14',
                        'type': 'invalid_ph'
                    })
        
        # Temperature check
        temp_cols = [c for c in self.df.columns if 'temp' in c.lower()]
        for col in temp_cols:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                invalid = self.df[self.df[col] < -273.15]
                
                for idx, row in invalid.iterrows():
                    violations.append({
                        'row': int(idx),
                        'column': col,
                        'value': float(row[col]),
                        'rule': 'Temperature must be > -273.15°C',
                        'type': 'below_absolute_zero'
                    })
        
        # Concentration check
        conc_cols = [c for c in self.df.columns if 'conc' in c.lower()]
        for col in conc_cols:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                invalid = self.df[self.df[col] < 0]
                
                for idx, row in invalid.iterrows():
                    violations.append({
                        'row': int(idx),
                        'column': col,
                        'value': float(row[col]),
                        'rule': 'Concentration must be positive',
                        'type': 'negative_concentration'
                    })
        
        return {
            'method': 'Domain Rules',
            'anomalies': violations,
            'count': len(violations)
        }
    
    def get_summary(self) -> str:
        """
        Get human-readable anomaly summary
        
        Returns:
            Formatted summary string
        """
        if not self.anomalies:
            self.detect_all_anomalies()
        
        total = sum(method['count'] for method in self.anomalies.values())
        
        summary = f"""
╔═══════════════════════════════════════════════════════╗
║            ANOMALY DETECTION SUMMARY                  ║
╠═══════════════════════════════════════════════════════╣
║ Total Anomalies Found: {total:>3}                          ║
╠═══════════════════════════════════════════════════════╣
║ Z-Score Method:        {self.anomalies['z_score']['count']:>3}                          ║
║ IQR Method:            {self.anomalies['iqr']['count']:>3}                          ║
║ Domain Rules:          {self.anomalies['domain_rules']['count']:>3}                          ║
╚═══════════════════════════════════════════════════════╝
"""
        return summary


def demo():
    """Demo the anomaly detector"""
    print("=" * 60)
    print("Anomaly Detector Demo")
    print("=" * 60)
    
    # Create sample data with outliers
    np.random.seed(42)
    
    sample_data = {
        'experiment_id': [f'EXP{i:03d}' for i in range(1, 101)],
        'compound_name': ['Aspirin'] * 100,
        'ph': list(np.random.normal(7.0, 0.5, 95)) + [15.5, -0.5, 16.0, 13.8, 14.2],  # Invalid pH
        'temperature': list(np.random.normal(25.0, 2.0, 97)) + [-300.0, 500.0, -50.0],  # Invalid temps
        'concentration': list(np.random.normal(100, 10, 98)) + [-10.0, -5.0]  # Negative concentrations
    }
    
    df = pd.DataFrame(sample_data)
    
    # Detect anomalies
    detector = AnomalyDetector(df)
    anomalies = detector.detect_all_anomalies()
    
    # Display summary
    print(detector.get_summary())
    
    # Show details
    print("\nDETAILED ANOMALIES:")
    print("-" * 60)
    
    for method_name, method_data in anomalies.items():
        print(f"\n{method_data['method']}:")
        
        if method_data['count'] == 0:
            print("  No anomalies detected")
        else:
            print(f"  Found {method_data['count']} anomalies")
            
            # Show first 3 examples
            for anomaly in method_data['anomalies'][:3]:
                print(f"    - Row {anomaly['row']}, {anomaly['column']}: {anomaly['value']:.2f}")
                if 'rule' in anomaly:
                    print(f"      Rule: {anomaly['rule']}")
    
    print("\n" + "=" * 60)
    print("✅ Anomaly Detector Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
