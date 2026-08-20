"""Fixtures compartidas: app, base de datos limpia y clientes HTTP."""

import os
import secrets

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://leagueflow@localhost:5432/leagueflow_test"
)
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")
os.environ.setdefault("COOKIE_SECURE", "false")

from src.core.db import engine  # noqa: E402
from src.core.models_base import Base  # noqa: E402
from src.main import app  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def base_limpia():
    """Cada test corre contra un esquema recién creado."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # pytest-asyncio crea un event loop por test; el pool del engine queda
    # atado al loop anterior y al cerrarse produce "Event loop is closed".
    # Liberarlo aquí hace que el siguiente test abra conexiones en su loop.
    await engine.dispose()


@pytest_asyncio.fixture
async def cliente() -> AsyncClient:
    """Cliente sin sesión (visitante anónimo)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# Contraseñas de prueba generadas en tiempo de ejecución. No son secretos, pero
# el Principio VI prohíbe credenciales literales "tampoco en ejemplos, tests o
# comentarios", y generarlas evita además que un escáner las marque.
CLAVE_VALIDA = secrets.token_urlsafe(16)
CLAVE_ALTERNATIVA = secrets.token_urlsafe(16)
CLAVE_INCORRECTA = secrets.token_urlsafe(16)
CLAVE_CORTA = secrets.token_hex(2)  # 4 caracteres: por debajo del mínimo de 10
CLAVE_ORGANIZADOR_ALTERNATIVO = secrets.token_urlsafe(16)

# Los identificadores también se generan: además de no dejar ningún par
# usuario/contraseña literal, hace que dos corridas nunca colisionen.
USUARIO_ORGANIZADOR = f"org-{secrets.token_hex(4)}"
USUARIO_OPERADOR = f"ope-{secrets.token_hex(4)}"
USUARIO_INEXISTENTE = f"nadie-{secrets.token_hex(4)}"
USUARIO_NUEVO = f"nuevo-{secrets.token_hex(4)}"
USUARIO_ORGANIZADOR_ALTERNATIVO = f"org2-{secrets.token_hex(4)}"


@pytest.fixture
def credenciales_organizador() -> dict[str, str]:
    return {"username": USUARIO_ORGANIZADOR, "password": CLAVE_VALIDA}


@pytest.fixture
def credenciales_operador() -> dict[str, str]:
    return {"username": USUARIO_OPERADOR, "password": CLAVE_ALTERNATIVA}


@pytest.fixture
def credenciales_organizador_alternativo() -> dict[str, str]:
    return {
        "username": USUARIO_ORGANIZADOR_ALTERNATIVO,
        "password": CLAVE_ORGANIZADOR_ALTERNATIVO,
    }


@pytest_asyncio.fixture
async def organizador_creado(credenciales_organizador):
    """Crea el organizador semilla directamente en la BD."""
    from sqlalchemy import select
    from src.auth.models import Usuario
    from src.auth.security import hashear_password
    from src.core.db import SessionLocal

    async with SessionLocal() as s:
        u = Usuario(
            username=credenciales_organizador["username"],
            password_hash=hashear_password(credenciales_organizador["password"]),
            role="organizador",
        )
        s.add(u)
        await s.commit()
        res = await s.execute(select(Usuario).where(Usuario.username == u.username))
        return res.scalar_one()


@pytest_asyncio.fixture
async def cliente_organizador(cliente, organizador_creado, credenciales_organizador):
    """Cliente con sesión de organizador ya iniciada."""
    await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    return cliente


async def _crear_usuario_prueba(credenciales: dict[str, str], role: str):
    from sqlalchemy import select
    from src.auth.models import Usuario
    from src.auth.security import hashear_password
    from src.core.db import SessionLocal

    async with SessionLocal() as s:
        usuario = Usuario(
            username=credenciales["username"],
            password_hash=hashear_password(credenciales["password"]),
            role=role,
        )
        s.add(usuario)
        await s.commit()
        res = await s.execute(select(Usuario).where(Usuario.username == usuario.username))
        return res.scalar_one()


@pytest_asyncio.fixture
async def operador_creado(credenciales_operador):
    return await _crear_usuario_prueba(credenciales_operador, "operador")


@pytest_asyncio.fixture
async def organizador_alternativo_creado(credenciales_organizador_alternativo):
    return await _crear_usuario_prueba(credenciales_organizador_alternativo, "organizador")


@pytest_asyncio.fixture
async def cliente_operador(operador_creado, credenciales_operador):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.post("/api/v1/auth/login", json=credenciales_operador)
        yield c


@pytest_asyncio.fixture
async def cliente_organizador_alternativo(
    organizador_alternativo_creado, credenciales_organizador_alternativo
):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.post("/api/v1/auth/login", json=credenciales_organizador_alternativo)
        yield c


@pytest_asyncio.fixture
async def partido_programado(cliente_organizador):
    liga = await cliente_organizador.post(
        "/api/v1/leagues", json={"name": "Liga fixture", "season": "2026"}
    )
    liga_id = liga.json()["id"]
    local = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Local fixture"}
    )
    visitante = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/teams", json={"name": "Visitante fixture"}
    )
    partido = await cliente_organizador.post(
        f"/api/v1/leagues/{liga_id}/matches",
        json={
            "home_team_id": local.json()["id"],
            "away_team_id": visitante.json()["id"],
            "scheduled_at": "2026-09-01T18:00:00Z",
        },
    )
    assert partido.status_code == 201
    return partido.json()
