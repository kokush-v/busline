from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.city.models import City
from app.features.city.service import CityService
from app.features.stop.models import Stop
from app.features.stop.schemas import StopCreate, StopQueryParams, StopSearchItem, StopSearchParams, StopSearchResponse, StopUpdate
from app.utils.decorators import transactional


class StopService:
    """Service for managing stop operations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session), city_service: CityService = Depends()):
        self._session = session
        self._city_service = city_service

    async def get_stops(self, params: StopQueryParams) -> tuple[list[Stop], int]:
        """Get stops with filtering and pagination."""
        query = select(Stop).join(City, Stop.city_id == City.id)

        if params.search:
            query = query.where((City.name.ilike(f'%{params.search}%')) | (Stop.name.ilike(f'%{params.search}%')))

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Stop.name).limit(params.limit).offset(params.offset)

        result = await self._session.execute(query)
        stops = list(result.scalars().all())

        return stops, total

    async def get_stop(self, stop_id: UUID) -> Stop:
        result = await self._session.execute(select(Stop).where(Stop.id == stop_id))
        stop = result.scalars().one()
        return stop

    @transactional
    async def create_stop(self, payload: StopCreate) -> Stop:
        city_result = await self._session.execute(select(City).where(City.id == payload.city_id))
        city_result.scalars().one()

        stmt = insert(Stop).values(**payload.model_dump()).returning(Stop)
        result = await self._session.execute(stmt)
        return result.scalars().one()

    @transactional
    async def update_stop(self, stop_id: UUID, payload: StopUpdate) -> Stop:
        await self.get_stop(stop_id)

        if payload.city_id is not None:
            city_result = await self._session.execute(select(City).where(City.id == payload.city_id))
            city_result.scalars().one()

        update_data = payload.model_dump(exclude_unset=True)
        if update_data:
            stmt = update(Stop).where(Stop.id == stop_id).values(**update_data).returning(Stop)
            result = await self._session.execute(stmt)
            return result.scalars().one()

        return await self.get_stop(stop_id)

    @transactional
    async def delete_stop(self, stop_id: UUID) -> None:
        await self.get_stop(stop_id)
        stmt = delete(Stop).where(Stop.id == stop_id)
        await self._session.execute(stmt)

    async def search_stops(self, params: StopSearchParams) -> StopSearchResponse:
        """Search stops with cursor-based pagination (keyset pagination)."""
        query = select(Stop, City.name.label('city_name')).join(City, Stop.city_id == City.id)

        if params.search:
            query = query.where(Stop.name.ilike(f'%{params.search}%') | City.name.ilike(f'%{params.search}%'))

        if params.cursor:
            last_stop = await self._session.execute(select(Stop.name).where(Stop.id == params.cursor))
            last_stop_name = last_stop.scalar_one_or_none()
            if last_stop_name is not None:
                query = query.where(
                    (Stop.name > last_stop_name) | ((Stop.name == last_stop_name) & (Stop.id > params.cursor))
                )

        query = query.order_by(asc(Stop.name), asc(Stop.id))
        query = query.limit(params.limit + 1)

        result = await self._session.execute(query)
        rows = list(result.all())

        has_more = len(rows) > params.limit
        if has_more:
            rows = rows[: params.limit]

        items = [StopSearchItem(id=row.Stop.id, name=row.Stop.name, city_name=row.city_name) for row in rows]
        next_cursor = items[-1].id if has_more and items else None

        return StopSearchResponse(items=items, next_cursor=next_cursor, has_more=has_more)
