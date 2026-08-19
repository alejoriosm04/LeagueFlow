"""Reglas de negocio de autenticación (FR-004 a FR-010)."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import Sesion, Usuario
from src.auth.security import hashear_password, verificar_password
from src.core.config import get_settings
from src.core.errors import ErrorDeNegocio

# FR-010: la misma respuesta para "no existe" y "clave incorrecta", de modo que
# no se pueda deducir si un identificador está registrado.
_CREDENCIALES_INVALIDAS = ErrorDeNegocio(
    code="invalid_credentials",
    message="Usuario o contraseña incorrectos.",
    status_code=status.HTTP_401_UNAUTHORIZED,
)

# Hash señuelo, generado una sola vez al importar el módulo. Verificar contra
# él cuando el usuario no existe iguala el tiempo de respuesta y evita deducir
# qué identificadores están registrados (checklist security CHK017). Calcularlo
# una vez, y no en cada intento fallido, ahorra un bcrypt completo por request.
_HASH_SENUELO = hashear_password(secrets.token_urlsafe(32))


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()

    # --- usuarios --------------------------------------------------------
    async def crear_usuario(
        self, username: str, password: str, role: str, creado_por: uuid.UUID | None
    ) -> Usuario:
        existente = await self.db.execute(
            select(Usuario).where(func.lower(Usuario.username) == username.lower())
        )
        if existente.scalar_one_or_none() is not None:
            raise ErrorDeNegocio(
                code="username_already_exists",
                message="Ya existe un usuario con ese identificador.",
                status_code=status.HTTP_409_CONFLICT,
                field="username",
            )

        usuario = Usuario(
            username=username,
            password_hash=hashear_password(password),
            role=role,
            created_by=creado_por,
        )
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario

    async def listar_usuarios(self, page: int, page_size: int) -> tuple[list[Usuario], int]:
        total = await self.db.scalar(select(func.count()).select_from(Usuario)) or 0
        res = await self.db.execute(
            select(Usuario)
            .order_by(Usuario.created_at)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total

    # --- sesiones --------------------------------------------------------
    async def autenticar(self, username: str, password: str) -> Usuario:
        res = await self.db.execute(
            select(Usuario).where(func.lower(Usuario.username) == username.lower())
        )
        usuario = res.scalar_one_or_none()

        if usuario is None or usuario.status != "active":
            verificar_password(password, _HASH_SENUELO)
            raise _CREDENCIALES_INVALIDAS

        if not verificar_password(password, usuario.password_hash):
            raise _CREDENCIALES_INVALIDAS

        return usuario

    async def crear_sesion(self, usuario: Usuario) -> Sesion:
        sesion = Sesion(
            user_id=usuario.id,
            expires_at=datetime.now(UTC) + timedelta(seconds=self.settings.session_ttl_seconds),
        )
        self.db.add(sesion)
        await self.db.commit()
        await self.db.refresh(sesion)
        return sesion

    async def obtener_sesion_valida(self, token: str) -> Sesion | None:
        try:
            sesion_id = uuid.UUID(token)
        except ValueError:
            return None

        res = await self.db.execute(select(Sesion).where(Sesion.id == sesion_id))
        sesion = res.scalar_one_or_none()
        if sesion is None or sesion.revoked_at is not None:
            return None
        if sesion.expires_at <= datetime.now(UTC):
            return None

        # FR-006: expiración por INACTIVIDAD, no TTL fijo — cada request válido
        # corre la ventana hacia adelante (research.md §10).
        sesion.expires_at = datetime.now(UTC) + timedelta(seconds=self.settings.session_ttl_seconds)
        await self.db.commit()
        return sesion

    async def revocar_sesion(self, sesion: Sesion) -> None:
        sesion.revoked_at = datetime.now(UTC)
        await self.db.commit()
