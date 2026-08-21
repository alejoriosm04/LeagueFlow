"""Contrato de alineaciones y estadísticas de jugador — spec 010."""

from pathlib import Path

import pytest
import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/010-alineaciones-estadisticas/contracts/lineups-statistics.openapi.yaml"
)
RUTA_LINEUP = "/matches/{matchId}/lineup"
RUTA_TOP_SCORERS = "/leagues/{leagueId}/top-scorers"
RUTA_PLAYER_STATS = "/players/{playerId}/statistics"

CAMPOS_LINEUP_VIEW = ["match_id", "status", "home_players", "away_players"]
CAMPOS_LINEUP_PLAYER = ["player_id", "player_name", "team_id"]
CAMPOS_PLAYER_STATISTICS = [
    "player_id",
    "player_name",
    "team_id",
    "team_name",
    "goals",
    "matches_played",
]
CAMPOS_TOP_SCORER_ROW = [
    "rank",
    "player_id",
    "player_name",
    "team_id",
    "team_name",
    "goals",
    "matches_played",
    "is_top_scorer",
]


def contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_contrato_declara_escritura_privada_y_lectura_publica_de_lineup():
    recurso = contrato()["paths"][RUTA_LINEUP]
    assert set(recurso) == {"put", "get"}
    assert recurso["get"]["security"] == []
    assert "security" not in recurso["put"]
    assert {"400", "401", "403", "404", "409"} <= set(recurso["put"]["responses"])
    assert set(recurso["get"]["responses"]) == {"200", "404"}


def test_contrato_declara_lectura_publica_de_estadisticas():
    top_scorers = contrato()["paths"][RUTA_TOP_SCORERS]["get"]
    ficha = contrato()["paths"][RUTA_PLAYER_STATS]["get"]
    assert top_scorers["security"] == []
    assert ficha["security"] == []
    assert set(top_scorers) & {"put", "post", "patch", "delete"} == set()
    assert set(ficha) & {"put", "post", "patch", "delete"} == set()


def test_contrato_declara_los_esquemas_de_alineacion():
    esquemas = contrato()["components"]["schemas"]
    assert esquemas["MatchLineupView"]["required"] == CAMPOS_LINEUP_VIEW
    assert esquemas["LineupPlayer"]["required"] == CAMPOS_LINEUP_PLAYER
    assert esquemas["MatchLineupView"]["properties"]["status"]["enum"] == ["registered", "missing"]


def test_contrato_declara_los_esquemas_de_estadisticas():
    esquemas = contrato()["components"]["schemas"]
    assert esquemas["PlayerStatistics"]["required"] == CAMPOS_PLAYER_STATISTICS
    assert esquemas["TopScorerRow"]["required"] == CAMPOS_TOP_SCORER_ROW


@pytest.mark.asyncio
async def test_respuesta_de_lineup_respeta_el_esquema(cliente, partido_con_plantillas):
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/matches/{partido_con_plantillas['match_id']}/lineup")
    assert respuesta.status_code == 200
    assert list(respuesta.json()) == CAMPOS_LINEUP_VIEW


@pytest.mark.asyncio
async def test_respuesta_de_ficha_de_jugador_respeta_el_esquema(cliente, partido_con_plantillas):
    respuesta = await cliente.get(
        f"/api/v1/players/{partido_con_plantillas['home_player_id']}/statistics"
    )
    assert respuesta.status_code == 200
    assert list(respuesta.json()) == CAMPOS_PLAYER_STATISTICS


@pytest.mark.asyncio
async def test_respuesta_de_tabla_de_goleadores_respeta_el_esquema(cliente, partido_con_plantillas):
    respuesta = await cliente.get(
        f"/api/v1/leagues/{partido_con_plantillas['league_id']}/top-scorers"
    )
    assert respuesta.status_code == 200
    assert list(respuesta.json()) == ["items"]


@pytest.mark.asyncio
async def test_guardar_lineup_sin_sesion_devuelve_401(cliente, partido_con_plantillas):
    cliente.cookies.clear()
    respuesta = await cliente.put(
        f"/api/v1/matches/{partido_con_plantillas['match_id']}/lineup",
        json={"home_player_ids": [], "away_player_ids": []},
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["code"] == "not_authenticated"


@pytest.mark.asyncio
async def test_liga_inexistente_en_top_scorers_conserva_envelope(cliente):
    respuesta = await cliente.get(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000099/top-scorers"
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "league_not_found"


@pytest.mark.asyncio
async def test_jugador_inexistente_en_ficha_conserva_envelope(cliente):
    respuesta = await cliente.get("/api/v1/players/00000000-0000-0000-0000-000000000099/statistics")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "player_not_found"
