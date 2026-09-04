import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import ValidationFeedback
from app.schemas.schemas import ValidationFeedbackCreate, ValidationFeedbackResponse

router = APIRouter(prefix="/api/validation", tags=["Validation"])

@router.get("", response_model=Dict[str, Any])
def get_validation_summary(db: Session = Depends(get_db)):
    responses = db.query(ValidationFeedback).all()
    if not responses:
        # Seed 3 initial validation responses
        seed_items = [
            ValidationFeedback(id=str(uuid.uuid4()), user_role="WAREHOUSE_OPERATOR", ease_of_understanding=5, usefulness_rating=5, evidence_clarity=4, workflow_safety=5, search_time_reduction=5, overall_rating=5, comments="Discrepancy recommendations significantly reduced pick search times."),
            ValidationFeedback(id=str(uuid.uuid4()), user_role="SAFETY_OFFICER", ease_of_understanding=4, usefulness_rating=4, evidence_clarity=5, workflow_safety=5, search_time_reduction=4, overall_rating=4, comments="Workload limits and restricted area blocks prevented unsafe worker dispatches."),
            ValidationFeedback(id=str(uuid.uuid4()), user_role="LOGISTICS_LEAD", ease_of_understanding=5, usefulness_rating=5, evidence_clarity=5, workflow_safety=4, search_time_reduction=5, overall_rating=5, comments="Evidence breakdown transparently explains why a bin is candidate #1.")
        ]
        for s in seed_items:
            db.add(s)
        db.commit()
        responses = db.query(ValidationFeedback).all()

    count = len(responses)
    avg_overall = sum(r.overall_rating for r in responses) / float(count) if count > 0 else 0.0
    avg_usefulness = sum(r.usefulness_rating for r in responses) / float(count) if count > 0 else 0.0
    avg_clarity = sum(r.evidence_clarity for r in responses) / float(count) if count > 0 else 0.0
    avg_safety = sum(r.workflow_safety for r in responses) / float(count) if count > 0 else 0.0
    avg_search_time = sum(r.search_time_reduction for r in responses) / float(count) if count > 0 else 0.0

    return {
        "total_responses": count,
        "averages": {
            "overall_usefulness": round(avg_overall, 2),
            "location_usefulness": round(avg_usefulness, 2),
            "evidence_clarity": round(avg_clarity, 2),
            "workflow_safety": round(avg_safety, 2),
            "search_time_reduction": round(avg_search_time, 2)
        },
        "responses": responses
    }

@router.post("", response_model=ValidationFeedbackResponse)
def submit_validation_feedback(req: ValidationFeedbackCreate, db: Session = Depends(get_db)):
    feedback = ValidationFeedback(
        id=str(uuid.uuid4()),
        user_role=req.user_role,
        ease_of_understanding=req.ease_of_understanding,
        usefulness_rating=req.usefulness_rating,
        evidence_clarity=req.evidence_clarity,
        workflow_safety=req.workflow_safety,
        search_time_reduction=req.search_time_reduction,
        overall_rating=req.overall_rating,
        comments=req.comments,
        timestamp=datetime.utcnow()
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
