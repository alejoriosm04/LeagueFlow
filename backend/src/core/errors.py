"""Envelope de error y manejadores globales.

Contrato: `contracts/conventions.md` §Envelope de error. Toda respuesta 4xx/5xx
tiene la forma {"error": {"code", "message", "field"}}.

FR-012 de la spec y Estándares de Seguridad de la constitución: NUNCA se expone
un stack trace ni un detalle interno al cliente.
"""

import logging
import uuid

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("leagueflow")


class ErrorDeNegocio(Exception):
    """Error esperado, con traducción directa al envelope.

    Cada subclase/instancia fija su `code` estable, que el frontend consume sin
    parsear el mensaje.
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field


def envelope(code: str, message: str, field: str | None = None) -> dict:
    return {"error": {"code": code, "message": message, "field": field}}


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorDeNegocio)
    async def _negocio(_: Request, exc: ErrorDeNegocio) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope(exc.code, exc.message, exc.field),
        )

    @app.exception_handler(RequestValidationError)
    async def _validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        primero = exc.errors()[0] if exc.errors() else {}
        loc = [p for p in primero.get("loc", []) if p != "body"]
        campo = ".".join(str(p) for p in loc) or None
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=envelope(
                "validation_error",
                primero.get("msg", "La solicitud no es válida."),
                campo,
            ),
        )

    @app.exception_handler(Exception)
    async def _inesperado(_: Request, exc: Exception) -> JSONResponse:
        # El detalle va al log del servidor; al cliente solo un identificador
        # con el que rastrearlo. FR-012.
        incidente = uuid.uuid4().hex[:12]
        logger.exception("Error inesperado [%s]", incidente, exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=envelope(
                "internal_error",
                f"Ocurrió un error inesperado. Identificador del incidente: {incidente}",
            ),
        )
