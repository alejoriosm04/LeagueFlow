"""Reglas de negocio de ligas (FR-001, FR-002, FR-004)."""

import uuid

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.leagues.models import League


def normalizar(texto: str) -> str:
    """Recorta y colapsa espacios sobrantes (research.md §2, data-model.md).

    '  Interfacultades   2026  ' -> 'Interfacultades 2026'. Se preserva la
    capitalización original para mostrar.
    """
    return " ".join(texto.split())


class LeagueService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def crear_liga(
        self, name: str, season: str, description: str | None, creado_por: uuid.UUID
    ) -> League:
        nombre = normalizar(name)
        temporada = normalizar(season)

        # FR-002: unicidad insensible a mayúsculas y espacios (research.md §2).
        # La comparación espeja el índice único funcional para que la base de
        # datos pueda usar ese índice en vez de un barrido completo.
        existente = await self.db.execute(
            select(League).where(
                func.lower(func.trim(League.name)) == nombre.lower(),
                func.lower(func.trim(League.season)) == temporada.lower(),
            )
        )
        if existente.scalar_one_or_none() is not None:
            raise ErrorDeNegocio(
                code="league_already_exists",
                message="Ya existe una liga con ese nombre y temporada.",
                status_code=status.HTTP_409_CONFLICT,
                field="name",
            )

        liga = League(
            name=nombre,
            season=temporada,
            description=description,
            created_by=creado_por,
        )
        self.db.add(liga)
        try:
            await self.db.commit()
        except IntegrityError:
            # research.md §1: la comprobación previa deja una ventana de carrera
            # entre dos organizadores; el índice único la cierra y se traduce al
            # mismo 409 legible del camino normal.
            await self.db.rollback()
            raise ErrorDeNegocio(
                code="league_already_exists",
                message="Ya existe una liga con ese nombre y temporada.",
                status_code=status.HTTP_409_CONFLICT,
                field="name",
            ) from None

        await self.db.refresh(liga)
        return liga

    async def listar_ligas(self, page: int, page_size: int) -> tuple[list[League], int]:
        total = await self.db.scalar(select(func.count()).select_from(League)) or 0
        res = await self.db.execute(
            select(League)
            .order_by(League.created_at)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total

    async def obtener_liga(self, liga_id: uuid.UUID) -> League | None:
        return await self.db.get(League, liga_id)
