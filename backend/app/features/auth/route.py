from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.aws.cognito import CognitoService, get_cognito_service, security
from app.features.auth.schemas import (
    AuthCode,
    AuthResponse,
    CognitoUser,
    ConfirmSignUpRequest,
    LoginRequest,
    RefreshTokenRequest,
    SignUpRequest,
    TokenResponse,
)
from app.features.user.enums import UserRoleGroups
from app.features.user.schemas import UserRead
from app.features.user.service import UserService

cognito_service = get_cognito_service()

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/sign-up', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    payload: SignUpRequest,
    cognito: CognitoService = Depends(get_cognito_service),
):
    """
    Register a new user in Cognito.
    Returns user_id (Cognito sub) which should be stored for later user creation in database.
    """
    result = await cognito.sign_up(
        payload.email,
        payload.password,
        user_attributes={'name': payload.name, 'phone_number': payload.phone_number},
    )
    return AuthResponse(
        code=AuthCode.SIGN_UP_SUCCESS,
        user_id=result['UserSub'],
    )


@router.post('/confirm-sign-up', response_model=AuthResponse)
async def confirm_sign_up(
    payload: ConfirmSignUpRequest,
    cognito: CognitoService = Depends(get_cognito_service),
):
    """
    Confirm user registration with code from email.
    User creation in database is handled by Cognito Post Confirmation Lambda trigger.
    """
    await cognito.confirm_sign_up(payload.email, payload.code)
    return AuthResponse(code=AuthCode.CONFIRM_SUCCESS)


@router.post('/login', response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    cognito: CognitoService = Depends(get_cognito_service),
):
    """
    Authenticate user with email and password.
    Returns access and refresh tokens.
    """
    auth_result = await cognito.login(payload.email, payload.password)
    return TokenResponse(
        access_token=auth_result['AccessToken'],
        refresh_token=auth_result['RefreshToken'],
        expires_in=auth_result.get('ExpiresIn'),
    )


@router.post('/refresh', response_model=TokenResponse)
async def refresh_tokens(
    payload: RefreshTokenRequest,
    cognito: CognitoService = Depends(get_cognito_service),
):
    """
    Refresh access token using refresh token.
    Returns new access token.
    """
    auth_result = await cognito.refresh_tokens(payload.refresh_token)
    return TokenResponse(
        access_token=auth_result['AccessToken'],
        refresh_token=payload.refresh_token,
        expires_in=auth_result.get('ExpiresIn'),
    )


@router.get('/profile', response_model=UserRead)
async def get_profile(
    service: UserService = Depends(),
    user: CognitoUser = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN, UserRoleGroups.USER])),
):
    """Get current user profile from DB without joins."""
    return await service.get_user(user_id=UUID(user.sub))


@router.post('/sign-out', status_code=status.HTTP_204_NO_CONTENT)
async def sign_out(
    auth: HTTPAuthorizationCredentials = Depends(security),
    _: CognitoUser = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN, UserRoleGroups.USER])),
    cognito: CognitoService = Depends(get_cognito_service),
):
    """Sign out user globally in Cognito using access token."""
    await cognito.sign_out(auth.credentials)
