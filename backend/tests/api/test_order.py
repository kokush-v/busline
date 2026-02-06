from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from httpx import AsyncClient
from pydantic import TypeAdapter
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.bus.schemas import BusRead
from app.features.bus.service import BusService
from app.features.city.schemas import CityRead
from app.features.city.service import CityService
from app.features.order.enums import OrderStatus
from app.features.order.models import Order
from app.features.order.schemas import OrderPaymentResponse, OrderRead
from app.features.seat.enums import SeatStatus
from app.features.seat.models import Seat
from app.features.seat.schemas import SeatRead
from app.features.seat.service import SeatService
from app.features.stop.schemas import StopRead
from app.features.stop.service import StopService
from app.features.ticket.schemas import TicketRead
from app.features.trip.schemas import TripRead
from app.features.trip_stop.schemas import TripStopCreate
from tests.conftest import TEST_USER_ID
from tests.factories import (
    BusCreateFactory,
    CityCreateFactory,
    ReserveTicketRequestFactory,
    StopCreateFactory,
    TripStopCreateFactory,
)


async def create_test_bus(session: AsyncSession, **kwargs) -> BusRead:
    bus_data = BusCreateFactory.build(**kwargs)
    bus = await BusService(session).create_bus(bus_data)
    return BusRead.model_validate(bus)


async def create_test_city(session: AsyncSession, **kwargs) -> CityRead:
    city_data = CityCreateFactory.build(**kwargs)
    city = await CityService(session).create_city(city_data)
    return CityRead.model_validate(city)


async def create_test_stop(session: AsyncSession, city_id, **kwargs) -> StopRead:
    stop_data = StopCreateFactory.build(city_id=city_id, **kwargs)
    city_service = CityService(session)
    stop = await StopService(session, city_service).create_stop(stop_data)
    return StopRead.model_validate(stop)


async def create_test_trip(
    session: AsyncSession, bus_id, stops: list[TripStopCreate] | None = None, price_per_seat: float = 50.0
) -> TripRead:
    from app.features.bus.models import Bus
    from app.features.trip.models import Trip
    from app.features.trip_stop.models import TripStop

    bus_result = await session.execute(select(Bus).where(Bus.id == bus_id))
    bus = bus_result.scalar_one()

    trip_stmt = (
        insert(Trip).values(bus_id=bus_id, price_per_seat=price_per_seat, seats_left=bus.seats_quantity).returning(Trip)
    )
    trip_result = await session.execute(trip_stmt)
    trip = trip_result.scalar_one()

    seat_service = SeatService(session, ticket_service=None, order_service=None, trip_stop_service=None)
    await seat_service._create_seats_for_bus(bus.seats_quantity, trip.id)

    if stops:
        stops_data = [{**stop.model_dump(), 'trip_id': trip.id} for stop in stops]
        await session.execute(insert(TripStop).values(stops_data))

    await session.refresh(trip)
    return TripRead.model_validate(trip)


async def create_test_seats(session: AsyncSession, trip_id, count: int = 3) -> list[SeatRead]:
    """Create test seats for a trip."""
    seats_data = [{'trip_id': trip_id, 'position_index': i + 1, 'status': SeatStatus.FREE} for i in range(count)]
    result = await session.execute(insert(Seat).values(seats_data).returning(Seat))
    seats = result.scalars().all()
    return [SeatRead.model_validate(seat) for seat in seats]


async def create_reservation(
    client: AsyncClient,
    trip_id,
    seats: list[SeatRead],
    start_stop_id,
    finish_stop_id,
) -> dict:
    """Helper to create a reservation via API using factories."""
    tickets = [
        ReserveTicketRequestFactory.build(
            seat_id=seat.id,
            start_stop_id=start_stop_id,
            finish_stop_id=finish_stop_id,
        ).model_dump(mode='json')
        for seat in seats
    ]

    payload = {'trip_id': str(trip_id), 'tickets': tickets}

    response = await client.post('/seats/reserve', json=payload)
    return response


