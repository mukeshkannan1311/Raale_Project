from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Worker, Driver
from app.schemas.schemas import WorkerBase

router = APIRouter(prefix="/api/workers", tags=["Workers"])

@router.get("/drivers")
def get_all_drivers(db: Session = Depends(get_db)):
    drivers = db.query(Driver).all()
    return drivers

@router.get("", response_model=List[WorkerBase])
def get_all_workers(
    shift: Optional[str] = None,
    shift_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Worker)
    if shift:
        query = query.filter(Worker.shift == shift)
    if shift_status:
        query = query.filter(Worker.shift_status == shift_status)
    return query.all()

@router.get("/{worker_id}", response_model=WorkerBase)
def get_worker_by_id(worker_id: str, db: Session = Depends(get_db)):
    w = db.query(Worker).filter(Worker.worker_id == worker_id).first()
    if not w:
        raise HTTPException(status_code=404, detail=f"Worker with ID '{worker_id}' not found.")
    return w
