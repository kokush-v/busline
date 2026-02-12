from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

from httpx import AsyncClient
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.aws.s3_service import S3Service
from app.core.exeptions.s3 import S3Exception
from app.features.bus.schemas import BusRead
from app.features.bus.service import BusService
from tests.factories import BusCreateFactory


async def create_test_bus(session: AsyncSession, **kwargs) -> BusRead:
    bus_data = BusCreateFactory.build(**kwargs)
    bus = await BusService(session).create_bus(bus_data)
    return BusRead.model_validate(bus)


class TestBusesCreate:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        payload = BusCreateFactory.build().model_dump()

        response = await client.post('/buses', json=payload)
        assert response.status_code == 201

        created_bus = BusRead.model_validate(response.json())
        assert created_bus.color == payload['color']
        assert created_bus.seats_quantity == payload['seats_quantity']
        assert created_bus.number_plate == payload['number_plate']
        assert created_bus.photo_url is None
        assert created_bus.thumbnail_url is None

    async def test_fail_already_exist(self, session: AsyncSession, client: AsyncClient):
        exist_bus = await create_test_bus(session)
        payload = BusCreateFactory.build(number_plate=exist_bus.number_plate).model_dump()

        response = await client.post('/buses', json=payload)
        assert response.status_code == 400
        assert response.json()['message'] == 'Bus with this number plate already exists'

    async def test_fail_negative_seats(self, session: AsyncSession, client: AsyncClient):
        payload = BusCreateFactory.build().model_dump()
        payload['seats_quantity'] = -1

        response = await client.post('/buses', json=payload)
        assert response.status_code == 422

    async def test_fail_empty_color(self, session: AsyncSession, client: AsyncClient):
        payload = BusCreateFactory.build().model_dump()
        payload['color'] = ''

        response = await client.post('/buses', json=payload)
        assert response.status_code == 422

    async def test_fail_empty_number_plate(self, session: AsyncSession, client: AsyncClient):
        payload = BusCreateFactory.build().model_dump()
        payload['number_plate'] = ''

        response = await client.post('/buses', json=payload)
        assert response.status_code == 422


class TestBusesList:
    async def test_list_empty(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/buses')
        assert response.status_code == 200
        assert response.json()['items'] == []
        assert response.json()['total'] == 0

    async def test_list(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)

        response = await client.get('/buses')
        assert response.status_code == 200

        data = response.json()
        response_buses = TypeAdapter(list[BusRead]).validate_python(data['items'])
        assert len(response_buses) == 1
        assert response_buses[0].number_plate == bus.number_plate


class TestBusesGet:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)

        response = await client.get(f'/buses/{bus.id}')
        assert response.status_code == 200

        response_bus = BusRead.model_validate(response.json())
        assert response_bus.number_plate == bus.number_plate
        assert response_bus.color == bus.color

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        response = await client.get(f'/buses/{uuid4()}')
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Resource not found'


class TestBusesUpdate:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        payload = {'color': 'UpdatedColor'}

        response = await client.put(f'/buses/{bus.id}', json=payload)
        assert response.status_code == 200

        updated_bus = BusRead.model_validate(response.json())
        assert updated_bus.color == 'UpdatedColor'
        assert updated_bus.number_plate == bus.number_plate

    async def test_success_update_seats(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        payload = {'seats_quantity': 60}

        response = await client.put(f'/buses/{bus.id}', json=payload)
        assert response.status_code == 200

        updated_bus = BusRead.model_validate(response.json())
        assert updated_bus.seats_quantity == 60

    async def test_success_update_number_plate(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        new_plate = 'NEW1234'
        payload = {'number_plate': new_plate}

        response = await client.put(f'/buses/{bus.id}', json=payload)
        assert response.status_code == 200

        updated_bus = BusRead.model_validate(response.json())
        assert updated_bus.number_plate == new_plate

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        payload = {'color': 'UpdatedColor'}

        response = await client.put(f'/buses/{uuid4()}', json=payload)
        assert response.status_code == 404

    async def test_fail_duplicate_number_plate(self, session: AsyncSession, client: AsyncClient):
        bus1 = await create_test_bus(session)
        bus2 = await create_test_bus(session)
        payload = {'number_plate': bus1.number_plate}

        response = await client.put(f'/buses/{bus2.id}', json=payload)
        assert response.status_code == 400
        assert response.json()['message'] == 'Bus with this number plate already exists'


class TestBusesDelete:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)

        response = await client.delete(f'/buses/{bus.id}')
        assert response.status_code == 204

        get_response = await client.get(f'/buses/{bus.id}')
        assert get_response.status_code == 404

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        response = await client.delete(f'/buses/{uuid4()}')
        assert response.status_code == 404


class TestBusesPresignedUrl:
    async def test_get_upload_url_success(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        payload = {'filename': 'test-image.jpg', 'content_type': 'image/jpeg'}

        response = await client.post(f'/buses/{bus.id}/upload-url', json=payload)
        assert response.status_code == 200

        data = response.json()
        assert 'upload_url' in data
        assert 'photo_key' in data
        UUID(data['photo_key'])  # validate it's a valid UUID
        assert 'fields' in data

    async def test_get_upload_url_png(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        payload = {'filename': 'test-image.png', 'content_type': 'image/png'}

        response = await client.post(f'/buses/{bus.id}/upload-url', json=payload)
        assert response.status_code == 200

    async def test_get_upload_url_invalid_content_type(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        payload = {'filename': 'test-file.pdf', 'content_type': 'application/pdf'}

        response = await client.post(f'/buses/{bus.id}/upload-url', json=payload)
        assert response.status_code == 422


class TestBusesImageSave:
    async def test_save_image_success(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        photo_key = 'buses/test-image.jpg'

        with patch.object(S3Service, 'validate_object_access', new_callable=AsyncMock):
            response = await client.post(f'/buses/{bus.id}/image/save', json={'photo_key': photo_key})
        assert response.status_code == 200

        updated_bus = BusRead.model_validate(response.json())
        assert updated_bus.photo_url is not None
        assert 'test-image.jpg' in updated_bus.photo_url

    async def test_save_image_thumbnail_missing(self, session: AsyncSession, client: AsyncClient):
        bus = await create_test_bus(session)
        photo_key = f'buses/{uuid4()}.jpg'

        mock = AsyncMock(side_effect=[None, S3Exception(status=404, message='File not found in S3')])
        with patch.object(S3Service, 'validate_object_access', mock):
            response = await client.post(f'/buses/{bus.id}/image/save', json={'photo_key': photo_key})
        assert response.status_code == 404

    async def test_save_image_not_found(self, session: AsyncSession, client: AsyncClient):
        payload = {'photo_key': 'buses/test-image.jpg'}

        response = await client.post(f'/buses/{uuid4()}/image/save', json=payload)
        assert response.status_code == 404


class TestBusesImageDelete:
    async def test_delete_image_not_found(self, session: AsyncSession, client: AsyncClient):
        response = await client.delete(f'/buses/{uuid4()}/image')
        assert response.status_code == 404
