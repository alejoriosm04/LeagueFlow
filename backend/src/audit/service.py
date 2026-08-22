"""Reglas de la auditoría (FR-001 a FR-007): registrar() y listar()."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audit.models import AuditLogEntry
from src.auth.models import Usuario


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def registrar(
        self, method: str, path: str, status_code: int, actor: Usuario | None
    ) -> AuditLogEntry:
        """Guarda una fila de auditoría (FR-001, FR-003).

        Recibe el actor ya resuelto (no reresuelve la sesión — eso lo hace
        `AuditMiddleware`, research.md §3). Snapshot de `actor_id`/
        `actor_username` en el momento de escribir; ambos `null` cuando el
        actor no es determinable (FR-004).
        """
        entrada = AuditLogEntry(
            method=method,
            path=path,
            status_code=status_code,
            actor_id=actor.id if actor is not None else None,
            actor_username=actor.username if actor is not None else None,
        )
        self.db.add(entrada)
        await self.db.commit()
        return entrada

    async def listar(self, page: int, page_size: int) -> tuple[list[AuditLogEntry], int]:
        """FR-005: orden `created_at` descendente (más reciente primero)."""
        total = await self.db.scalar(select(func.count()).select_from(AuditLogEntry)) or 0
        res = await self.db.execute(
            select(AuditLogEntry)
            .order_by(AuditLogEntry.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(res.scalars()), total
