"""Reglas de negocio de grupos (FR-001 a FR-012)."""

import uuid

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.groups.models import GroupTeamMembership, LeagueGroup
from src.leagues.service import LeagueService
from src.teams.models import Team
from src.teams.service import TeamService


def normalizar(texto: str) -> str:
    """Recorta y colapsa espacios sobrantes (data-model.md, research.md)."""
    return " ".join(texto.split())


class GroupService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _exigir_liga(self, league_id: uuid.UUID) -> None:
        """Principio VIII: se accede a ligas por su servicio, no por su modelo."""
        liga = await LeagueService(self.db).obtener_liga(league_id)
        if liga is None:
            raise ErrorDeNegocio(
                code="league_not_found",
                message="La liga no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    async def _exigir_grupo(self, group_id: uuid.UUID) -> LeagueGroup:
        grupo = await self.db.get(LeagueGroup, group_id)
        if grupo is None:
            raise ErrorDeNegocio(
                code="group_not_found",
                message="El grupo no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return grupo

    async def _nombre_en_uso(
        self, league_id: uuid.UUID, nombre: str, excluir: uuid.UUID | None = None
    ) -> bool:
        """FR-002: unicidad por liga, insensible a mayúsculas y espacios."""
        consulta = select(LeagueGroup).where(
            LeagueGroup.league_id == league_id,
            func.lower(func.trim(LeagueGroup.name)) == nombre.lower(),
        )
        if excluir is not None:
            consulta = consulta.where(LeagueGroup.id != excluir)
        return (await self.db.execute(consulta)).scalar_one_or_none() is not None

    async def crear_grupo(
        self, league_id: uuid.UUID, name: str, position: int | None, creado_por: uuid.UUID
    ) -> LeagueGroup:
        await self._exigir_liga(league_id)
        nombre = normalizar(name)
        if await self._nombre_en_uso(league_id, nombre):
            raise ErrorDeNegocio(
                code="group_name_duplicate",
                message="Ya existe un grupo con ese nombre en esta liga.",
                status_code=status.HTTP_409_CONFLICT,
                field="name",
            )

        grupo = LeagueGroup(
            league_id=league_id, name=nombre, position=position, created_by=creado_por
        )
        self.db.add(grupo)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ErrorDeNegocio(
                code="group_name_duplicate",
                message="Ya existe un grupo con ese nombre en esta liga.",
                status_code=status.HTTP_409_CONFLICT,
                field="name",
            ) from None
        await self.db.refresh(grupo)
        return grupo

    async def renombrar_grupo(self, group_id: uuid.UUID, name: str) -> LeagueGroup:
        grupo = await self._exigir_grupo(group_id)
        nombre = normalizar(name)
        if await self._nombre_en_uso(grupo.league_id, nombre, excluir=group_id):
            raise ErrorDeNegocio(
                code="group_name_duplicate",
                message="Ya existe un grupo con ese nombre en esta liga.",
                status_code=status.HTTP_409_CONFLICT,
                field="name",
            )
        grupo.name = nombre
        await self.db.commit()
        await self.db.refresh(grupo)
        return grupo

    async def eliminar_grupo(self, group_id: uuid.UUID) -> None:
        """FR-004: borra el grupo y sus membresías (CASCADE), nunca los equipos."""
        grupo = await self._exigir_grupo(group_id)
        await self.db.delete(grupo)
        await self.db.commit()

    async def asignar_equipo(
        self, group_id: uuid.UUID, team_id: uuid.UUID, creado_por: uuid.UUID
    ) -> GroupTeamMembership:
        grupo = await self._exigir_grupo(group_id)

        equipo = await TeamService(self.db).obtener_equipo(team_id)
        if equipo is None:
            raise ErrorDeNegocio(
                code="team_not_found",
                message="El equipo no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if equipo.league_id != grupo.league_id:  # FR-008
            raise ErrorDeNegocio(
                code="team_not_found_in_league",
                message="El equipo no pertenece a la liga del grupo.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if equipo.status != "active":  # FR-011
            raise ErrorDeNegocio(
                code="team_inactive",
                message="El equipo está inactivo y no puede asignarse a un grupo.",
                status_code=status.HTTP_409_CONFLICT,
            )

        # FR-007: a lo sumo un grupo (respaldado por UNIQUE team_id en la base).
        existente = await self.db.execute(
            select(GroupTeamMembership).where(GroupTeamMembership.team_id == team_id)
        )
        if existente.scalar_one_or_none() is not None:
            raise ErrorDeNegocio(
                code="team_already_in_group",
                message="El equipo ya pertenece a un grupo de esta liga.",
                status_code=status.HTTP_409_CONFLICT,
            )

        membresia = GroupTeamMembership(group_id=group_id, team_id=team_id, created_by=creado_por)
        self.db.add(membresia)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ErrorDeNegocio(
                code="team_already_in_group",
                message="El equipo ya pertenece a un grupo de esta liga.",
                status_code=status.HTTP_409_CONFLICT,
            ) from None
        await self.db.refresh(membresia)
        return membresia

    async def desasignar_equipo(self, group_id: uuid.UUID, team_id: uuid.UUID) -> None:
        """FR-006: quita la membresía; si no existe, el grupo es el que no se encuentra."""
        await self._exigir_grupo(group_id)
        membresia = (
            await self.db.execute(
                select(GroupTeamMembership).where(
                    GroupTeamMembership.group_id == group_id,
                    GroupTeamMembership.team_id == team_id,
                )
            )
        ).scalar_one_or_none()
        if membresia is None:
            raise ErrorDeNegocio(
                code="group_not_found",
                message="El equipo no está en este grupo.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        await self.db.delete(membresia)
        await self.db.commit()

    async def listar_grupos(
        self, league_id: uuid.UUID
    ) -> list[tuple[LeagueGroup, list[tuple[uuid.UUID, str, str]]]]:
        """FR-009: grupos de una liga con su composición (FR-012 incluye inactivos)."""
        await self._exigir_liga(league_id)
        grupos = list(
            (
                await self.db.execute(
                    select(LeagueGroup)
                    .where(LeagueGroup.league_id == league_id)
                    .order_by(LeagueGroup.position.asc().nulls_last(), LeagueGroup.name.asc())
                )
            ).scalars()
        )
        if not grupos:
            return []

        ids = [g.id for g in grupos]
        filas = await self.db.execute(
            select(GroupTeamMembership.group_id, Team.id, Team.name, Team.status)
            .join(Team, Team.id == GroupTeamMembership.team_id)
            .where(GroupTeamMembership.group_id.in_(ids))
        )
        por_grupo: dict[uuid.UUID, list[tuple[uuid.UUID, str, str]]] = {g.id: [] for g in grupos}
        for group_id, team_id, nombre, estado in filas:
            por_grupo[group_id].append((team_id, nombre, estado))

        return [(g, por_grupo[g.id]) for g in grupos]
