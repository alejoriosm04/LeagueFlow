"""Composición del dashboard general de la liga — spec 011.

No reimplementa el filtro/orden de 007 ni el cálculo de 008: cada
aserción compara el bloque del dashboard contra lo que devuelven por
separado `GET /leagues/{id}/matches` y `GET /leagues/{id}/standings`, para
que una futura reimplementación local (en vez de una llamada real a esos
servicios) rompa la prueba.
"""

import pytest

pytestmark = pytest.mark.asyncio


async def dashboard(cliente, liga_id) -> dict:
    respuesta = await cliente.get(f"/api/v1/leagues/{liga_id}/dashboard")
    assert respuesta.status_code == 200
    return respuesta.json()


async def test_recientes_son_los_5_finalizados_mas_recientes_en_orden(cliente, dashboard_resumen):
    liga_id = dashboard_resumen["league_id"]
    resumen = await dashboard(cliente, liga_id)
    ids = [m["id"] for m in resumen["recent_matches"]]
    assert ids == dashboard_resumen["recientes_esperados"]

    calendario = await cliente.get(f"/api/v1/leagues/{liga_id}/matches?status=finished")
    assert ids == [m["id"] for m in calendario.json()["items"][:5]]


async def test_proximos_son_los_5_programados_mas_cercanos_en_orden(cliente, dashboard_resumen):
    liga_id = dashboard_resumen["league_id"]
    resumen = await dashboard(cliente, liga_id)
    ids = [m["id"] for m in resumen["upcoming_matches"]]
    assert ids == dashboard_resumen["proximos_esperados"]

    calendario = await cliente.get(f"/api/v1/leagues/{liga_id}/matches?status=scheduled")
    assert ids == [m["id"] for m in calendario.json()["items"][:5]]


async def test_top_standings_son_las_5_primeras_filas_en_orden(cliente, dashboard_resumen):
    liga_id = dashboard_resumen["league_id"]
    resumen = await dashboard(cliente, liga_id)
    nombres = [f["team_name"] for f in resumen["top_standings"]]
    assert nombres == dashboard_resumen["clasificacion_esperada"]
    assert [f["position"] for f in resumen["top_standings"]] == [1, 2, 3, 4, 5]

    clasificacion = await cliente.get(f"/api/v1/leagues/{liga_id}/standings")
    assert resumen["top_standings"] == clasificacion.json()["items"][:5]


async def test_liga_sin_equipos_ni_partidos_devuelve_los_tres_bloques_vacios(
    cliente, cliente_organizador
):
    """FR-002, AS2."""
    liga = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga dashboard vacia", "season": "2026"}
    )
    cliente.cookies.clear()
    resumen = await dashboard(cliente, liga.json()["id"])
    assert resumen["recent_matches"] == []
    assert resumen["upcoming_matches"] == []
    assert resumen["top_standings"] == []


async def test_liga_con_equipos_sin_partidos_solo_vacia_los_bloques_de_partidos(
    cliente, cliente_organizador
):
    """AS5 / Assumption "Bloque de clasificación 'vacío'" de spec.md."""
    liga = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga dashboard sin partidos", "season": "2026"}
    )
    liga_id = liga.json()["id"]
    await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": "Equipo A"})
    await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": "Equipo B"})
    cliente.cookies.clear()
    resumen = await dashboard(cliente, liga_id)
    assert resumen["recent_matches"] == []
    assert resumen["upcoming_matches"] == []
    assert len(resumen["top_standings"]) == 2
    assert {f["played"] for f in resumen["top_standings"]} == {0}
    assert {f["points"] for f in resumen["top_standings"]} == {0}


async def test_resultado_recien_registrado_se_refleja_sin_recalculo(
    cliente, cliente_operador, dashboard_resumen
):
    """AS3: el dashboard recargado refleja el nuevo resultado y la
    clasificación actualizada, sin ninguna acción manual de recálculo."""
    liga_id = dashboard_resumen["league_id"]
    antes = await dashboard(cliente, liga_id)
    proximo_id = antes["upcoming_matches"][0]["id"]

    registro = await cliente_operador.put(
        f"/api/v1/matches/{proximo_id}/result", json={"home_score": 5, "away_score": 0}
    )
    assert registro.status_code == 200

    despues = await dashboard(cliente, liga_id)
    assert proximo_id in [m["id"] for m in despues["recent_matches"]]
    assert proximo_id not in [m["id"] for m in despues["upcoming_matches"]]
    assert despues["top_standings"] != antes["top_standings"]


async def test_liga_inexistente_devuelve_404(cliente):
    respuesta = await cliente.get("/api/v1/leagues/00000000-0000-0000-0000-000000000099/dashboard")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "league_not_found"


async def test_la_consulta_no_exige_sesion(cliente, dashboard_resumen):
    """FR-003, AS4."""
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/leagues/{dashboard_resumen['league_id']}/dashboard")
    assert respuesta.status_code == 200
