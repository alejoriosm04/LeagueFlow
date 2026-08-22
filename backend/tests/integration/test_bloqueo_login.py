"""Integration tests — specs/017-bloqueo-login.

Los 7 Acceptance Scenarios de la spec (4 de la Historia 1, 3 de la Historia 2)
más los edge cases. Cada test nombra el escenario que verifica; Principio II de
la constitución: toda regla de negocio tiene una prueba que la afirma.

Los helpers viven aquí y NO en `conftest.py`, a propósito: esta HU se desarrolla
en paralelo con las specs 013-016 y tocar el conftest compartido arriesgaría sus
suites (tasks.md §Notes).
"""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from src.auth.models import IntentoDeLogin
from src.core.config import get_settings
from src.core.db import SessionLocal

from tests.conftest import CLAVE_INCORRECTA, USUARIO_INEXISTENTE, USUARIO_ORGANIZADOR

pytestmark = pytest.mark.asyncio


# --- helpers locales ------------------------------------------------------
async def fallar_n_veces(cliente, username: str, n: int) -> list:
    """`n` intentos de login fallidos consecutivos contra `username`."""
    respuestas = []
    for _ in range(n):
        respuestas.append(
            await cliente.post(
                "/api/v1/auth/login", json={"username": username, "password": CLAVE_INCORRECTA}
            )
        )
    return respuestas


async def fallar_una_vez(cliente, username: str):
    """Un único intento de login fallido. Devuelve la respuesta."""
    return (await fallar_n_veces(cliente, username, 1))[0]


async def leer_intento(username: str) -> IntentoDeLogin | None:
    """Fila de `login_attempts` del identificador, o None si no existe."""
    async with SessionLocal() as s:
        res = await s.execute(
            select(IntentoDeLogin).where(IntentoDeLogin.username_normalizado == username.lower())
        )
        return res.scalar_one_or_none()


async def caducar_bloqueo(username: str) -> None:
    """Mueve `blocked_until` al pasado.

    El desbloqueo es una comparación de timestamps, no un job (research.md §8),
    así que expirar un bloqueo no necesita `sleep` ni relojes falsos.
    """
    async with SessionLocal() as s:
        res = await s.execute(
            select(IntentoDeLogin).where(IntentoDeLogin.username_normalizado == username.lower())
        )
        fila = res.scalar_one()
        fila.blocked_until = datetime.now(UTC) - timedelta(seconds=1)
        await s.commit()


def umbral() -> int:
    return get_settings().login_max_failed_attempts


# --- Historia 1: bloquear -------------------------------------------------
async def test_h1_as1_superar_el_umbral_bloquea(cliente, organizador_creado):
    """H1-AS1: superado el umbral de fallos, el identificador queda bloqueado."""
    fallos = await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, umbral())
    assert [r.status_code for r in fallos] == [401] * umbral()

    siguiente = await fallar_una_vez(cliente, USUARIO_ORGANIZADOR)
    assert siguiente.status_code == 429
    assert siguiente.json()["error"]["code"] == "login_locked"


async def test_h1_as2_bloqueado_rechaza_la_clave_correcta(
    cliente, organizador_creado, credenciales_organizador
):
    """H1-AS2: durante el bloqueo ni la contraseña correcta pasa (FR-003).

    Es el núcleo de la historia: la clave es la buena y aun así se rechaza.
    """
    await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, umbral())

    r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert r.status_code == 429
    assert r.json()["error"]["code"] == "login_locked"
    assert "lf_session" not in r.cookies


async def test_h1_as3_el_bloqueo_no_afecta_a_otro_usuario(
    cliente, organizador_creado, operador_creado, credenciales_operador
):
    """H1-AS3: un identificador bloqueado no interfiere con nadie más (SC-004)."""
    await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, umbral())

    otro = await cliente.post("/api/v1/auth/login", json=credenciales_operador)
    assert otro.status_code == 200
    assert "lf_session" in otro.cookies


async def test_h1_as4_el_bloqueo_no_revela_si_el_identificador_existe(cliente, organizador_creado):
    """H1-AS4: el 429 es idéntico para un identificador registrado y uno inventado.

    FR-006: el bloqueo se aplica igual a ambos, así que la respuesta no permite
    deducir si la cuenta existe.
    """
    await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, umbral())
    await fallar_n_veces(cliente, USUARIO_INEXISTENTE, umbral())

    existente = await fallar_una_vez(cliente, USUARIO_ORGANIZADOR)
    inventado = await fallar_una_vez(cliente, USUARIO_INEXISTENTE)

    assert existente.status_code == inventado.status_code == 429
    assert existente.json() == inventado.json()


# --- Historia 1: edge cases ----------------------------------------------
async def test_edge_alternar_mayusculas_suma_al_mismo_contador(cliente, organizador_creado):
    """Edge: el conteo es normalizado, así que alternar mayúsculas no lo esquiva."""
    variantes = [
        USUARIO_ORGANIZADOR.upper(),
        USUARIO_ORGANIZADOR.capitalize(),
        USUARIO_ORGANIZADOR.lower(),
    ]
    for i in range(umbral()):
        r = await fallar_una_vez(cliente, variantes[i % len(variantes)])
        assert r.status_code == 401, f"el intento {i + 1} debería seguir siendo 401"

    # Una sola fila para todas las variantes: el contador es compartido.
    async with SessionLocal() as s:
        filas = (await s.execute(select(IntentoDeLogin))).scalars().all()
        assert len(filas) == 1
        assert filas[0].username_normalizado == USUARIO_ORGANIZADOR.lower()

    bloqueado = await fallar_una_vez(cliente, USUARIO_ORGANIZADOR.upper())
    assert bloqueado.status_code == 429
    assert bloqueado.json()["error"]["code"] == "login_locked"


