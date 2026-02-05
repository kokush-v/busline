import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.features.auth.enums import AuthCode


class CognitoUser(BaseModel):
    """JWT payload from Cognito token."""

    sub: str
    email: str | None = None
    name: str | None = None
    phone_number: str | None = None
    cognito_groups: list[str] = Field(default_factory=list, alias='cognito:groups')
    iat: int
    exp: int
    aud: str | None = None
    iss: str | None = None

    model_config = ConfigDict(extra='allow', populate_by_name=True)


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description='At least 8 characters, must contain uppercase, lowercase, number, and special character',
    )
    name: str = Field(..., max_length=255, description='Full name')
    phone_number: str = Field(..., description='Phone number with country code, e.g. +380123456789')

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets Cognito requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
        return v


class ConfirmSignUpRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description='6-digit confirmation code')


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int | None = None


class AuthResponse(BaseModel):
    code: AuthCode
    user_id: str | None = None
