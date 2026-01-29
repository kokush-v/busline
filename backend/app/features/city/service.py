from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.city.models import City
from app.features.city.schemas import CityCreate, CityUpdate


class CityService:
    """Service for managing city operations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self._session = session

    async def get_cities(self) -> list[City]:
        result = await self._session.execute(select(City))
        return list(result.scalars().all())

    async def get_city(self, city_id: UUID) -> City:
        result = await self._session.execute(select(City).where(City.id == city_id))
        city = result.scalars().one()
        return city

    async def create_city(self, payload: CityCreate) -> City:
        result = await self._session.execute(select(City).filter(City.name == payload.name))
        result.scalar_one()

        stmt = insert(City).values(**payload.model_dump()).returning(City)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def update_city(self, city_id: UUID, payload: CityUpdate) -> City:
        await self.get_city(city_id)

        update_data = payload.model_dump(exclude_unset=True)
        if 'name' in update_data:
            result = await self._session.execute(
                select(City).filter(City.name == update_data['name'], City.id != city_id)
            )
            result.scalar_one()

        stmt = update(City).where(City.id == city_id).values(**update_data).returning(City)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def delete_city(self, city_id: UUID) -> None:
        await self.get_city(city_id)
        stmt = delete(City).where(City.id == city_id)
        await self._session.execute(stmt)
        await self._session.commit()
