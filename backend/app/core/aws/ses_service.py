from enum import StrEnum
from functools import lru_cache
import json
import logging

import aioboto3
from botocore.exceptions import ClientError
from fastapi import status

from app.core.exeptions import SESException
from app.settings.env import get_env_settings


class SESErrorCode(StrEnum):
    """Common AWS SES error codes for handling exceptions."""

    MESSAGE_REJECTED = 'MessageRejected'
    MAIL_FROM_DOMAIN_NOT_VERIFIED = 'MailFromDomainNotVerified'
    TEMPLATE_DOES_NOT_EXIST = 'TemplateDoesNotExist'


class EmailTemplate(StrEnum):
    """AWS SES email template names."""

    PAYMENT_CONFIRMATION = 'PaymentConfirmation'


class SESService:
    """Service for handling AWS SES email operations asynchronously."""

    def __init__(self):
        self._settings = get_env_settings()
        self._session = aioboto3.Session()
        self._logger = logging.getLogger(__name__)

    @property
    def _client_kwargs(self):
        """Common arguments for initializing the SES client."""
        return {
            'service_name': 'ses',
            'aws_access_key_id': self._settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': self._settings.AWS_SECRET_ACCESS_KEY,
            'region_name': self._settings.AWS_REGION,
        }

    def _handle_ses_error(self, e: ClientError, to_email: str, context: str) -> None:
        """Handle SES client errors with appropriate exceptions."""
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')

        match error_code:
            case SESErrorCode.MESSAGE_REJECTED:
                raise SESException(
                    status=status.HTTP_400_BAD_REQUEST,
                    message='Email was rejected by SES',
                    details={'error': str(e), 'to_email': to_email},
                ) from e
            case SESErrorCode.MAIL_FROM_DOMAIN_NOT_VERIFIED:
                raise SESException(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Sender domain is not verified in SES',
                    details={'error': str(e)},
                ) from e
            case SESErrorCode.TEMPLATE_DOES_NOT_EXIST:
                raise SESException(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Email template does not exist in SES',
                    details={'error': str(e)},
                ) from e
            case _:
                raise SESException(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Failed to send email',
                    details={'error': str(e), 'error_code': error_code},
                ) from e

    async def send_templated_email(
        self,
        to_email: str,
        template_name: str,
        template_data: dict,
    ) -> str:
        """
        Send an email using an AWS SES template.

        Args:
            to_email: Recipient email address
            template_name: Name of the SES template
            template_data: Dictionary of template variables

        Returns:
            Message ID from SES
        """

        try:
            async with self._session.client(**self._client_kwargs) as ses_client:
                response = await ses_client.send_templated_email(
                    Source=self._settings.SES_SENDER_EMAIL,
                    Destination={'ToAddresses': [to_email]},
                    Template=template_name,
                    TemplateData=json.dumps(template_data),
                )
                message_id = response['MessageId']
                self._logger.info(f'Templated email sent to {to_email}, MessageId: {message_id}')
                return message_id

        except ClientError as e:
            self._handle_ses_error(e, to_email, 'Failed to send templated email')

    async def send_payment_confirmation(
        self,
        to_email: str,
        order_id: str,
        total_amount: str,
    ) -> str:
        """
        Send a payment confirmation email using SES template.

        Args:
            to_email: Recipient email address
            order_id: Order ID for reference
            total_amount: Total payment amount

        Returns:
            Message ID from SES
        """
        template_data = {
            'order_id': order_id,
            'order_id_short': order_id[:8],
            'total_amount': total_amount,
        }

        return await self.send_templated_email(
            to_email=to_email,
            template_name=EmailTemplate.PAYMENT_CONFIRMATION,
            template_data=template_data,
        )


@lru_cache(maxsize=1)
def get_ses_service() -> SESService:
    """Get or create SES service instance."""
    return SESService()
