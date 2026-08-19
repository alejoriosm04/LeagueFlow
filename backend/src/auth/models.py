"""Modelos de autenticación.

Definidos en specs/001-fundacion-y-autenticacion/data-model.md §User y §Session.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
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


__all__ = ["Usuario", "Sesion", "func"]
