"""Orden, filtros y paginación del calendario público — FR-001 a FR-003."""

import uuid

import pytest
from sqlalchemy import select
from src.core.db import SessionLocal
from src.matches.models import Match

pytestmark = pytest.mark.asyncio


async def test_proximos_asc_y_jugados_desc_con_marcador(cliente, calendario_mixto):
    liga_id = calendario_mixto["league_id"]
    proximos = await cliente.get(f"/api/v1/leagues/{liga_id}/matches?status=scheduled")
    jugados = await cliente.get(f"/api/v1/leagues/{liga_id}/matches?status=finished")
    assert proximos.status_code == jugados.status_code == 200
    assert [p["scheduled_at"] for p in proximos.json()["items"]] == sorted(
        p["scheduled_at"] for p in proximos.json()["items"]
    )
    fechas_jugados = [p["scheduled_at"] for p in jugados.json()["items"]]
    assert fechas_jugados == sorted(fechas_jugados, reverse=True)
    assert all(
        p["home_score"] is not None and p["away_score"] is not None for p in jugados.json()["items"]
    )


@pytest.mark.parametrize("estado", ["scheduled", "in_progress", "finished", "cancelled"])
async def test_cada_filtro_devuelve_solo_su_estado(cliente, calendario_mixto, estado):
    respuesta = await cliente.get(
        f"/api/v1/leagues/{calendario_mixto['league_id']}/matches?status={estado}"
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["items"]
    assert {p["status"] for p in respuesta.json()["items"]} == {estado}


async def test_sin_filtro_conserva_orden_ascendente_de_005(cliente, calendario_mixto):
    respuesta = await cliente.get(f"/api/v1/leagues/{calendario_mixto['league_id']}/matches")
    fechas = [p["scheduled_at"] for p in respuesta.json()["items"]]
    assert fechas == sorted(fechas)


async def test_desempate_por_id_es_estable(cliente, calendario_mixto):
    partidos = calendario_mixto["matches"][:2]
    async with SessionLocal() as db:
        segundo = await db.scalar(select(Match).where(Match.id == partidos[1].id))
        segundo.scheduled_at = partidos[0].scheduled_at
        await db.commit()
    respuesta = await cliente.get(
        f"/api/v1/leagues/{calendario_mixto['league_id']}/matches?status=scheduled"
    )
    ids = [uuid.UUID(p["id"]) for p in respuesta.json()["items"]]
    assert ids == sorted(ids)


async def test_recorrer_paginas_recupera_190_partidos(cliente, calendario_190):
    liga_id = calendario_190["league_id"]
    primera = await cliente.get(
        f"/api/v1/leagues/{liga_id}/matches?status=scheduled&page=1&page_size=100"
    )
    segunda = await cliente.get(
        f"/api/v1/leagues/{liga_id}/matches?status=scheduled&page=2&page_size=100"
    )
    assert primera.status_code == segunda.status_code == 200
    assert primera.json()["total"] == calendario_190["total"] == 190
    assert len(primera.json()["items"]) == 100
    assert len(segunda.json()["items"]) == 90
    todos = primera.json()["items"] + segunda.json()["items"]
    assert len({p["id"] for p in todos}) == 190
