"""Integration tests — los 7 Acceptance Scenarios de spec.md (User Story 1).

Cada test nombra el escenario que verifica. Principio II de la constitución:
toda regla de negocio tiene una prueba que la afirma.
"""

import time

import pytest
from sqlalchemy import select
from src.auth.models import Usuario
from src.core.db import SessionLocal

from tests.conftest import (
    CLAVE_ALTERNATIVA,
    CLAVE_CORTA,
    CLAVE_INCORRECTA,
    USUARIO_INEXISTENTE,
    USUARIO_NUEVO,
    USUARIO_ORGANIZADOR,
)

pytestmark = pytest.mark.asyncio


async def test_as1_login_valido_da_acceso(cliente, organizador_creado, credenciales_organizador):
    """AS1: credenciales válidas -> accede a las operaciones de su rol."""
    r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "organizador"
    assert "lf_session" in r.cookies

    me = await cliente.get("/api/v1/auth/me")
    assert me.json()["user"]["username"] == credenciales_organizador["username"]


async def test_as2_login_invalido_mensaje_generico(cliente, organizador_creado):
    """AS2: credenciales inválidas -> mensaje que no revela si el usuario existe."""
    inexistente = await cliente.post(
        "/api/v1/auth/login", json={"username": USUARIO_INEXISTENTE, "password": CLAVE_INCORRECTA}
    )
    mala_clave = await cliente.post(
        "/api/v1/auth/login", json={"username": USUARIO_ORGANIZADOR, "password": CLAVE_INCORRECTA}
    )

    assert inexistente.status_code == 401
    assert mala_clave.status_code == 401
    # FR-010: la respuesta debe ser indistinguible entre ambos casos.
    assert inexistente.json() == mala_clave.json()
    cuerpo = inexistente.json()["error"]
    assert cuerpo["code"] == "invalid_credentials"
    assert "no-existe" not in cuerpo["message"]


async def test_as3_consulta_sin_sesion_es_publica(cliente):
    """AS3: un visitante sin sesión consulta sin autenticarse."""
    r = await cliente.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["user"] is None


async def test_as4_escritura_sin_sesion_se_rechaza(cliente):
    """AS4: sin sesión, cualquier escritura se rechaza pidiendo iniciar sesión."""
    r = await cliente.post(
        "/api/v1/users",
        json={"username": USUARIO_NUEVO, "password": CLAVE_ALTERNATIVA, "role": "operador"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "not_authenticated"


async def test_as5_rol_insuficiente_se_rechaza(cliente, cliente_organizador, credenciales_operador):
    """AS5: un operador no puede crear usuarios (competencia del organizador)."""
    creado = await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    assert creado.status_code == 201

    await cliente.post("/api/v1/auth/logout")
    await cliente.post("/api/v1/auth/login", json=credenciales_operador)

    r = await cliente.post(
        "/api/v1/users",
        json={"username": USUARIO_NUEVO, "password": CLAVE_ALTERNATIVA, "role": "operador"},
    )
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "insufficient_role"


async def test_as6_logout_revoca_el_acceso(cliente_organizador):
    """AS6: tras cerrar sesión se pierde el acceso a las escrituras."""
    salida = await cliente_organizador.post("/api/v1/auth/logout")
    assert salida.status_code == 200

    r = await cliente_organizador.post(
        "/api/v1/users",
        json={"username": USUARIO_NUEVO, "password": CLAVE_ALTERNATIVA, "role": "operador"},
    )
    assert r.status_code == 401


async def test_as7_escritura_queda_atribuida_a_su_autor(cliente_organizador, organizador_creado):
    """AS7: toda escritura queda atribuida al usuario que la realizó (FR-008)."""
    r = await cliente_organizador.post(
        "/api/v1/users",
        json={"username": USUARIO_NUEVO, "password": CLAVE_ALTERNATIVA, "role": "operador"},
    )
    assert r.status_code == 201

    async with SessionLocal() as s:
        res = await s.execute(select(Usuario).where(Usuario.username == USUARIO_NUEVO))
        creado = res.scalar_one()
        assert creado.created_by == organizador_creado.id


async def test_sc003_login_responde_en_menos_de_5s(
    cliente, organizador_creado, credenciales_organizador
):
    """SC-003: el login se completa en menos de 5 segundos."""
    inicio = time.perf_counter()
    r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert r.status_code == 200
    assert time.perf_counter() - inicio < 5.0


async def test_username_duplicado_se_rechaza(cliente_organizador, credenciales_operador):
    """FR-004: el identificador de usuario es único."""
    primero = await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    assert primero.status_code == 201

    repetido = await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    assert repetido.status_code == 409
    assert repetido.json()["error"]["code"] == "username_already_exists"


async def test_password_corta_se_rechaza(cliente_organizador):
    """research.md §10: mínimo 10 caracteres."""
    r = await cliente_organizador.post(
        "/api/v1/users",
        json={"username": USUARIO_NUEVO, "password": CLAVE_CORTA, "role": "operador"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["field"] == "password"


async def test_password_nunca_se_expone(cliente_organizador, credenciales_operador):
    """FR-005: la contraseña no viaja en ninguna respuesta."""
    r = await cliente_organizador.post(
        "/api/v1/users", json={**credenciales_operador, "role": "operador"}
    )
    assert "password" not in r.text
    assert "hash" not in r.text.lower()
