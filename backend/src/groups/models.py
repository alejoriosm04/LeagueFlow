"""Modelo de dominio de grupos — specs/013-grupos-divisiones/data-model.md."""

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models_base import Base, TimestampCreated, TimestampUpdated, UUIDPrimaryKey


class LeagueGroup(Base, UUIDPrimaryKey, TimestampCreated, TimestampUpdated):
    """División de una liga (FR-001)."""

    __tablename__ = "groups"

    # RESTRICT: una liga con grupos no se borra por accidente (data-model.md).
    league_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("leagues.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    # research.md §5: orden de presentación opcional, sin regla de negocio.
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # FR-008 de specs/001: toda escritura queda atribuida a su autor.
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # FR-002: nombre único dentro de la liga, insensible a mayúsculas y espacios
    # (mismo patrón que leagues/teams).
    __table_args__ = (
        Index(
            "ix_groups_unique_league_name",
            "league_id",
            text("lower(trim(name))"),
            unique=True,
        ),
    )


class GroupTeamMembership(Base, UUIDPrimaryKey, TimestampCreated):
    """Pertenencia de un equipo a un grupo (FR-005, FR-006, FR-007).

    Tabla puente: no se toca `teams` (Principio VIII).
    """

    __tablename__ = "group_memberships"

    # CASCADE: al borrar el grupo se borran sus membresías, nunca los equipos (FR-004).
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    # RESTRICT: no se borra un equipo que está en un grupo.
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    # FR-007 / research.md §2: "a lo sumo un grupo por liga" es equivalente a
    # "a lo sumo un grupo" porque un equipo es de una sola liga.
    __table_args__ = (
        Index("uq_group_memberships_team", "team_id", unique=True),
        Index("ix_group_memberships_group", "group_id"),
    )


__all__ = ["LeagueGroup", "GroupTeamMembership"]
