"""Reglas de registro de tarjetas — spec 014."""

import uuid

import pytest
from src.core.errors import ErrorDeNegocio
from src.matches.goal_rules import validar_registro_de_evento

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
    return validar_registro_de_evento(**argumentos)


def codigo_de(excinfo) -> str:
    return excinfo.value.code


@pytest.mark.parametrize("estado", ["finished", "in_progress"])
def test_acepta_partidos_jugables(estado):
    assert validar(match_status=estado) is None


@pytest.mark.parametrize("estado", ["scheduled", "cancelled"])
def test_rechaza_partidos_no_jugables(estado):
    with pytest.raises(ErrorDeNegocio) as exc:
        validar(match_status=estado)
    assert codigo_de(exc) == "match_not_playable"


def test_rechaza_jugador_ajeno():
    with pytest.raises(ErrorDeNegocio) as exc:
        validar(player_team_id=AJENO)
    assert codigo_de(exc) == "player_not_in_match"


def test_sin_alineacion_acepta_jugador_del_partido():
    assert validar(alineados=None) is None


def test_con_alineacion_rechaza_jugador_ausente():
    with pytest.raises(ErrorDeNegocio) as exc:
        validar(player_id=uuid.uuid4(), alineados={uuid.uuid4()})
    assert codigo_de(exc) == "player_not_in_lineup"


def test_varias_validaciones_no_se_bloquean_entre_si():
    """FR-005: la regla no impide varias tarjetas; solo valida cada registro."""
    assert validar() is None
    assert validar() is None