async def test_edge_intentos_simultaneos_no_saltan_el_bloqueo(cliente, organizador_creado):
    """Edge: el conteo es consistente ante intentos concurrentes (research.md §6).

    Un `SELECT`+`UPDATE` en Python permitiría que dos peticiones leyeran 4 y
    ambas escribieran 5 (*lost update*), dejando el bloqueo sin activar. El
    UPSERT atómico lo impide.
    """
    peticiones = [
        cliente.post(
            "/api/v1/auth/login",
            json={"username": USUARIO_ORGANIZADOR, "password": CLAVE_INCORRECTA},
        )
        for _ in range(umbral())
    ]
    respuestas = await asyncio.gather(*peticiones)
    assert all(r.status_code == 401 for r in respuestas)

    siguiente = await fallar_una_vez(cliente, USUARIO_ORGANIZADOR)
    assert siguiente.status_code == 429, "los intentos simultáneos no activaron el bloqueo"


async def test_edge_el_bloqueo_no_se_auto_extiende(cliente, organizador_creado):
    """Edge: reintentar durante el bloqueo no empuja la fecha de expiración.

    Si lo hiciera, un atacante persistente mantendría al usuario legítimo
    bloqueado para siempre y FR-004 dejaría de cumplirse.
    """
    await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, umbral())
    fila = await leer_intento(USUARIO_ORGANIZADOR)
    expiracion_original = fila.blocked_until
    assert expiracion_original is not None

    await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, 3)

    despues = await leer_intento(USUARIO_ORGANIZADOR)
    assert despues.blocked_until == expiracion_original
    # Tampoco se cuentan: el gate rechaza antes de llegar al contador.
    assert despues.failed_count == fila.failed_count


async def test_fr007_el_umbral_es_configurable(cliente, organizador_creado, monkeypatch):
    """FR-007: cambiar `LOGIN_MAX_FAILED_ATTEMPTS` cambia cuándo salta el bloqueo.

    Con umbral 2 el bloqueo llega al tercer intento, no al sexto. Cubre además
    el edge case "si el umbral cambia entre intentos, se aplica en cada
    comprobación": se lee en cada request, no se congela al arrancar.
    """
    from src.core.config import get_settings as _get_settings

    monkeypatch.setenv("LOGIN_MAX_FAILED_ATTEMPTS", "2")
    _get_settings.cache_clear()
    try:
        assert _get_settings().login_max_failed_attempts == 2

        primeros = await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, 2)
        assert [r.status_code for r in primeros] == [401, 401]

        tercero = await fallar_una_vez(cliente, USUARIO_ORGANIZADOR)
        assert tercero.status_code == 429
        assert tercero.json()["error"]["code"] == "login_locked"
    finally:
        # Sin esto el umbral de 2 contaminaría el resto de la suite.
        _get_settings.cache_clear()


# --- Historia 2: desbloquear ---------------------------------------------
async def test_h2_as1_el_bloqueo_caduca_y_el_login_vuelve_a_funcionar(
    cliente, organizador_creado, credenciales_organizador
):
    """H2-AS1: expirado el periodo, el login correcto vuelve a dar 200 (FR-004).

    El desbloqueo no tiene código propio: es la propia condición del gate
    (`blocked_until > now()`). No hay job que esperar, así que el test mueve la
    expiración al pasado en vez de dormir 15 minutos.
    """
    await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, umbral())
    bloqueado = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert bloqueado.status_code == 429

    await caducar_bloqueo(USUARIO_ORGANIZADOR)

    r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert r.status_code == 200
    assert "lf_session" in r.cookies


async def test_h2_as2_acertar_antes_del_umbral_reinicia_el_conteo(
    cliente, organizador_creado, credenciales_organizador
):
    """H2-AS2: un login correcto pone el contador a cero (FR-005).

    3 fallos -> 1 acierto -> 3 fallos más sigue en 401. Sin el reinicio serían
    6 fallos acumulados y el último habría devuelto 429.
    """
    assert umbral() == 5, "el escenario está calculado para el umbral por defecto"

    primeros = await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, 3)
    assert [r.status_code for r in primeros] == [401, 401, 401]

    acierto = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert acierto.status_code == 200

    despues = await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, 3)
    assert [r.status_code for r in despues] == [401, 401, 401], (
        "el conteo no se reinició tras el login correcto"
    )


async def test_h2_as3_acertar_tras_el_desbloqueo_deja_el_conteo_en_cero(
    cliente, organizador_creado, credenciales_organizador
):
    """H2-AS3: tras el login correcto posterior al desbloqueo no queda fila."""
    await fallar_n_veces(cliente, USUARIO_ORGANIZADOR, umbral())
    await caducar_bloqueo(USUARIO_ORGANIZADOR)

    r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert r.status_code == 200

    assert await leer_intento(USUARIO_ORGANIZADOR) is None
