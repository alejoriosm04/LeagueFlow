"""Contrato de los eventos de partido — spec 009."""

from pathlib import Path

import pytest
import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3] / "specs/009-registrar-goles/contracts/events.openapi.yaml"
)
RUTA = "/matches/{matchId}/events"

CAMPOS_EVENTO = [
    "id",
    "match_id",
    "type",
    "player_id",
    "team_id",
    "minute",
    "created_by",
    "created_at",
]
CAMPOS_CONSISTENCIA = [
    "home_goals_recorded",
    "away_goals_recorded",
    "home_score",
    "away_score",
    "matches_official",
]


def contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_contrato_declara_escritura_privada_y_lectura_publica():
    recurso = contrato()["paths"][RUTA]
    assert set(recurso) == {"post", "get"}
    assert recurso["get"]["security"] == []
    assert "security" not in recurso["post"]
    assert {"401", "403", "404", "409"} <= set(recurso["post"]["responses"])


def test_contrato_no_pide_team_id_al_cliente():
    """research.md §4: el equipo se deriva del jugador."""
    entrada = contrato()["components"]["schemas"]["CreateEventInput"]
    assert entrada["required"] == ["player_id", "minute"]
    assert "team_id" not in entrada["properties"]
    assert entrada["properties"]["type"]["enum"] == ["GOAL"]


def test_contrato_declara_evento_y_consistencia():
    esquemas = contrato()["components"]["schemas"]
    assert esquemas["MatchEvent"]["required"] == CAMPOS_EVENTO
    assert esquemas["EventConsistency"]["required"] == CAMPOS_CONSISTENCIA
    assert set(esquemas["MatchEvents"]["required"]) == {"items", "consistency"}


@pytest.mark.asyncio
async def test_respuesta_publica_respeta_el_esquema(cliente, partido_con_plantillas):
    cliente.cookies.clear()
    respuesta = await cliente.get(f"/api/v1/matches/{partido_con_plantillas['match_id']}/events")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"items", "consistency"}
    assert list(cuerpo["consistency"]) == CAMPOS_CONSISTENCIA


@pytest.mark.asyncio
async def test_evento_creado_respeta_el_esquema(cliente_operador, partido_con_plantillas):
    respuesta = await cliente_operador.post(
        f"/api/v1/matches/{partido_con_plantillas['match_id']}/events",
        json={"player_id": partido_con_plantillas["home_player_id"], "minute": 23},
    )
    assert respuesta.status_code == 201
    assert list(respuesta.json()) == CAMPOS_EVENTO


@pytest.mark.asyncio
async def test_registrar_sin_sesion_devuelve_401(cliente, partido_con_plantillas):
    """FR-006. El 403 insufficient_role no es alcanzable en este endpoint:
    acepta los dos únicos roles que existen. El contrato lo declara como forma
    genérica, igual que hace 006 en PUT /result."""
    cliente.cookies.clear()
    respuesta = await cliente.post(
        f"/api/v1/matches/{partido_con_plantillas['match_id']}/events",
        json={"player_id": partido_con_plantillas["home_player_id"], "minute": 10},
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["code"] == "not_authenticated"


@pytest.mark.asyncio
async def test_ambos_roles_de_escritura_son_aceptados(
    cliente_operador, cliente_organizador, partido_con_plantillas
):
    ruta = f"/api/v1/matches/{partido_con_plantillas['match_id']}/events"
    cuerpo = {"player_id": partido_con_plantillas["home_player_id"], "minute": 5}
    assert (await cliente_operador.post(ruta, json=cuerpo)).status_code == 201
    assert (await cliente_organizador.post(ruta, json=cuerpo)).status_code == 201


@pytest.mark.asyncio
async def test_partido_inexistente_conserva_envelope(cliente):
    respuesta = await cliente.get("/api/v1/matches/00000000-0000-0000-0000-000000000099/events")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"] == {
        "code": "match_not_found",
        "message": "El partido no existe.",
        "field": None,
    }
