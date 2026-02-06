from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
import time
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from app.settings.env import get_env_settings


class ErrorCode(StrEnum):
    DATABASE = 'database'
    STORAGE = 'storage'
    EMAIL = 'email'


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


def _log_error_to_file(request: Request, exc: Exception) -> None:
    """Write error details to logs/error.log in dev+DEBUG mode."""
    settings = get_env_settings()
    if settings.ENVIRONMENT != 'dev' or settings.LOG_LEVEL != 'DEBUG':
        return

    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    with (log_dir / 'error.log').open('a') as f:
        f.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {type(exc).__name__}\n')
        f.write(f'Path: {request.url.path} | Method: {request.method}\n')
        f.write(f'Error: {exc}\n')
        f.write('Stacktrace:\n')
        f.write(traceback.format_exc())
        f.write('\n' + '=' * 80 + '\n\n')


def setup_exceptions_handler(app: FastAPI) -> None:
    """Global exception handlers for FastAPI app."""

    @app.exception_handler(ServerException)
    async def server_exception_handler(request: Request, exc: ServerException):
        _log_error_to_file(request, exc)
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

    @app.exception_handler(NoResultFound)
    async def not_found_exception_handler(request: Request, exc: NoResultFound):
        _log_error_to_file(request, exc)
        return JSONResponse(
            status_code=404,
            content={
                'error': ErrorSchema(
                    message='Resource not found',
                    code=None,
                    details=None,
                    timestamp=datetime.now(UTC).isoformat(),
                ).model_dump()
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        _log_error_to_file(request, exc)
        return JSONResponse(
            status_code=409,
            content={
                'error': ErrorSchema(
                    message='Referenced resource does not exist or conflicts with existing data',
                    code=ErrorCode.DATABASE.value,
                    details=None,
                    timestamp=datetime.now(UTC).isoformat(),
                ).model_dump()
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        _log_error_to_file(request, exc)
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
        _log_error_to_file(request, exc)
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
