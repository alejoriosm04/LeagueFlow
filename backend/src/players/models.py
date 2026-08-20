"""Modelo de dominio Player — specs/001-fundacion-y-autenticacion/data-model.md §Player."""

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models_base import Base, TimestampCreated, UUIDPrimaryKey


class Player(Base, UUIDPrimaryKey, TimestampCreated):
    """Integrante de la plantilla de un equipo (FR-001, FR-002)."""

    __tablename__ = "players"

    # FR-002: pertenece exactamente a un equipo. RESTRICT evita borrar un equipo
    # con plantilla. team_id es inmutable tras creación (Assumption traspaso).
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    # research.md §1: dorsal opcional 1–99; varios sin dorsal son válidos.
    number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # FR-005: borrado lógico. active por defecto; inactive preserva el historial.
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # FR-008 de specs/001: toda escritura queda atribuida a su autor.
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # FR-003: dorsal único dentro del equipo solo cuando está informado
    # (índice parcial; research.md §1).
    __table_args__ = (
        Index(
            "ix_players_unique_team_number",
            "team_id",
            "number",
            unique=True,
            postgresql_where=text("number IS NOT NULL"),
        ),
    )


__all__ = ["Player"]
