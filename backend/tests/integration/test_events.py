"""Registro y consulta de goles extremo a extremo — FR-001 a FR-006."""

import pytest

pytestmark = pytest.mark.asyncio


async def registrar(cliente, escenario, player_id, minute, **extra):
    cuerpo = {"player_id": player_id, "minute": minute, **extra}
    return await cliente.post(f"/api/v1/matches/{escenario['match_id']}/events", json=cuerpo)


async def eventos(cliente, match_id) -> dict:
    respuesta = await cliente.get(f"/api/v1/matches/{match_id}/events")
    assert respuesta.status_code == 200
    return respuesta.json()


async def test_registrar_gol_asocia_partido_jugador_y_equipo(
    cliente_operador, partido_con_plantillas
):
    """AS1: el equipo se deriva del jugador (research.md §4)."""
    respuesta = await registrar(
        cliente_operador, partido_con_plantillas, partido_con_plantillas["home_player_id"], 23
    )
    assert respuesta.status_code == 201
    evento = respuesta.json()
    assert evento["match_id"] == partido_con_plantillas["match_id"]
    assert evento["player_id"] == partido_con_plantillas["home_player_id"]
    assert evento["team_id"] == partido_con_plantillas["home_team_id"]
    assert (evento["minute"], evento["type"]) == (23, "GOAL")


