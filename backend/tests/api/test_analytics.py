from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.order.enums import OrderStatus
from app.features.order.models import Order
from app.features.seat.models import Seat
from app.features.ticket.models import Ticket
from app.features.user.models import User
from tests.api.test_order import create_test_bus, create_test_city, create_test_stop, create_test_trip
from tests.conftest import TEST_USER_ID
from tests.factories import TripStopCreateFactory


async def _create_paid_order(session: AsyncSession, total_price: Decimal = Decimal('100.00')) -> Order:
    result = await session.execute(
        insert(Order)
        .values(
            user_id=UUID(TEST_USER_ID),
            status=OrderStatus.PAID,
            total_price=total_price,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        .returning(Order)
    )
    return result.scalar_one()


async def _create_order_with_status(
    session: AsyncSession,
    status: OrderStatus,
    total_price: Decimal = Decimal('50.00'),
) -> Order:
    result = await session.execute(
        insert(Order)
        .values(
            user_id=UUID(TEST_USER_ID),
            status=status,
            total_price=total_price,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        .returning(Order)
    )
    return result.scalar_one()


async def _create_trip_with_tickets(session: AsyncSession, paid_order: Order, ticket_count: int = 2):
    bus = await create_test_bus(session)
    city = await create_test_city(session)
    stop1 = await create_test_stop(session, city.id)
    stop2 = await create_test_stop(session, city.id)

    trip_stop1 = TripStopCreateFactory.build(stop_id=stop1.id, position_index=1, hours_offset=0)
    trip_stop2 = TripStopCreateFactory.build(stop_id=stop2.id, position_index=2, hours_offset=2)

    trip = await create_test_trip(session, bus.id, [trip_stop1, trip_stop2])

    # Fetch seats from DB since TripRead doesn't include them
    seats_result = await session.execute(select(Seat).where(Seat.trip_id == trip.id))
    seats = list(seats_result.scalars().all())

    for i in range(ticket_count):
        await session.execute(
            insert(Ticket).values(
                order_id=paid_order.id,
                seat_id=seats[i].id,
                trip_id=trip.id,
                start_stop_id=stop1.id,
                finish_stop_id=stop2.id,
                passenger_name=f'Passenger {i + 1}',
                price=Decimal('50.00'),
            )
        )

    await session.flush()
    return trip


class TestRevenueAnalytics:
    async def test_empty_db(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/analytics/revenue')
        assert response.status_code == 200

        data = response.json()
        assert data['summary']['total_revenue'] == '0'
        assert data['summary']['today_revenue'] == '0'
        assert data['summary']['week_revenue'] == '0'
        assert data['summary']['month_revenue'] == '0'
        assert data['time_series'] == []

    async def test_with_paid_orders(self, session: AsyncSession, client: AsyncClient):
        await _create_paid_order(session, Decimal('100.00'))
        await _create_paid_order(session, Decimal('200.00'))
        # Non-paid order should not count
        await _create_order_with_status(session, OrderStatus.PENDING, Decimal('50.00'))
        await session.flush()

        response = await client.get('/analytics/revenue')
        assert response.status_code == 200

        data = response.json()
        assert Decimal(data['summary']['total_revenue']) == Decimal('300.00')
        assert Decimal(data['summary']['today_revenue']) == Decimal('300.00')
        assert len(data['time_series']) >= 1

    async def test_with_period_param(self, session: AsyncSession, client: AsyncClient):
        await _create_paid_order(session, Decimal('100.00'))
        await session.flush()

        response = await client.get('/analytics/revenue', params={'period': 'month'})
        assert response.status_code == 200

        data = response.json()
        assert Decimal(data['summary']['total_revenue']) >= Decimal('100.00')
        if data['time_series']:
            # Month format: "2025-01"
            assert '-' in data['time_series'][0]['date']


class TestBookingsAnalytics:
    async def test_empty_db(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/analytics/bookings')
        assert response.status_code == 200

        data = response.json()
        assert data['summary']['total_orders'] == 0
        assert data['summary']['paid_count'] == 0
        assert data['summary']['cancelled_count'] == 0
        assert data['summary']['failed_count'] == 0
        assert data['summary']['pending_count'] == 0
        assert Decimal(data['summary']['conversion_rate']) == Decimal('0')
        assert data['time_series'] == []

    async def test_with_orders(self, session: AsyncSession, client: AsyncClient):
        await _create_order_with_status(session, OrderStatus.PAID, Decimal('100.00'))
        await _create_order_with_status(session, OrderStatus.PAID, Decimal('200.00'))
        await _create_order_with_status(session, OrderStatus.CANCELLED, Decimal('50.00'))
        await _create_order_with_status(session, OrderStatus.FAILED, Decimal('75.00'))
        await _create_order_with_status(session, OrderStatus.PENDING, Decimal('60.00'))
        await session.flush()

        response = await client.get('/analytics/bookings')
        assert response.status_code == 200

        data = response.json()
        summary = data['summary']
        assert summary['total_orders'] == 5
        assert summary['paid_count'] == 2
        assert summary['cancelled_count'] == 1
        assert summary['failed_count'] == 1
        assert summary['pending_count'] == 1
        assert Decimal(summary['conversion_rate']) == Decimal('40.0')

        # Time series has per-status breakdown
        assert len(data['time_series']) >= 1
        point = data['time_series'][0]
        assert 'paid' in point
        assert 'cancelled' in point
        assert 'failed' in point
        assert 'pending' in point
        assert point['paid'] == 2
        assert point['cancelled'] == 1
        assert point['failed'] == 1
        assert point['pending'] == 1


class TestTripsAnalytics:
    async def test_empty_db(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/analytics/trips')
        assert response.status_code == 200

        data = response.json()
        assert data['summary']['total_trips'] == 0
        assert data['summary']['total_tickets_sold'] == 0
        assert Decimal(data['summary']['average_occupancy']) == Decimal('0')
        assert data['time_series'] == []

    async def test_with_trips_and_tickets(self, session: AsyncSession, client: AsyncClient):
        paid_order = await _create_paid_order(session, Decimal('100.00'))
        await session.flush()

        await _create_trip_with_tickets(session, paid_order, ticket_count=2)

        response = await client.get('/analytics/trips')
        assert response.status_code == 200

        data = response.json()
        assert data['summary']['total_trips'] >= 1
        assert data['summary']['total_tickets_sold'] >= 2
        assert Decimal(data['summary']['average_occupancy']) > Decimal('0')
        assert len(data['time_series']) >= 1


class TestUsersAnalytics:
    async def test_with_default_user(self, session: AsyncSession, client: AsyncClient):
        """Test user analytics — conftest creates one test user."""
        response = await client.get('/analytics/users')
        assert response.status_code == 200

        data = response.json()
        # At least the test user from conftest
        assert data['summary']['total_users'] >= 1
        assert data['summary']['active_users'] >= 1
        assert data['summary']['new_today'] >= 1
        assert data['summary']['new_this_week'] >= 1
        assert data['summary']['new_this_month'] >= 1
        assert len(data['time_series']) >= 1

    async def test_with_additional_users(self, session: AsyncSession, client: AsyncClient):
        import uuid

        await session.execute(
            insert(User).values(
                id=uuid.uuid4(),
                email=f'analytics_test_{uuid.uuid4().hex[:8]}@test.com',
                name='Analytics Test User',
                is_active=True,
            )
        )
        await session.flush()

        response = await client.get('/analytics/users')
        assert response.status_code == 200

        data = response.json()
        assert data['summary']['total_users'] >= 2
        assert len(data['time_series']) >= 1

    async def test_with_period_week(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/analytics/users', params={'period': 'week'})
        assert response.status_code == 200

        data = response.json()
        assert data['summary']['total_users'] >= 1
        if data['time_series']:
            # Week format: "2025-W03"
            assert '-W' in data['time_series'][0]['date']
