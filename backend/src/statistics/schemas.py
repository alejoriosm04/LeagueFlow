"""Schemas de la clasificación — contracts/standings.openapi.yaml.

`Standings` no es una entidad persistida: se deriva en cada lectura de los
partidos finalizados (specs/008-consultar-clasificacion/data-model.md).
"""

import uuid

from pydantic import BaseModel, Field

from src.matches.schemas import Match


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


class DashboardSummary(BaseModel):
    """Vista agregada de solo lectura — specs/011-dashboard-liga.

    No es una entidad persistida: se compone en cada lectura recortando lo
    que ya devuelven `MatchService.listar_partidos` (007) y
    `StandingsService.obtener_clasificacion` (008) a 5 elementos cada uno.
    `Match` y `StandingsRow` se reutilizan tal cual; este schema no
    redeclara sus propiedades (Principio III).
    """

    league_id: uuid.UUID
    recent_matches: list[Match] = Field(
        max_length=5, description="Últimos 5 finalizados, más reciente primero."
    )
    upcoming_matches: list[Match] = Field(
        max_length=5, description="Próximos 5 programados, más cercano primero."
    )
    top_standings: list[StandingsRow] = Field(
        max_length=5, description="Primeras 5 filas de la clasificación."
    )


__all__ = ["DashboardSummary", "Standings", "StandingsRow"]
