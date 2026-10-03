from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Worker, LocationMaster, Discrepancy, Assignment, Inventory, AuditLog
from app.schemas.schemas import SafetyCheckRequest, SafetyCheckResponse, AssignmentCreateRequest, AssignmentResponse
from app.services.safety_fairness import SafetyFairnessService

router = APIRouter(tags=["Safety & Task Assignments"])

@router.post("/api/safety/check-assignment", response_model=SafetyCheckResponse)
def check_assignment_safety(payload: SafetyCheckRequest, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.worker_id == payload.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker '{payload.worker_id}' not found.")
        
    location = db.query(LocationMaster).filter(LocationMaster.location_id == payload.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{payload.location_id}' not found.")
        
    inventory = db.query(Inventory).filter(Inventory.sku == payload.sku).first()
    dummy_disc = Discrepancy(
        id="TEMP",
        sku=payload.sku,
        expected_location=location.location_id,
        predicted_location=location.location_id
    )
    
    is_safe, reason = SafetyFairnessService.validate_worker_safety(worker, location, dummy_disc)
    
    return {
        "allowed": is_safe,
        "reason": reason,
        "worker_workload_status": {
            "current_tasks": worker.current_tasks,
            "max_tasks": worker.max_tasks,
            "utilization_pct": round((worker.current_tasks / float(worker.max_tasks)) * 100.0, 1),
            "shift_status": worker.shift_status
        },
        "zone_authorization_status": {
            "target_zone": location.zone,
            "worker_authorizations": worker.zone_authorization,
            "authorized": location.zone in [z.strip() for z in worker.zone_authorization.split(",")]
        },
        "location_status": {
            "location_id": location.location_id,
            "status": location.status,
            "restricted": location.restricted
        }
    }

@router.get("/api/assignments/fairness/{discrepancy_id}")
def get_fairness_panel(discrepancy_id: str, db: Session = Depends(get_db)):
    panel = SafetyFairnessService.compute_fairness_panel(db, discrepancy_id)
    return {
        "discrepancy_id": discrepancy_id,
        "evaluated_workers_count": len(panel),
        "candidates": panel
    }

@router.get("/api/assignments/fairness-panel/{discrepancy_id}")
def get_fairness_panel_rows(discrepancy_id: str, db: Session = Depends(get_db)):
    panel = SafetyFairnessService.compute_fairness_panel(db, discrepancy_id)
    return panel

@router.get("/api/assignments", response_model=List[AssignmentResponse])
def get_all_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).order_by(Assignment.assigned_at.desc()).all()

@router.post("/api/assignments", response_model=AssignmentResponse)
def create_investigation_assignment(payload: AssignmentCreateRequest, db: Session = Depends(get_db)):
    disc = db.query(Discrepancy).filter(Discrepancy.id == payload.discrepancy_id).first()
    if not disc:
        raise HTTPException(status_code=404, detail=f"Discrepancy '{payload.discrepancy_id}' not found.")
        
    worker = db.query(Worker).filter(Worker.worker_id == payload.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail=f"Worker '{payload.worker_id}' not found.")
        
    target_loc = db.query(LocationMaster).filter(LocationMaster.location_id == (disc.predicted_location or disc.expected_location)).first()
    
    is_safe, reason = SafetyFairnessService.validate_worker_safety(worker, target_loc, disc) if target_loc else (True, "OK")
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Safety Check Violation: {reason}")
        
    assignment_id = f"ASN-{db.query(Assignment).count() + 1:04d}"
    workload_utilization = round((worker.current_tasks / float(worker.max_tasks)) * 100.0, 1)
    
    assignment = Assignment(
        id=assignment_id,
        discrepancy_id=disc.id,
        worker_id=worker.worker_id,
        assigned_at=datetime.utcnow(),
        status="IN_PROGRESS",
        fairness_score=85.0,
        workload_utilization_pct=workload_utilization,
        note=payload.note
    )
    
    # Increment worker active task count
    worker.current_tasks += 1
    disc.status = "INVESTIGATING"
    
    db.add(assignment)
    db.add(worker)
    db.add(disc)
    
    db.add(AuditLog(
        id=f"AUD-{int(datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        action="ASSIGNMENT_CREATED",
        entity="ASSIGNMENT",
        sku=disc.sku,
        worker_id=worker.worker_id,
        details_json={"assignment_id": assignment_id, "discrepancy_id": disc.id}
    ))
    db.commit()
    
    return assignment
