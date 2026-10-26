from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TeamBase(BaseModel):
    name: str
    type: str
    member_count: int = 1
    specialisation: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    availability: bool = True
    assigned_mission_id: Optional[int] = None


class TeamCreate(TeamBase):
    pass


class TeamOut(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    team_id: int
    updated_at: datetime