from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Inventory, PutawayScan, MoveEvent, LocationMaster

def get_baseline_prediction(db: Session, sku: str) -> Dict[str, Any]:
    """
    Implements the Baseline strategy: Latest Known Location.
    Finds the latest scan or move event for the SKU and returns the destination location.
    If no events exist, falls back to expected_location_id.
    """
    inventory = db.query(Inventory).filter(Inventory.sku == sku).first()
    expected_loc = inventory.expected_location_id if inventory else "UNKNOWN"
    
    putaways = db.query(PutawayScan).filter(PutawayScan.sku == sku).all()
    moves = db.query(MoveEvent).filter(MoveEvent.sku == sku).all()
    
    latest_event_time = None
    latest_location = expected_loc
    event_source = "EXPECTED_LOCATION_FALLBACK"
    
    for p in putaways:
        dest = p.destination_location or p.to_location
        if p.timestamp and (latest_event_time is None or p.timestamp > latest_event_time):
            latest_event_time = p.timestamp
            latest_location = dest
            event_source = f"PUTAWAY_SCAN_{p.scan_id}"
            
    for m in moves:
        if m.timestamp and (latest_event_time is None or m.timestamp > latest_event_time):
            latest_event_time = m.timestamp
            latest_location = m.destination_location
            event_source = f"MOVE_EVENT_{m.move_id}"

    # Calculate estimated search time for baseline (standard manual search without probabilistic ranking)
    # Manual location search takes ~45 minutes baseline average
    estimated_search_time_mins = 45.0 if latest_location != expected_loc else 15.0

    return {
        "sku": sku,
        "expected_location": expected_loc,
        "baseline_predicted_location": latest_location,
        "model_name": "Latest Known Location Baseline",
        "evidence_source": event_source,
        "timestamp": latest_event_time.isoformat() if latest_event_time else datetime.utcnow().isoformat(),
        "estimated_search_time_mins": estimated_search_time_mins
    }
