"""Endpoint de la clasificación — contracts/standings.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.statistics.schemas import PlayerStatistics, Standings, TopScorers
from src.statistics.service import PlayerStatisticsService, StandingsService

router = APIRouter(tags=["standings"])


@router.get("/leagues/{liga_id}/standings")
async def obtener_clasificacion(
    liga_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Standings:
    """FR-008: consulta pública, sin sesión.

    FR-002: este recurso solo declara GET. La clasificación no se edita por
    ninguna vía; para corregir una posición se corrige el resultado de origen
    con `PUT /matches/{id}/result`.
    """
    return await StandingsService(db).obtener_clasificacion(liga_id)


# --- Estadísticas de jugador (spec 010) --------------------------------------


@router.get("/players/{player_id}/statistics")
async def obtener_ficha_jugador(
    player_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> PlayerStatistics:
    """FR-010, FR-011: consulta pública, sin sesión."""
    return await PlayerStatisticsService(db).obtener_ficha_jugador(player_id)


@router.get("/leagues/{league_id}/top-scorers")
async def obtener_tabla_goleadores(
    league_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> TopScorers:
    """FR-009, FR-011: consulta pública, ordenada por goles descendente (NFR-003)."""
    return await PlayerStatisticsService(db).tabla_goleadores(league_id)
