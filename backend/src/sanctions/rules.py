"""Reglas de ficha disciplinaria — spec 014.

Funciones puras: se prueban sin base de datos ni HTTP.
"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TarjetaRegistrada:
    type: str
    match_id: uuid.UUID


def calcular_ficha_disciplinaria(
    tarjetas: list[TarjetaRegistrada],
) -> tuple[int, int, bool]:
    """FR-007: conteos y suspensión derivados en lectura."""
    amarillas = sum(1 for t in tarjetas if t.type == "YELLOW_CARD")
    rojas = sum(1 for t in tarjetas if t.type == "RED_CARD")
    partidos_con_amarilla = {t.match_id for t in tarjetas if t.type == "YELLOW_CARD"}
    suspendido = rojas >= 1 or len(partidos_con_amarilla) >= 2
    return amarillas, rojas, suspendido


__all__ = ["TarjetaRegistrada", "calcular_ficha_disciplinaria"]
