"""Reglas de negocio de partidos (FR-001, FR-002, FR-003, FR-005)."""

import uuid
from datetime import UTC, datetime

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.leagues.service import LeagueService
from src.matches.models import Match, ResultCorrectionRequest
from src.matches.schemas import MatchStatus
from src.teams.service import TeamService


class MatchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _exigir_liga(self, league_id: uuid.UUID) -> None:
        liga = await LeagueService(self.db).obtener_liga(league_id)
        if liga is None:
            raise ErrorDeNegocio(
                code="league_not_found",
                message="La liga no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    async def _exigir_equipo_activo_en_liga(self, team_id: uuid.UUID, league_id: uuid.UUID) -> None:
        """research.md §3: activo y de la liga; si no, 404 team_not_found genérico."""
        equipo = await TeamService(self.db).obtener_equipo(team_id)
        if equipo is None or equipo.status != "active" or equipo.league_id != league_id:
            raise ErrorDeNegocio(
                code="team_not_found",
                message="El equipo no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    async def crear_partido(
        self,
        league_id: uuid.UUID,
        home_team_id: uuid.UUID,
        away_team_id: uuid.UUID,
        scheduled_at: datetime,
        creado_por: uuid.UUID,
    ) -> Match:
        await self._exigir_liga(league_id)

        # FR-002
        if home_team_id == away_team_id:
            raise ErrorDeNegocio(
                code="match_same_team",
                message="Un equipo no puede enfrentarse a sí mismo.",
                status_code=status.HTTP_409_CONFLICT,
            )

        # FR-003 / research.md §3
        await self._exigir_equipo_activo_en_liga(home_team_id, league_id)
        await self._exigir_equipo_activo_en_liga(away_team_id, league_id)

        partido = Match(
            league_id=league_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            scheduled_at=scheduled_at,
            status="scheduled",
            home_score=None,
            away_score=None,
            created_by=creado_por,
        )
        self.db.add(partido)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ErrorDeNegocio(
                code="match_same_team",
                message="Un equipo no puede enfrentarse a sí mismo.",
                status_code=status.HTTP_409_CONFLICT,
            ) from None

        await self.db.refresh(partido)
        return partido

    async def listar_partidos(
        self,
        league_id: uuid.UUID,
        page: int,
        page_size: int,
        match_status: MatchStatus | None = None,
    ) -> tuple[list[Match], int]:
        await self._exigir_liga(league_id)
        filtros = [Match.league_id == league_id]
        if match_status is not None:
            filtros.append(Match.status == match_status)
        total = await self.db.scalar(select(func.count()).select_from(Match).where(*filtros)) or 0
        orden = (
            (Match.scheduled_at.desc(), Match.id.desc())
            if match_status == "finished"
            else (Match.scheduled_at.asc(), Match.id.asc())
        )
        res = await self.db.execute(
            select(Match)
            .where(*filtros)
            .order_by(*orden)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total

    async def listar_finalizados(self, league_id: uuid.UUID) -> list[Match]:
        """Interfaz de dominio para la clasificación (spec 008).

        Sin paginación: la tabla es indivisible. El filtro por estado también
        vive aquí para no traer partidos que la clasificación descartaría.
        """
        await self._exigir_liga(league_id)
        res = await self.db.execute(
            select(Match)
            .where(Match.league_id == league_id, Match.status == "finished")
            .order_by(Match.scheduled_at.asc(), Match.id.asc())
        )
        return list(res.scalars())

    async def obtener_partido(self, match_id: uuid.UUID) -> Match | None:
        return await self.db.get(Match, match_id)

    async def registrar_resultado(
        self, match_id: uuid.UUID, home_score: int, away_score: int
    ) -> Match:
        res = await self.db.execute(select(Match).where(Match.id == match_id).with_for_update())
        partido = res.scalar_one_or_none()
        if partido is None:
            raise ErrorDeNegocio(
                code="match_not_found",
                message="El partido no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if partido.status == "finished":
            raise ErrorDeNegocio(
                code="result_already_recorded",
                message="El resultado ya fue registrado; crea una solicitud de corrección.",
                status_code=status.HTTP_409_CONFLICT,
            )
        if partido.status != "scheduled":
            raise ErrorDeNegocio(
                code="match_not_scheduled",
                message="Solo un partido programado admite el resultado inicial.",
                status_code=status.HTTP_409_CONFLICT,
            )
        partido.home_score = home_score
        partido.away_score = away_score
        partido.status = "finished"
        await self.db.commit()
        await self.db.refresh(partido)
        return partido

    async def crear_correccion(
        self,
        match_id: uuid.UUID,
        proposed_home_score: int,
        proposed_away_score: int,
        reason: str,
        requested_by: uuid.UUID,
    ) -> ResultCorrectionRequest:
        res = await self.db.execute(select(Match).where(Match.id == match_id).with_for_update())
        partido = res.scalar_one_or_none()
        if partido is None:
            raise ErrorDeNegocio(
                code="match_not_found",
                message="El partido no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if partido.status != "finished" or partido.home_score is None or partido.away_score is None:
            raise ErrorDeNegocio(
                code="match_not_finished",
                message="Solo un partido finalizado admite correcciones.",
                status_code=status.HTTP_409_CONFLICT,
            )
        solicitud = ResultCorrectionRequest(
            match_id=partido.id,
            proposed_home_score=proposed_home_score,
            proposed_away_score=proposed_away_score,
            previous_home_score=partido.home_score,
            previous_away_score=partido.away_score,
            reason=reason.strip(),
            status="pending",
            requested_by=requested_by,
        )
        self.db.add(solicitud)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ErrorDeNegocio(
                code="correction_pending_exists",
                message="Ya existe una solicitud de corrección pendiente para este partido.",
                status_code=status.HTTP_409_CONFLICT,
            ) from None
        await self.db.refresh(solicitud)
        return solicitud

    async def listar_correcciones(
        self, match_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[ResultCorrectionRequest], int]:
        if await self.db.get(Match, match_id) is None:
            raise ErrorDeNegocio(
                code="match_not_found",
                message="El partido no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        filtros = [ResultCorrectionRequest.match_id == match_id]
        total = (
            await self.db.scalar(
                select(func.count()).select_from(ResultCorrectionRequest).where(*filtros)
            )
            or 0
        )
        res = await self.db.execute(
            select(ResultCorrectionRequest)
            .where(*filtros)
            .order_by(ResultCorrectionRequest.created_at.desc(), ResultCorrectionRequest.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total

    async def decidir_correccion(
        self,
        correction_id: uuid.UUID,
        decision: str,
        decision_reason: str | None,
        decided_by: uuid.UUID,
    ) -> ResultCorrectionRequest:
        res = await self.db.execute(
            select(ResultCorrectionRequest)
            .where(ResultCorrectionRequest.id == correction_id)
            .with_for_update()
        )
        solicitud = res.scalar_one_or_none()
        if solicitud is None:
            raise ErrorDeNegocio(
                code="correction_not_found",
                message="La solicitud de corrección no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if solicitud.status != "pending":
            raise ErrorDeNegocio(
                code="correction_already_decided",
                message="La solicitud ya fue decidida.",
                status_code=status.HTTP_409_CONFLICT,
            )
        if solicitud.requested_by == decided_by:
            raise ErrorDeNegocio(
                code="correction_self_decision",
                message="El solicitante no puede decidir su propia corrección.",
                status_code=status.HTTP_409_CONFLICT,
            )
        solicitud.status = decision
        solicitud.decided_by = decided_by
        solicitud.decided_at = datetime.now(UTC)
        solicitud.decision_reason = decision_reason.strip() if decision_reason else None
        if decision == "approved":
            match_res = await self.db.execute(
                select(Match).where(Match.id == solicitud.match_id).with_for_update()
            )
            partido = match_res.scalar_one()
            partido.home_score = solicitud.proposed_home_score
            partido.away_score = solicitud.proposed_away_score
        await self.db.commit()
        await self.db.refresh(solicitud)
        return solicitud
