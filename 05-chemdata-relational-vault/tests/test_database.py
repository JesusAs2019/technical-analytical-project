import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from schema_manager import create_schema
from sync_engine import load_seed_records, sync_records
from queries import get_all_compounds


def test_database_pipeline():
    seed_file = PROJECT_ROOT / "data" / "seed_data.json"

    create_schema()
    records = load_seed_records(str(seed_file))
    sync_records(records)

    df = get_all_compounds()

    assert len(df) >= 3
    assert "compound_id" in df.columns
    assert "compound_name" in df.columns
    assert "validation_status" in df.columns
