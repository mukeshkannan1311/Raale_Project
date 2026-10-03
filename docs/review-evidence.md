# PharmaTrace - Project Review Evidence Document

This document provides concrete, empirically verified evidence of the implementation and validation of the **PharmaTrace Pharmaceutical Warehouse Inventory Discrepancy Finder**.

---

## 1. Database Evidence (Tables & ORM Models)
- **ORM Implementation**: `backend/app/models/models.py`
- **Supported Databases**: PostgreSQL (Production default) & SQLite (Zero-config local fallback)
- **14 Relational Models Implemented and Verified**:
  1. `Inventory` (`inventory` table) — SKU master, expected locations, batch, storage requirements
  2. `LocationMaster` (`location_master` table) — Zone, aisle, rack, temperature class, capacity, utilization, status, restricted flag
  3. `PutawayScan` (`putaway_scans` table) — Scan events, worker, destination location, timestamp
  4. `MoveEvent` (`move_events` table) — Relocation, unrecorded movements, source & destination
  5. `PickFailure` (`pick_failures` table) — Failed picking attempts, reported missing reason, worker ID
  6. `CycleCount` (`cycle_counts` table) — Counted vs system inventory quantities, variance
  7. `Worker` (`workers` table) — Role, active task count, workload limits, authorized zones, shift status
  8. `Driver` (`drivers` table) — Transit assignments and distance metrics
  9. `Prediction` (`predictions` table) — Historical model predictions, confidence scores, model name
  10. `Discrepancy` (`discrepancies` table) — Detected discrepancy lifecycle, SLA deadlines, candidate locations, transparent explanations, verified location, resolution status
  11. `Assignment` (`assignments` table) — Worker investigation tasks, workload utilization, fairness scores
  12. `User` (`users` table) — Role-based accounts: `ADMIN`, `WAREHOUSE_MANAGER`, `WORKER`
  13. `ValidationFeedback` (`validation_feedback` table) — Stakeholder rating surveys & reviews
  14. `AuditLog` (`audit_logs` table) — Immutable system governance and event log stream

---

## 2. Warehouse Data Sources & Generated Records
- **Data Generator**: `scripts/generate_data.py`
- **Seeding Pipeline**: `scripts/seed_database.py`
- **Verified Record Counts**:
  - Inventory Records: 110 SKUs
  - Warehouse Locations: 40 active bins across 5 storage zones (`COLD_STORAGE`, `CONTROLLED_ROOM`, `HAZARDOUS`, `HIGH_VALUE`, `RECEIVING_STAGING`)
  - Put-away Scans: 330 records
  - Move Events: 330 records
  - Pick Failures: 24 logged incidents
  - Cycle Counts: 54 audit counts
  - Warehouse Workers: 18 active workers across 4 roles (`PICKER`, `INSPECTOR`, `WAREHOUSE_LEAD`, `FORKLIFT_OPERATOR`)
  - Ground-Truth Discrepancies: 12 empirical test cases

---

## 3. Backend API Evidence
- **Framework**: FastAPI (Python 3.10 / 3.11)
- **Main Server File**: `backend/app/main.py`
- **Verified Endpoints**:
  - `GET  /api/health` — System health & version status
  - `POST /api/auth/login` — JWT authentication and role assignment
  - `GET  /api/auth/me` — Authenticated profile verification
  - `GET  /api/inventory` & `GET /api/inventory/{sku}` — Inventory catalog & batch details
  - `GET  /api/dashboard/summary` — Warehouse KPIs, zone counts, workload
  - `GET  /api/discrepancies` — List active discrepancy investigations
  - `POST /api/discrepancies/detect` — Trigger discrepancy scanning pipeline
  - `POST /api/discrepancies/{id}/resolve` — Physical verification & inventory correction
  - `POST /api/predict-location` — Multi-signal probabilistic location prediction
  - `GET  /api/predictions/{sku}` — Historical predictions for SKU
  - `GET  /api/scan-trail/{sku}` — Chronological multi-source scan timeline
  - `GET  /api/locations` & `GET /api/locations/{code}` — Warehouse bin map
  - `GET  /api/workers` — Worker availability, workload, and zone credentials
  - `POST /api/safety/check-assignment` — Real-time worker safety and fairness validation
  - `POST /api/assignments` — Safe worker dispatch
  - `POST /api/experiment/run` & `GET /api/experiment/results` — Empirical benchmark execution & metrics retrieval
  - `GET  /api/edge-cases/run` — 7 automated edge-case test runs
  - `POST /api/validation/feedback` — Qualitative evaluation ratings submission
  - `GET  /api/audit/logs` — Immutable audit trail

---

## 4. Authentication & Authorization Evidence
- **Implementation**: `backend/app/services/auth_service.py` & `backend/app/routers/auth.py`
- **Features Tested and Verified**:
  - Password hashing with SHA256 and secure salt
  - JWT creation (HS256 HMAC) with payload claims (`sub`, `role`, `name`, `exp`)
  - Signature validation & token decoding
  - Rejection of expired tokens (HTTP 401)
  - Rejection of tampered signatures & malformed tokens (HTTP 401)
  - Role-based access control via `require_roles("ADMIN", "MANAGER", "WORKER")`
  - Unauthorized access blocked (HTTP 403)

