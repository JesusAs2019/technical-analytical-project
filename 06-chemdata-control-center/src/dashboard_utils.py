from __future__ import annotations

import json
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

from data_loader import (
    get_bond_metadata,
    get_conformers,
    get_dashboard_summary,
    get_energy_profile,
    get_frame_by_index,
    get_trajectory_frames,
    records_to_dataframe,
)


def filter_records(
    records: List[Dict[str, Any]],
    status_filter: str = "All",
    source_filter: str = "All",
    provenance_filter: str = "All",
    viewer_ready_only: bool = False,
    search_text: str = "",
) -> List[Dict[str, Any]]:
    filtered = []

    search_text = (search_text or "").strip().lower()

    for record in records:
        if status_filter != "All" and record.get("validation_status") != status_filter:
            continue

        if source_filter != "All" and record.get("source_project") != source_filter:
            continue

        if provenance_filter != "All" and record.get("provenance_type") != provenance_filter:
            continue

        if viewer_ready_only and not record.get("viewer_ready", False):
            continue

        if search_text:
            haystack = " ".join(
                [
                    str(record.get("compound_id", "")),
                    str(record.get("compound_name", "")),
                    str(record.get("smiles", "")),
                    str(record.get("reaction_name", "")),
                ]
            ).lower()

            if search_text not in haystack:
                continue

        filtered.append(record)

    return filtered


