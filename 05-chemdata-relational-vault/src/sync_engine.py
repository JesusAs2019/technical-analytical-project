import json
from pathlib import Path

from database import SessionLocal
from schema_manager import VerifiedCompound, StereochemicalMetric, ReactionCondition


def load_seed_records(path: str):
    seed_path = Path(path)
    if not seed_path.exists():
        raise FileNotFoundError(f"Seed data file not found: {path}")

    with seed_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sync_records(records):
    inserted_count = 0

    with SessionLocal() as session:
        for record in records:
            existing = session.get(VerifiedCompound, record["compound_id"])
            if existing:
                continue

            compound = VerifiedCompound(
                compound_id=record["compound_id"],
                compound_name=record["compound_name"],
                smiles=record["smiles"],
                molecular_formula=record["molecular_formula"],
                molecular_weight=record["molecular_weight"],
                validation_status=record["validation_status"],
            )

            stereo = StereochemicalMetric(
                compound_id=record["compound_id"],
                chiral_centers=record["chiral_centers"],
                stereochemistry_notes=record["stereochemistry_notes"],
            )

            reaction = ReactionCondition(
                compound_id=record["compound_id"],
                temperature_c=record["temperature_c"],
                solvent=record["solvent"],
                reaction_time_hr=record["reaction_time_hr"],
                ph=record["ph"],
            )

            session.add(compound)
            session.add(stereo)
            session.add(reaction)

            inserted_count += 1

        session.commit()

    return inserted_count
