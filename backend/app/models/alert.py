from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
class Alert(Base):
    __tablename__ = "alerts"
    alert_id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    severity = Column(String(20), default="INFO")
    related_incident_id = Column(Integer, ForeignKey("incidents.incident_id"), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    escalation_level = Column(Integer, default=0)
    incident = relationship("Incident", back_populates="alerts")