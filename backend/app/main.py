import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base, SessionLocal
from app.routers import (
    dashboard, discrepancies, scan_trails, locations, workers,
    assignments, experiments, edge_cases, validation, audit, auth, health, inventory
)
from app.models.models import LocationMaster

app = FastAPI(
    title="PharmaTrace API",
    description="Pharmaceutical Warehouse Inventory Location Discrepancy Finder Engine API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
            print("Database empty. Auto-executing seed database...")
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from scripts.seed_database import seed_database
            seed_database()
    except Exception as e:
        print(f"Startup check note: {e}")
    finally:
        db.close()

# Register API Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(inventory.router)
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

# Mount Single Host Link static assets and SPA fallback
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Exclude API routes and Swagger docs
        if full_path.startswith("api") or full_path in ["docs", "redoc", "openapi.json"]:
            return None
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
