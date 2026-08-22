"""Contrato de tarjetas y sanciones — spec 014."""

from pathlib import Path

import pytest
import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/014-tarjetas-sanciones/contracts/cards-sanctions.openapi.yaml"
)
RUTA_EVENTOS = "/matches/{matchId}/events"
RUTA_DISCIPLINA = "/players/{playerId}/discipline"
TIPOS_EVENTO = ["GOAL", "YELLOW_CARD", "RED_CARD"]


def contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_contrato_eventos_admite_los_tres_tipos():
    esquema = contrato()["components"]["schemas"]["CreateEventInput"]
    assert set(esquema["properties"]["type"]["enum"]) == set(TIPOS_EVENTO)
    assert "team_id" not in esquema["properties"]


def test_contrato_eventos_declara_errores_de_tarjeta():
    respuestas = contrato()["paths"][RUTA_EVENTOS]["post"]["responses"]
    assert {"401", "403", "404", "409"} <= set(respuestas)


def test_contrato_disciplina_es_publico():
    recurso = contrato()["paths"][RUTA_DISCIPLINA]["get"]
    assert recurso["security"] == []
    esquema = contrato()["components"]["schemas"]["PlayerDiscipline"]
    assert set(esquema["required"]) == {"player_id", "yellow_cards", "red_cards", "suspended"}


@pytest.mark.asyncio
async def test_ficha_disciplinaria_respeta_esquema(cliente, escenario_tarjetas):
    respuesta = await cliente.get(
        f"/api/v1/players/{escenario_tarjetas['home_player_id']}/discipline"
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"player_id", "yellow_cards", "red_cards", "suspended"}


@pytest.mark.asyncio
async def test_jugador_inexistente_en_disciplina(cliente):
    respuesta = await cliente.get("/api/v1/players/00000000-0000-0000-0000-000000000099/discipline")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["code"] == "player_not_found"
