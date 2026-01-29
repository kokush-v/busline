from uuid import uuid4

from httpx import AsyncClient
import pytest


async def _create_bus(client: AsyncClient, number_plate: str = None) -> dict:
    """Helper function to create a bus for testing."""
    if number_plate is None:
        number_plate = f'TEST{uuid4().hex[:8].upper()}'

    response = await client.post(
        '/buses',
        json={
            'color': 'Blue',
            'seats_quantity': 50,
            'number_plate': number_plate,
        },
    )
    assert response.status_code == 201
    return response.json()


async def _create_trip(client: AsyncClient, bus_id: str = None) -> dict:
    """Helper function to create a trip for testing."""
    if bus_id is None:
        bus = await _create_bus(client)
        bus_id = bus['id']

    response = await client.post(
        '/trips',
        json={'bus_id': bus_id},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_trip(client: AsyncClient):
    """Test creating a new trip."""
    bus = await _create_bus(client)

    response = await client.post(
        '/trips',
        json={'bus_id': bus['id']},
    )
    assert response.status_code == 201
    data = response.json()
    assert data['bus_id'] == bus['id']
    assert data['seats_left'] == bus['seats_quantity']
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data
    assert 'trip_stops' in data


@pytest.mark.asyncio
async def test_create_trip_invalid_bus(client: AsyncClient):
    """Test creating a trip with non-existent bus."""
    fake_bus_id = str(uuid4())

    response = await client.post(
        '/trips',
        json={'bus_id': fake_bus_id},
    )
    assert response.status_code == 404
    assert 'Bus not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_get_trips_list(client: AsyncClient):
    """Test getting all trips."""
    created = await _create_trip(client)

    list_response = await client.get('/trips')
    assert list_response.status_code == 200
    trips = list_response.json()
    assert isinstance(trips, list)
    assert any(trip['id'] == created['id'] for trip in trips)


@pytest.mark.asyncio
async def test_get_trips_list_empty(client: AsyncClient):
    """Test getting trips list when empty."""
    list_response = await client.get('/trips')
    assert list_response.status_code == 200
    trips = list_response.json()
    assert isinstance(trips, list)
    assert len(trips) == 0


@pytest.mark.asyncio
async def test_get_trip_by_id(client: AsyncClient):
    """Test getting a specific trip by ID."""
    created = await _create_trip(client)

    detail_response = await client.get(f'/trips/{created["id"]}')
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert data['id'] == created['id']
    assert data['bus_id'] == created['bus_id']
    assert data['seats_left'] == created['seats_left']


@pytest.mark.asyncio
async def test_get_trip_by_id_public_access(client: AsyncClient):
    """Test public access to trip endpoint."""
    created = await _create_trip(client)

    # Public endpoint should be accessible without authentication
    detail_response = await client.get(f'/trips/{created["id"]}')
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert 'id' in data
    assert 'bus_id' in data
    assert 'seats_left' in data
    assert 'created_at' in data


@pytest.mark.asyncio
async def test_get_trip_not_found(client: AsyncClient):
    """Test getting a non-existent trip."""
    fake_uuid = uuid4()
    response = await client.get(f'/trips/{fake_uuid}')
    assert response.status_code == 404
    assert 'Trip not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_update_trip_bus_id(client: AsyncClient):
    """Test updating a trip's bus."""
    created = await _create_trip(client)
    bus2 = await _create_bus(client)

    response = await client.put(
        f'/trips/{created["id"]}',
        json={'bus_id': bus2['id']},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == created['id']
    assert data['bus_id'] == bus2['id']
    assert data['seats_left'] == bus2['seats_quantity']


@pytest.mark.asyncio
async def test_update_trip_invalid_bus(client: AsyncClient):
    """Test updating a trip with non-existent bus."""
    created = await _create_trip(client)
    fake_bus_id = str(uuid4())

    response = await client.put(
        f'/trips/{created["id"]}',
        json={'bus_id': fake_bus_id},
    )
    assert response.status_code == 404
    assert 'Bus not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_update_trip_not_found(client: AsyncClient):
    """Test updating a non-existent trip."""
    bus = await _create_bus(client)
    fake_uuid = uuid4()

    response = await client.put(
        f'/trips/{fake_uuid}',
        json={'bus_id': bus['id']},
    )
    assert response.status_code == 404
    assert 'Trip not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_delete_trip(client: AsyncClient):
    """Test deleting a trip."""
    created = await _create_trip(client)

    response = await client.delete(f'/trips/{created["id"]}')
    assert response.status_code == 204

    # Verify trip is deleted
    get_response = await client.get(f'/trips/{created["id"]}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_trip_not_found(client: AsyncClient):
    """Test deleting a non-existent trip."""
    fake_uuid = uuid4()
    response = await client.delete(f'/trips/{fake_uuid}')
    assert response.status_code == 404
    assert 'Trip not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_multiple_trips_same_bus(client: AsyncClient):
    """Test creating multiple trips with the same bus."""
    bus = await _create_bus(client)

    # Create first trip
    trip1 = await _create_trip(client, bus_id=bus['id'])
    # Create second trip
    trip2 = await _create_trip(client, bus_id=bus['id'])

    assert trip1['id'] != trip2['id']
    assert trip1['bus_id'] == trip2['bus_id'] == bus['id']

    # Both trips should exist
    list_response = await client.get('/trips')
    trip_ids = [trip['id'] for trip in list_response.json()]
    assert trip1['id'] in trip_ids
    assert trip2['id'] in trip_ids
