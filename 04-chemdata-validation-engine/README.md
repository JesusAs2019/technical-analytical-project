# ChemData Validation Engine

A starter Python project for domain-aware chemical data ingestion, validation, and basic 3D molecular visualization.

## Features
- JSON / CSV ingestion
- Pydantic schema validation
- RDKit-based SMILES validation
- Molecular property calculation
- Validation report generation
- Simple browser-based 3D viewer demo

## Project Structure
- `src/schemas.py` → data contracts
- `src/ingestion.py` → file loading and report saving
- `src/validator.py` → chemistry validation logic
- `src/viewer.py` → 3D HTML viewer generation
- `src/main.py` → pipeline entry point

## Example Run

```bash
python src/main.py --input data/sample_compounds.json --viewer-compound-id CMP001
Absolutely — below is a **GitHub-ready README** you can paste directly into **Project 4: `04-chemdata-validation-engine`**, followed by a **professional GitHub project description** and a **portfolio summary** you can use in your main repo README, LinkedIn, or portfolio site.

---

# README for Project 4

```markdown
# ChemData Validation Engine

A Python-based chemical data validation and molecular visualization demo that combines structured ingestion, schema validation, RDKit-powered chemistry checks, JSON reporting, and an analytical dashboard with 2D/3D molecular views plus bond-length and bond-angle metrics.

## Overview

The **ChemData Validation Engine** is a portfolio project designed to demonstrate how domain-aware data validation can be applied to chemical records in a practical engineering workflow. The project ingests sample compound data, validates molecular structure information, flags invalid entries, generates a structured validation report, and produces a browser-based dashboard for molecular inspection.

This project is part of the broader **technical-analytical-project** repository and showcases a blend of:

- data ingestion and validation
- scientific/chemical data handling
- molecular structure visualization
- HTML-based reporting
- test-driven portfolio development

## Key Features

- Ingests chemical records from structured sample input
- Validates compound records using Python schema and chemistry-aware checks
- Detects invalid SMILES strings and flags failed entries
- Generates a JSON validation report
- Produces a branded molecular dashboard in HTML
- Displays:
  - 2D molecular structure
  - 3D molecular viewer
  - bond length metrics
  - bond angle metrics
- Includes automated tests with `pytest`

## Dashboard Highlights

The generated dashboard is presented as an **R&D Data Accelerator System Dashboard** and includes:

- **Structure Visualization Screen**
  - 2D Molecular Structure
  - 3D Molecular Viewer
  - explanatory descriptions below both panels

- **Geometric Metrics Screen**
  - Bond Length Metrics
  - Bond Angle Metrics
  - explanatory descriptions below both metric tables

- **Molecular Graph Inspector**
  - isolate molecule ID
  - molecular formula
  - molecular weight
  - bond-length row count
  - bond-angle row count

## Tech Stack

- **Python**
- **RDKit**
- **Pydantic**
- **Pandas**
- **Pytest**
- **HTML / CSS / JavaScript**
- **3Dmol.js** for interactive molecular rendering

## Project Structure

```text
04-chemdata-validation-engine/
├── data/
│   ├── reports/
│   └── sample_compounds.json
├── src/
│   ├── ingestion.py
│   ├── main.py
│   ├── schemas.py
│   ├── validator.py
│   └── viewer.py
├── tests/
│   └── test_validator.py
├── README.md
└── requirements.txt
```

## Sample Workflow

1. Load compound records from `sample_compounds.json`
2. Validate each record
3. Accept valid molecular records
4. Reject invalid entries such as malformed SMILES
5. Save validation results to JSON
6. Generate an HTML dashboard for a selected compound
7. Review the 2D/3D structure and molecular geometry metrics in the browser

## Installation

Clone the repository and move into Project 4:

```bash
git clone <your-repo-url>
cd technical-analytical-project/04-chemdata-validation-engine
```

Create and activate a virtual environment:

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install rdkit
```

## Run the Project

Generate the validation report and molecular dashboard:

```bash
python src/main.py --input data/sample_compounds.json --viewer-compound-id CMP001
```

## Expected Output

Typical terminal output:

```text
SMILES Parse Error: Failed parsing SMILES 'INVALID_SMILES'
Input records: 3
Passed: 2
Failed: 1
Report saved to: data/reports/validation_report.json
3D viewer generated: .../data/reports/CMP001_viewer.html
```

This output is expected because the sample dataset intentionally includes one invalid record to demonstrate validation failure handling.

## Open the Dashboard

After running the script, open:

```text
data/reports/CMP001_viewer.html
```

The page displays:

- branded molecular dashboard
- 2D structure view
- 3D interactive molecular model
- bond length table
- bond angle table
- supporting scientific descriptions

## Run Tests

```bash
pytest
```

Expected result:

```text
2 passed
```

## Example Use Case

This project demonstrates how a technical data workflow can move from raw structured input to validated scientific output and visual interpretation. It is relevant to portfolio themes such as:

- scientific data engineering
- cheminformatics-lite demos
- validation pipelines
- technical analytics dashboards
- R&D data tooling
- industrial and laboratory data quality workflows

## Validation Logic

The project validates both record structure and molecular content. Example checks include:

- required record fields
- chemistry-aware parsing
- valid vs invalid SMILES detection
- successful molecule construction
- extraction of molecular descriptors
- generation of geometry metrics for accepted compounds

## Public-Safe Design Notes

This project is intentionally designed as a **public-safe portfolio demo**. It is not intended to replicate proprietary research systems or enterprise laboratory platforms. Instead, it demonstrates the technical concepts behind:

- structured ingestion
- analytical validation
- molecular visualization
- data-to-dashboard workflow design

All sample data and outputs are portfolio-oriented and safe for public GitHub presentation.

## Screenshots

Browser dashboard preview: [Viewer screenshot]()  
Development and execution view in VS Code: [Workspace screenshot]()

## Why This Project Matters

This project shows the ability to combine software engineering and domain logic in one workflow. It demonstrates:

- practical Python implementation
- structured project organization
- testing discipline
- domain-aware validation
- scientific visualization
- portfolio storytelling suitable for technical consulting, analytics, and data engineering roles

## Future Improvements

Planned enhancements may include:

- CSV ingestion support
- richer descriptor reporting
- downloadable HTML/PDF report exports
- dashboard theming improvements
- integration with a lightweight relational storage layer
- linkage to a future Streamlit control center

## Author Positioning

This project supports a broader portfolio focused on:

- data engineering
- technical analytics
- scientific/industrial data workflows
- validation systems
- molecular and R&D data dashboards

---

If you found this project interesting, feel free to explore the wider `technical-analytical-project` repository for additional data engineering, AI, and scientific analytics demos.
```



