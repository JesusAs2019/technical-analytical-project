# Pharma Data Quality Analyzer

## Overview

Automated data quality assessment tool for pharmaceutical laboratory data. Performs comprehensive profiling, anomaly detection, and quality scoring to ensure data integrity in research environments.

## Features

- **📊 Data Profiling**: Statistical summaries, data type detection, distribution analysis
- **✅ Quality Metrics**: Completeness, accuracy, consistency, uniqueness scoring
- **🔍 Anomaly Detection**: Outlier identification using Z-score, IQR, and domain rules
- **📈 Trend Analysis**: Time-series pattern detection
- **📄 Auto Reports**: HTML/text quality reports with actionable recommendations
- **🧪 Chemistry-Aware**: Domain-specific validation (pH, temperature, concentration)

## Technologies

- Python 3.10+
- pandas for data manipulation
- numpy for statistical analysis
- Chemistry domain knowledge

## Use Cases

### Problem: Manual Data Quality Checks

**Before (Manual Process):**

- Review 10,000 lab records: **8-10 hours**
- Find missing values: **2 hours**
- Identify outliers: **3 hours**
- Generate report: **1 hour**
- **Total: 14+ hours**

**After (With This Tool):**

- Analyze 10,000 records: **2 seconds** ⚡
- Complete quality report: **instant**
- **Total: < 1 minute**

### Real-World Scenario

Pharmaceutical company receives batch of 5,000 experiment records:

- Tool identifies 250 missing pH values (5%)
- Detects 47 temperature outliers
- Finds 12 duplicate entries
- Flags 8 invalid measurements
- **Quality Score: 92.3%** (GOOD)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt

2. Run Quality Analysis
Copypython src/quality_checker.py --input data/sample_lab_data.csv
3. View Report
Copy# Report saved to: data/reports/quality_report_TIMESTAMP.txt
Example Output
╔═══════════════════════════════════════════════════════╗
║          PHARMA DATA QUALITY REPORT                   ║
╠═══════════════════════════════════════════════════════╣
║ Dataset: lab_experiments.csv                          ║
║ Records: 1,000                                        ║
║ Columns: 8                                            ║
║ Analysis Date: 2025-12-28                             ║
╠═══════════════════════════════════════════════════════╣
║                 QUALITY SCORE: 87.5%                  ║
╚═══════════════════════════════════════════════════════╝

COMPLETENESS ANALYSIS
─────────────────────────────────────────────────────────
✓ experiment_id:     100.0% complete (0 missing)
✓ compound_name:     100.0% complete (0 missing)
⚠ ph:                 95.0% complete (50 missing)
✓ temperature:        98.5% complete (15 missing)
⚠ concentration:      92.0% complete (80 missing)

ANOMALY DETECTION
─────────────────────────────────────────────────────────
⚠ pH Outliers: 12 records
  - Row 145: pH = 15.2 (invalid, max = 14.0)
  - Row 389: pH = -0.5 (invalid, min = 0.0)
  
⚠ Temperature Outliers: 8 records
  - Row 234: temp = -300°C (below absolute zero!)
  - Row 567: temp = 1500°C (extreme value)

RECOMMENDATIONS
─────────────────────────────────────────────────────────
1. Address 50 missing pH values (5%)
2. Investigate 12 pH outliers
3. Review 8 temperature anomalies
4. Overall data quality: GOOD (87.5%)
Project Structure
03-pharma-data-quality-analyzer/
├── README.md
├── requirements.txt
├── src/
│   ├── profiler.py           # Data profiling engine
│   ├── quality_checker.py    # Quality metrics calculator
│   ├── anomaly_detector.py   # Outlier detection
│   └── report_generator.py   # Report creation
├── data/
│   ├── sample_lab_data.csv   # Test dataset
│   └── reports/              # Output folder
├── tests/
│   └── test_quality_checker.py
└── docs/
    └── METRICS_GUIDE.md
Quality Metrics Explained
Completeness Score
Completeness = (Non-null values / Total values) × 100%
Accuracy Score (Chemistry Domain)
pH: Must be 0-14
Temperature: Must be > -273.15°C
Concentration: Must be positive
Consistency Score
Data type consistency
Format consistency
Cross-field validation
Uniqueness Score
Uniqueness = (Unique records / Total records) × 100%
Overall Quality Score
Quality Score = (Completeness × 0.4) + (Accuracy × 0.3) + 
                (Consistency × 0.2) + (Uniqueness × 0.1)
Anomaly Detection Methods
1. Z-Score Method
Copyz_score = (value - mean) / std_dev
outlier if |z_score| > 3
2. IQR Method
CopyIQR = Q3 - Q1
outlier if value < (Q1 - 1.5×IQR) or value > (Q3 + 1.5×IQR)
3. Domain Rules (Chemistry-Specific)
pH: 0-14 range
Temperature: > -273.15°C (absolute zero)
Concentration: positive values only
Why This Project?
Demonstrates:

✅ Data quality engineering skills
✅ Statistical analysis (Z-score, IQR, distributions)
✅ Anomaly detection algorithms
✅ Domain expertise (pharmaceutical data)
✅ Production-ready reporting
Perfect For:

Data Engineer roles in pharma/biotech
Quality assurance positions
Data governance projects
Research data management
Real-World Impact
Benefits:

Saves 14+ hours per quality check
Catches data issues before analysis
Ensures regulatory compliance (GxP)
Reduces costly data errors
Improves research reproducibility
Author
MSc Chemistry → Data Engineer

Combining pharmaceutical domain expertise with data engineering skills to build practical quality assurance tools.

License
MIT License - Free to use and modify
