import sys
from pathlib import Path

# Add src/ to Python path so pytest can import project modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from validator import ChemValidator


def test_valid_smiles():
    validator = ChemValidator()
    record = {
        "compound_id": "CMP001",
        "compound_name": "Aspirin",
        "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "source": "test"
    }
    result, _ = validator.validate_record(record)
    assert result.validation_status == "PASS"


def test_invalid_smiles():
    validator = ChemValidator()
    record = {
        "compound_id": "CMP002",
        "compound_name": "Broken Molecule",
        "smiles": "INVALID",
        "source": "test"
    }
    result, _ = validator.validate_record(record)
    assert result.validation_status == "FAIL"
