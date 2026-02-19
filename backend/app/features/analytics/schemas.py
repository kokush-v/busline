from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.features.analytics.enums import AnalyticsPeriod


class AnalyticsQueryParams(BaseModel):
    period: AnalyticsPeriod = AnalyticsPeriod.DAY
    date_from: datetime | None = None
    date_to: datetime | None = None


class TimeSeriesPoint(BaseModel):
    date: str
    value: Decimal


# Revenue
class RevenueSummary(BaseModel):
    total_revenue: Decimal
    today_revenue: Decimal
    week_revenue: Decimal
    month_revenue: Decimal


class RevenueResponse(BaseModel):
    summary: RevenueSummary
    time_series: list[TimeSeriesPoint]


# Bookings
class BookingsSummary(BaseModel):
    total_orders: int
    paid_count: int
    cancelled_count: int
    failed_count: int
    pending_count: int
    conversion_rate: Decimal


class BookingsTimeSeriesPoint(BaseModel):
    date: str
    paid: int
    cancelled: int
    failed: int
    pending: int


class BookingsResponse(BaseModel):
    summary: BookingsSummary
    time_series: list[BookingsTimeSeriesPoint]


# Trips
class TripsSummary(BaseModel):
    total_trips: int
    average_occupancy: Decimal
    total_tickets_sold: int


class TripsResponse(BaseModel):
    summary: TripsSummary
    time_series: list[TimeSeriesPoint]


# Users
class UsersSummary(BaseModel):
    total_users: int
    active_users: int
    new_today: int
    new_this_week: int
    new_this_month: int


class UsersResponse(BaseModel):
    summary: UsersSummary
    time_series: list[TimeSeriesPoint]
