"""Contrato de la consulta pública de calendario — spec 007."""

from pathlib import Path

import pytest
import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/007-consultar-calendario/contracts/calendar.openapi.yaml"
)


def test_contrato_declara_filtro_publico_y_paginacion():
    contrato = yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))
    operacion = contrato["paths"]["/leagues/{leagueId}/matches"]["get"]
    assert operacion["security"] == []
    parametros = {p["name"]: p for p in operacion["parameters"]}
    assert parametros["status"]["schema"]["enum"] == [
        "scheduled",
        "in_progress",
        "finished",
        "cancelled",
    ]
    assert parametros["page_size"]["schema"]["maximum"] == 100
    assert {"200", "400", "404"} <= set(operacion["responses"])


@pytest.mark.asyncio
async def test_endpoint_es_publico_vacio_y_valida_estado(cliente, cliente_organizador):
    liga = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga contrato calendario", "season": "2026"}
    )
    cliente.cookies.clear()
    vacio = await cliente.get(f"/api/v1/leagues/{liga.json()['id']}/matches?status=scheduled")
    assert vacio.status_code == 200
    assert vacio.json() == {"items": [], "page": 1, "page_size": 20, "total": 0}
    invalido = await cliente.get(f"/api/v1/leagues/{liga.json()['id']}/matches?status=desconocido")
    assert invalido.status_code == 400
    assert invalido.json()["error"]["code"] == "validation_error"


@pytest.mark.asyncio
async def test_liga_inexistente_conserva_envelope(cliente):
    respuesta = await cliente.get(
        "/api/v1/leagues/00000000-0000-0000-0000-000000000099/matches?status=finished"
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["error"] == {
        "code": "league_not_found",
        "message": "La liga no existe.",
        "field": None,
    }
