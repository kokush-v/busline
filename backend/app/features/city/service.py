from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.features.city.models import City
from app.features.city.schemas import CityCreate, CityUpdate


class CityService:
    @staticmethod
    def list_cities(db: Session) -> list[City]:
        return db.query(City).all()

    @staticmethod
    def get_city(city_id: UUID, db: Session) -> City:
        city = db.get(City, city_id)
        if city is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="City not found"
            )
        return city

    @staticmethod
    def create_city(payload: CityCreate, db: Session) -> City:
        existing = db.query(City).filter(City.name == payload.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City with this name already exists",
            )

        city = City(**payload.model_dump())
        db.add(city)
        db.commit()
        db.refresh(city)
        return city

    @staticmethod
    def update_city(city_id: UUID, payload: CityUpdate, db: Session) -> City:
        city = CityService.get_city(city_id, db)

        update_data = payload.model_dump(exclude_unset=True)
        if "name" in update_data:
            conflict = (
                db.query(City)
                .filter(City.name == update_data["name"], City.id != city_id)
                .first()
            )
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="City with this name already exists",
                )

        for field, value in update_data.items():
            setattr(city, field, value)

        db.add(city)
        db.commit()
        db.refresh(city)
        return city

    @staticmethod
    def delete_city(city_id: UUID, db: Session) -> None:
        city = CityService.get_city(city_id, db)
        db.delete(city)
        db.commit()
