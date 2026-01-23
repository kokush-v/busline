from botocore.exceptions import BotoCoreError, ClientError
from fastapi import status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def normalize_error(exc: Exception) -> tuple[int, str]:
    """
    Convert exception to HTTP status code and error message.
    Centralized error handling logic for all exception types.

    Returns:
        tuple[int, str]: HTTP status code and error message
    """
    if isinstance(exc, IntegrityError):
        return status.HTTP_409_CONFLICT, 'Data conflict: Record already exists.'

    if isinstance(exc, SQLAlchemyError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Database internal error.'

    if isinstance(exc, ClientError):
        error_code = exc.response.get('Error', {}).get('Code')

        if error_code == 'NoSuchKey':
            return status.HTTP_404_NOT_FOUND, 'File not found in storage.'

        if error_code == 'AccessDenied':
            return status.HTTP_403_FORBIDDEN, 'Storage access denied.'

        return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Storage error: {error_code}'

    if isinstance(exc, BotoCoreError):
        return status.HTTP_503_SERVICE_UNAVAILABLE, 'Storage service unavailable.'

    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Unknown internal server error.'
