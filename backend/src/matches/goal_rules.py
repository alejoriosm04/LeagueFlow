"""Reglas de atribución de goles y consistencia con el marcador — spec 009.

Funciones puras: no tocan la base de datos ni la sesión HTTP. Aquí viven
FR-002, FR-003 y FR-005, y aquí se prueban
(`tests/unit/test_goal_rules.py`). El servicio solo aporta los datos.
"""

import uuid
from dataclasses import dataclass

from fastapi import status

from src.core.errors import ErrorDeNegocio
from src.matches.schemas import EventConsistency

# research.md §3: solo un partido en juego o ya jugado admite eventos.
ESTADOS_CON_JUEGO = ("finished", "in_progress")


@dataclass(frozen=True)
class GolRegistrado:
    """Lo único que la consistencia necesita saber de un evento."""

    team_id: uuid.UUID


def validar_registro_de_gol(
    *,
    match_status: str,
    home_team_id: uuid.UUID,
    away_team_id: uuid.UUID,
    player_id: uuid.UUID,
    player_team_id: uuid.UUID,
    alineados: set[uuid.UUID] | None,
) -> None:
    """Lanza `ErrorDeNegocio` si el gol no puede atribuirse.

    `alineados` es `None` cuando el partido no tiene alineación registrada, y
    entonces FR-003 no aplica. Un conjunto vacío significa lo contrario:
    alineación registrada y sin jugadores, así que rechaza a todos.
    """
    if match_status not in ESTADOS_CON_JUEGO:
        raise ErrorDeNegocio(
            code="match_not_playable",
            message="Solo un partido en curso o finalizado admite goles.",
            status_code=status.HTTP_409_CONFLICT,
        )

    # FR-002
    if player_team_id not in (home_team_id, away_team_id):
        raise ErrorDeNegocio(
            code="player_not_in_match",
            message="El jugador no pertenece a ninguno de los dos equipos del partido.",
            status_code=status.HTTP_409_CONFLICT,
        )

    # FR-003
    if alineados is not None and player_id not in alineados:
        raise ErrorDeNegocio(
            code="player_not_in_lineup",
            message="El jugador no figura en la alineación registrada del partido.",
            status_code=status.HTTP_409_CONFLICT,
        )


def calcular_consistencia(
    *,
    eventos: list[GolRegistrado],
    home_team_id: uuid.UUID,
    away_team_id: uuid.UUID,
    home_score: int | None,
    away_score: int | None,
) -> EventConsistency:
    """FR-005: contrasta los goles atribuidos con el marcador oficial.

    `matches_official` es `None` mientras el partido no tenga marcador: no hay
    nada contra qué contrastar. El marcador oficial nunca se modifica aquí.
    """
    local = sum(1 for evento in eventos if evento.team_id == home_team_id)
    visitante = sum(1 for evento in eventos if evento.team_id == away_team_id)

    if home_score is None or away_score is None:
        cuadra = None
    else:
        cuadra = (local, visitante) == (home_score, away_score)

    return EventConsistency(
        home_goals_recorded=local,
        away_goals_recorded=visitante,
        home_score=home_score,
        away_score=away_score,
        matches_official=cuadra,
    )


__all__ = ["GolRegistrado", "calcular_consistencia", "validar_registro_de_gol"]
