# LabData ETL Pipeline

## Overview

Chemistry-aware ETL pipeline for pharmaceutical laboratory data processing with domain-specific validation rules.

## Features

- **pH Validation**: Chemistry-aware pH range checking (0-14 scale)
- **Concentration Converter**: Multi-unit converter (mg/mL, µM, mM, g/L)
- **Temperature Validator**: Celsius/Fahrenheit/Kelvin support with safety checks
- **Data Quality Reports**: Comprehensive validation metrics
- **Production-Ready**: Error handling, logging, type hints

## Technologies

- Python 3.10+
- pandas, sqlite3
- Type hints for production code quality

## Quick Start

```bash
# Install dependencies

pip install -r requirements.txt

# Run pipeline

python src/pipeline.py

# View results

sqlite3 pharma_data.db "SELECT * FROM experiments LIMIT 5;"
Project Structure
01-labdata-etl-pipeline/
├── src/
│   ├── validators.py      # Domain validation logic
│   └── pipeline.py         # ETL workflow
├── data/
│   └── sample_experiment.csv
├── tests/
└── README.md

## Example Output

✓ Processed 100 records
✓ 95 passed validation
✗ 5 failed (pH out of range)

Author
Chemistry MSc → Data Engineer | Pharmaceutical domain expertise

