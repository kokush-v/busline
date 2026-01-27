from enum import Enum
from functools import wraps

from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy.exc import SQLAlchemyError
import structlog

from app.core.exceptions import DatabaseError, StorageError

logger = structlog.get_logger()


class ErrorType(Enum):
    DATABASE = 'database'
    STORAGE = 'storage'


def handle_errors(*error_types: ErrorType):
    """
    Universal decorator that catches specified error types.

    Usage:
        @handle_errors(ErrorType.DATABASE)
        async def get_buses(self): ...

        @handle_errors(ErrorType.STORAGE)
        async def upload_file(self): ...

        @handle_errors(ErrorType.DATABASE, ErrorType.STORAGE)
        async def delete_bus_with_photo(self): ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except SQLAlchemyError as e:
                if ErrorType.DATABASE in error_types:
                    await logger.aerror(
                        'database_error',
                        function=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e),
                    )
                    raise DatabaseError(f'Database error in {func.__name__}: {e}') from e
                raise
            except ClientError as e:
                if ErrorType.STORAGE in error_types:
                    error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                    await logger.aerror(
                        'storage_error',
                        function=func.__name__,
                        error_type=type(e).__name__,
                        error_code=error_code,
                        error_message=str(e),
                    )
                    raise StorageError(f'Storage error in {func.__name__}: {error_code}') from e
                raise
            except BotoCoreError as e:
                if ErrorType.STORAGE in error_types:
                    await logger.aerror(
                        'storage_error',
                        function=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e),
                    )
                    raise StorageError(f'Storage service unavailable: {e}') from e
                raise

        return wrapper

    return decorator
