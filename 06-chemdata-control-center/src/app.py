from __future__ import annotations
import streamlit.components.v1 as components
from pathlib import Path
from typing import Any, Dict, List, Optional
import plotly.graph_objects as go
import streamlit as st
import json

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D


from data_loader import (
    get_available_compounds,
    load_records,
)
from dashboard_utils import (
    build_energy_cards,
    build_energy_profile_figure,
    build_playback_controls,
    build_reaction_pathway_summary,
    build_summary_markdown,
    filter_records,
    get_bond_metadata_table,
    get_compound_overview,
    get_conformer_table,
    get_download_payloads,
    get_filter_options,
    get_kpi_metrics,
    get_mechanism_step_labels,
    get_reaction_overview,
    get_record_table,
    get_status_badge_html,
    get_synthesis_conditions,
    get_trajectory_table,
    interpret_provenance,
    interpret_thermodynamics,
    summarize_selected_state,
)
from molecule_viewer_2d import (
    export_2d_svg,
    generate_2d_svg,
    get_available_conformer_options,
    get_available_step_options,
    get_reaction_step_description,
)
from molecule_viewer_3d import (
    export_playback_bundle_json,
    export_state_molblock,
    generate_3d_viewer_html,
    generate_playback_html,
    get_3d_state_summary,
    get_available_3d_styles,
)


