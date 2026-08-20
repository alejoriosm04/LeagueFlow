"""Endpoints de partidos — contracts/matches.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import requiere_rol
from src.auth.models import Usuario
from src.core.db import get_db
from src.core.errors import ErrorDeNegocio
from src.matches.schemas import CreateMatchRequest, Match, PaginatedMatches
from src.matches.service import MatchService

router = APIRouter(tags=["matches"])


@router.post("/leagues/{liga_id}/matches", status_code=status.HTTP_201_CREATED)
async def crear_partido(
    liga_id: uuid.UUID,
    datos: CreateMatchRequest,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Match:
    """FR-006: solo organizador. `created_by` se deriva de la sesión."""
    servicio = MatchService(db)
    creado = await servicio.crear_partido(
        league_id=liga_id,
        home_team_id=datos.home_team_id,
        away_team_id=datos.away_team_id,
        scheduled_at=datos.scheduled_at,
        creado_por=actor.id,
    )
    return Match.model_validate(creado)


@router.get("/leagues/{liga_id}/matches")
async def listar_partidos(
    liga_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedMatches:
    """Listado público por liga (research.md §2)."""
    servicio = MatchService(db)
    partidos, total = await servicio.listar_partidos(liga_id, page, page_size)
    return PaginatedMatches(
        items=[Match.model_validate(p) for p in partidos],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/matches/{partido_id}")
async def obtener_partido(partido_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Match:
    """FR-005: detalle público."""
    servicio = MatchService(db)
    partido = await servicio.obtener_partido(partido_id)
    if partido is None:
        raise ErrorDeNegocio(
            code="match_not_found",
            message="El partido no existe.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return Match.model_validate(partido)
