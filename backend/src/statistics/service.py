"""Orquestación de la clasificación — spec 008.

Este módulo NO importa los modelos `Match` ni `Team`: consume la interfaz
pública de esos dominios (Principio VIII de la constitución) y delega la regla
de negocio en `calculator.py`.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.matches.schemas import Match
from src.matches.service import MatchService
from src.statistics.calculator import EquipoEnTabla, PartidoParaTabla, calcular_clasificacion
from src.statistics.schemas import DashboardSummary, Standings
from src.teams.service import TeamService


class StandingsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def obtener_clasificacion(self, league_id: uuid.UUID) -> Standings:
        """Deriva la tabla en lectura. Una liga inexistente produce 404."""
        equipos = await TeamService(self.db).listar_por_liga(league_id)
        partidos = await MatchService(self.db).listar_finalizados(league_id)

        filas = calcular_clasificacion(
            [
                EquipoEnTabla(id=equipo.id, name=equipo.name, activo=equipo.status == "active")
                for equipo in equipos
            ],
            [
                PartidoParaTabla(
                    home_team_id=partido.home_team_id,
                    away_team_id=partido.away_team_id,
                    home_score=partido.home_score,
                    away_score=partido.away_score,
                    status=partido.status,
                )
                for partido in partidos
            ],
        )
        return Standings(league_id=league_id, items=filas)


class DashboardService:
    """Orquestación del dashboard general de la liga — spec 011.

    No reimplementa el filtro/orden de `MatchService` ni el cálculo de
    `StandingsService`: los llama tal cual y recorta a 5 (research.md §2).
    Sin SQL ni cálculo propio.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def obtener_resumen(self, league_id: uuid.UUID) -> DashboardSummary:
        recientes, _ = await MatchService(self.db).listar_partidos(
            league_id, page=1, page_size=5, match_status="finished"
        )
        proximos, _ = await MatchService(self.db).listar_partidos(
            league_id, page=1, page_size=5, match_status="scheduled"
        )
        clasificacion = await StandingsService(self.db).obtener_clasificacion(league_id)

        return DashboardSummary(
            league_id=league_id,
            recent_matches=[Match.model_validate(m) for m in recientes],
            upcoming_matches=[Match.model_validate(m) for m in proximos],
            top_standings=clasificacion.items[:5],
        )
