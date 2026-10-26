from typing import Optional

from pydantic import BaseModel, Field


class SOSCreate(BaseModel):
    category: str = Field(..., description="flood, earthquake, fire, medical, trapped, other")
    affected_people: int = Field(1, ge=0)
    description: str = Field(..., min_length=3)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class SOSOut(BaseModel):
    severity: str
    matched_evidence: list[str]
    candidate_location: Optional[str] = None
    incident_id: int
    message: str