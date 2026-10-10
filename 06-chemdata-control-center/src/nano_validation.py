"""
ChemData Scientific Services — Nanomaterial Validation Engine
Deterministic schema validation for nanoparticle characterization, DLS distributions, and colloidal stability.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class NanoparticleType(str, Enum):
    METALLIC = "Metallic (Au, Ag, Pt)"
    LIPID_NANOPARTICLE = "Lipid Nanoparticle (LNP)"
    SEMICONDUCTOR_QD = "Quantum Dot (CdSe, InP)"
    POLYMER_MICELLE = "Polymeric Micelle / Dendrimer"
    CARBON_NANO = "Carbon Nanotube / Graphene"
    OXIDE = "Metal Oxide (Fe3O4, TiO2, SiO2)"


class MorphologyShape(str, Enum):
    SPHERICAL = "Spherical"
    ROD_CYLINDER = "Nanorod / Cylindrical"
    CORE_SHELL = "Core-Shell"
    CUBIC = "Nanocube"
    POROUS_CAGE = "Mesoporous / Nanocage"


class StabilityRating(str, Enum):
    HIGHLY_STABLE = "Highly Stable (No aggregation risk)"
    MODERATELY_STABLE = "Moderately Stable"
    INCIPIENT_INSTABILITY = "Incipient Instability (Aggregation risk)"
    COAGULATION_RAPID = "Unstable / Rapid Precipitation"


class NanoparticleBatchSchema(BaseModel):
    """Schema for nanoparticle batch characterization & quality assurance."""
    
    batch_id: str = Field(..., description="Unique batch identifier, e.g. NP-2026-AU01")
    sample_name: str = Field(..., description="Descriptive sample label")
    nanoparticle_type: NanoparticleType
    morphology: MorphologyShape
    
    # Core-Shell Chemistry
    core_composition: str = Field(..., description="Core chemical formula, e.g. Fe3O4, Au, SiO2")
    shell_composition: Optional[str] = Field(None, description="Shell coating / polymer ligand, e.g. PEG-2000, Citrate")
    
    # Dynamic Light Scattering (DLS) & Size Measurements (in nm)
    hydrodynamic_diameter_nm: float = Field(..., ge=1.0, le=2000.0, description="DLS Hydrodynamic Diameter in nm [1.0 - 2000.0]")
    polydispersity_index: float = Field(..., ge=0.01, le=1.0, description="Polydispersity Index (PDI) [0.01 - 1.0]")
    tem_core_diameter_nm: Optional[float] = Field(None, ge=0.5, le=1000.0, description="TEM Core diameter in nm")
    
    # Electrokinetic & Colloidal Properties
    zeta_potential_mv: float = Field(..., ge=-120.0, le=120.0, description="Zeta Potential in mV [-120.0 to +120.0]")
    suspension_ph: float = Field(7.0, ge=1.0, le=14.0, description="Measurement pH")
    ionic_strength_mm: float = Field(10.0, ge=0.0, le=1000.0, description="Solvent ionic strength in mM")
    
    target_application: str = Field("Targeted Drug Delivery / Catalysis / Battery Materials")

    @field_validator("polydispersity_index")
    @classmethod
    def validate_pdi_quality(cls, v: float) -> float:
        return round(v, 3)

    @property
    def stability_evaluation(self) -> Dict[str, Any]:
        """Calculates colloidal stability classification based on DLVO electrokinetic theory."""
        abs_zeta = abs(self.zeta_potential_mv)
        if abs_zeta >= 30.0:
            rating = StabilityRating.HIGHLY_STABLE
            color = "green"
            explanation = "Strong electrostatic repulsion prevents particle coalescence."
        elif abs_zeta >= 20.0:
            rating = StabilityRating.MODERATELY_STABLE
            color = "blue"
            explanation = "Moderate stability; steric stabilization may be beneficial."
        elif abs_zeta >= 10.0:
            rating = StabilityRating.INCIPIENT_INSTABILITY
            color = "amber"
            explanation = "Incipient instability; high risk of flocculation over time."
        else:
            rating = StabilityRating.COAGULATION_RAPID
            color = "red"
            explanation = "Critical aggregation threshold (< 10 mV); van der Waals forces dominate."
            
        is_monodisperse = self.polydispersity_index <= 0.2
        
        return {
            "rating": rating.value,
            "status_color": color,
            "is_monodisperse": is_monodisperse,
            "explanation": explanation,
            "abs_zeta_mv": abs_zeta
        }
