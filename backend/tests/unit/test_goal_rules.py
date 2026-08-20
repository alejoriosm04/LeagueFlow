"""Reglas de atribución de goles y consistencia con el marcador — spec 009.

Funciones puras: se prueban sin base de datos ni HTTP. FR-003 usa un doble del
puerto de alineación, porque `MatchLineup` es entidad de la spec 010.
"""

import uuid

import pytest
from src.core.errors import ErrorDeNegocio
from src.matches.goal_rules import GolRegistrado, calcular_consistencia, validar_registro_de_gol

LOCAL = uuid.uuid4()
VISITANTE = uuid.uuid4()
AJENO = uuid.uuid4()


def validar(**cambios):
    argumentos = {
        "match_status": "finished",
        "home_team_id": LOCAL,
        "away_team_id": VISITANTE,
        "player_id": uuid.uuid4(),
        "player_team_id": LOCAL,
        "alineados": None,
    }
    argumentos.update(cambios)
    return validar_registro_de_gol(**argumentos)


def codigo_de(excinfo) -> str:
    return excinfo.value.code


# --- FR-002: pertenencia al partido ----------------------------------------


def test_acepta_al_jugador_del_equipo_local():
    assert validar(player_team_id=LOCAL) is None


def test_acepta_al_jugador_del_equipo_visitante():
    assert validar(player_team_id=VISITANTE) is None


def test_rechaza_al_jugador_de_un_equipo_ajeno():
    """AS2 / SC-002."""
    with pytest.raises(ErrorDeNegocio) as exc:
        validar(player_team_id=AJENO)
    assert codigo_de(exc) == "player_not_in_match"
    assert exc.value.status_code == 409


# --- FR-003: alineación (puerto doblado) -----------------------------------


def test_sin_alineacion_registrada_acepta_a_cualquier_jugador_del_partido():
    """Hoy siempre es este caso: el puerto devuelve None hasta la spec 010."""
    assert validar(alineados=None) is None


def test_con_alineacion_acepta_al_jugador_que_figura():
    jugador = uuid.uuid4()
    assert validar(player_id=jugador, alineados={jugador, uuid.uuid4()}) is None


def test_con_alineacion_rechaza_al_jugador_que_no_figura():
    """AS3 — cobertura unitaria; la de integración corresponde a la spec 010."""
    with pytest.raises(ErrorDeNegocio) as exc:
        validar(player_id=uuid.uuid4(), alineados={uuid.uuid4()})
    assert codigo_de(exc) == "player_not_in_lineup"
    assert exc.value.status_code == 409


def test_alineacion_vacia_no_es_lo_mismo_que_ausente():
    """Un set vacío significa 'alineación registrada y sin jugadores'."""
    with pytest.raises(ErrorDeNegocio):
        validar(alineados=set())


# --- Estado del partido (research.md §3) -----------------------------------


@pytest.mark.parametrize("estado", ["finished", "in_progress"])
def test_acepta_partidos_con_juego(estado):
    assert validar(match_status=estado) is None


@pytest.mark.parametrize("estado", ["scheduled", "cancelled"])
def test_rechaza_partidos_sin_juego(estado):
    with pytest.raises(ErrorDeNegocio) as exc:
        validar(match_status=estado)
    assert codigo_de(exc) == "match_not_playable"
    assert exc.value.status_code == 409


def test_el_estado_se_valida_antes_que_la_pertenencia():
    """Un partido cancelado se rechaza por su estado, no por el jugador."""
    with pytest.raises(ErrorDeNegocio) as exc:
        validar(match_status="cancelled", player_team_id=AJENO)
    assert codigo_de(exc) == "match_not_playable"


# --- FR-005: consistencia con el marcador ----------------------------------


def goles(local: int, visitante: int) -> list[GolRegistrado]:
    return [GolRegistrado(team_id=LOCAL) for _ in range(local)] + [
        GolRegistrado(team_id=VISITANTE) for _ in range(visitante)
    ]


def consistencia(eventos, home_score, away_score):
    return calcular_consistencia(
        eventos=eventos,
        home_team_id=LOCAL,
        away_team_id=VISITANTE,
        home_score=home_score,
        away_score=away_score,
    )


def test_consistencia_cuando_los_goles_cuadran():
    resultado = consistencia(goles(3, 1), 3, 1)
    assert (resultado.home_goals_recorded, resultado.away_goals_recorded) == (3, 1)
    assert resultado.matches_official is True


def test_consistencia_cuando_faltan_goles_por_registrar():
    """AS4: se advierte, no se bloquea."""
    resultado = consistencia(goles(2, 0), 3, 1)
    assert (resultado.home_goals_recorded, resultado.away_goals_recorded) == (2, 0)
    assert resultado.matches_official is False


def test_consistencia_cuando_sobran_goles_registrados():
    """Edge case: más goles atribuidos que los del marcador oficial."""
    assert consistencia(goles(4, 1), 3, 1).matches_official is False


def test_consistencia_es_nula_sin_marcador_oficial():
    """Un partido in_progress no tiene contra qué contrastar."""
    resultado = consistencia(goles(1, 0), None, None)
    assert resultado.home_goals_recorded == 1
    assert resultado.matches_official is None


def test_consistencia_de_un_partido_sin_eventos():
    resultado = consistencia([], 3, 1)
    assert (resultado.home_goals_recorded, resultado.away_goals_recorded) == (0, 0)
    assert resultado.matches_official is False


def test_partido_sin_goles_y_marcador_cero_cuadra():
    assert consistencia([], 0, 0).matches_official is True
