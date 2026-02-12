from uuid import uuid4

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.city.schemas import CityRead, CitySearchResponse
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
        assert response.json()['message'] == 'City with this name already exists'

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
        assert response.json()['message'] == 'City with this name already exists'


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


class TestCitiesSearch:
    async def _public_client(self, app: FastAPI) -> AsyncClient:
        """Create an unauthenticated client for public endpoints."""
        return AsyncClient(transport=ASGITransport(app=app), base_url='http://test')

    async def test_search_empty(self, session: AsyncSession, app: FastAPI):
        async with await self._public_client(app) as public:
            response = await public.get('/cities/search')
        assert response.status_code == 200
        data = CitySearchResponse.model_validate(response.json())
        assert data.items == []
        assert data.has_more is False
        assert data.next_cursor is None

    async def test_search_returns_results(self, session: AsyncSession, app: FastAPI):
        await create_test_city(session, name='Kyiv')
        await create_test_city(session, name='Kharkiv')

        async with await self._public_client(app) as public:
            response = await public.get('/cities/search', params={'search': 'K'})
        assert response.status_code == 200
        data = CitySearchResponse.model_validate(response.json())
        assert len(data.items) == 2

    async def test_search_filters_by_name(self, session: AsyncSession, app: FastAPI):
        await create_test_city(session, name='Odesa')
        await create_test_city(session, name='Lviv')

        async with await self._public_client(app) as public:
            response = await public.get('/cities/search', params={'search': 'Ode'})
        assert response.status_code == 200
        data = CitySearchResponse.model_validate(response.json())
        assert len(data.items) == 1
        assert data.items[0].name == 'Odesa'

    async def test_search_pagination(self, session: AsyncSession, app: FastAPI):
        for name in ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon']:
            await create_test_city(session, name=name)

        async with await self._public_client(app) as public:
            response = await public.get('/cities/search', params={'limit': 3})
        assert response.status_code == 200
        data = CitySearchResponse.model_validate(response.json())
        assert len(data.items) == 3
        assert data.has_more is True
        assert data.next_cursor is not None

        # Fetch next page
        async with await self._public_client(app) as public:
            response = await public.get('/cities/search', params={'limit': 3, 'cursor': str(data.next_cursor)})
        assert response.status_code == 200
        data2 = CitySearchResponse.model_validate(response.json())
        assert len(data2.items) == 2
        assert data2.has_more is False
        assert data2.next_cursor is None

    async def test_search_ordered_by_name(self, session: AsyncSession, app: FastAPI):
        for name in ['Zaporizhzhia', 'Dnipro', 'Mykolaiv']:
            await create_test_city(session, name=name)

        async with await self._public_client(app) as public:
            response = await public.get('/cities/search')
        assert response.status_code == 200
        data = CitySearchResponse.model_validate(response.json())
        names = [item.name for item in data.items]
        assert names == sorted(names)

    async def test_search_no_auth_required(self, session: AsyncSession, app: FastAPI):
        """Verify the endpoint works without an Authorization header."""
        async with await self._public_client(app) as public:
            response = await public.get('/cities/search')
        assert response.status_code == 200

    async def test_search_with_auth_also_works(self, session: AsyncSession, client: AsyncClient):
        """Verify the endpoint also works with an Authorization header."""
        response = await client.get('/cities/search')
        assert response.status_code == 200
