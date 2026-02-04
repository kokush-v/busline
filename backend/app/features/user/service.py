import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.common.enums import SortOrder
from app.core.aws.cognito import CognitoService, get_cognito_service
from app.core.exeptions import ServerException
from app.database.db import get_db_session
from app.features.user.enums import UserRoleGroups
from app.features.user.models import User
from app.features.user.schemas import UserCreate, UserQueryParams, UserSortBy, UserUpdate
from app.utils.decorators import transactional

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user operations."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        cognito: CognitoService = Depends(get_cognito_service),
    ):
        self._session = session
        self._cognito = cognito

    async def get_users(self, params: UserQueryParams) -> tuple[list[User], int]:
        """Get users with filtering, sorting, and pagination."""
        query = select(User)
        query = self.__apply_search_filter(query, params)
        query = self.__apply_role_filter(query, params)
        query = self.__apply_active_filter(query, params)

        total = await self.__get_total_count(query)

        query = self.__apply_sorting(query, params)
        query = self.__apply_pagination(query, params)

        result = await self._session.execute(query)
        users = list(result.scalars().all())

        return users, total

    def __apply_search_filter(self, query: Select, params: UserQueryParams) -> Select:
        if params.search:
            query = query.where((User.email.ilike(f'%{params.search}%')) | (User.name.ilike(f'%{params.search}%')))
        return query

    def __apply_role_filter(self, query: Select, params: UserQueryParams) -> Select:
        if params.role:
            query = query.where(User.role == params.role)
        return query

    def __apply_active_filter(self, query: Select, params: UserQueryParams) -> Select:
        if params.is_active is not None:
            query = query.where(User.is_active == params.is_active)
        return query

    async def __get_total_count(self, query: Select) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        return total_result.scalar_one()

    def __apply_sorting(self, query: Select, params: UserQueryParams) -> Select:
        match params.sort_by:
            case UserSortBy.EMAIL:
                sort_column = User.email
            case UserSortBy.NAME:
                sort_column = User.name
            case UserSortBy.CREATED_AT:
                sort_column = User.created_at
            case _:
                sort_column = User.created_at

        match params.sort_order:
            case SortOrder.DESC:
                return query.order_by(desc(sort_column))
            case _:
                return query.order_by(asc(sort_column))

    def __apply_pagination(self, query: Select, params: UserQueryParams) -> Select:
        return query.limit(params.limit).offset(params.offset)

    async def get_user(self, user_id: UUID) -> User:
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalars().one()
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalars().one_or_none()

    async def __create_user_in_cognito(self, email: str, name: str | None, role: str) -> str:
        """Create user in Cognito with specified role and return the user sub."""
        response = await self._cognito.admin_create_user(
            email,
            user_attributes={'name': name} if name else None,
        )
        await self._cognito.admin_add_user_to_group(email, role)

        user_sub = None
        for attr in response['User']['Attributes']:
            if attr['Name'] == 'sub':
                user_sub = attr['Value']
                break

        if not user_sub:
            raise ServerException(
                message='Failed to get user sub from Cognito',
                status=500,
                details={'email': email},
            )

        return user_sub

    async def __rollback_cognito_user(self, email: str) -> None:
        """Delete user from Cognito if DB operation fails."""
        try:
            await self._cognito.admin_delete_user(email)
            logger.info(f'Rolled back Cognito user: {email}')
        except Exception as e:
            logger.error(f'Failed to rollback Cognito user {email}: {str(e)}')

    @transactional
    async def create_user(self, payload: UserCreate) -> User:
        """
        Create a new user by admin (e.g., creating other admins).
        For regular user sign-up, use /auth/sign-up endpoint.
        """
        result = await self._session.execute(select(User).filter(User.email == payload.email))
        existing_user = result.scalars().one_or_none()

        if existing_user:
            result.scalar_one()

        user_sub = await self.__create_user_in_cognito(payload.email, payload.name, payload.role)

        try:
            user_data = payload.model_dump()
            user_data['id'] = user_sub

            stmt = insert(User).values(**user_data).returning(User)
            result = await self._session.execute(stmt)
            user = result.scalars().one()
            return user
        except Exception as e:
            await self.__rollback_cognito_user(payload.email)
            raise ServerException(
                message='Failed to create user in database',
                status=500,
                details={'email': payload.email, 'error': str(e)},
            ) from e

    async def __update_user_attributes_in_cognito(self, email: str, update_data: dict) -> None:
        """Update user attributes (name, phone_number) in Cognito."""
        cognito_attributes = {}
        if 'name' in update_data:
            cognito_attributes['name'] = update_data['name']
        if 'phone_number' in update_data:
            cognito_attributes['phone_number'] = update_data['phone_number']

        if cognito_attributes:
            await self._cognito.admin_update_user_attributes(email, cognito_attributes)

    async def __update_user_role_in_cognito(self, email: str, new_role: str) -> None:
        """Update user role/group in Cognito."""
        current_groups = await self._cognito.admin_list_groups_for_user(email)

        for role in UserRoleGroups:
            if role in current_groups:
                await self._cognito.admin_remove_user_from_group(email, role)

        await self._cognito.admin_add_user_to_group(email, new_role)

    @transactional
    async def update_user(self, user_id: UUID, payload: UserUpdate) -> User:
        """Update user information."""
        user = await self.get_user(user_id)

        update_data = payload.model_dump(exclude_unset=True)

        await self.__update_user_attributes_in_cognito(user.email, update_data)

        if 'role' in update_data:
            await self.__update_user_role_in_cognito(user.email, update_data['role'])

        stmt = update(User).where(User.id == user_id).values(**update_data).returning(User)
        result = await self._session.execute(stmt)
        updated_user = result.scalars().one()

        return updated_user

    async def __delete_user_from_cognito(self, email: str) -> None:
        """Delete user from Cognito."""
        await self._cognito.admin_delete_user(email)

    @transactional
    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_user(user_id)

        await self.__delete_user_from_cognito(user.email)

        stmt = delete(User).where(User.id == user_id)
        await self._session.execute(stmt)

    async def __disable_user_in_cognito(self, email: str) -> None:
        await self._cognito.admin_disable_user(email)

    async def __enable_user_in_cognito(self, email: str) -> None:
        await self._cognito.admin_enable_user(email)

    async def deactivate_user(self, user_id: UUID) -> User:
        user = await self.get_user(user_id)

        await self.__disable_user_in_cognito(user.email)
        user = await self.update_user(user_id, UserUpdate(is_active=False))

        return user

    async def activate_user(self, user_id: UUID) -> User:
        user = await self.get_user(user_id)

        await self.__enable_user_in_cognito(user.email)
        user = await self.update_user(user_id, UserUpdate(is_active=True))

        return user
