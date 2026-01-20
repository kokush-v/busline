from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.features.city.schemas import CityCreate, CityRead, CityUpdate
from app.features.city.service import CityService


router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("", response_model=list[CityRead])
def list_cities(db: Session = Depends(get_db)):
    return CityService.list_cities(db)


@router.get("/{city_id}", response_model=CityRead)
def get_city(city_id: UUID, db: Session = Depends(get_db)):
    return CityService.get_city(city_id, db)


@router.post(
    "",
    response_model=CityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_city(payload: CityCreate, db: Session = Depends(get_db)):
    return CityService.create_city(payload, db)


@router.put(
    "/{city_id}",
    response_model=CityRead,
)
def update_city(city_id: UUID, payload: CityUpdate, db: Session = Depends(get_db)):
    return CityService.update_city(city_id, payload, db)


@router.delete(
    "/{city_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_city(city_id: UUID, db: Session = Depends(get_db)):
    CityService.delete_city(city_id, db)
