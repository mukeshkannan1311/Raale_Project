import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.models import Inventory, LocationMaster, PutawayScan, MoveEvent, PickFailure, CycleCount

def extract_candidate_features(
    db: Session,
    sku: str,
    candidate_location: LocationMaster,
    inventory: Inventory,
    putaways: List[PutawayScan],
    moves: List[MoveEvent],
    pick_failures: List[PickFailure],
    cycle_counts: List[CycleCount]
) -> Dict[str, float]:
    """
    Extracts numerical and categorical feature signals for a candidate location.
    """
    now = datetime.utcnow()
    loc_id = candidate_location.location_id
    expected_loc = inventory.expected_location_id if inventory else ""
    storage_req = inventory.storage_requirement if inventory else "AMBIENT"
    qty_expected = inventory.quantity if inventory else 100
    
    # 1. Scan Recency (hours)
    scans_to_loc = [p for p in putaways if (p.destination_location == loc_id or p.to_location == loc_id)]
    if scans_to_loc:
        last_scan_time = max(p.timestamp for p in scans_to_loc if p.timestamp)
        scan_recency = (now - last_scan_time).total_seconds() / 3600.0
    else:
        scan_recency = 999.0 # Default large value
        
    # 2. Movement Recency & Frequency
    moves_to_loc = [m for m in moves if m.destination_location == loc_id]
    movement_frequency = float(len(moves_to_loc))
    if moves_to_loc:
        last_move_time = max(m.timestamp for m in moves_to_loc if m.timestamp)
        movement_recency = (now - last_move_time).total_seconds() / 3600.0
    else:
        movement_recency = 999.0
        
    # 3. Previous Location Match (is candidate destination of latest move event?)
    if moves:
        latest_move = max(moves, key=lambda m: m.timestamp if m.timestamp else datetime.min)
        previous_location_match = 1.0 if latest_move.destination_location == loc_id else 0.0
    else:
        previous_location_match = 0.0
        
    # 4. Pick Failure Signal (-1.0 if pick failed at candidate location recently)
    failures_at_loc = [pf for pf in pick_failures if pf.expected_location == loc_id]
    pick_failure_signal = -1.0 if len(failures_at_loc) > 0 else 0.0
    
    # 5. Cycle Count Signal & Quantity Match
    counts_at_loc = [cc for cc in cycle_counts if cc.location_id == loc_id]
    if counts_at_loc:
        latest_count = max(counts_at_loc, key=lambda c: c.timestamp if c.timestamp else datetime.min)
        if latest_count.counted_quantity > 0:
            cycle_count_signal = 1.0
            quantity_match = 1.0 if abs(latest_count.counted_quantity - qty_expected) <= 5 else 0.5
        else:
            cycle_count_signal = -1.0
            quantity_match = 0.0
    else:
        cycle_count_signal = 0.0
        quantity_match = 0.5
        
    # 6. Storage Compatibility (HARD CHECK)
    # COLD_STORAGE product requires COLD_STORAGE zone; CONTROLLED_ACCESS requires CONTROLLED_ACCESS, etc.
    if storage_req == candidate_location.zone:
        storage_compatibility = 1.0
    elif storage_req in ["AMBIENT", "QUARANTINE"] and candidate_location.zone in ["AMBIENT", "QUARANTINE"]:
        storage_compatibility = 0.8
    else:
        # Incompatible storage (e.g. Cold medicine in Ambient zone)
        storage_compatibility = 0.0
        
    # 7. Location Available & Location Status
    if candidate_location.status == "ACTIVE":
        location_available = 1.0
        location_status = 1.0
    elif candidate_location.status == "RESTRICTED":
        location_available = 1.0
        location_status = 0.5
    else: # BLOCKED or MAINTENANCE
        location_available = 0.0
        location_status = 0.0
        
    # 8. Location Distance Proxy (difference in aisle/rack from expected location)
    if candidate_location.location_id == expected_loc:
        location_distance = 0.0
    elif inventory and candidate_location.zone == inventory.storage_requirement:
        location_distance = 1.0
    else:
        location_distance = 3.0
        
    # 9. Recent Activity Count
    recent_activity_count = float(len(scans_to_loc) + len(moves_to_loc))

    return {
        "scan_recency": scan_recency,
        "movement_recency": movement_recency,
        "movement_frequency": movement_frequency,
        "previous_location_match": previous_location_match,
        "pick_failure_signal": pick_failure_signal,
        "cycle_count_signal": cycle_count_signal,
        "quantity_match": quantity_match,
        "storage_compatibility": storage_compatibility,
        "location_available": location_available,
        "location_status": location_status,
        "location_distance": location_distance,
        "recent_activity_count": recent_activity_count
    }
