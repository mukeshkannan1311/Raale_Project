import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Assignment, Discrepancy, Worker, LocationMaster, AuditLog
from app.schemas.schemas import AssignmentResponse, AssignmentCreateRequest
from app.services.safety_fairness import SafetyFairnessService

router = APIRouter(prefix="/api/assignments", tags=["Assignments"])

@router.get("", response_model=List[AssignmentResponse])
def list_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).all()

@router.get("/fairness-panel/{discrepancy_id}")
def get_fairness_panel(discrepancy_id: str, db: Session = Depends(get_db)):
    return SafetyFairnessService.compute_fairness_panel(db, discrepancy_id)

@router.post("", response_model=AssignmentResponse)
def create_assignment(req: AssignmentCreateRequest, db: Session = Depends(get_db)):
    discrepancy = db.query(Discrepancy).filter(Discrepancy.id == req.discrepancy_id).first()
    if not discrepancy:
        raise HTTPException(status_code=404, detail="Discrepancy record not found.")

    worker = db.query(Worker).filter(Worker.worker_id == req.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker record not found.")

    target_loc_id = discrepancy.predicted_location or discrepancy.expected_location
    location = db.query(LocationMaster).filter(LocationMaster.location_id == target_loc_id).first()

    # Enforce Safety System Validation
    is_safe, safety_msg = SafetyFairnessService.validate_worker_safety(worker, location, discrepancy)
    if not is_safe:
        # Create audit entry for safety block
        audit = AuditLog(
            id=str(uuid.uuid4()),
            event_type="SAFETY_BLOCK",
            sku=discrepancy.sku,
            worker_id=worker.worker_id,
            location_id=target_loc_id,
            details_json={"reason": safety_msg}
        )
        db.add(audit)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail=f"Assignment blocked due to workload/safety constraint: {safety_msg}"
        )

    workload_utilization = round((worker.current_tasks / float(worker.max_tasks)) * 100.0, 1)

    assignment = Assignment(
        id=f"ASN-{uuid.uuid4().hex[:8].upper()}",
        discrepancy_id=discrepancy.id,
        worker_id=worker.worker_id,
        assigned_at=datetime.utcnow(),
        status="IN_PROGRESS",
        fairness_score=88.5,
        workload_utilization_pct=workload_utilization,
        note=req.note
    )
    
    # Update worker task count
    worker.current_tasks += 1
    discrepancy.status = "IN_PROGRESS"

    audit = AuditLog(
        id=str(uuid.uuid4()),
        event_type="ASSIGNMENT_CREATED",
        sku=discrepancy.sku,
        worker_id=worker.worker_id,
        location_id=target_loc_id,
        details_json={"assignment_id": assignment.id, "worker_name": worker.name}
    )

    db.add(assignment)
    db.add(audit)
    db.commit()
    db.refresh(assignment)

    return assignment
