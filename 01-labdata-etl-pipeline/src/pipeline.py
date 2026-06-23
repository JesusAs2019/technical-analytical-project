"""
LabData ETL Pipeline - Pharmaceutical Laboratory Data Processing
Author: MSc Chemistry → Data Engineer
"""

import pandas as pd
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime

from validators import PharmaceuticalValidator, generate_quality_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LabDataPipeline:
    """ETL Pipeline for pharmaceutical laboratory data"""
    
    def __init__(self, db_path: str = "pharma_data.db"):
        """
        Initialize pipeline with database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.validator = PharmaceuticalValidator()
        self.validation_errors = []
        
    def extract(self, csv_path: str) -> pd.DataFrame:
        """
        Extract data from CSV file
        
        Args:
            csv_path: Path to source CSV file
            
        Returns:
            DataFrame with raw laboratory data
        """
        logger.info(f"Extracting data from {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Extracted {len(df)} records")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            raise
    
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Transform and validate data with domain rules
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            (cleaned_df, list_of_validation_errors)
        """
        logger.info("Transforming data with chemistry validation rules")
        
        errors = []
        valid_records = []
        
        for idx, row in df.iterrows():
            # Convert row to dict for validation
            record = row.to_dict()
            
            # Validate pH (convert to float first)
            try:
                ph_value = float(record.get('ph', 0))
            except (ValueError, TypeError):
                ph_value = 0
                
            is_valid_ph, ph_error = self.validator.validate_ph(ph_value)
            
            # Validate temperature (convert to float first)
            try:
                temp_value = float(record.get('temperature', 0))
            except (ValueError, TypeError):
                temp_value = 0
                
            is_valid_temp, temp_error = self.validator.validate_temperature(
                temp_value,
                record.get('temp_unit', 'celsius')
            )
            
            # Track errors
            if not is_valid_ph:
                errors.append(f"Row {idx}: {ph_error}")
                continue
            
            if not is_valid_temp:
                errors.append(f"Row {idx}: {temp_error}")
                continue
            
            # Add validation timestamp
            record['validated_at'] = datetime.now().isoformat()
            record['validation_status'] = 'PASS'
            
            valid_records.append(record)
        
        # Create cleaned DataFrame
        cleaned_df = pd.DataFrame(valid_records)
        
        logger.info(f"Transformation complete: {len(cleaned_df)}/{len(df)} records valid")
        
        return cleaned_df, errors
    
    def load(self, df: pd.DataFrame, table_name: str = "experiments") -> None:
        """
        Load data into SQLite database
        
        Args:
            df: Cleaned DataFrame
            table_name: Target database table
        """
        logger.info(f"Loading {len(df)} records to {self.db_path}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Create table with schema
            df.to_sql(
                table_name,
                conn,
                if_exists='replace',
                index=False
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Successfully loaded data to {table_name} table")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def run(self, csv_path: str) -> Dict:
        """
        Execute full ETL pipeline
        
        Args:
            csv_path: Path to source CSV file
            
        Returns:
            Pipeline execution summary
        """
        logger.info("=" * 60)
        logger.info("STARTING LABDATA ETL PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Extract
            raw_data = self.extract(csv_path)
            total_records = len(raw_data)
            
            # Transform
            cleaned_data, errors = self.transform(raw_data)
            valid_records = len(cleaned_data)
            
            # Load
            if not cleaned_data.empty:
                self.load(cleaned_data)
            else:
                logger.warning("No valid records to load!")
            
            # Generate quality report
            report = generate_quality_report(total_records, valid_records, errors)
            print(report)
            
            summary = {
                'total_records': total_records,
                'valid_records': valid_records,
                'failed_records': total_records - valid_records,
                'pass_rate': (valid_records / total_records * 100) if total_records > 0 else 0,
                'errors': errors
            }
            
            logger.info("Pipeline execution complete!")
            
            return summary
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


def main():
    """Main execution function"""
    
    # Define paths
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "data" / "sample_experiment.csv"
    db_path = project_root / "pharma_data.db"
    
    # Run pipeline
    pipeline = LabDataPipeline(db_path=str(db_path))
    summary = pipeline.run(str(csv_path))
    
    # Display summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Total Records:   {summary['total_records']}")
    print(f"Valid Records:   {summary['valid_records']}")
    print(f"Failed Records:  {summary['failed_records']}")
    print(f"Pass Rate:       {summary['pass_rate']:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    main()       
    
            