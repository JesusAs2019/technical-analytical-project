import pandas as pd
from sqlalchemy import select

from database import SessionLocal
from schema_manager import VerifiedCompound, StereochemicalMetric, ReactionCondition


def get_all_compounds():
    with SessionLocal() as session:
        stmt = (
            select(
                VerifiedCompound.compound_id,
                VerifiedCompound.compound_name,
                VerifiedCompound.smiles,
                VerifiedCompound.molecular_formula,
                VerifiedCompound.molecular_weight,
                VerifiedCompound.validation_status,
                StereochemicalMetric.chiral_centers,
                StereochemicalMetric.stereochemistry_notes,
                ReactionCondition.temperature_c,
                ReactionCondition.solvent,
                ReactionCondition.reaction_time_hr,
                ReactionCondition.ph,
            )
            .join(
                StereochemicalMetric,
                VerifiedCompound.compound_id == StereochemicalMetric.compound_id,
            )
            .join(
                ReactionCondition,
                VerifiedCompound.compound_id == ReactionCondition.compound_id,
            )
        )

        rows = session.execute(stmt).all()

    columns = [
        "compound_id",
        "compound_name",
        "smiles",
        "molecular_formula",
        "molecular_weight",
        "validation_status",
        "chiral_centers",
        "stereochemistry_notes",
        "temperature_c",
        "solvent",
        "reaction_time_hr",
        "ph",
    ]

    return pd.DataFrame(rows, columns=columns)


def get_compounds_by_status(status: str):
    df = get_all_compounds()
    return df[df["validation_status"] == status].reset_index(drop=True)
