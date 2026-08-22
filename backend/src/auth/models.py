"""Modelos de autenticación.

Definidos en specs/001-fundacion-y-autenticacion/data-model.md §User y §Session.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models_base import Base, TimestampCreated, UUIDPrimaryKey


class Usuario(Base, UUIDPrimaryKey, TimestampCreated):
    """Persona autenticada que opera el sistema (organizador u operador)."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # FR-008: toda escritura queda atribuida a su autor. Nulo solo en el
    # usuario semilla, que crea el script de despliegue y no otro usuario.
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class Sesion(Base, UUIDPrimaryKey, TimestampCreated):
    """Sesión de servidor. El id es el token opaco que viaja en la cookie.

    Sin `created_by` a propósito: una sesión pertenece a quien se autenticó, no
    la crea otro usuario en su nombre (data-model.md §Session).
    """

    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def esta_activa(self) -> bool:
        ahora = datetime.now(tz=self.expires_at.tzinfo)
        return self.revoked_at is None and self.expires_at > ahora


class IntentoDeLogin(Base, UUIDPrimaryKey, TimestampCreated):
    """Contador de fallos consecutivos por identificador (specs/017, FR-001).

    No es un log: hay una sola fila por identificador normalizado, se
    sobrescribe en cada intento fallido y se borra al iniciar sesión bien.

    Sin clave foránea a `users` a propósito: FR-001 obliga a contar intentos
    contra identificadores que NO existen, y una FK haría imposible registrar
    justamente ese caso. Es también lo que impide que la fila revele si el
    identificador está registrado (FR-006). Ver research.md §1.
    """

    __tablename__ = "login_attempts"

    # Ya normalizado en Python (`username.lower()`), la misma expresión con la
    # que `AuthService.autenticar` busca al usuario: el bloqueo no se esquiva
    # alternando mayúsculas. Columna normalizada, NO índice funcional
    # `lower(trim(...))` — así `alembic --autogenerate` no lo verá cambiar
    # espuriamente en specs futuras (AGENTS.md). El UNIQUE es además el
    # `ON CONFLICT target` del UPSERT atómico del conteo (research.md §6).
    username_normalizado: Mapped[str] = mapped_column(
        String(60), unique=True, nullable=False, index=True
    )
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Nulo o en el pasado significa "no bloqueado": el desbloqueo es implícito,
    # por comparación de timestamps, sin job ni scheduler (research.md §8).
    blocked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


__all__ = ["Usuario", "Sesion", "IntentoDeLogin", "func"]
