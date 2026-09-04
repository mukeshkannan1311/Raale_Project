from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import PutawayScan, MoveEvent, PickFailure, CycleCount

router = APIRouter(prefix="/api/scan-trails", tags=["Scan Trails"])

@router.get("/{sku}")
def get_scan_trail(sku: str, db: Session = Depends(get_db)):
    putaways = db.query(PutawayScan).filter(PutawayScan.sku == sku).all()
    moves = db.query(MoveEvent).filter(MoveEvent.sku == sku).all()
    failures = db.query(PickFailure).filter(PickFailure.sku == sku).all()
    counts = db.query(CycleCount).filter(CycleCount.sku == sku).all()

    timeline = []

    for p in putaways:
        timeline.append({
            "id": p.scan_id,
            "event_type": "PUT_AWAY",
            "timestamp": p.timestamp,
            "location": p.to_location,
            "worker_id": p.worker_id,
            "quantity": p.quantity,
            "details": f"Put-away scan from {p.from_location} to {p.to_location}",
            "suspicious": False
        })

    for m in moves:
        timeline.append({
            "id": m.move_id,
            "event_type": "MOVE_EVENT",
            "timestamp": m.timestamp,
            "location": m.destination_location,
            "worker_id": m.worker_id,
            "quantity": m.quantity,
            "details": f"Move event ({m.reason}) from {m.source_location} to {m.destination_location}",
            "suspicious": m.reason == "UNRECORDED_MOVE"
        })

    for f in failures:
        timeline.append({
            "id": f.failure_id,
            "event_type": "PICK_FAILURE",
            "timestamp": f.timestamp,
            "location": f.expected_location,
            "worker_id": f.worker_id,
            "quantity": 0,
            "details": f"Pick failure reported at {f.expected_location} ({f.failure_reason})",
            "suspicious": True
        })

    for c in counts:
        timeline.append({
            "id": c.count_id,
            "event_type": "CYCLE_COUNT",
            "timestamp": c.timestamp,
            "location": c.location_id,
            "worker_id": c.worker_id,
            "quantity": c.counted_quantity,
            "details": f"Cycle count: {c.counted_quantity} counted vs {c.system_quantity} system (variance: {c.variance})",
            "suspicious": c.variance != 0
        })

    # Sort chronologically ascending
    timeline.sort(key=lambda x: x["timestamp"])

    return {
        "sku": sku,
        "total_events": len(timeline),
        "timeline": timeline
    }
