import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.models import (
    Inventory, LocationMaster, PutawayScan, MoveEvent, PickFailure, CycleCount
)

def load_warehouse_data(db: Session, sku: str) -> Dict[str, Any]:
    """
    Load all warehouse events related to a specific SKU from DB or raw data tables.
    """
    inventory_item = db.query(Inventory).filter(Inventory.sku == sku).first()
    locations = db.query(LocationMaster).all()
    putaways = db.query(PutawayScan).filter(PutawayScan.sku == sku).all()
    moves = db.query(MoveEvent).filter(MoveEvent.sku == sku).all()
    pick_failures = db.query(PickFailure).filter(PickFailure.sku == sku).all()
    cycle_counts = db.query(CycleCount).filter(CycleCount.sku == sku).all()
    
    return {
        "inventory": inventory_item,
        "locations": locations,
        "putaways": putaways,
        "moves": moves,
        "pick_failures": pick_failures,
        "cycle_counts": cycle_counts
    }

def build_inventory_scan_trail(db: Session, sku: str) -> List[Dict[str, Any]]:
    """
    Creates a unified, chronologically sorted timeline of all warehouse events for an SKU.
    """
    data = load_warehouse_data(db, sku)
    events = []
    
    # 1. Putaway events
    for p in data["putaways"]:
        events.append({
            "event_type": "PUTAWAY",
            "id": p.scan_id,
            "timestamp": p.timestamp.isoformat() if p.timestamp else "",
            "dt": p.timestamp,
            "location": p.destination_location or p.to_location,
            "source": p.source_location or p.from_location,
            "worker_id": p.worker_id,
            "quantity": p.quantity,
            "details": f"Putaway scan to location {p.destination_location or p.to_location}"
        })
        
    # 2. Move events
    for m in data["moves"]:
        events.append({
            "event_type": "MOVE",
            "id": m.move_id,
            "timestamp": m.timestamp.isoformat() if m.timestamp else "",
            "dt": m.timestamp,
            "location": m.destination_location,
            "source": m.source_location,
            "worker_id": m.worker_id,
            "quantity": m.quantity,
            "reason": m.reason,
            "details": f"Move event from {m.source_location} to {m.destination_location} (Reason: {m.reason})"
        })
        
    # 3. Pick Failures
    for pf in data["pick_failures"]:
        events.append({
            "event_type": "PICK_FAILURE",
            "id": pf.failure_id,
            "timestamp": pf.timestamp.isoformat() if pf.timestamp else "",
            "dt": pf.timestamp,
            "location": pf.expected_location,
            "source": pf.expected_location,
            "worker_id": pf.worker_id,
            "reason": pf.failure_reason,
            "details": f"Pick failure reported at expected location {pf.expected_location} ({pf.failure_reason})"
        })
        
    # 4. Cycle Counts
    for cc in data["cycle_counts"]:
        events.append({
            "event_type": "CYCLE_COUNT",
            "id": cc.count_id,
            "timestamp": cc.timestamp.isoformat() if cc.timestamp else "",
            "dt": cc.timestamp,
            "location": cc.location_id,
            "counted_quantity": cc.counted_quantity,
            "system_quantity": cc.system_quantity,
            "variance": cc.variance,
            "worker_id": cc.worker_id,
            "details": f"Cycle count at {cc.location_id}: Counted {cc.counted_quantity} (System expected: {cc.system_quantity}, Variance: {cc.variance})"
        })
        
    # Sort chronologically by timestamp
    events.sort(key=lambda x: x["dt"] if x.get("dt") else datetime.min)
    
    # Remove temporary datetime object before returning
    for e in events:
        e.pop("dt", None)
        
    return events
