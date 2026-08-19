"""Integration tests — los 4 Acceptance Scenarios de spec.md (US1).

Cada test nombra el escenario que verifica. Principio II de la constitución:
toda regla de negocio tiene una prueba que la afirma.
"""

import pytest

pytestmark = pytest.mark.asyncio


async def test_as1_crear_liga_queda_registrada_y_listada(cliente, cliente_organizador):
    """AS1: crear con nombre y temporada válidos -> registrada y visible."""
    r = await cliente_organizador.post(
        "/api/v1/leagues",
        json={"name": "Interfacultades", "season": "2026-1", "description": "Liga universitaria"},
    )
    assert r.status_code == 201
    liga = r.json()
    assert liga["name"] == "Interfacultades"
    assert liga["season"] == "2026-1"
    assert liga["description"] == "Liga universitaria"

    listado = await cliente.get("/api/v1/leagues")
    assert listado.status_code == 200
    nombres = [liga["name"] for liga in listado.json()["items"]]
    assert "Interfacultades" in nombres

    detalle = await cliente.get(f"/api/v1/leagues/{liga['id']}")
    assert detalle.status_code == 200
    assert detalle.json()["name"] == "Interfacultades"


async def test_as2_nombre_y_temporada_duplicados_se_rechazan(cliente_organizador):
    """AS2: repetir la misma liga -> 409 identificando el conflicto (FR-002)."""
    datos = {"name": "Interfacultades", "season": "2026-1"}
    assert (await cliente_organizador.post("/api/v1/leagues", json=datos)).status_code == 201

    repetido = await cliente_organizador.post("/api/v1/leagues", json=datos)
    assert repetido.status_code == 409
    assert repetido.json()["error"]["code"] == "league_already_exists"
    assert repetido.json()["error"]["field"] == "name"


async def test_unicidad_insensible_a_mayusculas_y_espacios(cliente_organizador):
    """research.md §2: 'Interfacultades 2026' y '  interfacultades   2026 ' son la misma liga."""
    primera = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Interfacultades", "season": "2026-1"}
    )
    assert primera.status_code == 201

    repetida = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "  INTERFACULTADES    ", "season": "  2026-1 "}
    )
    assert repetida.status_code == 409
    assert repetida.json()["error"]["code"] == "league_already_exists"


async def test_normalizacion_recorta_y_colapsa_espacios(cliente_organizador):
    """data-model.md: name/season se guardan con espacios recortados y colapsados."""
    r = await cliente_organizador.post(
        "/api/v1/leagues",
        json={"name": "  Interfacultades   2026  ", "season": "  Apertura  2026 "},
    )
    assert r.status_code == 201
    liga = r.json()
    # Preserva la capitalización original, sin espacios sobrantes.
    assert liga["name"] == "Interfacultades 2026"
    assert liga["season"] == "Apertura 2026"


async def test_as3_nombre_vacio_se_rechaza_con_campo(cliente_organizador):
    """AS3: nombre vacío -> 400 indicando qué campo falta."""
    r = await cliente_organizador.post("/api/v1/leagues", json={"name": "", "season": "2026-1"})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"
    assert r.json()["error"]["field"] == "name"


async def test_as4_sin_sesion_se_rechaza(cliente):
    """AS4: sin cookie de sesión -> 401."""
    r = await cliente.post("/api/v1/leagues", json={"name": "X", "season": "2026"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_as4_rol_operador_se_rechaza(cliente, cliente_organizador, credenciales_operador):
    """AS4: con sesión de operador -> 403 (FR-005)."""
    await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    await cliente.post("/api/v1/auth/logout")
    await cliente.post("/api/v1/auth/login", json=credenciales_operador)

    r = await cliente.post("/api/v1/leagues", json={"name": "X", "season": "2026"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_autoria_automatica_desde_la_sesion(cliente_organizador, organizador_creado):
    """FR-008 / quickstart §6: created_by lo deriva el servidor, nunca el payload."""
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Interfacultades", "season": "2026-1"}
    )
    assert r.status_code == 201
    assert r.json()["created_by"] == str(organizador_creado.id)


async def test_fr004_ligas_independientes_coexisten(cliente, cliente_organizador):
    """FR-004: varias ligas independientes, sin que los datos de una afecten a otra."""
    await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Interfacultades", "season": "2026-1"}
    )
    await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Interfacultades", "season": "2026-2"}
    )
    await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Copa Universidad", "season": "2026"}
    )

    listado = await cliente.get("/api/v1/leagues")
    assert listado.json()["total"] == 3


async def test_consulta_publica_sin_sesion(cliente, cliente_organizador):
    """FR-003: GET /leagues y GET /leagues/{id} no exigen autenticación."""
    creada = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Interfacultades", "season": "2026-1"}
    )
    liga_id = creada.json()["id"]

    assert (await cliente.get("/api/v1/leagues")).status_code == 200
    assert (await cliente.get(f"/api/v1/leagues/{liga_id}")).status_code == 200


async def test_detalle_liga_inexistente_devuelve_404(cliente):
    r = await cliente.get("/api/v1/leagues/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "league_not_found"
