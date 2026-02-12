from collections.abc import Callable, Coroutine
from functools import lru_cache
import logging
import time
from typing import Any

import aioboto3
from botocore.exceptions import ClientError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from jose import JWTError, jwt

from app.core.exeptions import ServerException
from app.features.auth.schemas import CognitoUser
from app.settings.env import get_env_settings

logger = logging.getLogger(__name__)

security = HTTPBearer(
    scheme_name='CognitoJWT',
    description='Enter your AccessToken or IdToken from AWS Cognito',
)


class CognitoService:
    """Service for handling AWS Cognito operations."""

    JWKS_TTL = 3600  # Cache JWKS for 1 hour

    def __init__(self):
        self._settings = get_env_settings()
        self.region = self._settings.AWS_REGION
        self.user_pool_id = self._settings.COGNITO_USER_POOL_ID
        self.client_id = self._settings.COGNITO_CLIENT_ID

        self._session = aioboto3.Session(
            aws_access_key_id=self._settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self._settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.region,
        )

        self.jwks_url = f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json'
        self._jwks: list[dict[str, Any]] | None = None
        self._jwks_expire_at: float = 0

    async def _get_jwks(self) -> list[dict[str, Any]]:
        """Get JWKS keys from Cognito with TTL caching."""
        now = time.time()

        if not self._jwks or now > self._jwks_expire_at:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
                self._jwks = response.json()['keys']
                self._jwks_expire_at = now + self.JWKS_TTL
        return self._jwks

    async def sign_up(self, email: str, password: str, user_attributes: dict[str, str] | None = None):
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

            async with self._session.client('cognito-idp', region_name=self.region) as client:
                return await client.sign_up(**kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    async def confirm_sign_up(self, email: str, code: str):
        """Confirm registration with code from email."""
        try:
            kwargs = {'ClientId': self.client_id, 'Username': email, 'ConfirmationCode': code}

            async with self._session.client('cognito-idp', region_name=self.region) as client:
                return await client.confirm_sign_up(**kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    async def login(self, email: str, password: str):
        """Authenticate user and return tokens."""
        try:
            auth_params = {'USERNAME': email, 'PASSWORD': password}

            async with self._session.client('cognito-idp', region_name=self.region) as client:
                response = await client.initiate_auth(
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

    async def refresh_tokens(self, refresh_token: str):
        """Get new access token using refresh token."""
        try:
            auth_params = {'REFRESH_TOKEN': refresh_token}

            async with self._session.client('cognito-idp', region_name=self.region) as client:
                response = await client.initiate_auth(
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

    async def sign_out(self, access_token: str) -> None:
        """Invalidate user session in Cognito using access token."""
        try:
            async with self._session.client('cognito-idp', region_name=self.region) as client:
                await client.global_sign_out(AccessToken=access_token)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code},
            ) from e

    async def verify_token(self, token: str) -> CognitoUser | None:
        """Validate JWT and return payload."""
        try:
            jwks = await self._get_jwks()
            header = jwt.get_unverified_header(token)
            key = next((k for k in jwks if k['kid'] == header['kid']), None)

            if not key:
                logger.warning(f'Key {header.get("kid")} not found in JWKS, refreshing cache')
                self._jwks = None
                self._jwks_expire_at = 0
                jwks = await self._get_jwks()
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
            return CognitoUser.model_validate(payload)
        except (JWTError, StopIteration, KeyError):
            return None

    async def admin_create_user(self, email: str, user_attributes: dict[str, str] | None = None):
        """Admin API to create a user with temporary password (used when user is created in DB)."""
        try:
            logger.info(f'Admin create user - email: {email}, user_attributes: {user_attributes}')

            attributes = [{'Name': 'email', 'Value': email}, {'Name': 'email_verified', 'Value': 'true'}]

            if user_attributes:
                if user_attributes.get('name'):
                    attributes.append({'Name': 'name', 'Value': user_attributes['name']})
                if user_attributes.get('phone_number'):
                    attributes.append({'Name': 'phone_number', 'Value': user_attributes['phone_number']})

            async with self._session.client('cognito-idp', region_name=self.region) as client:
                return await client.admin_create_user(
                    UserPoolId=self.user_pool_id,
                    Username=email,
                    UserAttributes=attributes,
                    MessageAction='SUPPRESS',  # Don't send welcome message
                )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    async def admin_update_user_attributes(self, email: str, user_attributes: dict[str, str]):
        """Update user attributes in Cognito."""
        try:
            logger.info(f'Admin update user attributes - email: {email}, attributes: {user_attributes}')

            attributes = []
            if user_attributes.get('name'):
                attributes.append({'Name': 'name', 'Value': user_attributes['name']})
            if user_attributes.get('phone_number'):
                attributes.append({'Name': 'phone_number', 'Value': user_attributes['phone_number']})

            if attributes:
                async with self._session.client('cognito-idp', region_name=self.region) as client:
                    await client.admin_update_user_attributes(
                        UserPoolId=self.user_pool_id,
                        Username=email,
                        UserAttributes=attributes,
                    )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    async def admin_delete_user(self, email: str):
        """Delete user from Cognito."""
        try:
            logger.info(f'Admin delete user - email: {email}')
            async with self._session.client('cognito-idp', region_name=self.region) as client:
                await client.admin_delete_user(UserPoolId=self.user_pool_id, Username=email)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    async def admin_disable_user(self, email: str):
        """Disable user in Cognito (user cannot sign in)."""
        try:
            logger.info(f'Admin disable user - email: {email}')
            async with self._session.client('cognito-idp', region_name=self.region) as client:
                await client.admin_disable_user(UserPoolId=self.user_pool_id, Username=email)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    async def admin_enable_user(self, email: str):
        """Enable user in Cognito."""
        try:
            logger.info(f'Admin enable user - email: {email}')
            async with self._session.client('cognito-idp', region_name=self.region) as client:
                await client.admin_enable_user(UserPoolId=self.user_pool_id, Username=email)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    async def admin_add_user_to_group(self, email: str, group_name: str):
        """Add user to a Cognito group."""
        try:
            logger.info(f'Admin add user to group - email: {email}, group: {group_name}')
            async with self._session.client('cognito-idp', region_name=self.region) as client:
                await client.admin_add_user_to_group(
                    UserPoolId=self.user_pool_id,
                    Username=email,
                    GroupName=group_name,
                )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email, 'group': group_name},
            ) from e

    async def admin_remove_user_from_group(self, email: str, group_name: str):
        """Remove user from a Cognito group."""
        try:
            logger.info(f'Admin remove user from group - email: {email}, group: {group_name}')
            async with self._session.client('cognito-idp', region_name=self.region) as client:
                await client.admin_remove_user_from_group(
                    UserPoolId=self.user_pool_id,
                    Username=email,
                    GroupName=group_name,
                )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email, 'group': group_name},
            ) from e

    async def admin_list_groups_for_user(self, email: str) -> list[str]:
        """Get list of groups for a user."""
        try:
            logger.info(f'Admin list groups for user - email: {email}')
            async with self._session.client('cognito-idp', region_name=self.region) as client:
                response = await client.admin_list_groups_for_user(
                    UserPoolId=self.user_pool_id,
                    Username=email,
                )
            return [group['GroupName'] for group in response.get('Groups', [])]
        except ClientError as e:
            error_code = e.response['Error']['Code']
            raise ServerException(
                message=e.response['Error']['Message'],
                status=400,
                details={'error_code': error_code, 'email': email},
            ) from e

    def roles_required(self, allowed_groups: list[str]) -> Callable[..., Coroutine[Any, Any, CognitoUser]]:
        """Dependency for verifying user roles (Cognito Groups)."""

        async def dependency(auth: HTTPAuthorizationCredentials = Depends(security)) -> CognitoUser:
            token = auth.credentials

            payload = await self.verify_token(token)
            if not payload:
                raise ServerException(
                    message='Invalid or expired token',
                    status=401,
                )

            user_groups = payload.cognito_groups
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
