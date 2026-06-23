import json
from pathlib import Path
from typing import List, Dict

import pandas as pd


def load_records(file_path: str) -> List[Dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON input must contain a list of records")
        return data

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        return df.to_dict(orient="records")

    raise ValueError("Supported file types: .json, .csv")


def save_report(records: List[Dict], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
