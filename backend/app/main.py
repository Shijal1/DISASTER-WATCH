from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.realtime.manager import manager
from app.feeds.scheduler import start_scheduler, poll_all
from app.routers import (
    incidents, assets, teams, camps, alerts, predictions, sos, feeds, satellite,
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    asyncio.create_task(poll_all())
    yield
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Assisted Disaster Intelligence and Emergency Response Coordination Platform",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/api/health")
def api_health():
    return {"status": "ok"}
@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
app.include_router(incidents.router)
app.include_router(assets.router)
app.include_router(teams.router)
app.include_router(camps.router)
app.include_router(alerts.router)
app.include_router(predictions.router)
app.include_router(sos.router)
app.include_router(feeds.router)
app.include_router(satellite.router)