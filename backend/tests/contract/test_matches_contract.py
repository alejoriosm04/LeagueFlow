"""Contract tests — la API cumple contracts/matches.openapi.yaml."""

from pathlib import Path

import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/005-programar-partido/contracts/matches.openapi.yaml"
)

FECHA = "2026-09-01T18:00:00Z"


def cargar_contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


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


def test_el_contrato_existe_y_es_valido():
    contrato = cargar_contrato()
    assert contrato["openapi"].startswith("3.")
    assert set(contrato["paths"]) == {"/leagues/{leagueId}/matches", "/matches/{matchId}"}


async def test_crear_partido_responde_201_con_esquema_match(cliente_organizador):
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
    cuerpo = r.json()
    assert set(cuerpo) == {
        "id",
        "league_id",
        "home_team_id",
        "away_team_id",
        "scheduled_at",
        "status",
        "home_score",
        "away_score",
        "created_by",
        "created_at",
        "updated_at",
    }
    assert cuerpo["status"] == "scheduled"
    assert cuerpo["home_score"] is None
    assert cuerpo["away_score"] is None


async def test_listar_partidos_devuelve_envelope_de_paginacion(cliente, cliente_organizador):
    liga_id = await crear_liga(cliente_organizador)
    r = await cliente.get(f"/api/v1/leagues/{liga_id}/matches")
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"items", "page", "page_size", "total"}


async def test_detalle_partido_responde_200_sin_autenticarse(cliente, cliente_organizador):
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
    partido_id = creado.json()["id"]
    r = await cliente.get(f"/api/v1/matches/{partido_id}")
    assert r.status_code == 200


async def test_sin_sesion_recibe_401(cliente):
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


async def test_rol_operador_recibe_403(cliente, cliente_organizador, credenciales_operador):
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


async def test_mismo_equipo_recibe_409(cliente_organizador):
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


async def test_liga_inexistente_devuelve_404(cliente_organizador):
    r = await cliente_organizador.post(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000000/matches",
        json={
            "home_team_id": "00000000-0000-0000-0000-000000000001",
            "away_team_id": "00000000-0000-0000-0000-000000000002",
            "scheduled_at": FECHA,
        },
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "league_not_found"


async def test_partido_inexistente_devuelve_404(cliente):
    r = await cliente.get("/api/v1/matches/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "match_not_found"