def get_filter_options(records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    status_options = sorted({str(r.get("validation_status", "UNKNOWN")) for r in records})
    source_options = sorted({str(r.get("source_project", "Unknown")) for r in records})
    provenance_options = sorted({str(r.get("provenance_type", "Unknown")) for r in records})

    return {
        "status_options": ["All"] + status_options,
        "source_options": ["All"] + source_options,
        "provenance_options": ["All"] + provenance_options,
    }


def get_kpi_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = get_dashboard_summary(records)

    if not records:
        summary["experimental_count"] = 0
        summary["predicted_count"] = 0
        return summary

    df = records_to_dataframe(records)
    summary["experimental_count"] = int((df["provenance_type"] == "Experimental").sum())
    summary["predicted_count"] = int((df["provenance_type"] == "ML-Predicted").sum())

    return summary


def get_record_table(records: List[Dict[str, Any]]) -> pd.DataFrame:
    df = records_to_dataframe(records)

    if df.empty:
        return df

    preferred_cols = [
        "compound_id",
        "compound_name",
        "validation_status",
        "molecular_formula",
        "molecular_weight",
        "source_project",
        "reaction_name",
        "activation_energy_kj_mol",
        "provenance_type",
        "confidence_score",
        "viewer_ready",
        "last_updated",
    ]

    cols = [c for c in preferred_cols if c in df.columns]
    return df[cols].sort_values(by=["compound_id"]).reset_index(drop=True)


def get_compound_overview(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "compound_id": record.get("compound_id"),
        "compound_name": record.get("compound_name"),
        "smiles": record.get("smiles"),
        "molecular_formula": record.get("molecular_formula"),
        "molecular_weight": record.get("molecular_weight"),
        "validation_status": record.get("validation_status"),
        "status_color": record.get("status_color", "gray"),
        "chiral_centers": record.get("chiral_centers"),
        "stereochemistry_notes": record.get("stereochemistry_notes"),
        "viewer_ready": record.get("viewer_ready"),
        "source_project": record.get("source_project"),
        "last_updated": record.get("last_updated"),
    }


def get_reaction_overview(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "reaction_name": record.get("reaction_name"),
        "reactants": record.get("reactants", []),
        "products": record.get("products", []),
        "transition_state_label": record.get("transition_state_label"),
        "activation_energy_kj_mol": record.get("activation_energy_kj_mol"),
        "activation_energy_kcal_mol": record.get("activation_energy_kcal_mol"),
        "delta_h_kj_mol": record.get("delta_h_kj_mol"),
        "delta_g_kj_mol": record.get("delta_g_kj_mol"),
        "provenance_type": record.get("provenance_type"),
        "confidence_score": record.get("confidence_score"),
    }


def get_synthesis_conditions(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "temperature_c": record.get("temperature_c"),
        "pressure_bar": record.get("pressure_bar"),
        "solvent": record.get("solvent"),
        "catalyst": record.get("catalyst"),
        "reaction_time_hr": record.get("reaction_time_hr"),
        "ph": record.get("ph"),
        "expected_yield_pct": record.get("expected_yield_pct"),
    }


def get_mechanism_steps(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    return record.get("mechanism_steps", [])


def get_mechanism_step_labels(record: Dict[str, Any]) -> List[str]:
    return [step.get("step_label", f"Step {idx}") for idx, step in enumerate(get_mechanism_steps(record))]


def get_mechanism_step_map(record: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    return {int(step.get("step_index", idx)): step for idx, step in enumerate(get_mechanism_steps(record))}


def get_selected_step(record: Dict[str, Any], step_index: int) -> Optional[Dict[str, Any]]:
    step_map = get_mechanism_step_map(record)
    return step_map.get(step_index)


def get_selected_frame(record: Dict[str, Any], step_index: int) -> Optional[Dict[str, Any]]:
    return get_frame_by_index(record, step_index)


def get_bond_metadata_table(record: Dict[str, Any]) -> pd.DataFrame:
    df = get_bond_metadata(record)
    if df.empty:
        return df

    preferred = [
        "compound_id",
        "bond_type",
        "atoms",
        "bond_order",
        "length_angstrom",
        "source",
        "step_scope",
    ]
    cols = [c for c in preferred if c in df.columns]
    return df[cols].reset_index(drop=True)


def get_conformer_table(record: Dict[str, Any]) -> pd.DataFrame:
    df = get_conformers(record)
    if df.empty:
        return df

    preferred = [
        "conformer_id",
        "frame_id",
        "step_label",
        "source",
        "embedding_method",
        "optimization_method",
        "viewer_style",
        "coordinates_ready",
        "relative_conformer_energy_kj_mol",
        "rmsd_reference",
    ]
    cols = [c for c in preferred if c in df.columns]
    return df[cols].reset_index(drop=True)


def get_trajectory_table(record: Dict[str, Any]) -> pd.DataFrame:
    df = get_trajectory_frames(record)
    if df.empty:
        return df

    preferred = [
        "frame_id",
        "step_index",
        "step_label",
        "stage",
        "energy_kj_mol",
        "energy_kcal_mol",
        "is_transition_state",
        "conformer_id",
        "playback_note",
    ]
    cols = [c for c in preferred if c in df.columns]
    return df[cols].sort_values(by=["step_index"]).reset_index(drop=True)


def get_status_badge_html(status: str, color: str = "gray") -> str:
    return f"""
    <div style="
        display:inline-block;
        padding:6px 12px;
        border-radius:999px;
        background:{_status_bg(color)};
        color:{_status_fg(color)};
        font-weight:700;
        font-size:13px;
        border:1px solid {_status_border(color)};
    ">
        {status}
    </div>
    """


def _status_bg(color: str) -> str:
    mapping = {
        "green": "#dcfce7",
        "orange": "#ffedd5",
        "red": "#fee2e2",
        "gray": "#e5e7eb",
    }
    return mapping.get(color, "#e5e7eb")


def _status_fg(color: str) -> str:
    mapping = {
        "green": "#166534",
        "orange": "#9a3412",
        "red": "#991b1b",
        "gray": "#374151",
    }
    return mapping.get(color, "#374151")


def _status_border(color: str) -> str:
    mapping = {
        "green": "#86efac",
        "orange": "#fdba74",
        "red": "#fca5a5",
        "gray": "#d1d5db",
    }
    return mapping.get(color, "#d1d5db")


def interpret_thermodynamics(record: Dict[str, Any]) -> str:
    delta_h = float(record.get("delta_h_kj_mol", 0.0))
    delta_g = float(record.get("delta_g_kj_mol", 0.0))

    enthalpy_label = "exothermic" if delta_h < 0 else "endothermic" if delta_h > 0 else "thermoneutral"
    spontaneity_label = "spontaneous" if delta_g < 0 else "non-spontaneous" if delta_g > 0 else "equilibrium-like"

    return (
        f"This pathway is modeled as {enthalpy_label} (ΔH = {delta_h:.2f} kJ/mol) "
        f"and {spontaneity_label} under the indicated conditions (ΔG = {delta_g:.2f} kJ/mol)."
    )


def interpret_provenance(record: Dict[str, Any]) -> str:
    provenance = str(record.get("provenance_type", "Unknown"))
    confidence = float(record.get("confidence_score", 0.0))

    if provenance == "Experimental":
        return "This record is flagged as experimental and may be treated as the higher-confidence reference case for the dashboard."
    if provenance == "ML-Predicted":
        return f"This record is flagged as ML-predicted with a confidence score of {confidence:.2f}, so values should be interpreted as model-supported estimates."
    return "Provenance is unspecified for this record."


def build_energy_profile_figure(record: Dict[str, Any], active_step_index: Optional[int] = None) -> go.Figure:
    df = get_energy_profile(record)

    fig = go.Figure()

    if df.empty:
        fig.update_layout(
            title="Reaction Energy Profile",
            template="plotly_white",
            xaxis_title="Reaction Step",
            yaxis_title="Energy (kJ/mol)",
        )
        return fig

    fig.add_trace(
        go.Scatter(
            x=df["step_label"],
            y=df["energy_kj_mol"],
            mode="lines+markers",
            line=dict(width=3),
            marker=dict(size=10),
            name="Energy Profile (kJ/mol)",
            hovertemplate="<b>%{x}</b><br>Energy: %{y:.2f} kJ/mol<extra></extra>",
        )
    )

    ts_df = df[df["is_transition_state"] == True]
    if not ts_df.empty:
        fig.add_trace(
            go.Scatter(
                x=ts_df["step_label"],
                y=ts_df["energy_kj_mol"],
                mode="markers",
                marker=dict(size=16, symbol="diamond", color="crimson"),
                name="Transition State",
                hovertemplate="<b>%{x}</b><br>Transition state<br>Energy: %{y:.2f} kJ/mol<extra></extra>",
            )
        )

    if active_step_index is not None and active_step_index in df["step_index"].values:
        active_row = df[df["step_index"] == active_step_index].iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[active_row["step_label"]],
                y=[active_row["energy_kj_mol"]],
                mode="markers",
                marker=dict(size=18, symbol="circle-open", color="#111827", line=dict(width=3)),
                name="Selected Step",
                hovertemplate="<b>%{x}</b><br>Selected step<br>Energy: %{y:.2f} kJ/mol<extra></extra>",
            )
        )

    fig.update_layout(
        title=f"Reaction Coordinate — {record.get('reaction_name', 'Energy Profile')}",
        template="plotly_white",
        xaxis_title="Mechanism Step",
        yaxis_title="Relative Energy (kJ/mol)",
        height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=40, r=20, t=70, b=40),
    )

    return fig


