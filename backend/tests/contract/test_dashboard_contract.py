"""Contrato del dashboard general de la liga — spec 011."""

from pathlib import Path

import pytest
import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/011-dashboard-liga/contracts/dashboard.openapi.yaml"
)
RUTA = "/leagues/{leagueId}/dashboard"


def contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_contrato_declara_recurso_publico_con_tres_bloques():
    documento = contrato()
    operacion = documento["paths"][RUTA]["get"]
    assert operacion["security"] == []
    assert {"200", "400", "404"} <= set(operacion["responses"])
    propiedades = documento["components"]["schemas"]["DashboardSummary"]["properties"]
    assert set(propiedades) == {
        "league_id",
        "recent_matches",
        "upcoming_matches",
        "top_standings",
    }
    for bloque in ("recent_matches", "upcoming_matches", "top_standings"):
        assert propiedades[bloque]["maxItems"] == 5


@pytest.mark.asyncio
async def test_endpoint_es_publico_y_respeta_el_esquema(cliente, dashboard_resumen):
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/leagues/{dashboard_resumen['league_id']}/dashboard")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {
        "league_id",
        "recent_matches",
        "upcoming_matches",
        "top_standings",
    }
    assert cuerpo["league_id"] == dashboard_resumen["league_id"]
    assert len(cuerpo["recent_matches"]) == 5
    assert len(cuerpo["upcoming_matches"]) == 5
    assert len(cuerpo["top_standings"]) == 5
    campos_match = {
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
    assert set(cuerpo["recent_matches"][0]) == campos_match
    assert set(cuerpo["upcoming_matches"][0]) == campos_match
    campos_fila = {
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
    }
    assert set(cuerpo["top_standings"][0]) == campos_fila


@pytest.mark.asyncio
async def test_leagueid_invalido_devuelve_validation_error(cliente):
    respuesta = await cliente.get("/api/v1/leagues/no-es-un-uuid/dashboard")
    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["code"] == "validation_error"


@pytest.mark.asyncio
async def test_liga_inexistente_conserva_envelope(cliente):
    respuesta = await cliente.get("/api/v1/leagues/00000000-0000-0000-0000-000000000099/dashboard")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"] == {
        "code": "league_not_found",
        "message": "La liga no existe.",
        "field": None,
    }
