"""Derivación extremo a extremo de la clasificación — FR-001 a FR-008."""

import pytest

pytestmark = pytest.mark.asyncio


async def tabla(cliente, liga_id) -> list[dict]:
    respuesta = await cliente.get(f"/api/v1/leagues/{liga_id}/standings")
    assert respuesta.status_code == 200
    return respuesta.json()["items"]


async def test_tabla_coincide_con_el_calculo_manual(cliente, clasificacion_liga):
    """SC-001: la tabla esperada está calculada a mano en la fixture."""
    filas = await tabla(cliente, clasificacion_liga["league_id"])
    assert [f["team_name"] for f in filas] == clasificacion_liga["orden_esperado"]
    assert [f["position"] for f in filas] == [1, 2, 3, 4, 5, 6]
    lider = filas[0]
    assert (lider["played"], lider["won"], lider["drawn"], lider["lost"]) == (2, 2, 0, 0)
    assert (lider["goals_for"], lider["goals_against"]) == (5, 1)
    assert (lider["goal_difference"], lider["points"]) == (4, 6)
    assert [f["points"] for f in filas] == [6, 4, 1, 0, 0, 0]
    assert [f["goal_difference"] for f in filas] == [4, 2, -2, 0, -2, -2]


async def test_equipo_inactivo_sin_historial_no_ocupa_fila(cliente, clasificacion_liga):
    filas = await tabla(cliente, clasificacion_liga["league_id"])
    assert "Fantasma" not in [f["team_name"] for f in filas]
    assert clasificacion_liga["teams"]["Retirado"] in [f["team_id"] for f in filas]


@pytest.mark.parametrize("nivel", ["gd", "gf", "total"])
async def test_los_tres_niveles_de_desempate(cliente, clasificacion_empates, nivel):
    """AS3, AS4 y FR-006."""
    escenario = clasificacion_empates[nivel]
    filas = await tabla(cliente, escenario["league_id"])
    assert [f["team_name"] for f in filas] == escenario["orden_esperado"]


async def test_consultas_sucesivas_devuelven_el_mismo_orden(cliente, clasificacion_empates):
    """FR-006: el desempate es estable, no depende del plan de ejecución."""
    liga_id = clasificacion_empates["total"]["league_id"]
    primera = await cliente.get(f"/api/v1/leagues/{liga_id}/standings")
    segunda = await cliente.get(f"/api/v1/leagues/{liga_id}/standings")
    assert primera.status_code == segunda.status_code == 200
    assert primera.json()["items"]
    assert primera.content == segunda.content


async def test_partido_programado_no_altera_la_tabla(cliente, clasificacion_liga):
    """AS5 / FR-001."""
    filas = await tabla(cliente, clasificacion_liga["league_id"])
    por_nombre = {f["team_name"]: f for f in filas}
    # El único partido pendiente de Bravo es el scheduled contra Delta.
    assert por_nombre["Bravo"]["played"] == 1
    assert por_nombre["Delta"]["played"] == 2


async def test_partido_cancelado_no_altera_la_tabla(cliente, cliente_operador, clasificacion_liga):
    """FR-007: el cancelado ni suma ni permite registrar resultado."""
    antes = await tabla(cliente, clasificacion_liga["league_id"])
    rechazo = await cliente_operador.put(
        f"/api/v1/matches/{clasificacion_liga['cancelado_id']}/result",
        json={"home_score": 5, "away_score": 0},
    )
    assert rechazo.status_code == 409
    assert await tabla(cliente, clasificacion_liga["league_id"]) == antes


async def test_registrar_resultado_se_refleja_sin_recalculo(
    cliente, cliente_operador, clasificacion_liga
):
    """SC-002: registrar el marcador basta; no hay acción intermedia."""
    antes = {f["team_name"]: f for f in await tabla(cliente, clasificacion_liga["league_id"])}
    registro = await cliente_operador.put(
        f"/api/v1/matches/{clasificacion_liga['programado_id']}/result",
        json={"home_score": 4, "away_score": 0},
    )
    assert registro.status_code == 200
    despues = {f["team_name"]: f for f in await tabla(cliente, clasificacion_liga["league_id"])}
    assert despues["Bravo"]["points"] == antes["Bravo"]["points"] + 3
    assert despues["Bravo"]["played"] == antes["Bravo"]["played"] + 1
    assert despues["Bravo"]["goals_for"] == antes["Bravo"]["goals_for"] + 4
    assert despues["Delta"]["points"] == antes["Delta"]["points"]
    assert despues["Delta"]["goals_against"] == antes["Delta"]["goals_against"] + 4


async def test_correccion_pendiente_no_altera_la_tabla_y_aprobada_si(
    cliente, cliente_operador, cliente_organizador, clasificacion_liga
):
    """Edge case de correcciones pendientes + SC-002 tras la aprobación."""
    liga_id = clasificacion_liga["league_id"]
    antes = await tabla(cliente, liga_id)

    solicitud = await cliente_operador.post(
        f"/api/v1/matches/{clasificacion_liga['finalizado_id']}/result-corrections",
        json={"home_score": 0, "away_score": 1, "reason": "Acta corregida por el árbitro."},
    )
    assert solicitud.status_code == 201
    assert solicitud.json()["status"] == "pending"
    # La tabla sigue reflejando el resultado vigente mientras está pendiente.
    assert await tabla(cliente, liga_id) == antes

    decision = await cliente_organizador.post(
        f"/api/v1/result-corrections/{solicitud.json()['id']}/decision",
        json={"decision": "approved"},
    )
    assert decision.status_code == 200
    despues = {f["team_name"]: f for f in await tabla(cliente, liga_id)}
    # Alfa 2-0 Bravo pasa a Alfa 0-1 Bravo: Alfa pierde la victoria, Bravo la gana.
    assert despues["Alfa"]["points"] == 3
    assert despues["Bravo"]["points"] == 3
    assert despues["Bravo"]["won"] == 1


async def test_la_consulta_no_exige_sesion(cliente, clasificacion_liga):
    """FR-008."""
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/leagues/{clasificacion_liga['league_id']}/standings")
    assert respuesta.status_code == 200
    assert respuesta.json()["items"]


async def test_liga_sin_equipos_devuelve_items_vacio(cliente, cliente_organizador):
    liga = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga sin equipos", "season": "2026"}
    )
    assert await tabla(cliente, liga.json()["id"]) == []
