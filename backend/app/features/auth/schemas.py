import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignUpRequest(BaseModel):
    """Request schema for user registration."""

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
    """Request schema for confirming registration."""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description='6-digit confirmation code')


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Response schema with authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int | None = None


class AuthResponse(BaseModel):
    """Generic authentication response."""

    message: str
    user_id: str | None = None
