"""Orquestación de la ficha disciplinaria — spec 014.

Consume la interfaz pública de `MatchService` y `PlayerService`; no importa
modelos ORM de matches (Principio VIII).
"""

import uuid

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.errors import ErrorDeNegocio
from src.matches.service import MatchService
from src.players.service import PlayerService
from src.sanctions.rules import TarjetaRegistrada, calcular_ficha_disciplinaria
from src.sanctions.schemas import PlayerDiscipline


class SanctionsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def obtener_ficha(self, player_id: uuid.UUID) -> PlayerDiscipline:
        jugador = await PlayerService(self.db).obtener_jugador(player_id)
        if jugador is None:
            raise ErrorDeNegocio(
                code="player_not_found",
                message="El jugador no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        filas = await MatchService(self.db).tarjetas_por_jugador(player_id)
        tarjetas = [TarjetaRegistrada(type=tipo, match_id=mid) for tipo, mid in filas]
        amarillas, rojas, suspendido = calcular_ficha_disciplinaria(tarjetas)
        return PlayerDiscipline(
            player_id=player_id,
            yellow_cards=amarillas,
            red_cards=rojas,
            suspended=suspendido,
        )
