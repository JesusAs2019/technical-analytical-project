# ChemData Relational Vault

A lightweight relational storage and export project for validated chemical records, built with Python, SQLAlchemy, SQLite, and analytical output generation.

## Overview

The **ChemData Relational Vault** is a portfolio project designed to demonstrate how validated chemical records can be stored, queried, and exported through a clean relational workflow.

This project acts as the **persistence layer** for a broader chemistry and technical analytics portfolio. It creates a reusable schema for validated compounds, synchronizes structured seed data into a SQLite database, supports query-based retrieval, and exports analytical outputs to CSV and Markdown formats.

It is designed to show practical capability in:

- relational schema design
- structured record synchronization
- analytical querying
- lightweight data persistence
- export-ready reporting workflows
- test-backed Python project organization

## Key Features

- Creates a relational database schema for validated chemical records
- Stores compound, stereochemical, and reaction-condition data in linked tables
- Loads and synchronizes seed records from JSON
- Prevents duplicate record insertion on rerun
- Queries stored compound records into a structured DataFrame
- Exports results to:
  - CSV
  - Markdown summary
- Includes automated test coverage with `pytest`

## Tech Stack

- Python
- SQLAlchemy
- SQLite
- Pandas
- Pytest

## Project Structure

```text
05-chemdata-relational-vault/
├── data/
│   ├── outputs/
│   │   ├── all_compounds.csv
│   │   └── summary.md
│   └── seed_data.json
├── db/
│   └── chemdata_vault.db
├── src/
│   ├── database.py
│   ├── schema_manager.py
│   ├── sync_engine.py
│   ├── queries.py
│   ├── export.py
│   └── main.py
├── tests/
│   └── test_database.py
├── README.md
└── requirements.txt

Purpose

This project represents the data persistence layer of a technical analytical workflow. Where Project 4 focuses on validation and visualization, Project 5 focuses on structured storage, retrieval, and export of validated records.

It is useful as a portfolio demonstration of how backend analytical systems can be designed for reuse in:

scientific workflows
R&D data systems
technical reporting pipelines
downstream dashboards and monitoring tools
Setup
From the Project 5 folder, install dependencies:

pip install -r requirements.txt

Run the Project

Execute the full pipeline with:

python src/main.py

Expected Workflow

The script performs the following steps:

Creates the database schema
Loads seed compound data from JSON
Syncs records into the relational vault
Queries stored compounds
Exports outputs to CSV and Markdown
Example Successful Run

============================================================
CHEMDATA RELATIONAL VAULT
============================================================
1. Creating database schema...
   Schema ready.
2. Loading seed data...
   Loaded 3 record(s).
3. Syncing records into relational vault...
   Inserted 3 new record(s).
4. Querying stored compounds...
   Total rows in vault: 3
   PASS rows: 2
5. Exporting outputs...
   CSV export saved to: .../data/outputs/all_compounds.csv
   Markdown summary saved to: .../data/outputs/summary.md
============================================================
PROJECT 5 RUN COMPLETED SUCCESSFULLY
============================================================

On later reruns, the inserted count may be 0, which is expected because the sync logic avoids duplicating records already stored in the database.

Test Results

Run tests with:
pytest tests/test_database.py -v

Expected result:

1 passed

Key Outputs

After running successfully, the project generates:

db/chemdata_vault.db — SQLite database file
data/outputs/all_compounds.csv — exported full dataset
data/outputs/summary.md — Markdown analytical summary

Why This Project Matters

This project demonstrates how validated technical data can be persisted in a reusable relational format instead of remaining trapped in one-off scripts or flat files.

It showcases practical strengths in:

schema-backed data design
backend analytical workflows
repeatable synchronization logic
queryable technical datasets
export-ready reporting outputs
For recruiters and technical reviewers, it shows the ability to build a clean storage layer that supports future dashboards, analytics tools, and reporting systems.

Public-Safe Portfolio Positioning

This project is intentionally designed as a public-safe portfolio demo. It does not represent proprietary laboratory systems or enterprise chemical platforms. Instead, it demonstrates the technical concepts behind:

relational persistence
structured analytical records
reusable query/export workflows
backend support for scientific dashboards
Future Improvements
Potential next improvements include:

PostgreSQL version for production-style deployment
richer filtering and query utilities
CLI options for export selection
direct integration with Project 4 validation outputs
integration with Project 6 control-center dashboards
lightweight database inspection UI

Summary

ChemData Relational Vault is a backend-oriented portfolio project that demonstrates relational storage, query workflows, export generation, and structured Python project design for technical and scientific data systems.



