from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Camp(Base):
    __tablename__ = "camps"

    camp_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, default=0)
    current_population = Column(Integer, default=0)
    status = Column(String(30), default="open")                    # open, full, closed
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resources = relationship("Resource", back_populates="camp", cascade="all, delete-orphan")