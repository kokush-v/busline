from functools import lru_cache
from urllib.parse import urlparse

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import status

from app.core.exeptions import S3Exception
from app.settings.env import get_env_settings


class S3Service:
    """Service for handling AWS S3 operations asynchronously."""

    """Service for handling AWS S3 operations asynchronously."""

    def __init__(self):
        self._settings = get_env_settings()
        self._session = aioboto3.Session()

    @property
    def _client_kwargs(self):
        """Common arguments for initializing the S3 client."""
        return {
            'service_name': 's3',
            'aws_access_key_id': self._settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': self._settings.AWS_SECRET_ACCESS_KEY,
            'region_name': self._settings.AWS_REGION,
            'config': Config(signature_version='s3v4'),
        }
        self._session = aioboto3.Session()

    @property
    def _client_kwargs(self):
        """Common arguments for initializing the S3 client."""
        return {
            'service_name': 's3',
            'aws_access_key_id': self._settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': self._settings.AWS_SECRET_ACCESS_KEY,
            'region_name': self._settings.AWS_REGION,
            'config': Config(signature_version='s3v4'),
        }

    async def generate_presigned_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        max_size: int = 10485760,
    ) -> dict:
        """
        Generate a presigned URL for uploading a file to S3.
        """
        try:
            async with self._session.client(**self._client_kwargs) as s3_client:
                presigned_post = await s3_client.generate_presigned_post(
                    Bucket=bucket,
                    Key=key,
                    Fields={'Content-Type': content_type},
                    Conditions=[
                        {'Content-Type': content_type},
                        ['content-length-range', 1, max_size],
                    ],
                    ExpiresIn=self._settings.S3_PRESIGNED_URL_EXPIRATION,
                )
                return presigned_post
        except ClientError as e:
            raise S3Exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to generate upload URL: {str(e)}',
            ) from e

    async def delete_object(self, bucket: str, key: str) -> bool:
        """
        Delete an object from S3 asynchronously.
        """
        try:
            async with self._session.client(**self._client_kwargs) as s3_client:
                await s3_client.delete_object(Bucket=bucket, Key=key)
                return True
        except ClientError as e:
            raise S3Exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to delete object from S3',
            ) from e

    def get_object_url(self, bucket: str, key: str) -> str:
        """
        Generate a public URL for an S3 object.
        NOTE: This is string formatting, no I/O, so it remains synchronous.
        """
        return f'https://{bucket}.s3.{self._settings.AWS_REGION}.amazonaws.com/{key}'

    def extract_key_from_url(self, url: str, bucket: str) -> str | None:
        """
        Extract the S3 key from a full URL.
        NOTE: Pure logic, remains synchronous.
        """
        try:
            parsed = urlparse(url)
            return parsed.path.lstrip('/')
        except (ValueError, AttributeError):
            return None


@lru_cache(maxsize=1)
def get_s3_service() -> S3Service:
    """Get or create S3 service instance."""
    return S3Service()
