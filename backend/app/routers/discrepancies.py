from datetime import datetime, timedelta
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Discrepancy, PutawayScan, MoveEvent, PickFailure, CycleCount, AuditLog
from app.schemas.schemas import DiscrepancyResponse, DiscrepancyActionRequest
from app.ml.engine import discrepancy_engine

router = APIRouter(prefix="/api/discrepancies", tags=["Discrepancies"])

@router.get("", response_model=List[DiscrepancyResponse])
def list_discrepancies(
    zone: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    min_confidence: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Discrepancy)
    if priority:
        query = query.filter(Discrepancy.priority == priority)
    if status:
        query = query.filter(Discrepancy.status == status)
    if min_confidence:
        query = query.filter(Discrepancy.confidence >= min_confidence)
    
    discrepancies = query.all()

    # If database discrepancies table is empty, generate from seed SKUs dynamically
    if not discrepancies:
        skus_with_failures = db.query(PickFailure.sku).distinct().all()
        sku_list = [s[0] for s in skus_with_failures] or ["MED-1042"]
        
        for sku in sku_list:
            pred = discrepancy_engine.predict_discrepancy(db, sku)
            disc = Discrepancy(
                id=f"DISC-{sku}",
                sku=pred["sku"],
                batch_id=pred["batch_id"],
                quantity=pred["quantity"],
                expected_location=pred["expected_location"],
                predicted_location=pred["predicted_location"],
                baseline_location=pred["baseline_location"],
                confidence=pred["confidence"],
                priority=pred["priority"],
                sla_deadline=pred["sla_deadline"],
                status="SUSPECTED",
                evidence_json=pred["evidence_json"],
                candidates_json=pred["candidates_json"],
                safety_blocked=pred["safety_blocked"],
                safety_reason=pred["safety_reason"]
            )
            db.add(disc)
        db.commit()
        discrepancies = db.query(Discrepancy).all()

    return discrepancies

@router.get("/{discrepancy_id}", response_model=DiscrepancyResponse)
def get_discrepancy(discrepancy_id: str, db: Session = Depends(get_db)):
    disc = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
    if not disc:
        # Try matching by SKU e.g. DISC-MED-1042 or MED-1042
        disc = db.query(Discrepancy).filter(Discrepancy.sku == discrepancy_id).first()
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy record not found.")
    return disc

@router.post("/{discrepancy_id}/verify", response_model=DiscrepancyResponse)
def verify_discrepancy(discrepancy_id: str, req: DiscrepancyActionRequest, db: Session = Depends(get_db)):
    disc = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found.")

    disc.status = "LOCATED"
    disc.updated_at = datetime.utcnow()

    # Log audit entry
    audit = AuditLog(
        id=str(uuid.uuid4()),
        event_type="VERIFY_LOCATION",
        sku=disc.sku,
        location_id=disc.predicted_location,
        details_json={"notes": req.notes, "previous_status": "SUSPECTED", "new_status": "LOCATED"}
    )
    db.add(audit)
    db.commit()
    db.refresh(disc)
    return disc

@router.post("/{discrepancy_id}/correct", response_model=DiscrepancyResponse)
def correct_discrepancy(discrepancy_id: str, req: DiscrepancyActionRequest, db: Session = Depends(get_db)):
    disc = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found.")

    verified_loc = req.actual_verified_location or disc.predicted_location

    disc.status = "CORRECTED"
    disc.expected_location = verified_loc
    disc.updated_at = datetime.utcnow()

    # Log audit entry
    audit = AuditLog(
        id=str(uuid.uuid4()),
        event_type="MARK_CORRECTED",
        sku=disc.sku,
        location_id=verified_loc,
        details_json={"notes": req.notes, "corrected_location": verified_loc}
    )
    db.add(audit)
    db.commit()
    db.refresh(disc)
    return disc

@router.post("/{discrepancy_id}/report-missing", response_model=DiscrepancyResponse)
def report_missing(discrepancy_id: str, req: DiscrepancyActionRequest, db: Session = Depends(get_db)):
    disc = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found.")

    disc.status = "MISSING"
    disc.updated_at = datetime.utcnow()

    audit = AuditLog(
        id=str(uuid.uuid4()),
        event_type="REPORT_MISSING",
        sku=disc.sku,
        location_id=disc.expected_location,
        details_json={"notes": req.notes}
    )
    db.add(audit)
    db.commit()
    db.refresh(disc)
    return disc