README for 04-Chemdata-validation-engine
# ChemData Validation Engine

A Python-based molecular validation and visualization project that ingests structured chemical records, validates molecular inputs, generates JSON reporting outputs, and renders a browser-based analytical dashboard with 2D/3D molecular views and bond geometry metrics.

## Overview

The **ChemData Validation Engine** is a technical analytics portfolio project designed to demonstrate how structured scientific records can move through a validation-first workflow into a user-facing dashboard.

The project processes sample compound records, detects invalid molecular inputs, generates a machine-readable validation report, and produces a branded HTML dashboard for molecular inspection.

This project showcases practical capability across:

- structured data ingestion
- domain-aware validation logic
- scientific computation with RDKit
- JSON reporting outputs
- analytical dashboard presentation
- test-backed Python project delivery

## Key Features

- Ingests structured compound data from sample input
- Validates molecular records and flags invalid SMILES entries
- Generates a JSON validation report for downstream inspection
- Produces a branded HTML dashboard for molecular visualization
- Displays **2D and 3D molecular structure views**
- Surfaces **bond-length and bond-angle metrics**
- Includes explanatory descriptions for structural and geometric outputs
- Uses automated tests with `pytest`

## Tech Stack

- Python
- RDKit
- Pydantic
- Pandas
- Pytest
- HTML / CSS / JavaScript
- 3Dmol.js

## Final GitHub Structure

```text
04-chemdata-validation-engine/
├── data/
│   ├── reports/
│   │   ├── validation_report.json
│   │   └── CMP001_viewer.html
│   └── sample_compounds.json
├── src/
│   ├── ingestion.py
│   ├── main.py
│   ├── schemas.py
│   ├── validator.py
│   └── viewer.py
├── tests/
│   └── test_validator.py
├── README.md
└── requirements.txt
Run the Project
Copypython src/main.py --input data/sample_compounds.json --viewer-compound-id CMP001
Example Output
Typical validated output:

CopyInput records: 3
Passed: 2
Failed: 1
Report saved to: data/reports/validation_report.json
3D viewer generated: data/reports/CMP001_viewer.html
The sample dataset intentionally includes one invalid molecular record to demonstrate validation failure handling.

Run Tests
Copypytest
Expected result:

Copy2 passed
Dashboard Screenshots
Screen 1 — Structure Visualization Screen
This screen presents the molecule in both 2D and 3D views within a single analytical layout, making it easier to compare structural connectivity with spatial geometry. It is designed to feel like a lightweight technical dashboard rather than a raw script output. Screen 1

### Screen 1 - Structure Visualization Screen

![Screen 1 - Structure Visualization Screen]()

### Screen 2 — Geometric Metrics Screen
This screen presents Bond Length Metrics and Bond Angle Metrics side by side, each with explanatory descriptions underneath. It supports quick interpretation of molecular geometry in a more structured R&D-style interface. Screen 2

### Screen 2 - Geometric Metrics Screen
![Screen 2 - Geometric Metrics Screen]()

Development and Execution View
This view shows the project running successfully in VS Code, including repository structure, generated outputs, and terminal execution evidence. It helps demonstrate tested workflow delivery as part of the public portfolio presentation. Workspace view

### VS Code Execution View
![VS Code Execution View]()

Workflow Summary
The project follows a simple end-to-end workflow:

Load structured chemical records from sample input
Validate molecular records using chemistry-aware checks
Reject malformed or invalid molecular entries
Save results to a JSON validation report
Generate an HTML dashboard for a selected compound
Display molecular structure and geometry metrics in the browser
Why This Project Matters
This project demonstrates how technical data can move from structured input to validated scientific output and finally into a visual analytical layer.

It is relevant to portfolio themes such as:

technical analytics
scientific data workflows
validation pipelines
cheminformatics-style demos
Python dashboard generation
R&D and industrial data tooling
Public-Safe Portfolio Positioning
This project is intentionally designed as a public-safe technical portfolio demo. It does not replicate proprietary systems or enterprise laboratory platforms. Instead, it demonstrates the technical concepts behind:

analytical ingestion
molecular validation
scientific reporting
dashboard-based technical communication
Future Improvements
Possible next enhancements include:

CSV ingestion support
richer molecular descriptor reporting
downloadable report exports
improved dashboard theming
integration with Project 5 relational storage
integration with Project 6 control-center dashboard
Summary
ChemData Validation Engine is a portfolio-ready example of domain-aware Python development that combines validation logic, scientific computation, technical reporting, and user-facing dashboard presentation in one cohesive workflow.

