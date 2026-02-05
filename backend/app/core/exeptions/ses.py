from app.core.exeptions.server import ErrorCode, ServerException


class SESException(ServerException):
    """Raised when SES/email operations fail."""

    def __init__(
        self,
        message: str = 'Email operation failed',
        status: int = 500,
        details: dict | None = None,
    ):
        super().__init__(
            status=status,
            message=message,
            code=ErrorCode.EMAIL,
            details=details,
        )
