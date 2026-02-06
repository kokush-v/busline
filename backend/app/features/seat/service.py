from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exeptions import ServerException
from app.database.db import get_db_session
from app.features.order.enums import OrderStatus
from app.features.order.schemas import OrderCreate
from app.features.order.service import OrderService
from app.features.seat.enums import SeatStatus
from app.features.seat.models import Seat
from app.features.seat.schemas import ReserveSeatRequest, ReserveSeatResponse
from app.features.ticket.schemas import ReserveTicketRequest, TicketCreate, TicketRead
from app.features.ticket.service import TicketService
from app.features.trip.models import Trip
from app.features.trip_stop.service import TripStopService
from app.utils.decorators import transactional


class SeatService:
    """Service for managing seats."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        ticket_service: TicketService = Depends(),
        order_service: OrderService = Depends(),
        trip_stop_service: TripStopService = Depends(),
    ):
        self._session = session
        self._ticket_service = ticket_service
        self._order_service = order_service
        self._trip_stop_service = trip_stop_service

    async def get_seat(self, seat_id: UUID) -> Seat:
        """Get seat details by ID."""
        result = await self._session.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalars().one()

    async def _create_seats_for_bus(self, seats_quantity: int, trip_id: UUID) -> list[Seat]:
        """Create seats for a specific bus and trip using Core DML."""

        result = await self._session.execute(select(Seat).where(Seat.trip_id == trip_id))
        existing_seats = list(result.scalars().all())
        if existing_seats:
            return existing_seats

        seat_data = [
            {'trip_id': trip_id, 'position_index': i, 'status': SeatStatus.FREE} for i in range(1, seats_quantity + 1)
        ]

        stmt = insert(Seat).values(seat_data).returning(Seat)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def __validate_seats_availability(self, trip_id: UUID, seat_ids: list[UUID]) -> list:
        stmt = (
            select(Seat.id, Seat.status, Seat.position_index)
            .where(Seat.trip_id == trip_id, Seat.id.in_(seat_ids))
            .with_for_update()
        )
        seats_res = await self._session.execute(stmt)
        seats = seats_res.all()

        if len(seats) != len(seat_ids):
            raise ServerException(message='One or more seats do not exist', status=409)

        for seat in seats:
            if seat.status != SeatStatus.FREE:
                raise ServerException(message=f'Seat {seat.position_index} is not available', status=409)

        return seats

    async def __create_order_for_reservation(self, trip_price: Decimal, seats_count: int) -> OrderCreate:
        price_per_seat = Decimal(str(trip_price))
        total_price = price_per_seat * seats_count
        expires_at = datetime.now(UTC) + timedelta(minutes=30)

        return OrderCreate(
            total_price=total_price,
            status=OrderStatus.PENDING,
            expires_at=expires_at,
        )

    async def __lock_reserved_seats(self, seat_ids: list[UUID]) -> None:
        await self._session.execute(update(Seat).where(Seat.id.in_(seat_ids)).values(status=SeatStatus.LOCKED))

    def __prepare_tickets_data(
        self, order_id: UUID, trip_id: UUID, price_per_seat: Decimal, tickets: list[ReserveTicketRequest]
    ) -> list[TicketCreate]:
        return [
            TicketCreate(
                order_id=order_id,
                trip_id=trip_id,
                seat_id=t.seat_id,
                price=price_per_seat,
                passenger_name=t.passenger_name,
                passenger_email=t.passenger_email,
                passenger_age=t.passenger_age,
                start_stop_id=t.start_stop_id,
                finish_stop_id=t.finish_stop_id,
            )
            for t in tickets
        ]

    @transactional
    async def reserve(self, payload: ReserveSeatRequest, user_id: UUID) -> ReserveSeatResponse:
        """
        Reserve seats, create an order, and generate tickets.
        """
        trip_id = payload.trip_id
        tickets = payload.tickets

        trip_result = await self._session.execute(select(Trip).where(Trip.id == trip_id))
        trip = trip_result.scalar_one()

        await self._trip_stop_service.validate_stops_exist_in_trip(trip_id, tickets)

        seat_ids = [t.seat_id for t in tickets]
        await self.__validate_seats_availability(trip_id, seat_ids)

        order_data = await self.__create_order_for_reservation(trip.price_per_seat, len(tickets))
        order = await self._order_service._create_order(order_data, user_id=user_id)

        await self.__lock_reserved_seats(seat_ids)

        price_per_seat = Decimal(str(trip.price_per_seat))
        tickets_data = self.__prepare_tickets_data(order.id, trip_id, price_per_seat, tickets)
        tickets = await self._ticket_service._create_many_tickets(tickets_data)

        added_tickets = [TicketRead.model_validate(ticket) for ticket in tickets]

        return ReserveSeatResponse(
            id=order.id,
            status=order.status,
            total_price=order.total_price,
            expires_at=order.expires_at,
            created_at=order.created_at,
            updated_at=order.updated_at,
            tickets=added_tickets,
        )
