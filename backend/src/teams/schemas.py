"""Schemas de la API de equipos — contracts/teams.openapi.yaml."""

import uuid
from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateTeamRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    crest_url: str | None = Field(default=None, max_length=500)
    colors: str | None = Field(default=None, max_length=60)

    @field_validator("name")
    @classmethod
    def no_vacio_tras_recorte(cls, v: str) -> str:
        """FR-001: el nombre es obligatorio; solo espacios no cuenta."""
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v

    @field_validator("crest_url")
    @classmethod
    def url_https_absoluta(cls, v: str | None) -> str | None:
        """research.md §1: URL https absoluta; el recurso nunca se descarga."""
        if v is None:
            return v
        parsed = urlparse(v)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("El escudo debe ser una URL https absoluta.")
        return v


class Team(BaseModel):
    """Respuesta pública de un equipo. crest_url y colors pueden ser null."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    league_id: uuid.UUID
    name: str
    crest_url: str | None
    colors: str | None
    status: str
    created_by: uuid.UUID
    created_at: datetime


class PaginatedTeams(BaseModel):
    """Envelope de paginación de conventions.md §Paginación."""

    items: list[Team]
    page: int
    page_size: int
    total: int
