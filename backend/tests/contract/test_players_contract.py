"""Contract tests — la API cumple contracts/players.openapi.yaml.

Verifica forma de request/response y códigos de estado, no reglas de negocio
(eso vive en tests/integration). Principio III: el contrato es la frontera.
"""

from pathlib import Path

import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/004-registrar-jugadores/contracts/players.openapi.yaml"
)


def cargar_contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


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


def test_el_contrato_existe_y_es_valido():
    contrato = cargar_contrato()
    assert contrato["openapi"].startswith("3.")
    assert set(contrato["paths"]) == {"/teams/{teamId}/players", "/players/{playerId}"}


async def test_crear_jugador_responde_201_con_esquema_player(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    r = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players",
        json={"name": "Andrés Gómez", "number": 10, "position": "delantero"},
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert set(cuerpo) == {
        "id",
        "team_id",
        "name",
        "number",
        "position",
        "status",
        "created_by",
        "created_at",
    }
    assert cuerpo["team_id"] == equipo_id
    assert cuerpo["number"] == 10
    assert cuerpo["position"] == "delantero"
    assert cuerpo["status"] == "active"


async def test_listar_jugadores_devuelve_envelope_de_paginacion(cliente, cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    r = await cliente.get(f"/api/v1/teams/{equipo_id}/players")
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"items", "page", "page_size", "total"}
    assert isinstance(cuerpo["items"], list)


async def test_detalle_jugador_responde_200_sin_autenticarse(cliente, cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    creado = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players", json={"name": "Andrés Gómez"}
    )
    jugador_id = creado.json()["id"]

    r = await cliente.get(f"/api/v1/players/{jugador_id}")
    assert r.status_code == 200
    assert set(r.json()) == {
        "id",
        "team_id",
        "name",
        "number",
        "position",
        "status",
        "created_by",
        "created_at",
    }


async def test_nombre_vacio_recibe_400_con_campo(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    r = await cliente_organizador.post(f"/api/v1/teams/{equipo_id}/players", json={"name": ""})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"
    assert r.json()["error"]["field"] == "name"


async def test_sin_sesion_recibe_401(cliente):
    r = await cliente.post(
        "/api/v1/teams/00000000-0000-0000-0000-000000000000/players",
        json={"name": "X"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_rol_operador_recibe_403(cliente, cliente_organizador, credenciales_operador):
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


async def test_dorsal_duplicado_recibe_409(cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    equipo_id = await crear_equipo(cliente_organizador, liga_id)
    datos = {"name": "Andrés Gómez", "number": 10}
    assert (
        await cliente_organizador.post(f"/api/v1/teams/{equipo_id}/players", json=datos)
    ).status_code == 201

    r = await cliente_organizador.post(
        f"/api/v1/teams/{equipo_id}/players",
        json={"name": "Otro Jugador", "number": 10},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "player_number_duplicate"


async def test_equipo_inexistente_devuelve_404(cliente_organizador):
    r = await cliente_organizador.post(
        "/api/v1/teams/00000000-0000-0000-0000-000000000000/players",
        json={"name": "X"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "team_not_found"


async def test_jugador_inexistente_devuelve_404(cliente):
    r = await cliente.get("/api/v1/players/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "player_not_found"
