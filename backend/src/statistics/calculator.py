"""StandingsCalculator — `MatchResult -> StandingsCalculator -> Standings`.

Función pura: no toca la base de datos ni la sesión HTTP. Aquí viven las reglas
de FR-001, FR-003, FR-005, FR-006 y FR-007, y aquí se prueban
(`tests/unit/test_standings_calculator.py`).
"""

import uuid
from dataclasses import dataclass

from src.statistics.schemas import StandingsRow


@dataclass(frozen=True)
class ScoringRules:
    """Única fuente de verdad de la puntuación de la clasificación (FR-003).

    Punto de extensión deliberado (enunciado §12): si una victoria, un empate o
    una derrota pasaran a valer otra cantidad, se cambia aquí y en ningún otro
    sitio. Por defecto, los valores estándar del fútbol: 3 / 1 / 0.
    """

    win_points: int = 3
    draw_points: int = 1
    loss_points: int = 0


SCORING: ScoringRules = ScoringRules()


@dataclass(frozen=True)
class EquipoEnTabla:
    """Equipo candidato a ocupar una fila. `activo` es Team.status == 'active'."""

    id: uuid.UUID
    name: str
    activo: bool


@dataclass(frozen=True)
class PartidoParaTabla:
    """Partido con su estado. Solo `finished` contribuye (FR-001, FR-007)."""

    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    home_score: int | None
    away_score: int | None
    status: str


@dataclass
class _Acumulado:
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    def anotar(self, propios: int, rivales: int) -> None:
        self.played += 1
        self.goals_for += propios
        self.goals_against += rivales
        if propios > rivales:
            self.won += 1
        elif propios == rivales:
            self.drawn += 1
        else:
            self.lost += 1

    @property
    def points(self) -> int:
        """FR-003: 3 por victoria, 1 por empate, 0 por derrota."""
        return (
            self.won * SCORING.win_points
            + self.drawn * SCORING.draw_points
            + self.lost * SCORING.loss_points
        )

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against


def calcular_clasificacion(
    equipos: list[EquipoEnTabla], partidos: list[PartidoParaTabla]
) -> list[StandingsRow]:
    """Devuelve la tabla ordenada y numerada de una liga.

    Ocupan fila los equipos activos y los inactivos con al menos un partido
    finalizado: omitir a un inactivo con historial dejaría sin explicación los
    puntos que sus rivales le ganaron (Assumption de la spec).
    """
    acumulados: dict[uuid.UUID, _Acumulado] = {equipo.id: _Acumulado() for equipo in equipos}

    for partido in partidos:
        # El servicio ya consulta solo partidos finalizados; la regla se
        # comprueba igualmente aquí porque es de esta función, no del SQL.
        if partido.status != "finished":
            continue
        if partido.home_score is None or partido.away_score is None:
            continue
        local = acumulados.get(partido.home_team_id)
        visitante = acumulados.get(partido.away_team_id)
        if local is None or visitante is None:
            continue
        local.anotar(partido.home_score, partido.away_score)
        visitante.anotar(partido.away_score, partido.home_score)

    con_fila = [e for e in equipos if e.activo or acumulados[e.id].played > 0]

    # FR-005 (puntos, GD, GF) y FR-006 (nombre normalizado). El id cierra el
    # orden para que sea total y no dependa del origen de los datos.
    ordenados = sorted(
        con_fila,
        key=lambda e: (
            -acumulados[e.id].points,
            -acumulados[e.id].goal_difference,
            -acumulados[e.id].goals_for,
            e.name.strip().lower(),
            str(e.id),
        ),
    )

    return [
        StandingsRow(
            position=posicion,
            team_id=equipo.id,
            team_name=equipo.name,
            played=acumulados[equipo.id].played,
            won=acumulados[equipo.id].won,
            drawn=acumulados[equipo.id].drawn,
            lost=acumulados[equipo.id].lost,
            goals_for=acumulados[equipo.id].goals_for,
            goals_against=acumulados[equipo.id].goals_against,
            goal_difference=acumulados[equipo.id].goal_difference,
            points=acumulados[equipo.id].points,
        )
        for posicion, equipo in enumerate(ordenados, start=1)
    ]


__all__ = ["EquipoEnTabla", "PartidoParaTabla", "ScoringRules", "SCORING", "calcular_clasificacion"]