---

## 5. Automated Test Suite Evidence
- **Test File**: `backend/tests/test_pharmatrace.py`
- **Execution Command**: `pytest backend/tests/test_pharmatrace.py -v`
- **Results**: **11 Passed / 0 Failed (100% Pass Rate)**
  1. `test_database_models` — PASSED
  2. `test_baseline_service` — PASSED
  3. `test_prediction_engine` — PASSED
  4. `test_discrepancy_detection` — PASSED
  5. `test_safety_and_fairness` — PASSED
  6. `test_edge_cases_suite` — PASSED
  7. `test_password_hashing_and_verification` — PASSED
  8. `test_jwt_generation_and_verification` — PASSED
  9. `test_jwt_expired_and_invalid_tokens_rejected` — PASSED
  10. `test_role_based_authorization_permissions` — PASSED
  11. `test_api_endpoints_via_testclient` — PASSED

---

## 6. Empirical Experiment Results (Code-Generated)
- **Benchmark Script**: `scripts/run_experiment.py`
- **Artifact**: `data/processed/experiment_results.json`
- **Empirical Metrics**:
  - Ground-Truth Test Cases Evaluated: 12
  - **Baseline (Latest Known Location)**:
    - Top-1 Accuracy: **33.3%** (4/12 correct)
    - Average Locate Time: **36.0 minutes**
  - **PharmaTrace ML Prediction Engine**:
    - Top-1 Accuracy: **91.7%** (11/12 correct) — **+58.4% Absolute Improvement**
    - Top-3 Accuracy: **100.0%** (12/12 in Top-3)
    - Average Locate Time: **9.8 minutes** — **72.8% Time Saved**
    - Precision: **0.917**
    - Recall: **0.917**
    - F1-Score: **0.917**
    - False Positive Rate: **8.0%**
    - Missing-Stock Recovery Rate: **91.7%**

---

## 7. Safety & Fairness Rules Verification
- **Implementation**: `backend/app/services/safety_fairness.py`
- **Verified Invariants**:
  - **Worker Workload Limit**: Workers at or above `max_tasks` are strictly rejected.
  - **Zone Authorization**: Workers cannot be dispatched to zones outside their security clearance (`authorized_zones`).
  - **Restricted Location Protection**: Restricted vaults require `WAREHOUSE_LEAD` or `INSPECTOR` roles.
  - **Blocked Location Prohibition**: Inactive or quarantined bins cannot receive task dispatches.
  - **Cold Chain Compatibility**: Refrigerated medications cannot be assigned to ambient racks.
  - **Fairness Guarantee**: Workload balancing prioritizes eligible workers with the lowest current workload score.

---

## 8. Edge Case Robustness (7/7 Pass)
- **Harness**: `backend/app/services/edge_cases.py` (`GET /api/edge-cases/run`)
- **Verified Scenarios**:
  1. `Missing Scan Trail`: Gracefully falls back to expected master location with low confidence warning.
  2. `Conflicting Scan Events`: Analyzes chronological event credibility and ranks alternative candidates.
  3. `Blocked / Inactive Location`: Safety rule triggers rejection; alerts operator.
  4. `Wrong Storage Temperature`: Safety incompatibility flagged immediately; prevents drug degradation.
  5. `Quantity Mismatch Variance`: Flags physical inventory discrepancy and logs cycle count variance.
  6. `Worker Workload Exceeded`: Blocks dispatch; prompts supervisor for task rebalancing.
  7. `Unauthorized Zone Access`: Blocks worker entry; flags security event in audit logs.

---

## 9. Frontend Evidence
- **Framework**: React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons + Recharts
- **Build Status**: `npm run build` completed cleanly (`tsc && vite build` passed, 0 errors)
- **Verified Client Routes**:
  - `/dashboard` — Live warehouse metrics, discrepancy counts, worker workload widgets
  - `/discrepancies` — Interactive discrepancy finder, live prediction run, Top-3 candidates, transparent explanations, physical verification & resolve workflow
  - `/scan-trail` — Multi-source chronological event trail visualizer
  - `/warehouse` — Interactive 5-zone warehouse map with rack/bin utilization details
  - `/experiments` — Benchmark dashboard comparing Baseline (33.3%) vs PharmaTrace (91.7%)
  - `/edge-cases` — Live execution of the 7 edge-case test suites
  - `/safety` — Worker dispatch safety and workload fairness validator
  - `/validation` — Stakeholder survey evaluation and ratings module
  - `/audit` — Immutable system audit log viewer
  - `/deployment` — Deployment readiness checklist & architecture guide
  - `/login` — Role-based authentication interface

---

## 10. Containerization & Deployment
- **Configuration**: `docker-compose.yml`
- **Services Defined**:
  - `postgres`: PostgreSQL 15 Alpine on port 5432 with health check
  - `backend`: FastAPI Python 3.10-slim on port 8000 with PostgreSQL driver and seed data mount
  - `frontend`: Node 18 build multi-staged to Nginx Alpine on port 3000 with `/api/` reverse proxy
- **Single-command Launch**: `docker compose up --build`
