"""Orquestación de la clasificación — spec 008.

Este módulo NO importa los modelos `Match` ni `Team`: consume la interfaz
pública de esos dominios (Principio VIII de la constitución) y delega la regla
de negocio en `calculator.py`.
"""

import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.matches.schemas import Match
from src.matches.service import MatchService
from src.players.service import PlayerService
from src.statistics.calculator import EquipoEnTabla, PartidoParaTabla, calcular_clasificacion
from src.statistics.schemas import (
    DashboardSummary,
    PlayerStatistics,
    Standings,
    TopScorerRow,
    TopScorers,
)
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


class PlayerStatisticsService:
    """Estadísticas de jugador — spec 010 (FR-006 a FR-011).

    Al igual que `StandingsService`, no importa los modelos de `matches` ni
    `players`: consume sus servicios (Principio VIII) y deriva en lectura,
    nunca persiste un acumulado (FR-008).
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def obtener_ficha_jugador(self, player_id: uuid.UUID) -> PlayerStatistics:
        """FR-010. 404 `player_not_found` si el jugador no existe."""
        jugador = await PlayerService(self.db).obtener_jugador(player_id)
        if jugador is None:
            raise ErrorDeNegocio(
                code="player_not_found",
                message="El jugador no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        equipo = await TeamService(self.db).obtener_equipo(jugador.team_id)
        match_service = MatchService(self.db)
        goles = await match_service.goles_por_jugadores([jugador.id])
        partidos = await match_service.partidos_jugados_por_jugadores([jugador.id])
        return PlayerStatistics(
            player_id=jugador.id,
            player_name=jugador.name,
            team_id=jugador.team_id,
            team_name=equipo.name if equipo is not None else "",
            goals=goles.get(jugador.id, 0),
            matches_played=partidos.get(jugador.id, 0),
        )

    async def tabla_goleadores(self, league_id: uuid.UUID) -> TopScorers:
        """FR-009, NFR-003.

        Solo incluye jugadores con al menos un gol: es una tabla "de
        goleadores", no el listado completo de plantillas (no está
        contemplado explícitamente en la spec; ver checklist CHK015/CHK024).
        """
        equipos = await TeamService(self.db).listar_por_liga(league_id)  # valida la liga (404)
        equipos_por_id = {equipo.id: equipo for equipo in equipos}
        jugadores = await PlayerService(self.db).listar_por_equipos(list(equipos_por_id))
        match_service = MatchService(self.db)
        ids = [jugador.id for jugador in jugadores]
        goles = await match_service.goles_por_jugadores(ids)
        partidos = await match_service.partidos_jugados_por_jugadores(ids)
        goleadores = [jugador for jugador in jugadores if goles.get(jugador.id, 0) > 0]
        goleadores.sort(key=lambda j: (-goles[j.id], j.name.strip().lower(), str(j.id)))
        maximo = goles[goleadores[0].id] if goleadores else 0
        filas = [
            TopScorerRow(
                rank=posicion,
                player_id=jugador.id,
                player_name=jugador.name,
                team_id=jugador.team_id,
                team_name=equipos_por_id[jugador.team_id].name,
                goals=goles[jugador.id],
                matches_played=partidos.get(jugador.id, 0),
                is_top_scorer=goles[jugador.id] == maximo,
            )
            for posicion, jugador in enumerate(goleadores, start=1)
        ]
        return TopScorers(items=filas)