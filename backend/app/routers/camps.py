from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.camp import Camp
from app.models.resource import Resource
from app.schemas.camp import CampCreate, CampUpdate, CampOut
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceOut

router = APIRouter(prefix="/api/camps", tags=["camps"])


@router.get("", response_model=list[CampOut])
def list_camps(db: Session = Depends(get_db)):
    return db.query(Camp).all()


@router.post("", response_model=CampOut, status_code=201)
def create_camp(payload: CampCreate, db: Session = Depends(get_db)):
    c = Camp(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.patch("/{camp_id}", response_model=CampOut)
def update_camp(camp_id: int, payload: CampUpdate, db: Session = Depends(get_db)):
    c = db.query(Camp).get(camp_id)
    if not c:
        raise HTTPException(404, "Camp not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.get("/{camp_id}/resources", response_model=list[ResourceOut])
def list_camp_resources(camp_id: int, db: Session = Depends(get_db)):
    return db.query(Resource).filter(Resource.camp_id == camp_id).all()


@router.post("/{camp_id}/resources", response_model=ResourceOut, status_code=201)
def add_resource(camp_id: int, payload: ResourceCreate, db: Session = Depends(get_db)):
    if not db.query(Camp).get(camp_id):
        raise HTTPException(404, "Camp not found")
    r = Resource(camp_id=camp_id, **payload.model_dump(exclude={"camp_id"}))
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/{camp_id}/resources/{resource_id}", response_model=ResourceOut)
def update_resource(camp_id: int, resource_id: int, payload: ResourceUpdate, db: Session = Depends(get_db)):
    r = db.query(Resource).filter(Resource.resource_id == resource_id, Resource.camp_id == camp_id).first()
    if not r:
        raise HTTPException(404, "Resource not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)

    # Threshold check → auto-raise low-stock alert
    if r.quantity < r.minimum_threshold:
        from app.models.alert import Alert
        alert = Alert(
            type="low_stock",
            severity="WARNING",
            message=f"Low stock: {r.type} at camp {camp_id} ({r.quantity} {r.unit} < {r.minimum_threshold})",
        )
        db.add(alert)
        db.commit()

    return r