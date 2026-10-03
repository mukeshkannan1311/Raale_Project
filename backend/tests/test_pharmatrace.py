import os
import sys
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.models.models import (
    Inventory, LocationMaster, Worker, PutawayScan, MoveEvent, PickFailure,
    CycleCount, Discrepancy, Assignment, User, AuditLog
)
from app.services.baseline_service import get_baseline_prediction
from app.ml.prediction_engine import predict_actual_location
from app.services.discrepancy_service import detect_all_discrepancies
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.services.safety_fairness import SafetyFairnessService
from app.services.edge_cases import EdgeCasesService
from app.services.auth_service import (
    hash_password, verify_password, create_access_token, decode_token,
    require_roles, get_current_user
)

from sqlalchemy.pool import StaticPool

# Use SQLite in-memory for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed test data
        loc1 = LocationMaster(
            location_id="COLD-A01-R01-B01",
            location_code="COLD-A01-R01-B01",
            zone="COLD_STORAGE",
            aisle="A01",
            rack="R01",
            bin_number="B01",
            temperature_class="COLD_4C",
            storage_type="COLD_VAULT",
            capacity=100,
            current_utilization=20,
            status="ACTIVE",
            restricted=False,
            allowed_product_type="VACCINE"
        )
        loc2 = LocationMaster(
            location_id="COLD-A01-R01-B02",
            location_code="COLD-A01-R01-B02",
            zone="COLD_STORAGE",
            aisle="A01",
            rack="R01",
            bin_number="B02",
            temperature_class="COLD_4C",
            storage_type="COLD_VAULT",
            capacity=100,
            current_utilization=30,
            status="ACTIVE",
            restricted=False,
            allowed_product_type="VACCINE"
        )
        loc_ambient = LocationMaster(
            location_id="AMBI-A01-R01-B01",
            location_code="AMBI-A01-R01-B01",
            zone="AMBIENT",
            aisle="A01",
            rack="R01",
            bin_number="B01",
            temperature_class="AMBIENT_20C",
            storage_type="SHELF",
            capacity=200,
            current_utilization=50,
            status="ACTIVE",
            restricted=False,
            allowed_product_type="GENERAL"
        )
        loc_blocked = LocationMaster(
            location_id="COLD-BLOCKED-B99",
            location_code="COLD-BLOCKED-B99",
            zone="COLD_STORAGE",
            aisle="A01",
            rack="R01",
            bin_number="B99",
            temperature_class="COLD_4C",
            storage_type="COLD_VAULT",
            capacity=100,
            current_utilization=0,
            status="BLOCKED",
            restricted=True,
            allowed_product_type="VACCINE"
        )
        db.add_all([loc1, loc2, loc_ambient, loc_blocked])

        inv = Inventory(
            id="INV-TEST-001",
            sku="MED-TEST-100",
            product_name="Test Insulin Vaccine",
            batch_id="BAT-TEST-01",
            quantity=50,
            expected_location_id="COLD-A01-R01-B01",
            storage_requirement="COLD_STORAGE",
            status="AVAILABLE"
        )
        db.add(inv)

        wrk1 = Worker(
            worker_id="WRK-TEST-01",
            name="Alex Test",
            role="PICKER",
            current_tasks=1,
            max_tasks=5,
            current_distance=2.0,
            max_distance=10.0,
            shift_status="ACTIVE",
            authorized_zones="COLD_STORAGE,AMBIENT",
            zone_authorization="COLD_STORAGE,AMBIENT"
        )
        wrk_full = Worker(
            worker_id="WRK-TEST-BUSY",
            name="Busy Bob",
            role="PICKER",
            current_tasks=5,
            max_tasks=5,
            shift_status="ACTIVE",
            authorized_zones="COLD_STORAGE,AMBIENT",
            zone_authorization="COLD_STORAGE,AMBIENT"
        )
        db.add_all([wrk1, wrk_full])

        # Add unrecorded move event to loc2
        move = MoveEvent(
            move_id="MOV-TEST-01",
            sku="MED-TEST-100",
            batch_id="BAT-TEST-01",
            quantity=50,
            source_location="COLD-A01-R01-B01",
            destination_location="COLD-A01-R01-B02",
            worker_id="WRK-TEST-01",
            timestamp=datetime.utcnow(),
            reason="UNRECORDED_MOVE"
        )
        db.add(move)

        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_database_models(db_session):
    inv = db_session.query(Inventory).filter(Inventory.sku == "MED-TEST-100").first()
    assert inv is not None
    assert inv.storage_requirement == "COLD_STORAGE"

def test_baseline_service(db_session):
    baseline = get_baseline_prediction(db_session, "MED-TEST-100")
    assert baseline["baseline_predicted_location"] == "COLD-A01-R01-B02"

def test_prediction_engine(db_session):
    pred = predict_actual_location(db_session, "MED-TEST-100")
    assert pred["predicted_location"] == "COLD-A01-R01-B02"
    assert pred["confidence"] >= 0.4
    assert len(pred["top_candidates"]) > 0

