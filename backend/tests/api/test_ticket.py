from decimal import Decimal
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.bus.schemas import BusRead
from app.features.bus.service import BusService
from app.features.city.schemas import CityRead
from app.features.city.service import CityService
from app.features.seat.enums import SeatStatus
from app.features.seat.models import Seat
from app.features.seat.schemas import SeatRead
from app.features.seat.service import SeatService
from app.features.stop.schemas import StopRead
from app.features.stop.service import StopService
from app.features.ticket.schemas import TicketRead
from app.features.trip.schemas import TripRead
from app.features.trip_stop.schemas import TripStopCreate
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
    price: Decimal = Decimal('75.00'),
) -> dict:
    """Helper to create a reservation via API using factories."""
    tickets = [
        ReserveTicketRequestFactory.build(
            seat_id=seat.id,
            start_stop_id=start_stop_id,
            finish_stop_id=finish_stop_id,
            price=price,
        ).model_dump(mode='json')
        for seat in seats
    ]

    payload = {'trip_id': str(trip_id), 'tickets': tickets}
    response = await client.post('/seats/reserve', json=payload)
    return response


async def setup_trip_with_stops_and_seats(session: AsyncSession):
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


class TestTicketGet:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        # Create a reservation to get tickets
        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        assert reserve_response.status_code == 201

        ticket_id = reserve_response.json()['tickets'][0]['id']

        # Get the ticket
        response = await client.get(f'/tickets/{ticket_id}')
        assert response.status_code == 200

        ticket = TicketRead.model_validate(response.json())
        assert ticket.price == Decimal('50.00')
        assert ticket.trip_id == trip.id

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        unreal_id = uuid4()
        response = await client.get(f'/tickets/{unreal_id}')
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Resource not found'


class TestTicketUpdate:
    async def test_success_update_passenger_name(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        # Create a reservation
        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        assert reserve_response.status_code == 201

        ticket_id = reserve_response.json()['tickets'][0]['id']

        # Update the ticket
        payload = {'passenger_name': 'Updated Name'}
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 200

        ticket = TicketRead.model_validate(response.json())
        assert ticket.passenger_name == 'Updated Name'

    async def test_success_update_passenger_email(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        ticket_id = reserve_response.json()['tickets'][0]['id']

        payload = {'passenger_email': 'newemail@test.com'}
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 200

        ticket = TicketRead.model_validate(response.json())
        assert ticket.passenger_email == 'newemail@test.com'

    async def test_success_update_passenger_age(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        ticket_id = reserve_response.json()['tickets'][0]['id']

        payload = {'passenger_age': 30}
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 200

        ticket = TicketRead.model_validate(response.json())
        assert ticket.passenger_age == 30

    async def test_success_update_unknown_field_ignored(self, session: AsyncSession, client: AsyncClient):
        """Test that unknown fields in update payload are ignored."""
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        ticket_id = reserve_response.json()['tickets'][0]['id']

        payload = {'unknown_field': 'some_value'}
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 200

        ticket = TicketRead.model_validate(response.json())
        assert ticket.pdf_status == 'PENDING'

    async def test_success_update_multiple_fields(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        ticket_id = reserve_response.json()['tickets'][0]['id']

        payload = {
            'passenger_name': 'New Passenger',
            'passenger_email': 'new@example.com',
            'passenger_age': 35,
        }
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 200

        ticket = TicketRead.model_validate(response.json())
        assert ticket.passenger_name == 'New Passenger'
        assert ticket.passenger_email == 'new@example.com'
        assert ticket.passenger_age == 35

    async def test_success_empty_update(self, session: AsyncSession, client: AsyncClient):
        """Test that empty update returns the ticket unchanged."""
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        ticket_id = reserve_response.json()['tickets'][0]['id']
        original_name = reserve_response.json()['tickets'][0]['passenger_name']

        payload = {}
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 200

        ticket = TicketRead.model_validate(response.json())
        assert ticket.passenger_name == original_name

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        unreal_id = uuid4()
        payload = {'passenger_name': 'Test'}

        response = await client.patch(f'/tickets/{unreal_id}', json=payload)
        assert response.status_code == 404

    async def test_fail_invalid_age(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        ticket_id = reserve_response.json()['tickets'][0]['id']

        payload = {'passenger_age': -1}
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 422

    async def test_fail_invalid_name_too_short(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        reserve_response = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        ticket_id = reserve_response.json()['tickets'][0]['id']

        payload = {'passenger_name': ''}
        response = await client.patch(f'/tickets/{ticket_id}', json=payload)
        assert response.status_code == 422


class TestSeatReservation:
    """Tests for the reservation flow through seats endpoint."""

    async def test_reserve_success(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        response = await create_reservation(client, trip.id, seats[:2], stop1.id, stop2.id)
        assert response.status_code == 201

        data = response.json()
        assert data['status'] == 'PENDING'
        assert Decimal(data['total_price']) == Decimal('100.00')
        assert len(data['tickets']) == 2
        assert data['expires_at'] is not None

    async def test_reserve_seat_not_available(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        # Reserve seats first time
        response1 = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        assert response1.status_code == 201

        # Try to reserve same seat again
        response2 = await create_reservation(client, trip.id, seats[:1], stop1.id, stop2.id)
        assert response2.status_code == 409
        assert 'not available' in response2.json()['error']['message']

    async def test_reserve_trip_not_found(self, session: AsyncSession, client: AsyncClient):
        fake_trip_id = uuid4()
        fake_seat_id = uuid4()
        fake_stop_id = uuid4()

        ticket_data = ReserveTicketRequestFactory.build(
            seat_id=fake_seat_id,
            start_stop_id=fake_stop_id,
            finish_stop_id=fake_stop_id,
        ).model_dump(mode='json')

        payload = {'trip_id': str(fake_trip_id), 'tickets': [ticket_data]}

        response = await client.post('/seats/reserve', json=payload)
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Resource not found'

    async def test_reserve_seat_not_exist(self, session: AsyncSession, client: AsyncClient):
        trip, seats, stop1, stop2 = await setup_trip_with_stops_and_seats(session)

        fake_seat_id = uuid4()
        ticket_data = ReserveTicketRequestFactory.build(
            seat_id=fake_seat_id,
            start_stop_id=stop1.id,
            finish_stop_id=stop2.id,
        ).model_dump(mode='json')

        payload = {'trip_id': str(trip.id), 'tickets': [ticket_data]}

        response = await client.post('/seats/reserve', json=payload)
        assert response.status_code == 409
        assert 'do not exist' in response.json()['error']['message']
