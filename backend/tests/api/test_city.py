from uuid import uuid4

from httpx import AsyncClient
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.city.schemas import CityRead
from app.features.city.service import CityService
from tests.factories import CityCreateFactory


async def create_test_city(session: AsyncSession, **kwargs) -> CityRead:
    city_data = CityCreateFactory.build(**kwargs)
    city = await CityService(session).create_city(city_data)
    return CityRead.model_validate(city)


class TestCitiesCreate:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        payload = CityCreateFactory.build().model_dump()

        response = await client.post('/cities', json=payload)
        assert response.status_code == 201

        created_city = CityRead.model_validate(response.json())
        assert created_city.name == payload['name']
        assert created_city.longitude == payload['longitude']
        assert created_city.latitude == payload['latitude']

    async def test_fail_already_exist(self, session: AsyncSession, client: AsyncClient):
        exist_city = await create_test_city(session)
        payload = CityCreateFactory.build(name=exist_city.name).model_dump()

        response = await client.post('/cities', json=payload)
        assert response.status_code == 400
        assert response.json()['error']['message'] == 'City with this name already exists'

    async def test_fail_invalid_longitude(self, session: AsyncSession, client: AsyncClient):
        payload = CityCreateFactory.build().model_dump()
        payload['longitude'] = 181.0

        response = await client.post('/cities', json=payload)
        assert response.status_code == 422

    async def test_fail_invalid_latitude(self, session: AsyncSession, client: AsyncClient):
        payload = CityCreateFactory.build().model_dump()
        payload['latitude'] = 91.0

        response = await client.post('/cities', json=payload)
        assert response.status_code == 422


class TestCitiesList:
    async def test_list_empty(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/cities')
        assert response.status_code == 200
        assert response.json()['items'] == []
        assert response.json()['total'] == 0

    async def test_list(self, session: AsyncSession, client: AsyncClient):
        city = await create_test_city(session)

        response = await client.get('/cities')
        assert response.status_code == 200

        data = response.json()
        response_cities = TypeAdapter(list[CityRead]).validate_python(data['items'])
        assert len(response_cities) == 1
        assert response_cities[0].name == city.name


class TestCitiesGet:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        city = await create_test_city(session)

        response = await client.get(f'/cities/{city.id}')
        assert response.status_code == 200

        response_city = CityRead.model_validate(response.json())
        assert response_city.name == city.name

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        response = await client.get(f'/cities/{uuid4()}')
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Resource not found'


class TestCitiesUpdate:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        city = await create_test_city(session)
        new_name = 'UpdatedCity'
        payload = {'name': new_name}

        response = await client.put(f'/cities/{city.id}', json=payload)
        assert response.status_code == 200

        updated_city = CityRead.model_validate(response.json())
        assert updated_city.name == new_name

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        payload = {'name': 'UpdatedCity'}

        response = await client.put(f'/cities/{uuid4()}', json=payload)
        assert response.status_code == 404

    async def test_fail_duplicate_name(self, session: AsyncSession, client: AsyncClient):
        city1 = await create_test_city(session)
        city2 = await create_test_city(session)
        payload = {'name': city1.name}

        response = await client.put(f'/cities/{city2.id}', json=payload)
        assert response.status_code == 400
        assert response.json()['error']['message'] == 'City with this name already exists'


class TestCitiesDelete:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        city = await create_test_city(session)

        response = await client.delete(f'/cities/{city.id}')
        assert response.status_code == 204

        get_response = await client.get(f'/cities/{city.id}')
        assert get_response.status_code == 404

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        response = await client.delete(f'/cities/{uuid4()}')
        assert response.status_code == 404
