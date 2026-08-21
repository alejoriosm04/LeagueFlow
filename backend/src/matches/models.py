"""Modelo de dominio Match — specs/001-fundacion-y-autenticacion/data-model.md §Match."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, text
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
        CheckConstraint(
            "home_score IS NULL OR home_score >= 0", name="ck_matches_home_score_nonnegative"
        ),
        CheckConstraint(
            "away_score IS NULL OR away_score >= 0", name="ck_matches_away_score_nonnegative"
        ),
        CheckConstraint(
            "(status = 'finished' AND home_score IS NOT NULL AND away_score IS NOT NULL) OR "
            "(status <> 'finished' AND home_score IS NULL AND away_score IS NULL)",
            name="ck_matches_status_scores_coherent",
        ),
        # specs/011-dashboard-liga/research.md §4: cubre el filtro + orden que
        # ya usan listar_partidos (007) y listar_finalizados (008), y que el
        # dashboard (011) reutiliza tal cual sin añadir consultas propias.
        # Aditivo: no toca columnas ni constraints existentes.
        Index("ix_matches_league_status_scheduled", "league_id", "status", "scheduled_at"),
    )


class ResultCorrectionRequest(Base, UUIDPrimaryKey, TimestampCreated):
    """Propuesta auditada de corrección para un partido finalizado."""

    __tablename__ = "result_correction_requests"

    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("matches.id", ondelete="RESTRICT"), nullable=False
    )
    proposed_home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    proposed_away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    requested_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "proposed_home_score >= 0", name="ck_corrections_proposed_home_nonnegative"
        ),
        CheckConstraint(
            "proposed_away_score >= 0", name="ck_corrections_proposed_away_nonnegative"
        ),
        CheckConstraint(
            "previous_home_score >= 0", name="ck_corrections_previous_home_nonnegative"
        ),
        CheckConstraint(
            "previous_away_score >= 0", name="ck_corrections_previous_away_nonnegative"
        ),
        CheckConstraint("length(trim(reason)) > 0", name="ck_corrections_reason_nonempty"),
        CheckConstraint(
            "(status = 'pending' AND decided_by IS NULL AND decided_at IS NULL "
            "AND decision_reason IS NULL) OR "
            "(status = 'approved' AND decided_by IS NOT NULL AND decided_at IS NOT NULL "
            "AND decision_reason IS NULL) OR "
            "(status = 'rejected' AND decided_by IS NOT NULL AND decided_at IS NOT NULL "
            "AND decision_reason IS NOT NULL AND length(trim(decision_reason)) > 0)",
            name="ck_corrections_resolution_coherent",
        ),
        CheckConstraint(
            "decided_by IS NULL OR decided_by <> requested_by",
            name="ck_corrections_separate_decider",
        ),
        Index("ix_corrections_match_created", "match_id", "created_at"),
        Index(
            "ix_corrections_one_pending_per_match",
            "match_id",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )


class MatchLineup(Base, UUIDPrimaryKey, TimestampCreated, TimestampUpdated):
    """Jugador participante de un partido, por equipo — specs/010.

    Grano: una fila por jugador participante (FR-001). `PUT /matches/{id}/lineup`
    la trata como reemplazo completo idempotente (research.md §1): corregir una
    alineación borra e inserta de nuevo, así que `created_at`/`updated_at`
    reflejan la última escritura, no el historial de correcciones (NFR-001).
    """

    __tablename__ = "match_lineups"

    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("matches.id", ondelete="RESTRICT"), nullable=False
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("players.id", ondelete="RESTRICT"), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        Index("uq_match_lineups_match_player", "match_id", "player_id", unique=True),
        Index("ix_match_lineups_match_team", "match_id", "team_id"),
        Index("ix_match_lineups_player", "player_id"),
    )


class MatchEvent(Base, UUIDPrimaryKey, TimestampCreated):
    """Hecho ocurrido durante un partido — specs/009-registrar-goles.

    Declarada en specs/001-fundacion-y-autenticacion/data-model.md §MatchEvent;
    esta HU la implementa. `type` es String + CHECK y no un ENUM de PostgreSQL
    a propósito: FR-004 exige que añadir un tipo no obligue a rediseñar, y
    sustituir un CHECK es una migración trivial mientras que `ALTER TYPE`
    bloquea (data-model.md de 009).
    """

    __tablename__ = "match_events"

    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("matches.id", ondelete="RESTRICT"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="GOAL")
    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("players.id", ondelete="RESTRICT"), nullable=False
    )
    # research.md §4: se deriva de Player.team_id, nunca lo envía el cliente.
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False
    )
    minute: Mapped[int] = mapped_column(Integer, nullable=False)

    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        CheckConstraint("minute >= 0", name="ck_match_events_minute_nonnegative"),
        CheckConstraint("type IN ('GOAL')", name="ck_match_events_type_supported"),
        # Dos goles del mismo jugador en el mismo minuto son legítimos: no hay
        # unicidad. El índice sirve al listado por partido y a la derivación de 010.
        Index("ix_match_events_match_minute", "match_id", "minute"),
    )


__all__ = ["Match", "MatchEvent", "MatchLineup", "ResultCorrectionRequest"]
