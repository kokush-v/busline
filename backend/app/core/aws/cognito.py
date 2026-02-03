from collections.abc import Callable
from functools import lru_cache
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from jose import JWTError, jwt

from app.core.exeptions import ServerException
from app.settings.env import get_env_settings

logger = logging.getLogger(__name__)

security = HTTPBearer(
    scheme_name='CognitoJWT',
    description='Enter your AccessToken or IdToken from AWS Cognito',
)


class CognitoService:
    """Service for handling AWS Cognito operations."""

    def __init__(self):
        self._settings = get_env_settings()
        self.region = self._settings.AWS_REGION
        self.user_pool_id = self._settings.COGNITO_USER_POOL_ID
        self.client_id = self._settings.COGNITO_CLIENT_ID

        self.client = boto3.client('cognito-idp', region_name=self.region)

        self.jwks_url = f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json'
        self._jwks: list[dict[str, Any]] | None = None

    async def _get_jwks(self) -> list[dict[str, Any]]:
        """Get JWKS keys from Cognito, cached after first retrieval."""
        if not self._jwks:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
                self._jwks = response.json()['keys']
        return self._jwks

    def sign_up(self, email: str, password: str, user_attributes: dict[str, str] | None = None):
        """Register a new user and return UserSub."""
        try:
            logger.info(f'Sign up request - email: {email}, user_attributes: {user_attributes}')

            kwargs = {
                'ClientId': self.client_id,
                'Username': email,
                'Password': password,
            }

            attributes = [{'Name': 'email', 'Value': email}]

            if user_attributes and user_attributes.get('name'):
                attributes.append({'Name': 'name', 'Value': user_attributes['name']})

            phone = user_attributes.get('phone_number', '+1') if user_attributes else '+1'
            attributes.append({'Name': 'phone_number', 'Value': phone})

            logger.info(f'Cognito attributes to send: {attributes}')

            kwargs['UserAttributes'] = attributes

            return self.client.sign_up(**kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    def confirm_sign_up(self, email: str, code: str):
        """Confirm registration with code from email."""
        try:
            kwargs = {'ClientId': self.client_id, 'Username': email, 'ConfirmationCode': code}

            return self.client.confirm_sign_up(**kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    def login(self, email: str, password: str):
        """Authenticate user and return tokens."""
        try:
            auth_params = {'USERNAME': email, 'PASSWORD': password}

            response = self.client.initiate_auth(
                ClientId=self.client_id, AuthFlow='USER_PASSWORD_AUTH', AuthParameters=auth_params
            )
            return response['AuthenticationResult']
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=401,
                details={'error_code': error_code, 'email': email},
            ) from e

    def refresh_tokens(self, refresh_token: str):
        """Get new access token using refresh token."""
        try:
            auth_params = {'REFRESH_TOKEN': refresh_token}

            response = self.client.initiate_auth(
                ClientId=self.client_id, AuthFlow='REFRESH_TOKEN_AUTH', AuthParameters=auth_params
            )
            return response['AuthenticationResult']
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message='Session expired, please login again',
                status=401,
                details={'error_code': error_code},
            ) from e

    async def verify_token(self, token: str) -> dict[str, Any] | None:
        """Validate JWT and return payload."""
        try:
            jwks = await self._get_jwks()
            header = jwt.get_unverified_header(token)
            key = next((k for k in jwks if k['kid'] == header['kid']), None)

            if not key:
                return None

            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}',
            )
            return payload
        except (JWTError, StopIteration, KeyError):
            return None

    def roles_required(self, allowed_groups: list[str]) -> Callable:
        """Dependency for verifying user roles (Cognito Groups)."""

        async def dependency(auth: HTTPAuthorizationCredentials = Depends(security)) -> dict[str, Any]:
            token = auth.credentials

            payload = await self.verify_token(token)
            if not payload:
                raise ServerException(
                    message='Invalid or expired token',
                    status=401,
                )

            user_groups = payload.get('cognito:groups', [])
            if not any(group in allowed_groups for group in user_groups):
                raise ServerException(
                    message='Access denied',
                    status=403,
                    details={
                        'required_groups': allowed_groups,
                        'user_groups': user_groups,
                    },
                )

            return payload

        return dependency


@lru_cache(maxsize=1)
def get_cognito_service() -> CognitoService:
    """Get or create Cognito service instance."""
    return CognitoService()
