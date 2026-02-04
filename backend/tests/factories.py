from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from app.features.bus.schemas import BusCreate
from app.features.city.schemas import CityCreate
from app.features.stop.schemas import StopCreate
from app.features.ticket.schemas import ReserveTicketRequest
from app.features.trip_stop.schemas import TripStopCreate


class CityCreateFactory(ModelFactory[CityCreate]):
    __model__ = CityCreate

    name = Use(lambda: f'City-{ModelFactory.__random__.randint(1000, 9999)}')
    latitude = Use(lambda: ModelFactory.__random__.uniform(-90, 90))
    longitude = Use(lambda: ModelFactory.__random__.uniform(-180, 180))


class BusCreateFactory(ModelFactory[BusCreate]):
    __model__ = BusCreate

    color = Use(lambda: ModelFactory.__random__.choice(['Red', 'Blue', 'Green', 'Yellow', 'White']))
    seats_quantity = Use(lambda: ModelFactory.__random__.randint(20, 60))
    number_plate = Use(lambda: f'AA{ModelFactory.__random__.randint(1000, 9999)}BB')


class StopCreateFactory(ModelFactory[StopCreate]):
    __model__ = StopCreate

    name = Use(lambda: f'Stop-{ModelFactory.__random__.randint(1000, 9999)}')
    latitude = Use(lambda: ModelFactory.__random__.uniform(-90, 90))
    longitude = Use(lambda: ModelFactory.__random__.uniform(-180, 180))

    @classmethod
    def build(cls, city_id: UUID, **kwargs) -> StopCreate:
        return super().build(city_id=city_id, **kwargs)


class TripStopCreateFactory(ModelFactory[TripStopCreate]):
    __model__ = TripStopCreate

    position_index = Use(lambda: 1)

    @classmethod
    def build(cls, stop_id: UUID, position_index: int = 1, hours_offset: int = 0, **kwargs) -> TripStopCreate:
        base_time = datetime.now(UTC) + timedelta(days=1, hours=hours_offset)
        return super().build(
            stop_id=stop_id,
            position_index=position_index,
            arrival_time=base_time,
            departure_time=base_time + timedelta(minutes=15),
            **kwargs,
        )


class ReserveTicketRequestFactory(ModelFactory[ReserveTicketRequest]):
    __model__ = ReserveTicketRequest

    passenger_name = Use(lambda: f'Passenger-{ModelFactory.__random__.randint(100, 999)}')
    passenger_email = Use(lambda: f'passenger{ModelFactory.__random__.randint(100, 999)}@test.com')
    passenger_age = Use(lambda: ModelFactory.__random__.randint(18, 65))
    price = Use(lambda: Decimal('50.00'))

    @classmethod
    def build(cls, seat_id: UUID, start_stop_id: UUID, finish_stop_id: UUID, **kwargs) -> ReserveTicketRequest:
        return super().build(
            seat_id=seat_id,
            start_stop_id=start_stop_id,
            finish_stop_id=finish_stop_id,
            **kwargs,
        )
