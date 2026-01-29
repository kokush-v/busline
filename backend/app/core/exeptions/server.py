from datetime import UTC, datetime
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError


class ErrorCode(Enum):
    DATABASE = 'database'
    STORAGE = 'storage'


class ErrorSchema(BaseModel):
    """Schema for errors in the response."""

    message: str
    code: str | None = None
    details: dict | None = None
    timestamp: str


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
                'error': ErrorSchema(
                    message=exc.message,
                    code=exc.code.value if exc.code else None,
                    details=exc.details,
                    timestamp=exc.timestamp.isoformat(),
                ).model_dump()
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=500,
            content={
                'error': ErrorSchema(
                    message='Database operation failed',
                    code=ErrorCode.DATABASE.value,
                    details={'error_type': type(exc).__name__},
                    timestamp=datetime.now(UTC).isoformat(),
                ).model_dump()
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                'error': ErrorSchema(
                    message='An unexpected error occurred',
                    code=type(exc).__name__,
                    details=None,
                    timestamp=datetime.now(UTC).isoformat(),
                ).model_dump()
            },
        )
