from uuid import uuid4

from httpx import AsyncClient
import pytest


async def _create_city(client: AsyncClient, name: str = None) -> dict:
    """Helper function to create a city for testing."""
    if name is None:
        name = f'City{uuid4().hex[:8]}'

    response = await client.post(
        '/cities',
        json={
            'name': name,
            'longitude': 30.5,
            'latitude': 50.45,
        },
    )
    assert response.status_code == 201
    return response.json()


async def _create_stop(
    client: AsyncClient,
    city_id: str = None,
    name: str = None,
    latitude: float = 50.45,
    longitude: float = 30.5,
) -> dict:
    """Helper function to create a stop for testing."""
    if city_id is None:
        city = await _create_city(client)
        city_id = city['id']

    if name is None:
        name = f'Stop{uuid4().hex[:8]}'

    response = await client.post(
        '/stops',
        json={
            'city_id': city_id,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_stop(client: AsyncClient):
    """Test creating a new stop."""
    city = await _create_city(client, name='Kyiv')

    response = await client.post(
        '/stops',
        json={
            'city_id': city['id'],
            'name': 'Central Station',
            'latitude': 50.4501,
            'longitude': 30.5234,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data['city_id'] == city['id']
    assert data['name'] == 'Central Station'
    assert data['latitude'] == 50.4501
    assert data['longitude'] == 30.5234
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data


@pytest.mark.asyncio
async def test_create_stop_invalid_city(client: AsyncClient):
    """Test creating a stop with non-existent city."""
    fake_city_id = str(uuid4())

    response = await client.post(
        '/stops',
        json={
            'city_id': fake_city_id,
            'name': 'Test Stop',
            'latitude': 50.45,
            'longitude': 30.5,
        },
    )
    assert response.status_code == 404
    assert 'City not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_create_stop_validation_empty_name(client: AsyncClient):
    """Test creating a stop with empty name."""
    city = await _create_city(client)

    response = await client.post(
        '/stops',
        json={
            'city_id': city['id'],
            'name': '',
            'latitude': 50.45,
            'longitude': 30.5,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_stop_validation_invalid_coordinates(client: AsyncClient):
    """Test creating a stop with invalid coordinates."""
    city = await _create_city(client)

    response = await client.post(
        '/stops',
        json={
            'city_id': city['id'],
            'name': 'Invalid Stop',
            'latitude': 200.0,  # Invalid latitude
            'longitude': 30.5,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_stops_list(client: AsyncClient):
    """Test getting all stops."""
    created = await _create_stop(client)

    list_response = await client.get('/stops')
    assert list_response.status_code == 200
    stops = list_response.json()
    assert isinstance(stops, list)
    assert any(stop['id'] == created['id'] for stop in stops)


@pytest.mark.asyncio
async def test_get_stops_list_empty(client: AsyncClient):
    """Test getting stops list when empty."""
    list_response = await client.get('/stops')
    assert list_response.status_code == 200
    stops = list_response.json()
    assert isinstance(stops, list)
    assert len(stops) == 0


@pytest.mark.asyncio
async def test_get_stops_search_by_stop_name(client: AsyncClient):
    """Test searching stops by stop name."""
    city = await _create_city(client, name='Kyiv')
    stop1 = await _create_stop(client, city_id=city['id'], name='Central Station')
    stop2 = await _create_stop(client, city_id=city['id'], name='Airport Terminal')

    # Search for "Central"
    response = await client.get('/stops?search=Central')
    assert response.status_code == 200
    stops = response.json()
    stop_ids = [stop['id'] for stop in stops]
    assert stop1['id'] in stop_ids
    assert stop2['id'] not in stop_ids


@pytest.mark.asyncio
async def test_get_stops_search_by_city_name(client: AsyncClient):
    """Test searching stops by city name."""
    city1 = await _create_city(client, name='Kyiv')
    city2 = await _create_city(client, name='Lviv')
    stop1 = await _create_stop(client, city_id=city1['id'], name='Stop A')
    stop2 = await _create_stop(client, city_id=city2['id'], name='Stop B')

    # Search for "Kyiv"
    response = await client.get('/stops?search=Kyiv')
    assert response.status_code == 200
    stops = response.json()
    stop_ids = [stop['id'] for stop in stops]
    assert stop1['id'] in stop_ids
    assert stop2['id'] not in stop_ids


@pytest.mark.asyncio
async def test_get_stops_search_case_insensitive(client: AsyncClient):
    """Test that search is case-insensitive."""
    city = await _create_city(client, name='Kyiv')
    stop = await _create_stop(client, city_id=city['id'], name='Central Station')

    # Search with different case
    response = await client.get('/stops?search=central')
    assert response.status_code == 200
    stops = response.json()
    assert any(s['id'] == stop['id'] for s in stops)


@pytest.mark.asyncio
async def test_get_stop_by_id(client: AsyncClient):
    """Test getting a specific stop by ID."""
    created = await _create_stop(client)

    detail_response = await client.get(f'/stops/{created["id"]}')
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert data['id'] == created['id']
    assert data['name'] == created['name']
    assert data['city_id'] == created['city_id']


@pytest.mark.asyncio
async def test_get_stop_not_found(client: AsyncClient):
    """Test getting a non-existent stop."""
    fake_uuid = uuid4()
    response = await client.get(f'/stops/{fake_uuid}')
    assert response.status_code == 404
    assert 'Stop not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_update_stop_name(client: AsyncClient):
    """Test updating a stop's name."""
    created = await _create_stop(client)

    response = await client.put(
        f'/stops/{created["id"]}',
        json={'name': 'Updated Stop Name'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == created['id']
    assert data['name'] == 'Updated Stop Name'
    assert data['city_id'] == created['city_id']


@pytest.mark.asyncio
async def test_update_stop_coordinates(client: AsyncClient):
    """Test updating a stop's coordinates."""
    created = await _create_stop(client)

    response = await client.put(
        f'/stops/{created["id"]}',
        json={'latitude': 51.5074, 'longitude': -0.1278},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['latitude'] == 51.5074
    assert data['longitude'] == -0.1278


@pytest.mark.asyncio
async def test_update_stop_city(client: AsyncClient):
    """Test updating a stop's city."""
    created = await _create_stop(client)
    city2 = await _create_city(client, name='Lviv')

    response = await client.put(
        f'/stops/{created["id"]}',
        json={'city_id': city2['id']},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['city_id'] == city2['id']


@pytest.mark.asyncio
async def test_update_stop_invalid_city(client: AsyncClient):
    """Test updating a stop with non-existent city."""
    created = await _create_stop(client)
    fake_city_id = str(uuid4())

    response = await client.put(
        f'/stops/{created["id"]}',
        json={'city_id': fake_city_id},
    )
    assert response.status_code == 404
    assert 'City not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_update_stop_not_found(client: AsyncClient):
    """Test updating a non-existent stop."""
    fake_uuid = uuid4()

    response = await client.put(
        f'/stops/{fake_uuid}',
        json={'name': 'New Name'},
    )
    assert response.status_code == 404
    assert 'Stop not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_update_stop_partial(client: AsyncClient):
    """Test partial update of a stop."""
    created = await _create_stop(client)
    original_latitude = created['latitude']

    response = await client.put(
        f'/stops/{created["id"]}',
        json={'longitude': 25.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['longitude'] == 25.0
    assert data['latitude'] == original_latitude


@pytest.mark.asyncio
async def test_delete_stop(client: AsyncClient):
    """Test deleting a stop."""
    created = await _create_stop(client)

    response = await client.delete(f'/stops/{created["id"]}')
    assert response.status_code == 204

    # Verify stop is deleted
    get_response = await client.get(f'/stops/{created["id"]}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_stop_not_found(client: AsyncClient):
    """Test deleting a non-existent stop."""
    fake_uuid = uuid4()
    response = await client.delete(f'/stops/{fake_uuid}')
    assert response.status_code == 404
    assert 'Stop not found' in response.json()['detail']


@pytest.mark.asyncio
async def test_multiple_stops_same_city(client: AsyncClient):
    """Test creating multiple stops in the same city."""
    city = await _create_city(client, name='Kyiv')

    stop1 = await _create_stop(client, city_id=city['id'], name='Stop 1')
    stop2 = await _create_stop(client, city_id=city['id'], name='Stop 2')

    assert stop1['id'] != stop2['id']
    assert stop1['city_id'] == stop2['city_id'] == city['id']

    # Both stops should exist
    list_response = await client.get('/stops')
    stop_ids = [stop['id'] for stop in list_response.json()]
    assert stop1['id'] in stop_ids
    assert stop2['id'] in stop_ids


@pytest.mark.asyncio
async def test_stops_ordered_by_name(client: AsyncClient):
    """Test that stops are returned ordered by name."""
    city = await _create_city(client)

    await _create_stop(client, city_id=city['id'], name='Zebra Stop')
    await _create_stop(client, city_id=city['id'], name='Alpha Stop')
    await _create_stop(client, city_id=city['id'], name='Beta Stop')

    response = await client.get('/stops')
    assert response.status_code == 200
    stops = response.json()
    names = [stop['name'] for stop in stops]

    assert names == sorted(names)
