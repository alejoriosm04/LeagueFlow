"""AuditMiddleware — ASGI puro (research.md §1-§6, FR-001 a FR-004, FR-007).

Intercepta toda petición POST/PUT/PATCH/DELETE que termina en 2xx y escribe
una fila en `audit_logs`. Solo inspecciona `scope["method"]`/`scope["path"]`
y el `status` del mensaje `http.response.start`: nunca lee ni reenvía
manualmente los bytes de `receive`/`send`, así que no tiene forma de acceder
al body de la petición ni de la respuesta (FR-003). No usa
`Starlette.BaseHTTPMiddleware`, que bufferiza la respuesta completa.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.audit.service import AuditService
from src.auth.dependencies import NOMBRE_COOKIE
from src.auth.models import Usuario
from src.auth.service import AuthService
from src.core.db import SessionLocal

logger = logging.getLogger("leagueflow")

_METODOS_AUDITADOS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class AuditMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # FR-002/FR-007: GET/HEAD/OPTIONS (y cualquier scope no-http, p. ej.
        # lifespan/websocket) se reenvían sin ningún trabajo adicional.
        if scope.get("type") != "http" or scope.get("method") not in _METODOS_AUDITADOS:
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]
        estado_capturado: dict[str, int] = {}

        async def send_wrapper(message: Message) -> None:
            # Solo se mira el `status` de http.response.start; todo mensaje
            # (incluido cada http.response.body) se reenvía sin tocarlo.
            if message["type"] == "http.response.start":
                estado_capturado["status"] = message["status"]
            await send(message)

        # research.md §2: sesión propia, independiente de la de la ruta de
        # negocio (que usa Depends(get_db)) — un fallo aquí no puede tumbar
        # ni revertir la transacción que esta auditoría describe.
        async with SessionLocal() as db:
            actor = await self._resolver_actor(scope, db)

            # research.md §4: la fila se escribe DESPUÉS de que la respuesta
            # ya se envió al cliente, nunca antes ni durante.
            await self.app(scope, receive, send_wrapper)

            status = estado_capturado.get("status")
            if status is not None and 200 <= status < 300:
                try:
                    await AuditService(db).registrar(method, path, status, actor)
                except Exception:
                    # Nunca relanza: perder una entrada de auditoría no debe
                    # afectar una respuesta que el cliente ya recibió.
                    logger.exception("No fue posible registrar la auditoría de %s %s", method, path)

    async def _resolver_actor(self, scope: Scope, db: AsyncSession) -> Usuario | None:
        """FR-004: reutiliza AuthService.obtener_sesion_valida tal cual (research.md §3)."""
        # Request(scope) sin `receive`: el constructor solo necesita el scope
        # para exponer .cookies, no consume el body.
        request = Request(scope)
        token = request.cookies.get(NOMBRE_COOKIE)
        if not token:
            return None

        sesion = await AuthService(db).obtener_sesion_valida(token)
        if sesion is None:
            return None

        return await db.get(Usuario, sesion.user_id)
