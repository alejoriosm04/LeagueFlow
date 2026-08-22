"""Modelo de auditoría — data-model.md §AuditLogEntry.

Entidad de solo inserción/lectura: no hay `updated_at` (el hecho es inmutable
una vez escrito) ni endpoint de edición o borrado.
"""

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models_base import Base, TimestampCreated, UUIDPrimaryKey


class AuditLogEntry(Base, UUIDPrimaryKey, TimestampCreated):
    """Entrada que documenta una operación de escritura exitosa (FR-001 a FR-004).

    Escrita únicamente por `AuditMiddleware` — ningún router de negocio la
    escribe directamente (research.md §1).
    """

    __tablename__ = "audit_logs"

    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)

    # FR-004: null cuando el actor no es determinable (p. ej. POST /auth/login
    # sin cookie previa). actor_username es un snapshot, no un join en lectura
    # (research.md §7).
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    actor_username: Mapped[str | None] = mapped_column(String(60), nullable=True)

    # Índice simple (no único, no funcional) para soportar el orden
    # "más reciente primero" de FR-005 (research.md §11, data-model.md).
    __table_args__ = (Index("ix_audit_logs_created_at", "created_at"),)


__all__ = ["AuditLogEntry"]
