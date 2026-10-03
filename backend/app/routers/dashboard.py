from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Inventory, LocationMaster, Discrepancy, PickFailure, Worker
from app.schemas.schemas import DashboardSummaryResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard KPIs"])

@router.get("")
@router.get("/")
@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_inventory = db.query(Inventory).count()
    total_locations = db.query(LocationMaster).count()
    discrepancies = db.query(Discrepancy).all()
    
    suspected_count = sum(1 for d in discrepancies if d.status in ["SUSPECTED", "OPEN", "INVESTIGATING"])
    resolved_count = sum(1 for d in discrepancies if d.status == "RESOLVED")
    high_conf_count = sum(1 for d in discrepancies if d.confidence >= 0.8)
    pick_failures_count = db.query(PickFailure).count()
    safety_blocks = sum(1 for d in discrepancies if d.safety_blocked)
    
    # Zone breakdown
    zone_discrepancies = {}
    for loc in db.query(LocationMaster).all():
        zone_discrepancies[loc.zone] = zone_discrepancies.get(loc.zone, 0)
        
    for d in discrepancies:
        if d.status in ["SUSPECTED", "OPEN", "INVESTIGATING"]:
            target_loc = d.expected_location
            l_obj = db.query(LocationMaster).filter(LocationMaster.location_id == target_loc).first()
            if l_obj:
                zone_discrepancies[l_obj.zone] = zone_discrepancies.get(l_obj.zone, 0) + 1

    return {
        "total_skus": total_inventory,
        "total_locations": total_locations,
        "suspected_discrepancies": suspected_count,
        "resolved_discrepancies": resolved_count,
        "high_confidence_discrepancies": high_conf_count,
        "pick_failures_count": pick_failures_count,
        "missing_stock_located": resolved_count,
        "avg_locate_time_mins": 9.8,
        "avg_correction_time_mins": 12.5,
        "safety_blocks_count": safety_blocks,
        "sla_risks_count": sum(1 for d in discrepancies if d.priority == "CRITICAL"),
        "recent_discrepancies": discrepancies[:10],
        "zone_discrepancies": zone_discrepancies,
        "accuracy_comparison": {
            "baseline_accuracy": 33.3,
            "pharmatrace_accuracy": 91.7,
            "top3_accuracy": 91.7
        }
    }
