"""Schemas de la ficha disciplinaria — contracts/cards-sanctions.openapi.yaml."""

import uuid

from pydantic import BaseModel, Field


class PlayerDiscipline(BaseModel):
    player_id: uuid.UUID
    yellow_cards: int = Field(ge=0)
    red_cards: int = Field(ge=0)
    suspended: bool
