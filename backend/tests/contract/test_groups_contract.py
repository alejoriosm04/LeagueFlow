"""Contract tests — la API cumple contracts/groups.openapi.yaml.

Verifica forma de request/response y códigos de estado, no reglas de negocio
(eso vive en tests/integration). Principio III: el contrato es la frontera.
"""

from pathlib import Path

import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/013-grupos-divisiones/contracts/groups.openapi.yaml"
)


def cargar_contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


async def crear_liga(cliente_organizador, nombre="Interfacultades", temporada="2026-1") -> str:
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": nombre, "season": temporada}
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_el_contrato_existe_y_es_valido():
    contrato = cargar_contrato()
    assert contrato["openapi"].startswith("3.")
    assert set(contrato["paths"]) == {
        "/leagues/{leagueId}/groups",
        "/groups/{groupId}",
        "/groups/{groupId}/teams",
    }


async def test_crear_grupo_responde_201_con_esquema_group(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/groups", json={"name": "Grupo A"}
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert set(cuerpo) == {"id", "league_id", "name", "position", "created_at"}
    assert cuerpo["league_id"] == liga_id
    assert cuerpo["position"] is None


async def test_listar_grupos_devuelve_envelope(cliente, cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente.get(f"/api/v1/leagues/{liga_id}/groups")
    assert r.status_code == 200
    assert set(r.json()) == {"items"}
    assert isinstance(r.json()["items"], list)


async def test_nombre_vacio_recibe_400_con_campo(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/groups", json={"name": ""})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"
    assert r.json()["error"]["field"] == "name"


async def test_sin_sesion_recibe_401(cliente):
    r = await cliente.post(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000000/groups", json={"name": "X"}
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_rol_operador_recibe_403(cliente, cliente_organizador, credenciales_operador):
    liga_id = await crear_liga(cliente_organizador)
    await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    await cliente.post("/api/v1/auth/logout")
    await cliente.post("/api/v1/auth/login", json=credenciales_operador)

    r = await cliente.post(f"/api/v1/leagues/{liga_id}/groups", json={"name": "X"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_duplicado_recibe_409(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    datos = {"name": "Grupo A"}
    assert (
        await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/groups", json=datos)
    ).status_code == 201

    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/groups", json=datos)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "group_name_duplicate"


async def test_liga_inexistente_devuelve_404(cliente_organizador):
    r = await cliente_organizador.post(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000000/groups", json={"name": "X"}
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "league_not_found"


async def test_grupo_inexistente_devuelve_404(cliente_organizador):
    r = await cliente_organizador.patch(
        "/api/v1/groups/00000000-0000-0000-0000-000000000000", json={"name": "X"}
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "group_not_found"
