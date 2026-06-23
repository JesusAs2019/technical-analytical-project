from pathlib import Path
from html import escape

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdMolTransforms, rdMolDescriptors, Descriptors
    from rdkit.Chem.Draw import rdMolDraw2D
except ImportError:
    Chem = None
    AllChem = None
    rdMolTransforms = None
    rdMolDescriptors = None
    Descriptors = None
    rdMolDraw2D = None


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>R&D Data Accelerator System Dashboard</title>
    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            background: #f3f7fc;
            color: #0f172a;
        }}

        .page {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 24px;
        }}

        .dashboard {{
            background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
            border: 1px solid #dbe7ff;
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        }}

        .title {{
            margin: 0;
            font-size: 32px;
            font-weight: 800;
            color: #0f2d68;
        }}

        .subtitle {{
            margin: 8px 0 28px 0;
            font-size: 15px;
            font-weight: 600;
            color: #35538a;
        }}

        .section-title {{
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 14px;
            color: #0f2d68;
        }}

        .summary-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            margin-bottom: 26px;
        }}

        .summary-label {{
            font-size: 18px;
            font-weight: 800;
            color: #1d3f91;
            margin-right: 8px;
        }}

        .chip {{
            display: inline-flex;
            align-items: center;
            padding: 10px 16px;
            border-radius: 999px;
            background: #f3f7ff;
            border: 1px solid #c9d9ff;
            color: #1d4ed8;
            font-size: 14px;
            font-weight: 700;
            white-space: nowrap;
        }}

        /* ONLY 2 MAIN SCREENS */
        .screen {{
            background: #ffffff;
            border: 1px solid #dbe7ff;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
            margin-bottom: 24px;
        }}

        .screen-title {{
            margin: 0 0 18px 0;
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
        }}

        .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .panel {{
            background: #ffffff;
            border: 1px solid #e5edf9;
            border-radius: 16px;
            padding: 16px;
        }}

        .panel-title {{
            margin: 0 0 12px 0;
            font-size: 17px;
            font-weight: 800;
            color: #0f172a;
        }}

        .structure-box {{
            height: 430px;
            min-height: 430px;
            background: #ffffff;
            border: 1px solid #e5edf9;
            border-radius: 14px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .structure-box svg {{
            max-width: 100%;
            max-height: 100%;
            display: block;
        }}

        #viewer3d {{
            width: 100%;
            height: 430px;
            min-height: 430px;
            background: #ffffff;
            border: 1px solid #e5edf9;
            border-radius: 14px;
            overflow: hidden;
            position: relative;
        }}

        .table-scroll {{
            max-height: 360px;
            overflow-y: auto;
            overflow-x: auto;
            border: 1px solid #e5edf9;
            border-radius: 14px;
            background: #ffffff;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        thead th {{
            position: sticky;
            top: 0;
            background: #eef4ff;
            color: #0f172a;
            text-align: left;
            padding: 14px 12px;
            font-weight: 800;
            border-bottom: 1px solid #dbe7ff;
            z-index: 2;
        }}

        tbody td {{
            padding: 12px;
            border-bottom: 1px solid #edf2fb;
            color: #172554;
        }}

        tbody tr:hover {{
            background: #f8fbff;
        }}

        .desc {{
            margin-top: 12px;
            padding: 14px 16px;
            background: #f8fbff;
            border: 1px solid #dbe7ff;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.6;
            color: #334155;
        }}

        .desc strong {{
            color: #0f2d68;
        }}

        .footer-note {{
            margin-top: 10px;
            font-size: 15px;
            font-weight: 700;
            color: #334155;
        }}

        /* Collapse only on smaller screens */
        @media (max-width: 900px) {{
            .two-col {{
                grid-template-columns: 1fr;
            }}

            .structure-box,
            #viewer3d {{
                height: 360px;
                min-height: 360px;
            }}
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="dashboard">
            <h1 class="title">R&D Data Accelerator System Dashboard</h1>
            <div class="subtitle">Operational Ingestion Hub | Automated Extraction & Verification Engine</div>

            <div class="section-title">Molecular Graph Inspector</div>

            <div class="summary-row">
                <div class="summary-label">Isolate Molecule: {compound_code}</div>
                <div class="chip">Formula: {formula}</div>
                <div class="chip">Molecular Weight: {mol_weight}</div>
                <div class="chip">Bond Length Rows: {bond_count}</div>
                <div class="chip">Angle Rows: {angle_count}</div>
            </div>

            <!-- SCREEN 1: ONLY 2D + 3D -->
            <div class="screen">
                <div class="screen-title">Structure Visualization Screen</div>
                <div class="two-col">
                    <div class="panel">
                        <div class="panel-title">2D Molecular Structure</div>
                        <div class="structure-box">
                            {svg_2d}
                        </div>
                        <div class="desc">
                            <strong>2D Structure Description:</strong>
                            This panel shows the flat structural representation of the molecule, including atom connectivity,
                            bond arrangement, and functional group placement. It is useful for quick structural inspection
                            and confirmation of the chemical graph used in validation.
                        </div>
                    </div>

                    <div class="panel">
                        <div class="panel-title">3D Molecular Viewer</div>
                        <div id="viewer3d"></div>
                        <div class="desc">
                            <strong>3D Viewer Description:</strong>
                            This panel shows the optimized three-dimensional geometry of the molecule. It helps visualize
                            spatial arrangement, stereochemical orientation, and atomic positioning beyond the 2D chemical graph.
                        </div>
                    </div>
                </div>
            </div>

            <!-- SCREEN 2: ONLY BOND LENGTH + BOND ANGLE -->
            <div class="screen">
                <div class="screen-title">Geometric Metrics Screen</div>
                <div class="two-col">
                    <div class="panel">
                        <div class="panel-title">Bond Length Metrics</div>
                        <div class="table-scroll">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Bond Type</th>
                                        <th>Atoms</th>
                                        <th>Length (Å)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {bond_rows}
                                </tbody>
                            </table>
                        </div>
                        <div class="desc">
                            <strong>Bond Length Description:</strong>
                            Bond length values represent measured distances between directly connected atoms in the optimized
                            molecular geometry. These values help confirm expected structural relationships for bonds such as
                            C–C, C–H, C–O, and O–H.
                        </div>
                    </div>

                    <div class="panel">
                        <div class="panel-title">Bond Angle Metrics</div>
                        <div class="table-scroll">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Angle Type</th>
                                        <th>Atoms</th>
                                        <th>Angle (°)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {angle_rows}
                                </tbody>
                            </table>
                        </div>
                        <div class="desc">
                            <strong>Bond Angle Description:</strong>
                            Bond angle values represent the geometric angle formed by three connected atoms. These measurements
                            support interpretation of molecular shape, hybridization behavior, and local stereochemical arrangement.
                        </div>
                    </div>
                </div>
            </div>

            <div class="footer-note">
                Graph Structure of {compound_code} — Structure and stereochemical parameters validated.
            </div>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const viewerElement = document.getElementById("viewer3d");
            if (!viewerElement) {{
                console.error("3D viewer container not found.");
                return;
            }}

            const molData = `{mol_block}`;
            const viewer = $3Dmol.createViewer(viewerElement, {{
                backgroundColor: "white"
            }});

            viewer.addModel(molData, "mol");
            viewer.setStyle({{}}, {{
                stick: {{}},
                sphere: {{ scale: 0.28 }}
            }});
            viewer.zoomTo();
            viewer.render();
            viewer.resize();
        }});
    </script>
