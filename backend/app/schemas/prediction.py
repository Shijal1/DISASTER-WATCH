from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PredictionBase(BaseModel):
    hazard_type: str
    risk_level: str
    geometry: Optional[str] = None
    estimated_arrival: Optional[datetime] = None
    estimated_population: Optional[int] = None
    recommended_action: Optional[str] = None


class PredictionCreate(PredictionBase):
    incident_id: int


class PredictionOut(PredictionBase):
    model_config = ConfigDict(from_attributes=True)

    prediction_id: int
    incident_id: int
    generated_at: datetime
    is_estimate: str