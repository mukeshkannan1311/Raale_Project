from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from app.database import Base

class LocationMaster(Base):
    __tablename__ = "location_master"

    location_id = Column(String, primary_key=True, index=True)
    zone = Column(String, index=True) # AMBIENT, COLD_STORAGE, QUARANTINE, HIGH_VALUE, CONTROLLED_ACCESS
    aisle = Column(String)
    rack = Column(String)
    temperature_class = Column(String) # AMBIENT_20C, COLD_4C, FROZEN_20C, CONTROLLED_15C
    capacity = Column(Integer)
    current_utilization = Column(Integer, default=0)
    status = Column(String, default="ACTIVE") # ACTIVE, BLOCKED, RESTRICTED, MAINTENANCE
    restricted = Column(Boolean, default=False)
    allowed_product_type = Column(String) # GENERAL, VACCINE, CONTROLLED_SUBSTANCE, BIOLOGIC, HAZARDOUS

class PutawayScan(Base):
    __tablename__ = "putaway_scans"

    scan_id = Column(String, primary_key=True, index=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True)
    quantity = Column(Integer)
    from_location = Column(String)
    to_location = Column(String, index=True)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    zone = Column(String)

class MoveEvent(Base):
    __tablename__ = "move_events"

    move_id = Column(String, primary_key=True, index=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True)
    quantity = Column(Integer)
    source_location = Column(String)
    destination_location = Column(String, index=True)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    reason = Column(String) # UNRECORDED_MOVE, RELOCATION, REPLENISHMENT, ISOLATION

class PickFailure(Base):
    __tablename__ = "pick_failures"

    failure_id = Column(String, primary_key=True, index=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True)
    expected_location = Column(String, index=True)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    failure_reason = Column(String) # NOT_FOUND, WRONG_SKU, DAMAGED_STOCK, EXPIRED

class CycleCount(Base):
    __tablename__ = "cycle_counts"

    count_id = Column(String, primary_key=True, index=True)
    location_id = Column(String, index=True)
    sku = Column(String, index=True)
    counted_quantity = Column(Integer)
    system_quantity = Column(Integer)
    variance = Column(Integer)
    worker_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Worker(Base):
    __tablename__ = "workers"

    worker_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String) # PICKER, INSPECTOR, WAREHOUSE_LEAD, FORKLIFT_OPERATOR
    current_tasks = Column(Integer, default=0)
    max_tasks = Column(Integer, default=5)
    current_distance = Column(Float, default=0.0) # km
    max_distance = Column(Float, default=10.0) # km
    shift_status = Column(String, default="ACTIVE") # ACTIVE, ON_BREAK, OFF_SHIFT
    zone_authorization = Column(String) # Comma-separated zones e.g. "AMBIENT,COLD_STORAGE,CONTROLLED_ACCESS"

class Driver(Base):
    __tablename__ = "drivers"

    driver_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    current_assignments = Column(Integer, default=0)
    max_assignments = Column(Integer, default=8)
    route_distance = Column(Float, default=0.0)
    max_route_distance = Column(Float, default=50.0)
    shift_status = Column(String, default="ACTIVE")

class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id = Column(String, primary_key=True, index=True)
    sku = Column(String, index=True)
    batch_id = Column(String, index=True)
    quantity = Column(Integer)
    expected_location = Column(String)
    predicted_location = Column(String)
    baseline_location = Column(String)
    confidence = Column(Float)
    priority = Column(String) # CRITICAL, HIGH, MEDIUM, LOW
    sla_deadline = Column(DateTime)
    status = Column(String, default="SUSPECTED") # SUSPECTED, LOCATED, CORRECTED, MISSING, BLOCKED
    evidence_json = Column(JSON) # Detailed breakdown of evidence items
    candidates_json = Column(JSON) # List of candidate locations with prob, evidence, valid flag
    safety_blocked = Column(Boolean, default=False)
    safety_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String, primary_key=True, index=True)
    discrepancy_id = Column(String, ForeignKey("discrepancies.id"))
    worker_id = Column(String, ForeignKey("workers.worker_id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    fairness_score = Column(Float, default=0.0)
    workload_utilization_pct = Column(Float, default=0.0)
    note = Column(String, nullable=True)

class ValidationFeedback(Base):
    __tablename__ = "validation_feedback"

    id = Column(String, primary_key=True, index=True)
    user_role = Column(String, default="WAREHOUSE_OPERATOR")
    ease_of_understanding = Column(Integer) # 1-5
    usefulness_rating = Column(Integer)     # 1-5
    evidence_clarity = Column(Integer)      # 1-5
    workflow_safety = Column(Integer)       # 1-5
    search_time_reduction = Column(Integer) # 1-5
    overall_rating = Column(Integer)        # 1-5
    comments = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String) # PREDICTION_GENERATED, VERIFY_LOCATION, MARK_CORRECTED, REPORT_MISSING, ASSIGNMENT_CREATED, SAFETY_BLOCK
    sku = Column(String)
    location_id = Column(String, nullable=True)
    worker_id = Column(String, nullable=True)
    details_json = Column(JSON, nullable=True)
