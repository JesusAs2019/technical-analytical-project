"""
ChemData Control Center — Nanomaterials Analytics Dashboard Component
Interactive DLS Size Distribution curve generator, Zeta Potential gauge, and batch inspection UI.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from nano_validation import NanoparticleBatchSchema, NanoparticleType, MorphologyShape

# High-Value Industry Seed Data (Lipid Nanoparticles, Gold, Quantum Dots, SPIONs)
SAMPLE_NANO_BATCHES = [
    {
        "batch_id": "NP-2026-LNP04",
        "sample_name": "mRNA Lipid Nanoparticle (LNP-mRNA-04)",
        "nanoparticle_type": NanoparticleType.LIPID_NANOPARTICLE.value,
        "morphology": MorphologyShape.CORE_SHELL.value,
        "core_composition": "mRNA / Ionizable Lipid Core",
        "shell_composition": "PEG-2000 / Cholesterol Shell",
        "hydrodynamic_diameter_nm": 88.0,
        "polydispersity_index": 0.085,
        "tem_core_diameter_nm": 75.0,
        "zeta_potential_mv": -4.2,
        "suspension_ph": 7.2,
        "ionic_strength_mm": 150.0,
        "target_application": "Targeted RNA Vaccine & Gene Therapy"
    },
    {
        "batch_id": "NP-2026-AU01",
        "sample_name": "Gold Nanospheres (Citrate-capped)",
        "nanoparticle_type": NanoparticleType.METALLIC.value,
        "morphology": MorphologyShape.SPHERICAL.value,
        "core_composition": "Au (Gold)",
        "shell_composition": "Trisodium Citrate Ligand",
        "hydrodynamic_diameter_nm": 32.5,
        "polydispersity_index": 0.120,
        "tem_core_diameter_nm": 28.0,
        "zeta_potential_mv": -38.4,
        "suspension_ph": 7.4,
        "ionic_strength_mm": 10.0,
        "target_application": "Surface-Enhanced Raman Scattering (SERS) & Biosensing"
    },
    {
        "batch_id": "NP-2026-FEOX",
        "sample_name": "Superparamagnetic Iron Oxide (SPIONs)",
        "nanoparticle_type": NanoparticleType.OXIDE.value,
        "morphology": MorphologyShape.CORE_SHELL.value,
        "core_composition": "Fe3O4 (Magnetite)",
        "shell_composition": "Dextran Biocompatible Polymer",
        "hydrodynamic_diameter_nm": 115.0,
        "polydispersity_index": 0.185,
        "tem_core_diameter_nm": 14.0,
        "zeta_potential_mv": +32.1,
        "suspension_ph": 6.8,
        "ionic_strength_mm": 50.0,
        "target_application": "T2 MRI Contrast Agent & Magnetic Hyperthermia"
    },
    {
        "batch_id": "NP-2026-QDOT",
        "sample_name": "Core-Shell Quantum Dots (InP/ZnS)",
        "nanoparticle_type": NanoparticleType.SEMICONDUCTOR_QD.value,
        "morphology": MorphologyShape.CORE_SHELL.value,
        "core_composition": "InP (Indium Phosphide)",
        "shell_composition": "ZnS Epitaxial Shell",
        "hydrodynamic_diameter_nm": 6.8,
        "polydispersity_index": 0.095,
        "tem_core_diameter_nm": 4.5,
        "zeta_potential_mv": -24.5,
        "suspension_ph": 7.0,
        "ionic_strength_mm": 20.0,
        "target_application": "Heavy-Metal-Free Bio-imaging & Solar Concentrators"
    }
]


def generate_dls_curve(mean_diameter: float, pdi: float):
    """Generates a physical Dynamic Light Scattering (DLS) Log-Normal Intensity distribution curve."""
    sigma = np.sqrt(np.log(1.0 + max(0.01, pdi)))
    mu = np.log(mean_diameter) - (sigma**2 / 2.0)
    
    diameters = np.logspace(np.log10(max(1.0, mean_diameter * 0.1)), np.log10(mean_diameter * 5.0), 300)
    intensity = (1.0 / (diameters * sigma * np.sqrt(2.0 * np.pi))) * np.exp(-((np.log(diameters) - mu)**2) / (2.0 * sigma**2))
    intensity_pct = (intensity / np.max(intensity)) * 100.0
    
    return diameters, intensity_pct


def render_nano_analytics_tab():
    st.header("🔬 Nanoparticles & Advanced Materials Analytics")
    st.caption("Standardized DLS hydrodynamic size distribution, polydispersity profiling, and DLVO colloidal stability evaluation.")

    # Top Selector & Interactive Batch Selection
    col_sel, col_stat = st.columns([2, 1])
    with col_sel:
        batch_options = [f"{b['batch_id']} — {b['sample_name']}" for b in SAMPLE_NANO_BATCHES]
        selected_idx = st.selectbox("Select Characterization Batch:", range(len(batch_options)), format_func=lambda x: batch_options[x])
        raw_batch = SAMPLE_NANO_BATCHES[selected_idx]
        batch = NanoparticleBatchSchema(**raw_batch)
        stability = batch.stability_evaluation

    with col_stat:
        st.markdown(f"**Classification:** `{batch.nanoparticle_type.value}`")
        st.markdown(f"**Morphology:** `{batch.morphology.value}`")

    st.markdown("---")

    # Metrics Summary Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Hydrodynamic Size (dH)", f"{batch.hydrodynamic_diameter_nm} nm", help="Intensity-weighted hydrodynamic diameter")
    m2.metric("Polydispersity Index (PDI)", f"{batch.polydispersity_index:.3f}", delta="Monodisperse" if stability["is_monodisperse"] else "Polydisperse")
    m3.metric("Zeta Potential (ζ)", f"{batch.zeta_potential_mv:+.1f} mV", help="Electrokinetic surface charge")
    m4.metric("Suspension pH", f"pH {batch.suspension_ph:.1f}")

    # Two Column Layout: DLS Curve & Stability Logic
    t1, t2 = st.columns([1.25, 0.75])
    
    with t1:
        st.subheader("Dynamic Light Scattering (DLS) Size Distribution")
        d, intensity = generate_dls_curve(batch.hydrodynamic_diameter_nm, batch.polydispersity_index)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=d, 
            y=intensity, 
            mode='lines', 
            fill='tozeroy', 
            name='DLS Intensity Distribution',
            line=dict(color='#047857', width=2.5),
            fillcolor='rgba(4, 120, 87, 0.15)'
        ))
        fig.add_vline(
            x=batch.hydrodynamic_diameter_nm, 
            line_dash="dash", 
            line_color="#b45309", 
            annotation_text=f"Peak: {batch.hydrodynamic_diameter_nm} nm",
            annotation_position="top right"
        )
        fig.update_layout(
            xaxis_type="log",
            xaxis_title="Hydrodynamic Diameter (nm)",
            yaxis_title="Relative Intensity (%)",
            margin=dict(l=20, r=20, t=30, b=20),
            height=340,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.subheader("Colloidal Stability Profile")
        
        if stability["status_color"] == "green":
            st.success(f"**{stability['rating']}**\n\n{stability['explanation']}")
        elif stability["status_color"] == "blue":
            st.info(f"**{stability['rating']}**\n\n{stability['explanation']}")
        elif stability["status_color"] == "amber":
            st.warning(f"**{stability['rating']}**\n\n{stability['explanation']}")
        else:
            st.error(f"**{stability['rating']}**\n\n{stability['explanation']}")
            
        st.markdown(f"""
        **Formulation Specifications:**
        * **Core Material:** `{batch.core_composition}`
        * **Surface Ligand:** `{batch.shell_composition}`
        * **TEM Core Size:** `{batch.tem_core_diameter_nm} nm`
        * **Ionic Strength:** `{batch.ionic_strength_mm} mM`
        * **Target Application:** *{batch.target_application}*
        """)

    # Batch Comparison Table
    st.subheader("Nanomaterial Formulation Vault")
    df = pd.DataFrame(SAMPLE_NANO_BATCHES)
    st.dataframe(
        df[['batch_id', 'sample_name', 'nanoparticle_type', 'hydrodynamic_diameter_nm', 'polydispersity_index', 'zeta_potential_mv', 'shell_composition']], 
        use_container_width=True
    )
