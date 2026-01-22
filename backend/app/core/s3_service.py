from functools import lru_cache

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from app.settings.env import get_env_settings


class S3Service:
    """Service for handling AWS S3 operations."""

    def __init__(self):
        self._settings = get_env_settings()
        self._s3_client = boto3.client(
            's3',
            aws_access_key_id=self._settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self._settings.AWS_SECRET_ACCESS_KEY,
            region_name=self._settings.AWS_REGION,
            config=Config(signature_version='s3v4'),
        )

    def generate_presigned_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        max_size: int = 10485760,  # 10MB
    ) -> dict:
        """
        Generate a presigned URL for uploading a file to S3.

        Args:
            bucket: S3 bucket name
            key: Object key in S3
            content_type: MIME type of the file
            max_size: Maximum file size in bytes

        Returns:
            Dictionary with 'url' and 'fields' for presigned POST
        """
        try:
            presigned_post = self._s3_client.generate_presigned_post(
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to generate upload URL: {str(e)}',
            ) from e

    def delete_object(self, bucket: str, key: str) -> bool:
        """
        Delete an object from S3.

        Args:
            bucket: S3 bucket name
            key: Object key in S3

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self._s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False

    def get_object_url(self, bucket: str, key: str) -> str:
        """
        Generate a public URL for an S3 object.

        Args:
            bucket: S3 bucket name
            key: Object key in S3

        Returns:
            Public URL to the S3 object
        """
        return f'https://{bucket}.s3.{self._settings.AWS_REGION}.amazonaws.com/{key}'

    def extract_key_from_url(self, url: str, bucket: str) -> str | None:
        """
        Extract the S3 key from a full URL.

        Args:
            url: Full S3 URL
            bucket: S3 bucket name

        Returns:
            S3 key or None if extraction fails
        """
        try:
            return url.split(f'{bucket}/')[-1]
        except (IndexError, AttributeError):
            return None


@lru_cache(maxsize=1)
def get_s3_service() -> S3Service:
    """Get or create S3 service instance."""
    return S3Service()
