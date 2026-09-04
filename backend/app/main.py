import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.routers import (
    dashboard, discrepancies, scan_trails, locations, workers,
    assignments, experiments, edge_cases, validation, audit, health
)
from app.models.models import LocationMaster

app = FastAPI(
    title="PharmaTrace API",
    description="Pharmaceutical Warehouse Inventory Location Discrepancy Finder Engine",
    version="1.0.0"
)

# CORS configuration for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local Vite frontend during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure database tables exist on launch
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    # Auto-seed database if empty
    db = SessionLocal()
    try:
        count = db.query(LocationMaster).count()
        if count == 0:
            print("Database empty. Auto-executing seed script...")
            from seed import seed_all
            seed_all()
    except Exception as e:
        print(f"Startup check note: {e}")
    finally:
        db.close()

# Register Routers
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(discrepancies.router)
app.include_router(scan_trails.router)
app.include_router(locations.router)
app.include_router(workers.router)
app.include_router(assignments.router)
app.include_router(experiments.router)
app.include_router(edge_cases.router)
app.include_router(validation.router)
app.include_router(audit.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
