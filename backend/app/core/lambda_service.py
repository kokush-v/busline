from functools import lru_cache
import json
import logging
from typing import Any
from uuid import UUID

import aioboto3
from botocore.config import Config

from app.settings.env import get_env_settings

logger = logging.getLogger(__name__)


class LambdaService:
    """Service for handling AWS Lambda operations."""

    def __init__(self):
        self._settings = get_env_settings()
        self._session = aioboto3.Session()

    @property
    def _client_kwargs(self) -> dict[str, Any]:
        """Common arguments for initializing the Lambda client."""
        return {
            'service_name': 'lambda',
            'aws_access_key_id': self._settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': self._settings.AWS_SECRET_ACCESS_KEY,
            'region_name': self._settings.AWS_REGION,
            'config': Config(signature_version='v4'),
        }

    async def trigger_ticket_generator_lambda(
        self,
        ticket_id: UUID,
        force: bool = False,
    ) -> None:
        """
        Trigger PDF generation Lambda asynchronously (fire-and-forget).

        Lambda Destinations will handle failures:
        - On success: Lambda sets status to READY
        - On failure/timeout: TIcketPdfGeneratorExceptionHandler sets status to FAILED

        Args:
            ticket_id: Ticket ID to generate PDF for
            force: Force regeneration even if PDF exists

        Raises:
            Exception: If Lambda invocation fails (AWS-level error)
        """
        function_name = self._settings.TICKET_PDF_LAMBDA_NAME
        payload = {'ticket_id': str(ticket_id), 'force': force}
        payload_bytes = json.dumps(payload).encode('utf-8')

        logger.info(f"Triggering Lambda '{function_name}' for ticket {ticket_id}")

        async with self._session.client(**self._client_kwargs) as lambda_client:
            await lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',  # Asynchronous - enables Destinations
                Payload=payload_bytes,
            )

        logger.info(f"Lambda '{function_name}' triggered successfully for ticket {ticket_id}")


@lru_cache(maxsize=1)
def get_lambda_service() -> LambdaService:
    """Get or create Lambda service instance."""
    return LambdaService()
