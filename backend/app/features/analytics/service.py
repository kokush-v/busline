from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.analytics.enums import AnalyticsPeriod
from app.features.analytics.schemas import (
    AnalyticsQueryParams,
    BookingsResponse,
    BookingsSummary,
    BookingsTimeSeriesPoint,
    RevenueResponse,
    RevenueSummary,
    TimeSeriesPoint,
    TripsResponse,
    TripsSummary,
    UsersResponse,
    UsersSummary,
)
from app.features.order.enums import OrderStatus
from app.features.order.models import Order
from app.features.seat.models import Seat
from app.features.ticket.models import Ticket
from app.features.trip.models import Trip
from app.features.user.models import User


class AnalyticsService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self._session = session

    def _resolve_dates(self, params: AnalyticsQueryParams) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)
        date_to = params.date_to or now
        date_from = params.date_from or (now - timedelta(days=30))
        return date_from, date_to

    def _format_date(self, dt: datetime, period: AnalyticsPeriod) -> str:
        if period == AnalyticsPeriod.DAY:
            return dt.strftime('%Y-%m-%d')
        elif period == AnalyticsPeriod.WEEK:
            iso_year, iso_week, _ = dt.isocalendar()
            return f'{iso_year}-W{iso_week:02d}'
        else:
            return dt.strftime('%Y-%m')

    async def get_revenue(self, params: AnalyticsQueryParams) -> RevenueResponse:
        date_from, date_to = self._resolve_dates(params)
        now = datetime.now(UTC)

        # Summary
        summary_stmt = select(
            func.coalesce(func.sum(Order.total_price), 0).label('total_revenue'),
            func.coalesce(
                func.sum(
                    case(
                        (func.date_trunc('day', Order.created_at) == func.date_trunc('day', now), Order.total_price),
                        else_=0,
                    )
                ),
                0,
            ).label('today_revenue'),
            func.coalesce(
                func.sum(case((Order.created_at >= now - timedelta(days=7), Order.total_price), else_=0)),
                0,
            ).label('week_revenue'),
            func.coalesce(
                func.sum(case((Order.created_at >= now - timedelta(days=30), Order.total_price), else_=0)),
                0,
            ).label('month_revenue'),
        ).where(Order.status == OrderStatus.PAID)

        result = await self._session.execute(summary_stmt)
        row = result.one()

        summary = RevenueSummary(
            total_revenue=row.total_revenue,
            today_revenue=row.today_revenue,
            week_revenue=row.week_revenue,
            month_revenue=row.month_revenue,
        )

        # Time series
        ts_stmt = (
            select(
                func.date_trunc(params.period.value, Order.created_at).label('period'),
                func.sum(Order.total_price).label('value'),
            )
            .where(Order.status == OrderStatus.PAID, Order.created_at >= date_from, Order.created_at <= date_to)
            .group_by('period')
            .order_by('period')
        )
        ts_result = await self._session.execute(ts_stmt)
        time_series = [
            TimeSeriesPoint(date=self._format_date(row.period, params.period), value=row.value)
            for row in ts_result.all()
        ]

        return RevenueResponse(summary=summary, time_series=time_series)

    async def get_bookings(self, params: AnalyticsQueryParams) -> BookingsResponse:
        date_from, date_to = self._resolve_dates(params)

        # Summary
        summary_stmt = select(
            func.count().label('total_orders'),
            func.count().filter(Order.status == OrderStatus.PAID).label('paid_count'),
            func.count().filter(Order.status == OrderStatus.CANCELLED).label('cancelled_count'),
            func.count().filter(Order.status == OrderStatus.FAILED).label('failed_count'),
            func.count().filter(Order.status == OrderStatus.PENDING).label('pending_count'),
        ).select_from(Order)

        result = await self._session.execute(summary_stmt)
        row = result.one()

        total = row.total_orders
        paid = row.paid_count
        conversion_rate = Decimal(str(round(paid / total * 100, 2))) if total > 0 else Decimal('0')

        summary = BookingsSummary(
            total_orders=total,
            paid_count=paid,
            cancelled_count=row.cancelled_count,
            failed_count=row.failed_count,
            pending_count=row.pending_count,
            conversion_rate=conversion_rate,
        )

        # Time series — orders per status per period
        ts_stmt = (
            select(
                func.date_trunc(params.period.value, Order.created_at).label('period'),
                func.count().filter(Order.status == OrderStatus.PAID).label('paid'),
                func.count().filter(Order.status == OrderStatus.CANCELLED).label('cancelled'),
                func.count().filter(Order.status == OrderStatus.FAILED).label('failed'),
                func.count().filter(Order.status == OrderStatus.PENDING).label('pending'),
            )
            .where(Order.created_at >= date_from, Order.created_at <= date_to)
            .group_by('period')
            .order_by('period')
        )
        ts_result = await self._session.execute(ts_stmt)
        time_series = [
            BookingsTimeSeriesPoint(
                date=self._format_date(row.period, params.period),
                paid=row.paid,
                cancelled=row.cancelled,
                failed=row.failed,
                pending=row.pending,
            )
            for row in ts_result.all()
        ]

        return BookingsResponse(summary=summary, time_series=time_series)

    async def get_trips(self, params: AnalyticsQueryParams) -> TripsResponse:
        date_from, date_to = self._resolve_dates(params)

        # Total trips
        total_trips_result = await self._session.execute(select(func.count()).select_from(Trip))
        total_trips = total_trips_result.scalar_one()

        # Total tickets sold (via paid orders)
        tickets_sold_result = await self._session.execute(
            select(func.count())
            .select_from(Ticket)
            .join(Order, Ticket.order_id == Order.id)
            .where(Order.status == OrderStatus.PAID)
        )
        total_tickets_sold = tickets_sold_result.scalar_one()

        # Average occupancy: total_tickets_sold / total_seats * 100
        total_seats_result = await self._session.execute(select(func.count()).select_from(Seat))
        total_seats = total_seats_result.scalar_one()
        average_occupancy = (
            Decimal(str(round(total_tickets_sold / total_seats * 100, 2))) if total_seats > 0 else Decimal('0')
        )

        summary = TripsSummary(
            total_trips=total_trips,
            average_occupancy=average_occupancy,
            total_tickets_sold=total_tickets_sold,
        )

        # Time series — tickets sold per period
        ts_stmt = (
            select(
                func.date_trunc(params.period.value, Ticket.created_at).label('period'),
                func.count().label('value'),
            )
            .join(Order, Ticket.order_id == Order.id)
            .where(Order.status == OrderStatus.PAID, Ticket.created_at >= date_from, Ticket.created_at <= date_to)
            .group_by('period')
            .order_by('period')
        )
        ts_result = await self._session.execute(ts_stmt)
        time_series = [
            TimeSeriesPoint(date=self._format_date(row.period, params.period), value=row.value)
            for row in ts_result.all()
        ]

        return TripsResponse(summary=summary, time_series=time_series)

    async def get_users(self, params: AnalyticsQueryParams) -> UsersResponse:
        date_from, date_to = self._resolve_dates(params)
        now = datetime.now(UTC)

        # Summary
        summary_stmt = select(
            func.count().label('total_users'),
            func.count().filter(User.is_active.is_(True)).label('active_users'),
            func.count()
            .filter(func.date_trunc('day', User.created_at) == func.date_trunc('day', now))
            .label('new_today'),
            func.count().filter(User.created_at >= now - timedelta(days=7)).label('new_this_week'),
            func.count().filter(User.created_at >= now - timedelta(days=30)).label('new_this_month'),
        ).select_from(User)

        result = await self._session.execute(summary_stmt)
        row = result.one()

        summary = UsersSummary(
            total_users=row.total_users,
            active_users=row.active_users,
            new_today=row.new_today,
            new_this_week=row.new_this_week,
            new_this_month=row.new_this_month,
        )

        # Time series — new registrations per period
        ts_stmt = (
            select(
                func.date_trunc(params.period.value, User.created_at).label('period'),
                func.count().label('value'),
            )
            .where(User.created_at >= date_from, User.created_at <= date_to)
            .group_by('period')
            .order_by('period')
        )
        ts_result = await self._session.execute(ts_stmt)
        time_series = [
            TimeSeriesPoint(date=self._format_date(row.period, params.period), value=row.value)
            for row in ts_result.all()
        ]

        return UsersResponse(summary=summary, time_series=time_series)
