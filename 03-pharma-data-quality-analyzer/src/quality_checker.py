"""
Quality Checker - Comprehensive data quality assessment
Author: MSc Chemistry → Data Engineer
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityChecker:
    """Calculate data quality metrics for pharmaceutical datasets"""
    
    # Chemistry domain rules
    DOMAIN_RULES = {
        'ph': {'min': 0.0, 'max': 14.0},
        'temperature': {'min': -273.15, 'max': 1000.0},  # Celsius
        'concentration': {'min': 0.0}
    }
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize quality checker
        
        Args:
            df: Input DataFrame
        """
        self.df = df
        self.metrics = {}
        
    def calculate_all_metrics(self) -> Dict:
        """
        Calculate all quality metrics
        
        Returns:
            Dictionary with quality scores
        """
        logger.info("Calculating quality metrics...")
        
        self.metrics = {
            'completeness': self._calculate_completeness(),
            'accuracy': self._calculate_accuracy(),
            'consistency': self._calculate_consistency(),
            'uniqueness': self._calculate_uniqueness(),
            'overall_score': 0.0
        }
        
        # Calculate overall score (weighted average)
        self.metrics['overall_score'] = self._calculate_overall_score()
        
        logger.info(f"✅ Overall Quality Score: {self.metrics['overall_score']:.1f}%")
        return self.metrics
    
    def _calculate_completeness(self) -> Dict:
        """
        Calculate completeness score (% of non-null values)
        
        Returns:
            Completeness metrics
        """
        total_cells = self.df.size
        non_null_cells = self.df.count().sum()
        
        completeness_score = (non_null_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Per-column completeness
        column_completeness = {}
        for col in self.df.columns:
            non_null = self.df[col].count()
            total = len(self.df)
            pct = (non_null / total * 100) if total > 0 else 0
            column_completeness[col] = {
                'non_null': int(non_null),
                'total': int(total),
                'percentage': float(pct)
            }
        
        return {
            'score': float(completeness_score),
            'total_cells': int(total_cells),
            'non_null_cells': int(non_null_cells),
            'missing_cells': int(total_cells - non_null_cells),
            'by_column': column_completeness
        }
    
    def _calculate_accuracy(self) -> Dict:
        """
        Calculate accuracy score (% of valid values per domain rules)
        
        Returns:
            Accuracy metrics
        """
        total_numeric_values = 0
        valid_values = 0
        violations = []
        
        for col in self.df.columns:
            # Check if column matches domain rule
            col_lower = col.lower()
            
            if col_lower in self.DOMAIN_RULES:
                rule = self.DOMAIN_RULES[col_lower]
                
                # Get non-null numeric values
                values = self.df[col].dropna()
                
                if pd.api.types.is_numeric_dtype(values):
                    total_numeric_values += len(values)
                    
                    # Check min constraint
                    if 'min' in rule:
                        invalid_min = values < rule['min']
                        valid_values += (len(values) - invalid_min.sum())
                        
                        if invalid_min.any():
                            invalid_indices = self.df[self.df[col] < rule['min']].index.tolist()
                            for idx in invalid_indices[:5]:  # Show first 5
                                violations.append({
                                    'row': int(idx),
                                    'column': col,
                                    'value': float(self.df.loc[idx, col]),
                                    'rule': f'min={rule["min"]}',
                                    'type': 'below_minimum'
                                })
                    
                    # Check max constraint
                    if 'max' in rule:
                        invalid_max = values > rule['max']
                        
                        if invalid_max.any():
                            # Subtract already counted violations
                            valid_values -= invalid_max.sum()
                            
                            invalid_indices = self.df[self.df[col] > rule['max']].index.tolist()
                            for idx in invalid_indices[:5]:  # Show first 5
                                violations.append({
                                    'row': int(idx),
                                    'column': col,
                                    'value': float(self.df.loc[idx, col]),
                                    'rule': f'max={rule["max"]}',
                                    'type': 'above_maximum'
                                })
        
        accuracy_score = (valid_values / total_numeric_values * 100) if total_numeric_values > 0 else 100.0
        
        return {
            'score': float(accuracy_score),
            'total_checked': int(total_numeric_values),
            'valid_values': int(valid_values),
            'violations_count': len(violations),
            'violations': violations
        }
    
    def _calculate_consistency(self) -> Dict:
        """
        Calculate consistency score (data type consistency, format consistency)
        
        Returns:
            Consistency metrics
        """
        issues = []
        total_columns = len(self.df.columns)
        consistent_columns = 0
        
        for col in self.df.columns:
            # Check if column has mixed types (e.g., numbers stored as strings)
            if self.df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    pd.to_numeric(self.df[col].dropna())
                    issues.append({
                        'column': col,
                        'issue': 'numeric_as_string',
                        'message': f'{col} contains numeric values stored as strings'
                    })
                except (ValueError, TypeError):
                    consistent_columns += 1
            else:
                consistent_columns += 1
        
        consistency_score = (consistent_columns / total_columns * 100) if total_columns > 0 else 100.0
        
        return {
            'score': float(consistency_score),
            'total_columns': int(total_columns),
            'consistent_columns': int(consistent_columns),
            'issues_count': len(issues),
            'issues': issues
        }
    
    def _calculate_uniqueness(self) -> Dict:
        """
        Calculate uniqueness score (detect duplicate records)
        
        Returns:
            Uniqueness metrics
        """
        total_rows = len(self.df)
        duplicate_rows = self.df.duplicated().sum()
        unique_rows = total_rows - duplicate_rows
        
        uniqueness_score = (unique_rows / total_rows * 100) if total_rows > 0 else 100.0
        
        # Find duplicate indices
        duplicate_indices = self.df[self.df.duplicated(keep=False)].index.tolist()
        
        return {
            'score': float(uniqueness_score),
            'total_rows': int(total_rows),
            'unique_rows': int(unique_rows),
            'duplicate_rows': int(duplicate_rows),
            'duplicate_indices': duplicate_indices[:10]  # Show first 10
        }
    
    def _calculate_overall_score(self) -> float:
        """
        Calculate weighted overall quality score
        
        Weights:
        - Completeness: 40%
        - Accuracy: 30%
        - Consistency: 20%
        - Uniqueness: 10%
        
        Returns:
            Overall quality score (0-100)
        """
        weights = {
            'completeness': 0.4,
            'accuracy': 0.3,
            'consistency': 0.2,
            'uniqueness': 0.1
        }
        
        overall = sum(
            self.metrics[metric]['score'] * weight
            for metric, weight in weights.items()
        )
        
        return round(overall, 1)
    
    def get_quality_summary(self) -> str:
        """
        Get human-readable quality summary
        
        Returns:
            Formatted summary string
        """
        if not self.metrics:
            self.calculate_all_metrics()
        
        score = self.metrics['overall_score']
        
        # Determine quality level
        if score >= 90:
            level = "EXCELLENT"
            emoji = "✓✓"
        elif score >= 75:
            level = "GOOD"
            emoji = "✓"
        elif score >= 60:
            level = "FAIR"
            emoji = "⚠"
        else:
            level = "POOR"
            emoji = "✗"
        
        summary = f"""
╔═══════════════════════════════════════════════════════╗
║          DATA QUALITY ASSESSMENT                      ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║         OVERALL QUALITY SCORE: {score:>5.1f}%              ║
║                 {level:>10} {emoji}                        ║
║                                                       ║
╠═══════════════════════════════════════════════════════╣
║ Completeness:    {self.metrics['completeness']['score']:>5.1f}%  (Weight: 40%)      ║
║ Accuracy:        {self.metrics['accuracy']['score']:>5.1f}%  (Weight: 30%)      ║
║ Consistency:     {self.metrics['consistency']['score']:>5.1f}%  (Weight: 20%)      ║
║ Uniqueness:      {self.metrics['uniqueness']['score']:>5.1f}%  (Weight: 10%)      ║
╚═══════════════════════════════════════════════════════╝
"""
        return summary


def demo():
    """Demo the quality checker"""
    print("=" * 60)
    print("Quality Checker Demo")
    print("=" * 60)
    
    # Create sample data with quality issues
    sample_data = {
        'experiment_id': [f'EXP{i:03d}' for i in range(1, 101)],
        'compound_name': ['Aspirin'] * 50 + ['Ibuprofen'] * 50,
        'ph': [7.4, 6.8, 7.2, None, 8.5, 15.5, -0.5] + [7.0] * 93,  # Some invalid pH
        'temperature': [25.0, 22.0, 24.0, 20.0, 23.0, -300.0] + [25.0] * 94,  # One invalid temp
        'concentration': [100, 50, 75, 200, None, -10] + [100] * 94,  # Negative concentration
        'batch_number': [f'BATCH{i:03d}' for i in range(1, 101)]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Check quality
    checker = QualityChecker(df)
    metrics = checker.calculate_all_metrics()
    
    # Display summary
    print(checker.get_quality_summary())
    
    # Show details
    print("\nDETAILED BREAKDOWN:")
    print("-" * 60)
    print(f"\nCompleteness: {metrics['completeness']['score']:.1f}%")
    print(f"  Missing cells: {metrics['completeness']['missing_cells']}/{metrics['completeness']['total_cells']}")
    
    print(f"\nAccuracy: {metrics['accuracy']['score']:.1f}%")
    if metrics['accuracy']['violations']:
        print(f"  Violations found: {metrics['accuracy']['violations_count']}")
        print("  Sample violations:")
        for v in metrics['accuracy']['violations'][:3]:
            print(f"    - Row {v['row']}, {v['column']}: {v['value']} ({v['type']})")
    
    print(f"\nConsistency: {metrics['consistency']['score']:.1f}%")
    print(f"  Consistent columns: {metrics['consistency']['consistent_columns']}/{metrics['consistency']['total_columns']}")
    
    print(f"\nUniqueness: {metrics['uniqueness']['score']:.1f}%")
    print(f"  Duplicates: {metrics['uniqueness']['duplicate_rows']}/{metrics['uniqueness']['total_rows']}")
    
    print("\n" + "=" * 60)
    print("✅ Quality Checker Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
