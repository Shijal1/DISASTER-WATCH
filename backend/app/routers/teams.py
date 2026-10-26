from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamOut

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("", response_model=list[TeamOut])
def list_teams(db: Session = Depends(get_db)):
    return db.query(Team).all()


@router.post("", response_model=TeamOut, status_code=201)
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    t = Team(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.post("/{team_id}/assign", response_model=TeamOut)
def assign_team(team_id: int, incident_id: int, db: Session = Depends(get_db)):
    t = db.query(Team).get(team_id)
    if not t:
        raise HTTPException(404, "Team not found")
    t.assigned_mission_id = incident_id
    t.availability = False
    db.commit()
    db.refresh(t)
    return t