def test_discrepancy_detection(db_session):
    pf = PickFailure(
        failure_id="FAIL-TEST-01",
        sku="MED-TEST-100",
        batch_id="BAT-TEST-01",
        expected_location="COLD-A01-R01-B01",
        worker_id="WRK-TEST-01",
        timestamp=datetime.utcnow(),
        failure_reason="NOT_FOUND"
    )
    db_session.add(pf)
    db_session.commit()

    discs = detect_all_discrepancies(db_session)
    assert len(discs) > 0
    assert discs[0].sku == "MED-TEST-100"

def test_safety_and_fairness(db_session):
    worker = db_session.query(Worker).filter(Worker.worker_id == "WRK-TEST-01").first()
    loc_cold = db_session.query(LocationMaster).filter(LocationMaster.location_id == "COLD-A01-R01-B01").first()
    loc_blocked = db_session.query(LocationMaster).filter(LocationMaster.location_id == "COLD-BLOCKED-B99").first()
    disc = Discrepancy(id="D1", sku="MED-TEST-100", expected_location="COLD-A01-R01-B01")

    # 1. Active worker in authorized zone -> Safe
    safe, reason = SafetyFairnessService.validate_worker_safety(worker, loc_cold, disc)
    assert safe is True

    # 2. Blocked location -> Reject
    safe, reason = SafetyFairnessService.validate_worker_safety(worker, loc_blocked, disc)
    assert safe is False
    assert "BLOCKED" in reason

    # 3. Workload limit exceeded -> Reject
    worker_busy = db_session.query(Worker).filter(Worker.worker_id == "WRK-TEST-BUSY").first()
    safe, reason = SafetyFairnessService.validate_worker_safety(worker_busy, loc_cold, disc)
    assert safe is False
    assert "maximum task capacity" in reason

def test_edge_cases_suite(db_session):
    edge_results = EdgeCasesService.run_all_edge_cases(db_session)
    assert len(edge_results) == 7
    for r in edge_results:
        assert r["status"] == "PASS"

def test_password_hashing_and_verification():
    raw_pass = "SecureWarehouse2026!"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_generation_and_verification():
    data = {"sub": "warehouse_mgr", "role": "MANAGER", "name": "Jane Manager"}
    token = create_access_token(data, expires_delta=timedelta(hours=2))
    payload = decode_token(token)
    assert payload["sub"] == "warehouse_mgr"
    assert payload["role"] == "MANAGER"
    assert payload["name"] == "Jane Manager"
    assert "exp" in payload

def test_jwt_expired_and_invalid_tokens_rejected():
    # 1. Expired token
    expired_token = create_access_token({"sub": "expired_user", "role": "WORKER"}, expires_delta=timedelta(seconds=-10))
    with pytest.raises(HTTPException) as exc_info:
        decode_token(expired_token)
    assert exc_info.value.status_code == 401
    assert "expired" in str(exc_info.value.detail).lower()

    # 2. Tampered signature
    parts = expired_token.split(".")
    tampered_token = f"{parts[0]}.{parts[1]}.corrupted_signature_xyz"
    with pytest.raises(HTTPException) as exc_info:
        decode_token(tampered_token)
    assert exc_info.value.status_code == 401

    # 3. Malformed token structure
    with pytest.raises(HTTPException) as exc_info:
        decode_token("not-a-real-token")
    assert exc_info.value.status_code == 401

def test_role_based_authorization_permissions():
    admin_user = User(id="U1", username="admin_user", role="ADMIN")
    mgr_user = User(id="U2", username="mgr_user", role="MANAGER")
    worker_user = User(id="U3", username="worker_user", role="WORKER")

    # ADMIN access
    admin_checker = require_roles("ADMIN")
    assert admin_checker(admin_user).role == "ADMIN"
    with pytest.raises(HTTPException) as exc:
        admin_checker(worker_user)
    assert exc.value.status_code == 403

    # Multi-role permission check (e.g. ADMIN or MANAGER)
    elevated_checker = require_roles("ADMIN", "MANAGER")
    assert elevated_checker(admin_user).role == "ADMIN"
    assert elevated_checker(mgr_user).role == "MANAGER"
    with pytest.raises(HTTPException) as exc:
        elevated_checker(worker_user)
    assert exc.value.status_code == 403

    # Worker role permission check
    worker_checker = require_roles("WORKER")
    assert worker_checker(worker_user).role == "WORKER"

def test_api_endpoints_via_testclient(db_session):
    admin_user = User(
        id="USR-TEST-001",
        username="admin",
        name="Warehouse Admin",
        hashed_password=hash_password("admin123"),
        role="ADMIN"
    )
    db_session.add(admin_user)
    db_session.commit()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        # 1. Health check
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"].lower() == "healthy"

        # 2. Login with valid demo credentials
        login_resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # 3. Authenticated endpoint
        me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == "admin"
        assert me_resp.json()["role"] == "ADMIN"

        # 4. Login with invalid password
        bad_resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword123"})
        assert bad_resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


