from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CampBase(BaseModel):
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    capacity: int = 0
    current_population: int = 0
    status: str = "open"


class CampCreate(CampBase):
    pass


class CampUpdate(BaseModel):
    capacity: Optional[int] = None
    current_population: Optional[int] = None
    status: Optional[str] = None


class CampOut(CampBase):
    model_config = ConfigDict(from_attributes=True)

    camp_id: int
    updated_at: datetime