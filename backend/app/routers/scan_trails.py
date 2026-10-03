from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Inventory
from app.services.data_pipeline import build_inventory_scan_trail

router = APIRouter(tags=["Scan Trail Timeline"])

@router.get("/api/scan-trail/{sku}")
@router.get("/api/scan-trails/{sku}")
def get_scan_trail_by_sku(sku: str, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.sku == sku).first()
    if not inventory:
        raise HTTPException(status_code=404, detail=f"SKU '{sku}' not found in inventory master.")
        
    events = build_inventory_scan_trail(db, sku)
    return {
        "sku": sku,
        "product_name": inventory.product_name,
        "expected_location": inventory.expected_location_id,
        "storage_requirement": inventory.storage_requirement,
        "status": inventory.status,
        "events_count": len(events),
        "events": events
    }
