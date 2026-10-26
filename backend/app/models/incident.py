from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
class Incident(Base):
    __tablename__ = "incidents"
    incident_id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)
    location_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False, default="LOW")
    description = Column(Text, nullable=True)
    source = Column(String(50), nullable=False, default="citizen")
    verified_flag = Column(Boolean, default=False)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_by = Column(String(100), nullable=True)
    responding_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    predictions = relationship("Prediction", back_populates="incident", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="incident", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="assigned_incident")