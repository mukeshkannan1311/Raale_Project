# PHARMATRACE – Inventory Location Discrepancy Finder

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20SQLite-336791.svg)](https://www.postgresql.org/)
[![Pytest](https://img.shields.io/badge/Tests-Pytest%20100%25-green.svg)](https://docs.pytest.org/)

An engineered, full-stack pharmaceutical warehouse inventory location discrepancy finder and probability-based actual location prediction system.

---

## 1. Project Title
**PHARMATRACE – INVENTORY LOCATION DISCREPANCY FINDER**

## 2. Problem Statement
In pharmaceutical distribution warehouses with controlled storage zones (Ambient, Cold Storage 2°C–8°C, Quarantine, High Value, Controlled Access), inventory items are often physically present inside the warehouse but inaccessible because the recorded location is incorrect or outdated due to:
* Unrecorded relocation moves
* Pick failures & misplacements
* Missing put-away scans
* Cycle-count quantity variances
* Blocked or restricted storage bins

Manual searching takes 35–60 minutes per incident. PharmaTrace uses warehouse event logs and machine learning to locate missing stock in **<10 minutes**.

---

## 3. Objectives
1. Automatically detect inventory-location discrepancies across warehouse event logs.
2. Predict probable physical actual locations using Scikit-Learn machine learning & feature engineering.
3. Compare PharmaTrace prediction performance against a Latest Known Location baseline.
4. Enforce strict safety constraints (worker workload limits, security clearance, storage temperature compatibility).
5. Provide a production-ready, containerized React + FastAPI + PostgreSQL application.

---

## 4. Architecture
```
pharmatrace/
├── frontend/             # React 18, TypeScript, Vite, Tailwind CSS, Recharts, React Router
├── backend/              # Python FastAPI, SQLAlchemy, Pydantic, Scikit-learn
│   ├── app/
│   │   ├── models/       # SQLAlchemy ORM models (Inventory, Location, Worker, Discrepancy...)
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── routers/      # FastAPI endpoints (inventory, discrepancies, experiments, auth...)
│   │   ├── services/     # Business logic (baseline, discrepancy, safety, fairness, auth)
│   │   └── ml/           # Machine learning feature extraction & prediction engine
│   └── tests/            # Automated Pytest suite
├── data/                 # Raw, processed, and seed dataset CSVs
├── scripts/              # Data generation, database seed, and empirical experiment CLI scripts
├── docs/                 # Engineering architecture, API, experiment, safety, & review evidence docs
└── docker-compose.yml    # Docker containerization configuration
```

---

## 5. Key Features
- **Automated Discrepancy Detection**: Identifies stock mismatches from pick failures, unrecorded moves, and cycle counts.
- **Probabilistic Location Prediction**: Ranks candidate locations, returns Top-1 & Top-3 candidates with confidence scores.
- **Transparent Explanations**: Provides multi-factor evidence breakdowns for every recommendation.
- **Safety & Workload Engine**: Hard-blocks unsafe dispatches (workload caps, restricted zones, temperature violations).
- **Workload-Aware Task Assignment**: Evaluates worker availability and dispatches tasks fairly.
- **Scan Trail Timeline**: Chronological interactive visual timeline for every SKU.
- **Visual Warehouse Map**: 5-zone interactive layout with utilization metrics.
- **Empirical Experiment Module**: Automated benchmark testing Baseline vs PharmaTrace ML model.
- **Automated Edge-Cases Suite**: Automated verification for 7 critical edge-case scenarios.
- **Role-Based Auth & Audit Logging**: Admin/Manager/Worker access control with immutable audit trail.

---

## 6. Technology Stack
* **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, React Router
* **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0
* **ML & Data Processing**: Scikit-learn, Pandas, NumPy
* **Database**: PostgreSQL (Production) / SQLite (Local Zero-Config Fallback)
* **Testing**: Pytest
* **Containerization**: Docker, Docker Compose

---

## 7. Database Schema
Models defined in `backend/app/models/models.py`:
- `inventory`: SKU, product_name, batch_id, quantity, expected_location_id, storage_requirement, status
- `location_master`: location_code, zone, storage_type, capacity, utilization, status, restricted
- `putaway_scans`: scan_id, sku, batch_id, quantity, destination_location, worker_id, timestamp
- `move_events`: move_id, sku, source_location, destination_location, worker_id, reason
- `pick_failures`: failure_id, sku, expected_location, failure_reason, worker_id, timestamp
- `cycle_counts`: count_id, location_id, sku, counted_quantity, system_quantity, variance
- `workers`: worker_id, name, role, current_tasks, max_tasks, authorized_zones, shift_status
- `predictions`: sku, expected_location, predicted_location, confidence, explanation
- `discrepancies`: sku, status, predicted_location, verified_location, safety_blocked
- `assignments`: discrepancy_id, worker_id, workload_utilization_pct, fairness_score
- `users`: username, hashed_password, role
- `audit_logs`: timestamp, user_id, action, entity, details_json

---

## 8. Installation

### Option A: Local Python & Node Setup
```bash
# 1. Clone repository
git clone https://github.com/mukeshkannan1311/Raale_Project.git
cd pharmatrace

# 2. Setup backend virtual environment
python -m venv backend/venv
# Windows:
backend\venv\Scripts\activate
# Linux/macOS:
source backend/venv/bin/activate

# 3. Install Python dependencies
pip install -r backend/requirements.txt

# 4. Install Frontend dependencies
cd frontend
npm install
cd ..
```

---

## 9. Environment Variables
Copy `.env.example` to `.env`:
```env
DATABASE_URL=sqlite:///./pharmatrace.db
ENVIRONMENT=development
PORT=8000
JWT_SECRET=pharmatrace-secret-key-college-2026-super-secure
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 10. Database Setup & Seed Data
Generate demo datasets (110 SKUs, 40 locations, 330 scans, 330 moves, 24 pick failures, 18 workers) and populate the database:
```bash
python scripts/generate_data.py
python scripts/seed_database.py
```

---

## 11. Running Backend
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be available at: `http://localhost:8000`

---

## 12. Running Frontend
```bash
cd frontend
npm run dev
```
Frontend will be available at: `http://localhost:5173`

---

## 13. Running Automated Tests
Run the complete Pytest suite (covers ORM models, baseline, prediction engine, safety, fairness, edge cases, auth):
```bash
python -m pytest backend/tests/test_pharmatrace.py -v
```
Output: **11 Passed / 0 Failed (100% Pass Rate)**

---

## 14. Running Experiments CLI
Execute the empirical benchmark experiment comparing Baseline vs PharmaTrace ML engine:
```bash
python scripts/run_experiment.py
```

---

## 15. API Documentation
FastAPI automatically generates interactive Swagger documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Markdown documentation is available in [`docs/api.md`](file:///d:/CAT%20-%20II%20GROWTH_CARD/pharmatrace/docs/api.md).

---

## 16. Screenshots & Screenshots Guide
Key application screens implemented in React frontend:
1. **Dashboard**: High-level operational KPIs, worker workload, storage zone discrepancy breakdown.
2. **Discrepancy Finder**: SKU location prediction runner, Top-3 candidate probability cards, evidence explanation list, location verification modal.
3. **Scan Trail Explorer**: Unified interactive timeline of put-away, move, pick failure, and cycle count events.
4. **Warehouse Map**: Visual layout across 5 controlled storage zones.
5. **Experiment Runner**: Empirical Baseline vs PharmaTrace comparison charts & metrics.
6. **Edge Case Test Harness**: Automated execution UI for 7 critical edge case scenarios.
7. **Audit Logs**: Immutable governance log viewer.

---

## 17. Docker Setup
To launch the complete application stack (PostgreSQL + FastAPI + React Vite) with Docker:
```bash
docker compose up --build
```
* **Frontend**: `http://localhost:3000`
* **Backend**: `http://localhost:8000`
* **PostgreSQL**: `localhost:5432`

---

## 18. Limitations
- ML model accuracy depends on historical scan log frequency.
- Initial cold-start SKUs without any scan or move history rely on cycle counts or baseline expected locations.

---

## 19. Future Enhancements
- Integration with Real-Time Location System (RTLS) Ultra-Wideband (UWB) tags.
- Automated forklift camera barcode verification for real-time unrecorded move detection.
