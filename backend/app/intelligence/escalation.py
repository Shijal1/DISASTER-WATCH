"""Auto-escalation of unacknowledged CRITICAL alerts.
Rule:
  - CRITICAL alert active & unacknowledged for >= 5 min  -> escalation_level = 1
  - CRITICAL alert active & unacknowledged for >= 15 min -> escalation_level = 2
Level 1: warn in log, broadcast `alert_escalated` with level 1
Level 2: broadcast `alert_escalated` with level 2 and mark severity as ESCALATED_CRITICAL
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.realtime.manager import manager
LEVEL_1_MINUTES = 5
LEVEL_2_MINUTES = 15
async def run_escalation_check(db: Session) -> list[dict]:
    now = datetime.utcnow()
    escalated = []
    candidates = (
        db.query(Alert)
        .filter(Alert.status == "active")
        .filter(Alert.severity.in_(["CRITICAL", "ESCALATED_CRITICAL"]))
        .all()
    )
    for alert in candidates:
        age_min = (now - alert.created_at).total_seconds() / 60
        current = alert.escalation_level or 0
        if current < 1 and age_min >= LEVEL_1_MINUTES:
            alert.escalation_level = 1
            db.commit()
            escalated.append({"alert_id": alert.alert_id, "level": 1})
            await manager.broadcast("alert_escalated", {
                "alert_id": alert.alert_id,
                "level": 1,
                "message": f"CRITICAL alert {alert.alert_id} unacknowledged for {int(age_min)} min",
            })
        if current < 2 and age_min >= LEVEL_2_MINUTES:
            alert.escalation_level = 2
            alert.severity = "ESCALATED_CRITICAL"
            db.commit()
            escalated.append({"alert_id": alert.alert_id, "level": 2})
            await manager.broadcast("alert_escalated", {
                "alert_id": alert.alert_id,
                "level": 2,
                "message": f"CRITICAL alert {alert.alert_id} unacknowledged for {int(age_min)} min - ESCALATED",
            })
    return escalated