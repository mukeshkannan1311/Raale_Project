from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
def health_check():
    return {
        "status": "healthy",
        "service": "PharmaTrace Backend API",
        "timestamp": datetime.utcnow().isoformat()
    }
