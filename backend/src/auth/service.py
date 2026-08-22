"""Reglas de negocio de autenticación (FR-004 a FR-010).

El bloqueo por intentos fallidos lo añade specs/017-bloqueo-login: un gate
antes de verificar la contraseña y un contador después de que falle.
"""

import math
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import status
from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import IntentoDeLogin, Sesion, Usuario
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

    # --- bloqueo por intentos fallidos (specs/017) -----------------------
    @staticmethod
    def _clave_de_intentos(username: str) -> str:
        """Identificador normalizado con el que se cuenta y se bloquea.

        Es EXACTAMENTE la misma expresión con la que `autenticar` busca al
        usuario (`username.lower()`), para que el identificador contado y el
        buscado sean siempre el mismo y el bloqueo no se esquive alternando
        mayúsculas (research.md §2). Sin `trim()`: el lookup tampoco lo aplica.
        """
        return username.lower()

    async def _leer_intentos(self, clave: str) -> IntentoDeLogin | None:
        res = await self.db.execute(
            select(IntentoDeLogin).where(IntentoDeLogin.username_normalizado == clave)
        )
        return res.scalar_one_or_none()

    def _error_bloqueado(self, segundos_restantes: float) -> ErrorDeNegocio:
        """429 con `Retry-After`, según contracts/auth-lockout.openapi.yaml.

        El mensaje habla de la DURACIÓN configurada, no del tiempo restante: es
        constante, y así el cuerpo del 429 es idéntico para un identificador
        registrado y para uno inventado (FR-006). El detalle exacto de cuánto
        falta viaja en `Retry-After`, que es lo que pide FR-002.
        """
        minutos = max(1, math.ceil(self.settings.login_lockout_seconds / 60))
        return ErrorDeNegocio(
            code="login_locked",
            message=(
                "Demasiados intentos fallidos. Vuelve a intentarlo en "
                f"{minutos} {'minuto' if minutos == 1 else 'minutos'}."
            ),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": str(max(1, math.ceil(segundos_restantes)))},
        )

    async def _registrar_fallo(self, clave: str) -> None:
        """Suma un fallo y, si alcanza el umbral, bloquea el identificador.

        El incremento es un UPSERT atómico: un `SELECT`+`UPDATE` en Python
        dejaría que dos intentos simultáneos leyeran 4 y ambos escribieran 5
        (*lost update*), y el bloqueo no llegaría a activarse (research.md §6).
        """
        ahora = datetime.now(UTC)
        sentencia = (
            pg_insert(IntentoDeLogin)
            .values(
                id=uuid.uuid4(),
                username_normalizado=clave,
                failed_count=1,
                last_attempt_at=ahora,
            )
            .on_conflict_do_update(
                index_elements=[IntentoDeLogin.username_normalizado],
                set_={
                    "failed_count": IntentoDeLogin.__table__.c.failed_count + 1,
                    "last_attempt_at": ahora,
                },
            )
            .returning(IntentoDeLogin.__table__.c.failed_count)
        )
        fallos = await self.db.scalar(sentencia)

        if fallos is not None and fallos >= self.settings.login_max_failed_attempts:
            # Se reinicia el contador al bloquear: cuando el bloqueo caduque, el
            # usuario legítimo vuelve a tener el cupo completo de intentos. Si
            # quedara en el umbral, el siguiente fallo re-bloquearía al instante
            # y FR-004 ("vuelve a funcionar normalmente") no se cumpliría.
            await self.db.execute(
                update(IntentoDeLogin)
                .where(IntentoDeLogin.username_normalizado == clave)
                .values(
                    failed_count=0,
                    blocked_until=ahora + timedelta(seconds=self.settings.login_lockout_seconds),
                )
            )

        # El commit va ANTES del `raise` de credenciales inválidas: si se lanzara
        # primero, la sesión se descartaría con la petición, el incremento se
        # perdería y el bloqueo no se activaría nunca (research.md §7).
        await self.db.commit()

    async def _olvidar_fallos(self, clave: str) -> None:
        """Borra el contador tras un login correcto (FR-005).

        Cubre los dos escenarios de la Historia 2: fallar y luego acertar
        reinicia el conteo, y acertar tras el desbloqueo lo deja en cero.
        """
        await self.db.execute(
            delete(IntentoDeLogin).where(IntentoDeLogin.username_normalizado == clave)
        )
        await self.db.commit()

    # --- sesiones --------------------------------------------------------
    async def autenticar(self, username: str, password: str) -> Usuario:
        clave = self._clave_de_intentos(username)

        # El gate va ANTES de buscar al usuario y de verificar la contraseña.
        # Es lo que hace cumplir FR-003: si se verificara primero, un acierto se
        # colaría durante el bloqueo. Ahorra además un bcrypt por intento
        # mientras dura un ataque (research.md §5).
        intentos = await self._leer_intentos(clave)
        if intentos is not None and intentos.blocked_until is not None:
            restante = (intentos.blocked_until - datetime.now(UTC)).total_seconds()
            if restante > 0:
                # No se cuenta ni se empuja `blocked_until`: el bloqueo no se
                # auto-extiende, o un atacante persistente dejaría al usuario
                # legítimo bloqueado para siempre.
                raise self._error_bloqueado(restante)

        res = await self.db.execute(
            select(Usuario).where(func.lower(Usuario.username) == username.lower())
        )
        usuario = res.scalar_one_or_none()

        if usuario is None or usuario.status != "active":
            verificar_password(password, _HASH_SENUELO)
            await self._registrar_fallo(clave)
            raise _CREDENCIALES_INVALIDAS

        if not verificar_password(password, usuario.password_hash):
            await self._registrar_fallo(clave)
            raise _CREDENCIALES_INVALIDAS

        await self._olvidar_fallos(clave)
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
