"""Alineaciones y estadísticas de jugador extremo a extremo — FR-001 a FR-011."""

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.asyncio


async def guardar(cliente, match_id, home_ids, away_ids):
    return await cliente.put(
        f"/api/v1/matches/{match_id}/lineup",
        json={"home_player_ids": home_ids, "away_player_ids": away_ids},
    )


async def obtener_lineup(cliente, match_id) -> dict:
    respuesta = await cliente.get(f"/api/v1/matches/{match_id}/lineup")
    assert respuesta.status_code == 200
    return respuesta.json()


async def ficha(cliente, player_id) -> dict:
    respuesta = await cliente.get(f"/api/v1/players/{player_id}/statistics")
    assert respuesta.status_code == 200
    return respuesta.json()


async def top_scorers(cliente, league_id) -> list[dict]:
    respuesta = await cliente.get(f"/api/v1/leagues/{league_id}/top-scorers")
    assert respuesta.status_code == 200
    return respuesta.json()["items"]


# --- FR-001 / AS1: registrar y ver la alineación -----------------------------


async def test_registrar_alineacion_queda_asociada_y_visible(
    cliente, cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    respuesta = await guardar(
        cliente_operador,
        escenario["match_id"],
        [escenario["home_player_id"]],
        [escenario["away_player_id"]],
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "registered"

    cliente.cookies.clear()
    vista = await obtener_lineup(cliente, escenario["match_id"])
    assert vista["status"] == "registered"
    assert [j["player_id"] for j in vista["home_players"]] == [escenario["home_player_id"]]
    assert [j["player_id"] for j in vista["away_players"]] == [escenario["away_player_id"]]


async def test_el_organizador_tambien_registra(cliente_organizador, partido_con_plantillas):
    escenario = partido_con_plantillas
    respuesta = await guardar(
        cliente_organizador, escenario["match_id"], [escenario["home_player_id"]], []
    )
    assert respuesta.status_code == 200


# --- FR-002 / AS2: pertenencia al partido ------------------------------------


async def test_rechaza_jugador_de_un_tercer_equipo(cliente_operador, partido_con_plantillas):
    escenario = partido_con_plantillas
    respuesta = await guardar(
        cliente_operador, escenario["match_id"], [escenario["foreign_player_id"]], []
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "player_not_in_match"


async def test_rechaza_jugador_del_equipo_rival_en_el_lado_equivocado(
    cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    respuesta = await guardar(
        cliente_operador, escenario["match_id"], [escenario["away_player_id"]], []
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "player_not_in_team"


async def test_jugador_inexistente_devuelve_404(cliente_operador, partido_con_plantillas):
    respuesta = await guardar(
        cliente_operador,
        partido_con_plantillas["match_id"],
        ["00000000-0000-0000-0000-000000000099"],
        [],
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "player_not_found"


async def test_partido_inexistente_devuelve_404(cliente_operador):
    respuesta = await guardar(cliente_operador, "00000000-0000-0000-0000-000000000099", [], [])
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "match_not_found"


async def test_jugador_repetido_en_el_mismo_lado_es_rechazado(
    cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    respuesta = await guardar(
        cliente_operador,
        escenario["match_id"],
        [escenario["home_player_id"], escenario["home_player_id"]],
        [],
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["code"] == "validation_error"


async def test_acepta_al_jugador_dado_de_baja(cliente_operador, partido_con_plantillas):
    """Historial: la baja es lógica (Assumption de spec 009)."""
    escenario = partido_con_plantillas
    respuesta = await guardar(
        cliente_operador, escenario["match_id"], [escenario["inactive_player_id"]], []
    )
    assert respuesta.status_code == 200


# --- FR-005: autorización ------------------------------------------------------


async def test_registrar_sin_sesion_devuelve_401(cliente, partido_con_plantillas):
    cliente.cookies.clear()
    respuesta = await guardar(cliente, partido_con_plantillas["match_id"], [], [])
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["code"] == "not_authenticated"


# --- FR-004 / edge case: partido finalizado sin alineación -------------------


async def test_partido_finalizado_sin_alineacion_muestra_missing(cliente, partido_con_plantillas):
    cliente.cookies.clear()
    vista = await obtener_lineup(cliente, partido_con_plantillas["match_id"])
    assert vista == {
        "match_id": partido_con_plantillas["match_id"],
        "status": "missing",
        "home_players": [],
        "away_players": [],
    }


async def test_lineup_de_partido_inexistente_devuelve_404(cliente):
    respuesta = await cliente.get("/api/v1/matches/00000000-0000-0000-0000-000000000099/lineup")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "match_not_found"


# --- FR-003: coherencia alineación-eventos -----------------------------------


async def test_excluir_a_un_goleador_de_una_correccion_es_rechazado(
    cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    assert (
        await guardar(
            cliente_operador,
            escenario["match_id"],
            [escenario["home_player_id"]],
            [escenario["away_player_id"]],
        )
    ).status_code == 200
    goleador = escenario["home_player_id"]
    assert (
        await cliente_operador.post(
            f"/api/v1/matches/{escenario['match_id']}/events",
            json={"player_id": goleador, "minute": 10},
        )
    ).status_code == 201

    respuesta = await guardar(
        cliente_operador, escenario["match_id"], [], [escenario["away_player_id"]]
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "lineup_conflicts_with_events"
    assert goleador in respuesta.json()["error"]["message"]

    # La alineación original —con el goleador— sigue vigente (rechazo atómico).
    vista = await obtener_lineup(cliente_operador, escenario["match_id"])
    assert goleador in [j["player_id"] for j in vista["home_players"]]


async def test_corregir_alineacion_manteniendo_al_goleador_se_acepta(
    cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    goleador = escenario["home_player_id"]
    await guardar(cliente_operador, escenario["match_id"], [goleador], [])
    await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/events",
        json={"player_id": goleador, "minute": 5},
    )
    # Reemplazo completo: se añade otro jugador local sin excluir al goleador.
    respuesta = await guardar(
        cliente_operador, escenario["match_id"], [goleador, escenario["inactive_player_id"]], []
    )
    assert respuesta.status_code == 200
    assert len(respuesta.json()["home_players"]) == 2


async def test_reemplazo_es_completo_no_acumulativo(cliente_operador, partido_con_plantillas):
    escenario = partido_con_plantillas
    await guardar(cliente_operador, escenario["match_id"], [escenario["home_player_id"]], [])
    respuesta = await guardar(
        cliente_operador, escenario["match_id"], [escenario["inactive_player_id"]], []
    )
    assert respuesta.status_code == 200
    ids = [j["player_id"] for j in respuesta.json()["home_players"]]
    assert ids == [escenario["inactive_player_id"]]


# --- Cierre de deuda heredada de spec 009 (FR-003 de 009) --------------------


async def test_gol_de_jugador_fuera_de_la_alineacion_registrada_es_rechazado(
    cliente_operador, partido_con_plantillas
):
    """Escenario 5 del quickstart: cobertura E2E que 009 dejó pendiente."""
    escenario = partido_con_plantillas
    await guardar(cliente_operador, escenario["match_id"], [escenario["home_player_id"]], [])
    # away_player_id pertenece al partido pero no fue incluido en la alineación.
    respuesta = await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/events",
        json={"player_id": escenario["away_player_id"], "minute": 30},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "player_not_in_lineup"


async def test_sin_alineacion_registrada_cualquier_jugador_del_partido_puede_anotar(
    cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    respuesta = await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/events",
        json={"player_id": escenario["away_player_id"], "minute": 30},
    )
    assert respuesta.status_code == 201


# --- FR-007 / AS3: partidos jugados ------------------------------------------


async def _crear_partido_finalizado(
    cliente_organizador, league_id, home_id, away_id, cuando, marcador
):
    creado = await cliente_organizador.post(
        f"/api/v1/leagues/{league_id}/matches",
        json={
            "home_team_id": home_id,
            "away_team_id": away_id,
            "scheduled_at": cuando.isoformat(),
        },
    )
    match_id = creado.json()["id"]
    await cliente_organizador.put(
        f"/api/v1/matches/{match_id}/result",
        json={"home_score": marcador[0], "away_score": marcador[1]},
    )
    return match_id


async def test_partidos_jugados_cuenta_solo_finalizados_con_alineacion(
    cliente, cliente_organizador, cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    jugador = escenario["home_player_id"]
    base = datetime(2026, 10, 1, 18, tzinfo=UTC)

    # El partido de la fixture (finalizado, sin alineación aún) + 2 nuevos.
    for indice in range(2):
        match_id = await _crear_partido_finalizado(
            cliente_organizador,
            escenario["league_id"],
            escenario["home_team_id"],
            escenario["away_team_id"],
            base + timedelta(days=indice),
            (1, 0),
        )
        assert (await guardar(cliente_operador, match_id, [jugador], [])).status_code == 200

    # Alineación del partido original de la fixture también incluye al jugador.
    await guardar(cliente_operador, escenario["match_id"], [jugador], [])

    cliente.cookies.clear()
    datos = await ficha(cliente, jugador)
    assert datos["matches_played"] == 3


async def test_partido_sin_alineacion_no_suma_partidos_jugados(
    cliente, cliente_organizador, partido_con_plantillas
):
    """Edge case: un partido finalizado nunca registrado no cuenta (FR-004)."""
    escenario = partido_con_plantillas
    cliente.cookies.clear()
    datos = await ficha(cliente, escenario["home_player_id"])
    assert datos["matches_played"] == 0


# --- FR-006 / AS4 / AS6: goles y ceros ---------------------------------------


async def test_ficha_muestra_los_goles_registrados(cliente_operador, partido_con_plantillas):
    escenario = partido_con_plantillas
    jugador = escenario["home_player_id"]
    for minuto in (10, 20, 30, 40):
        await cliente_operador.post(
            f"/api/v1/matches/{escenario['match_id']}/events",
            json={"player_id": jugador, "minute": minuto},
        )
    datos = await ficha(cliente_operador, jugador)
    assert datos["goals"] == 4
    assert datos["player_name"] and datos["team_name"]


async def test_jugador_sin_goles_ni_participaciones_muestra_ceros(cliente, partido_con_plantillas):
    """AS6: cero en vez de error o ficha vacía."""
    cliente.cookies.clear()
    datos = await ficha(cliente, partido_con_plantillas["away_player_id"])
    assert (datos["goals"], datos["matches_played"]) == (0, 0)


# --- FR-009 / AS5 / NFR-003: tabla de goleadores -----------------------------


async def test_tabla_de_goleadores_ordenada_descendente_y_top_scorer(
    cliente, cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    for minuto in (10, 20, 30):
        await cliente_operador.post(
            f"/api/v1/matches/{escenario['match_id']}/events",
            json={"player_id": escenario["home_player_id"], "minute": minuto},
        )
    await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/events",
        json={"player_id": escenario["away_player_id"], "minute": 15},
    )

    cliente.cookies.clear()
    filas = await top_scorers(cliente, escenario["league_id"])
    assert [f["goals"] for f in filas] == sorted((f["goals"] for f in filas), reverse=True)
    assert filas[0]["player_id"] == escenario["home_player_id"]
    assert filas[0]["rank"] == 1
    assert filas[0]["is_top_scorer"] is True
    assert filas[1]["is_top_scorer"] is False


async def test_jugadores_sin_goles_no_aparecen_en_la_tabla(
    cliente, cliente_operador, partido_con_plantillas
):
    escenario = partido_con_plantillas
    await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/events",
        json={"player_id": escenario["home_player_id"], "minute": 10},
    )
    cliente.cookies.clear()
    filas = await top_scorers(cliente, escenario["league_id"])
    assert escenario["away_player_id"] not in [f["player_id"] for f in filas]


async def test_liga_sin_goleadores_devuelve_lista_vacia(cliente, partido_con_plantillas):
    cliente.cookies.clear()
    assert await top_scorers(cliente, partido_con_plantillas["league_id"]) == []


# --- FR-006 / AS7: recalculo tras corrección ---------------------------------


async def test_correccion_de_marcador_sin_tocar_eventos_no_altera_goleadores(
    cliente, cliente_operador, cliente_organizador, partido_con_plantillas
):
    """Escenario 9 del quickstart: 006/009 no se pisan con 010."""
    escenario = partido_con_plantillas
    goleador = escenario["home_player_id"]
    await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/events",
        json={"player_id": goleador, "minute": 10},
    )
    antes = await ficha(cliente_operador, goleador)

    solicitud = await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/result-corrections",
        json={"home_score": 5, "away_score": 1, "reason": "Marcador oficial mal digitado."},
    )
    assert solicitud.status_code == 201
    decision = await cliente_organizador.post(
        f"/api/v1/result-corrections/{solicitud.json()['id']}/decision",
        json={"decision": "approved"},
    )
    assert decision.status_code == 200

    cliente.cookies.clear()
    despues = await ficha(cliente, goleador)
    assert despues["goals"] == antes["goals"]


async def test_eliminar_el_evento_gol_reduce_el_conteo_en_la_siguiente_lectura(
    cliente, cliente_operador, partido_con_plantillas
):
    """FR-006/SC-001: la derivación lee `match_events` en cada consulta.

    No existe endpoint de anulación de eventos en el alcance de esta HU ni de
    la 009 (ver research.md Decisión 6): se simula la anulación auditada
    borrando el evento directamente en BD, que es como cualquier mecanismo de
    corrección futuro impactaría el mismo dato.
    """
    from sqlalchemy import delete
    from src.core.db import SessionLocal
    from src.matches.models import MatchEvent

    escenario = partido_con_plantillas
    goleador = escenario["home_player_id"]
    registrado = await cliente_operador.post(
        f"/api/v1/matches/{escenario['match_id']}/events",
        json={"player_id": goleador, "minute": 10},
    )
    evento_id = registrado.json()["id"]

    antes = await ficha(cliente_operador, goleador)
    assert antes["goals"] == 1

    async with SessionLocal() as s:
        await s.execute(delete(MatchEvent).where(MatchEvent.id == evento_id))
        await s.commit()

    cliente.cookies.clear()
    despues = await ficha(cliente, goleador)
    assert despues["goals"] == 0
