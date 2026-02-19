from fastapi import APIRouter, Depends

from app.core.aws.cognito import get_cognito_service
from app.features.analytics.schemas import (
    AnalyticsQueryParams,
    BookingsResponse,
    RevenueResponse,
    TripsResponse,
    UsersResponse,
)
from app.features.analytics.service import AnalyticsService
from app.features.user.enums import UserRoleGroups

cognito_service = get_cognito_service()
router = APIRouter(prefix='/analytics', tags=['Analytics'])


@router.get('/revenue', response_model=RevenueResponse)
async def get_revenue_stats(
    params: AnalyticsQueryParams = Depends(),
    service: AnalyticsService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.get_revenue(params)


@router.get('/bookings', response_model=BookingsResponse)
async def get_bookings_stats(
    params: AnalyticsQueryParams = Depends(),
    service: AnalyticsService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.get_bookings(params)


@router.get('/trips', response_model=TripsResponse)
async def get_trips_stats(
    params: AnalyticsQueryParams = Depends(),
    service: AnalyticsService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.get_trips(params)


@router.get('/users', response_model=UsersResponse)
async def get_users_stats(
    params: AnalyticsQueryParams = Depends(),
    service: AnalyticsService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.get_users(params)
