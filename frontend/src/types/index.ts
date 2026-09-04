export interface EvidenceItem {
  factor: string;
  impact: string;
  description: string;
}

export interface CandidateLocation {
  location_id: string;
  probability: number;
  evidence_summary: string;
  is_valid: boolean;
  rejection_reason?: string;
  zone: string;
  temperature_class: string;
}

export interface Discrepancy {
  id: string;
  sku: string;
  batch_id: string;
  quantity: number;
  expected_location: string;
  predicted_location: string;
  baseline_location: string;
  confidence: number;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  sla_deadline: string;
  status: 'SUSPECTED' | 'LOCATED' | 'CORRECTED' | 'MISSING' | 'IN_PROGRESS' | 'BLOCKED';
  evidence_json: EvidenceItem[];
  candidates_json: CandidateLocation[];
  safety_blocked: boolean;
  safety_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface LocationMaster {
  location_id: string;
  zone: string;
  aisle: string;
  rack: string;
  temperature_class: string;
  capacity: number;
  current_utilization: number;
  status: string;
  restricted: boolean;
  allowed_product_type: string;
}

export interface Worker {
  worker_id: string;
  name: string;
  role: string;
  current_tasks: number;
  max_tasks: number;
  current_distance: number;
  max_distance: number;
  shift_status: 'ACTIVE' | 'ON_BREAK' | 'OFF_SHIFT';
  zone_authorization: string;
}

export interface Driver {
  driver_id: string;
  name: string;
  current_assignments: number;
  max_assignments: number;
  route_distance: number;
  max_route_distance: number;
  shift_status: 'ACTIVE' | 'OFF_SHIFT';
}

export interface Assignment {
  id: string;
  discrepancy_id: string;
  worker_id: string;
  assigned_at: string;
  status: string;
  fairness_score: number;
  workload_utilization_pct: number;
  note?: string;
}

export interface FairnessWorkerRow extends Worker {
  workload_pct: number;
  eligible: boolean;
  reason: string;
  fairness_score: number;
}

export interface TimelineEvent {
  id: string;
  event_type: 'PUT_AWAY' | 'MOVE_EVENT' | 'PICK_FAILURE' | 'CYCLE_COUNT';
  timestamp: string;
  location: string;
  worker_id: string;
  quantity: number;
  details: string;
  suspicious: boolean;
}

export interface ScanTrail {
  sku: string;
  total_events: number;
  timeline: TimelineEvent[];
}

export interface ExperimentMetrics {
  location_accuracy: number;
  top1_accuracy: number;
  top3_accuracy: number;
  false_positive_rate: number;
  avg_locate_time_mins: number;
  avg_correction_time_mins: number;
  missing_stock_located_pct: number;
  percentage_corrected: number;
  unsafe_assignment_count: number;
  worker_workload_violations: number;
}

export interface ErrorAnalysisItem {
  sku: string;
  actual_location: string;
  baseline_prediction: string;
  prototype_prediction: string;
  is_correct: boolean;
  failure_reason: string;
}

export interface ExperimentComparison {
  baseline: ExperimentMetrics;
  target: ExperimentMetrics;
  prototype: ExperimentMetrics;
  improvement_pct: {
    top1_accuracy: number;
    locate_time_reduction: number;
    stock_located_gain: number;
  };
  error_analysis: ErrorAnalysisItem[];
}

export interface EdgeCaseResult {
  case_name: string;
  sku: string;
  input_description: string;
  expected_behavior: string;
  actual_behavior: string;
  status: 'PASS' | 'FAIL';
  details: Record<string, any>;
}

export interface EdgeCaseSuite {
  results: EdgeCaseResult[];
  total_passed: number;
  total_failed: number;
}

export interface ValidationFeedbackItem {
  id: string;
  user_role: string;
  ease_of_understanding: number;
  usefulness_rating: number;
  evidence_clarity: number;
  workflow_safety: number;
  search_time_reduction: number;
  overall_rating: number;
  comments?: string;
  timestamp: string;
}

export interface ValidationSummary {
  total_responses: number;
  averages: {
    overall_usefulness: number;
    location_usefulness: number;
    evidence_clarity: number;
    workflow_safety: number;
    search_time_reduction: number;
  };
  responses: ValidationFeedbackItem[];
}

export interface DashboardSummary {
  total_skus: number;
  suspected_discrepancies: number;
  high_confidence_discrepancies: number;
  missing_stock_located: number;
  avg_locate_time_mins: number;
  avg_correction_time_mins: number;
  safety_blocks_count: number;
  sla_risks_count: number;
  recent_discrepancies: Discrepancy[];
  zone_discrepancies: Record<string, number>;
  accuracy_comparison: {
    baseline_top1: number;
    prototype_top1: number;
    baseline_top3: number;
    prototype_top3: number;
  };
}
