from fastapi import APIRouter

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


@router.get("/status")
def feeds_status():
    """Phase 5 wires real adapters. For now returns static health."""
    return {
        "usgs": {"healthy": False, "last_success": None},
        "eonet": {"healthy": False, "last_success": None},
        "gdacs": {"healthy": False, "last_success": None},
    }