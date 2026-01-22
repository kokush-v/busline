from uuid import uuid4

from httpx import AsyncClient
import pytest


async def _create_bus(
    client: AsyncClient,
    color: str = 'Red',
    seats_quantity: int = 50,
    number_plate: str = 'AB1234CD',
) -> dict:
    response = await client.post(
        '/buses',
        json={
            'color': color,
            'seats_quantity': seats_quantity,
            'number_plate': number_plate,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_bus(client: AsyncClient):
    response = await client.post(
        '/buses',
        json={
            'color': 'Blue',
            'seats_quantity': 40,
            'number_plate': 'XY5678ZT',
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data['color'] == 'Blue'
    assert data['seats_quantity'] == 40
    assert data['number_plate'] == 'XY5678ZT'
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data


@pytest.mark.asyncio
async def test_create_bus_validation_negative_seats(client: AsyncClient):
    response = await client.post(
        '/buses',
        json={
            'color': 'Green',
            'seats_quantity': -10,
            'number_plate': 'AB1111CD',
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_bus_validation_empty_color(client: AsyncClient):
    response = await client.post(
        '/buses',
        json={
            'color': '',
            'seats_quantity': 40,
            'number_plate': 'AB1111CD',
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_bus_duplicate_number_plate(client: AsyncClient):
    await _create_bus(client, number_plate='UNIQUE123')

    response = await client.post(
        '/buses',
        json={
            'color': 'Yellow',
            'seats_quantity': 30,
            'number_plate': 'UNIQUE123',
        },
    )
    assert response.status_code == 400
    assert 'number plate already exists' in response.json()['detail']


@pytest.mark.asyncio
async def test_get_buses_list(client: AsyncClient):
    created = await _create_bus(client)

    list_response = await client.get('/buses')
    assert list_response.status_code == 200
    assert any(bus['id'] == created['id'] for bus in list_response.json())


@pytest.mark.asyncio
async def test_get_bus_by_id(client: AsyncClient):
    created = await _create_bus(client)

    detail_response = await client.get(f'/buses/{created["id"]}')
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert data['id'] == created['id']
    assert data['color'] == created['color']
    assert data['seats_quantity'] == created['seats_quantity']
    assert data['number_plate'] == created['number_plate']


@pytest.mark.asyncio
async def test_get_bus_not_found(client: AsyncClient):
    fake_uuid = uuid4()
    response = await client.get(f'/buses/{fake_uuid}')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_bus(client: AsyncClient):
    created = await _create_bus(client)

    response = await client.put(
        f'/buses/{created["id"]}',
        json={'color': 'Updated Color', 'seats_quantity': 60},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['color'] == 'Updated Color'
    assert body['seats_quantity'] == 60
    assert body['number_plate'] == created['number_plate']


@pytest.mark.asyncio
async def test_update_bus_partial(client: AsyncClient):
    created = await _create_bus(client)

    response = await client.put(
        f'/buses/{created["id"]}',
        json={'color': 'Only Color Updated'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['color'] == 'Only Color Updated'
    assert body['seats_quantity'] == created['seats_quantity']
    assert body['number_plate'] == created['number_plate']


@pytest.mark.asyncio
async def test_update_bus_number_plate(client: AsyncClient):
    created = await _create_bus(client)

    response = await client.put(
        f'/buses/{created["id"]}',
        json={'number_plate': 'NEWPLATE1'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['number_plate'] == 'NEWPLATE1'


@pytest.mark.asyncio
async def test_update_bus_duplicate_number_plate(client: AsyncClient):
    await _create_bus(client, number_plate='FIRST123')
    second = await _create_bus(client, number_plate='SECOND456')

    response = await client.put(
        f'/buses/{second["id"]}',
        json={'number_plate': 'FIRST123'},
    )
    assert response.status_code == 400
    assert 'number plate already exists' in response.json()['detail']


@pytest.mark.asyncio
async def test_update_bus_not_found(client: AsyncClient):
    fake_uuid = uuid4()
    response = await client.put(
        f'/buses/{fake_uuid}',
        json={'color': 'New Color'},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_bus(client: AsyncClient):
    created = await _create_bus(client)

    response = await client.delete(f'/buses/{created["id"]}')
    assert response.status_code == 204

    get_response = await client.get(f'/buses/{created["id"]}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_bus_not_found(client: AsyncClient):
    fake_uuid = uuid4()
    response = await client.delete(f'/buses/{fake_uuid}')
    assert response.status_code == 404


# ===== Photo Upload Tests =====


@pytest.mark.asyncio
async def test_get_image_upload_url(client: AsyncClient):
    """Test generating presigned URL for image upload."""
    response = await client.post(
        '/buses/upload-url',
        json={
            'filename': 'test-image.jpg',
            'content_type': 'image/jpeg',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert 'upload_url' in data
    assert 'photo_key' in data
    assert 'fields' in data
    assert data['photo_key'] == 'test-image.jpg'
    # Verify presigned URL structure
    assert 'test-image.jpg' in data['upload_url'] or 'photos' in data['upload_url']


@pytest.mark.asyncio
async def test_get_image_upload_url_invalid_content_type(client: AsyncClient):
    """Test that invalid content types are rejected."""
    response = await client.post(
        '/buses/upload-url',
        json={
            'filename': 'test-image.pdf',
            'content_type': 'application/pdf',
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_image_upload_url_empty_filename(client: AsyncClient):
    """Test that empty filename is rejected."""
    response = await client.post(
        '/buses/upload-url',
        json={
            'filename': '',
            'content_type': 'image/jpeg',
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_confirm_image_upload(client: AsyncClient):
    """Test confirming image upload updates bus with photo URLs."""
    created = await _create_bus(client)

    response = await client.post(
        f'/buses/{created["id"]}/image/confirm',
        json={'photo_key': 'uploaded-image.jpg'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['photo_url'] is not None
    assert data['thumbnail_url'] is not None
    assert 'uploaded-image.jpg' in data['photo_url']
    assert 'uploaded-image.jpg' in data['thumbnail_url']


@pytest.mark.asyncio
async def test_confirm_image_upload_bus_not_found(client: AsyncClient):
    """Test confirming image upload for non-existent bus."""
    fake_uuid = uuid4()

    response = await client.post(
        f'/buses/{fake_uuid}/image/confirm',
        json={'photo_key': 'test-image.jpg'},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_image(client: AsyncClient):
    """Test deleting bus image."""
    created = await _create_bus(client)

    # First, add an image
    await client.post(
        f'/buses/{created["id"]}/image/confirm',
        json={'photo_key': 'test-image.jpg'},
    )

    # Now delete the image
    response = await client.delete(f'/buses/{created["id"]}/image')

    assert response.status_code == 204

    # Verify image is removed
    bus_response = await client.get(f'/buses/{created["id"]}')
    assert bus_response.status_code == 200
    bus_data = bus_response.json()
    assert bus_data['photo_url'] is None


@pytest.mark.asyncio
async def test_delete_image_bus_not_found(client: AsyncClient):
    """Test deleting image for non-existent bus."""
    fake_uuid = uuid4()

    response = await client.delete(f'/buses/{fake_uuid}/image')

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_bus_with_images(client: AsyncClient):
    """Test that deleting a bus also removes its images from S3."""
    created = await _create_bus(client)

    # Add image to bus
    await client.post(
        f'/buses/{created["id"]}/image/confirm',
        json={'photo_key': 'test-image.jpg'},
    )

    # Delete bus (this should also delete the images from S3)
    response = await client.delete(f'/buses/{created["id"]}')
    assert response.status_code == 204

    # Verify bus is deleted
    get_response = await client.get(f'/buses/{created["id"]}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_full_image_upload_workflow(client: AsyncClient, s3_service):
    """Test complete workflow: generate presigned URL, upload file to S3, and confirm."""
    created = await _create_bus(client)

    # Step 1: Get presigned URL
    presigned_response = await client.post(
        '/buses/upload-url',
        json={
            'filename': 'bus-photo.jpg',
            'content_type': 'image/jpeg',
        },
    )
    assert presigned_response.status_code == 200
    presigned_data = presigned_response.json()
    photo_key = presigned_data['photo_key']

    # Step 2: Upload file directly to S3 using s3_service's client
    test_image_content = b'fake JPEG image content for testing'
    s3_service._s3_client.put_object(
        Bucket='photos',
        Key=photo_key,
        Body=test_image_content,
        ContentType='image/jpeg',
    )

    # Step 3: Confirm upload
    confirm_response = await client.post(
        f'/buses/{created["id"]}/image/confirm',
        json={'photo_key': photo_key},
    )
    assert confirm_response.status_code == 200

    # Step 4: Verify URLs are set
    bus_data = confirm_response.json()
    assert bus_data['photo_url'] is not None
    assert bus_data['thumbnail_url'] is not None
    assert photo_key in bus_data['photo_url']
    assert photo_key in bus_data['thumbnail_url']

    # Step 5: Verify we can get the bus and URLs persist
    get_response = await client.get(f'/buses/{created["id"]}')
    assert get_response.status_code == 200
    bus = get_response.json()
    assert bus['photo_url'] == bus_data['photo_url']
    assert bus['thumbnail_url'] == bus_data['thumbnail_url']
