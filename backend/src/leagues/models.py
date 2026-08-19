"""Modelo de dominio League — specs/001-fundacion-y-autenticacion/data-model.md §League.

Unicidad `(name, season)` insensible a mayúsculas y a espacios sobrantes:
`research.md` §2 y `specs/002-crear-liga/data-model.md`.
"""

import uuid

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models_base import Base, TimestampCreated, UUIDPrimaryKey


class League(Base, UUIDPrimaryKey, TimestampCreated):
    """Contenedor raíz de una competición (FR-001, FR-004)."""

    __tablename__ = "leagues"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    season: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # FR-008: toda escritura queda atribuida a su autor (el organizador de la
    # sesión), nunca al payload.
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # Red de seguridad ante la ventana de carrera entre dos organizadores:
    # la comprobación de unicidad vive en el servicio (409 legible), y este
    # índice único funcional la respalda a nivel de base de datos (research.md §1).
    __table_args__ = (
        Index(
            "ix_leagues_unique_name_season",
            text("lower(trim(name))"),
            text("lower(trim(season))"),
            unique=True,
        ),
    )


__all__ = ["League"]
