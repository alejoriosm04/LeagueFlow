"""Dependencias de FastAPI para sesión y control de rol (FR-003, FR-009)."""

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import Usuario
from src.auth.service import AuthService
from src.core.db import get_db
from src.core.errors import ErrorDeNegocio

NOMBRE_COOKIE = "lf_session"


async def usuario_opcional(request: Request, db: AsyncSession = Depends(get_db)) -> Usuario | None:
    """Usuario de la sesión, o None. Para rutas públicas (FR-002)."""
    token = request.cookies.get(NOMBRE_COOKIE)
    if not token:
        return None

    servicio = AuthService(db)
    sesion = await servicio.obtener_sesion_valida(token)
    if sesion is None:
        return None

    return await db.get(Usuario, sesion.user_id)


async def usuario_actual(usuario: Usuario | None = Depends(usuario_opcional)) -> Usuario:
    """Exige sesión válida. Toda ruta de escritura depende de esta (FR-003)."""
    if usuario is None:
        raise ErrorDeNegocio(
            code="not_authenticated",
            message="Inicia sesión para realizar esta operación.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return usuario


def requiere_rol(*roles: str) -> Callable[..., Coroutine[Any, Any, Usuario]]:
    """Exige que la sesión tenga uno de los roles indicados (FR-009)."""

    async def verificar(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.role not in roles:
            raise ErrorDeNegocio(
                code="insufficient_role",
                message="No tienes permisos suficientes para esta operación.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return usuario

    return verificar
