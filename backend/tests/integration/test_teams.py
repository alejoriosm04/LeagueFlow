"""Integration tests — los 4 Acceptance Scenarios de spec.md (US1).

Cada test nombra el escenario que verifica. Principio II de la constitución:
toda regla de negocio tiene una prueba que la afirma.
"""

import uuid

import pytest
from sqlalchemy import select
from src.core.db import SessionLocal
from src.teams.models import Team

pytestmark = pytest.mark.asyncio


async def crear_liga(cliente_organizador, nombre="Interfacultades", temporada="2026-1") -> str:
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": nombre, "season": temporada}
    )
    assert r.status_code == 201
    return r.json()["id"]


async def test_as1_registrar_equipo_queda_asociado_y_listado(cliente, cliente_organizador):
    """AS1: registrar un equipo válido -> asociado a la liga y visible en su listado."""
    liga_id = await crear_liga(cliente_organizador)

    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams",
        json={"name": "Ingeniería FC", "colors": "azul/blanco"},
    )
    assert r.status_code == 201
    equipo = r.json()
    assert equipo["league_id"] == liga_id
    assert equipo["name"] == "Ingeniería FC"
    assert equipo["colors"] == "azul/blanco"

    listado = await cliente.get(f"/api/v1/leagues/{liga_id}/teams")
    assert listado.status_code == 200
    assert [t["name"] for t in listado.json()["items"]] == ["Ingeniería FC"]


async def test_as2_nombre_duplicado_en_misma_liga_se_rechaza(cliente_organizador):
    """AS2: mismo nombre en la misma liga -> 409 (FR-002)."""
    liga_id = await crear_liga(cliente_organizador)
    datos = {"name": "Ingeniería FC"}
    assert (
        await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json=datos)
    ).status_code == 201

    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json=datos)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "team_name_duplicate"
    assert r.json()["error"]["field"] == "name"


async def test_unicidad_insensible_a_mayusculas_y_espacios(cliente_organizador):
    """quickstart §2: 'INGENIERÍA FC' y '  ingeniería   fc  ' son el mismo equipo."""
    liga_id = await crear_liga(cliente_organizador)
    assert (
        await cliente_organizador.post(
            f"/api/v1/leagues/{liga_id}/teams", json={"name": "Ingeniería FC"}
        )
    ).status_code == 201

    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "  INGENIERÍA   FC  "}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "team_name_duplicate"


async def test_normalizacion_recorta_y_colapsa_espacios(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "  Ingeniería   FC  "}
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Ingeniería FC"


async def test_as3_mismo_nombre_en_ligas_distintas_es_valido(cliente_organizador):
    """AS3: 'Ingeniería FC' puede existir en dos ligas distintas (FR-002, FR-003)."""
    liga_a = await crear_liga(cliente_organizador, nombre="Interfacultades", temporada="2026-1")
    liga_b = await crear_liga(cliente_organizador, nombre="Copa Universidad", temporada="2026")

    for liga in (liga_a, liga_b):
        r = await cliente_organizador.post(
            f"/api/v1/leagues/{liga}/teams", json={"name": "Ingeniería FC"}
        )
        assert r.status_code == 201


async def test_as4_sin_sesion_se_rechaza(cliente):
    """AS4: sin cookie de sesión -> 401. Sin crear liga: el rol se evalúa primero."""
    r = await cliente.post(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000000/teams", json={"name": "X"}
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_as4_rol_operador_se_rechaza(cliente, cliente_organizador, credenciales_operador):
    """AS4: con sesión de operador -> 403 (FR-004)."""
    liga_id = await crear_liga(cliente_organizador)
    await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    await cliente.post("/api/v1/auth/logout")
    await cliente.post("/api/v1/auth/login", json=credenciales_operador)

    r = await cliente.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": "X"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_crest_url_no_https_se_rechaza(cliente_organizador):
    """research.md §1: solo URLs https absolutas, sin descargar el recurso."""
    liga_id = await crear_liga(cliente_organizador)

    for crest_url in ("http://example.com/escudo.png", "no-es-una-url", "ftp://example.com/x"):
        r = await cliente_organizador.post(
            f"/api/v1/leagues/{liga_id}/teams",
            json={"name": "Ingeniería FC", "crest_url": crest_url},
        )
        assert r.status_code == 400
        assert r.json()["error"]["field"] == "crest_url"


async def test_crest_url_https_valida_se_acepta(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams",
        json={"name": "Ingeniería FC", "crest_url": "https://example.com/escudo.png"},
    )
    assert r.status_code == 201
    assert r.json()["crest_url"] == "https://example.com/escudo.png"


async def test_equipo_inactive_desaparece_del_listado_pero_sigue_accesible(
    cliente, cliente_organizador
):
    """FR-005 / research.md §3: borrado lógico — invisible en listados, visible en historial."""
    liga_id = await crear_liga(cliente_organizador)
    creado = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Ingeniería FC"}
    )
    equipo_id = creado.json()["id"]

    # Se marca inactivo directamente en la BD: el endpoint de baja no forma
    # parte de esta HU (llegará con partidos, en specs 005+).
    async with SessionLocal() as s:
        res = await s.execute(select(Team).where(Team.id == uuid.UUID(equipo_id)))
        equipo = res.scalar_one()
        equipo.status = "inactive"
        await s.commit()

    # Desaparece del listado por defecto (solo activos).
    por_defecto = await cliente.get(f"/api/v1/leagues/{liga_id}/teams")
    assert [t["name"] for t in por_defecto.json()["items"]] == []

    # Sigue accesible por id (historial).
    detalle = await cliente.get(f"/api/v1/teams/{equipo_id}")
    assert detalle.status_code == 200
    assert detalle.json()["status"] == "inactive"

    # Aparece con include_inactive=true.
    con_inactivos = await cliente.get(
        f"/api/v1/leagues/{liga_id}/teams", params={"include_inactive": "true"}
    )
    assert [t["name"] for t in con_inactivos.json()["items"]] == ["Ingeniería FC"]


async def test_autoria_automatica_desde_la_sesion(cliente_organizador, organizador_creado):
    """FR-008 de specs/001: created_by lo deriva el servidor, nunca el payload."""
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Ingeniería FC"}
    )
    assert r.status_code == 201
    assert r.json()["created_by"] == str(organizador_creado.id)
