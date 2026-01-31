from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.bus.models import Bus
from app.features.bus.service import BusService
from app.features.seat.service import SeatService
from app.features.stop.service import StopService
from app.features.trip.models import Trip
from app.features.trip.schemas import TripCreate, TripUpdate
from app.features.trip_stop.models import TripStop
from app.utils.decorators import transactional


class TripService:
    """Service for managing trip operations."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        bus_service: BusService = Depends(),
        stop_service: StopService = Depends(),
        seat_service: SeatService = Depends(),
    ):
        self._session = session
        self._bus_service = bus_service
        self._stop_service = stop_service
        self._seat_service = seat_service

    async def get_trips(self) -> list[Trip]:
        result = await self._session.execute(select(Trip))
        return list(result.scalars().all())

    async def get_trip(self, trip_id: UUID) -> Trip:
        result = await self._session.execute(select(Trip).where(Trip.id == trip_id))
        trip = result.scalars().one()
        return trip

    @transactional
    async def create_trip(self, payload: TripCreate) -> Trip:
        """Create a new trip with associated stops."""
        bus_result = await self._session.execute(select(Bus).where(Bus.id == payload.bus_id))
        bus = bus_result.scalars().one()

        trip_stmt = (
            insert(Trip)
            .values(
                bus_id=payload.bus_id,
                seats_left=bus.seats_quantity,
            )
            .returning(Trip)
        )
        trip_res = await self._session.execute(trip_stmt)
        trip = trip_res.scalar_one()

        await self._seat_service._create_seats_for_bus(bus.seats_quantity, trip.id)

        if payload.stops:
            stops_data = [{**stop.model_dump(), 'trip_id': trip.id} for stop in payload.stops]
            await self._session.execute(insert(TripStop).values(stops_data))

        await self._session.refresh(trip)
        return trip

    @transactional
    async def update_trip(self, trip_id: UUID, payload: TripUpdate) -> Trip:
        """Update trip and its stops. Bus change is restricted."""
        trip = await self.get_trip(trip_id)

        if payload.stops is not None:
            await self._session.execute(delete(TripStop).where(TripStop.trip_id == trip_id))

            if payload.stops:
                stops_data = [{**stop.model_dump(), 'trip_id': trip_id} for stop in payload.stops]
                await self._session.execute(insert(TripStop).values(stops_data))

        await self._session.refresh(trip)
        return trip

    @transactional
    async def delete_trip(self, trip_id: UUID) -> None:
        trip = await self.get_trip(trip_id)
        await self._session.delete(trip)
        await self._session.commit()
