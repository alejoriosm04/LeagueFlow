"""Orquesta servicios públicos existentes y los proyecta a CSV."""

import uuid
from collections.abc import Callable
from datetime import datetime

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.exports.csv_serializer import CsvDocument, crear_csv
from src.leagues.service import LeagueService
from src.matches.service import MatchService
from src.statistics.service import StandingsService
from src.teams.service import TeamService


class ExportService:
    def __init__(self, db: AsyncSession, now: Callable[[], datetime] | None = None) -> None:
        self.db = db
        self.now = now

    async def _league_name(self, league_id: uuid.UUID) -> str:
        league = await LeagueService(self.db).obtener_liga(league_id)
        if league is None:
            raise ErrorDeNegocio(
                code="league_not_found",
                message="La liga no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return league.name

    async def standings(self, league_id: uuid.UUID) -> CsvDocument:
        name = await self._league_name(league_id)
        table = await StandingsService(self.db).obtener_clasificacion(league_id)
        rows = [
            [
                r.position,
                r.team_name,
                r.played,
                r.won,
                r.drawn,
                r.lost,
                r.goals_for,
                r.goals_against,
                r.goal_difference,
                r.points,
            ]
            for r in table.items
        ]
        return crear_csv(
            league_name=name,
            resource="clasificacion",
            headers=["Pos", "Equipo", "PJ", "G", "E", "P", "GF", "GC", "GD", "Pts"],
            rows=rows,
            now=self.now,
        )

    async def calendar(self, league_id: uuid.UUID) -> CsvDocument:
        name = await self._league_name(league_id)
        match_service = MatchService(self.db)
        matches = []
        for match_status in ("scheduled", "finished"):
            page = 1
            while True:
                items, total = await match_service.listar_partidos(
                    league_id, page=page, page_size=100, match_status=match_status
                )
                matches.extend(items)
                if page * 100 >= total:
                    break
                page += 1
        teams = await TeamService(self.db).listar_por_liga(league_id)
        names = {team.id: team.name for team in teams}
        rows = [
            [
                names.get(match.home_team_id, ""),
                names.get(match.away_team_id, ""),
                match.scheduled_at.isoformat().replace("+00:00", "Z"),
                match.status,
                "" if match.home_score is None else f"{match.home_score}-{match.away_score}",
            ]
            for match in matches
        ]
        return crear_csv(
            league_name=name,
            resource="calendario",
            headers=["Local", "Visitante", "Fecha", "Estado", "Marcador"],
            rows=rows,
            now=self.now,
        )