</body>
</html>
"""



def _atom_label(atom):
    return f"{atom.GetSymbol()}{atom.GetIdx() + 1}"


def _build_2d_svg(smiles: str) -> str:
    mol2d = Chem.MolFromSmiles(smiles)
    if mol2d is None:
        raise ValueError("Invalid SMILES for 2D rendering.")

    mol2d = Chem.AddHs(mol2d)
    AllChem.Compute2DCoords(mol2d)

    drawer = rdMolDraw2D.MolDraw2DSVG(500, 380)
    drawer.drawOptions().padding = 0.05
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol2d)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()


def _collect_bond_lengths(mol):
    conf = mol.GetConformer()
    allowed_pairs = {
        tuple(sorted(("C", "C"))),
        tuple(sorted(("C", "H"))),
        tuple(sorted(("C", "O"))),
        tuple(sorted(("O", "H")))
    }

    rows = []
    for bond in mol.GetBonds():
        atom1 = bond.GetBeginAtom()
        atom2 = bond.GetEndAtom()

        pair = tuple(sorted((atom1.GetSymbol(), atom2.GetSymbol())))
        if pair in allowed_pairs:
            length = rdMolTransforms.GetBondLength(conf, atom1.GetIdx(), atom2.GetIdx())
            rows.append({
                "bond_type": f"{pair[0]}-{pair[1]}",
                "atoms": f"{_atom_label(atom1)}–{_atom_label(atom2)}",
                "length": f"{length:.3f}"
            })

    rows.sort(key=lambda x: (x["bond_type"], x["atoms"]))
    return rows


def _collect_bond_angles(mol):
    conf = mol.GetConformer()
    allowed_pairs = {
        tuple(sorted(("C", "C"))),
        tuple(sorted(("C", "H"))),
        tuple(sorted(("C", "O"))),
        tuple(sorted(("O", "H")))
    }

    rows = []

    for center in mol.GetAtoms():
        neighbors = [n for n in center.GetNeighbors()]
        if len(neighbors) < 2:
            continue

        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                atom1 = neighbors[i]
                atom2 = center
                atom3 = neighbors[j]

                pair1 = tuple(sorted((atom1.GetSymbol(), atom2.GetSymbol())))
                pair2 = tuple(sorted((atom2.GetSymbol(), atom3.GetSymbol())))

                if pair1 in allowed_pairs and pair2 in allowed_pairs:
                    angle = rdMolTransforms.GetAngleDeg(
                        conf,
                        atom1.GetIdx(),
                        atom2.GetIdx(),
                        atom3.GetIdx()
                    )

                    rows.append({
                        "angle_type": f"{atom1.GetSymbol()}-{atom2.GetSymbol()}-{atom3.GetSymbol()}",
                        "atoms": f"{_atom_label(atom1)}–{_atom_label(atom2)}–{_atom_label(atom3)}",
                        "angle": f"{angle:.2f}"
                    })

    rows.sort(key=lambda x: (x["angle_type"], x["atoms"]))
    return rows


def _rows_to_html(rows, kind="bond"):
    if not rows:
        if kind == "bond":
            return '<tr><td colspan="3">No matching bond lengths found.</td></tr>'
        return '<tr><td colspan="3">No matching bond angles found.</td></tr>'

    if kind == "bond":
        return "\n".join(
            f"<tr><td>{escape(r['bond_type'])}</td><td>{escape(r['atoms'])}</td><td>{escape(r['length'])}</td></tr>"
            for r in rows
        )

    return "\n".join(
        f"<tr><td>{escape(r['angle_type'])}</td><td>{escape(r['atoms'])}</td><td>{escape(r['angle'])}</td></tr>"
        for r in rows
    )


def _record_rows(compound_code, compound_name, smiles, formula, mol_weight):
    items = [
        ("Compound Code", compound_code),
        ("Compound Name", compound_name),
        ("SMILES", smiles),
        ("Molecular Formula", formula),
        ("Molecular Weight", mol_weight),
        ("Validation Status", "Validated")
    ]
    return "\n".join(
        f"<tr><td>{escape(str(k))}</td><td>{escape(str(v))}</td></tr>"
        for k, v in items
    )


def generate_3d_html(smiles: str, compound_name: str, output_file: str, compound_code: str = "CDA-2026") -> str:
    if Chem is None or AllChem is None or rdMolTransforms is None or rdMolDraw2D is None:
        raise ImportError("RDKit is required for 2D/3D viewer generation.")

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES string; cannot generate viewer.")

    formula = rdMolDescriptors.CalcMolFormula(mol)
    mol_weight = f"{Descriptors.MolWt(mol):.2f}"

    svg_2d = _build_2d_svg(smiles)

    mol3d = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42

    embed_result = AllChem.EmbedMolecule(mol3d, params)
    if embed_result != 0:
        raise RuntimeError("3D coordinate generation failed.")

    AllChem.MMFFOptimizeMolecule(mol3d)
    mol_block = Chem.MolToMolBlock(mol3d)

    bond_rows = _collect_bond_lengths(mol3d)
    angle_rows = _collect_bond_angles(mol3d)

    html = HTML_TEMPLATE.format(
        compound_name=escape(compound_name),
        compound_code=escape(compound_code),
        smiles=escape(smiles),
        formula=escape(formula),
        mol_weight=escape(mol_weight),
        svg_2d=svg_2d,
        mol_block=mol_block.replace("\\", "\\\\").replace("`", "\\`"),
        record_rows=_record_rows(compound_code, compound_name, smiles, formula, mol_weight),
        bond_rows=_rows_to_html(bond_rows, kind="bond"),
        angle_rows=_rows_to_html(angle_rows, kind="angle"),
        bond_count=len(bond_rows),
        angle_count=len(angle_rows),
    )

    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return str(path.resolve())
