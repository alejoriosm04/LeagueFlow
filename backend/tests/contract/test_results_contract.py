"""Contrato de resultados y correcciones — spec 006."""

from pathlib import Path

import yaml

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/006-registrar-resultado/contracts/results.openapi.yaml"
)


def cargar_contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_contrato_declara_paths_schemas_y_seguridad():
    contrato = cargar_contrato()
    assert contrato["openapi"] == "3.0.3"
    assert set(contrato["paths"]) == {
        "/matches/{matchId}/result",
        "/matches/{matchId}/result-corrections",
        "/result-corrections/{correctionId}/decision",
    }
    assert {"ScoreInput", "CreateCorrectionInput", "DecisionInput", "ResultCorrection"} <= set(
        contrato["components"]["schemas"]
    )
    assert contrato["security"] == [{"sessionCookie": []}]
    assert contrato["paths"]["/matches/{matchId}/result-corrections"]["get"]["security"] == []


async def test_resultado_respeta_status_y_envelope(cliente, cliente_operador, partido_programado):
    cliente.cookies.clear()
    sin_sesion = await cliente.put(
        f"/api/v1/matches/{partido_programado['id']}/result",
        json={"home_score": 3, "away_score": 1},
    )
    assert sin_sesion.status_code == 401
    assert set(sin_sesion.json()["error"]) == {"code", "message", "field"}

    creado = await cliente_operador.put(
        f"/api/v1/matches/{partido_programado['id']}/result",
        json={"home_score": 3, "away_score": 1},
    )
    assert creado.status_code == 200
    assert creado.json()["status"] == "finished"


async def test_historial_publico_usa_envelope_paginado(cliente, partido_programado):
    respuesta = await cliente.get(f"/api/v1/matches/{partido_programado['id']}/result-corrections")
    assert respuesta.status_code == 200
    assert set(respuesta.json()) == {"items", "page", "page_size", "total"}
