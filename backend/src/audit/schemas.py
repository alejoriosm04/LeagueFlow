"""Schemas de la API de auditoría — contracts/audit.openapi.yaml."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogEntry(BaseModel):
    """Respuesta pública de una entrada de auditoría."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    method: str
    path: str
    status_code: int
    actor_id: uuid.UUID | None
    actor_username: str | None
    created_at: datetime


class PaginatedAuditLog(BaseModel):
    """Envelope de paginación de conventions.md §Paginación."""

    items: list[AuditLogEntry]
    page: int
    page_size: int
    total: int
