"""Contract tests — la API cumple contracts/leagues.openapi.yaml.

Verifica forma de request/response y códigos de estado, no reglas de negocio
(eso vive en tests/integration). Principio III: el contrato es la frontera.
"""

from pathlib import Path

import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3] / "specs/002-crear-liga/contracts/leagues.openapi.yaml"
)


def cargar_contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_el_contrato_existe_y_es_valido():
    contrato = cargar_contrato()
    assert contrato["openapi"].startswith("3.")
    assert set(contrato["paths"]) == {"/leagues", "/leagues/{leagueId}"}


async def test_crear_liga_responde_201_con_esquema_league(cliente_organizador):
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Interfacultades", "season": "2026-1"}
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert set(cuerpo) == {"id", "name", "season", "description", "created_by", "created_at"}
    assert cuerpo["description"] is None


async def test_listar_ligas_devuelve_envelope_de_paginacion(cliente):
    r = await cliente.get("/api/v1/leagues")
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"items", "page", "page_size", "total"}
    assert isinstance(cuerpo["items"], list)


async def test_detalle_liga_responde_200_sin_autenticarse(cliente, cliente_organizador):
    creada = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Interfacultades", "season": "2026-1"}
    )
    liga_id = creada.json()["id"]

    r = await cliente.get(f"/api/v1/leagues/{liga_id}")
    assert r.status_code == 200
    assert set(r.json()) == {"id", "name", "season", "description", "created_by", "created_at"}


async def test_nombre_vacio_recibe_400_con_campo(cliente_organizador):
    r = await cliente_organizador.post("/api/v1/leagues", json={"name": "", "season": "2026-1"})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"
    assert r.json()["error"]["field"] == "name"


async def test_sin_sesion_recibe_401(cliente):
    r = await cliente.post("/api/v1/leagues", json={"name": "X", "season": "2026"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_rol_operador_recibe_403(cliente, cliente_organizador, credenciales_operador):
    await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    await cliente.post("/api/v1/auth/logout")
    await cliente.post("/api/v1/auth/login", json=credenciales_operador)

    r = await cliente.post("/api/v1/leagues", json={"name": "X", "season": "2026"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_duplicado_recibe_409(cliente_organizador):
    datos = {"name": "Interfacultades", "season": "2026-1"}
    assert (await cliente_organizador.post("/api/v1/leagues", json=datos)).status_code == 201

    r = await cliente_organizador.post("/api/v1/leagues", json=datos)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "league_already_exists"


async def test_detalle_liga_inexistente_devuelve_404(cliente):
    r = await cliente.get("/api/v1/leagues/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "league_not_found"
