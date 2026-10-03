from typing import Dict, List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import EdgeCaseSuiteResponse
from app.services.edge_cases import EdgeCasesService

router = APIRouter(prefix="/api/edge-cases", tags=["Automated Edge Cases"])

@router.get("", response_model=EdgeCaseSuiteResponse)
@router.get("/", response_model=EdgeCaseSuiteResponse)
@router.get("/run", response_model=EdgeCaseSuiteResponse)
@router.post("/run", response_model=EdgeCaseSuiteResponse)
def run_edge_cases_suite(db: Session = Depends(get_db)):
    results = EdgeCasesService.run_all_edge_cases(db)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    return {
        "results": results,
        "total_passed": passed,
        "total_failed": failed
    }