def build_energy_cards(record: Dict[str, Any]) -> Dict[str, float]:
    return {
        "activation_energy_kj_mol": float(record.get("activation_energy_kj_mol", 0.0)),
        "activation_energy_kcal_mol": float(record.get("activation_energy_kcal_mol", 0.0)),
        "delta_h_kj_mol": float(record.get("delta_h_kj_mol", 0.0)),
        "delta_g_kj_mol": float(record.get("delta_g_kj_mol", 0.0)),
    }


def build_reaction_pathway_summary(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    summary = []
    for step in get_mechanism_steps(record):
        summary.append(
            {
                "step_index": step.get("step_index"),
                "step_label": step.get("step_label"),
                "stage": step.get("stage"),
                "relative_energy_kj_mol": step.get("relative_energy_kj_mol"),
                "transition_state": step.get("transition_state"),
                "description": step.get("description"),
            }
        )
    return summary


def build_playback_controls(record: Dict[str, Any]) -> Dict[str, Any]:
    controls = record.get("interactive_controls", {}) or {}

    defaults = {
        "play_enabled": True,
        "pause_enabled": True,
        "next_step_enabled": True,
        "previous_step_enabled": True,
        "trajectory_slider_enabled": True,
        "energy_highlight_sync": True,
        "auto_rotate_3d": False,
        "style_options": ["stick", "ball-and-stick", "sphere"],
        "export_options": ["json", "csv", "md", "mol", "xyz", "pdb"],
        "default_playback_speed_ms": 900,
    }

    merged = defaults.copy()
    merged.update(controls)
    return merged


def export_records_csv_text(records: List[Dict[str, Any]]) -> str:
    df = records_to_dataframe(records)
    return df.to_csv(index=False)


def export_record_markdown(record: Dict[str, Any]) -> str:
    compound_name = record.get("compound_name", "Unknown Compound")
    compound_id = record.get("compound_id", "UNKNOWN")
    reaction_name = record.get("reaction_name", "N/A")
    provenance = record.get("provenance_type", "Unknown")
    confidence = record.get("confidence_score", 0.0)

    energy_df = get_energy_profile(record)
    trajectory_df = get_trajectory_table(record)
    conformer_df = get_conformer_table(record)
    bond_df = get_bond_metadata_table(record)

    energy_md = energy_df.to_markdown(index=False) if not energy_df.empty else "_No energy profile available_"
    trajectory_md = trajectory_df.to_markdown(index=False) if not trajectory_df.empty else "_No trajectory frames available_"
    conformer_md = conformer_df.to_markdown(index=False) if not conformer_df.empty else "_No conformer data available_"
    bond_md = bond_df.to_markdown(index=False) if not bond_df.empty else "_No bond metadata available_"

    return f"""# ChemData Control Center Record Export

## Compound
- ID: **{compound_id}**
- Name: **{compound_name}**
- SMILES: **{record.get('smiles', '')}**
- Formula: **{record.get('molecular_formula', 'N/A')}**
- Molecular Weight: **{record.get('molecular_weight', 0.0)}**
- Validation Status: **{record.get('validation_status', 'UNKNOWN')}**

## Reaction Context
- Reaction Name: **{reaction_name}**
- Activation Energy (kJ/mol): **{record.get('activation_energy_kj_mol', 0.0)}**
- Activation Energy (kcal/mol): **{record.get('activation_energy_kcal_mol', 0.0)}**
- ΔH (kJ/mol): **{record.get('delta_h_kj_mol', 0.0)}**
- ΔG (kJ/mol): **{record.get('delta_g_kj_mol', 0.0)}**
- Provenance: **{provenance}**
- Confidence Score: **{confidence}**

## Thermodynamic Interpretation
{interpret_thermodynamics(record)}

## Provenance Interpretation
{interpret_provenance(record)}

## Energy Profile
{energy_md}

## Trajectory Frames
{trajectory_md}

## Conformers
{conformer_md}

## Bond Metadata
{bond_md}
"""


def export_record_json_text(record: Dict[str, Any]) -> str:
    return json.dumps(record, indent=2)


def get_download_payloads(record: Dict[str, Any], records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, bytes]:
    payloads = {
        "record_json": export_record_json_text(record).encode("utf-8"),
        "record_markdown": export_record_markdown(record).encode("utf-8"),
    }

    if records is not None:
        payloads["records_csv"] = export_records_csv_text(records).encode("utf-8")

    return payloads


def summarize_selected_state(record: Dict[str, Any], step_index: int) -> Dict[str, Any]:
    step = get_selected_step(record, step_index)
    frame = get_selected_frame(record, step_index)

    if not step and not frame:
        return {
            "step_label": "Unknown",
            "stage": "unknown",
            "energy_kj_mol": None,
            "is_transition_state": False,
            "description": "No state information available.",
        }

    summary = {
        "step_label": (step or frame or {}).get("step_label", "Unknown"),
        "stage": (step or frame or {}).get("stage", "unknown"),
        "energy_kj_mol": (frame or {}).get("energy_kj_mol", (step or {}).get("relative_energy_kj_mol")),
        "is_transition_state": bool((frame or step or {}).get("is_transition_state", (step or {}).get("transition_state", False))),
        "description": (step or frame or {}).get("description", (frame or {}).get("playback_note", "")),
        "highlight_atoms": (frame or step or {}).get("highlight_atoms", []),
        "highlight_bonds": (frame or step or {}).get("highlight_bonds", []),
        "bond_events": (frame or step or {}).get("bond_events", []),
    }
    return summary


def build_summary_markdown(records: List[Dict[str, Any]]) -> str:
    metrics = get_kpi_metrics(records)
    df = get_record_table(records)
    preview = df.to_markdown(index=False) if not df.empty else "_No records available_"

    return f"""# ChemData Control Center Summary

## KPI Snapshot
- Total Records: **{metrics.get('total_records', 0)}**
- PASS Records: **{metrics.get('pass_count', 0)}**
- WARN Records: **{metrics.get('warn_count', 0)}**
- FAIL Records: **{metrics.get('fail_count', 0)}**
- Viewer-Ready Records: **{metrics.get('viewer_ready_count', 0)}**
- Reaction-Enabled Records: **{metrics.get('reaction_enabled_count', 0)}**
- Average Molecular Weight: **{metrics.get('average_molecular_weight', 0.0)}**

## Record Preview
{preview}
"""
