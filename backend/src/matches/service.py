"""Reglas de negocio de partidos (FR-001, FR-002, FR-003, FR-005)."""

import uuid
from datetime import datetime

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.leagues.service import LeagueService
from src.matches.models import Match
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
        self, league_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Match], int]:
        await self._exigir_liga(league_id)
        filtros = [Match.league_id == league_id]
        total = await self.db.scalar(select(func.count()).select_from(Match).where(*filtros)) or 0
        res = await self.db.execute(
            select(Match)
            .where(*filtros)
            .order_by(Match.scheduled_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total

    async def obtener_partido(self, match_id: uuid.UUID) -> Match | None:
        return await self.db.get(Match, match_id)
