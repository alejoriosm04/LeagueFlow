"""Endpoint de auditoría — contracts/audit.openapi.yaml."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.schemas import AuditLogEntry, PaginatedAuditLog
from src.audit.service import AuditService
from src.auth.dependencies import requiere_rol
from src.auth.models import Usuario
from src.core.db import get_db

router = APIRouter(tags=["audit"])


@router.get("/admin/audit-log")
async def listar_audit_log(
    _actor: Usuario = Depends(requiere_rol("organizador")),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedAuditLog:
    """FR-005, FR-006: solo organizador; orden created_at DESC."""
    servicio = AuditService(db)
    entradas, total = await servicio.listar(page, page_size)
    return PaginatedAuditLog(
        items=[AuditLogEntry.model_validate(e) for e in entradas],
        page=page,
        page_size=page_size,
        total=total,
    )