async def test_el_organizador_tambien_registra(cliente_organizador, partido_con_plantillas):
    respuesta = await registrar(
        cliente_organizador, partido_con_plantillas, partido_con_plantillas["away_player_id"], 40
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["team_id"] == partido_con_plantillas["away_team_id"]


async def test_rechaza_al_jugador_ajeno_al_partido(cliente_operador, partido_con_plantillas):
    """AS2 / SC-002."""
    respuesta = await registrar(
        cliente_operador, partido_con_plantillas, partido_con_plantillas["foreign_player_id"], 12
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "player_not_in_match"


async def test_acepta_al_jugador_dado_de_baja(cliente_operador, partido_con_plantillas):
    """Assumption "Jugadores dados de baja": la baja es lógica y conserva historial."""
    respuesta = await registrar(
        cliente_operador, partido_con_plantillas, partido_con_plantillas["inactive_player_id"], 77
    )
    assert respuesta.status_code == 201


async def test_jugador_inexistente_devuelve_404(cliente_operador, partido_con_plantillas):
    respuesta = await registrar(
        cliente_operador,
        partido_con_plantillas,
        "00000000-0000-0000-0000-000000000099",
        10,
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "player_not_found"


@pytest.mark.parametrize("clave", ["scheduled_match_id", "cancelled_match_id"])
async def test_rechaza_partidos_sin_juego(cliente_operador, partido_con_plantillas, clave):
    respuesta = await cliente_operador.post(
        f"/api/v1/matches/{partido_con_plantillas[clave]}/events",
        json={"player_id": partido_con_plantillas["home_player_id"], "minute": 5},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "match_not_playable"


async def test_minuto_negativo_es_rechazado(cliente_operador, partido_con_plantillas):
    respuesta = await registrar(
        cliente_operador, partido_con_plantillas, partido_con_plantillas["home_player_id"], -1
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["code"] == "validation_error"


async def test_tipo_no_soportado_es_rechazado(cliente_operador, partido_con_plantillas):
    """FR-004: hoy solo GOAL; ampliar el enum será una migración, no un rediseño."""
    respuesta = await registrar(
        cliente_operador,
        partido_con_plantillas,
        partido_con_plantillas["home_player_id"],
        10,
        type="RED_CARD",
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["code"] == "validation_error"


async def test_descuadre_con_el_marcador_advierte_sin_bloquear(
    cliente, cliente_operador, partido_con_plantillas
):
    """AS4 / FR-005: el partido es 3-1 y solo se registran dos goles."""
    for minuto in (10, 20):
        assert (
            await registrar(
                cliente_operador,
                partido_con_plantillas,
                partido_con_plantillas["home_player_id"],
                minuto,
            )
        ).status_code == 201

    consistencia = (await eventos(cliente, partido_con_plantillas["match_id"]))["consistency"]
    assert (consistencia["home_goals_recorded"], consistencia["away_goals_recorded"]) == (2, 0)
    assert (consistencia["home_score"], consistencia["away_score"]) == (3, 1)
    assert consistencia["matches_official"] is False


async def test_marcador_cuadrado_no_advierte(cliente, cliente_operador, partido_con_plantillas):
    for minuto in (10, 20, 30):
        await registrar(
            cliente_operador,
            partido_con_plantillas,
            partido_con_plantillas["home_player_id"],
            minuto,
        )
    await registrar(
        cliente_operador, partido_con_plantillas, partido_con_plantillas["away_player_id"], 55
    )
    consistencia = (await eventos(cliente, partido_con_plantillas["match_id"]))["consistency"]
    assert consistencia["matches_official"] is True


async def test_listado_publico_en_orden_de_minuto(
    cliente, cliente_operador, partido_con_plantillas
):
    for minuto in (60, 12, 35):
        await registrar(
            cliente_operador,
            partido_con_plantillas,
            partido_con_plantillas["home_player_id"],
            minuto,
        )
    cliente.cookies.clear()
    cuerpo = await eventos(cliente, partido_con_plantillas["match_id"])
    assert [evento["minute"] for evento in cuerpo["items"]] == [12, 35, 60]


async def test_partido_sin_eventos_devuelve_lista_vacia_con_consistencia(
    cliente, partido_con_plantillas
):
    cuerpo = await eventos(cliente, partido_con_plantillas["match_id"])
    assert cuerpo["items"] == []
    assert cuerpo["consistency"]["matches_official"] is False


async def test_registrar_goles_no_altera_el_marcador_oficial(
    cliente, cliente_operador, partido_con_plantillas
):
    """El marcador es la fuente de verdad de la clasificación (FR-005).

    La aserción directa sobre GET /leagues/{id}/standings no es posible en esta
    rama: ese endpoint es de specs/008-consultar-clasificacion, todavía sin
    mezclar en main.
    """
    ruta = f"/api/v1/matches/{partido_con_plantillas['match_id']}"
    antes = (await cliente.get(ruta)).json()
    for minuto in (10, 20, 30, 40, 50):
        creado = await registrar(
            cliente_operador,
            partido_con_plantillas,
            partido_con_plantillas["home_player_id"],
            minuto,
        )
        assert creado.status_code == 201
    despues = (await cliente.get(ruta)).json()
    # Cinco goles registrados contra un marcador oficial de 3-1: aun así el
    # marcador no se mueve.
    assert (await eventos(cliente, partido_con_plantillas["match_id"]))["consistency"][
        "matches_official"
    ] is False
    assert (despues["home_score"], despues["away_score"]) == (
        antes["home_score"],
        antes["away_score"],
    )
    assert despues["status"] == antes["status"]


async def test_eventos_de_partido_inexistente(cliente):
    respuesta = await cliente.get("/api/v1/matches/00000000-0000-0000-0000-000000000099/events")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "match_not_found"


async def test_el_cliente_no_puede_suplantar_equipo_ni_autor(
    cliente_operador, partido_con_plantillas
):
    """T018: `team_id` y `created_by` se derivan del servidor, no del cuerpo."""
    respuesta = await registrar(
        cliente_operador,
        partido_con_plantillas,
        partido_con_plantillas["home_player_id"],
        15,
        team_id=partido_con_plantillas["away_team_id"],
        created_by="00000000-0000-0000-0000-000000000099",
    )
    assert respuesta.status_code == 201
    evento = respuesta.json()
    # El equipo sigue siendo el del jugador, no el que envió el cliente.
    assert evento["team_id"] == partido_con_plantillas["home_team_id"]
    assert evento["created_by"] != "00000000-0000-0000-0000-000000000099"
