import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def _error_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "error": {"code": code, "message": message, "details": details},
    }


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(code=exc.code, message=exc.message, details=exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_response(
                code="INVALID_REQUEST",
                message="Erro de validacao no corpo da requisicao.",
                details=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro interno nao tratado: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content=_error_response(
                code="INTERNAL_SERVER_ERROR",
                message="Falha interna ao processar a requisicao.",
            ),
        )

