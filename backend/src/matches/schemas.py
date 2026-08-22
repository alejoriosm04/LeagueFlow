"""Schemas de la API de partidos — contracts/matches.openapi.yaml."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MatchStatus = Literal["scheduled", "in_progress", "finished", "cancelled"]


class CreateMatchRequest(BaseModel):
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    scheduled_at: datetime = Field(description="ISO 8601; timezone-aware preferido.")


class Match(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    league_id: uuid.UUID
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    scheduled_at: datetime
    status: MatchStatus
    home_score: int | None
    away_score: int | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PaginatedMatches(BaseModel):
    items: list[Match]
    page: int
    page_size: int
    total: int


class ScoreInput(BaseModel):
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)


class CreateCorrectionInput(ScoreInput):
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def motivo_no_vacio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El motivo es obligatorio.")
        return value


class DecisionInput(BaseModel):
    decision: Literal["approved", "rejected"]
    decision_reason: str | None = None

    @model_validator(mode="after")
    def validar_motivo(self):
        if self.decision == "rejected":
            self.decision_reason = (self.decision_reason or "").strip()
            if not self.decision_reason:
                raise ValueError("El motivo de rechazo es obligatorio.")
        elif self.decision_reason is not None:
            raise ValueError("Una aprobación no admite motivo de rechazo.")
        return self


class ResultCorrection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    match_id: uuid.UUID
    proposed_home_score: int
    proposed_away_score: int
    previous_home_score: int
    previous_away_score: int
    reason: str
    status: Literal["pending", "approved", "rejected"]
    requested_by: uuid.UUID
    decided_by: uuid.UUID | None
    decision_reason: str | None
    created_at: datetime
    decided_at: datetime | None


class PaginatedCorrections(BaseModel):
    items: list[ResultCorrection]
    page: int
    page_size: int
    total: int


# --- Eventos de partido (spec 009) ----------------------------------------

EventType = Literal["GOAL", "YELLOW_CARD", "RED_CARD"]


class CreateEventInput(BaseModel):
    """FR-001. `team_id` no se envía: se deriva del jugador (research.md §4)."""

    player_id: uuid.UUID
    minute: int = Field(ge=0)
    type: EventType = "GOAL"


class MatchEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    match_id: uuid.UUID
    type: EventType
    player_id: uuid.UUID
    team_id: uuid.UUID
    minute: int
    created_by: uuid.UUID
    created_at: datetime


class EventConsistency(BaseModel):
    """Advertencia de FR-005: informa, nunca bloquea ni altera el marcador."""

    home_goals_recorded: int = Field(ge=0)
    away_goals_recorded: int = Field(ge=0)
    home_score: int | None
    away_score: int | None
    matches_official: bool | None


class MatchEvents(BaseModel):
    items: list[MatchEvent]
    consistency: EventConsistency


# --- Alineaciones (spec 010) ------------------------------------------------

LineupStatus = Literal["registered", "missing"]


class UpsertLineupInput(BaseModel):
    """FR-001, FR-003. `PUT` reemplaza la alineación completa (home + away)."""

    home_player_ids: list[uuid.UUID]
    away_player_ids: list[uuid.UUID]

    @field_validator("home_player_ids", "away_player_ids")
    @classmethod
    def sin_duplicados(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(value) != len(set(value)):
            raise ValueError("No se puede repetir un jugador en la misma alineación.")
        return value


class LineupPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: uuid.UUID
    player_name: str
    team_id: uuid.UUID


class MatchLineupView(BaseModel):
    match_id: uuid.UUID
    status: LineupStatus
    home_players: list[LineupPlayer]
    away_players: list[LineupPlayer]
