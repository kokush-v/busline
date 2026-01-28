from datetime import UTC, datetime
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ErrorCode(Enum):
    DATABASE = 'database'
    STORAGE = 'storage'


class ServerException(Exception):
    """Base exception for all server-side errors."""

    def __init__(
        self,
        message: str = 'An internal server error occurred',
        status: int = 500,
        details: dict | None = None,
        code: ErrorCode | None = None,
    ):
        self.status = status
        self.message = message
        self.details = details
        self.code = code
        self.timestamp = datetime.now(UTC)
        super().__init__(self.message)


def setup_exceptions_handler(app: FastAPI) -> None:
    """Global exception handlers for FastAPI app."""

    @app.exception_handler(ServerException)
    async def server_exception_handler(request: Request, exc: ServerException):
        return JSONResponse(
            status_code=exc.status,
            content={
                'error': {
                    'message': exc.message,
                    'code': exc.code.value if exc.code else None,
                    'details': exc.details,
                    'timestamp': exc.timestamp.isoformat(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': type(exc).__name__,
                }
            },
        )
