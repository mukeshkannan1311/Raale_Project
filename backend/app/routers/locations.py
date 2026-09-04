from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import LocationMaster, Discrepancy, PutawayScan, MoveEvent, CycleCount
from app.schemas.schemas import LocationMasterBase

router = APIRouter(prefix="/api/locations", tags=["Locations"])

@router.get("", response_model=List[LocationMasterBase])
def list_locations(zone: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(LocationMaster)
    if zone:
        query = query.filter(LocationMaster.zone == zone)
    if status:
        query = query.filter(LocationMaster.status == status)
    return query.all()

@router.get("/{location_id}")
def get_location_details(location_id: str, db: Session = Depends(get_db)):
    loc = db.query(LocationMaster).filter(LocationMaster.location_id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location master record not found.")

    # Find active inventory / scans
    putaways = db.query(PutawayScan).filter(PutawayScan.to_location == location_id).limit(10).all()
    moves = db.query(MoveEvent).filter(MoveEvent.destination_location == location_id).limit(10).all()
    cycle_counts = db.query(CycleCount).filter(CycleCount.location_id == location_id).limit(5).all()

    # Active discrepancies pointing to or at this location
    discrepancies = db.query(Discrepancy).filter(
        (Discrepancy.expected_location == location_id) | (Discrepancy.predicted_location == location_id)
    ).all()

    return {
        "location": loc,
        "recent_putaways": putaways,
        "recent_moves": moves,
        "recent_cycle_counts": cycle_counts,
        "discrepancies": discrepancies
    }
