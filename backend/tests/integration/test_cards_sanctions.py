"""Registro de tarjetas y ficha disciplinaria — spec 014."""

import pytest

pytestmark = pytest.mark.asyncio


async def registrar(cliente, match_id, player_id, minute, tipo):
    return await cliente.post(
        f"/api/v1/matches/{match_id}/events",
        json={"player_id": player_id, "minute": minute, "type": tipo},
    )


async def disciplina(cliente, player_id) -> dict:
    respuesta = await cliente.get(f"/api/v1/players/{player_id}/discipline")
    assert respuesta.status_code == 200
    return respuesta.json()


async def test_registrar_amarilla_deriva_equipo(cliente_operador, escenario_tarjetas):
    respuesta = await registrar(
        cliente_operador,
        escenario_tarjetas["match_id"],
        escenario_tarjetas["home_player_id"],
        12,
        "YELLOW_CARD",
    )
    assert respuesta.status_code == 201
    evento = respuesta.json()
    assert evento["type"] == "YELLOW_CARD"
    assert evento["team_id"] == escenario_tarjetas["home_team_id"]


async def test_registrar_roja(cliente_operador, escenario_tarjetas):
    respuesta = await registrar(
        cliente_operador,
        escenario_tarjetas["in_progress_match_id"],
        escenario_tarjetas["away_player_id"],
        70,
        "RED_CARD",
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["type"] == "RED_CARD"


@pytest.mark.parametrize("clave", ["scheduled_match_id", "cancelled_match_id"])
async def test_rechaza_partido_no_jugable(cliente_operador, escenario_tarjetas, clave):
    respuesta = await registrar(
        cliente_operador,
        escenario_tarjetas[clave],
        escenario_tarjetas["home_player_id"],
        5,
        "YELLOW_CARD",
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "match_not_playable"


async def test_rechaza_jugador_fuera_de_alineacion(cliente_operador, escenario_tarjetas):
    respuesta = await registrar(
        cliente_operador,
        escenario_tarjetas["match_id"],
        escenario_tarjetas["player_not_in_lineup_id"],
        20,
        "YELLOW_CARD",
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "player_not_in_lineup"


async def test_sin_alineacion_permite_tarjeta(cliente_operador, escenario_tarjetas):
    respuesta = await registrar(
        cliente_operador,
        escenario_tarjetas["in_progress_match_id"],
        escenario_tarjetas["home_player_id"],
        33,
        "YELLOW_CARD",
    )
    assert respuesta.status_code == 201


async def test_varias_tarjetas_mismo_partido(cliente_operador, escenario_tarjetas):
    for minuto in (10, 55):
        assert (
            await registrar(
                cliente_operador,
                escenario_tarjetas["in_progress_match_id"],
                escenario_tarjetas["home_player_id"],
                minuto,
                "YELLOW_CARD",
            )
        ).status_code == 201


async def test_listado_publico_incluye_tarjetas_y_consistencia_solo_goles(
    cliente, cliente_operador, escenario_tarjetas
):
    await registrar(
        cliente_operador,
        escenario_tarjetas["match_id"],
        escenario_tarjetas["home_player_id"],
        15,
        "YELLOW_CARD",
    )
    await registrar(
        cliente_operador,
        escenario_tarjetas["match_id"],
        escenario_tarjetas["home_player_id"],
        20,
        "GOAL",
    )
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/matches/{escenario_tarjetas['match_id']}/events")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    tipos = {evento["type"] for evento in cuerpo["items"]}
    assert {"GOAL", "YELLOW_CARD"} <= tipos
    assert cuerpo["consistency"]["home_goals_recorded"] == 1


async def test_suspension_por_roja(cliente_operador, escenario_tarjetas):
    await registrar(
        cliente_operador,
        escenario_tarjetas["match_id"],
        escenario_tarjetas["home_player_id"],
        88,
        "RED_CARD",
    )
    ficha = await disciplina(cliente_operador, escenario_tarjetas["home_player_id"])
    assert ficha["red_cards"] == 1
    assert ficha["suspended"] is True


async def test_suspension_por_dos_amarillas_en_partidos_distintos(
    cliente_operador, escenario_tarjetas
):
    await registrar(
        cliente_operador,
        escenario_tarjetas["match_id"],
        escenario_tarjetas["home_player_id"],
        10,
        "YELLOW_CARD",
    )
    await registrar(
        cliente_operador,
        escenario_tarjetas["match_id_2"],
        escenario_tarjetas["home_player_id"],
        20,
        "YELLOW_CARD",
    )
    ficha = await disciplina(cliente_operador, escenario_tarjetas["home_player_id"])
    assert ficha["yellow_cards"] == 2
    assert ficha["suspended"] is True


async def test_dos_amarillas_mismo_partido_no_suspende(cliente_operador, escenario_tarjetas):
    await registrar(
        cliente_operador,
        escenario_tarjetas["in_progress_match_id"],
        escenario_tarjetas["away_player_id"],
        11,
        "YELLOW_CARD",
    )
    await registrar(
        cliente_operador,
        escenario_tarjetas["in_progress_match_id"],
        escenario_tarjetas["away_player_id"],
        44,
        "YELLOW_CARD",
    )
    ficha = await disciplina(cliente_operador, escenario_tarjetas["away_player_id"])
    assert ficha["yellow_cards"] == 2
    assert ficha["suspended"] is False


async def test_ficha_publica_sin_sesion(cliente, escenario_tarjetas):
    cliente.cookies.clear()
    respuesta = await cliente.get(
        f"/api/v1/players/{escenario_tarjetas['home_player_id']}/discipline"
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["yellow_cards"] == 0


async def test_jugador_inexistente_en_ficha(cliente):
    respuesta = await cliente.get("/api/v1/players/00000000-0000-0000-0000-000000000099/discipline")
    assert respuesta.status_code == 404
