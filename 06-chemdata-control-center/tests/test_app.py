import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from data_loader import (
    get_dashboard_summary,
    get_energy_profile,
    get_trajectory_frames,
    load_records,
)
from dashboard_utils import (
    build_energy_cards,
    build_reaction_pathway_summary,
    get_mechanism_step_labels,
    summarize_selected_state,
)
from molecule_viewer_2d import (
    generate_2d_svg,
    get_available_conformer_options,
    get_available_step_options,
    get_reaction_step_description,
)
from molecule_viewer_3d import (
    build_3d_state_package,
    build_trajectory_playback_package,
    get_3d_state_summary,
)


DATA_FILE = PROJECT_ROOT / "data" / "sample_records.json"


def _load_sample_records():
    return load_records(str(DATA_FILE))


def test_data_loading_smoke():
    records = _load_sample_records()

    assert isinstance(records, list)
    assert len(records) >= 3

    first = records[0]
    required_keys = [
        "compound_id",
        "compound_name",
        "smiles",
        "molecular_formula",
        "molecular_weight",
        "validation_status",
        "mechanism_steps",
        "energy_profile",
        "trajectory_frames",
        "conformers",
        "bond_metadata",
    ]

    for key in required_keys:
        assert key in first, f"Missing required key: {key}"


def test_dashboard_summary_smoke():
    records = _load_sample_records()
    summary = get_dashboard_summary(records)

    assert summary["total_records"] >= 3
    assert "pass_count" in summary
    assert "warn_count" in summary
    assert "viewer_ready_count" in summary
    assert "reaction_enabled_count" in summary


def test_energy_profile_smoke():
    records = _load_sample_records()
    record = records[0]

    energy_df = get_energy_profile(record)

    assert not energy_df.empty
    assert "step_label" in energy_df.columns
    assert "energy_kj_mol" in energy_df.columns
    assert len(energy_df) >= 3


def test_trajectory_frames_smoke():
    records = _load_sample_records()
    record = records[0]

    traj_df = get_trajectory_frames(record)

    assert not traj_df.empty
    assert "frame_id" in traj_df.columns
    assert "step_index" in traj_df.columns
    assert "step_label" in traj_df.columns
    assert len(traj_df) >= 3


def test_reaction_step_handling_smoke():
    records = _load_sample_records()
    record = records[0]

    step_labels = get_mechanism_step_labels(record)
    step_options = get_available_step_options(record)

    assert len(step_labels) >= 3
    assert len(step_options) >= 3
    assert "step_index" in step_options[0]
    assert "step_label" in step_options[0]

    state_summary = summarize_selected_state(record, step_index=0)
    assert "step_label" in state_summary
    assert "stage" in state_summary
    assert "description" in state_summary


def test_reaction_pathway_summary_smoke():
    records = _load_sample_records()
    record = records[0]

    pathway_summary = build_reaction_pathway_summary(record)

    assert isinstance(pathway_summary, list)
    assert len(pathway_summary) >= 3
    assert "step_label" in pathway_summary[0]
    assert "relative_energy_kj_mol" in pathway_summary[0]


def test_energy_cards_smoke():
    records = _load_sample_records()
    record = records[0]

    cards = build_energy_cards(record)

    assert "activation_energy_kj_mol" in cards
    assert "activation_energy_kcal_mol" in cards
    assert "delta_h_kj_mol" in cards
    assert "delta_g_kj_mol" in cards


def test_2d_rendering_smoke():
    records = _load_sample_records()
    record = records[0]

    svg = generate_2d_svg(record=record, step_index=0)

    assert isinstance(svg, str)
    assert "<svg" in svg.lower()
    assert "</svg>" in svg.lower()


def test_conformer_options_smoke():
    records = _load_sample_records()
    record = records[0]

    conformer_options = get_available_conformer_options(record)

    assert isinstance(conformer_options, list)
    assert len(conformer_options) >= 1
    assert "conformer_id" in conformer_options[0]
    assert "label" in conformer_options[0]


def test_reaction_step_description_smoke():
    records = _load_sample_records()
    record = records[0]

    desc = get_reaction_step_description(record, step_index=0)

    assert "step_label" in desc
    assert "stage" in desc
    assert "description" in desc


def test_3d_state_package_smoke():
    records = _load_sample_records()
    record = records[0]

    pkg = build_3d_state_package(record=record, step_index=0)

    assert isinstance(pkg, dict)
    assert "molblock" in pkg
    assert "compound_id" in pkg
    assert "step_label" in pkg
    assert "highlight_atoms" in pkg
    assert "highlight_bonds" in pkg
    assert isinstance(pkg["molblock"], str)
    assert len(pkg["molblock"]) > 50


def test_3d_state_summary_smoke():
    records = _load_sample_records()
    record = records[0]

    summary = get_3d_state_summary(record=record, step_index=0)

    assert "compound_id" in summary
    assert "step_label" in summary
    assert "stage" in summary
    assert "highlight_atom_count" in summary
    assert "highlight_bond_count" in summary


def test_trajectory_playback_package_smoke():
    records = _load_sample_records()
    record = records[0]

    playback = build_trajectory_playback_package(record=record)

    assert isinstance(playback, list)
    assert len(playback) >= 3
    assert "molblock" in playback[0]
    assert "step_label" in playback[0]
    assert "frame_id" in playback[0]
