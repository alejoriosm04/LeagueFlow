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


__all__ = ["Standings", "StandingsRow"]
