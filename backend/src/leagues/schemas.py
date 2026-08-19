"""Schemas de la API de ligas — contracts/leagues.openapi.yaml."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateLeagueRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    season: str = Field(min_length=1, max_length=60)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name", "season")
    @classmethod
    def no_vacio_tras_recorte(cls, v: str) -> str:
        """FR-001: nombre y temporada obligatorios; solo espacios no cuenta."""
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v


class League(BaseModel):
    """Respuesta pública de una liga. description puede ser null (opcional)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    season: str
    description: str | None
    created_by: uuid.UUID
    created_at: datetime


class PaginatedLeagues(BaseModel):
    """Envelope de paginación de conventions.md §Paginación."""

    items: list[League]
    page: int
    page_size: int
    total: int
