"""Endpoints de equipos — contracts/teams.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import requiere_rol
from src.auth.models import Usuario
from src.core.db import get_db
from src.core.errors import ErrorDeNegocio
from src.teams.schemas import CreateTeamRequest, PaginatedTeams, Team
from src.teams.service import TeamService

router = APIRouter(tags=["teams"])


@router.post("/leagues/{liga_id}/teams", status_code=status.HTTP_201_CREATED)
async def crear_equipo(
    liga_id: uuid.UUID,
    datos: CreateTeamRequest,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Team:
    """FR-004: solo organizador. `created_by` se deriva de la sesión."""
    servicio = TeamService(db)
    creado = await servicio.crear_equipo(
        league_id=liga_id,
        name=datos.name,
        crest_url=datos.crest_url,
        colors=datos.colors,
        creado_por=actor.id,
    )
    return Team.model_validate(creado)


@router.get("/leagues/{liga_id}/teams")
async def listar_equipos(
    liga_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedTeams:
    """FR-003: listado público. Solo activos por defecto (FR-005)."""
    servicio = TeamService(db)
    equipos, total = await servicio.listar_equipos(liga_id, include_inactive, page, page_size)
    return PaginatedTeams(
        items=[Team.model_validate(equipo) for equipo in equipos],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/teams/{equipo_id}")
async def obtener_equipo(equipo_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Team:
    """FR-003: detalle público, incluido si está inactivo (historial)."""
    servicio = TeamService(db)
    equipo = await servicio.obtener_equipo(equipo_id)
    if equipo is None:
        raise ErrorDeNegocio(
            code="team_not_found",
            message="El equipo no existe.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return Team.model_validate(equipo)
