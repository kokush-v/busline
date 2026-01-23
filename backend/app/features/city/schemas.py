from pydantic import BaseModel, Field

from app.common.schemas import EntityModel, Latitude, Longitude


class CityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    longitude: Longitude
    latitude: Latitude


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    longitude: Longitude | None = None
    latitude: Latitude | None = None


class CityRead(CityBase, EntityModel):
    pass
