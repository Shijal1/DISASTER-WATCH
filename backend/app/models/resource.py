from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Resource(Base):
    __tablename__ = "resources"

    resource_id = Column(Integer, primary_key=True, index=True)
    camp_id = Column(Integer, ForeignKey("camps.camp_id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)                      # food, water, medicine, blankets, fuel
    quantity = Column(Integer, default=0)
    unit = Column(String(20), default="units")
    minimum_threshold = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    camp = relationship("Camp", back_populates="resources")