from uuid import uuid4

from httpx import AsyncClient
import pytest


async def _create_city(client: AsyncClient, name: str = 'Kyiv') -> dict:
    response = await client.post(
        '/cities',
        json={'name': name, 'longitude': 30.5, 'latitude': 50.45},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_city(client: AsyncClient):
    response = await client.post('/cities', json={'name': 'Lviv', 'longitude': 24.0, 'latitude': 49.84})
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'Lviv'
    assert data['longitude'] == 24.0
    assert data['latitude'] == 49.84
    assert 'id' in data


@pytest.mark.asyncio
async def test_create_city_validation_bounds(client: AsyncClient):
    response = await client.post(
        '/cities',
        json={'name': 'NorthPole', 'longitude': 200.0, 'latitude': 90.1},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_cities_list(client: AsyncClient):
    created = await _create_city(client)

    list_response = await client.get('/cities')
    assert list_response.status_code == 200
    assert any(city['id'] == created['id'] for city in list_response.json())


@pytest.mark.asyncio
async def test_get_city_by_id(client: AsyncClient):
    created = await _create_city(client)

    detail_response = await client.get(f'/cities/{created["id"]}')
    assert detail_response.status_code == 200
    assert detail_response.json()['name'] == created['name']


@pytest.mark.asyncio
async def test_get_city_not_found(client: AsyncClient):
    fake_uuid = uuid4()
    response = await client.get(f'/cities/{fake_uuid}')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_city(client: AsyncClient):
    created = await _create_city(client)

    response = await client.put(
        f'/cities/{created["id"]}',
        json={'name': 'Updated City', 'longitude': 31.0},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['name'] == 'Updated City'
    assert body['longitude'] == 31.0


@pytest.mark.asyncio
async def test_update_city_partial(client: AsyncClient):
    created = await _create_city(client)

    response = await client.put(
        f'/cities/{created["id"]}',
        json={'name': 'Only Name Updated'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['name'] == 'Only Name Updated'
    assert body['longitude'] == created['longitude']


@pytest.mark.asyncio
async def test_delete_city(client: AsyncClient):
    created = await _create_city(client)

    response = await client.delete(f'/cities/{created["id"]}')
    assert response.status_code == 204

    get_response = await client.get(f'/cities/{created["id"]}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_city_not_found(client: AsyncClient):
    fake_uuid = uuid4()
    response = await client.delete(f'/cities/{fake_uuid}')
    assert response.status_code == 404
