from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.models import (
    Inventory, LocationMaster, PutawayScan, MoveEvent, PickFailure, CycleCount, Discrepancy
)
from app.ml.prediction_engine import predict_actual_location
from app.services.baseline_service import get_baseline_prediction

def detect_all_discrepancies(db: Session) -> List[Discrepancy]:
    """
    Scans entire inventory database to automatically identify location discrepancies.
    Creates or updates Discrepancy records in the database.
    """
    inventory_items = db.query(Inventory).all()
    detected_discrepancies = []
    
    for inv in inventory_items:
        sku = inv.sku
        expected_loc = inv.expected_location_id
        
        # Check signals
        pick_fails = db.query(PickFailure).filter(PickFailure.sku == sku).all()
        cycle_counts = db.query(CycleCount).filter(CycleCount.sku == sku, CycleCount.location_id == expected_loc).all()
        latest_move = db.query(MoveEvent).filter(MoveEvent.sku == sku).order_by(MoveEvent.timestamp.desc()).first()
        
        has_pick_failure = len(pick_fails) > 0
        has_count_mismatch = any(cc.variance != 0 for cc in cycle_counts)
        has_unrecorded_move = latest_move and latest_move.destination_location != expected_loc
        
        if has_pick_failure or has_count_mismatch or has_unrecorded_move:
            # Run baseline and PharmaTrace predictions
            baseline = get_baseline_prediction(db, sku)
            prediction = predict_actual_location(db, sku)
            
            # Check existing discrepancy record
            existing = db.query(Discrepancy).filter(Discrepancy.sku == sku).first()
            priority = "CRITICAL" if has_pick_failure and inv.storage_requirement != "AMBIENT" else "HIGH"
            
            if existing:
                existing.predicted_location = prediction["predicted_location"]
                existing.baseline_location = baseline["baseline_predicted_location"]
                existing.confidence = prediction["confidence"]
                existing.priority = priority
                existing.candidates_json = prediction["top_candidates"]
                existing.evidence_json = prediction["explanation"]
                existing.safety_blocked = not prediction["is_valid_recommendation"]
                existing.safety_reason = prediction["rejection_reason"]
                existing.updated_at = datetime.utcnow()
                db.add(existing)
                detected_discrepancies.append(existing)
            else:
                disc_id = f"DISC-{db.query(Discrepancy).count() + 1:04d}"
                new_disc = Discrepancy(
                    id=disc_id,
                    sku=sku,
                    batch_id=inv.batch_id,
                    quantity=inv.quantity,
                    expected_location=expected_loc,
                    predicted_location=prediction["predicted_location"],
                    verified_location=None,
                    baseline_location=baseline["baseline_predicted_location"],
                    confidence=prediction["confidence"],
                    priority=priority,
                    sla_deadline=datetime.utcnow() + timedelta(hours=12),
                    status="SUSPECTED",
                    correction_status="PENDING",
                    evidence_json=prediction["explanation"],
                    candidates_json=prediction["top_candidates"],
                    safety_blocked=not prediction["is_valid_recommendation"],
                    safety_reason=prediction["rejection_reason"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_disc)
                inv.status = "DISCREPANT"
                db.add(inv)
                detected_discrepancies.append(new_disc)
                
    db.commit()
    return detected_discrepancies
