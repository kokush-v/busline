from pydantic import ValidationError
import pytest

from app.features.bus.schemas import (
    BusCreate,
    BusUpdate,
    PhotoUploadComplete,
    PresignedUrlRequest,
)


def test_bus_create_valid():
    payload = BusCreate(
        color='Red',
        seats_quantity=50,
        number_plate='AB1234CD',
    )
    assert payload.color == 'Red'
    assert payload.seats_quantity == 50
    assert payload.number_plate == 'AB1234CD'


def test_bus_create_invalid_seats_negative():
    with pytest.raises(ValidationError):
        BusCreate(
            color='Blue',
            seats_quantity=-10,
            number_plate='AB1234CD',
        )


def test_bus_create_invalid_empty_color():
    with pytest.raises(ValidationError):
        BusCreate(
            color='',
            seats_quantity=40,
            number_plate='AB1234CD',
        )


def test_bus_create_invalid_empty_number_plate():
    with pytest.raises(ValidationError):
        BusCreate(
            color='Green',
            seats_quantity=40,
            number_plate='',
        )


def test_bus_create_invalid_color_too_long():
    with pytest.raises(ValidationError):
        BusCreate(
            color='A' * 51,  # More than 50 characters
            seats_quantity=40,
            number_plate='AB1234CD',
        )


def test_bus_create_invalid_number_plate_too_long():
    with pytest.raises(ValidationError):
        BusCreate(
            color='Red',
            seats_quantity=40,
            number_plate='A' * 21,  # More than 20 characters
        )


def test_bus_update_partial_valid():
    payload = BusUpdate(color='Yellow')
    assert payload.color == 'Yellow'
    assert payload.seats_quantity is None
    assert payload.number_plate is None


def test_bus_update_all_fields():
    payload = BusUpdate(
        color='White',
        seats_quantity=60,
        number_plate='XY9876ZT',
    )
    assert payload.color == 'White'
    assert payload.seats_quantity == 60
    assert payload.number_plate == 'XY9876ZT'


def test_bus_update_invalid_seats_negative():
    with pytest.raises(ValidationError):
        BusUpdate(seats_quantity=-5)


def test_bus_update_invalid_empty_color():
    with pytest.raises(ValidationError):
        BusUpdate(color='')


def test_bus_update_invalid_empty_number_plate():
    with pytest.raises(ValidationError):
        BusUpdate(number_plate='')


# ===== Photo Upload Schema Tests =====


def test_presigned_url_request_valid_jpeg():
    payload = PresignedUrlRequest(
        filename='test-photo.jpg',
        content_type='image/jpeg',
    )
    assert payload.filename == 'test-photo.jpg'
    assert payload.content_type == 'image/jpeg'


def test_presigned_url_request_valid_png():
    payload = PresignedUrlRequest(
        filename='test-photo.png',
        content_type='image/png',
    )
    assert payload.filename == 'test-photo.png'
    assert payload.content_type == 'image/png'


def test_presigned_url_request_invalid_content_type():
    with pytest.raises(ValidationError):
        PresignedUrlRequest(
            filename='test-photo.pdf',
            content_type='application/pdf',
        )


def test_presigned_url_request_invalid_content_type_gif():
    with pytest.raises(ValidationError):
        PresignedUrlRequest(
            filename='test-photo.gif',
            content_type='image/gif',
        )


def test_presigned_url_request_empty_filename():
    with pytest.raises(ValidationError):
        PresignedUrlRequest(
            filename='',
            content_type='image/jpeg',
        )


def test_presigned_url_request_filename_too_long():
    with pytest.raises(ValidationError):
        PresignedUrlRequest(
            filename='a' * 256,  # Більше 255 символів
            content_type='image/jpeg',
        )


def test_photo_upload_complete_valid():
    payload = PhotoUploadComplete(photo_key='uploaded-photo.jpg')
    assert payload.photo_key == 'uploaded-photo.jpg'


def test_photo_upload_complete_with_path():
    payload = PhotoUploadComplete(photo_key='buses/photos/12345.jpg')
    assert payload.photo_key == 'buses/photos/12345.jpg'
