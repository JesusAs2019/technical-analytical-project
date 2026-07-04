from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rdkit import Chem
from rdkit.Chem import AllChem

try:
    import py3Dmol
except ImportError:  # pragma: no cover
    py3Dmol = None


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
    Resolve selection priority:
    1. conformer_id -> linked frame
    2. explicit step_index
    3. first trajectory frame
    4. base record only
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


def _seed_from_text(*parts: str) -> int:
    text = "|".join(str(p) for p in parts if p is not None)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Keep seed within safe 32-bit signed integer range for RDKit
    seed = int(digest[:8], 16) % 2147483647

    if seed == 0:
        seed = 104729

    return seed


def _build_3d_molecule(
    smiles: str,
    seed: int,
    add_hs: bool = True,
    embed_method: str = "ETKDGv3",
    optimize_method: str = "MMFF94",
) -> Chem.Mol:
    if not smiles:
        raise ValueError("No SMILES string available for 3D rendering.")

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES for 3D rendering: {smiles}")

    if add_hs:
        mol = Chem.AddHs(mol)
     
    params = AllChem.ETKDGv3()
    params.randomSeed = int(seed % 2147483647)
    params.useRandomCoords = False

    embed_status = AllChem.EmbedMolecule(mol, params)
    if embed_status != 0:
        raise RuntimeError(f"3D embedding failed for SMILES: {smiles}")

    if optimize_method.upper() == "MMFF94":
        mmff_ok = AllChem.MMFFHasAllMoleculeParams(mol)
        if mmff_ok:
            AllChem.MMFFOptimizeMolecule(mol, mmffVariant="MMFF94")
        else:
            AllChem.UFFOptimizeMolecule(mol)
    else:
        AllChem.UFFOptimizeMolecule(mol)

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

    pairs = []
    for item in raw:
        pair = _normalize_bond_pair(item)
        if pair is not None:
            pairs.append(pair)
    return pairs


def _build_atom_overlay_data(mol: Chem.Mol, atom_indices: List[int]) -> List[Dict[str, Any]]:
    conf = mol.GetConformer()
    overlays = []

    for atom_idx in atom_indices:
        if atom_idx < 0 or atom_idx >= mol.GetNumAtoms():
            continue

        atom = mol.GetAtomWithIdx(atom_idx)
        pos = conf.GetAtomPosition(atom_idx)
        overlays.append(
            {
                "atom_index": atom_idx,
                "label": f"{atom.GetSymbol()}{atom_idx}",
                "x": float(pos.x),
                "y": float(pos.y),
                "z": float(pos.z),
                "color": "#dc2626",
                "radius": 0.38,
            }
        )

    return overlays


