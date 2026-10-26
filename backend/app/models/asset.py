from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)                      # ambulance, helicopter, police, fire_truck, drone, boat
    label = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    availability = Column(Boolean, default=True)
    status = Column(String(30), default="idle")                    # idle, assigned, en_route, on_scene, offline
    assigned_incident_id = Column(Integer, ForeignKey("incidents.incident_id"), nullable=True)
    assigned_team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_incident = relationship("Incident", back_populates="assets")