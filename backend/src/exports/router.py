"""Endpoints públicos de exportación CSV."""

import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.errors import ErrorDeNegocio
from src.exports.csv_serializer import CsvDocument
from src.exports.service import ExportService

router = APIRouter(tags=["exports"])


def _validar_formato(value: str) -> None:
    if value.lower() != "csv":
        raise ErrorDeNegocio(
            code="validation_error",
            message="Solo se admite el formato CSV.",
            status_code=status.HTTP_400_BAD_REQUEST,
            field="format",
        )


def _response(document: CsvDocument) -> Response:
    return Response(
        content=document.content,
        media_type=document.media_type,
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )


@router.get("/leagues/{league_id}/standings/export")
async def export_standings(
    league_id: uuid.UUID,
    format: str = Query(default="csv"),
    db: AsyncSession = Depends(get_db),
) -> Response:
    _validar_formato(format)
    return _response(await ExportService(db).standings(league_id))


@router.get("/leagues/{league_id}/matches/export")
async def export_calendar(
    league_id: uuid.UUID,
    format: str = Query(default="csv"),
    db: AsyncSession = Depends(get_db),
) -> Response:
    _validar_formato(format)
    return _response(await ExportService(db).calendar(league_id))
