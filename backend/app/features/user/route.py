from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.roles import RoleChecker
from app.features.user.enums import UserRole
from app.features.user.schemas import (
    PaginatedUserResponse,
    UserCreate,
    UserQueryParams,
    UserRead,
    UserUpdate,
)
from app.features.user.service import UserService

router = APIRouter(prefix='/users', tags=['Users'])

admin_only = RoleChecker([UserRole.ADMIN])


@router.get('', response_model=PaginatedUserResponse)
async def get_users(params: UserQueryParams = Depends(), service: UserService = Depends()):
    """Get all users with pagination and search. Admin only."""
    users, total = await service.get_users(params)
    return PaginatedUserResponse(
        items=users,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )


@router.get('/{user_id}', response_model=UserRead)
async def get_user(user_id: UUID, service: UserService = Depends()):
    """Get a specific user by ID."""
    return await service.get_user(user_id)


@router.post(
    '',
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(payload: UserCreate, service: UserService = Depends()):
    """Create a new user. Typically called by Lambda after Cognito registration."""
    return await service.create_user(payload)


@router.put('/{user_id}', response_model=UserRead)
async def update_user(user_id: UUID, payload: UserUpdate, service: UserService = Depends()):
    """Update user information. Admin only."""
    return await service.update_user(user_id, payload)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, service: UserService = Depends()):
    """Delete a user. Admin only."""
    await service.delete_user(user_id)


@router.post('/{user_id}/deactivate', response_model=UserRead)
async def deactivate_user(user_id: UUID, service: UserService = Depends()):
    """Deactivate a user (soft delete). Admin only."""
    return await service.deactivate_user(user_id)


@router.post('/{user_id}/activate', response_model=UserRead)
async def activate_user(user_id: UUID, service: UserService = Depends()):
    """Activate a user. Admin only."""
    return await service.activate_user(user_id)
