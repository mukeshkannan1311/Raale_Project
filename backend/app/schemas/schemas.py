from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class LocationMasterBase(BaseModel):
    location_id: str
    zone: str
    aisle: str
    rack: str
    temperature_class: str
    capacity: int
    current_utilization: int
    status: str
    restricted: bool
    allowed_product_type: str

    class Config:
        from_attributes = True

class PutawayScanBase(BaseModel):
    scan_id: str
    sku: str
    batch_id: str
    quantity: int
    from_location: str
    to_location: str
    worker_id: str
    timestamp: datetime
    zone: str

    class Config:
        from_attributes = True

class MoveEventBase(BaseModel):
    move_id: str
    sku: str
    batch_id: str
    quantity: int
    source_location: str
    destination_location: str
    worker_id: str
    timestamp: datetime
    reason: str

    class Config:
        from_attributes = True

class PickFailureBase(BaseModel):
    failure_id: str
    sku: str
    batch_id: str
    expected_location: str
    worker_id: str
    timestamp: datetime
    failure_reason: str

    class Config:
        from_attributes = True

class CycleCountBase(BaseModel):
    count_id: str
    location_id: str
    sku: str
    counted_quantity: int
    system_quantity: int
    variance: int
    worker_id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class WorkerBase(BaseModel):
    worker_id: str
    name: str
    role: str
    current_tasks: int
    max_tasks: int
    current_distance: float
    max_distance: float
    shift_status: str
    zone_authorization: str

    class Config:
        from_attributes = True

class DriverBase(BaseModel):
    driver_id: str
    name: str
    current_assignments: int
    max_assignments: int
    route_distance: float
    max_route_distance: float
    shift_status: str

    class Config:
        from_attributes = True

class EvidenceItem(BaseModel):
    factor: str
    impact: str # e.g. "+32%" or "-15%"
    description: str

class CandidateLocation(BaseModel):
    location_id: str
    probability: float
    evidence_summary: str
    is_valid: bool
    rejection_reason: Optional[str] = None
    zone: str
    temperature_class: str

class DiscrepancyResponse(BaseModel):
    id: str
    sku: str
    batch_id: str
    quantity: int
    expected_location: str
    predicted_location: str
    baseline_location: str
    confidence: float
    priority: str
    sla_deadline: datetime
    status: str
    evidence_json: List[EvidenceItem]
    candidates_json: List[CandidateLocation]
    safety_blocked: bool
    safety_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DiscrepancyActionRequest(BaseModel):
    notes: Optional[str] = None
    actual_verified_location: Optional[str] = None

class AssignmentCreateRequest(BaseModel):
    discrepancy_id: str
    worker_id: str
    note: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: str
    discrepancy_id: str
    worker_id: str
    assigned_at: datetime
    status: str
    fairness_score: float
    workload_utilization_pct: float
    note: Optional[str] = None

    class Config:
        from_attributes = True

class ValidationFeedbackCreate(BaseModel):
    user_role: str = "WAREHOUSE_OPERATOR"
    ease_of_understanding: int = Field(..., ge=1, le=5)
    usefulness_rating: int = Field(..., ge=1, le=5)
    evidence_clarity: int = Field(..., ge=1, le=5)
    workflow_safety: int = Field(..., ge=1, le=5)
    search_time_reduction: int = Field(..., ge=1, le=5)
    overall_rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None

class ValidationFeedbackResponse(ValidationFeedbackCreate):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ExperimentMetrics(BaseModel):
    location_accuracy: float
    top1_accuracy: float
    top3_accuracy: float
    false_positive_rate: float
    avg_locate_time_mins: float
    avg_correction_time_mins: float
    missing_stock_located_pct: float
    percentage_corrected: float
    unsafe_assignment_count: int
    worker_workload_violations: int

class ExperimentComparisonResponse(BaseModel):
    baseline: ExperimentMetrics
    target: ExperimentMetrics
    prototype: ExperimentMetrics
    improvement_pct: Dict[str, float]
    error_analysis: List[Dict[str, Any]]

class EdgeCaseTestResult(BaseModel):
    case_name: str
    sku: str
    input_description: str
    expected_behavior: str
    actual_behavior: str
    status: str # PASS or FAIL
    details: Dict[str, Any]

class EdgeCaseSuiteResponse(BaseModel):
    results: List[EdgeCaseTestResult]
    total_passed: int
    total_failed: int

class DashboardSummaryResponse(BaseModel):
    total_skus: int
    suspected_discrepancies: int
    high_confidence_discrepancies: int
    missing_stock_located: int
    avg_locate_time_mins: float
    avg_correction_time_mins: float
    safety_blocks_count: int
    sla_risks_count: int
    recent_discrepancies: List[DiscrepancyResponse]
    zone_discrepancies: Dict[str, int]
    accuracy_comparison: Dict[str, float]
