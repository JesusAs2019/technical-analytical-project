# ChemData Relational Vault Summary

## Record Counts
- Total records: **3**
- PASS: **2**
- WARN: **1**
- FAIL: **0**

## Dataset Preview
| compound_id   | compound_name   | smiles                       | molecular_formula   |   molecular_weight | validation_status   |   chiral_centers | stereochemistry_notes      |   temperature_c | solvent   |   reaction_time_hr |   ph |
|:--------------|:----------------|:-----------------------------|:--------------------|-------------------:|:--------------------|-----------------:|:---------------------------|----------------:|:----------|-------------------:|-----:|
| CMP001        | Aspirin         | CC(=O)OC1=CC=CC=C1C(=O)O     | C9H8O4              |             180.16 | PASS                |                0 | No chiral centers detected |              25 | Ethanol   |                2.5 |  3.5 |
| CMP002        | Caffeine        | Cn1cnc2n(C)c(=O)n(C)c(=O)c12 | C8H10N4O2           |             194.19 | PASS                |                0 | Planar heterocyclic system |              22 | Water     |                1   |  6.8 |
| CMP003        | Demo Warning    | CCO                          | C2H6O               |              46.07 | WARN                |                0 | Simple alcohol demo entry  |              20 | Methanol  |                0.5 |  7   |
