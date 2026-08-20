"""Registro inicial de marcador — AS1, AS2, AS3, AS10 y FR-013."""

import asyncio
import uuid

import pytest
from sqlalchemy import select
from src.core.db import SessionLocal
from src.matches.models import Match

pytestmark = pytest.mark.asyncio


async def test_registrar_3_1_finaliza_partido(cliente_operador, partido_programado):
    r = await cliente_operador.put(
        f"/api/v1/matches/{partido_programado['id']}/result",
        json={"home_score": 3, "away_score": 1},
    )
    assert r.status_code == 200
    assert (r.json()["home_score"], r.json()["away_score"], r.json()["status"]) == (
        3,
        1,
        "finished",
    )


@pytest.mark.parametrize("marcador", [(-1, 0), (0, -1), (1.5, 0)])
async def test_marcador_invalido_se_rechaza(cliente_operador, partido_programado, marcador):
    r = await cliente_operador.put(
        f"/api/v1/matches/{partido_programado['id']}/result",
        json={"home_score": marcador[0], "away_score": marcador[1]},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"


async def test_empate_es_valido(cliente_operador, partido_programado):
    r = await cliente_operador.put(
        f"/api/v1/matches/{partido_programado['id']}/result",
        json={"home_score": 2, "away_score": 2},
    )
    assert r.status_code == 200


async def test_no_autenticado_y_partido_inexistente(cliente, cliente_operador, partido_programado):
    cliente.cookies.clear()
    sin_sesion = await cliente.put(
        f"/api/v1/matches/{partido_programado['id']}/result",
        json={"home_score": 1, "away_score": 0},
    )
    assert sin_sesion.status_code == 401
    inexistente = await cliente_operador.put(
        f"/api/v1/matches/{uuid.uuid4()}/result", json={"home_score": 1, "away_score": 0}
    )
    assert inexistente.status_code == 404


@pytest.mark.parametrize("estado", ["in_progress", "cancelled"])
async def test_estado_no_programado_se_rechaza(cliente_operador, partido_programado, estado):
    async with SessionLocal() as s:
        partido = await s.get(Match, uuid.UUID(partido_programado["id"]))
        partido.status = estado
        await s.commit()
    r = await cliente_operador.put(
        f"/api/v1/matches/{partido_programado['id']}/result",
        json={"home_score": 1, "away_score": 0},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "match_not_scheduled"


async def test_resultado_finalizado_no_se_sobrescribe(cliente_operador, partido_programado):
    ruta = f"/api/v1/matches/{partido_programado['id']}/result"
    assert (
        await cliente_operador.put(ruta, json={"home_score": 3, "away_score": 1})
    ).status_code == 200
    repetido = await cliente_operador.put(ruta, json={"home_score": 2, "away_score": 1})
    assert repetido.status_code == 409
    assert repetido.json()["error"]["code"] == "result_already_recorded"


async def test_dos_registros_concurrentes_solo_aplican_uno(cliente_operador, partido_programado):
    ruta = f"/api/v1/matches/{partido_programado['id']}/result"
    respuestas = await asyncio.gather(
        cliente_operador.put(ruta, json={"home_score": 3, "away_score": 1}),
        cliente_operador.put(ruta, json={"home_score": 2, "away_score": 0}),
    )
    assert sorted(r.status_code for r in respuestas) == [200, 409]
    async with SessionLocal() as s:
        partido = (
            await s.execute(select(Match).where(Match.id == uuid.UUID(partido_programado["id"])))
        ).scalar_one()
        assert (partido.home_score, partido.away_score) in {(3, 1), (2, 0)}
