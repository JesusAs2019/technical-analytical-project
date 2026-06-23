"""
Report Generator - Comprehensive quality reports for pharmaceutical data
Author: MSc Chemistry → Data Engineer
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

from profiler import DataProfiler
from quality_checker import QualityChecker
from anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate comprehensive data quality reports"""
    
    def __init__(self, df: pd.DataFrame, dataset_name: str = "Dataset"):
        """
        Initialize report generator
        
        Args:
            df: Input DataFrame
            dataset_name: Name of the dataset
        """
        self.df = df
        self.dataset_name = dataset_name
        self.timestamp = datetime.now()
        
        # Initialize components
        self.profiler = DataProfiler(df)
        self.quality_checker = QualityChecker(df)
        self.anomaly_detector = AnomalyDetector(df)
        
    def generate_full_report(self) -> str:
        """
        Generate complete quality report
        
        Returns:
            Formatted report string
        """
        logger.info("Generating comprehensive quality report...")
        
        # Run all analyses
        profile = self.profiler.generate_profile()
        quality_metrics = self.quality_checker.calculate_all_metrics()
        anomalies = self.anomaly_detector.detect_all_anomalies()
        
        # Build report
        report = self._build_header()
        report += self._build_overview_section(profile)
        report += self._build_quality_section(quality_metrics)
        report += self._build_completeness_section(quality_metrics)
        report += self._build_anomaly_section(anomalies)
        report += self._build_recommendations_section(quality_metrics, anomalies)
        report += self._build_footer()
        
        logger.info("✅ Report generation complete")
        return report
    
    def _build_header(self) -> str:
        """Build report header"""
        return f"""
╔═══════════════════════════════════════════════════════╗
║       PHARMA DATA QUALITY REPORT                      ║
╠═══════════════════════════════════════════════════════╣
║ Dataset:        {self.dataset_name:<35} ║
║ Records:        {len(self.df):<35} ║
║ Columns:        {len(self.df.columns):<35} ║
║ Analysis Date:  {self.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<35} ║
╚═══════════════════════════════════════════════════════╝

"""
    
    def _build_overview_section(self, profile: Dict) -> str:
        """Build overview section"""
        overview = profile['overview']
        missing = profile['missing_values']
        
        return f"""
DATASET OVERVIEW
{'='*60}
Rows:              {overview['rows']}
Columns:           {overview['columns']}
Memory Usage:      {overview['memory_usage']}
Missing Values:    {missing['total_missing']} ({missing['missing_pct']:.1f}%)
Column Names:      {', '.join(overview['column_names'][:5])}{'...' if len(overview['column_names']) > 5 else ''}

"""
    
    def _build_quality_section(self, metrics: Dict) -> str:
        """Build quality metrics section"""
        score = metrics['overall_score']
        
        # Determine quality level
        if score >= 90:
            level = "EXCELLENT ✓✓"
        elif score >= 75:
            level = "GOOD ✓"
        elif score >= 60:
            level = "FAIR ⚠"
        else:
            level = "POOR ✗"
        
        return f"""
╔═══════════════════════════════════════════════════════╗
║             OVERALL QUALITY SCORE                     ║
║                                                       ║
║                   {score:.1f}%                               ║
║                 {level:<10}                         ║
╚═══════════════════════════════════════════════════════╝

QUALITY BREAKDOWN
{'='*60}
Completeness:      {metrics['completeness']['score']:>6.1f}%  (Weight: 40%)
Accuracy:          {metrics['accuracy']['score']:>6.1f}%  (Weight: 30%)
Consistency:       {metrics['consistency']['score']:>6.1f}%  (Weight: 20%)
Uniqueness:        {metrics['uniqueness']['score']:>6.1f}%  (Weight: 10%)

"""
    
    def _build_completeness_section(self, metrics: Dict) -> str:
        """Build completeness analysis section"""
        completeness = metrics['completeness']
        
        section = """
COMPLETENESS ANALYSIS
{'='*60}
"""
        
        for col, details in completeness['by_column'].items():
            pct = details['percentage']
            status = "✓" if pct == 100 else "⚠" if pct >= 90 else "✗"
            
            section += f"{status} {col:<20} {pct:>5.1f}% complete ({details['total'] - details['non_null']} missing)\n"
        
        return section + "\n"
    
    def _build_anomaly_section(self, anomalies: Dict) -> str:
        """Build anomaly detection section"""
        total = sum(method['count'] for method in anomalies.values())
        
        section = f"""
ANOMALY DETECTION
{'='*60}
Total Anomalies Found: {total}

"""
        
        # Z-Score anomalies
        if anomalies['z_score']['count'] > 0:
            section += f"⚠ Z-Score Outliers: {anomalies['z_score']['count']} records\n"
            for anomaly in anomalies['z_score']['anomalies'][:5]:
                section += f"  - Row {anomaly['row']}, {anomaly['column']}: {anomaly['value']:.2f} (z-score: {anomaly['z_score']:.2f})\n"
            if anomalies['z_score']['count'] > 5:
                section += f"  ... and {anomalies['z_score']['count'] - 5} more\n"
            section += "\n"
        
        # Domain violations
        if anomalies['domain_rules']['count'] > 0:
            section += f"⚠ Domain Rule Violations: {anomalies['domain_rules']['count']} records\n"
            for anomaly in anomalies['domain_rules']['anomalies'][:5]:
                section += f"  - Row {anomaly['row']}, {anomaly['column']}: {anomaly['value']:.2f}\n"
                section += f"    Rule: {anomaly['rule']}\n"
            if anomalies['domain_rules']['count'] > 5:
                section += f"  ... and {anomalies['domain_rules']['count'] - 5} more\n"
            section += "\n"
        
        # IQR anomalies
        if anomalies['iqr']['count'] > 0:
            section += f"⚠ IQR Outliers: {anomalies['iqr']['count']} records\n"
            for anomaly in anomalies['iqr']['anomalies'][:3]:
                section += f"  - Row {anomaly['row']}, {anomaly['column']}: {anomaly['value']:.2f}\n"
            if anomalies['iqr']['count'] > 3:
                section += f"  ... and {anomalies['iqr']['count'] - 3} more\n"
            section += "\n"
        
        if total == 0:
            section += "✓ No anomalies detected\n\n"
        
        return section
    
    def _build_recommendations_section(self, metrics: Dict, anomalies: Dict) -> str:
        """Build recommendations section"""
        recommendations = []
        
        # Check completeness
        missing_count = metrics['completeness']['missing_cells']
        if missing_count > 0:
            pct = (missing_count / metrics['completeness']['total_cells'] * 100)
            recommendations.append(f"Address {missing_count} missing values ({pct:.1f}% of data)")
        
        # Check accuracy violations
        if metrics['accuracy']['violations_count'] > 0:
            recommendations.append(f"Investigate {metrics['accuracy']['violations_count']} accuracy violations")
        
        # Check anomalies
        total_anomalies = sum(method['count'] for method in anomalies.values())
        if total_anomalies > 0:
            recommendations.append(f"Review {total_anomalies} detected anomalies")
        
        # Check duplicates
        if metrics['uniqueness']['duplicate_rows'] > 0:
            recommendations.append(f"Remove {metrics['uniqueness']['duplicate_rows']} duplicate records")
        
        # Overall assessment
        score = metrics['overall_score']
        if score >= 90:
            recommendations.append("Overall data quality: EXCELLENT - Proceed with confidence")
        elif score >= 75:
            recommendations.append("Overall data quality: GOOD - Minor issues to address")
        elif score >= 60:
            recommendations.append("Overall data quality: FAIR - Significant improvements needed")
        else:
            recommendations.append("Overall data quality: POOR - Major data cleaning required")
        
        section = """
RECOMMENDATIONS
{'='*60}
"""
        
        for i, rec in enumerate(recommendations, 1):
            section += f"{i}. {rec}\n"
        
        return section + "\n"
    
    def _build_footer(self) -> str:
        """Build report footer"""
        return f"""
{'='*60}
Report generated by Pharma Data Quality Analyzer
Author: MSc Chemistry → Data Engineer
Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
    
    def save_report(self, output_dir: str = "data/reports") -> Path:
        """
        Save report to file
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to saved report
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate report
        report = self.generate_full_report()
        
        # Create filename
        timestamp = self.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"quality_report_{timestamp}.txt"
        file_path = output_path / filename
        
        # Save to file
        file_path.write_text(report, encoding='utf-8')
        logger.info(f"💾 Report saved to: {file_path}")
        
        return file_path


