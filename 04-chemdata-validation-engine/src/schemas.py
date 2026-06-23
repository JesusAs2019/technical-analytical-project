from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CompoundInput(BaseModel):
    compound_id: str = Field(..., min_length=3, max_length=50)
    compound_name: str = Field(..., min_length=2, max_length=100)
    smiles: str = Field(..., min_length=1)
    source: Optional[str] = Field(default="unknown")
    temperature_c: Optional[float] = None
    ph: Optional[float] = None

    @field_validator("compound_id", "compound_name", "smiles")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, value):
        if value is None:
            return value
        if not (0.0 <= value <= 14.0):
            raise ValueError("pH must be between 0.0 and 14.0")
        return value

    @field_validator("temperature_c")
    @classmethod
    def validate_temperature(cls, value):
        if value is None:
            return value
        if value < -273.15:
            raise ValueError("temperature_c cannot be below absolute zero")
        return value


class ValidatedCompound(BaseModel):
    compound_id: str
    compound_name: str
    smiles: str
    source: str
    molecular_weight: Optional[float] = None
    molecular_formula: Optional[str] = None
    logp: Optional[float] = None
    h_bond_donors: Optional[int] = None
    h_bond_acceptors: Optional[int] = None
    chiral_centers: Optional[int] = None
    validation_status: str
    validation_message: str
