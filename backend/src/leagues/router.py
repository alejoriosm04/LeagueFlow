"""Endpoints de ligas — contracts/leagues.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import requiere_rol
from src.auth.models import Usuario
from src.core.db import get_db
from src.core.errors import ErrorDeNegocio
from src.leagues.schemas import CreateLeagueRequest, League, PaginatedLeagues
from src.leagues.service import LeagueService

router = APIRouter(tags=["leagues"])


@router.post("/leagues", status_code=status.HTTP_201_CREATED)
async def crear_liga(
    datos: CreateLeagueRequest,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> League:
    """FR-005: solo organizador. `created_by` se deriva de la sesión, no del payload."""
    servicio = LeagueService(db)
    creada = await servicio.crear_liga(
        name=datos.name,
        season=datos.season,
        description=datos.description,
        creado_por=actor.id,
    )
    return League.model_validate(creada)


@router.get("/leagues")
async def listar_ligas(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedLeagues:
    """FR-003: listado público, sin autenticación."""
    servicio = LeagueService(db)
    ligas, total = await servicio.listar_ligas(page, page_size)
    return PaginatedLeagues(
        items=[League.model_validate(liga) for liga in ligas],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/leagues/{liga_id}")
async def obtener_liga(liga_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> League:
    """FR-003: detalle público, sin autenticación."""
    servicio = LeagueService(db)
    liga = await servicio.obtener_liga(liga_id)
    if liga is None:
        raise ErrorDeNegocio(
            code="league_not_found",
            message="La liga no existe.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return League.model_validate(liga)
