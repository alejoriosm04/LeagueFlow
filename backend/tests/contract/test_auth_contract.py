"""Contract tests — la API cumple contracts/auth.openapi.yaml.

Verifica forma de request/response y códigos de estado, no reglas de negocio
(eso vive en tests/integration). Principio III: el contrato es la frontera.
"""

from pathlib import Path

import yaml

from tests.conftest import CLAVE_INCORRECTA, USUARIO_INEXISTENTE

CONTRATO = (
    Path(__file__).resolve().parents[3]
    / "specs/001-fundacion-y-autenticacion/contracts/auth.openapi.yaml"
)


def cargar_contrato() -> dict:
    return yaml.safe_load(CONTRATO.read_text(encoding="utf-8"))


def test_el_contrato_existe_y_es_valido():
    contrato = cargar_contrato()
    assert contrato["openapi"].startswith("3.")
    assert set(contrato["paths"]) == {"/auth/login", "/auth/logout", "/auth/me", "/users"}


async def test_login_responde_segun_contrato(cliente, organizador_creado, credenciales_organizador):
    r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
    assert r.status_code == 200

    # UserPublic: nunca incluye password_hash (schema del contrato).
    usuario = r.json()["user"]
    assert set(usuario) == {"id", "username", "role", "status"}
    assert usuario["role"] in {"organizador", "operador"}
    assert usuario["status"] in {"active", "inactive"}


async def test_me_sin_sesion_devuelve_user_null(cliente):
    r = await cliente.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json() == {"user": None}


async def test_users_get_devuelve_envelope_de_paginacion(cliente_organizador):
    """CHK006: GET /users sigue el envelope de conventions.md, no un array plano."""
    r = await cliente_organizador.get("/api/v1/users")
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"items", "page", "page_size", "total"}
    assert isinstance(cuerpo["items"], list)


async def test_errores_usan_el_envelope_estandar(cliente):
    """Todo 4xx tiene la forma {error:{code,message,field}}."""
    r = await cliente.post(
        "/api/v1/auth/login", json={"username": USUARIO_INEXISTENTE, "password": CLAVE_INCORRECTA}
    )
    assert r.status_code == 401
    assert set(r.json()["error"]) == {"code", "message", "field"}


async def test_cookie_de_sesion_tiene_los_atributos_del_contrato(
    cliente, organizador_creado, credenciales_organizador, monkeypatch
):
    """conventions.md: httpOnly + Secure + SameSite=None + Path=/ (research.md §4).

    Se fuerza COOKIE_SECURE=true porque el contrato describe la configuración
    de PRODUCCIÓN. En local la app cae a SameSite=lax a propósito: los
    navegadores rechazan SameSite=None sin Secure, y en desarrollo se sirve por
    http. Este test protege justamente el caso que no se puede reproducir a
    mano en local y que rompería el login entre Vercel y Railway.
    """
    from src.core.config import get_settings

    monkeypatch.setenv("COOKIE_SECURE", "true")
    get_settings.cache_clear()
    try:
        r = await cliente.post("/api/v1/auth/login", json=credenciales_organizador)
        set_cookie = r.headers.get("set-cookie", "").lower()
        assert "lf_session=" in set_cookie
        assert "httponly" in set_cookie
        assert "secure" in set_cookie
        assert "samesite=none" in set_cookie
        assert "path=/" in set_cookie
    finally:
        get_settings.cache_clear()


async def test_login_bloqueado_responde_segun_contrato_429(cliente):
    """specs/017 contracts/auth-lockout.openapi.yaml: 429 + Retry-After + envelope.

    Se usa un identificador INEXISTENTE a propósito: el contrato exige que el
    bloqueo se aplique igual exista o no la cuenta (FR-006), así que este test
    afirma de paso esa simetría.
    """
    from src.core.config import get_settings

    umbral = get_settings().login_max_failed_attempts
    for _ in range(umbral):
        await cliente.post(
            "/api/v1/auth/login",
            json={"username": USUARIO_INEXISTENTE, "password": CLAVE_INCORRECTA},
        )

    r = await cliente.post(
        "/api/v1/auth/login", json={"username": USUARIO_INEXISTENTE, "password": CLAVE_INCORRECTA}
    )

    assert r.status_code == 429
    # Retry-After: entero >= 1 (FR-002). El contrato lo marca `required: true`.
    retry_after = r.headers.get("retry-after")
    assert retry_after is not None, "la respuesta 429 debe traer la cabecera Retry-After"
    assert retry_after.isdigit()
    assert int(retry_after) >= 1

    # Mismo envelope que el resto de errores: no se inventan campos nuevos.
    cuerpo = r.json()["error"]
    assert set(cuerpo) == {"code", "message", "field"}
    assert cuerpo["code"] == "login_locked"
