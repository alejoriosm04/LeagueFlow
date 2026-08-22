import csv
import io

import pytest


def _records(response):
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"].startswith("attachment;")
    return list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))


@pytest.mark.asyncio
async def test_clasificacion_exportada_conserva_filas_columnas_y_orden(cliente, clasificacion_liga):
    league_id = clasificacion_liga["league_id"]
    source = await cliente.get(f"/api/v1/leagues/{league_id}/standings")
    records = _records(await cliente.get(f"/api/v1/leagues/{league_id}/standings/export"))
    assert records[3] == ["Pos", "Equipo", "PJ", "G", "E", "P", "GF", "GC", "GD", "Pts"]
    expected = source.json()["items"]
    assert [row[1] for row in records[4:]] == [row["team_name"] for row in expected]
    assert [row[0] for row in records[4:]] == [str(row["position"]) for row in expected]


@pytest.mark.asyncio
async def test_calendario_exporta_todas_las_paginas(cliente, calendario_190):
    records = _records(
        await cliente.get(f"/api/v1/leagues/{calendario_190['league_id']}/matches/export")
    )
    assert records[3] == ["Local", "Visitante", "Fecha", "Estado", "Marcador"]
    assert len(records[4:]) == 190


@pytest.mark.asyncio
async def test_calendario_vacio_conserva_encabezados(cliente, organizador_creado):
    from src.core.db import SessionLocal
    from src.leagues.models import League

    async with SessionLocal() as session:
        league = League(name="Liga vacía", season="2026", created_by=organizador_creado.id)
        session.add(league)
        await session.commit()
        league_id = league.id
    records = _records(await cliente.get(f"/api/v1/leagues/{league_id}/matches/export"))
    assert records[3] == ["Local", "Visitante", "Fecha", "Estado", "Marcador"]
    assert records[4:] == []
