from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Discrepancy, Inventory, AuditLog
from app.schemas.schemas import DiscrepancyResponse, PredictLocationRequest, PredictionResponse, DiscrepancyActionRequest
from app.services.discrepancy_service import detect_all_discrepancies
from app.ml.prediction_engine import predict_actual_location, get_baseline_prediction

router = APIRouter(tags=["Discrepancies & Predictions"])

@router.get("/api/discrepancies", response_model=List[DiscrepancyResponse])
def get_discrepancies(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Discrepancy)
    if status:
        query = query.filter(Discrepancy.status == status)
    if priority:
        query = query.filter(Discrepancy.priority == priority)
    return query.order_by(Discrepancy.created_at.desc()).all()

@router.get("/api/discrepancies/{id}", response_model=DiscrepancyResponse)
def get_discrepancy_by_id(id: str, db: Session = Depends(get_db)):
    disc = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not disc:
        raise HTTPException(status_code=404, detail=f"Discrepancy with ID '{id}' not found.")
    return disc

@router.post("/api/discrepancies/detect")
def run_discrepancy_detection(db: Session = Depends(get_db)):
    results = detect_all_discrepancies(db)
    
    db.add(AuditLog(
        id=f"AUD-{int(datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        action="DISCREPANCY_DETECTION_RUN",
        entity="DISCREPANCIES",
        details_json={"detected_count": len(results)}
    ))
    db.commit()
    
    return {
        "message": f"Discrepancy detection engine completed successfully.",
        "detected_count": len(results),
        "discrepancies": [r.id for r in results]
    }

@router.post("/api/predict-location", response_model=PredictionResponse)
def predict_location_endpoint(payload: PredictLocationRequest, db: Session = Depends(get_db)):
    sku = payload.sku
    inventory = db.query(Inventory).filter(Inventory.sku == sku).first()
    if not inventory:
        raise HTTPException(status_code=404, detail=f"SKU '{sku}' not found in inventory master.")
        
    res = predict_actual_location(db, sku)
    
    db.add(AuditLog(
        id=f"AUD-{int(datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        action="PREDICTION_GENERATED",
        entity="PREDICTION",
        sku=sku,
        location_id=res["predicted_location"],
        details_json={"confidence": res["confidence"], "top_candidates_count": len(res["top_candidates"])}
    ))
    db.commit()
    
    return res

@router.get("/api/predictions/{sku}", response_model=PredictionResponse)
def get_prediction_by_sku(sku: str, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.sku == sku).first()
    if not inventory:
        raise HTTPException(status_code=404, detail=f"SKU '{sku}' not found in inventory master.")
    return predict_actual_location(db, sku)

@router.post("/api/discrepancies/{id}/resolve")
def resolve_discrepancy(
    id: str,
    action: DiscrepancyActionRequest,
    db: Session = Depends(get_db)
):
    disc = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not disc:
        raise HTTPException(status_code=404, detail=f"Discrepancy with ID '{id}' not found.")
        
    verified_loc = action.actual_verified_location or disc.predicted_location
    disc.status = "RESOLVED"
    disc.correction_status = "RESOLVED"
    disc.verified_location = verified_loc
    disc.resolved_at = datetime.utcnow()
    disc.updated_at = datetime.utcnow()
    
    # Update inventory master location and status
    inv = db.query(Inventory).filter(Inventory.sku == disc.sku).first()
    if inv:
        inv.expected_location_id = verified_loc
        inv.status = "AVAILABLE"
        inv.updated_at = datetime.utcnow()
        db.add(inv)
        
    db.add(AuditLog(
        id=f"AUD-{int(datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        action="DISCREPANCY_RESOLVED",
        entity="DISCREPANCY",
        sku=disc.sku,
        location_id=verified_loc,
        details_json={"notes": action.notes, "resolved_location": verified_loc}
    ))
    db.commit()
    
    return {
        "message": f"Discrepancy '{id}' resolved and inventory location updated to '{verified_loc}'.",
        "discrepancy_id": id,
        "verified_location": verified_loc
    }

@router.post("/api/discrepancies/{id}/verify")
def verify_discrepancy_endpoint(
    id: str,
    action: Optional[DiscrepancyActionRequest] = None,
    db: Session = Depends(get_db)
):
    disc = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not disc:
        raise HTTPException(status_code=404, detail=f"Discrepancy with ID '{id}' not found.")
    disc.status = "VERIFIED"
    disc.updated_at = datetime.utcnow()
    db.add(AuditLog(
        id=f"AUD-{int(datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        action="DISCREPANCY_VERIFIED",
        entity="DISCREPANCY",
        sku=disc.sku,
        details_json={"notes": action.notes if action else None}
    ))
    db.commit()
    return disc

@router.post("/api/discrepancies/{id}/correct")
def correct_discrepancy_endpoint(
    id: str,
    action: DiscrepancyActionRequest,
    db: Session = Depends(get_db)
):
    return resolve_discrepancy(id, action, db)

@router.post("/api/discrepancies/{id}/report-missing")
def report_missing_endpoint(
    id: str,
    action: Optional[DiscrepancyActionRequest] = None,
    db: Session = Depends(get_db)
):
    disc = db.query(Discrepancy).filter(Discrepancy.id == id).first()
    if not disc:
        raise HTTPException(status_code=404, detail=f"Discrepancy with ID '{id}' not found.")
    disc.status = "REPORTED_MISSING"
    disc.updated_at = datetime.utcnow()
    db.add(AuditLog(
        id=f"AUD-{int(datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        action="DISCREPANCY_REPORTED_MISSING",
        entity="DISCREPANCY",
        sku=disc.sku,
        details_json={"notes": action.notes if action else None}
    ))
    db.commit()
    return disc
