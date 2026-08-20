"""Schemas de la API de partidos — contracts/matches.openapi.yaml."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
    status: str
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
