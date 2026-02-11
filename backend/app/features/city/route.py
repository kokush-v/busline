from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.aws.cognito import get_cognito_service
from app.features.city.schemas import (
    CityCreate,
    CityListResponse,
    CityQueryParams,
    CityRead,
    CitySearchParams,
    CitySearchResponse,
    CityUpdate,
)
from app.features.city.service import CityService
from app.features.user.enums import UserRoleGroups

cognito_service = get_cognito_service()

router = APIRouter(prefix='/cities', tags=['Cities'])


@router.get('/search', response_model=CitySearchResponse)
async def search_cities(
    params: CitySearchParams = Depends(),
    service: CityService = Depends(),
):
    """Public endpoint for searching cities with lazy loading."""
    return await service.search_cities(params)


@router.get('', response_model=CityListResponse)
async def get_cities(
    params: CityQueryParams = Depends(),
    service: CityService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    """Get cities with filtering, sorting, and pagination."""
    cities, total = await service.get_cities(params)

    return CityListResponse(
        items=cities,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )


@router.get('/{city_id}', response_model=CityRead)
async def get_city(
    city_id: UUID,
    service: CityService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.get_city(city_id)


@router.post(
    '',
    response_model=CityRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_city(
    payload: CityCreate,
    service: CityService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.create_city(payload)


@router.put(
    '/{city_id}',
    response_model=CityRead,
)
async def update_city(
    city_id: UUID,
    payload: CityUpdate,
    service: CityService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.update_city(city_id, payload)


@router.delete(
    '/{city_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_city(
    city_id: UUID,
    service: CityService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    await service.delete_city(city_id)
