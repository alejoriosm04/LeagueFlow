"""Reglas de negocio de partidos (FR-001, FR-002, FR-003, FR-005)."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from fastapi import status
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.leagues.service import LeagueService
from src.matches.goal_rules import (
    GolRegistrado,
    calcular_consistencia,
    validar_registro_de_evento,
)
from src.matches.lineup_rules import (
    JugadorCandidato,
    detectar_conflicto_con_eventos,
    validar_lado_de_alineacion,
)
from src.matches.models import Match, MatchEvent, MatchLineup, ResultCorrectionRequest
from src.matches.schemas import (
    EventConsistency,
    EventType,
    LineupPlayer,
    MatchLineupView,
    MatchStatus,
)
from src.players.service import PlayerService
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

    # --- Eventos de partido (spec 009) -------------------------------------

    async def _exigir_partido(self, match_id: uuid.UUID) -> Match:
        partido = await self.db.get(Match, match_id)
        if partido is None:
            raise ErrorDeNegocio(
                code="match_not_found",
                message="El partido no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return partido

    async def jugadores_alineados(self, match_id: uuid.UUID) -> set[uuid.UUID] | None:
        """Puerto de lectura de la alineación (FR-003 de la spec 009, cerrado en 010).

        `None` significa "sin alineación registrada" (FR-003 de 009 no aplica);
        un conjunto —vacío incluido— significa que sí existe alineación.
        data-model.md de esta HU define `lineup_status` por existencia de filas
        en `match_lineups`, así que una alineación guardada explícitamente vacía
        es indistinguible de "nunca registrada": ambas devuelven `None` aquí.
        """
        await self._exigir_partido(match_id)
        res = await self.db.execute(
            select(MatchLineup.player_id).where(MatchLineup.match_id == match_id)
        )
        alineados = set(res.scalars())
        return alineados or None

    # --- Alineaciones (spec 010) --------------------------------------------

    async def guardar_alineacion(
        self,
        match_id: uuid.UUID,
        home_player_ids: list[uuid.UUID],
        away_player_ids: list[uuid.UUID],
        actor_id: uuid.UUID,
    ) -> MatchLineupView:
        """FR-001, FR-002, FR-003: reemplazo completo idempotente."""
        partido = await self._exigir_partido(match_id)
        player_service = PlayerService(self.db)

        async def _candidatos(ids: list[uuid.UUID]) -> list[JugadorCandidato | None]:
            candidatos: list[JugadorCandidato | None] = []
            for player_id in ids:
                jugador = await player_service.obtener_jugador(player_id)
                candidatos.append(
                    JugadorCandidato(id=jugador.id, team_id=jugador.team_id)
                    if jugador is not None
                    else None
                )
            return candidatos

        validar_lado_de_alineacion(
            jugadores=await _candidatos(home_player_ids),
            equipo_id=partido.home_team_id,
            otro_equipo_id=partido.away_team_id,
        )
        validar_lado_de_alineacion(
            jugadores=await _candidatos(away_player_ids),
            equipo_id=partido.away_team_id,
            otro_equipo_id=partido.home_team_id,
        )

        nueva_alineacion = set(home_player_ids) | set(away_player_ids)
        res = await self.db.execute(
            select(MatchEvent.player_id)
            .where(MatchEvent.match_id == match_id, MatchEvent.type == "GOAL")
            .distinct()
        )
        detectar_conflicto_con_eventos(
            jugadores_con_gol=set(res.scalars()), nueva_alineacion=nueva_alineacion
        )

        await self.db.execute(delete(MatchLineup).where(MatchLineup.match_id == match_id))
        filas = [
            MatchLineup(
                match_id=match_id, team_id=partido.home_team_id, player_id=pid, created_by=actor_id
            )
            for pid in home_player_ids
        ] + [
            MatchLineup(
                match_id=match_id, team_id=partido.away_team_id, player_id=pid, created_by=actor_id
            )
            for pid in away_player_ids
        ]
        self.db.add_all(filas)
        await self.db.commit()
        return await self.obtener_alineacion(match_id)

    async def obtener_alineacion(self, match_id: uuid.UUID) -> MatchLineupView:
        """FR-004: lectura pública. `status` se deriva de la existencia de filas."""
        partido = await self._exigir_partido(match_id)
        res = await self.db.execute(
            select(MatchLineup)
            .where(MatchLineup.match_id == match_id)
            .order_by(MatchLineup.team_id, MatchLineup.player_id)
        )
        filas = list(res.scalars())
        if not filas:
            return MatchLineupView(
                match_id=match_id, status="missing", home_players=[], away_players=[]
            )

        nombres = await PlayerService(self.db).mapa_nombres([fila.player_id for fila in filas])

        def _armar(equipo_id: uuid.UUID) -> list[LineupPlayer]:
            jugadores = [
                LineupPlayer(
                    player_id=fila.player_id,
                    player_name=nombres.get(fila.player_id, ""),
                    team_id=fila.team_id,
                )
                for fila in filas
                if fila.team_id == equipo_id
            ]
            return sorted(
                jugadores, key=lambda j: (j.player_name.strip().lower(), str(j.player_id))
            )

        return MatchLineupView(
            match_id=match_id,
            status="registered",
            home_players=_armar(partido.home_team_id),
            away_players=_armar(partido.away_team_id),
        )

    async def goles_por_jugadores(self, player_ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, int]:
        """Fuente de estadísticas (spec 010, FR-006): goles por jugador, desde eventos."""
        if not player_ids:
            return {}
        res = await self.db.execute(
            select(MatchEvent.player_id, func.count())
            .where(MatchEvent.type == "GOAL", MatchEvent.player_id.in_(player_ids))
            .group_by(MatchEvent.player_id)
        )
        return dict(res.all())

    async def partidos_jugados_por_jugadores(
        self, player_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        """Fuente de estadísticas (spec 010, FR-007): partidos finalizados por jugador."""
        if not player_ids:
            return {}
        res = await self.db.execute(
            select(MatchLineup.player_id, func.count(func.distinct(MatchLineup.match_id)))
            .join(Match, Match.id == MatchLineup.match_id)
            .where(MatchLineup.player_id.in_(player_ids), Match.status == "finished")
            .group_by(MatchLineup.player_id)
        )
        return dict(res.all())

    async def registrar_evento(
        self,
        match_id: uuid.UUID,
        player_id: uuid.UUID,
        minute: int,
        tipo: EventType,
        creado_por: uuid.UUID,
    ) -> MatchEvent:
        """FR-001 (009/014). El equipo se deriva del jugador (research.md §4)."""
        partido = await self._exigir_partido(match_id)

        jugador = await PlayerService(self.db).obtener_jugador(player_id)
        if jugador is None:
            raise ErrorDeNegocio(
                code="player_not_found",
                message="El jugador no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        validar_registro_de_evento(
            match_status=partido.status,
            home_team_id=partido.home_team_id,
            away_team_id=partido.away_team_id,
            player_id=jugador.id,
            player_team_id=jugador.team_id,
            alineados=await self.jugadores_alineados(match_id),
        )

        evento = MatchEvent(
            match_id=partido.id,
            type=tipo,
            player_id=jugador.id,
            team_id=jugador.team_id,
            minute=minute,
            created_by=creado_por,
        )
        self.db.add(evento)
        await self.db.commit()
        await self.db.refresh(evento)
        return evento

    async def registrar_gol(
        self,
        match_id: uuid.UUID,
        player_id: uuid.UUID,
        minute: int,
        tipo: EventType,
        creado_por: uuid.UUID,
    ) -> MatchEvent:
        """Alias de `registrar_evento` para la spec 009."""
        return await self.registrar_evento(match_id, player_id, minute, tipo, creado_por)

    async def tarjetas_por_jugador(
        self, player_id: uuid.UUID
    ) -> list[tuple[str, uuid.UUID]]:
        """Puerto de lectura para sanctions/ (spec 014): tipo y partido de cada tarjeta."""
        res = await self.db.execute(
            select(MatchEvent.type, MatchEvent.match_id).where(
                MatchEvent.player_id == player_id,
                MatchEvent.type.in_(("YELLOW_CARD", "RED_CARD")),
            )
        )
        return [(fila.type, fila.match_id) for fila in res.all()]

    async def listar_eventos(
        self, match_id: uuid.UUID
    ) -> tuple[list[MatchEvent], EventConsistency]:
        """Listado público más la advertencia de FR-005."""
        partido = await self._exigir_partido(match_id)
        res = await self.db.execute(
            select(MatchEvent)
            .where(MatchEvent.match_id == match_id)
            .order_by(MatchEvent.minute.asc(), MatchEvent.created_at.asc())
        )
        eventos = list(res.scalars())
        consistencia = calcular_consistencia(
            eventos=[GolRegistrado(team_id=e.team_id) for e in eventos if e.type == "GOAL"],
            home_team_id=partido.home_team_id,
            away_team_id=partido.away_team_id,
            home_score=partido.home_score,
            away_score=partido.away_score,
        )
        return eventos, consistencia

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
