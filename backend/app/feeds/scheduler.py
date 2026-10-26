"""Background scheduler for feed polling and auto-escalation."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import SessionLocal
from app.models.incident import Incident
from app.feeds.usgs import USGSAdapter
from app.feeds.eonet import EONETAdapter
from app.feeds.gdacs import GDACSAdapter
from app.intelligence.escalation import run_escalation_check
from app.realtime.manager import manager
scheduler = AsyncIOScheduler()
async def poll_feed(adapter) -> None:
    db = SessionLocal()
    try:
        items = await adapter.run()
        new_count = 0
        for payload in items:
            existing = (
                db.query(Incident)
                .filter(Incident.source == payload["source"])
                .filter(Incident.type == payload["type"])
                .filter(Incident.latitude.between(payload["latitude"] - 0.01, payload["latitude"] + 0.01))
                .filter(Incident.longitude.between(payload["longitude"] - 0.01, payload["longitude"] + 0.01))
                .first()
            )
            if existing:
                continue
            inc = Incident(**payload)
            db.add(inc); db.commit(); db.refresh(inc)
            new_count += 1
            await manager.broadcast("feed_incident", {
                "incident_id": inc.incident_id,
                "type": inc.type,
                "severity": inc.severity,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "source": inc.source,
            })
        print(f"[{adapter.name}] {len(items)} fetched, {new_count} new")
    except Exception as e:
        print(f"[{adapter.name}] failed: {e}")
    finally:
        db.close()
async def poll_all():
    await poll_feed(USGSAdapter())
    await poll_feed(EONETAdapter())
    await poll_feed(GDACSAdapter())
async def escalation_tick():
    db = SessionLocal()
    try:
        out = await run_escalation_check(db)
        if out:
            print(f"[escalation] {len(out)} alerts escalated")
    finally:
        db.close()
def start_scheduler():
    scheduler.add_job(poll_all, "interval", seconds=300, id="feeds", replace_existing=True)
    scheduler.add_job(escalation_tick, "interval", seconds=60, id="escalation", replace_existing=True)
    scheduler.start()
    print("[scheduler] Started - feeds every 5 min, escalation check every 1 min")