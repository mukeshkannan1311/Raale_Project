from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    product_name = Column(String, index=True)
    batch_id = Column(String, index=True)
    quantity = Column(Integer)
    expected_location_id = Column(String, index=True)
    storage_requirement = Column(String, index=True) # AMBIENT, COLD_STORAGE, QUARANTINE, HIGH_VALUE, CONTROLLED_ACCESS
    status = Column(String, default="AVAILABLE") # AVAILABLE, DISCREPANT, QUARANTINED, IN_TRANSIT, RESERVED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LocationMaster(Base):
    __tablename__ = "location_master"

    location_id = Column(String, primary_key=True, index=True)
    location_code = Column(String, unique=True, index=True)
    zone = Column(String, index=True) # AMBIENT, COLD_STORAGE, QUARANTINE, HIGH_VALUE, CONTROLLED_ACCESS
    aisle = Column(String)
    rack = Column(String)
    bin_number = Column(String, nullable=True)
    temperature_class = Column(String) # AMBIENT_20C, COLD_4C, FROZEN_20C, CONTROLLED_15C
    storage_type = Column(String) # PALLET, SHELF, COLD_VAULT, SECURE_BIN
    capacity = Column(Integer)
    current_utilization = Column(Integer, default=0)
    status = Column(String, default="ACTIVE") # ACTIVE, BLOCKED, RESTRICTED, MAINTENANCE
    restricted = Column(Boolean, default=False)
    allowed_product_type = Column(String) # GENERAL, VACCINE, CONTROLLED_SUBSTANCE, BIOLOGIC, HAZARDOUS

class PutawayScan(Base):
    __tablename__ = "putaway_scans"

    scan_id = Column(String, primary_key=True, index=True)
    id = Column(String, nullable=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True)
    quantity = Column(Integer)
    source_location = Column(String)
    destination_location = Column(String, index=True)
    from_location = Column(String, nullable=True)
    to_location = Column(String, nullable=True)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    zone = Column(String, nullable=True)

class MoveEvent(Base):
    __tablename__ = "move_events"

    move_id = Column(String, primary_key=True, index=True)
    id = Column(String, nullable=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True)
    quantity = Column(Integer, default=1)
    source_location = Column(String)
    destination_location = Column(String, index=True)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    reason = Column(String) # UNRECORDED_MOVE, RELOCATION, REPLENISHMENT, ISOLATION

class PickFailure(Base):
    __tablename__ = "pick_failures"

    failure_id = Column(String, primary_key=True, index=True)
    id = Column(String, nullable=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True)
    expected_location = Column(String, index=True)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    failure_reason = Column(String) # NOT_FOUND, WRONG_SKU, DAMAGED_STOCK, EXPIRED

class CycleCount(Base):
    __tablename__ = "cycle_counts"

    count_id = Column(String, primary_key=True, index=True)
    id = Column(String, nullable=True)
    location_id = Column(String, index=True)
    sku = Column(String, index=True)
    counted_quantity = Column(Integer)
    actual_quantity = Column(Integer, nullable=True)
    system_quantity = Column(Integer)
    variance = Column(Integer)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Worker(Base):
    __tablename__ = "workers"

    worker_id = Column(String, primary_key=True, index=True)
    id = Column(String, nullable=True)
    name = Column(String)
    worker_name = Column(String, nullable=True)
    role = Column(String) # PICKER, INSPECTOR, WAREHOUSE_LEAD, FORKLIFT_OPERATOR
    shift = Column(String, default="DAY_SHIFT")
    current_tasks = Column(Integer, default=0)
    max_tasks = Column(Integer, default=5)
    current_distance = Column(Float, default=0.0) # km
    max_distance = Column(Float, default=10.0) # km
    shift_status = Column(String, default="ACTIVE")
    status = Column(String, default="ACTIVE")
    authorized_zones = Column(String)
    zone_authorization = Column(String, nullable=True)

class Driver(Base):
    __tablename__ = "drivers"

    driver_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    current_assignments = Column(Integer, default=0)
    max_assignments = Column(Integer, default=8)
    route_distance = Column(Float, default=0.0)
    max_route_distance = Column(Float, default=50.0)
    shift_status = Column(String, default="ACTIVE")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, index=True)
    sku = Column(String, index=True)
    expected_location = Column(String)
    predicted_location = Column(String)
    confidence = Column(Float)
    model_name = Column(String, default="PharmaTrace Probability Engine")
    explanation = Column(JSON)
    top_candidates = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id = Column(String, primary_key=True, index=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True, nullable=True)
    quantity = Column(Integer, default=1)
    expected_location = Column(String)
    predicted_location = Column(String)
    verified_location = Column(String, nullable=True)
    baseline_location = Column(String, nullable=True)
    confidence = Column(Float)
    priority = Column(String, default="HIGH")
    sla_deadline = Column(DateTime, nullable=True)
    status = Column(String, default="OPEN")
    correction_status = Column(String, default="PENDING")
    evidence_json = Column(JSON, nullable=True)
    candidates_json = Column(JSON, nullable=True)
    safety_blocked = Column(Boolean, default=False)
    safety_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String, primary_key=True, index=True)
    discrepancy_id = Column(String, ForeignKey("discrepancies.id"))
    worker_id = Column(String, ForeignKey("workers.worker_id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="PENDING")
    fairness_score = Column(Float, default=0.0)
    workload_utilization_pct = Column(Float, default=0.0)
    note = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="WAREHOUSE_MANAGER")
    created_at = Column(DateTime, default=datetime.utcnow)

class ValidationFeedback(Base):
    __tablename__ = "validation_feedback"

    id = Column(String, primary_key=True, index=True)
    user_role = Column(String, default="WAREHOUSE_OPERATOR")
    ease_of_understanding = Column(Integer)
    usefulness_rating = Column(Integer)
    evidence_clarity = Column(Integer)
    workflow_safety = Column(Integer)
    search_time_reduction = Column(Integer)
    overall_rating = Column(Integer)
    comments = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True)
    action = Column(String)
    event_type = Column(String, nullable=True)
    entity = Column(String, nullable=True)
    sku = Column(String, nullable=True)
    location_id = Column(String, nullable=True)
    worker_id = Column(String, nullable=True)
    details_json = Column(JSON, nullable=True)
