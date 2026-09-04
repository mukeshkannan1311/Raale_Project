from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Worker, Driver
from app.schemas.schemas import WorkerBase, DriverBase

router = APIRouter(prefix="/api/workers", tags=["Workers & Drivers"])

@router.get("", response_model=List[WorkerBase])
def list_workers(db: Session = Depends(get_db)):
    return db.query(Worker).all()

@router.get("/drivers", response_model=List[DriverBase])
def list_drivers(db: Session = Depends(get_db)):
    return db.query(Driver).all()
