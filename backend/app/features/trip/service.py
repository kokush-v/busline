from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, asc, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.common.enums import SortOrder
from app.database.db import get_db_session
from app.features.bus.models import Bus
from app.features.bus.service import BusService
from app.features.seat.models import Seat
from app.features.seat.service import SeatService
from app.features.stop.service import StopService
from app.features.trip.models import Trip
from app.features.trip.schemas import TripCreate, TripQueryParams, TripSortBy, TripUpdate
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

    def __apply_from_stop_filter(self, query: Select, params: TripQueryParams) -> Select:
        if not params.from_stop_id:
            return query

        from_stop_subq = (
            select(TripStop.trip_id)
            .where(
                and_(
                    TripStop.stop_id == params.from_stop_id,
                    TripStop.position_index == 1,
                )
            )
            .subquery()
        )
        query = query.where(Trip.id.in_(select(from_stop_subq)))

        if params.departure_date_from or params.departure_date_to:
            date_conditions = []
            if params.departure_date_from:
                date_conditions.append(TripStop.departure_time >= params.departure_date_from)
            if params.departure_date_to:
                date_conditions.append(TripStop.departure_time <= params.departure_date_to)

            query = query.join(TripStop, Trip.id == TripStop.trip_id).where(
                and_(
                    TripStop.stop_id == params.from_stop_id,
                    TripStop.position_index == 1,
                    *date_conditions,
                )
            )

        return query

    def __apply_to_stop_filter(self, query: Select, params: TripQueryParams) -> Select:
        if not params.to_stop_id:
            return query

        to_stop_subq = select(TripStop.trip_id).where(TripStop.stop_id == params.to_stop_id).subquery()
        return query.where(Trip.id.in_(select(to_stop_subq)))

    def __apply_price_filters(self, query: Select, params: TripQueryParams) -> Select:
        if params.min_price is not None:
            query = query.where(Trip.price_per_seat >= params.min_price)
        if params.max_price is not None:
            query = query.where(Trip.price_per_seat <= params.max_price)
        return query

    def __apply_seats_filter(self, query: Select, params: TripQueryParams) -> Select:
        if params.available_seats_min is not None:
            query = query.where(Trip.seats_left >= params.available_seats_min)
        return query

    def __apply_sorting(self, query: Select, params: TripQueryParams) -> Select:
        match params.sort_by:
            case TripSortBy.DEPARTURE_TIME:
                query = query.join(TripStop, Trip.id == TripStop.trip_id).where(TripStop.position_index == 1)
                sort_column = TripStop.departure_time
            case TripSortBy.PRICE:
                sort_column = Trip.price_per_seat
            case TripSortBy.SEATS_LEFT:
                sort_column = Trip.seats_left
            case TripSortBy.CREATED_AT:
                sort_column = Trip.created_at
            case _:
                sort_column = Trip.created_at

        match params.sort_order:
            case SortOrder.DESC:
                query = query.order_by(desc(sort_column))
            case _:
                query = query.order_by(asc(sort_column))

        return query

    def __apply_pagination(self, query: Select, params: TripQueryParams) -> Select:
        return query.limit(params.limit).offset(params.offset)

    async def __get_total_count(self, query: Select) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        return total_result.scalar_one()

    async def get_trips(self, params: TripQueryParams) -> tuple[list[Trip], int]:
        """Get trips with filtering, sorting, and pagination."""
        query = select(Trip).distinct()

        query = self.__apply_from_stop_filter(query, params)
        query = self.__apply_to_stop_filter(query, params)
        query = self.__apply_price_filters(query, params)
        query = self.__apply_seats_filter(query, params)

        total = await self.__get_total_count(query)

        query = self.__apply_sorting(query, params)
        query = self.__apply_pagination(query, params)

        result = await self._session.execute(query)
        trips = list(result.scalars().all())

        return trips, total

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
                price_per_seat=payload.price_per_seat,
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

        update_data = payload.model_dump(exclude_none=True, exclude={'stops'})
        if update_data:
            await self._session.execute(update(Trip).where(Trip.id == trip_id).values(**update_data))

        if payload.stops is not None:
            await self._session.execute(delete(TripStop).where(TripStop.trip_id == trip_id))

            if payload.stops:
                stops_data = [{**stop.model_dump(), 'trip_id': trip_id} for stop in payload.stops]
                await self._session.execute(insert(TripStop).values(stops_data))

        await self._session.refresh(trip)
        return trip

    async def get_seats(self, trip_id: UUID) -> list[Seat]:
        await self.get_trip(trip_id)
        result = await self._session.execute(select(Seat).where(Seat.trip_id == trip_id))
        return list(result.scalars().all())

    @transactional
    async def delete_trip(self, trip_id: UUID) -> None:
        trip = await self.get_trip(trip_id)
        await self._session.delete(trip)
        await self._session.commit()
