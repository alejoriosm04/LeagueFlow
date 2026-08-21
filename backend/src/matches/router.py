"""Endpoints de partidos — contracts/matches.openapi.yaml."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import requiere_rol
from src.auth.models import Usuario
from src.core.db import get_db
from src.core.errors import ErrorDeNegocio
from src.matches.schemas import (
    CreateCorrectionInput,
    CreateEventInput,
    CreateMatchRequest,
    DecisionInput,
    Match,
    MatchEvent,
    MatchEvents,
    MatchLineupView,
    MatchStatus,
    PaginatedCorrections,
    PaginatedMatches,
    ResultCorrection,
    ScoreInput,
    UpsertLineupInput,
)
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
    match_status: MatchStatus | None = Query(None, alias="status"),
) -> PaginatedMatches:
    """Listado público por liga (research.md §2)."""
    servicio = MatchService(db)
    partidos, total = await servicio.listar_partidos(liga_id, page, page_size, match_status)
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


@router.put("/matches/{partido_id}/result")
async def registrar_resultado(
    partido_id: uuid.UUID,
    datos: ScoreInput,
    _: Usuario = Depends(requiere_rol("operador", "organizador")),
    db: AsyncSession = Depends(get_db),
) -> Match:
    partido = await MatchService(db).registrar_resultado(
        partido_id, datos.home_score, datos.away_score
    )
    return Match.model_validate(partido)


@router.post("/matches/{partido_id}/result-corrections", status_code=status.HTTP_201_CREATED)
async def crear_correccion(
    partido_id: uuid.UUID,
    datos: CreateCorrectionInput,
    actor: Usuario = Depends(requiere_rol("operador", "organizador")),
    db: AsyncSession = Depends(get_db),
) -> ResultCorrection:
    solicitud = await MatchService(db).crear_correccion(
        partido_id,
        datos.home_score,
        datos.away_score,
        datos.reason,
        actor.id,
    )
    return ResultCorrection.model_validate(solicitud)


@router.get("/matches/{partido_id}/result-corrections")
async def listar_correcciones(
    partido_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedCorrections:
    solicitudes, total = await MatchService(db).listar_correcciones(partido_id, page, page_size)
    return PaginatedCorrections(
        items=[ResultCorrection.model_validate(s) for s in solicitudes],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("/result-corrections/{correction_id}/decision")
async def decidir_correccion(
    correction_id: uuid.UUID,
    datos: DecisionInput,
    actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
) -> ResultCorrection:
    solicitud = await MatchService(db).decidir_correccion(
        correction_id,
        datos.decision,
        datos.decision_reason,
        actor.id,
    )
    return ResultCorrection.model_validate(solicitud)


@router.post("/matches/{partido_id}/events", status_code=status.HTTP_201_CREATED)
async def registrar_gol(
    partido_id: uuid.UUID,
    datos: CreateEventInput,
    actor: Usuario = Depends(requiere_rol("operador", "organizador")),
    db: AsyncSession = Depends(get_db),
) -> MatchEvent:
    """FR-001 y FR-006: solo operador u organizador; el autor sale de la sesión.

    Nunca falla por descuadre con el marcador: FR-005 advierte, no bloquea, y
    la advertencia se consulta en el GET.
    """
    evento = await MatchService(db).registrar_gol(
        partido_id, datos.player_id, datos.minute, datos.type, actor.id
    )
    return MatchEvent.model_validate(evento)


@router.get("/matches/{partido_id}/events")
async def listar_eventos(partido_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> MatchEvents:
    """Consulta pública, sin sesión (research.md §6)."""
    eventos, consistencia = await MatchService(db).listar_eventos(partido_id)
    return MatchEvents(
        items=[MatchEvent.model_validate(e) for e in eventos],
        consistency=consistencia,
    )


# --- Alineaciones (spec 010) ------------------------------------------------


@router.put("/matches/{partido_id}/lineup")
async def guardar_alineacion(
    partido_id: uuid.UUID,
    datos: UpsertLineupInput,
    actor: Usuario = Depends(requiere_rol("operador", "organizador")),
    db: AsyncSession = Depends(get_db),
) -> MatchLineupView:
    """FR-001, FR-005: solo operador u organizador. Reemplazo completo (research.md §1)."""
    return await MatchService(db).guardar_alineacion(
        partido_id, datos.home_player_ids, datos.away_player_ids, actor.id
    )


@router.get("/matches/{partido_id}/lineup")
async def obtener_alineacion(
    partido_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> MatchLineupView:
    """FR-004: consulta pública. `status` señala si la alineación existe."""
    return await MatchService(db).obtener_alineacion(partido_id)
