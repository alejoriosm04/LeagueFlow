"""Endpoint de la clasificación — contracts/standings.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.statistics.schemas import Standings
from src.statistics.service import StandingsService

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
