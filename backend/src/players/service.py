"""Reglas de negocio de jugadores (FR-001, FR-002, FR-003, FR-005)."""

import uuid

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.players.models import Player
from src.teams.service import TeamService, normalizar


class PlayerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _exigir_equipo_activo(self, team_id: uuid.UUID) -> None:
        """research.md §4 / Principio VIII: equipos vía TeamService, no su modelo."""
        equipo = await TeamService(self.db).obtener_equipo(team_id)
        if equipo is None or equipo.status != "active":
            raise ErrorDeNegocio(
                code="team_not_found",
                message="El equipo no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    async def _exigir_equipo(self, team_id: uuid.UUID) -> None:
        """Listado/detalle: el equipo debe existir (activo o inactivo)."""
        equipo = await TeamService(self.db).obtener_equipo(team_id)
        if equipo is None:
            raise ErrorDeNegocio(
                code="team_not_found",
                message="El equipo no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    async def crear_jugador(
        self,
        team_id: uuid.UUID,
        name: str,
        number: int | None,
        position: str | None,
        creado_por: uuid.UUID,
    ) -> Player:
        await self._exigir_equipo_activo(team_id)
        nombre = normalizar(name)

        # FR-003: unicidad de dorsal solo cuando está informado.
        if number is not None:
            existente = await self.db.execute(
                select(Player).where(Player.team_id == team_id, Player.number == number)
            )
            if existente.scalar_one_or_none() is not None:
                raise ErrorDeNegocio(
                    code="player_number_duplicate",
                    message="Ya existe un jugador con ese dorsal en este equipo.",
                    status_code=status.HTTP_409_CONFLICT,
                    field="number",
                )

        jugador = Player(
            team_id=team_id,
            name=nombre,
            number=number,
            position=position,
            created_by=creado_por,
        )
        self.db.add(jugador)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ErrorDeNegocio(
                code="player_number_duplicate",
                message="Ya existe un jugador con ese dorsal en este equipo.",
                status_code=status.HTTP_409_CONFLICT,
                field="number",
            ) from None

        await self.db.refresh(jugador)
        return jugador

    async def listar_jugadores(
        self, team_id: uuid.UUID, include_inactive: bool, page: int, page_size: int
    ) -> tuple[list[Player], int]:
        await self._exigir_equipo(team_id)

        # FR-005 / research.md §3: inactivos invisibles por defecto en listados.
        filtros = [Player.team_id == team_id]
        if not include_inactive:
            filtros.append(Player.status == "active")

        total = await self.db.scalar(select(func.count()).select_from(Player).where(*filtros)) or 0
        res = await self.db.execute(
            select(Player)
            .where(*filtros)
            .order_by(Player.created_at)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total

    async def obtener_jugador(self, player_id: uuid.UUID) -> Player | None:
        """Devuelve el jugador aunque esté inactivo (historial, research.md §3)."""
        return await self.db.get(Player, player_id)

    async def mapa_nombres(self, player_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
        """Interfaz de dominio para alineaciones (spec 010): id -> nombre, en lote."""
        if not player_ids:
            return {}
        res = await self.db.execute(select(Player.id, Player.name).where(Player.id.in_(player_ids)))
        return dict(res.all())

    async def listar_por_equipos(self, team_ids: list[uuid.UUID]) -> list[Player]:
        """Interfaz de dominio para estadísticas (spec 010).

        Sin paginación y con los inactivos incluidos (mismo criterio que
        `TeamService.listar_por_liga`): un jugador dado de baja conserva su
        historial de goles y partidos jugados.
        """
        if not team_ids:
            return []
        res = await self.db.execute(select(Player).where(Player.team_id.in_(team_ids)))
        return list(res.scalars())
