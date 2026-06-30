from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, engine


class VerifiedCompound(Base):
    __tablename__ = "verified_compounds"

    compound_id: Mapped[str] = mapped_column(String, primary_key=True)
    compound_name: Mapped[str] = mapped_column(String, nullable=False)
    smiles: Mapped[str] = mapped_column(String, nullable=False)
    molecular_formula: Mapped[str] = mapped_column(String, nullable=False)
    molecular_weight: Mapped[float] = mapped_column(Float, nullable=False)
    validation_status: Mapped[str] = mapped_column(String, nullable=False)

    stereochemical_metric = relationship(
        "StereochemicalMetric",
        back_populates="compound",
        uselist=False,
        cascade="all, delete-orphan"
    )

    reaction_condition = relationship(
        "ReactionCondition",
        back_populates="compound",
        uselist=False,
        cascade="all, delete-orphan"
    )


class StereochemicalMetric(Base):
    __tablename__ = "stereochemical_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    compound_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("verified_compounds.compound_id"),
        nullable=False,
        unique=True
    )
    chiral_centers: Mapped[int] = mapped_column(Integer, nullable=False)
    stereochemistry_notes: Mapped[str] = mapped_column(String, nullable=False)

    compound = relationship("VerifiedCompound", back_populates="stereochemical_metric")


class ReactionCondition(Base):
    __tablename__ = "reaction_conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    compound_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("verified_compounds.compound_id"),
        nullable=False,
        unique=True
    )
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    solvent: Mapped[str] = mapped_column(String, nullable=False)
    reaction_time_hr: Mapped[float] = mapped_column(Float, nullable=False)
    ph: Mapped[float] = mapped_column(Float, nullable=False)

    compound = relationship("VerifiedCompound", back_populates="reaction_condition")


def create_schema():
    Base.metadata.create_all(bind=engine)
