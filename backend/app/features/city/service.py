from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import db_helper
from app.features.city.models import City
from app.features.city.schemas import CityCreate, CityUpdate


class CityService:
    def __init__(
        self, session: Annotated[AsyncSession, Depends(db_helper.get_db_session)]
    ):
        self._session = session

    async def list_cities(self) -> list[City]:
        result = await self._session.execute(select(City))
        return list(result.scalars().all())

    async def get_city(self, city_id: UUID) -> City:
        city = await self._session.get(City, city_id)
        if city is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="City not found"
            )
        return city

    async def create_city(self, payload: CityCreate) -> City:
        result = await self._session.execute(
            select(City).filter(City.name == payload.name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City with this name already exists",
            )

        city = City(**payload.model_dump())
        self._session.add(city)
        await self._session.commit()
        await self._session.refresh(city)
        return city

    async def update_city(self, city_id: UUID, payload: CityUpdate) -> City:
        city = await self.get_city(city_id)

        update_data = payload.model_dump(exclude_unset=True)
        if "name" in update_data:
            result = await self._session.execute(
                select(City).filter(
                    City.name == update_data["name"], City.id != city_id
                )
            )
            conflict = result.scalar_one_or_none()
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="City with this name already exists",
                )

        for field, value in update_data.items():
            setattr(city, field, value)

        self._session.add(city)
        await self._session.commit()
        await self._session.refresh(city)
        return city

    async def delete_city(self, city_id: UUID) -> None:
        city = await self.get_city(city_id)
        await self._session.delete(city)
        await self._session.commit()
