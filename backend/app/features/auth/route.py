from fastapi import APIRouter, Depends, status

from app.core.aws.cognito import CognitoService, get_cognito_service
from app.features.auth.schemas import (
    AuthCode,
    AuthResponse,
    ConfirmSignUpRequest,
    LoginRequest,
    RefreshTokenRequest,
    SignUpRequest,
    TokenResponse,
)

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
