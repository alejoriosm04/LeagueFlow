"""Reglas de negocio de equipos (FR-001, FR-002, FR-003, FR-005)."""

import uuid

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.leagues.service import LeagueService
from src.teams.models import Team


def normalizar(texto: str) -> str:
    """Recorta y colapsa espacios sobrantes (data-model.md, research.md §2)."""
    return " ".join(texto.split())


class TeamService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _exigir_liga(self, league_id: uuid.UUID) -> None:
        """FR-003 / Principio VIII: se accede a ligas por su servicio, no por su modelo."""
        liga = await LeagueService(self.db).obtener_liga(league_id)
        if liga is None:
            raise ErrorDeNegocio(
                code="league_not_found",
                message="La liga no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    async def crear_equipo(
        self,
        league_id: uuid.UUID,
        name: str,
        crest_url: str | None,
        colors: str | None,
        creado_por: uuid.UUID,
    ) -> Team:
        await self._exigir_liga(league_id)
        nombre = normalizar(name)

        # FR-002: unicidad por liga, insensible a mayúsculas y espacios. La
        # comparación espeja el índice único funcional (league_id, lower(trim(name))).
        existente = await self.db.execute(
            select(Team).where(
                Team.league_id == league_id,
                func.lower(func.trim(Team.name)) == nombre.lower(),
            )
        )
        if existente.scalar_one_or_none() is not None:
            raise ErrorDeNegocio(
                code="team_name_duplicate",
                message="Ya existe un equipo con ese nombre en esta liga.",
                status_code=status.HTTP_409_CONFLICT,
                field="name",
            )

        equipo = Team(
            league_id=league_id,
            name=nombre,
            crest_url=crest_url,
            colors=colors,
            created_by=creado_por,
        )
        self.db.add(equipo)
        try:
            await self.db.commit()
        except IntegrityError:
            # Fallback ante la ventana de carrera (research.md de 002, mismo patrón).
            await self.db.rollback()
            raise ErrorDeNegocio(
                code="team_name_duplicate",
                message="Ya existe un equipo con ese nombre en esta liga.",
                status_code=status.HTTP_409_CONFLICT,
                field="name",
            ) from None

        await self.db.refresh(equipo)
        return equipo

    async def listar_equipos(
        self, league_id: uuid.UUID, include_inactive: bool, page: int, page_size: int
    ) -> tuple[list[Team], int]:
        await self._exigir_liga(league_id)

        # FR-005 / research.md §3: inactivos invisibles por defecto en listados.
        filtros = [Team.league_id == league_id]
        if not include_inactive:
            filtros.append(Team.status == "active")

        total = await self.db.scalar(select(func.count()).select_from(Team).where(*filtros)) or 0
        res = await self.db.execute(
            select(Team)
            .where(*filtros)
            .order_by(Team.created_at)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total

    async def listar_por_liga(self, league_id: uuid.UUID) -> list[Team]:
        """Interfaz de dominio para la clasificación (spec 008).

        Sin paginación y con los inactivos incluidos: quién ocupa fila lo
        decide el calculador, no esta consulta.
        """
        await self._exigir_liga(league_id)
        res = await self.db.execute(
            select(Team).where(Team.league_id == league_id).order_by(Team.created_at)
        )
        return list(res.scalars())

    async def obtener_equipo(self, team_id: uuid.UUID) -> Team | None:
        """Devuelve el equipo aunque esté inactivo (historial, research.md §3)."""
        return await self.db.get(Team, team_id)
