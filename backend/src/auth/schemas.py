"""Schemas de la API de autenticación — contracts/auth.openapi.yaml."""

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.auth.security import LONGITUD_MAXIMA, LONGITUD_MINIMA


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=1, max_length=LONGITUD_MAXIMA)


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    # research.md §10: la longitud aporta más que las reglas de composición.
    password: str = Field(min_length=LONGITUD_MINIMA, max_length=LONGITUD_MAXIMA)
    role: Literal["organizador", "operador"]


class UserPublic(BaseModel):
    """Nunca incluye password_hash (contrato)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    role: str
    status: str


class SesionActual(BaseModel):
    user: UserPublic | None


class PaginatedUsers(BaseModel):
    """Envelope de paginación de conventions.md §Paginación."""

    items: list[UserPublic]
    page: int
    page_size: int
    total: int
