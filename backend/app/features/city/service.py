from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.common.enums import SortOrder
from app.core.exeptions import ServerException
from app.database.db import get_db_session
from app.features.city.enums import CitySortBy
from app.features.city.models import City
from app.features.city.schemas import (
    CityCreate,
    CityQueryParams,
    CitySearchItem,
    CitySearchParams,
    CitySearchResponse,
    CityUpdate,
)
from app.utils.decorators import transactional


class CityService:
    """Service for managing city operations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self._session = session

    def __apply_search_filter(self, query: Select, params: CityQueryParams) -> Select:
        if not params.search:
            return query

        return query.where(City.name.ilike(f'%{params.search}%'))

    def __apply_sorting(self, query: Select, params: CityQueryParams) -> Select:
        match params.sort_by:
            case CitySortBy.NAME:
                sort_column = City.name
            case CitySortBy.CREATED_AT:
                sort_column = City.created_at
            case _:
                sort_column = City.name

        match params.sort_order:
            case SortOrder.DESC:
                query = query.order_by(desc(sort_column))
            case _:
                query = query.order_by(asc(sort_column))

        return query

    def __apply_pagination(self, query: Select, params: CityQueryParams) -> Select:
        return query.limit(params.limit).offset(params.offset)

    async def __get_total_count(self, query: Select) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        return total_result.scalar_one()

    async def get_cities(self, params: CityQueryParams) -> tuple[list[City], int]:
        """Get cities with filtering, sorting, and pagination."""
        query = select(City)

        query = self.__apply_search_filter(query, params)
        total = await self.__get_total_count(query)
        query = self.__apply_sorting(query, params)
        query = self.__apply_pagination(query, params)

        result = await self._session.execute(query)
        cities = list(result.scalars().all())

        return cities, total

    async def get_city(self, city_id: UUID) -> City:
        result = await self._session.execute(select(City).where(City.id == city_id))
        city = result.scalars().one()
        return city

    @transactional
    async def create_city(self, payload: CityCreate) -> City:
        result = await self._session.execute(select(City).filter(City.name == payload.name))
        if result.scalar_one_or_none():
            raise ServerException(message='City with this name already exists', status=400)

        stmt = insert(City).values(**payload.model_dump()).returning(City)
        result = await self._session.execute(stmt)
        return result.scalars().one()

    @transactional
    async def update_city(self, city_id: UUID, payload: CityUpdate) -> City:
        await self.get_city(city_id)

        update_data = payload.model_dump(exclude_unset=True)
        if 'name' in update_data:
            result = await self._session.execute(
                select(City).filter(City.name == update_data['name'], City.id != city_id)
            )
            if result.scalar_one_or_none():
                raise ServerException(message='City with this name already exists', status=400)

        if update_data:
            stmt = update(City).where(City.id == city_id).values(**update_data).returning(City)
            result = await self._session.execute(stmt)
            return result.scalars().one()

        return await self.get_city(city_id)

    @transactional
    async def delete_city(self, city_id: UUID) -> None:
        await self.get_city(city_id)
        stmt = delete(City).where(City.id == city_id)
        await self._session.execute(stmt)

    async def search_cities(self, params: CitySearchParams) -> CitySearchResponse:
        """Search cities with cursor-based pagination (keyset pagination)."""
        query = select(City)

        if params.search:
            query = query.where(City.name.ilike(f'%{params.search}%'))

        if params.cursor:
            last_city = await self._session.execute(select(City.name).where(City.id == params.cursor))
            last_city_name = last_city.scalar_one_or_none()
            if last_city_name is not None:
                query = query.where(
                    (City.name > last_city_name) | ((City.name == last_city_name) & (City.id > params.cursor))
                )

        query = query.order_by(asc(City.name), asc(City.id))
        query = query.limit(params.limit + 1)

        result = await self._session.execute(query)
        cities = list(result.scalars().all())

        has_more = len(cities) > params.limit
        if has_more:
            cities = cities[: params.limit]

        items = [CitySearchItem(id=city.id, name=city.name) for city in cities]
        next_cursor = items[-1].id if has_more and items else None

        return CitySearchResponse(items=items, next_cursor=next_cursor, has_more=has_more)
