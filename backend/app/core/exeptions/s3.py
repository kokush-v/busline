from app.core.exeptions.server import ErrorCode, ServerException


class S3Exception(ServerException):
    """Raised when S3/storage operations fail."""

    def __init__(
        self,
        message: str = 'Storage operation failed',
        status: int = 500,
        details: dict | None = None,
    ):
        super().__init__(
            status=status,
            message=message,
            code=ErrorCode.STORAGE,
            details=details,
        )
