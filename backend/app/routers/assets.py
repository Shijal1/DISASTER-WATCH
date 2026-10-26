from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate, AssetOut

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("", response_model=list[AssetOut])
def list_assets(availability: Optional[bool] = None, db: Session = Depends(get_db)):
    q = db.query(Asset)
    if availability is not None:
        q = q.filter(Asset.availability == availability)
    return q.all()


@router.post("", response_model=AssetOut, status_code=201)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    a = Asset(**payload.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.patch("/{asset_id}", response_model=AssetOut)
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    a = db.query(Asset).get(asset_id)
    if not a:
        raise HTTPException(404, "Asset not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@router.post("/{asset_id}/assign", response_model=AssetOut)
def assign_asset(asset_id: int, incident_id: int, db: Session = Depends(get_db)):
    a = db.query(Asset).get(asset_id)
    if not a:
        raise HTTPException(404, "Asset not found")
    a.assigned_incident_id = incident_id
    a.availability = False
    a.status = "assigned"
    db.commit()
    db.refresh(a)
    return a