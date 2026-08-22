"""Schemas de la API de grupos — contracts/groups.openapi.yaml."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    position: int | None = Field(default=None)

    @field_validator("name")
    @classmethod
    def no_vacio_tras_recorte(cls, v: str) -> str:
        """FR-001: el nombre es obligatorio; solo espacios no cuenta."""
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v


class RenameGroupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def no_vacio_tras_recorte(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El campo no puede estar vacío.")
        return v


class AssignTeamRequest(BaseModel):
    team_id: uuid.UUID


class Group(BaseModel):
    """Respuesta pública de un grupo."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    league_id: uuid.UUID
    name: str
    position: int | None
    created_at: datetime


class TeamInGroup(BaseModel):
    """Equipo dentro de la composición de un grupo (FR-009, FR-012)."""

    team_id: uuid.UUID
    name: str
    status: str


class GroupWithTeams(Group):
    """Grupo con su composición (FR-009)."""

    teams: list[TeamInGroup]


class GroupList(BaseModel):
    items: list[GroupWithTeams]
