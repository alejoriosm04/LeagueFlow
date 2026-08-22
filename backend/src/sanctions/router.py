"""Endpoint de ficha disciplinaria — contracts/cards-sanctions.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.sanctions.schemas import PlayerDiscipline
from src.sanctions.service import SanctionsService

router = APIRouter(tags=["sanctions"])


@router.get("/players/{player_id}/discipline")
async def obtener_ficha_disciplinaria(
    player_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> PlayerDiscipline:
    """FR-008: consulta pública, sin sesión."""
    return await SanctionsService(db).obtener_ficha(player_id)
