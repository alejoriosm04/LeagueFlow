"""Reglas de alineación — spec 010 (FR-002, FR-003).

Funciones puras: se prueban sin base de datos ni HTTP, igual que
`test_goal_rules.py`.
"""

import uuid

import pytest
from src.core.errors import ErrorDeNegocio
from src.matches.lineup_rules import (
    JugadorCandidato,
    detectar_conflicto_con_eventos,
    validar_lado_de_alineacion,
)

LOCAL = uuid.uuid4()
VISITANTE = uuid.uuid4()
AJENO = uuid.uuid4()


def codigo_de(excinfo) -> str:
    return excinfo.value.code


# --- FR-002: pertenencia al equipo del lado declarado -----------------------


def test_acepta_jugadores_del_equipo_local_en_el_lado_local():
    jugador = uuid.uuid4()
    validar_lado_de_alineacion(
        jugadores=[JugadorCandidato(id=jugador, team_id=LOCAL)],
        equipo_id=LOCAL,
        otro_equipo_id=VISITANTE,
    )  # no lanza


def test_jugador_inexistente_devuelve_404():
    with pytest.raises(ErrorDeNegocio) as exc:
        validar_lado_de_alineacion(
            jugadores=[None],
            equipo_id=LOCAL,
            otro_equipo_id=VISITANTE,
        )
    assert codigo_de(exc) == "player_not_found"
    assert exc.value.status_code == 404


def test_jugador_de_un_tercer_equipo_se_rechaza():
    """AS2: jugador que no pertenece a ninguno de los dos equipos del partido."""
    jugador = uuid.uuid4()
    with pytest.raises(ErrorDeNegocio) as exc:
        validar_lado_de_alineacion(
            jugadores=[JugadorCandidato(id=jugador, team_id=AJENO)],
            equipo_id=LOCAL,
            otro_equipo_id=VISITANTE,
        )
    assert codigo_de(exc) == "player_not_in_match"
    assert exc.value.status_code == 409


def test_jugador_del_equipo_rival_declarado_en_el_lado_equivocado_se_rechaza():
    """Pertenece al partido, pero no al lado que lo declara."""
    jugador = uuid.uuid4()
    with pytest.raises(ErrorDeNegocio) as exc:
        validar_lado_de_alineacion(
            jugadores=[JugadorCandidato(id=jugador, team_id=VISITANTE)],
            equipo_id=LOCAL,
            otro_equipo_id=VISITANTE,
        )
    assert codigo_de(exc) == "player_not_in_team"
    assert exc.value.status_code == 409


def test_lado_vacio_no_lanza():
    validar_lado_de_alineacion(jugadores=[], equipo_id=LOCAL, otro_equipo_id=VISITANTE)


# --- FR-003: coherencia con goles ya registrados -----------------------------


def test_sin_goleadores_previos_no_hay_conflicto():
    detectar_conflicto_con_eventos(jugadores_con_gol=set(), nueva_alineacion={uuid.uuid4()})


def test_goleador_presente_en_la_nueva_alineacion_no_es_conflicto():
    goleador = uuid.uuid4()
    detectar_conflicto_con_eventos(
        jugadores_con_gol={goleador}, nueva_alineacion={goleador, uuid.uuid4()}
    )


def test_excluir_a_un_goleador_es_rechazado():
    goleador = uuid.uuid4()
    with pytest.raises(ErrorDeNegocio) as exc:
        detectar_conflicto_con_eventos(
            jugadores_con_gol={goleador}, nueva_alineacion={uuid.uuid4()}
        )
    assert codigo_de(exc) == "lineup_conflicts_with_events"
    assert exc.value.status_code == 409
    assert str(goleador) in exc.value.message


def test_vaciar_la_alineacion_con_goleadores_previos_es_rechazado():
    """Estado `missing` (FR-004) no puede alcanzarse borrando goleadores existentes."""
    goleador = uuid.uuid4()
    with pytest.raises(ErrorDeNegocio):
        detectar_conflicto_con_eventos(jugadores_con_gol={goleador}, nueva_alineacion=set())
