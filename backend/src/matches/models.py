"""Modelo de dominio Match — specs/001-fundacion-y-autenticacion/data-model.md §Match."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models_base import Base, TimestampCreated, TimestampUpdated, UUIDPrimaryKey


class Match(Base, UUIDPrimaryKey, TimestampCreated, TimestampUpdated):
    """Enfrentamiento entre dos equipos de la misma liga (FR-001)."""

    __tablename__ = "matches"

    league_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("leagues.id", ondelete="RESTRICT"), nullable=False
    )
    home_team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False
    )
    away_team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # FR-004: enum abierto; esta HU solo produce scheduled.
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")
    # research.md §4: columnas presentes; siempre null al crear en esta HU.
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "home_team_id <> away_team_id",
            name="ck_matches_home_ne_away",
        ),
    )


__all__ = ["Match"]
