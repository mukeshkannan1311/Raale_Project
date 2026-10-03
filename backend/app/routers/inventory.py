from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Inventory
from app.schemas.schemas import InventoryBase

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryBase])
def get_all_inventory(
    status: Optional[str] = None,
    storage_requirement: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Inventory)
    if status:
        query = query.filter(Inventory.status == status)
    if storage_requirement:
        query = query.filter(Inventory.storage_requirement == storage_requirement)
    if search:
        query = query.filter(
            (Inventory.sku.ilike(f"%{search}%")) | (Inventory.product_name.ilike(f"%{search}%"))
        )
    return query.all()

@router.get("/{sku}", response_model=InventoryBase)
def get_inventory_by_sku(sku: str, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.sku == sku).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Inventory item with SKU '{sku}' not found.")
    return item
