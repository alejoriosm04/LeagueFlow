"""Flujo auditado de correcciones — AS4 a AS9."""

import asyncio

import pytest

pytestmark = pytest.mark.asyncio


async def finalizar(cliente_operador, partido_id: str, home=3, away=1):
    r = await cliente_operador.put(
        f"/api/v1/matches/{partido_id}/result", json={"home_score": home, "away_score": away}
    )
    assert r.status_code == 200


async def solicitar(cliente_operador, partido_id: str, home=2, away=1, reason="Acta corregida"):
    return await cliente_operador.post(
        f"/api/v1/matches/{partido_id}/result-corrections",
        json={"home_score": home, "away_score": away, "reason": reason},
    )


async def test_pendiente_guarda_snapshot_y_no_altera_partido(
    cliente, cliente_operador, partido_programado
):
    await finalizar(cliente_operador, partido_programado["id"])
    r = await solicitar(cliente_operador, partido_programado["id"])
    assert r.status_code == 201
    assert r.json()["status"] == "pending"
    assert (r.json()["previous_home_score"], r.json()["previous_away_score"]) == (3, 1)
    detalle = await cliente.get(f"/api/v1/matches/{partido_programado['id']}")
    assert (detalle.json()["home_score"], detalle.json()["away_score"]) == (3, 1)


async def test_aprobar_aplica_y_rechazar_conserva(
    cliente_operador, cliente_organizador_alternativo, partido_programado
):
    await finalizar(cliente_operador, partido_programado["id"])
    pendiente = await solicitar(cliente_operador, partido_programado["id"])
    aprobada = await cliente_organizador_alternativo.post(
        f"/api/v1/result-corrections/{pendiente.json()['id']}/decision",
        json={"decision": "approved"},
    )
    assert aprobada.status_code == 200
    assert aprobada.json()["status"] == "approved"

    otra = await solicitar(cliente_operador, partido_programado["id"], 1, 1, "Segunda acta")
    rechazada = await cliente_organizador_alternativo.post(
        f"/api/v1/result-corrections/{otra.json()['id']}/decision",
        json={"decision": "rejected", "decision_reason": "Acta original confirmada"},
    )
    assert rechazada.status_code == 200
    assert rechazada.json()["status"] == "rejected"


async def test_propuesta_identica_es_valida(
    cliente_operador, cliente_organizador_alternativo, partido_programado
):
    await finalizar(cliente_operador, partido_programado["id"])
    pendiente = await solicitar(cliente_operador, partido_programado["id"], 3, 1)
    r = await cliente_organizador_alternativo.post(
        f"/api/v1/result-corrections/{pendiente.json()['id']}/decision",
        json={"decision": "approved"},
    )
    assert r.status_code == 200


async def test_solo_una_pendiente_incluso_concurrente(cliente_operador, partido_programado):
    await finalizar(cliente_operador, partido_programado["id"])
    ruta = f"/api/v1/matches/{partido_programado['id']}/result-corrections"
    respuestas = await asyncio.gather(
        cliente_operador.post(ruta, json={"home_score": 2, "away_score": 1, "reason": "Acta A"}),
        cliente_operador.post(ruta, json={"home_score": 1, "away_score": 1, "reason": "Acta B"}),
    )
    assert sorted(r.status_code for r in respuestas) == [201, 409]


async def test_solicitante_no_puede_decidir_y_operador_no_decide(
    cliente_operador, partido_programado
):
    await finalizar(cliente_operador, partido_programado["id"])
    pendiente = await solicitar(cliente_operador, partido_programado["id"])
    ruta = f"/api/v1/result-corrections/{pendiente.json()['id']}/decision"
    r = await cliente_operador.post(ruta, json={"decision": "approved"})
    assert r.status_code == 403


async def test_organizador_solicitante_no_puede_decidir_su_solicitud(
    cliente_organizador, partido_programado
):
    await finalizar(cliente_organizador, partido_programado["id"])
    pendiente = await solicitar(cliente_organizador, partido_programado["id"])
    r = await cliente_organizador.post(
        f"/api/v1/result-corrections/{pendiente.json()['id']}/decision",
        json={"decision": "approved"},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "correction_self_decision"


async def test_historial_publico_auditado(
    cliente, cliente_operador, cliente_organizador_alternativo, partido_programado
):
    await finalizar(cliente_operador, partido_programado["id"])
    pendiente = await solicitar(cliente_operador, partido_programado["id"])
    await cliente_organizador_alternativo.post(
        f"/api/v1/result-corrections/{pendiente.json()['id']}/decision",
        json={"decision": "approved"},
    )
    historial = await cliente.get(f"/api/v1/matches/{partido_programado['id']}/result-corrections")
    assert historial.status_code == 200
    item = historial.json()["items"][0]
    assert item["requested_by"] and item["decided_by"] and item["created_at"] and item["decided_at"]


async def test_decision_repetida_se_rechaza(
    cliente_operador, cliente_organizador_alternativo, partido_programado
):
    await finalizar(cliente_operador, partido_programado["id"])
    pendiente = await solicitar(cliente_operador, partido_programado["id"])
    ruta = f"/api/v1/result-corrections/{pendiente.json()['id']}/decision"
    assert (
        await cliente_organizador_alternativo.post(ruta, json={"decision": "approved"})
    ).status_code == 200
    repetida = await cliente_organizador_alternativo.post(ruta, json={"decision": "approved"})
    assert repetida.status_code == 409
    assert repetida.json()["error"]["code"] == "correction_already_decided"
