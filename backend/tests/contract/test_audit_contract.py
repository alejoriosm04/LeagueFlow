"""Contract tests — la API cumple contracts/audit.openapi.yaml.

Verifica forma de request/response y códigos de estado, no reglas de negocio
(eso vive en tests/integration). Principio III: el contrato es la frontera.
"""

from pathlib import Path

import yaml

CONTRATO = Path(__file__).resolve().parents[3] / "specs/016-auditoria/contracts/audit.openapi.yaml"


def cargar_contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_el_contrato_existe_y_es_valido():
    contrato = cargar_contrato()
    assert contrato["openapi"].startswith("3.")
    assert set(contrato["paths"]) == {"/admin/audit-log"}


async def test_listar_audit_log_responde_200_con_envelope_de_paginacion(cliente_organizador):
    await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga Contrato", "season": "2026"}
    )

    r = await cliente_organizador.get("/api/v1/admin/audit-log")
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"items", "page", "page_size", "total"}
    assert isinstance(cuerpo["items"], list)
    assert len(cuerpo["items"]) > 0
    assert set(cuerpo["items"][0]) == {
        "id",
        "method",
        "path",
        "status_code",
        "actor_id",
        "actor_username",
        "created_at",
    }


async def test_sin_sesion_recibe_401(cliente):
    r = await cliente.get("/api/v1/admin/audit-log")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_rol_operador_recibe_403(cliente_operador):
    r = await cliente_operador.get("/api/v1/admin/audit-log")
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"
