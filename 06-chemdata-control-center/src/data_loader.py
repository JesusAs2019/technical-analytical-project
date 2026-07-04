from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

KJ_TO_KCAL = 0.239005736


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_list(value: Any, default: Optional[List[Any]] = None) -> List[Any]:
    if isinstance(value, list):
        return value
    return default[:] if default else []


def _status_color(status: str) -> str:
    status = (status or "").upper()
    if status == "PASS":
        return "green"
    if status == "WARN":
        return "orange"
    if status == "FAIL":
        return "red"
    return "gray"


def _default_mechanism_steps(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    compound_name = record.get("compound_name", "Unknown Compound")
    smiles = record.get("smiles", "")

    return [
        {
            "step_index": 0,
            "step_label": "Reactant",
            "stage": "reactant",
            "description": f"Initial molecular state for {compound_name}.",
            "smiles": smiles,
            "relative_energy_kj_mol": 0.0,
            "highlight_atoms": [],
            "highlight_bonds": [],
            "bond_events": [],
            "transition_state": False,
        },
        {
            "step_index": 1,
            "step_label": "Activated Complex",
            "stage": "transition",
            "description": "High-energy transition-state-like placeholder for pathway playback.",
            "smiles": smiles,
            "relative_energy_kj_mol": 58.5,
            "highlight_atoms": [0, 1],
            "highlight_bonds": [],
            "bond_events": [{"type": "strain", "description": "Activated geometry region"}],
            "transition_state": True,
        },
        {
            "step_index": 2,
            "step_label": "Product",
            "stage": "product",
            "description": "Final product-side representation for conceptual pathway playback.",
            "smiles": smiles,
            "relative_energy_kj_mol": -12.5,
            "highlight_atoms": [],
            "highlight_bonds": [],
            "bond_events": [],
            "transition_state": False,
        },
    ]


def _default_energy_profile(record: Dict[str, Any], mechanism_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    activation_energy_kj = _safe_float(record.get("activation_energy_kj_mol"), 58.5)
    delta_h_kj = _safe_float(record.get("delta_h_kj_mol"), -12.5)
    delta_g_kj = _safe_float(record.get("delta_g_kj_mol"), -8.0)

    labels = [step["step_label"] for step in mechanism_steps]

    points = []
    for step in mechanism_steps:
        step_energy = _safe_float(step.get("relative_energy_kj_mol"), 0.0)
        points.append(
            {
                "step_index": step["step_index"],
                "step_label": step["step_label"],
                "stage": step.get("stage", "unknown"),
                "energy_kj_mol": step_energy,
                "energy_kcal_mol": round(step_energy * KJ_TO_KCAL, 3),
                "activation_energy_kj_mol": activation_energy_kj,
                "activation_energy_kcal_mol": round(activation_energy_kj * KJ_TO_KCAL, 3),
                "delta_h_kj_mol": delta_h_kj,
                "delta_g_kj_mol": delta_g_kj,
                "is_transition_state": bool(step.get("transition_state", False)),
            }
        )

    # Guarantee at least 3 classic states for charting
    if len(points) < 3:
        points = [
            {
                "step_index": 0,
                "step_label": labels[0] if labels else "Reactant",
                "stage": "reactant",
                "energy_kj_mol": 0.0,
                "energy_kcal_mol": round(0.0 * KJ_TO_KCAL, 3),
                "activation_energy_kj_mol": activation_energy_kj,
                "activation_energy_kcal_mol": round(activation_energy_kj * KJ_TO_KCAL, 3),
                "delta_h_kj_mol": delta_h_kj,
                "delta_g_kj_mol": delta_g_kj,
                "is_transition_state": False,
            },
            {
                "step_index": 1,
                "step_label": "Transition State",
                "stage": "transition",
                "energy_kj_mol": activation_energy_kj,
                "energy_kcal_mol": round(activation_energy_kj * KJ_TO_KCAL, 3),
                "activation_energy_kj_mol": activation_energy_kj,
                "activation_energy_kcal_mol": round(activation_energy_kj * KJ_TO_KCAL, 3),
                "delta_h_kj_mol": delta_h_kj,
                "delta_g_kj_mol": delta_g_kj,
                "is_transition_state": True,
            },
            {
                "step_index": 2,
                "step_label": "Product",
                "stage": "product",
                "energy_kj_mol": delta_h_kj,
                "energy_kcal_mol": round(delta_h_kj * KJ_TO_KCAL, 3),
                "activation_energy_kj_mol": activation_energy_kj,
                "activation_energy_kcal_mol": round(activation_energy_kj * KJ_TO_KCAL, 3),
                "delta_h_kj_mol": delta_h_kj,
                "delta_g_kj_mol": delta_g_kj,
                "is_transition_state": False,
            },
        ]

    return points


def _default_trajectory_frames(record: Dict[str, Any], mechanism_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    frames: List[Dict[str, Any]] = []
    compound_id = record.get("compound_id", "UNKNOWN")
    base_smiles = record.get("smiles", "")

    for step in mechanism_steps:
        step_index = _safe_int(step.get("step_index"), 0)
        energy_kj = _safe_float(step.get("relative_energy_kj_mol"), 0.0)

        frames.append(
            {
                "frame_id": f"{compound_id}_frame_{step_index}",
                "step_index": step_index,
                "step_label": step.get("step_label", f"Step {step_index}"),
                "stage": step.get("stage", "unknown"),
                "smiles": step.get("smiles", base_smiles),
                "energy_kj_mol": energy_kj,
                "energy_kcal_mol": round(energy_kj * KJ_TO_KCAL, 3),
                "delta_h_kj_mol": _safe_float(record.get("delta_h_kj_mol"), -12.5),
                "delta_g_kj_mol": _safe_float(record.get("delta_g_kj_mol"), -8.0),
                "is_transition_state": bool(step.get("transition_state", False)),
                "highlight_atoms": _as_list(step.get("highlight_atoms"), []),
                "highlight_bonds": _as_list(step.get("highlight_bonds"), []),
                "bond_events": _as_list(step.get("bond_events"), []),
                "playback_note": step.get("description", ""),
                "conformer_id": f"{compound_id}_conf_{step_index}",
                "viewer_ready": True,
            }
        )

    return frames


def _default_conformers(record: Dict[str, Any], trajectory_frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    compound_id = record.get("compound_id", "UNKNOWN")
    conformers = []

    for idx, frame in enumerate(trajectory_frames):
        conformers.append(
            {
                "conformer_id": frame.get("conformer_id", f"{compound_id}_conf_{idx}"),
                "frame_id": frame.get("frame_id"),
                "step_label": frame.get("step_label"),
                "source": "synthetic-placeholder",
                "embedding_method": "ETKDGv3",
                "optimization_method": "MMFF94",
                "viewer_style": "ball-and-stick",
                "coordinates_ready": False,
                "export_formats": ["mol", "xyz", "pdb"],
            }
        )

    return conformers


def _default_bond_metadata(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    smiles = record.get("smiles", "")
    compound_id = record.get("compound_id", "UNKNOWN")

    # Placeholder metadata structure to support the UI before full geometry extraction
    return [
        {
            "compound_id": compound_id,
            "bond_type": "C-C",
            "atoms": "C1-C2",
            "length_angstrom": 1.50,
            "source": "placeholder",
            "smiles_reference": smiles,
        },
        {
            "compound_id": compound_id,
            "bond_type": "C-O",
            "atoms": "C2-O3",
            "length_angstrom": 1.36,
            "source": "placeholder",
            "smiles_reference": smiles,
        },
    ]


def _default_interactive_controls(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "play_enabled": True,
        "pause_enabled": True,
        "next_step_enabled": True,
        "previous_step_enabled": True,
        "trajectory_slider_enabled": True,
        "energy_highlight_sync": True,
        "auto_rotate_3d": False,
        "style_options": ["stick", "ball-and-stick", "sphere"],
        "export_options": ["json", "csv", "md", "mol", "xyz"],
        "default_playback_speed_ms": 900,
    }


def _normalize_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    record = deepcopy(raw)

    record.setdefault("compound_id", "UNKNOWN")
    record.setdefault("compound_name", "Unknown Compound")
    record.setdefault("smiles", "")
    record.setdefault("molecular_formula", "N/A")
    record.setdefault("molecular_weight", 0.0)
    record.setdefault("validation_status", "UNKNOWN")
    record.setdefault("chiral_centers", 0)
    record.setdefault("stereochemistry_notes", "No stereochemistry notes available.")
    record.setdefault("temperature_c", 25.0)
    record.setdefault("solvent", "Not specified")
    record.setdefault("reaction_time_hr", 0.0)
    record.setdefault("ph", 7.0)
    record.setdefault("source_project", "Project 5")
    record.setdefault("last_updated", "2026-06-30")
    record.setdefault("viewer_ready", True)

    record.setdefault("reaction_name", f"{record['compound_name']} Reaction Profile")
    record.setdefault("reactants", [record["compound_name"]])
    record.setdefault("products", [record["compound_name"]])
    record.setdefault("transition_state_label", "Transition State")
    record.setdefault("catalyst", "Not specified")
    record.setdefault("pressure_bar", 1.0)
    record.setdefault("expected_yield_pct", 78.0)
    record.setdefault("confidence_score", 0.88)
    record.setdefault("provenance_type", "Experimental")

    record["molecular_weight"] = round(_safe_float(record.get("molecular_weight"), 0.0), 4)
    record["temperature_c"] = _safe_float(record.get("temperature_c"), 25.0)
    record["reaction_time_hr"] = _safe_float(record.get("reaction_time_hr"), 0.0)
    record["ph"] = _safe_float(record.get("ph"), 7.0)
    record["pressure_bar"] = _safe_float(record.get("pressure_bar"), 1.0)
    record["expected_yield_pct"] = _safe_float(record.get("expected_yield_pct"), 78.0)
    record["confidence_score"] = _safe_float(record.get("confidence_score"), 0.88)
    record["chiral_centers"] = _safe_int(record.get("chiral_centers"), 0)

    if "activation_energy_kj_mol" not in record:
        record["activation_energy_kj_mol"] = 58.5
    if "activation_energy_kcal_mol" not in record:
        record["activation_energy_kcal_mol"] = round(_safe_float(record["activation_energy_kj_mol"]) * KJ_TO_KCAL, 3)

    if "delta_h_kj_mol" not in record:
        record["delta_h_kj_mol"] = -12.5
    if "delta_g_kj_mol" not in record:
        record["delta_g_kj_mol"] = -8.0

    mechanism_steps = _as_list(record.get("mechanism_steps"))
    if not mechanism_steps:
        mechanism_steps = _default_mechanism_steps(record)
    record["mechanism_steps"] = mechanism_steps

    energy_profile = _as_list(record.get("energy_profile"))
    if not energy_profile:
        energy_profile = _default_energy_profile(record, mechanism_steps)
    record["energy_profile"] = energy_profile

    trajectory_frames = _as_list(record.get("trajectory_frames"))
    if not trajectory_frames:
        trajectory_frames = _default_trajectory_frames(record, mechanism_steps)
    record["trajectory_frames"] = trajectory_frames

    conformers = _as_list(record.get("conformers"))
    if not conformers:
        conformers = _default_conformers(record, trajectory_frames)
    record["conformers"] = conformers

    bond_metadata = _as_list(record.get("bond_metadata"))
    if not bond_metadata:
        bond_metadata = _default_bond_metadata(record)
    record["bond_metadata"] = bond_metadata

    record["interactive_controls"] = record.get("interactive_controls") or _default_interactive_controls(record)
    record["status_color"] = _status_color(record.get("validation_status", "UNKNOWN"))

    return record


def load_records(path: str) -> List[Dict[str, Any]]:
    records_path = Path(path)
    if not records_path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    with records_path.open("r", encoding="utf-8") as f:
        raw_records = json.load(f)

    if not isinstance(raw_records, list):
        raise ValueError("Expected the dataset to be a JSON list of records.")

    return [_normalize_record(item) for item in raw_records]


def save_records(path: str, records: List[Dict[str, Any]]) -> str:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    return str(output_path.resolve())


def get_record_by_compound_id(records: List[Dict[str, Any]], compound_id: str) -> Optional[Dict[str, Any]]:
    for record in records:
        if record.get("compound_id") == compound_id:
            return record
    return None


def get_available_compounds(records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [
        {
            "compound_id": record.get("compound_id", ""),
            "compound_name": record.get("compound_name", ""),
            "display_label": f"{record.get('compound_id', '')} — {record.get('compound_name', '')}",
        }
        for record in records
    ]


def records_to_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for record in records:
        rows.append(
            {
                "compound_id": record.get("compound_id"),
                "compound_name": record.get("compound_name"),
                "smiles": record.get("smiles"),
                "molecular_formula": record.get("molecular_formula"),
                "molecular_weight": record.get("molecular_weight"),
                "validation_status": record.get("validation_status"),
                "chiral_centers": record.get("chiral_centers"),
                "temperature_c": record.get("temperature_c"),
                "solvent": record.get("solvent"),
                "reaction_time_hr": record.get("reaction_time_hr"),
                "ph": record.get("ph"),
                "source_project": record.get("source_project"),
                "last_updated": record.get("last_updated"),
                "viewer_ready": record.get("viewer_ready"),
                "reaction_name": record.get("reaction_name"),
                "activation_energy_kj_mol": record.get("activation_energy_kj_mol"),
                "activation_energy_kcal_mol": record.get("activation_energy_kcal_mol"),
                "delta_h_kj_mol": record.get("delta_h_kj_mol"),
                "delta_g_kj_mol": record.get("delta_g_kj_mol"),
                "provenance_type": record.get("provenance_type"),
                "confidence_score": record.get("confidence_score"),
            }
        )
    return pd.DataFrame(rows)


def get_dashboard_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    df = records_to_dataframe(records)

    total_records = len(df)
    pass_count = int((df["validation_status"] == "PASS").sum()) if not df.empty else 0
    warn_count = int((df["validation_status"] == "WARN").sum()) if not df.empty else 0
    fail_count = int((df["validation_status"] == "FAIL").sum()) if not df.empty else 0
    viewer_ready_count = int(df["viewer_ready"].sum()) if not df.empty else 0
    reaction_enabled_count = int(df["reaction_name"].notna().sum()) if not df.empty else 0
    avg_mw = round(float(df["molecular_weight"].mean()), 3) if not df.empty else 0.0

    return {
        "total_records": total_records,
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "viewer_ready_count": viewer_ready_count,
        "reaction_enabled_count": reaction_enabled_count,
        "average_molecular_weight": avg_mw,
    }


def get_energy_profile(record: Dict[str, Any]) -> pd.DataFrame:
    energy_profile = _as_list(record.get("energy_profile"))
    if not energy_profile:
        energy_profile = _default_energy_profile(record, record.get("mechanism_steps", []))
    return pd.DataFrame(energy_profile)


def get_trajectory_frames(record: Dict[str, Any]) -> pd.DataFrame:
    frames = _as_list(record.get("trajectory_frames"))
    if not frames:
        frames = _default_trajectory_frames(record, record.get("mechanism_steps", []))
    return pd.DataFrame(frames)


def get_conformers(record: Dict[str, Any]) -> pd.DataFrame:
    conformers = _as_list(record.get("conformers"))
    if not conformers:
        conformers = _default_conformers(record, record.get("trajectory_frames", []))
    return pd.DataFrame(conformers)


def get_bond_metadata(record: Dict[str, Any]) -> pd.DataFrame:
    bond_metadata = _as_list(record.get("bond_metadata"))
    if not bond_metadata:
        bond_metadata = _default_bond_metadata(record)
    return pd.DataFrame(bond_metadata)


def get_mechanism_step_labels(record: Dict[str, Any]) -> List[str]:
    return [step.get("step_label", f"Step {i}") for i, step in enumerate(record.get("mechanism_steps", []))]


def get_frame_by_index(record: Dict[str, Any], step_index: int) -> Optional[Dict[str, Any]]:
    for frame in record.get("trajectory_frames", []):
        if _safe_int(frame.get("step_index"), -1) == step_index:
            return frame
    return None


def build_export_bundle(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "record_metadata": {
            "compound_id": record.get("compound_id"),
            "compound_name": record.get("compound_name"),
            "smiles": record.get("smiles"),
            "molecular_formula": record.get("molecular_formula"),
            "molecular_weight": record.get("molecular_weight"),
            "validation_status": record.get("validation_status"),
            "provenance_type": record.get("provenance_type"),
            "confidence_score": record.get("confidence_score"),
        },
        "reaction_metadata": {
            "reaction_name": record.get("reaction_name"),
            "activation_energy_kj_mol": record.get("activation_energy_kj_mol"),
            "activation_energy_kcal_mol": record.get("activation_energy_kcal_mol"),
            "delta_h_kj_mol": record.get("delta_h_kj_mol"),
            "delta_g_kj_mol": record.get("delta_g_kj_mol"),
            "catalyst": record.get("catalyst"),
            "pressure_bar": record.get("pressure_bar"),
            "expected_yield_pct": record.get("expected_yield_pct"),
        },
        "mechanism_steps": deepcopy(record.get("mechanism_steps", [])),
        "trajectory_frames": deepcopy(record.get("trajectory_frames", [])),
        "conformers": deepcopy(record.get("conformers", [])),
        "bond_metadata": deepcopy(record.get("bond_metadata", [])),
        "energy_profile": deepcopy(record.get("energy_profile", [])),
    }


def export_record_bundle(record: Dict[str, Any], output_dir: str) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    bundle = build_export_bundle(record)
    filename = f"{record.get('compound_id', 'unknown').lower()}_control_center_bundle.json"
    target = output_path / filename

    with target.open("w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)

    return str(target.resolve())
