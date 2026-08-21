"""Reglas de negocio de alineaciones — spec 010 (FR-002, FR-003).

Funciones puras: no tocan la base de datos ni la sesión HTTP. Aquí vive la
validación de pertenencia de cada jugador a su equipo del partido y la
detección de conflicto con goles ya registrados; el servicio solo aporta los
datos (mismo patrón que `matches/goal_rules.py`).
"""

import uuid
from dataclasses import dataclass

from fastapi import status

from src.core.errors import ErrorDeNegocio


@dataclass(frozen=True)
class JugadorCandidato:
    """Lo único que la validación de alineación necesita saber de un jugador."""

    id: uuid.UUID
    team_id: uuid.UUID


def validar_lado_de_alineacion(
    *,
    jugadores: list[JugadorCandidato | None],
    equipo_id: uuid.UUID,
    otro_equipo_id: uuid.UUID,
) -> None:
    """Valida un lado (home o away) de `UpsertLineupInput`.

    Cada elemento de `jugadores` es `None` cuando el id solicitado no existe
    como jugador (404 `player_not_found`). FR-002: el jugador debe pertenecer
    a alguno de los dos equipos del partido (409 `player_not_in_match`) y,
    dentro de eso, al equipo del lado que lo declara (409 `player_not_in_team`
    cuando pertenece al equipo rival del mismo partido).
    """
    for jugador in jugadores:
        if jugador is None:
            raise ErrorDeNegocio(
                code="player_not_found",
                message="El jugador no existe.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if jugador.team_id not in (equipo_id, otro_equipo_id):
            raise ErrorDeNegocio(
                code="player_not_in_match",
                message="El jugador no pertenece a ninguno de los dos equipos del partido.",
                status_code=status.HTTP_409_CONFLICT,
            )
        if jugador.team_id != equipo_id:
            raise ErrorDeNegocio(
                code="player_not_in_team",
                message="El jugador pertenece al equipo rival de este partido.",
                status_code=status.HTTP_409_CONFLICT,
            )


def detectar_conflicto_con_eventos(
    *, jugadores_con_gol: set[uuid.UUID], nueva_alineacion: set[uuid.UUID]
) -> None:
    """FR-003: rechaza excluir de la alineación a un jugador con gol ya registrado."""
    conflicto = jugadores_con_gol - nueva_alineacion
    if conflicto:
        ids = ", ".join(str(id_) for id_ in sorted(conflicto, key=str))
        raise ErrorDeNegocio(
            code="lineup_conflicts_with_events",
            message=(
                "No se puede excluir de la alineación a jugadores con goles ya "
                f"registrados en este partido: {ids}."
            ),
            status_code=status.HTTP_409_CONFLICT,
        )


__all__ = [
    "JugadorCandidato",
    "detectar_conflicto_con_eventos",
    "validar_lado_de_alineacion",
]
