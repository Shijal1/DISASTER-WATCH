from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)                      # rescue, medical, fire, police, volunteer
    member_count = Column(Integer, default=1)
    specialisation = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    availability = Column(Boolean, default=True)
    assigned_mission_id = Column(Integer, nullable=True)           # references incident_id (soft)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)