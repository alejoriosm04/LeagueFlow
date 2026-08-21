"""Schemas de la clasificación — contracts/standings.openapi.yaml.

`Standings` no es una entidad persistida: se deriva en cada lectura de los
partidos finalizados (specs/008-consultar-clasificacion/data-model.md).
"""

import uuid

from pydantic import BaseModel, Field


class StandingsRow(BaseModel):
    """Fila de la tabla. El orden de los campos es el orden del contrato."""

    position: int = Field(ge=1, description="Posición 1..N según FR-005 y FR-006.")
    team_id: uuid.UUID
    team_name: str
    played: int = Field(ge=0)
    won: int = Field(ge=0)
    drawn: int = Field(ge=0)
    lost: int = Field(ge=0)
    goals_for: int = Field(ge=0)
    goals_against: int = Field(ge=0)
    goal_difference: int = Field(description="GF - GC; puede ser negativo.")
    points: int = Field(ge=0, description="3 por victoria, 1 por empate (FR-003).")


class Standings(BaseModel):
    """Tabla completa de una liga. Sin paginación: media tabla no es un ranking."""

    league_id: uuid.UUID
    items: list[StandingsRow]


# --- Estadísticas de jugador (spec 010) -------------------------------------
#
# Vistas derivadas de solo lectura: nunca se editan (FR-008). Se recalculan en
# cada consulta desde `match_events` y `match_lineups` (data-model.md).


class PlayerStatistics(BaseModel):
    """Ficha estadística de un jugador (FR-010)."""

    player_id: uuid.UUID
    player_name: str
    team_id: uuid.UUID
    team_name: str
    goals: int = Field(ge=0)
    matches_played: int = Field(ge=0)


class TopScorerRow(BaseModel):
    """Fila de la tabla de goleadores (FR-009). Orden: goals DESC, name ASC, id ASC (NFR-003)."""

    rank: int = Field(ge=1)
    player_id: uuid.UUID
    player_name: str
    team_id: uuid.UUID
    team_name: str
    goals: int = Field(ge=0)
    matches_played: int = Field(ge=0)
    is_top_scorer: bool = Field(description="true cuando goals coincide con el máximo de la liga.")


class TopScorers(BaseModel):
    items: list[TopScorerRow]


__all__ = ["PlayerStatistics", "Standings", "StandingsRow", "TopScorerRow", "TopScorers"]
