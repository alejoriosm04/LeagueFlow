"""Endpoints de grupos — contracts/groups.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import requiere_rol
from src.auth.models import Usuario
from src.core.db import get_db
from src.groups.schemas import (
    AssignTeamRequest,
    CreateGroupRequest,
    Group,
    GroupList,
    GroupWithTeams,
    RenameGroupRequest,
    TeamInGroup,
)
from src.groups.service import GroupService

router = APIRouter(tags=["groups"])


@router.post("/leagues/{league_id}/groups", status_code=status.HTTP_201_CREATED)
async def crear_grupo(
    league_id: uuid.UUID,
    datos: CreateGroupRequest,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Group:
    """FR-001: solo organizador."""
    grupo = await GroupService(db).crear_grupo(
        league_id=league_id, name=datos.name, position=datos.position, creado_por=actor.id
    )
    return Group.model_validate(grupo)


@router.get("/leagues/{league_id}/groups")
async def listar_grupos(league_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> GroupList:
    """FR-009: composición pública (FR-012 incluye inactivos miembros)."""
    grupos = await GroupService(db).listar_grupos(league_id)
    return GroupList(
        items=[
            GroupWithTeams(
                id=grupo.id,
                league_id=grupo.league_id,
                name=grupo.name,
                position=grupo.position,
                created_at=grupo.created_at,
                teams=[
                    TeamInGroup(team_id=tid, name=nombre, status=estado)
                    for tid, nombre, estado in equipos
                ],
            )
            for grupo, equipos in grupos
        ]
    )


@router.patch("/groups/{group_id}")
async def renombrar_grupo(
    group_id: uuid.UUID,
    datos: RenameGroupRequest,
    _: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Group:
    """FR-003: solo organizador."""
    grupo = await GroupService(db).renombrar_grupo(group_id, datos.name)
    return Group.model_validate(grupo)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_grupo(
    group_id: uuid.UUID,
    _: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """FR-004: borra el grupo y sus membresías, nunca los equipos."""
    await GroupService(db).eliminar_grupo(group_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/groups/{group_id}/teams", status_code=status.HTTP_201_CREATED)
async def asignar_equipo(
    group_id: uuid.UUID,
    datos: AssignTeamRequest,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """FR-005: asigna un equipo activo de la liga al grupo."""
    await GroupService(db).asignar_equipo(group_id, datos.team_id, creado_por=actor.id)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/groups/{group_id}/teams", status_code=status.HTTP_204_NO_CONTENT)
async def desasignar_equipo(
    group_id: uuid.UUID,
    team_id: uuid.UUID = Query(...),
    _: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """FR-006: quita la membresía del equipo en el grupo."""
    await GroupService(db).desasignar_equipo(group_id, team_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
