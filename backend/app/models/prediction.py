from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.incident_id"), nullable=False, index=True)
    hazard_type = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False)                # CORE, HIGH, MEDIUM, LOW
    geometry = Column(Text, nullable=True)                         # GeoJSON string (polygon / circle spec)
    estimated_arrival = Column(DateTime, nullable=True)
    estimated_population = Column(Integer, nullable=True)
    recommended_action = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_estimate = Column(String(10), default="ESTIMATE")           # explicit flag for UI

    incident = relationship("Incident", back_populates="predictions")