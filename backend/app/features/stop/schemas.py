from uuid import UUID

from pydantic import BaseModel, Field

from app.common.schemas import EntityModel, Latitude, Longitude


class StopBase(BaseModel):
    city_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    latitude: Latitude
    longitude: Longitude


class StopCreate(StopBase):
    pass


class StopUpdate(BaseModel):
    city_id: UUID | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    latitude: Latitude | None = None
    longitude: Longitude | None = None


class StopRead(StopBase, EntityModel):
    pass