def demo():
    """Demo the report generator"""
    print("=" * 60)
    print("Report Generator Demo")
    print("=" * 60)
    
    # Create sample data with various quality issues
    import numpy as np
    np.random.seed(42)
    
    sample_data = {
        'experiment_id': [f'EXP{i:03d}' for i in range(1, 101)],
        'compound_name': ['Aspirin'] * 50 + ['Ibuprofen'] * 50,
        'ph': list(np.random.normal(7.0, 0.5, 95)) + [None, 15.5, -0.5, None, 14.2],
        'temperature': list(np.random.normal(25.0, 2.0, 96)) + [None, -300.0, 500.0, None],
        'concentration': list(np.random.normal(100, 10, 97)) + [None, -10.0, None],
        'batch_number': [f'BATCH{i:03d}' for i in range(1, 101)],
        'scientist': ['Dr. Smith'] * 100
    }
    
    df = pd.DataFrame(sample_data)
    
    # Generate report
    generator = ReportGenerator(df, dataset_name="lab_experiments.csv")
    report = generator.generate_full_report()
    
    # Display report
    print("\n" + report)
    
    # Save to file
    file_path = generator.save_report()
    print(f"\n✅ Full report saved to: {file_path}")
    
    print("\n" + "=" * 60)
    print("✅ Report Generator Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
