from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalize_bond_pair(pair: Any) -> Optional[Tuple[int, int]]:
    if not isinstance(pair, (list, tuple)) or len(pair) != 2:
        return None

    try:
        a = int(pair[0])
        b = int(pair[1])
        return tuple(sorted((a, b)))
    except (TypeError, ValueError):
        return None


def _get_mechanism_step(record: Dict[str, Any], step_index: int) -> Optional[Dict[str, Any]]:
    for step in record.get("mechanism_steps", []):
        try:
            if int(step.get("step_index", -1)) == int(step_index):
                return step
        except (TypeError, ValueError):
            continue
    return None


def _get_trajectory_frame(record: Dict[str, Any], step_index: int) -> Optional[Dict[str, Any]]:
    for frame in record.get("trajectory_frames", []):
        try:
            if int(frame.get("step_index", -1)) == int(step_index):
                return frame
        except (TypeError, ValueError):
            continue
    return None


def _get_conformer_by_id(record: Dict[str, Any], conformer_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not conformer_id:
        return None
    for conformer in record.get("conformers", []):
        if conformer.get("conformer_id") == conformer_id:
            return conformer
    return None


def _get_frame_by_id(record: Dict[str, Any], frame_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not frame_id:
        return None
    for frame in record.get("trajectory_frames", []):
        if frame.get("frame_id") == frame_id:
            return frame
    return None


def _resolve_selected_state(
    record: Dict[str, Any],
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resolve the best available state for 2D rendering.
    Priority:
    1. conformer_id -> linked frame
    2. explicit step_index
    3. first trajectory frame
    4. base record
    """
    selected_conformer = _get_conformer_by_id(record, conformer_id)
    if selected_conformer:
        linked_frame = _get_frame_by_id(record, selected_conformer.get("frame_id"))
        if linked_frame:
            linked_step = _get_mechanism_step(record, linked_frame.get("step_index", 0))
            return {
                "step": linked_step,
                "frame": linked_frame,
                "conformer": selected_conformer,
            }

    if step_index is not None:
        selected_frame = _get_trajectory_frame(record, step_index)
        selected_step = _get_mechanism_step(record, step_index)
        return {
            "step": selected_step,
            "frame": selected_frame,
            "conformer": None,
        }

    frames = record.get("trajectory_frames", [])
    if frames:
        first_frame = frames[0]
        selected_step = _get_mechanism_step(record, first_frame.get("step_index", 0))
        return {
            "step": selected_step,
            "frame": first_frame,
            "conformer": None,
        }

    return {
        "step": None,
        "frame": None,
        "conformer": None,
    }


def _get_state_smiles(record: Dict[str, Any], state: Dict[str, Any]) -> str:
    if state.get("frame") and state["frame"].get("smiles"):
        return state["frame"]["smiles"]
    if state.get("step") and state["step"].get("smiles"):
        return state["step"]["smiles"]
    return record.get("smiles", "")


def _build_molecule_from_smiles(smiles: str) -> Chem.Mol:
    if not smiles:
        raise ValueError("No SMILES string available for 2D rendering.")

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES for 2D rendering: {smiles}")

    mol = Chem.AddHs(mol)
    AllChem.Compute2DCoords(mol)
    return mol


def _collect_highlight_atoms(state: Dict[str, Any]) -> List[int]:
    if state.get("frame"):
        return [int(x) for x in _safe_list(state["frame"].get("highlight_atoms"))]
    if state.get("step"):
        return [int(x) for x in _safe_list(state["step"].get("highlight_atoms"))]
    return []


def _collect_highlight_bonds(state: Dict[str, Any]) -> List[Tuple[int, int]]:
    raw = []
    if state.get("frame"):
        raw = _safe_list(state["frame"].get("highlight_bonds"))
    elif state.get("step"):
        raw = _safe_list(state["step"].get("highlight_bonds"))

    normalized = []
    for item in raw:
        pair = _normalize_bond_pair(item)
        if pair is not None:
            normalized.append(pair)
    return normalized


def _map_bond_pairs_to_indices(mol: Chem.Mol, bond_pairs: List[Tuple[int, int]]) -> List[int]:
    indices = []
    for bond in mol.GetBonds():
        pair = tuple(sorted((bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())))
        if pair in bond_pairs:
            indices.append(bond.GetIdx())
    return indices


def _build_atom_label_overrides(mol: Chem.Mol) -> Dict[int, str]:
    """
    Use human-readable labels like C1, O3, N5.
    """
    labels = {}
    for atom in mol.GetAtoms():
        labels[atom.GetIdx()] = f"{atom.GetSymbol()}{atom.GetIdx()}"
    return labels


def _format_bond_label(bond_row: Dict[str, Any]) -> str:
    bond_type = bond_row.get("bond_type", "")
    atoms = bond_row.get("atoms", "")
    length = bond_row.get("length_angstrom", None)

    if length is not None:
        try:
            return f"{bond_type} {atoms} ({float(length):.3f} Å)"
        except (TypeError, ValueError):
            pass

    return f"{bond_type} {atoms}".strip()


def _add_text_before_svg_close(svg_text: str, extra_markup: str) -> str:
    closing_tag = "</svg>"
    idx = svg_text.rfind(closing_tag)
    if idx == -1:
        return svg_text + extra_markup
    return svg_text[:idx] + extra_markup + svg_text[idx:]


def _build_bond_annotation_markup(
    mol: Chem.Mol,
    drawer: rdMolDraw2D.MolDraw2DSVG,
    bond_metadata: List[Dict[str, Any]],
    state_step_label: Optional[str] = None,
    show_bond_labels: bool = True,
) -> str:
    """
    Overlay SVG text labels near bond midpoints for matching state scope.
    """
    if not show_bond_labels or not bond_metadata:
        return ""

    overlay_parts = ['<g id="bond-label-overlays">']

    # Build quick lookup from bond atom pair -> midpoint
    bond_midpoints: Dict[Tuple[int, int], Tuple[float, float]] = {}
    for bond in mol.GetBonds():
        a1 = bond.GetBeginAtomIdx()
        a2 = bond.GetEndAtomIdx()
        p1 = drawer.GetDrawCoords(a1)
        p2 = drawer.GetDrawCoords(a2)
        pair = tuple(sorted((a1, a2)))
        bond_midpoints[pair] = ((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)

    for row in bond_metadata:
        atoms = str(row.get("atoms", ""))
        pair = _parse_atoms_label_to_pair(atoms)
        if pair is None or pair not in bond_midpoints:
            continue

        x, y = bond_midpoints[pair]
        label = _format_bond_label(row)

        overlay_parts.append(
            f"""
            <text x="{x:.2f}" y="{y - 10:.2f}"
                  text-anchor="middle"
                  font-size="10"
                  font-family="Arial, sans-serif"
                  fill="#1f2937"
                  style="font-weight:600;">
                {label}
            </text>
            """
        )

    overlay_parts.append("</g>")
    return "\n".join(overlay_parts)


def _parse_atoms_label_to_pair(atoms_label: str) -> Optional[Tuple[int, int]]:
    """
    Accepts strings like 'C1-C2' or 'O11-H12' and returns (1,2), (11,12).
    Note: assumes labels match atom index numbering used in this portfolio dataset.
    """
    try:
        left, right = atoms_label.split("-")
        left_num = int("".join(ch for ch in left if ch.isdigit()))
        right_num = int("".join(ch for ch in right if ch.isdigit()))
        return tuple(sorted((left_num, right_num)))
    except Exception:
        return None


def _collect_state_bond_metadata(record: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    step_label = None
    stage = None

    if state.get("step"):
        step_label = state["step"].get("step_label")
        stage = state["step"].get("stage")

    filtered = []
    for row in record.get("bond_metadata", []):
        scope = str(row.get("step_scope", "baseline")).lower()

        if scope == "baseline":
            filtered.append(row)
        elif stage and scope == stage.lower():
            filtered.append(row)
        elif step_label and scope == str(step_label).lower():
            filtered.append(row)

    return filtered


def get_2d_render_state_summary(
    record: Dict[str, Any],
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
) -> Dict[str, Any]:
    state = _resolve_selected_state(record, step_index=step_index, conformer_id=conformer_id)
    smiles = _get_state_smiles(record, state)

    return {
        "compound_id": record.get("compound_id"),
        "compound_name": record.get("compound_name"),
        "selected_step_label": (state.get("step") or {}).get("step_label"),
        "selected_stage": (state.get("step") or state.get("frame") or {}).get("stage"),
        "selected_frame_id": (state.get("frame") or {}).get("frame_id"),
        "selected_conformer_id": (state.get("conformer") or {}).get("conformer_id"),
        "smiles": smiles,
        "highlight_atoms": _collect_highlight_atoms(state),
        "highlight_bonds": _collect_highlight_bonds(state),
        "bond_events": (state.get("frame") or state.get("step") or {}).get("bond_events", []),
        "playback_note": (state.get("frame") or {}).get("playback_note", ""),
    }


def generate_2d_svg(
    record: Dict[str, Any],
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
    width: int = 560,
    height: int = 460,                 
    show_atom_indices: bool = False,
    show_bond_labels: bool = True,
    highlight_atoms: bool = True,
    highlight_bonds: bool = True,
    annotate_state: bool = True,
) -> str:
    """
    Main 2D rendering function for Streamlit/dashboard use.
    Supports:
    - reaction step selection
    - conformer-linked frame selection
    - atom highlighting
    - bond highlighting
    - bond label overlays
    """
    state = _resolve_selected_state(record, step_index=step_index, conformer_id=conformer_id)
    smiles = _get_state_smiles(record, state)
    mol = _build_molecule_from_smiles(smiles)

    atom_highlights = _collect_highlight_atoms(state) if highlight_atoms else []
    bond_pairs = _collect_highlight_bonds(state) if highlight_bonds else []
    bond_indices = _map_bond_pairs_to_indices(mol, bond_pairs)

    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    options = drawer.drawOptions()
    options.padding = 0.04
    options.legendFontSize = 16
    options.bondLineWidth = 2
    options.fixedBondLength = 25

    if show_atom_indices:
        options.addAtomIndices = True
    else:
        # custom labels like C0, O1, N2
        atom_label_map = _build_atom_label_overrides(mol)
        for atom_idx, label in atom_label_map.items():
            options.atomLabels[atom_idx] = label

    # Styling colors
    atom_color_map = {idx: (0.85, 0.15, 0.15) for idx in atom_highlights}
    bond_color_map = {idx: (0.12, 0.29, 0.85) for idx in bond_indices}
    highlight_radii = {idx: 0.45 for idx in atom_highlights}

    legend_parts = []
    if annotate_state:
        if state.get("step") and state["step"].get("step_label"):
            legend_parts.append(str(state["step"]["step_label"]))
        if state.get("conformer") and state["conformer"].get("conformer_id"):
            legend_parts.append(str(state["conformer"]["conformer_id"]))

    legend_text = " | ".join(legend_parts) if legend_parts else record.get("compound_name", "2D Molecule")

    rdMolDraw2D.PrepareAndDrawMolecule(
        drawer,
        mol,
        legend=legend_text,
        highlightAtoms=atom_highlights,
        highlightAtomColors=atom_color_map,
        highlightAtomRadii=highlight_radii,
        highlightBonds=bond_indices,
        highlightBondColors=bond_color_map,
    )

    drawer.FinishDrawing()
    svg_text = drawer.GetDrawingText()

    state_bond_metadata = _collect_state_bond_metadata(record, state)
    bond_markup = _build_bond_annotation_markup(
        mol=mol,
        drawer=drawer,
        bond_metadata=state_bond_metadata,
        state_step_label=(state.get("step") or {}).get("step_label"),
        show_bond_labels=show_bond_labels,
    )

    if bond_markup:
        svg_text = _add_text_before_svg_close(svg_text, bond_markup)

    return svg_text


def export_2d_svg(
    record: Dict[str, Any],
    output_file: str,
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
    width: int = 560,
    height: int = 460,
    show_atom_indices: bool = False,
    show_bond_labels: bool = True,
) -> str:
    svg = generate_2d_svg(
        record=record,
        step_index=step_index,
        conformer_id=conformer_id,
        width=width,
        height=height,
        show_atom_indices=show_atom_indices,
        show_bond_labels=show_bond_labels,
    )

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")

    return str(output_path.resolve())


def get_available_conformer_options(record: Dict[str, Any]) -> List[Dict[str, str]]:
    options = []
    for conformer in record.get("conformers", []):
        conformer_id = conformer.get("conformer_id", "")
        step_label = conformer.get("step_label", "")
        source = conformer.get("source", "")
        label = f"{conformer_id} — {step_label} ({source})".strip()
        options.append(
            {
                "conformer_id": conformer_id,
                "label": label,
            }
        )
    return options


def get_available_step_options(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    options = []
    for step in record.get("mechanism_steps", []):
        options.append(
            {
                "step_index": step.get("step_index"),
                "step_label": step.get("step_label"),
                "stage": step.get("stage"),
                "description": step.get("description", ""),
            }
        )
    return options


def get_reaction_step_description(
    record: Dict[str, Any],
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
) -> Dict[str, Any]:
    state = _resolve_selected_state(record, step_index=step_index, conformer_id=conformer_id)
    step = state.get("step") or {}
    frame = state.get("frame") or {}

    return {
        "step_label": step.get("step_label", "Unknown Step"),
        "stage": step.get("stage", frame.get("stage", "unknown")),
        "description": step.get("description", frame.get("playback_note", "")),
        "bond_events": frame.get("bond_events", step.get("bond_events", [])),
        "highlight_atoms": frame.get("highlight_atoms", step.get("highlight_atoms", [])),
        "highlight_bonds": frame.get("highlight_bonds", step.get("highlight_bonds", [])),
    }