async def setup_trip_with_stops_and_seats(session: AsyncSession, client: AsyncClient):
    """Helper to set up a complete trip with stops and seats."""
    bus = await create_test_bus(session)
    city = await create_test_city(session)
    stop1 = await create_test_stop(session, city.id)
    stop2 = await create_test_stop(session, city.id)

    trip_stop1 = TripStopCreateFactory.build(stop_id=stop1.id, position_index=1, hours_offset=0)
    trip_stop2 = TripStopCreateFactory.build(stop_id=stop2.id, position_index=2, hours_offset=2)

    trip = await create_test_trip(session, bus.id, [trip_stop1, trip_stop2])
    seats = await create_test_seats(session, trip.id, count=5)

    return trip, seats, stop1, stop2


class TestOrderGet:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session, client)

        # Create a reservation first
        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        assert reserve_response.status_code == 201
        order_id = reserve_response.json()['id']

        # Get the order
        response = await client.get(f'/orders/{order_id}')
        assert response.status_code == 200

        order = OrderRead.model_validate(response.json())
        assert order.status == OrderStatus.PENDING
        assert order.total_price == Decimal('50.00')

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        unreal_id = uuid4()
        response = await client.get(f'/orders/{unreal_id}')
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Resource not found'


class TestOrderPay:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session, client)

        # Create a reservation
        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        assert reserve_response.status_code == 201
        order_id = reserve_response.json()['id']

        # Pay the order
        response = await client.post(f'/orders/{order_id}/pay')
        assert response.status_code == 200

        payment_response = OrderPaymentResponse.model_validate(response.json())
        assert str(payment_response.order_id) == str(order_id)
        assert payment_response.message.startswith('Payment request')

    async def test_already_paid(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session, client)

        # Create and pay a reservation
        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        order_id = reserve_response.json()['id']

        await client.post(f'/orders/{order_id}/pay')

        # Try to pay again
        response = await client.post(f'/orders/{order_id}/pay')
        assert response.status_code == 200  # Should return 200 (idempotent)

        payment_response = OrderPaymentResponse.model_validate(response.json())
        assert str(payment_response.order_id) == str(order_id)
        assert payment_response.message.startswith('Payment request')

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        unreal_id = uuid4()
        response = await client.post(f'/orders/{unreal_id}/pay')
        assert response.status_code == 200

        payment_response = OrderPaymentResponse.model_validate(response.json())
        assert payment_response.order_id == unreal_id


class TestOrderCancel:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session, client)

        # Create a reservation
        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        assert reserve_response.status_code == 201
        order_id = reserve_response.json()['id']

        # Cancel the order
        response = await client.delete(f'/orders/{order_id}')
        assert response.status_code == 204

        # Verify order is cancelled
        get_response = await client.get(f'/orders/{order_id}')
        assert get_response.status_code == 200
        order = OrderRead.model_validate(get_response.json())
        assert order.status == OrderStatus.CANCELLED

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        unreal_id = uuid4()
        response = await client.delete(f'/orders/{unreal_id}')
        assert response.status_code == 404


class TestOrderTickets:
    async def test_get_order_tickets(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session, client)

        # Create a reservation with multiple tickets
        reserve_response = await create_reservation(client, trip.id, seats[:2], stop1.id, stop2.id)
        assert reserve_response.status_code == 201
        order_id = reserve_response.json()['id']

        # Get order tickets
        response = await client.get(f'/orders/{order_id}/tickets')
        assert response.status_code == 200

        tickets = TypeAdapter(list[TicketRead]).validate_python(response.json())
        assert len(tickets) == 2

    async def test_get_order_tickets_empty(self, session: AsyncSession, client: AsyncClient):
        """Test that an order without tickets returns empty list."""
        # Create order directly in DB without tickets
        order_data = {
            'status': OrderStatus.PENDING,
            'total_price': Decimal('0.00'),
            'expires_at': datetime.now(UTC) + timedelta(minutes=30),
            'user_id': UUID(TEST_USER_ID),
        }
        result = await session.execute(insert(Order).values(**order_data).returning(Order))
        order = result.scalar_one()

        response = await client.get(f'/orders/{order.id}/tickets')
        assert response.status_code == 200
        assert response.json() == []
