from uuid import uuid4

from pydantic import ValidationError
import pytest

from app.features.stop.schemas import StopCreate, StopRead, StopUpdate


class TestStopCreate:
    """Tests for StopCreate schema."""

    def test_stop_create_valid(self):
        """Test creating a valid StopCreate object."""
        city_id = uuid4()
        stop = StopCreate(
            city_id=city_id,
            name='Central Station',
            latitude=50.45,
            longitude=30.5,
        )
        assert stop.city_id == city_id
        assert stop.name == 'Central Station'
        assert stop.latitude == 50.45
        assert stop.longitude == 30.5

    def test_stop_create_missing_required_fields(self):
        """Test StopCreate fails without required fields."""
        with pytest.raises(ValidationError):
            StopCreate()

    def test_stop_create_missing_city_id(self):
        """Test StopCreate fails without city_id."""
        with pytest.raises(ValidationError):
            StopCreate(
                name='Test Stop',
                latitude=50.45,
                longitude=30.5,
            )

    def test_stop_create_missing_name(self):
        """Test StopCreate fails without name."""
        with pytest.raises(ValidationError):
            StopCreate(
                city_id=uuid4(),
                latitude=50.45,
                longitude=30.5,
            )

    def test_stop_create_empty_name(self):
        """Test StopCreate fails with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            StopCreate(
                city_id=uuid4(),
                name='',
                latitude=50.45,
                longitude=30.5,
            )
        assert 'name' in str(exc_info.value)

    def test_stop_create_name_too_long(self):
        """Test StopCreate fails with name exceeding max length."""
        with pytest.raises(ValidationError) as exc_info:
            StopCreate(
                city_id=uuid4(),
                name='A' * 256,  # Max is 255
                latitude=50.45,
                longitude=30.5,
            )
        assert 'name' in str(exc_info.value)

    def test_stop_create_invalid_latitude_high(self):
        """Test StopCreate fails with latitude > 90."""
        with pytest.raises(ValidationError) as exc_info:
            StopCreate(
                city_id=uuid4(),
                name='Test Stop',
                latitude=91.0,
                longitude=30.5,
            )
        assert 'latitude' in str(exc_info.value)

    def test_stop_create_invalid_latitude_low(self):
        """Test StopCreate fails with latitude < -90."""
        with pytest.raises(ValidationError) as exc_info:
            StopCreate(
                city_id=uuid4(),
                name='Test Stop',
                latitude=-91.0,
                longitude=30.5,
            )
        assert 'latitude' in str(exc_info.value)

    def test_stop_create_invalid_longitude_high(self):
        """Test StopCreate fails with longitude > 180."""
        with pytest.raises(ValidationError) as exc_info:
            StopCreate(
                city_id=uuid4(),
                name='Test Stop',
                latitude=50.45,
                longitude=181.0,
            )
        assert 'longitude' in str(exc_info.value)

    def test_stop_create_invalid_longitude_low(self):
        """Test StopCreate fails with longitude < -180."""
        with pytest.raises(ValidationError) as exc_info:
            StopCreate(
                city_id=uuid4(),
                name='Test Stop',
                latitude=50.45,
                longitude=-181.0,
            )
        assert 'longitude' in str(exc_info.value)

    def test_stop_create_boundary_coordinates(self):
        """Test StopCreate with boundary coordinate values."""
        stop = StopCreate(
            city_id=uuid4(),
            name='Boundary Stop',
            latitude=90.0,
            longitude=180.0,
        )
        assert stop.latitude == 90.0
        assert stop.longitude == 180.0

        stop2 = StopCreate(
            city_id=uuid4(),
            name='Boundary Stop 2',
            latitude=-90.0,
            longitude=-180.0,
        )
        assert stop2.latitude == -90.0
        assert stop2.longitude == -180.0

    def test_stop_create_invalid_city_id_format(self):
        """Test StopCreate fails with invalid city_id format."""
        with pytest.raises(ValidationError):
            StopCreate(
                city_id='not-a-uuid',
                name='Test Stop',
                latitude=50.45,
                longitude=30.5,
            )


class TestStopUpdate:
    """Tests for StopUpdate schema."""

    def test_stop_update_all_fields(self):
        """Test updating all fields."""
        city_id = uuid4()
        update = StopUpdate(
            city_id=city_id,
            name='Updated Stop',
            latitude=51.5,
            longitude=31.0,
        )
        assert update.city_id == city_id
        assert update.name == 'Updated Stop'
        assert update.latitude == 51.5
        assert update.longitude == 31.0

    def test_stop_update_partial_name_only(self):
        """Test updating only name."""
        update = StopUpdate(name='New Name')
        assert update.name == 'New Name'
        assert update.city_id is None
        assert update.latitude is None
        assert update.longitude is None

    def test_stop_update_partial_coordinates_only(self):
        """Test updating only coordinates."""
        update = StopUpdate(latitude=50.0, longitude=25.0)
        assert update.latitude == 50.0
        assert update.longitude == 25.0
        assert update.name is None
        assert update.city_id is None

    def test_stop_update_no_fields(self):
        """Test StopUpdate with no fields."""
        update = StopUpdate()
        assert update.city_id is None
        assert update.name is None
        assert update.latitude is None
        assert update.longitude is None

    def test_stop_update_empty_name_fails(self):
        """Test StopUpdate fails with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            StopUpdate(name='')
        assert 'name' in str(exc_info.value)

    def test_stop_update_invalid_latitude(self):
        """Test StopUpdate fails with invalid latitude."""
        with pytest.raises(ValidationError):
            StopUpdate(latitude=100.0)

    def test_stop_update_invalid_longitude(self):
        """Test StopUpdate fails with invalid longitude."""
        with pytest.raises(ValidationError):
            StopUpdate(longitude=200.0)

    def test_stop_update_invalid_city_id_format(self):
        """Test StopUpdate fails with invalid city_id format."""
        with pytest.raises(ValidationError):
            StopUpdate(city_id='invalid-uuid')


class TestStopRead:
    """Tests for StopRead schema."""

    def test_stop_read_valid(self):
        """Test creating a valid StopRead object."""
        from datetime import datetime

        stop_id = uuid4()
        city_id = uuid4()
        now = datetime.now()

        stop = StopRead(
            id=stop_id,
            city_id=city_id,
            name='Main Station',
            latitude=50.45,
            longitude=30.5,
            created_at=now,
            updated_at=now,
        )
        assert stop.id == stop_id
        assert stop.city_id == city_id
        assert stop.name == 'Main Station'
        assert stop.latitude == 50.45
        assert stop.longitude == 30.5
        assert stop.created_at == now
        assert stop.updated_at == now

    def test_stop_read_missing_required_fields(self):
        """Test StopRead fails without required fields."""
        with pytest.raises(ValidationError):
            StopRead(
                id=uuid4(),
                city_id=uuid4(),
            )

    def test_stop_read_invalid_id_format(self):
        """Test StopRead fails with invalid id format."""
        from datetime import datetime

        with pytest.raises(ValidationError):
            StopRead(
                id='not-a-uuid',
                city_id=uuid4(),
                name='Test',
                latitude=50.0,
                longitude=30.0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

    def test_stop_read_inherits_validation(self):
        """Test StopRead inherits validation from StopBase."""
        from datetime import datetime

        # Should fail with invalid coordinates
        with pytest.raises(ValidationError):
            StopRead(
                id=uuid4(),
                city_id=uuid4(),
                name='Test',
                latitude=200.0,  # Invalid
                longitude=30.0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
