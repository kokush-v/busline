from datetime import UTC, datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient
from pydantic import TypeAdapter
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.bus.schemas import BusRead
from app.features.bus.service import BusService
from app.features.city.schemas import CityRead
from app.features.city.service import CityService
from app.features.seat.service import SeatService
from app.features.stop.schemas import StopRead
from app.features.stop.service import StopService
from app.features.trip.schemas import TripRead, TripReadPublic
from app.features.trip_stop.schemas import TripStopCreate
from tests.factories import BusCreateFactory, CityCreateFactory, StopCreateFactory, TripStopCreateFactory


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
    session: AsyncSession, bus_id, stops: list[TripStopCreate] | None = None, price_per_seat: float = 100.0
) -> TripRead:
    from sqlalchemy import select

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


class TestTripsCreate:
    async def test_fail_without_stops(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        payload = {'bus_id': str(bus.id), 'price_per_seat': 100.0, 'stops': []}

        response = await client.post('/trips', json=payload)
        assert response.status_code == 422

    async def test_success_with_stops(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        city = await create_test_city(session)
        stop1 = await create_test_stop(session, city.id)
        stop2 = await create_test_stop(session, city.id)

        trip_stop1 = TripStopCreateFactory.build(stop_id=stop1.id, position_index=1, hours_offset=0)
        trip_stop2 = TripStopCreateFactory.build(stop_id=stop2.id, position_index=2, hours_offset=2)

        payload = {
            'bus_id': str(bus.id),
            'price_per_seat': 150.0,
            'stops': [
                {
                    'stop_id': str(trip_stop1.stop_id),
                    'position_index': trip_stop1.position_index,
                    'arrival_time': trip_stop1.arrival_time.isoformat(),
                    'departure_time': trip_stop1.departure_time.isoformat(),
                },
                {
                    'stop_id': str(trip_stop2.stop_id),
                    'position_index': trip_stop2.position_index,
                    'arrival_time': trip_stop2.arrival_time.isoformat(),
                    'departure_time': trip_stop2.departure_time.isoformat(),
                },
            ],
        }

        response = await client.post('/trips', json=payload)
        assert response.status_code == 201

        created_trip = TripRead.model_validate(response.json())
        assert created_trip.bus_id == bus.id

        # Verify stops by fetching the trip again (relationships loaded on read)
        get_response = await client.get(f'/trips/{created_trip.id}')
        assert get_response.status_code == 200
        fetched_trip = TripReadPublic.model_validate(get_response.json())
        assert len(fetched_trip.trip_stops) == 2

    async def test_fail_bus_not_found(self, session: AsyncSession, client: AsyncClient):
        base_time = datetime.now(UTC) + timedelta(days=1)
        payload = {
            'bus_id': str(uuid4()),
            'price_per_seat': 100.0,
            'stops': [
                {
                    'stop_id': str(uuid4()),
                    'position_index': 1,
                    'arrival_time': base_time.isoformat(),
                    'departure_time': (base_time + timedelta(minutes=15)).isoformat(),
                },
                {
                    'stop_id': str(uuid4()),
                    'position_index': 2,
                    'arrival_time': (base_time + timedelta(hours=1)).isoformat(),
                    'departure_time': (base_time + timedelta(hours=1, minutes=15)).isoformat(),
                },
            ],
        }

        response = await client.post('/trips', json=payload)
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Resource not found'

    async def test_fail_invalid_stop_position(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        city = await create_test_city(session)
        stop = await create_test_stop(session, city.id)

        base_time = datetime.now(UTC) + timedelta(days=1)
        payload = {
            'bus_id': str(bus.id),
            'stops': [
                {
                    'stop_id': str(stop.id),
                    'position_index': 0,  # Invalid: must be >= 1
                    'arrival_time': base_time.isoformat(),
                    'departure_time': (base_time + timedelta(minutes=15)).isoformat(),
                },
            ],
        }

        response = await client.post('/trips', json=payload)
        assert response.status_code == 422

    async def test_fail_departure_before_arrival(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        city = await create_test_city(session)
        stop = await create_test_stop(session, city.id)

        base_time = datetime.now(UTC) + timedelta(days=1)
        payload = {
            'bus_id': str(bus.id),
            'stops': [
                {
                    'stop_id': str(stop.id),
                    'position_index': 1,
                    'arrival_time': base_time.isoformat(),
                    'departure_time': (base_time - timedelta(minutes=15)).isoformat(),  # Before arrival
                },
            ],
        }

        response = await client.post('/trips', json=payload)
        assert response.status_code == 422

    async def test_fail_trip_with_one_stop(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        city = await create_test_city(session)
        stop = await create_test_stop(session, city.id)

        base_time = datetime.now(UTC) + timedelta(days=1)
        payload = {
            'bus_id': str(bus.id),
            'stops': [
                {
                    'stop_id': str(stop.id),
                    'position_index': 1,
                    'arrival_time': base_time.isoformat(),
                    'departure_time': (base_time + timedelta(minutes=15)).isoformat(),
                },
            ],
        }

        response = await client.post('/trips', json=payload)
        assert response.status_code == 422


class TestTripsList:
    async def test_list_empty(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/trips', params={'sort_by': 'created_at'})
        assert response.status_code == 200
        assert response.json()['items'] == []
        assert response.json()['total'] == 0

    async def test_list(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        trip = await create_test_trip(session, bus.id)

        response = await client.get('/trips', params={'sort_by': 'created_at'})
        assert response.status_code == 200

        data = response.json()
        response_trips = TypeAdapter(list[TripReadPublic]).validate_python(data['items'])
        assert len(response_trips) == 1
        assert response_trips[0].bus_id == trip.bus_id


class TestTripsGet:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        trip = await create_test_trip(session, bus.id)

        response = await client.get(f'/trips/{trip.id}')
        assert response.status_code == 200

        response_trip = TripReadPublic.model_validate(response.json())
        assert response_trip.bus_id == trip.bus_id
        assert response_trip.seats_left == bus.seats_quantity

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        response = await client.get(f'/trips/{uuid4()}')
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Resource not found'


class TestTripsUpdate:
    async def test_success_update_bus_id_ignored(self, session: AsyncSession, client: AsyncClient):
        """bus_id change is restricted — payload with bus_id should be ignored."""
        bus1 = await create_test_bus(session, seats_quantity=40)
        bus2 = await create_test_bus(session, seats_quantity=60)
        trip = await create_test_trip(session, bus1.id)

        payload = {'bus_id': str(bus2.id)}

        response = await client.put(f'/trips/{trip.id}', json=payload)
        assert response.status_code == 200

        updated_trip = TripRead.model_validate(response.json())
        assert updated_trip.bus_id == bus1.id
        assert updated_trip.seats_left == bus1.seats_quantity

    async def test_success_update_stops(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        city = await create_test_city(session)
        stop1 = await create_test_stop(session, city.id)
        stop2 = await create_test_stop(session, city.id)
        trip = await create_test_trip(session, bus.id)

        trip_stop1 = TripStopCreateFactory.build(stop_id=stop1.id, position_index=1, hours_offset=0)
        trip_stop2 = TripStopCreateFactory.build(stop_id=stop2.id, position_index=2, hours_offset=2)

        payload = {
            'stops': [
                {
                    'stop_id': str(trip_stop1.stop_id),
                    'position_index': trip_stop1.position_index,
                    'arrival_time': trip_stop1.arrival_time.isoformat(),
                    'departure_time': trip_stop1.departure_time.isoformat(),
                },
                {
                    'stop_id': str(trip_stop2.stop_id),
                    'position_index': trip_stop2.position_index,
                    'arrival_time': trip_stop2.arrival_time.isoformat(),
                    'departure_time': trip_stop2.departure_time.isoformat(),
                },
            ]
        }

        response = await client.put(f'/trips/{trip.id}', json=payload)
        assert response.status_code == 200

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        payload = {'bus_id': str(bus.id)}

        response = await client.put(f'/trips/{uuid4()}', json=payload)
        assert response.status_code == 404

    async def test_bus_id_in_payload_ignored(self, session: AsyncSession, client: AsyncClient):
        """bus_id in update payload should be ignored, not cause an error."""
        bus = await create_test_bus(session)
        trip = await create_test_trip(session, bus.id)

        payload = {'bus_id': str(uuid4())}

        response = await client.put(f'/trips/{trip.id}', json=payload)
        assert response.status_code == 200

        updated_trip = TripRead.model_validate(response.json())
        assert updated_trip.bus_id == bus.id

    async def test_fail_duplicate_position_index(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        city = await create_test_city(session)
        stop1 = await create_test_stop(session, city.id)
        stop2 = await create_test_stop(session, city.id)
        trip = await create_test_trip(session, bus.id)

        base_time = datetime.now(UTC) + timedelta(days=1)
        payload = {
            'stops': [
                {
                    'stop_id': str(stop1.id),
                    'position_index': 1,
                    'arrival_time': base_time.isoformat(),
                    'departure_time': (base_time + timedelta(minutes=15)).isoformat(),
                },
                {
                    'stop_id': str(stop2.id),
                    'position_index': 1,  # Duplicate position_index
                    'arrival_time': (base_time + timedelta(hours=1)).isoformat(),
                    'departure_time': (base_time + timedelta(hours=1, minutes=15)).isoformat(),
                },
            ]
        }

        response = await client.put(f'/trips/{trip.id}', json=payload)
        assert response.status_code == 422


class TestTripsDelete:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        trip = await create_test_trip(session, bus.id)

        response = await client.delete(f'/trips/{trip.id}')
        assert response.status_code == 204

        get_response = await client.get(f'/trips/{trip.id}')
        assert get_response.status_code == 404

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        response = await client.delete(f'/trips/{uuid4()}')
        assert response.status_code == 404
