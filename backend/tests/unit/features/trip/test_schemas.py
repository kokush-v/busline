from datetime import datetime
from uuid import uuid4

from pydantic import ValidationError
import pytest

from app.features.trip.schemas import TripCreate, TripRead, TripReadPublic, TripUpdate


class TestTripCreate:
    """Tests for TripCreate schema."""

    def test_trip_create_valid(self):
        """Test creating a valid TripCreate object."""
        bus_id = uuid4()
        trip = TripCreate(bus_id=bus_id)
        assert trip.bus_id == bus_id

    def test_trip_create_missing_bus_id(self):
        """Test TripCreate fails without bus_id."""
        with pytest.raises(ValidationError):
            TripCreate()

    def test_trip_create_invalid_bus_id_format(self):
        """Test TripCreate fails with invalid bus_id format."""
        with pytest.raises(ValidationError):
            TripCreate(bus_id='not-a-uuid')


class TestTripUpdate:
    """Tests for TripUpdate schema."""

    def test_trip_update_with_bus_id(self):
        """Test updating trip with bus_id."""
        bus_id = uuid4()
        update = TripUpdate(bus_id=bus_id)
        assert update.bus_id == bus_id

    def test_trip_update_without_bus_id(self):
        """Test TripUpdate with None bus_id."""
        update = TripUpdate()
        assert update.bus_id is None

    def test_trip_update_explicit_none(self):
        """Test TripUpdate with explicit None."""
        update = TripUpdate(bus_id=None)
        assert update.bus_id is None

    def test_trip_update_invalid_bus_id_format(self):
        """Test TripUpdate fails with invalid bus_id format."""
        with pytest.raises(ValidationError):
            TripUpdate(bus_id='invalid-uuid')


class TestTripRead:
    """Tests for TripRead schema."""

    def test_trip_read_valid(self):
        """Test creating a valid TripRead object."""
        trip_id = uuid4()
        bus_id = uuid4()
        trip = TripRead(
            id=trip_id,
            bus_id=bus_id,
            seats_left=30,
            trip_stops=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert trip.id == trip_id
        assert trip.bus_id == bus_id
        assert trip.seats_left == 30
        assert trip.trip_stops == []

    def test_trip_read_missing_required_field(self):
        """Test TripRead fails without required fields."""
        with pytest.raises(ValidationError):
            TripRead(
                id=uuid4(),
                bus_id=uuid4(),
                seats_left=30,
            )

    def test_trip_read_negative_seats(self):
        """Test TripRead with negative seats_left."""
        trip = TripRead(
            id=uuid4(),
            bus_id=uuid4(),
            seats_left=-5,
            trip_stops=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert trip.seats_left == -5

    def test_trip_read_zero_seats(self):
        """Test TripRead with zero seats_left."""
        trip = TripRead(
            id=uuid4(),
            bus_id=uuid4(),
            seats_left=0,
            trip_stops=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert trip.seats_left == 0


class TestTripReadPublic:
    """Tests for TripReadPublic schema."""

    def test_trip_read_public_valid(self):
        """Test creating a valid TripReadPublic object."""
        trip_id = uuid4()
        bus_id = uuid4()
        created_at = datetime.now()
        trip = TripReadPublic(
            id=trip_id,
            bus_id=bus_id,
            seats_left=50,
            trip_stops=[],
            created_at=created_at,
        )
        assert trip.id == trip_id
        assert trip.bus_id == bus_id
        assert trip.seats_left == 50
        assert trip.trip_stops == []
        assert trip.created_at == created_at

    def test_trip_read_public_has_created_at(self):
        """Test TripReadPublic includes created_at field."""
        trip = TripReadPublic(
            id=uuid4(),
            bus_id=uuid4(),
            seats_left=40,
            trip_stops=[],
            created_at=datetime.now(),
        )
        assert hasattr(trip, 'created_at')
        assert isinstance(trip.created_at, datetime)

    def test_trip_read_public_missing_created_at(self):
        """Test TripReadPublic fails without created_at."""
        with pytest.raises(ValidationError):
            TripReadPublic(
                id=uuid4(),
                bus_id=uuid4(),
                seats_left=40,
                trip_stops=[],
            )

    def test_trip_read_public_no_updated_at_field(self):
        """Test TripReadPublic does not include updated_at."""
        trip = TripReadPublic(
            id=uuid4(),
            bus_id=uuid4(),
            seats_left=40,
            trip_stops=[],
            created_at=datetime.now(),
        )
        assert not hasattr(trip, 'updated_at')

    def test_trip_read_public_invalid_id_format(self):
        """Test TripReadPublic fails with invalid id format."""
        with pytest.raises(ValidationError):
            TripReadPublic(
                id='not-a-uuid',
                bus_id=uuid4(),
                seats_left=40,
                trip_stops=[],
                created_at=datetime.now(),
            )
