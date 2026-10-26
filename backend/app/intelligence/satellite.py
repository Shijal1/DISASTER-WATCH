"""Satellite integration framework (Sentinel-2 via Copernicus CDSE)."""
import time
from typing import Optional

import httpx

from app.config import settings


TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
INSTANCE_ID = "4877e93a-6038-4e52-ba18-ee81f2174f1d"
WMS_URL = f"https://sh.dataspace.copernicus.eu/ogc/wms/{INSTANCE_ID}"


_token_cache = {"access_token": None, "expires_at": 0}


async def get_access_token() -> Optional[str]:
    if not settings.COPERNICUS_CLIENT_ID or not settings.COPERNICUS_CLIENT_SECRET:
        return None

    now = time.time()
    if _token_cache["access_token"] and _token_cache["expires_at"] > now + 30:
        return _token_cache["access_token"]

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(TOKEN_URL, data={
            "grant_type": "client_credentials",
            "client_id": settings.COPERNICUS_CLIENT_ID,
            "client_secret": settings.COPERNICUS_CLIENT_SECRET,
        })
        if r.status_code != 200:
            print(f"[satellite] token error: {r.status_code} {r.text[:200]}")
            return None
        data = r.json()
        _token_cache["access_token"] = data["access_token"]
        _token_cache["expires_at"] = now + data.get("expires_in", 600)
        return data["access_token"]


async def credentials_ok() -> bool:
    return (await get_access_token()) is not None


def wms_url(layer: str = "NDWI") -> str:
    return WMS_URL


AVAILABLE_LAYERS = {
    "TRUE_COLOR": "TRUE-COLOR-S2L2A",
    "NDWI": "NDWI",
    "NDVI": "NDVI",
}


def layer_meta() -> list[dict]:
    return [
        {"id": "TRUE_COLOR", "label": "True colour",
         "description": "Visual interpretation of terrain and surface"},
        {"id": "NDWI", "label": "NDWI (water index)",
         "description": "Highlights water bodies and possible flooding"},
        {"id": "NDVI", "label": "NDVI (vegetation)",
         "description": "Vegetation health; low values indicate bare/burnt ground"},
    ]