def _build_bond_overlay_data(mol: Chem.Mol, bond_pairs: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
    conf = mol.GetConformer()
    overlays = []

    for a1, a2 in bond_pairs:
        if a1 < 0 or a2 < 0 or a1 >= mol.GetNumAtoms() or a2 >= mol.GetNumAtoms():
            continue

        p1 = conf.GetAtomPosition(a1)
        p2 = conf.GetAtomPosition(a2)

        overlays.append(
            {
                "bond_pair": [a1, a2],
                "start": {"x": float(p1.x), "y": float(p1.y), "z": float(p1.z)},
                "end": {"x": float(p2.x), "y": float(p2.y), "z": float(p2.z)},
                "color": "#2563eb",
                "radius": 0.12,
            }
        )

    return overlays


def get_available_3d_styles() -> List[str]:
    return ["stick", "ball-and-stick", "sphere"]


def _get_style_spec(style: str) -> Dict[str, Any]:
    style = (style or "ball-and-stick").lower()

    if style == "stick":
        return {"stick": {}}

    if style == "sphere":
        return {"sphere": {"scale": 0.32}}

    # default ball-and-stick
    return {
        "stick": {},
        "sphere": {"scale": 0.28},
    }


def build_3d_state_package(
    record: Dict[str, Any],
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
    style: str = "ball-and-stick",
) -> Dict[str, Any]:
    """
    Build a single 3D-ready package for one selected state.
    """
    state = _resolve_selected_state(record, step_index=step_index, conformer_id=conformer_id)
    smiles = _get_state_smiles(record, state)

    selected_step = state.get("step") or {}
    selected_frame = state.get("frame") or {}
    selected_conformer = state.get("conformer") or {}

    seed = _seed_from_text(
        record.get("compound_id", "UNKNOWN"),
        selected_frame.get("frame_id", ""),
        selected_conformer.get("conformer_id", ""),
        smiles,
    )

    mol = _build_3d_molecule(
        smiles=smiles,
        seed=seed,
        add_hs=True,
        embed_method="ETKDGv3",
        optimize_method="MMFF94",
    )

    molblock = Chem.MolToMolBlock(mol)
    highlight_atoms = _collect_highlight_atoms(state)
    highlight_bonds = _collect_highlight_bonds(state)

    package = {
        "compound_id": record.get("compound_id"),
        "compound_name": record.get("compound_name"),
        "step_label": selected_step.get("step_label", selected_frame.get("step_label")),
        "stage": selected_step.get("stage", selected_frame.get("stage")),
        "frame_id": selected_frame.get("frame_id"),
        "conformer_id": selected_conformer.get("conformer_id", selected_frame.get("conformer_id")),
        "smiles": smiles,
        "molblock": molblock,
        "energy_kj_mol": selected_frame.get(
            "energy_kj_mol",
            selected_step.get("relative_energy_kj_mol", record.get("activation_energy_kj_mol", 0.0)),
        ),
        "energy_kcal_mol": selected_frame.get("energy_kcal_mol"),
        "is_transition_state": bool(
            selected_frame.get("is_transition_state", selected_step.get("transition_state", False))
        ),
        "playback_note": selected_frame.get("playback_note", selected_step.get("description", "")),
        "highlight_atoms": highlight_atoms,
        "highlight_bonds": [list(pair) for pair in highlight_bonds],
        "atom_overlays": _build_atom_overlay_data(mol, highlight_atoms),
        "bond_overlays": _build_bond_overlay_data(mol, highlight_bonds),
        "style": style,
        "viewer_ready": True,
    }

    return package


def build_trajectory_playback_package(
    record: Dict[str, Any],
    style: str = "ball-and-stick",
) -> List[Dict[str, Any]]:
    """
    Build all frame packages for playback.
    """
    frames = sorted(
        record.get("trajectory_frames", []),
        key=lambda x: _safe_int(x.get("step_index"), 0),
    )

    playback = []
    if not frames:
        playback.append(build_3d_state_package(record, step_index=0, style=style))
        return playback

    for frame in frames:
        step_index = _safe_int(frame.get("step_index"), 0)
        package = build_3d_state_package(record, step_index=step_index, style=style)
        playback.append(package)

    return playback


def generate_3d_viewer_html(
    record: Dict[str, Any],
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
    style: str = "ball-and-stick",
    width: int = 100,
    height: int = 480,
    background_color: str = "white",
    show_labels: bool = True,
) -> str:
    """
    Generate a single-state HTML 3D viewer block for embedding in Streamlit.
    """
    if py3Dmol is None:
        raise ImportError("py3Dmol is required for 3D viewer rendering.")

    pkg = build_3d_state_package(
        record=record,
        step_index=step_index,
        conformer_id=conformer_id,
        style=style,
    )

    frame_json = json.dumps(pkg)

    html = f"""
    <div style="width:100%; max-width:100%;">
      <div id="viewer3d-single" style="width:100%; height:{height}px; position:relative; border:1px solid #dbe7ff; border-radius:14px; background:{background_color}; overflow:hidden; box-sizing:border-box;"></div>

      <div style="margin-top:10px; padding:12px 14px; border:1px solid #dbe7ff; border-radius:12px; background:#f8fbff; font-family:Arial, sans-serif; font-size:13px; color:#334155;">
        <strong>3D State:</strong> <span id="single-step-label"></span><br>
        <strong>Stage:</strong> <span id="single-stage"></span><br>
        <strong>Energy:</strong> <span id="single-energy"></span><br>
        <strong>Note:</strong> <span id="single-note"></span>
      </div>
    </div>

    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <script>
      (function() {{
        const frame = {frame_json};
        const viewerElement = document.getElementById("viewer3d-single");
        const viewer = $3Dmol.createViewer(viewerElement, {{ backgroundColor: "{background_color}" }});

        function applyBaseStyle() {{
          const style = frame.style || "{style}";
          if (style === "stick") {{
            viewer.setStyle({{}}, {{ stick: {{}} }});
          }} else if (style === "sphere") {{
            viewer.setStyle({{}}, {{ sphere: {{ scale: 0.32 }} }});
          }} else {{
            viewer.setStyle({{}}, {{ stick: {{}}, sphere: {{ scale: 0.28 }} }});
          }}
        }}

        function addOverlays() {{
          (frame.atom_overlays || []).forEach(atom => {{
            viewer.addSphere({{
              center: {{x: atom.x, y: atom.y, z: atom.z}},
              radius: atom.radius || 0.35,
              color: atom.color || "red",
              alpha: 0.85
            }});

            if ({str(show_labels).lower()}) {{
              viewer.addLabel(atom.label, {{
                position: {{x: atom.x, y: atom.y, z: atom.z}},
                backgroundColor: "rgba(255,255,255,0.75)",
                fontColor: "#111827",
                fontSize: 12,
                borderThickness: 0,
                inFront: true
              }});
            }}
          }});

          (frame.bond_overlays || []).forEach(bond => {{
            viewer.addCylinder({{
              start: bond.start,
              end: bond.end,
              radius: bond.radius || 0.12,
              color: bond.color || "#2563eb",
              fromCap: 1,
              toCap: 1
            }});
          }});
        }}
         
        viewer.addModel(frame.molblock, "mol");
        applyBaseStyle();
        addOverlays();

        viewer.zoomTo();
        viewer.center();
        viewer.render();
        viewer.resize();

        setTimeout(function () {{
         viewer.zoomTo();
         viewer.center();
         viewer.render();
         viewer.resize();
        }}, 120);
        
        document.getElementById("single-step-label").textContent = frame.step_label || "N/A";
        document.getElementById("single-stage").textContent = frame.stage || "N/A";
        document.getElementById("single-energy").textContent = `${{frame.energy_kj_mol ?? "N/A"}} kJ/mol`;
        document.getElementById("single-note").textContent = frame.playback_note || "No playback note available.";
      }})();
    </script>
    """
    return html


def generate_playback_html(
    record: Dict[str, Any],
    style: str = "ball-and-stick",
    width: int = 100,
    height: int = 520,
    background_color: str = "white",
    start_step_index: int = 0,
    autoplay: bool = False,
    playback_speed_ms: int = 900,
    show_labels: bool = True,
) -> str:
    """
    Generate a multi-frame HTML viewer with playback controls:
    - previous
    - next
    - play / pause
    - slider
    - state metadata
    """
    if py3Dmol is None:
        raise ImportError("py3Dmol is required for playback rendering.")

    frames = build_trajectory_playback_package(record=record, style=style)
    if not frames:
        raise ValueError("No trajectory frames available for playback.")

    max_index = len(frames) - 1
    if start_step_index < 0 or start_step_index > max_index:
        start_step_index = 0

    frames_json = json.dumps(frames)

     
    html = f"""
    <div style="width:100%; max-width:100%; font-family:Arial, sans-serif; box-sizing:border-box;">
      <div id="viewer3d-playback" style="width:100%; height:{height}px; position:relative; border:1px solid #dbe7ff; border-radius:16px; background:{background_color}; overflow:hidden; box-sizing:border-box;"></div>

    
      <div style="margin-top:12px; display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <button onclick="prevFrame3D()" style="padding:8px 12px; border-radius:10px; border:1px solid #cbd5e1; background:white; cursor:pointer;">◀ Prev</button>
        <button onclick="togglePlayback3D()" id="playPauseBtn3D" style="padding:8px 12px; border-radius:10px; border:1px solid #cbd5e1; background:white; cursor:pointer;">{"Pause" if autoplay else "Play"}</button>
        <button onclick="nextFrame3D()" style="padding:8px 12px; border-radius:10px; border:1px solid #cbd5e1; background:white; cursor:pointer;">Next ▶</button>

        <input type="range" id="frameSlider3D" min="0" max="{max_index}" value="{start_step_index}" step="1" style="width:260px;" oninput="setFrame3D(parseInt(this.value))">

        <span style="font-weight:600; color:#1e3a8a;">Frame:</span>
        <span id="frameIndex3D" style="color:#334155;">{start_step_index + 1} / {len(frames)}</span>
      </div>

      <div style="margin-top:12px; padding:14px 16px; border:1px solid #dbe7ff; border-radius:14px; background:#f8fbff; color:#334155; font-size:13px; line-height:1.6;">
        <div><strong>Step:</strong> <span id="frameStepLabel3D"></span></div>
        <div><strong>Stage:</strong> <span id="frameStage3D"></span></div>
        <div><strong>Energy:</strong> <span id="frameEnergy3D"></span></div>
        <div><strong>Transition State:</strong> <span id="frameTS3D"></span></div>
        <div><strong>Note:</strong> <span id="frameNote3D"></span></div>
      </div>
    </div>

    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <script>
      (function() {{
        const frames = {frames_json};
        let currentFrameIndex = {start_step_index};
        let isPlaying = {str(autoplay).lower()};
        let playbackTimer = null;

        const viewerElement = document.getElementById("viewer3d-playback");
        const viewer = $3Dmol.createViewer(viewerElement, {{ backgroundColor: "{background_color}" }});

        function applyBaseStyle(frame) {{
          const style = frame.style || "{style}";
          if (style === "stick") {{
            viewer.setStyle({{}}, {{ stick: {{}} }});
          }} else if (style === "sphere") {{
            viewer.setStyle({{}}, {{ sphere: {{ scale: 0.32 }} }});
          }} else {{
            viewer.setStyle({{}}, {{ stick: {{}}, sphere: {{ scale: 0.28 }} }});
          }}
        }}

        function addOverlays(frame) {{
          (frame.atom_overlays || []).forEach(atom => {{
            viewer.addSphere({{
              center: {{x: atom.x, y: atom.y, z: atom.z}},
              radius: atom.radius || 0.35,
              color: atom.color || "red",
              alpha: 0.85
            }});

            if ({str(show_labels).lower()}) {{
              viewer.addLabel(atom.label, {{
                position: {{x: atom.x, y: atom.y, z: atom.z}},
                backgroundColor: "rgba(255,255,255,0.75)",
                fontColor: "#111827",
                fontSize: 12,
                borderThickness: 0,
                inFront: true
              }});
            }}
          }});

          (frame.bond_overlays || []).forEach(bond => {{
            viewer.addCylinder({{
              start: bond.start,
              end: bond.end,
              radius: bond.radius || 0.12,
              color: bond.color || "#2563eb",
              fromCap: 1,
              toCap: 1
            }});
          }});
        }}

        function renderFrame(index) {{
          const frame = frames[index];
          viewer.clear();
          viewer.addModel(frame.molblock, "mol");
          applyBaseStyle(frame);
          addOverlays(frame);

          viewer.zoomTo();
          viewer.center();
          viewer.render();
          viewer.resize();

          setTimeout(function () {{
            viewer.zoomTo();
            viewer.center();
            viewer.render();
            viewer.resize();
          }}, 120);
                                                                                   
          document.getElementById("frameSlider3D").value = index;
          document.getElementById("frameIndex3D").textContent = `${{index + 1}} / ${{frames.length}}`;
          document.getElementById("frameStepLabel3D").textContent = frame.step_label || "N/A";
          document.getElementById("frameStage3D").textContent = frame.stage || "N/A";
          document.getElementById("frameEnergy3D").textContent = `${{frame.energy_kj_mol ?? "N/A"}} kJ/mol`;
          document.getElementById("frameTS3D").textContent = frame.is_transition_state ? "Yes" : "No";
          document.getElementById("frameNote3D").textContent = frame.playback_note || "No playback note available.";
        }}

        function stopPlayback() {{
          if (playbackTimer) {{
            clearInterval(playbackTimer);
            playbackTimer = null;
          }}
          isPlaying = false;
          document.getElementById("playPauseBtn3D").textContent = "Play";
        }}

        function startPlayback() {{
          stopPlayback();
          isPlaying = true;
          document.getElementById("playPauseBtn3D").textContent = "Pause";
          playbackTimer = setInterval(() => {{
            currentFrameIndex = (currentFrameIndex + 1) % frames.length;
            renderFrame(currentFrameIndex);
          }}, {playback_speed_ms});
        }}

        window.setFrame3D = function(index) {{
          currentFrameIndex = index;
          renderFrame(currentFrameIndex);
        }}

        window.nextFrame3D = function() {{
          currentFrameIndex = (currentFrameIndex + 1) % frames.length;
          renderFrame(currentFrameIndex);
        }}

        window.prevFrame3D = function() {{
          currentFrameIndex = (currentFrameIndex - 1 + frames.length) % frames.length;
          renderFrame(currentFrameIndex);
        }}

        window.togglePlayback3D = function() {{
          if (isPlaying) {{
            stopPlayback();
          }} else {{
            startPlayback();
          }}
        }}

        renderFrame(currentFrameIndex);
        if (isPlaying) {{
          startPlayback();
        }}
      }})();
    </script>
    """
    return html


def export_state_molblock(
    record: Dict[str, Any],
    output_file: str,
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
) -> str:
    pkg = build_3d_state_package(record, step_index=step_index, conformer_id=conformer_id)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(pkg["molblock"], encoding="utf-8")
    return str(output_path.resolve())


def export_playback_bundle_json(
    record: Dict[str, Any],
    output_file: str,
    style: str = "ball-and-stick",
) -> str:
    playback = build_trajectory_playback_package(record, style=style)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(playback, indent=2), encoding="utf-8")
    return str(output_path.resolve())


def get_3d_state_summary(
    record: Dict[str, Any],
    step_index: Optional[int] = None,
    conformer_id: Optional[str] = None,
) -> Dict[str, Any]:
    pkg = build_3d_state_package(record, step_index=step_index, conformer_id=conformer_id)
    return {
        "compound_id": pkg.get("compound_id"),
        "compound_name": pkg.get("compound_name"),
        "step_label": pkg.get("step_label"),
        "stage": pkg.get("stage"),
        "frame_id": pkg.get("frame_id"),
        "conformer_id": pkg.get("conformer_id"),
        "energy_kj_mol": pkg.get("energy_kj_mol"),
        "is_transition_state": pkg.get("is_transition_state"),
        "playback_note": pkg.get("playback_note"),
        "highlight_atom_count": len(pkg.get("highlight_atoms", [])),
        "highlight_bond_count": len(pkg.get("highlight_bonds", [])),
    }
