from app.core.exeptions.server import ErrorCode, ServerException


class DatabaseException(ServerException):
    """Raised when database operations fail."""

    def __init__(
        self,
        message: str = 'Database operation failed',
        status: int = 500,
        details: dict | None = None,
    ):
        super().__init__(
            status=status,
            message=message,
            code=ErrorCode.DATABASE,
            details=details,
        )
