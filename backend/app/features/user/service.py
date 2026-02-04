from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.common.enums import SortOrder
from app.database.db import get_db_session
from app.features.user.models import User
from app.features.user.schemas import UserCreate, UserQueryParams, UserSortBy, UserUpdate


class UserService:
    """Service for managing user operations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self._session = session

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

    async def create_user(self, payload: UserCreate) -> User:
        """Create a new user (typically called by Lambda after Cognito registration)."""
        result = await self._session.execute(select(User).filter(User.email == payload.email))
        existing_user = result.scalars().one_or_none()

        if existing_user:
            result.scalar_one()

        stmt = insert(User).values(**payload.model_dump()).returning(User)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def update_user(self, user_id: UUID, payload: UserUpdate) -> User:
        """Update user information."""
        await self.get_user(user_id)

        update_data = payload.model_dump(exclude_unset=True)
        stmt = update(User).where(User.id == user_id).values(**update_data).returning(User)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user (soft delete by setting is_active to False is recommended)."""
        await self.get_user(user_id)

        stmt = delete(User).where(User.id == user_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user (soft delete)."""
        return await self.update_user(user_id, UserUpdate(is_active=False))

    async def activate_user(self, user_id: UUID) -> User:
        """Activate a user."""
        return await self.update_user(user_id, UserUpdate(is_active=True))
