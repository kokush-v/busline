from botocore.exceptions import BotoCoreError, ClientError
import pytest
from sqlalchemy.exc import OperationalError

from app.core.decorators import ErrorType, handle_errors
from app.core.exceptions import DatabaseError, StorageError


class TestHandleErrorsDecorator:
    """Tests for the handle_errors decorator."""

    async def test_database_error_is_caught_and_wrapped(self):
        """Test that SQLAlchemy errors are caught and wrapped in DatabaseError."""

        @handle_errors(ErrorType.DATABASE)
        async def failing_db_function():
            raise OperationalError('statement', {}, Exception('Connection refused'))

        with pytest.raises(DatabaseError) as exc_info:
            await failing_db_function()

        assert 'Database error in failing_db_function' in str(exc_info.value)

    async def test_storage_client_error_is_caught_and_wrapped(self):
        """Test that S3 ClientError is caught and wrapped in StorageError."""

        @handle_errors(ErrorType.STORAGE)
        async def failing_s3_function():
            error_response = {'Error': {'Code': 'NoSuchBucket', 'Message': 'Bucket not found'}}
            raise ClientError(error_response, 'GetObject')

        with pytest.raises(StorageError) as exc_info:
            await failing_s3_function()

        assert 'Storage error in failing_s3_function' in str(exc_info.value)
        assert 'NoSuchBucket' in str(exc_info.value)

    async def test_storage_botocore_error_is_caught_and_wrapped(self):
        """Test that BotoCoreError is caught and wrapped in StorageError."""

        @handle_errors(ErrorType.STORAGE)
        async def failing_s3_function():
            raise BotoCoreError()

        with pytest.raises(StorageError) as exc_info:
            await failing_s3_function()

        assert 'Storage service unavailable' in str(exc_info.value)

    async def test_combined_decorator_catches_database_error(self):
        """Test that combined decorator catches database errors."""

        @handle_errors(ErrorType.DATABASE, ErrorType.STORAGE)
        async def mixed_function():
            raise OperationalError('statement', {}, Exception('Connection refused'))

        with pytest.raises(DatabaseError):
            await mixed_function()

    async def test_combined_decorator_catches_storage_error(self):
        """Test that combined decorator catches storage errors."""

        @handle_errors(ErrorType.DATABASE, ErrorType.STORAGE)
        async def mixed_function():
            error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}}
            raise ClientError(error_response, 'PutObject')

        with pytest.raises(StorageError):
            await mixed_function()

    async def test_successful_function_returns_result(self):
        """Test that successful functions return their result unchanged."""

        @handle_errors(ErrorType.DATABASE)
        async def successful_function():
            return {'status': 'ok', 'data': [1, 2, 3]}

        result = await successful_function()

        assert result == {'status': 'ok', 'data': [1, 2, 3]}

    async def test_unhandled_error_type_is_not_caught(self):
        """Test that errors not in error_types are re-raised as-is."""

        @handle_errors(ErrorType.DATABASE)  # Only DATABASE, not STORAGE
        async def function_with_storage_error():
            error_response = {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}}
            raise ClientError(error_response, 'GetObject')

        # ClientError should pass through since we only handle DATABASE
        with pytest.raises(ClientError):
            await function_with_storage_error()

    async def test_non_handled_exception_passes_through(self):
        """Test that non-handled exceptions pass through unchanged."""

        @handle_errors(ErrorType.DATABASE, ErrorType.STORAGE)
        async def function_with_value_error():
            raise ValueError('Some validation error')

        with pytest.raises(ValueError) as exc_info:
            await function_with_value_error()

        assert 'Some validation error' in str(exc_info.value)
