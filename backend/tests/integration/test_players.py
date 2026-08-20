"""Integration tests — los 4 Acceptance Scenarios de spec.md (US1).

Cada test nombra el escenario que verifica. Principio II de la constitución:
toda regla de negocio tiene una prueba que la afirma.
"""

import uuid

import pytest
from sqlalchemy import select
from src.core.db import SessionLocal
from src.players.models import Player
from src.teams.models import Team

pytestmark = pytest.mark.asyncio


async def crear_liga(cliente_organizador, nombre="Interfacultades", temporada="2026-1") -> str:
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": nombre, "season": temporada}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def crear_equipo(cliente_organizador, liga_id: str, nombre="Ingeniería FC") -> str:
    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": nombre})
    assert r.status_code == 201
    return r.json()["id"]


async def test_as1_registrar_jugador_queda_asociado_y_listado(cliente, cliente_organizador):
    """AS1: registrar jugadores válidos -> asociados al equipo y visibles en plantilla."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)

    nombres = ["Andrés Gómez", "Luis Pérez", "María Ruiz"]
    for i, nombre in enumerate(nombres, start=1):
        r = await cliente_organizador.post(
            f"/api/v1/teams/{equipo_id}/players",
            json={"name": nombre, "number": i, "position": "delantero"},
        )
        assert r.status_code == 201
        assert r.json()["team_id"] == equipo_id

    listado = await cliente.get(f"/api/v1/teams/{equipo_id}/players")
    assert listado.status_code == 200
    assert [j["name"] for j in listado.json()["items"]] == nombres


async def test_as2_dorsal_duplicado_en_mismo_equipo_se_rechaza(cliente_organizador):
    """AS2: mismo dorsal en el mismo equipo -> 409 (FR-003)."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    assert (
        await cliente_organizador.post(
            f"/api/v1/teams/{equipo_id}/players",
            json={"name": "Andrés Gómez", "number": 10},
        )
    ).status_code == 201

    r = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players",
        json={"name": "Otro Jugador", "number": 10},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "player_number_duplicate"
    assert r.json()["error"]["field"] == "number"


async def test_as3_plantilla_aislada_por_equipo(cliente, cliente_organizador):
    """AS3: jugador del equipo A no aparece en la plantilla del equipo B."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_a = await crear_equipo(cliente_organizador, liga_id, "Ingeniería FC")
    equipo_b = await crear_equipo(cliente_organizador, liga_id, "Medicina FC")

    r = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_a}/players",
        json={"name": "Andrés Gómez", "number": 10},
    )
    assert r.status_code == 201

    plantilla_b = await cliente.get(f"/api/v1/teams/{equipo_b}/players")
    assert plantilla_b.status_code == 200
    assert plantilla_b.json()["items"] == []


async def test_as4_sin_sesion_se_rechaza(cliente):
    """AS4: sin cookie de sesión -> 401."""
    r = await cliente.post(
        "/api/v1/teams/00000000-0000-0000-0000-000000000000/players",
        json={"name": "X"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_as4_rol_operador_se_rechaza(cliente, cliente_organizador, credenciales_operador):
    """AS4: con sesión de operador -> 403 (FR-004)."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    await cliente.post("/api/v1/auth/logout")
    await cliente.post("/api/v1/auth/login", json=credenciales_operador)

    r = await cliente.post(f"/api/v1/teams/{equipo_id}/players", json={"name": "X"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_dorsal_fuera_de_rango_se_rechaza(cliente_organizador):
    """research.md §1: number debe estar en 1–99."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)

    for number in (0, 100):
        r = await cliente_organizador.post(
            f"/api/v1/teams/{equipo_id}/players",
            json={"name": "Andrés Gómez", "number": number},
        )
        assert r.status_code == 400
        assert r.json()["error"]["field"] == "number"


async def test_dos_jugadores_sin_dorsal_en_mismo_equipo_son_validos(cliente_organizador):
    """research.md §1: la unicidad no aplica cuando number es null."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)

    for nombre in ("Sin Dorsal A", "Sin Dorsal B"):
        r = await cliente_organizador.post(
            f"/api/v1/teams/{equipo_id}/players", json={"name": nombre}
        )
        assert r.status_code == 201
        assert r.json()["number"] is None


async def test_alta_sobre_equipo_inactive_se_rechaza(cliente_organizador):
    """research.md §4: POST sobre equipo inactive -> 404 team_not_found."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)

    async with SessionLocal() as s:
        res = await s.execute(select(Team).where(Team.id == uuid.UUID(equipo_id)))
        equipo = res.scalar_one()
        equipo.status = "inactive"
        await s.commit()

    r = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players", json={"name": "Andrés Gómez"}
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "team_not_found"


async def test_jugador_inactive_desaparece_del_listado_pero_sigue_accesible(
    cliente, cliente_organizador
):
    """FR-005 / research.md §3: borrado lógico — invisible en listados, visible en historial."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    creado = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players",
        json={"name": "Andrés Gómez", "number": 10},
    )
    jugador_id = creado.json()["id"]

    async with SessionLocal() as s:
        res = await s.execute(select(Player).where(Player.id == uuid.UUID(jugador_id)))
        jugador = res.scalar_one()
        jugador.status = "inactive"
        await s.commit()

    por_defecto = await cliente.get(f"/api/v1/teams/{equipo_id}/players")
    assert [j["name"] for j in por_defecto.json()["items"]] == []

    detalle = await cliente.get(f"/api/v1/players/{jugador_id}")
    assert detalle.status_code == 200
    assert detalle.json()["status"] == "inactive"

    con_inactivos = await cliente.get(
        f"/api/v1/teams/{equipo_id}/players", params={"include_inactive": "true"}
    )
    assert [j["name"] for j in con_inactivos.json()["items"]] == ["Andrés Gómez"]


async def test_autoria_automatica_desde_la_sesion(cliente_organizador, organizador_creado):
    """FR-008 de specs/001: created_by lo deriva el servidor, nunca el payload."""
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    r = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players", json={"name": "Andrés Gómez"}
    )
    assert r.status_code == 201
    assert r.json()["created_by"] == str(organizador_creado.id)


async def test_normalizacion_recorta_y_colapsa_espacios(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    r = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players", json={"name": "  Andrés   Gómez  "}
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Andrés Gómez"