st.set_page_config(
    page_title="ChemData Control Center",
    page_icon="🧪",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "sample_records.json"
EXPORT_DIR = PROJECT_ROOT / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_data(show_spinner=False)
def load_dashboard_records(path: str) -> List[Dict[str, Any]]:
    return load_records(path)


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
            .main .block-container {
                padding-top: 1.25rem;
                padding-bottom: 2rem;
                max-width: 1450px;
            }

            .hero-card {
                background: linear-gradient(135deg, #eff6ff 0%, #f8fbff 100%);
                border: 1px solid #dbeafe;
                border-radius: 20px;
                padding: 22px 24px;
                margin-bottom: 18px;
                box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
            }

            .hero-title {
                font-size: 30px;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 6px;
            }

            .hero-subtitle {
                font-size: 15px;
                color: #334155;
                line-height: 1.65;
            }

            .kpi-card {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 18px 18px;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
                height: 100%;
            }

            .kpi-label {
                font-size: 13px;
                color: #64748b;
                font-weight: 600;
                margin-bottom: 6px;
            }

            .kpi-value {
                font-size: 28px;
                font-weight: 800;
                color: #0f172a;
                line-height: 1.15;
            }

            .section-card {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                padding: 18px 20px;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
                margin-bottom: 16px;
            }

            .info-card {
                background: #f8fbff;
                border: 1px solid #dbeafe;
                border-radius: 16px;
                padding: 14px 16px;
                margin-bottom: 12px;
            }

            .info-title {
                font-size: 14px;
                font-weight: 800;
                color: #1e3a8a;
                margin-bottom: 4px;
            }

            .info-body {
                font-size: 14px;
                color: #334155;
                line-height: 1.6;
            }

            .metric-mini {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 14px 16px;
                margin-bottom: 10px;
            }

            .metric-mini-label {
                font-size: 12px;
                color: #64748b;
                font-weight: 700;
            }

            .metric-mini-value {
                font-size: 20px;
                color: #0f172a;
                font-weight: 800;
                margin-top: 4px;
            }

            .small-note {
                font-size: 13px;
                color: #475569;
                line-height: 1.6;
            }

            .streamlit-expanderHeader {
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">ChemData Control Center</div>
            <div class="hero-subtitle">
                A portfolio-grade molecular analytics dashboard for browsing validated chemistry records,
                rendering 2D and 3D structures, exploring reaction pathway playback, interpreting activation
                energy, and reviewing synthesis conditions in a control-center style interface.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(records: List[Dict[str, Any]]) -> None:
    metrics = get_kpi_metrics(records)

    cols = st.columns(6)

    items = [
        ("Total Records", metrics.get("total_records", 0)),
        ("PASS Records", metrics.get("pass_count", 0)),
        ("WARN Records", metrics.get("warn_count", 0)),
        ("Viewer Ready", metrics.get("viewer_ready_count", 0)),
        ("Reaction Enabled", metrics.get("reaction_enabled_count", 0)),
        ("Avg. Mol. Weight", metrics.get("average_molecular_weight", 0.0)),
    ]

    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def sidebar_filters(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    st.sidebar.header("Dashboard Controls")

    options = get_filter_options(records)

    status_filter = st.sidebar.selectbox("Validation status", options["status_options"])
    source_filter = st.sidebar.selectbox("Source project", options["source_options"])
    provenance_filter = st.sidebar.selectbox("Provenance", options["provenance_options"])
    viewer_ready_only = st.sidebar.checkbox("Viewer-ready only", value=False)
    search_text = st.sidebar.text_input("Search compound / reaction")

    filtered = filter_records(
        records=records,
        status_filter=status_filter,
        source_filter=source_filter,
        provenance_filter=provenance_filter,
        viewer_ready_only=viewer_ready_only,
        search_text=search_text,
    )

    compound_options = get_available_compounds(filtered)
    display_labels = [item["display_label"] for item in compound_options]

    selected_label = None
    selected_record = None

    if display_labels:
        selected_label = st.sidebar.selectbox("Compound selection", display_labels)
        selected_id = next(
            (
                item["compound_id"]
                for item in compound_options
                if item["display_label"] == selected_label
            ),
            None,
        )
        selected_record = next(
            (record for record in filtered if record.get("compound_id") == selected_id),
            None,
        )
    else:
        st.sidebar.warning("No records match the selected filters.")

    if selected_record:
        step_options = get_available_step_options(selected_record)
        step_map = {str(opt["step_label"]): int(opt["step_index"]) for opt in step_options}
        default_step_label = next(iter(step_map.keys())) if step_map else None

        selected_step_label = st.sidebar.selectbox(
            "Reaction step",
            list(step_map.keys()) if step_map else ["No step available"],
        )
        selected_step_index = step_map.get(selected_step_label, 0)

        conformer_options = get_available_conformer_options(selected_record)
        conformer_labels = ["Auto-select from step"]
        conformer_label_map = {"Auto-select from step": None}

        for item in conformer_options:
            conformer_labels.append(item["label"])
            conformer_label_map[item["label"]] = item["conformer_id"]

        selected_conformer_label = st.sidebar.selectbox(
            "Conformer",
            conformer_labels,
        )
        selected_conformer_id = conformer_label_map.get(selected_conformer_label)

        style_options = get_available_3d_styles()
        selected_style = st.sidebar.selectbox("3D render style", style_options, index=1 if "ball-and-stick" in style_options else 0)

        autoplay = st.sidebar.checkbox("Autoplay trajectory", value=False)
        show_labels = st.sidebar.checkbox("Show atom labels in 3D", value=True)
        playback_speed = st.sidebar.slider("Playback speed (ms)", 300, 2000, 900, 100)

    else:
        selected_step_index = 0
        selected_conformer_id = None
        selected_style = "ball-and-stick"
        autoplay = False
        show_labels = True
        playback_speed = 900

    return {
        "filtered_records": filtered,
        "selected_record": selected_record,
        "selected_step_index": selected_step_index,
        "selected_conformer_id": selected_conformer_id,
        "selected_style": selected_style,
        "autoplay": autoplay,
        "show_labels": show_labels,
        "playback_speed": playback_speed,
    }


def render_record_header(record: Dict[str, Any]) -> None:
    overview = get_compound_overview(record)

    left, right = st.columns([3, 1])

    with left:
        st.subheader(f"{overview['compound_id']} — {overview['compound_name']}")
        st.caption(f"SMILES: {overview['smiles']}")

    with right:
        st.markdown(
            get_status_badge_html(
                overview["validation_status"],
                overview["status_color"],
            ),
            unsafe_allow_html=True,
        )


def render_info_grid(record: Dict[str, Any]) -> None:
    overview = get_compound_overview(record)
    reaction = get_reaction_overview(record)
    synthesis = get_synthesis_conditions(record)

    cols = st.columns(4)

    blocks = [
        ("Molecular Formula", overview.get("molecular_formula")),
        ("Molecular Weight", overview.get("molecular_weight")),
        ("Source Project", overview.get("source_project")),
        ("Last Updated", overview.get("last_updated")),
        ("Reaction Name", reaction.get("reaction_name")),
        ("Catalyst", synthesis.get("catalyst")),
        ("Solvent", synthesis.get("solvent")),
        ("Temperature (°C)", synthesis.get("temperature_c")),
    ]

    for idx, (label, value) in enumerate(blocks):
        with cols[idx % 4]:
            st.markdown(
                f"""
                <div class="metric-mini">
                    <div class="metric-mini-label">{label}</div>
                    <div class="metric-mini-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_tab_molecular_control_center(
    record: Dict[str, Any],
    step_index: int,
    conformer_id: Optional[str],
    style: str,
    show_labels: bool,
) -> None:
    render_record_header(record)
    render_info_grid(record)

    left, right = st.columns([1, 1])

    with left:
        st.markdown("### 2D Molecular Structure")

        svg = generate_2d_svg(
            record=record,
            step_index=step_index,
            conformer_id=conformer_id,
            show_bond_labels=False,
            highlight_atoms=True,
            highlight_bonds=True,
        )

        if svg and "<svg" in svg:
            components.html(
                f"""
                <div style="
                    width:100%;
                    height:460px;
                    background:white;
                    border:1px solid #e5e7eb;
                    border-radius:12px;
                    overflow:hidden;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    padding:10px;
                    box-sizing:border-box;
                ">
                    <style>
                        .svg-wrap {{
                            width:100%;
                            height:100%;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            overflow:hidden;
                        }}
                        .svg-wrap svg {{
                            width:110% !important;
                            height:110% !important;
                            max-width:none !important;
                            max-height:none !important;
                            display:block;
                            margin:auto;
                        }}
                    </style>
                    <div class="svg-wrap">
                        {svg}
                    </div>
                </div>
                """,
                height=500,
                scrolling=False,
            )
        else:
            st.info("2D structure unavailable for this record.")

        state_desc = get_reaction_step_description(
            record,
            step_index=step_index,
            conformer_id=conformer_id,
        )

        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-title">2D Step Interpretation</div>
                <div class="info-body">
                    <strong>{state_desc.get('step_label', 'Unknown Step')}</strong> —
                    {state_desc.get('description', 'No description available.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### 3D Molecular Viewer")

        viewer_html = generate_3d_viewer_html(
            record=record,
            step_index=step_index,
            conformer_id=conformer_id,
            style=style,
            height=380,
            show_labels=False,
        )

        components.html(
            viewer_html,
            height=640,
            scrolling=False,
        )


def render_tab_geometry_and_metrics(
    record: Dict[str, Any],
    step_index: int,
    conformer_id: Optional[str],
) -> None:
    st.markdown("### Geometry & Structural Metrics")

    if not record:
        st.info("No record selected.")
        return

    state_summary = summarize_selected_state(
        record,
        step_index=step_index,
    )

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">Selected State Summary</div>
            <div class="info-body">
                <strong>{state_summary.get("step_label", "Unknown Step")}</strong><br>
                Stage: {state_summary.get("stage", "N/A")}<br>
                Transition State: {"Yes" if state_summary.get("is_transition_state", False) else "No"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Chiral Centers", record.get("chiral_centers", 0))
    with col2:
        st.metric("Validation Status", record.get("validation_status", "N/A"))
    with col3:
        st.metric("Viewer Ready", "Yes" if record.get("viewer_ready", False) else "No")

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">Stereochemistry Notes</div>
            <div class="info-body">
                {record.get("stereochemistry_notes", "No stereochemistry notes available.")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bond_metadata = record.get("bond_metadata", [])
    if bond_metadata:
        st.markdown("#### Bond Metadata")
        st.dataframe(bond_metadata, use_container_width=True)
    else:
        st.info("No bond metadata available for this record.")

def render_tab_reaction_pathway(
    record: Dict[str, Any],
    step_index: int,
    style: str,
    autoplay: bool,
    playback_speed: int,
    show_labels: bool,
):
    st.markdown("### Reaction Pathway & Energy Intelligence")

    mechanism_steps = record.get("mechanism_steps", []) or []

    if mechanism_steps and 0 <= step_index < len(mechanism_steps):
        current_step = mechanism_steps[step_index]
    else:
        current_step = {}

    reaction_name = record.get("reaction_name", "Conceptual Reaction Pathway")
    step_label = current_step.get("step_label", "N/A")
    stage = current_step.get("stage", "N/A")
    energy = current_step.get("relative_energy_kj_mol", "N/A")
    transition_state = "Yes" if current_step.get("transition_state", False) else "No"
    description = current_step.get("description", "No description available.")

    st.markdown(
        f"""
        <div style="
            margin: 8px 0 18px 0;
            padding: 16px 18px;
            border: 1px solid #dbe7ff;
            border-radius: 14px;
            background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
        ">
            <div style="font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 10px;">
                Reaction Summary
            </div>
            <div style="font-size: 14px; color: #334155; line-height: 1.7;">
                <strong>Reaction:</strong> {reaction_name}<br>
                <strong>Current Step:</strong> {step_label}<br>
                <strong>Stage:</strong> {stage}<br>
                <strong>Relative Energy:</strong> {energy} kJ/mol<br>
                <strong>Transition State:</strong> {transition_state}<br>
                <strong>Description:</strong> {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if mechanism_steps:
        left, right = st.columns([2, 1])

        with left:
            x_labels = [step.get("step_label", f"Step {i+1}") for i, step in enumerate(mechanism_steps)]
            y_values = [step.get("relative_energy_kj_mol", 0.0) for step in mechanism_steps]
            is_ts = [step.get("transition_state", False) for step in mechanism_steps]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=x_labels,
                    y=y_values,
                    mode="lines+markers",
                    name="Energy Profile (kJ/mol)",
                    line=dict(color="#5b6cf9", width=3),
                    marker=dict(
                        size=[14 if flag else 10 for flag in is_ts],
                        color=["crimson" if flag else "#5b6cf9" for flag in is_ts],
                        symbol=["diamond" if flag else "circle" for flag in is_ts],
                    ),
                )
            )

            fig.update_layout(
                title=f"Reaction Coordinate — {reaction_name}",
                xaxis_title="Mechanism Step",
                yaxis_title="Relative Energy (kJ/mol)",
                height=380,
                margin=dict(l=20, r=20, t=55, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )

            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown("#### Mechanism Step Labels")
            step_labels = get_mechanism_step_labels(record)
            if step_labels:
                for label in step_labels:
                    st.markdown(f"- {label}")
            else:
                st.info("No mechanism step labels available.")
    else:
        st.info("No mechanism step data available for this record.")

    st.markdown("### 3D Trajectory Playback")

    playback_html = generate_playback_html(
        record=record,
        start_step_index=step_index,
        style=style,
        autoplay=autoplay,
        playback_speed_ms=playback_speed,
        show_labels=show_labels,
    )

    if playback_html and isinstance(playback_html, str):
        components.html(playback_html, height=720, scrolling=False)
    else:
        st.warning("Reaction playback unavailable for this record.")

def render_tab_synthesis_and_provenance(record: Dict[str, Any]) -> None:
    st.markdown("### Synthesis Conditions and Provenance")

    synthesis = get_synthesis_conditions(record)
    reaction = get_reaction_overview(record)

    left, right = st.columns(2)

    with left:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="info-title">Synthesis Condition Card</div>
                <div class="info-body">
                    <strong>Temperature:</strong> {synthesis.get('temperature_c')} °C<br>
                    <strong>Pressure:</strong> {synthesis.get('pressure_bar')} bar<br>
                    <strong>Solvent:</strong> {synthesis.get('solvent')}<br>
                    <strong>Catalyst:</strong> {synthesis.get('catalyst')}<br>
                    <strong>Reaction Time:</strong> {synthesis.get('reaction_time_hr')} hr<br>
                    <strong>pH:</strong> {synthesis.get('ph')}<br>
                    <strong>Expected Yield:</strong> {synthesis.get('expected_yield_pct')} %
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="info-title">Provenance and Confidence</div>
                <div class="info-body">
                    <strong>Provenance Type:</strong> {reaction.get('provenance_type')}<br>
                    <strong>Confidence Score:</strong> {reaction.get('confidence_score')}<br>
                    <strong>Transition State Label:</strong> {reaction.get('transition_state_label')}<br>
                    <strong>Reaction Name:</strong> {reaction.get('reaction_name')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">Provenance Interpretation</div>
            <div class="info-body">{interpret_provenance(record)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tab_operational_monitoring(record: Dict[str, Any], filtered_records: List[Dict[str, Any]]) -> None:
    st.markdown("### Operational Monitoring and Export")

    record_table = get_record_table(filtered_records)
    st.dataframe(record_table, use_container_width=True, hide_index=True)

    st.markdown("### Export Options")
    payloads = get_download_payloads(record, filtered_records)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "Download record JSON",
            data=payloads["record_json"],
            file_name=f"{record.get('compound_id', 'record').lower()}_record.json",
            mime="application/json",
        )
    with c2:
        st.download_button(
            "Download record Markdown",
            data=payloads["record_markdown"],
            file_name=f"{record.get('compound_id', 'record').lower()}_record.md",
            mime="text/markdown",
        )
    with c3:
        st.download_button(
            "Download filtered CSV",
            data=payloads["records_csv"],
            file_name="chemdata_control_center_records.csv",
            mime="text/csv",
        )

    st.markdown("### Local Export Helpers")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        if st.button("Export current 2D SVG to file"):
            svg_path = EXPORT_DIR / f"{record.get('compound_id', 'record').lower()}_2d.svg"
            export_2d_svg(record, str(svg_path))
            st.success(f"Saved 2D SVG to: {svg_path}")

    with export_col2:
        if st.button("Export 3D playback bundle to file"):
            bundle_path = EXPORT_DIR / f"{record.get('compound_id', 'record').lower()}_playback_bundle.json"
            export_playback_bundle_json(record, str(bundle_path))
            st.success(f"Saved playback bundle to: {bundle_path}")

    st.markdown("### Dashboard Summary")
    summary_md = build_summary_markdown(filtered_records)
    st.markdown(summary_md)

def _reaction_svg_from_smiles(smiles: str, width: int = 560, height: int = 320) -> str:
    """
    Create a 2D SVG for a reaction step from SMILES.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return """
        <div style="display:flex; align-items:center; justify-content:center; height:100%; color:#991b1b; font-family:Arial, sans-serif;">
            Invalid reaction-step SMILES
        </div>
        """

    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    opts = drawer.drawOptions()
    opts.padding = 0.08
    opts.bondLineWidth = 2
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
    drawer.FinishDrawing()

    svg = drawer.GetDrawingText().replace("svg:", "")
    return svg


def get_conceptual_reaction_steps(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build a conceptual reaction-step list for playback.
    Priority:
    1) record['reaction_animation']['mechanism_steps']
    2) record['mechanism_steps']
    3) fallback conceptual A + B -> C + D demo
    """
    reaction_animation = record.get("reaction_animation", {})
    source_steps = reaction_animation.get("mechanism_steps") or record.get("mechanism_steps") or []

    normalized_steps: List[Dict[str, Any]] = []
    for idx, step in enumerate(source_steps):
        normalized_steps.append(
            {
                "step_index": idx,
                "step_label": step.get("step_label", f"Step {idx + 1}"),
                "description": step.get("description", "Conceptual reaction state."),
                "smiles": step.get("smiles", record.get("smiles", "")),
                "energy_kj_mol": step.get(
                    "relative_energy_kj_mol",
                    step.get("energy_kj_mol", 0.0),
                ),
            }
        )

    if normalized_steps:
        return normalized_steps

    # Fallback conceptual demo if no mechanism steps exist on the record
    return [
        {
            "step_index": 0,
            "step_label": "A + B (Reactants)",
            "description": "Separated reactants before interaction begins.",
            "smiles": "CCO.O",
            "energy_kj_mol": 0.0,
        },
        {
            "step_index": 1,
            "step_label": "Encounter Complex",
            "description": "Reactants approach and align for interaction.",
            "smiles": "CCO.O",
            "energy_kj_mol": 8.0,
        },
        {
            "step_index": 2,
            "step_label": "Transition-like State",
            "description": "Conceptual high-energy state during rearrangement.",
            "smiles": "CCO.O",
            "energy_kj_mol": 22.0,
        },
        {
            "step_index": 3,
            "step_label": "C + D (Products)",
            "description": "Separated products after the conceptual reaction step.",
            "smiles": "CC=O.O",
            "energy_kj_mol": -6.0,
        },
    ]


def render_tab_conceptual_reaction_animation(record: Dict[str, Any]) -> None:
    """
    Render a conceptual 2D reaction animation tab using client-side HTML/JS playback.
    """
    st.markdown("### Conceptual Reaction Animation")
    st.caption(
        "Frame-based conceptual playback for a reaction pathway. "
        "This is a visual interpretation aid, not a kinetics or quantum-mechanical simulator."
    )

    reaction_label = (
        record.get("reaction_animation", {}).get("reaction_label")
        or record.get("reaction_name")
        or "A + B → C + D"
    )

    steps = get_conceptual_reaction_steps(record)
    frames: List[Dict[str, Any]] = []

    for step in steps:
        frames.append(
            {
                "step_label": step["step_label"],
                "description": step["description"],
                "energy_kj_mol": step["energy_kj_mol"],
                "svg": _reaction_svg_from_smiles(step["smiles"]),
            }
        )

    frames_json = json.dumps(frames)
    reaction_label_json = json.dumps(reaction_label)

    components.html(
        f"""
        <div style="width:100%; font-family:Arial, sans-serif;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div style="font-size:20px; font-weight:700; color:#0f172a;">Conceptual 2D Reaction Playback</div>
            <div style="font-size:12px; color:#475569;">Client-side step animation</div>
          </div>

          <div style="border:1px solid #dbe7ff; border-radius:16px; background:white; padding:16px; box-sizing:border-box;">
            <div id="reaction2dStage"
                 style="height:360px; border:1px solid #e5e7eb; border-radius:12px; background:white; display:flex; align-items:center; justify-content:center; overflow:hidden; padding:8px; box-sizing:border-box;">
            </div>

            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-top:14px;">
              <button onclick="prevReaction2DFrame()"
                      style="padding:8px 12px; border-radius:10px; border:1px solid #cbd5e1; background:white; cursor:pointer;">
                ◀ Prev
              </button>

              <button onclick="toggleReaction2DPlayback()"
                      id="reaction2DPlayBtn"
                      style="padding:8px 12px; border-radius:10px; border:1px solid #cbd5e1; background:white; cursor:pointer;">
                Play
              </button>

              <button onclick="nextReaction2DFrame()"
                      style="padding:8px 12px; border-radius:10px; border:1px solid #cbd5e1; background:white; cursor:pointer;">
                Next ▶
              </button>

              <input type="range"
                     id="reaction2DSlider"
                     min="0"
                     max="{max(len(frames) - 1, 0)}"
                     value="0"
                     step="1"
                     oninput="setReaction2DFrame(parseInt(this.value))"
                     style="width:260px;" />

              <span style="font-weight:600; color:#1e3a8a;">Frame:</span>
              <span id="reaction2DFrameCounter" style="color:#334155;">1 / {len(frames)}</span>
            </div>

            <div style="margin-top:14px; padding:14px 16px; border:1px solid #dbe7ff; border-radius:14px; background:#f8fbff; color:#334155; font-size:13px; line-height:1.65;">
              <div><strong>Reaction:</strong> <span id="reaction2DEquation"></span></div>
              <div><strong>Step:</strong> <span id="reaction2DStepLabel"></span></div>
              <div><strong>Energy:</strong> <span id="reaction2DEnergy"></span></div>
              <div><strong>Description:</strong> <span id="reaction2DDescription"></span></div>
            </div>
          </div>
        </div>

        <script>
          (function() {{
            const frames = {frames_json};
            const reactionLabel = {reaction_label_json};
            let currentFrameIndex = 0;
            let autoplayTimer = null;
            let isPlaying = false;

            function renderReaction2DFrame(index) {{
              const frame = frames[index];
              document.getElementById("reaction2dStage").innerHTML = frame.svg || "";
              document.getElementById("reaction2DSlider").value = index;
              document.getElementById("reaction2DFrameCounter").textContent = `${{index + 1}} / ${{frames.length}}`;
              document.getElementById("reaction2DEquation").textContent = reactionLabel;
              document.getElementById("reaction2DStepLabel").textContent = frame.step_label || "N/A";
              document.getElementById("reaction2DEnergy").textContent = `${{frame.energy_kj_mol ?? "N/A"}} kJ/mol`;
              document.getElementById("reaction2DDescription").textContent = frame.description || "";
            }}

            window.setReaction2DFrame = function(index) {{
              currentFrameIndex = index;
              renderReaction2DFrame(currentFrameIndex);
            }}

            window.nextReaction2DFrame = function() {{
              currentFrameIndex = (currentFrameIndex + 1) % frames.length;
              renderReaction2DFrame(currentFrameIndex);
            }}

            window.prevReaction2DFrame = function() {{
              currentFrameIndex = (currentFrameIndex - 1 + frames.length) % frames.length;
              renderReaction2DFrame(currentFrameIndex);
            }}

            function stopReaction2DPlayback() {{
              if (autoplayTimer) {{
                clearInterval(autoplayTimer);
                autoplayTimer = null;
              }}
              isPlaying = false;
              document.getElementById("reaction2DPlayBtn").textContent = "Play";
            }}

            function startReaction2DPlayback() {{
              stopReaction2DPlayback();
              isPlaying = true;
              document.getElementById("reaction2DPlayBtn").textContent = "Pause";
              autoplayTimer = setInterval(() => {{
                currentFrameIndex = (currentFrameIndex + 1) % frames.length;
                renderReaction2DFrame(currentFrameIndex);
              }}, 900);
            }}

            window.toggleReaction2DPlayback = function() {{
              if (isPlaying) {{
                stopReaction2DPlayback();
              }} else {{
                startReaction2DPlayback();
              }}
            }}

            renderReaction2DFrame(0);
          }})();
        </script>
        """,
        height=620,
        scrolling=False,
    )

def main() -> None:
    inject_custom_css()
    render_hero()

    try:
        records = load_dashboard_records(str(DATA_FILE))
    except Exception as exc:
        st.error(f"Failed to load dashboard data: {exc}")
        st.stop()

    render_kpis(records)

    controls = sidebar_filters(records)
    filtered_records = controls["filtered_records"]
    selected_record = controls["selected_record"]

    if not selected_record:
        st.info("No record is currently selected. Adjust the filters in the sidebar to continue.")
        return

    selected_step_index = controls["selected_step_index"]
    selected_conformer_id = controls["selected_conformer_id"]
    selected_style = controls["selected_style"]
    autoplay = controls["autoplay"]
    show_labels = controls["show_labels"]
    playback_speed = controls["playback_speed"]

    tabs = st.tabs(
        [
            "Molecular Control Center",
            "Conceptual Reaction Animation",
            "Geometry & Structural Metrics",
            "Reaction Pathway & Energy Intelligence",
            "Synthesis Conditions & Provenance",
            "Operational Monitoring",
        ]
    )

    with tabs[0]:
        render_tab_molecular_control_center(
            record=selected_record,
            step_index=selected_step_index,
            conformer_id=selected_conformer_id,
            style=selected_style,
            show_labels=show_labels,
        )

    with tabs[1]:
        render_tab_conceptual_reaction_animation(selected_record)

    with tabs[2]:
        render_tab_geometry_and_metrics(
            record=selected_record,
            step_index=selected_step_index,
            conformer_id=selected_conformer_id,
        )

    with tabs[3]:
        render_tab_reaction_pathway(
            record=selected_record,
            step_index=selected_step_index,
            style=selected_style,
            autoplay=autoplay,
            playback_speed=playback_speed,
            show_labels=show_labels,
        )

    with tabs[4]:
        render_tab_synthesis_and_provenance(selected_record)

    with tabs[5]:
        render_tab_operational_monitoring(selected_record, filtered_records)


if __name__ == "__main__":
    main()

