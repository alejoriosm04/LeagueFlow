"""Contract tests — la API cumple contracts/teams.openapi.yaml.

Verifica forma de request/response y códigos de estado, no reglas de negocio
(eso vive en tests/integration). Principio III: el contrato es la frontera.
"""

from pathlib import Path

import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3] / "specs/003-registrar-equipos/contracts/teams.openapi.yaml"
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
    assert set(contrato["paths"]) == {"/leagues/{leagueId}/teams", "/teams/{teamId}"}


async def test_crear_equipo_responde_201_con_esquema_team(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Ingeniería FC"}
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert set(cuerpo) == {
        "id",
        "league_id",
        "name",
        "crest_url",
        "colors",
        "status",
        "created_by",
        "created_at",
    }
    assert cuerpo["league_id"] == liga_id
    assert cuerpo["crest_url"] is None
    assert cuerpo["colors"] is None
    assert cuerpo["status"] == "active"


async def test_listar_equipos_devuelve_envelope_de_paginacion(cliente, cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente.get(f"/api/v1/leagues/{liga_id}/teams")
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"items", "page", "page_size", "total"}
    assert isinstance(cuerpo["items"], list)


async def test_detalle_equipo_responde_200_sin_autenticarse(cliente, cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    creado = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Ingeniería FC"}
    )
    equipo_id = creado.json()["id"]

    r = await cliente.get(f"/api/v1/teams/{equipo_id}")
    assert r.status_code == 200
    assert set(r.json()) == {
        "id",
        "league_id",
        "name",
        "crest_url",
        "colors",
        "status",
        "created_by",
        "created_at",
    }


async def test_nombre_vacio_recibe_400_con_campo(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": ""})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"
    assert r.json()["error"]["field"] == "name"


async def test_sin_sesion_recibe_401(cliente):
    # 401 ante la ausencia de sesión; no hace falta crear la liga porque el
    # control de rol se evalúa antes que la existencia de la liga.
    r = await cliente.post(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000000/teams", json={"name": "X"}
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

    r = await cliente.post(f"/api/v1/leagues/{liga_id}/teams", json={"name": "X"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_duplicado_recibe_409(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    datos = {"name": "Ingeniería FC"}
    assert (
        await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json=datos)
    ).status_code == 201

    r = await cliente_organizador.post(f"/api/v1/leagues/{liga_id}/teams", json=datos)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "team_name_duplicate"


async def test_liga_inexistente_devuelve_404(cliente_organizador):
    r = await cliente_organizador.post(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000000/teams", json={"name": "X"}
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "league_not_found"


async def test_equipo_inexistente_devuelve_404(cliente):
    r = await cliente.get("/api/v1/teams/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "team_not_found"
