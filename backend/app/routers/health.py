from fastapi import APIRouter

router = APIRouter(tags=["Health Check"])

@router.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PharmaTrace Discrepancy Finder Engine",
        "version": "1.0.0"
    }
