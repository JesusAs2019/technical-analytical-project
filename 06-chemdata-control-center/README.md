# ChemData Control Center

A Streamlit-based molecular analytics dashboard for browsing validated chemistry records, rendering 2D and 3D molecular structures, exploring reaction pathway playback, and reviewing energy, provenance, and synthesis-condition metadata.

## Overview

**ChemData Control Center** is the interactive dashboard layer of the ChemData portfolio. It brings together structured chemistry records, 2D/3D molecular visualization, reaction-step interpretation, conceptual playback, and operational monitoring in a single control-center-style interface.

This project demonstrates how chemistry-oriented data can be transformed into a user-facing analytical application for inspection, filtering, and visual storytelling. It complements earlier validation and storage projects by acting as the dashboard and presentation layer for molecular records and reaction-state exploration. Recent dashboard iterations and reaction-tab refinements are reflected in the screenshots below. [Source](https://www.genspark.ai/api/files/s/jsrmuGCQ) [Source](https://www.genspark.ai/api/files/s/Oovzqkxn)

## Feature Overview

### Molecular Control Center
- Browse validated chemistry records from a structured dataset
- Filter records by validation status, source project, provenance, and selected compound
- Inspect molecule-specific metadata in a dashboard layout
- View reaction-step-aware record state selection

### 2D Molecular Visualization
- RDKit-generated 2D structure rendering
- Responsive SVG-based structure display
- Step-aware 2D interpretation panel for conceptual mechanism context

### 3D Molecular Visualization
- Interactive 3D molecular viewer
- Conformer-aware rendering support
- Cleaner default viewing mode for portfolio presentation
- State metadata shown alongside the selected molecular view

### Reaction Pathway & Energy Intelligence
- Conceptual reaction pathway analysis tab
- Reaction summary card with current step, stage, relative energy, and description
- Energy-profile chart across mechanism steps
- Mechanism-step labels for quick step tracking

### Conceptual Reaction Animation / Playback
- Step-based conceptual playback of reaction states
- Designed for educational and analytical interpretation
- Supports step progression such as reactant → intermediate → transition state → product
- Intended as a portfolio-grade visual explanation tool rather than a first-principles kinetics or quantum-mechanical simulator

### Operational Monitoring
- Dashboard-style record review for filtered compounds
- Monitoring-oriented layout aligned with technical analytics workflows

### Conceptual Reaction Animation / Playback

The dashboard includes a **conceptual 2D reaction playback module** that allows users to step through mechanism states for selected compounds in a visually guided format. This feature is designed for analytical interpretation, portfolio demonstration, and chemistry storytelling rather than first-principles reaction simulation.

Key capabilities include:

- **Frame-based reaction playback** with step progression controls
- **Previous / Play / Next** navigation buttons
- **Interactive frame slider** with frame counter
- **Reaction summary card** showing:
  - reaction name
  - current step
  - relative energy
  - step description
- Support for conceptual mechanism pathways such as:
  - reactant complex
  - activated/intermediate state
  - transition state
  - product state
- Reusable playback structure across multiple compounds

This playback layer is intended to help communicate how reaction states evolve conceptually across a pathway. It works well as a portfolio-grade explanatory tool for molecular analytics dashboards, educational demos, and chemistry-oriented technical presentations.

> **Note:** The reaction playback is **conceptual and step-based**. It should be interpreted as a structured visualization aid rather than a true kinetics engine, molecular dynamics simulator, or quantum-mechanical reaction solver.


## Tools & Technologies

- **Python**
- **Streamlit**
- **RDKit**
- **Pandas**
- **Plotly**
- **py3Dmol**
- **Pytest**
- **JSON-based sample records**
- **HTML/CSS embedded rendering for responsive viewer panels**

## Project Structure

```text
06-chemdata-control-center/
├── README.md
├── requirements.txt
├── data/
│   └── sample_records.json
├── exports/
├── assets/
│   └── screenshots/
├── src/
│   ├── app.py
│   ├── data_loader.py
│   ├── dashboard_utils.py
│   ├── file_watcher.py
│   ├── molecule_viewer_2d.py
│   └── molecule_viewer_3d.py
└── tests/
    └── test_app.py

Purpose
This project serves as the dashboard and monitoring layer for the wider ChemData portfolio. It is designed to present validated molecular data in a way that is visual, interactive, and useful for technical review.

It extends the portfolio from backend validation and relational storage into a front-end analytical application where users can inspect compounds, review structural states, and interpret conceptual reaction pathways.

Setup Instructions
From the Project 6 folder, install dependencies:

Copypip install -r requirements.txt
If any package is missing in your current environment, install it explicitly and rerun the app:

Copypip install streamlit plotly pandas pytest py3Dmol tabulate watchdog
Run the Dashboard
From inside the Project 6 folder:

Copypython -m streamlit run src/app.py
Then open the local URL shown in the terminal, typically:

Copyhttp://localhost:8501

Expected Dashboard Capabilities

Browse chemistry records from data/sample_records.json
Filter records using sidebar controls
Render a 2D molecular structure view
Render a 3D molecular structure view
Interpret the selected reaction step
Review conceptual reaction pathway information
View an energy profile chart for mechanism steps
Use conceptual reaction playback as a step-based visual aid
Conceptual Reaction Animation Note
The reaction playback/animation layer in this dashboard is conceptual and step-based. It is designed to visually represent mechanism stages and relative energy changes for portfolio demonstration and analytical storytelling.
- Use a conceptual reaction animation tab to step through reaction states with energy-aware playback

It should be interpreted as a structured visualization aid rather than a true kinetics solver, molecular dynamics engine, or first-principles reaction simulator.

Screenshots

Molecular Control Center Layout
Project 6 Molecular Control Center

Improved Viewer Layout Iteration
Improved Layout Iteration

Earlier Viewer Framing Iteration
Earlier Viewer Framing Iteration

Reaction Pathway & Energy Intelligence
Reaction Pathway and Energy Intelligence
### ⚛️ Project 6: ChemData Control Center

A Streamlit-based molecular analytics dashboard that acts as the front-end control center for validated chemistry records. It combines 2D/3D visualization, reaction-step interpretation, energy-profile analysis, and conceptual reaction playback into a portfolio-ready analytical interface.

#### 🖥️ Interface Highlights

##### 1. Project 6 Molecular Control Center

### Aspirin
![Project 6 Molecular Control Center](./assets/screenshots/Aspirin_2D_3D.png)

### Caffeine
![Project 6 Molecular Control Center](./assets/screenshots/Caffeine_2D Molecular_Structure_&_3D_Molecular_viewer.png)

### Ethanol
![Project 6 Molecular Control Center](./assets/screenshots/Ethanol_2D_Molecular Structure_&_3D_Molecular_Viewer.png)

##### 2. Reaction Pathway & Energy Intelligence

### Aspirin
![Reaction Pathway & Energy Intelligence](./assets/screenshots/Aspirin_Reaction_Energy_pathway.png)

### Caffeine
![Reaction Pathway & Energy Intelligence](./assets/screenshots/Caffeine_Reaction_Pathway_&_Energy_Intelligence.png)

### Ethanol
![Reaction Pathway & Energy Intelligence](./assets/screenshots/Ethanol_ReactionPathway_&_Energy_Intelligence.png)

##### 3. Conceptual Reaction Playback

### Aspirin Hydrolysis Playback
![Aspirin Hydrolysis Playback](./assets/screenshots/Aspirin_2D-3D.png)
![Aspirin Hydrolysis Playback](./assets/screenshots/Aspirin_Conceptual_Reaction_Animation1.png)
![Aspirin Hydrolysis Playback](./assets/screenshots/Aspirin_Conceptual_Reaction_Animation2.png)

### Caffeine Protonation Playback
![Caffeine Protonation Playback](./assets/screenshots/Caffeine_Conceptual_Reaction_Animation2.png)
![Caffeine Protonation Playback](./assets/screenshots/Caffeine_Conceptual_Reaction_Animation.png)

### Ethanol
![Ethanol Conceptual Reaction Playback](./assets/screenshots/Ethanol_Conceptual_Reaction_Animation.png)

These screenshots illustrate the dashboard evolution from viewer layout cleanup toward a more polished reaction-analysis interface. Source Source Source Source

Testing

Run the smoke tests with:

Copypytest tests/test_app.py -v

Expected result: passing checks for data loading, state handling, rendering setup, and reaction-step support.

Why This Project Matters

This project demonstrates how structured scientific records can be turned into an interactive dashboard for technical interpretation. It combines:

chemistry-specific data presentation

2D and 3D visualization workflows
reaction-step storytelling
dashboard-style monitoring
portfolio-oriented Python application design
It is a strong example of technical analytics, scientific UI development, and domain-aware visualization.

Public-Safe Portfolio Positioning

This repository is designed as a public-safe chemistry analytics demo. It focuses on molecular rendering, dashboard interaction, and structured analytical presentation without exposing proprietary business logic or confidential scientific assets.

Future Improvements

richer reaction playback controls
cleaner animation tab integration
export/download actions for selected compounds
stronger operational monitoring hooks
enhanced energy-profile annotation
tighter integration with Project 4 validation outputs
tighter integration with Project 5 relational storage workflows

Summary

ChemData Control Center demonstrates how validated chemistry records can be transformed into a clean, interactive, and portfolio-ready molecular dashboard using Python, Streamlit, RDKit, Plotly, and 3D molecular visualization components.
