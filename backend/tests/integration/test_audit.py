"""Integration tests — auditoría de operaciones administrativas (specs/016-auditoria).

US1 (T007): la captura transversal escribe `audit_logs` sin pasar por el
endpoint de lectura (todavía no existe, es US2) — se consulta la BD
directamente. US2 (T013) se añade a continuación en este mismo archivo.
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from src.audit.models import AuditLogEntry
from src.auth.models import Sesion
from src.core.db import SessionLocal

pytestmark = pytest.mark.asyncio


def _en_utc(momento: datetime) -> datetime:
    """SQLite (sustituto local, ver AGENTS.md) pierde el tzinfo al releer
    columnas `DateTime(timezone=True)`; Postgres (CI/producción) lo conserva.
    Normaliza para que la comparación sea válida en ambos casos."""
    return momento if momento.tzinfo is not None else momento.replace(tzinfo=UTC)


async def _contar_audit_logs() -> int:
    async with SessionLocal() as s:
        return await s.scalar(select(func.count()).select_from(AuditLogEntry)) or 0


async def _ultima_entrada(method: str, contiene_path: str) -> AuditLogEntry | None:
    async with SessionLocal() as s:
        res = await s.execute(
            select(AuditLogEntry)
            .where(AuditLogEntry.method == method, AuditLogEntry.path.contains(contiene_path))
            .order_by(AuditLogEntry.created_at.desc())
        )
        return res.scalars().first()


async def test_as1_escritura_exitosa_queda_registrada(cliente_organizador, organizador_creado):
    """AC1/US1, FR-001: POST /leagues exitoso -> fila con actor, acción y fecha."""
    r = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga Auditoria", "season": "2026"}
    )
    assert r.status_code == 201

    entrada = await _ultima_entrada("POST", "/leagues")
    assert entrada is not None
    assert entrada.status_code == 201
    assert entrada.actor_id == organizador_creado.id
    assert entrada.actor_username == organizador_creado.username
    assert _en_utc(entrada.created_at) >= datetime.now(UTC) - timedelta(minutes=1)


async def test_as2_lectura_no_se_registra(cliente, cliente_organizador):
    """AC2/US1, FR-002: una consulta de lectura no produce ninguna fila nueva."""
    await cliente_organizador.post("/api/v1/leagues", json={"name": "Liga X", "season": "2026"})
    antes = await _contar_audit_logs()

    r = await cliente.get("/api/v1/leagues")
    assert r.status_code == 200

    despues = await _contar_audit_logs()
    assert despues == antes


async def test_escritura_que_falla_por_regla_de_negocio_no_se_registra(cliente_organizador):
    """Clarificación de spec.md: solo se registran escrituras EXITOSAS."""
    datos = {"name": "Liga Duplicada", "season": "2026"}
    assert (await cliente_organizador.post("/api/v1/leagues", json=datos)).status_code == 201
    antes = await _contar_audit_logs()

    repetido = await cliente_organizador.post("/api/v1/leagues", json=datos)
    assert repetido.status_code == 409

    despues = await _contar_audit_logs()
    assert despues == antes


async def test_fr004_login_exitoso_registra_actor_no_determinable(
    cliente, organizador_creado, credenciales_organizador
):
    """FR-004: POST /auth/login exitoso -> actor_id/actor_username en null.

    La petición que CREA la sesión no trae todavía la cookie que
    identificaría al actor (research.md §3, Edge Case de spec.md).
    """
    r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert r.status_code == 200

    entrada = await _ultima_entrada("POST", "/auth/login")
    assert entrada is not None
    assert entrada.status_code == 200
    assert entrada.actor_id is None
    assert entrada.actor_username is None


async def test_ac3_ningun_registro_contiene_el_body(cliente_organizador):
    """AC3/US1, FR-003: por inspección de columnas, no hay dónde guardar el body."""
    await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga Body", "season": "2026", "description": "secreto"}
    )

    columnas = {c.name for c in AuditLogEntry.__table__.columns}
    assert columnas == {
        "id",
        "method",
        "path",
        "status_code",
        "actor_id",
        "actor_username",
        "created_at",
    }

    async with SessionLocal() as s:
        res = await s.execute(select(AuditLogEntry))
        entradas = list(res.scalars())
    assert len(entradas) > 0


# --- US2: consultar el historial ------------------------------------------


async def test_us2_ac1_historial_en_orden_created_at_desc(cliente_organizador):
    """AC1/US2, FR-005: filas devueltas de más reciente a más antigua."""
    for nombre in ("Liga Orden A", "Liga Orden B", "Liga Orden C"):
        r = await cliente_organizador.post(
            "/api/v1/leagues", json={"name": nombre, "season": "2026"}
        )
        assert r.status_code == 201

    r = await cliente_organizador.get("/api/v1/admin/audit-log")
    assert r.status_code == 200
    fechas = [item["created_at"] for item in r.json()["items"]]
    assert fechas == sorted(fechas, reverse=True)


async def test_us2_historial_vacio_devuelve_lista_vacia_sin_error(cliente, organizador_creado):
    """Edge Case de spec.md: audit_logs vacía -> 200 con items:[] y total:0.

    Un login vía HTTP normal ya queda auditado (FR-004), así que nunca deja
    `audit_logs` realmente vacía. Para probar el caso vacío de verdad, la
    sesión se crea directamente en la BD (sin pasar por POST /auth/login),
    igual que el Independent Test de US2 en tasks.md describe.
    """
    async with SessionLocal() as s:
        sesion = Sesion(
            user_id=organizador_creado.id,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        s.add(sesion)
        await s.commit()
        await s.refresh(sesion)
        token = str(sesion.id)

    cliente.cookies.set("lf_session", token)
    r = await cliente.get("/api/v1/admin/audit-log")
    assert r.status_code == 200
    assert r.json() == {"items": [], "page": 1, "page_size": 20, "total": 0}
