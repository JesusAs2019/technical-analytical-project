from typing import Dict, Tuple

from schemas import CompoundInput, ValidatedCompound

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors, Lipinski
except ImportError:
    Chem = None


class ChemValidator:
    def __init__(self):
        if Chem is None:
            raise ImportError(
                "RDKit is required for chemical validation. Please install RDKit first."
            )

    def validate_record(self, record: Dict) -> Tuple[ValidatedCompound, object]:
        """
        Returns:
            (validated_output, mol_object_or_none)
        """
        try:
            record_obj = CompoundInput(**record)
        except Exception as e:
            return (
                ValidatedCompound(
                    compound_id=record.get("compound_id", "UNKNOWN"),
                    compound_name=record.get("compound_name", "UNKNOWN"),
                    smiles=record.get("smiles", ""),
                    source=record.get("source", "unknown"),
                    validation_status="FAIL",
                    validation_message=f"Schema validation error: {e}",
                ),
                None,
            )

        mol = Chem.MolFromSmiles(record_obj.smiles)
        if mol is None:
            return (
                ValidatedCompound(
                    compound_id=record_obj.compound_id,
                    compound_name=record_obj.compound_name,
                    smiles=record_obj.smiles,
                    source=record_obj.source or "unknown",
                    validation_status="FAIL",
                    validation_message="Invalid SMILES string",
                ),
                None,
            )

        try:
            molecular_weight = round(Descriptors.MolWt(mol), 2)
            molecular_formula = rdMolDescriptors.CalcMolFormula(mol)
            logp = round(Crippen.MolLogP(mol), 2)
            donors = Lipinski.NumHDonors(mol)
            acceptors = Lipinski.NumHAcceptors(mol)
            chiral_centers = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True))

            return (
                ValidatedCompound(
                    compound_id=record_obj.compound_id,
                    compound_name=record_obj.compound_name,
                    smiles=record_obj.smiles,
                    source=record_obj.source or "unknown",
                    molecular_weight=molecular_weight,
                    molecular_formula=molecular_formula,
                    logp=logp,
                    h_bond_donors=donors,
                    h_bond_acceptors=acceptors,
                    chiral_centers=chiral_centers,
                    validation_status="PASS",
                    validation_message="Validated successfully",
                ),
                mol,
            )
        except Exception as e:
            return (
                ValidatedCompound(
                    compound_id=record_obj.compound_id,
                    compound_name=record_obj.compound_name,
                    smiles=record_obj.smiles,
                    source=record_obj.source or "unknown",
                    validation_status="FAIL",
                    validation_message=f"RDKit processing error: {e}",
                ),
                None,
            )
