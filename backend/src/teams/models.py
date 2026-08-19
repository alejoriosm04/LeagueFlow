"""Modelo de dominio Team — specs/001-fundacion-y-autenticacion/data-model.md §Team."""

import uuid

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models_base import Base, TimestampCreated, UUIDPrimaryKey


class Team(Base, UUIDPrimaryKey, TimestampCreated):
    """Participante de una liga (FR-001, FR-003)."""

    __tablename__ = "teams"

    # FR-003: un equipo pertenece exactamente a una liga. RESTRICT evita borrar
    # por accidente una liga que ya tiene equipos (data-model.md).
    league_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("leagues.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    crest_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    colors: Mapped[str | None] = mapped_column(String(60), nullable=True)
    # FR-005: borrado lógico. active por defecto; inactive preserva el historial.
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # FR-008 de specs/001: toda escritura queda atribuida a su autor.
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # FR-002: nombre único dentro de la liga, insensible a mayúsculas y espacios;
    # el mismo nombre es válido en ligas distintas (data-model.md, research.md §2).
    __table_args__ = (
        Index(
            "ix_teams_unique_league_name",
            "league_id",
            text("lower(trim(name))"),
            unique=True,
        ),
    )


__all__ = ["Team"]
