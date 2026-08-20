"""Integration tests — Acceptance Scenarios de spec.md (US1)."""

import uuid

import pytest
from sqlalchemy import select
from src.core.db import SessionLocal
from src.teams.models import Team

pytestmark = pytest.mark.asyncio

FECHA = "2026-09-01T18:00:00Z"


async def crear_liga(cliente_organizador, nombre="Interfacultades", temporada="2026-1") -> str:
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": nombre, "season": temporada}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def crear_equipo(cliente_organizador, liga_id: str, nombre: str) -> str:
    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": nombre})
    assert r.status_code == 201
    return r.json()["id"]


async def test_as1_programar_partido_queda_scheduled_sin_marcador(cliente, cliente_organizador):
    """AS1: A vs B con fecha → scheduled, sin marcador, visible en listado."""
    liga_id = await crear_liga(cliente_organizador)
    local = await crear_equipo(cliente_organizador, liga_id, "Ingeniería FC")
    visitante = await crear_equipo(cliente_organizador, liga_id, "Medicina FC")

    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/matches",
        json={
            "home_team_id": local,
            "away_team_id": visitante,
            "scheduled_at": FECHA,
        },
    )
    assert r.status_code == 201
    partido = r.json()
    assert partido["league_id"] == liga_id
    assert partido["home_team_id"] == local
    assert partido["away_team_id"] == visitante
    assert partido["status"] == "scheduled"
    assert partido["home_score"] is None
    assert partido["away_score"] is None

    listado = await cliente.get(f"/api/v1/leagues/{liga_id}/matches")
    assert listado.status_code == 200
    assert listado.json()["total"] == 1
    assert listado.json()["items"][0]["id"] == partido["id"]


async def test_as2_mismo_equipo_se_rechaza(cliente_organizador):
    """AS2: A vs A → 409 match_same_team (FR-002)."""
    liga_id = await crear_liga(cliente_organizador)
    equipo = await crear_equipo(cliente_organizador, liga_id, "Ingeniería FC")
    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/matches",
        json={
            "home_team_id": equipo,
            "away_team_id": equipo,
            "scheduled_at": FECHA,
        },
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "match_same_team"


async def test_as3_equipos_de_ligas_distintas_se_rechaza(cliente_organizador):
    """AS3: equipos de ligas distintas → 404 team_not_found (FR-003)."""
    liga_1 = await crear_liga(cliente_organizador, nombre="Liga 1", temporada="2026-1")
    liga_2 = await crear_liga(cliente_organizador, nombre="Liga 2", temporada="2026")
    equipo_a = await crear_equipo(cliente_organizador, liga_1, "Ingeniería FC")
    equipo_c = await crear_equipo(cliente_organizador, liga_2, "Derecho FC")

    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_1}/matches",
        json={
            "home_team_id": equipo_a,
            "away_team_id": equipo_c,
            "scheduled_at": FECHA,
        },
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "team_not_found"


async def test_as4_sin_sesion_se_rechaza(cliente):
    """AS4: sin cookie → 401."""
    r = await cliente.post(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000000/matches",
        json={
            "home_team_id": "00000000-0000-0000-0000-000000000001",
            "away_team_id": "00000000-0000-0000-0000-000000000002",
            "scheduled_at": FECHA,
        },
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_as4_rol_operador_se_rechaza(cliente, cliente_organizador, credenciales_operador):
    """AS4: operador → 403 (FR-006)."""
    liga_id = await crear_liga(cliente_organizador)
    local = await crear_equipo(cliente_organizador, liga_id, "Ingeniería FC")
    visitante = await crear_equipo(cliente_organizador, liga_id, "Medicina FC")
    await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    await cliente.post("/api/v1/auth/logout")
    await cliente.post("/api/v1/auth/login", json=credenciales_operador)

    r = await cliente.post(
        f"/api/v1/leagues/{liga_id}/matches",
        json={
            "home_team_id": local,
            "away_team_id": visitante,
            "scheduled_at": FECHA,
        },
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_equipo_inactive_se_rechaza(cliente_organizador):
    """research.md §3: equipo inactive → 404 team_not_found."""
    liga_id = await crear_liga(cliente_organizador)
    local = await crear_equipo(cliente_organizador, liga_id, "Ingeniería FC")
    visitante = await crear_equipo(cliente_organizador, liga_id, "Medicina FC")

    async with SessionLocal() as s:
        res = await s.execute(select(Team).where(Team.id == uuid.UUID(visitante)))
        equipo = res.scalar_one()
        equipo.status = "inactive"
        await s.commit()

    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/matches",
        json={
            "home_team_id": local,
            "away_team_id": visitante,
            "scheduled_at": FECHA,
        },
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "team_not_found"


async def test_detalle_publico_y_autoria(cliente, cliente_organizador, organizador_creado):
    """FR-005 + FR-008 de 001: detalle público; created_by desde sesión."""
    liga_id = await crear_liga(cliente_organizador)
    local = await crear_equipo(cliente_organizador, liga_id, "Ingeniería FC")
    visitante = await crear_equipo(cliente_organizador, liga_id, "Medicina FC")
    creado = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/matches",
        json={
            "home_team_id": local,
            "away_team_id": visitante,
            "scheduled_at": FECHA,
        },
    )
    assert creado.status_code == 201
    assert creado.json()["created_by"] == str(organizador_creado.id)

    detalle = await cliente.get(f"/api/v1/matches/{creado.json()['id']}")
    assert detalle.status_code == 200
    assert detalle.json()["status"] == "scheduled"
