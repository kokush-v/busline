from uuid import UUID

from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.bus.models import Bus
from app.features.stop.service import StopService
from app.features.trip.models import Trip
from app.features.trip.schemas import TripCreate, TripUpdate


class TripService:
    """Service for managing trip operations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session), stop_service: StopService = Depends()):
        self._session = session
        self._stop_service = stop_service

    async def get_many_trips(self) -> list[Trip]:
        """Get all trips."""
        result = await self._session.execute(select(Trip))
        return list(result.scalars().all())

    async def get_one_trip(self, trip_id: UUID) -> Trip:
        """Get a specific trip by ID."""
        result = await self._session.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalars().one()
        return trip

    async def create_trip(self, payload: TripCreate) -> Trip:
        """Create a new trip with associated stops."""
        bus_result = await self._session.execute(select(Bus).where(Bus.id == payload.bus_id))
        bus = bus_result.scalars().one()

        trip_data = {
            'bus_id': payload.bus_id,
            'seats_left': bus.seats_quantity,
        }

        stmt = insert(Trip).values(**trip_data).returning(Trip)
        result = await self._session.execute(stmt)
        trip = result.scalars().one()
        await self._session.commit()

        return trip

    async def update_trip(self, trip_id: UUID, payload: TripUpdate) -> Trip:
        """Update a trip."""
        trip = await self.get_one_trip(trip_id)

        update_data = {}

        if payload.bus_id is not None:
            bus_result = await self._session.execute(select(Bus).where(Bus.id == payload.bus_id))
            bus = bus_result.scalars().one()
            update_data['bus_id'] = bus.id

        if update_data:
            stmt = update(Trip).where(Trip.id == trip_id).values(**update_data).returning(Trip)
            result = await self._session.execute(stmt)
            trip = result.scalars().one()

        await self._session.commit()
        return trip

    async def delete_trip(self, trip_id: UUID) -> None:
        """Delete a trip."""
        trip = await self.get_one_trip(trip_id)
        await self._session.delete(trip)
        await self._session.commit()
