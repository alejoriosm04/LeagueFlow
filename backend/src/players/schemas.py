"""Schemas de la API de jugadores — contracts/players.openapi.yaml."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreatePlayerRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    number: int | None = Field(default=None, ge=1, le=99)
    position: str | None = Field(default=None, max_length=40)

    @field_validator("name")
    @classmethod
    def no_vacio_tras_recorte(cls, v: str) -> str:
        """FR-001: el nombre es obligatorio; solo espacios no cuenta."""
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v

    @field_validator("position")
    @classmethod
    def posicion_sin_solo_espacios(cls, v: str | None) -> str | None:
        """research.md §2: texto libre; cadena vacía se trata como ausente."""
        if v is None:
            return v
        recortado = v.strip()
        return recortado or None


class Player(BaseModel):
    """Respuesta pública de un jugador. number y position pueden ser null."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID
    name: str
    number: int | None
    position: str | None
    status: str
    created_by: uuid.UUID
    created_at: datetime


class PaginatedPlayers(BaseModel):
    """Envelope de paginación de conventions.md §Paginación."""

    items: list[Player]
    page: int
    page_size: int
    total: int
