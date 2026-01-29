from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.city.models import City
from app.features.stop.models import Stop
from app.features.stop.schemas import StopCreate, StopUpdate


class StopService:
    """Service for managing stop operations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self._session = session

    async def get_stops(self, search: str | None = None) -> list[Stop]:
        query = select(Stop).join(City, Stop.city_id == City.id)

        if search:
            query = query.where((City.name.ilike(f'%{search}%')) | (Stop.name.ilike(f'%{search}%')))

        query = query.order_by(Stop.name)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_stop(self, stop_id: UUID) -> Stop:
        result = await self._session.execute(select(Stop).where(Stop.id == stop_id))
        stop = result.scalars().one()
        return stop

    async def create_stop(self, payload: StopCreate) -> Stop:
        city_result = await self._session.execute(select(City).where(City.id == payload.city_id))
        city_result.scalars().one()

        stmt = insert(Stop).values(**payload.model_dump()).returning(Stop)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def update_stop(self, stop_id: UUID, payload: StopUpdate) -> Stop:
        await self.get_stop(stop_id)

        if payload.city_id is not None:
            city_result = await self._session.execute(select(City).where(City.id == payload.city_id))
            city_result.scalars().one()

        update_data = payload.model_dump(exclude_unset=True)
        if update_data:
            stmt = update(Stop).where(Stop.id == stop_id).values(**update_data).returning(Stop)
            result = await self._session.execute(stmt)
            await self._session.commit()
            return result.scalars().one()

        return await self.get_stop(stop_id)

    async def delete_stop(self, stop_id: UUID) -> None:
        await self.get_stop(stop_id)
        stmt = delete(Stop).where(Stop.id == stop_id)
        await self._session.execute(stmt)
        await self._session.commit()
