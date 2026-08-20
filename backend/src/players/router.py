"""Endpoints de jugadores — contracts/players.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import requiere_rol
from src.auth.models import Usuario
from src.core.db import get_db
from src.core.errors import ErrorDeNegocio
from src.players.schemas import CreatePlayerRequest, PaginatedPlayers, Player
from src.players.service import PlayerService

router = APIRouter(tags=["players"])


@router.post("/teams/{equipo_id}/players", status_code=status.HTTP_201_CREATED)
async def crear_jugador(
    equipo_id: uuid.UUID,
    datos: CreatePlayerRequest,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> Player:
    """FR-004: solo organizador. `created_by` se deriva de la sesión."""
    servicio = PlayerService(db)
    creado = await servicio.crear_jugador(
        team_id=equipo_id,
        name=datos.name,
        number=datos.number,
        position=datos.position,
        creado_por=actor.id,
    )
    return Player.model_validate(creado)


@router.get("/teams/{equipo_id}/players")
async def listar_jugadores(
    equipo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedPlayers:
    """Listado público de la plantilla. Solo activos por defecto (FR-005)."""
    servicio = PlayerService(db)
    jugadores, total = await servicio.listar_jugadores(equipo_id, include_inactive, page, page_size)
    return PaginatedPlayers(
        items=[Player.model_validate(j) for j in jugadores],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/players/{jugador_id}")
async def obtener_jugador(jugador_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Player:
    """Detalle público, incluido si está inactivo (historial)."""
    servicio = PlayerService(db)
    jugador = await servicio.obtener_jugador(jugador_id)
    if jugador is None:
        raise ErrorDeNegocio(
            code="player_not_found",
            message="El jugador no existe.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return Player.model_validate(jugador)
