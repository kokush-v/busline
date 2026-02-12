from pydantic import BaseModel, EmailStr, Field

from app.common.schemas import EntityModel, PaginatedResponse, QueryParams
from app.features.user.enums import UserRoleGroups, UserSortBy


class UserQueryParams(QueryParams):
    """Query parameters for user list."""

    sort_by: UserSortBy = Field(UserSortBy.CREATED_AT, description='Field to sort by')
    role: UserRoleGroups | None = Field(None, description='Filter by role')
    is_active: bool | None = Field(None, description='Filter by active status')


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=20)


class UserCreate(UserBase):
    role: UserRoleGroups = Field(default=UserRoleGroups.USER)


class UserUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=255)
    role: UserRoleGroups | None = None
    is_active: bool | None = None


class UserRead(UserBase, EntityModel):
    role: UserRoleGroups
    is_active: bool


class PaginatedUserResponse(PaginatedResponse[UserRead]):
    """Paginated response for users."""
