from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import LocationMaster
from app.schemas.schemas import LocationMasterBase

router = APIRouter(prefix="/api/locations", tags=["Locations"])

@router.get("", response_model=List[LocationMasterBase])
def get_all_locations(
    zone: Optional[str] = None,
    status: Optional[str] = None,
    restricted: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LocationMaster)
    if zone:
        query = query.filter(LocationMaster.zone == zone)
    if status:
        query = query.filter(LocationMaster.status == status)
    if restricted is not None:
        query = query.filter(LocationMaster.restricted == restricted)
    return query.all()

@router.get("/{location_code}", response_model=LocationMasterBase)
def get_location_by_code(location_code: str, db: Session = Depends(get_db)):
    loc = db.query(LocationMaster).filter(
        (LocationMaster.location_code == location_code) | (LocationMaster.location_id == location_code)
    ).first()
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location '{location_code}' not found.")
    return loc
