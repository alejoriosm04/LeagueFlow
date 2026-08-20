"""Contrato de la clasificación pública — spec 008."""

from pathlib import Path

import pytest
import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/008-consultar-clasificacion/contracts/standings.openapi.yaml"
)
RUTA = "/leagues/{leagueId}/standings"

COLUMNAS = [
    "position",
    "team_id",
    "team_name",
    "played",
    "won",
    "drawn",
    "lost",
    "goals_for",
    "goals_against",
    "goal_difference",
    "points",
]


def contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_contrato_declara_recurso_publico_de_solo_lectura():
    documento = contrato()
    recurso = documento["paths"][RUTA]
    # FR-002: ningún verbo de escritura documentado.
    assert set(recurso) == {"get"}
    assert recurso["get"]["security"] == []
    assert set(recurso["get"]["responses"]) == {"200", "404", "405"}


def test_contrato_declara_tabla_completa_sin_paginacion():
    esquemas = contrato()["components"]["schemas"]
    assert set(esquemas["Standings"]["required"]) == {"league_id", "items"}
    assert not {"page", "page_size", "total"} & set(esquemas["Standings"]["properties"])
    assert esquemas["StandingsRow"]["required"] == COLUMNAS


def test_contrato_no_promete_envelope_en_el_405():
    """El 405 lo emite el router del framework: se afirma el status, no el cuerpo."""
    respuestas = contrato()["paths"][RUTA]["get"]["responses"]
    assert "content" in respuestas["404"]
    assert "content" not in respuestas["405"]


@pytest.mark.asyncio
async def test_respuesta_publica_respeta_el_esquema(cliente, clasificacion_liga):
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/leagues/{clasificacion_liga['league_id']}/standings")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"league_id", "items"}
    assert cuerpo["league_id"] == clasificacion_liga["league_id"]
    for fila in cuerpo["items"]:
        assert list(fila) == COLUMNAS
        assert isinstance(fila["team_name"], str)
        assert all(isinstance(fila[c], int) for c in COLUMNAS if c not in ("team_id", "team_name"))


@pytest.mark.asyncio
async def test_liga_vacia_devuelve_tabla_vacia(cliente, cliente_organizador):
    liga = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga contrato clasificacion", "season": "2026"}
    )
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/leagues/{liga.json()['id']}/standings")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"league_id": liga.json()["id"], "items": []}


@pytest.mark.asyncio
async def test_liga_inexistente_conserva_envelope(cliente):
    respuesta = await cliente.get("/api/v1/leagues/00000000-0000-0000-0000-000000000099/standings")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"] == {
        "code": "league_not_found",
        "message": "La liga no existe.",
        "field": None,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("verbo", ["post", "put", "patch", "delete"])
async def test_la_clasificacion_no_admite_escritura(cliente_organizador, clasificacion_liga, verbo):
    """FR-002 / AS6: ni siquiera un organizador con sesión puede editar la tabla."""
    ruta = f"/api/v1/leagues/{clasificacion_liga['league_id']}/standings"
    respuesta = await getattr(cliente_organizador, verbo)(
        ruta, **({"json": {"points": 99}} if verbo != "delete" else {})
    )
    assert respuesta.status_code == 405
