# PharmaTrace - API Specification & Documentation

## Overview
The PharmaTrace REST API is powered by FastAPI and automatically generates OpenAPI 3.0 documentation available at `/docs` (Swagger UI).

Base URL: `http://localhost:8000/api`

---

## Endpoint Summary Table

| Endpoint | Method | Purpose | Input / Query | Response |
|---|---|---|---|---|
| `/health` | GET | System health check | None | `{"status": "healthy"}` |
| `/auth/login` | POST | User login & JWT issuance | `UserLoginRequest` | `TokenResponse` |
| `/auth/me` | GET | Fetch active user profile | Bearer Token | `UserResponse` |
| `/inventory` | GET | List inventory items | `status`, `storage_requirement`, `search` | `List[InventoryBase]` |
| `/inventory/{sku}` | GET | Get single inventory SKU detail | `sku` | `InventoryBase` |
| `/discrepancies` | GET | List detected discrepancies | `status`, `priority` | `List[DiscrepancyResponse]` |
| `/discrepancies/{id}` | GET | Get discrepancy detail | `id` | `DiscrepancyResponse` |
| `/discrepancies/detect` | POST | Run discrepancy detection sweep | None | `{"detected_count": int}` |
| `/predict-location` | POST | Execute ML location prediction | `{"sku": str}` | `PredictionResponse` |
| `/predictions/{sku}` | GET | Fetch prediction for SKU | `sku` | `PredictionResponse` |
| `/discrepancies/{id}/resolve` | POST | Verify location & resolve discrepancy | `DiscrepancyActionRequest` | `{"verified_location": str}` |
| `/scan-trail/{sku}` | GET | Get chronological scan history | `sku` | `ScanTrailResponse` |
| `/locations` | GET | List warehouse location master | `zone`, `status`, `restricted` | `List[LocationMasterBase]` |
| `/locations/{location_code}` | GET | Get single location detail | `location_code` | `LocationMasterBase` |
| `/workers` | GET | List warehouse workers | `shift`, `shift_status` | `List[WorkerBase]` |
| `/safety/check-assignment` | POST | Verify worker & location safety | `SafetyCheckRequest` | `SafetyCheckResponse` |
| `/assignments` | POST | Create worker investigation task | `AssignmentCreateRequest` | `AssignmentResponse` |
| `/assignments/fairness/{id}` | GET | Evaluate fairness panel for task | `discrepancy_id` | `{"candidates": List}` |
| `/experiment/run` | POST | Run benchmark experiment | None | `ExperimentComparisonResponse` |
| `/experiment/results` | GET | Get benchmark results | None | `ExperimentComparisonResponse` |
| `/edge-cases/run` | GET/POST | Execute automated edge cases | None | `EdgeCaseSuiteResponse` |
| `/validation/feedback` | POST | Submit stakeholder feedback | `ValidationFeedbackCreate` | `ValidationFeedbackResponse` |
| `/validation/feedback` | GET | List submitted feedback | None | `List[ValidationFeedbackResponse]` |
| `/audit/logs` | GET | List system audit log entries | None | `List[AuditLogResponse]` |

---

## Detailed Example Payloads

### POST `/api/predict-location`
**Request**:
```json
{
  "sku": "MED-1002-001"
}
```

**Response**:
```json
{
  "sku": "MED-1002-001",
  "expected_location": "COLD-A01-R05-B01",
  "predicted_location": "COLD-A02-R03-B04",
  "confidence": 0.91,
  "top_candidates": [
    {
      "location_id": "COLD-A02-R03-B04",
      "probability": 0.91,
      "evidence_summary": "High confidence: Supported by recent movement and cycle count events.",
      "is_valid": true,
      "rejection_reason": null,
      "zone": "COLD_STORAGE",
      "temperature_class": "COLD_4C"
    },
    {
      "location_id": "COLD-A01-R05-B01",
      "probability": 0.08,
      "evidence_summary": "Low probability candidate location.",
      "is_valid": true,
      "rejection_reason": null,
      "zone": "COLD_STORAGE",
      "temperature_class": "COLD_4C"
    }
  ],
  "model_name": "PharmaTrace Probability Model v1.0",
  "explanation": [
    {
      "factor": "Recent Unrecorded Movement",
      "impact": "+35%",
      "description": "Move event history shows SKU was transferred to location COLD-A02-R03-B04."
    },
    {
      "factor": "Storage Compatibility",
      "impact": "REQUIRED PASS",
      "description": "Storage zone (COLD_STORAGE) matches product requirement (COLD_STORAGE)."
    }
  ]
}
```

### POST `/api/safety/check-assignment`
**Request**:
```json
{
  "worker_id": "WRK-003",
  "location_id": "COLD-A01-R05-B01",
  "sku": "MED-1002-001"
}
```

**Response**:
```json
{
  "allowed": false,
  "reason": "Worker Alex Smith has reached maximum task capacity (5/5 tasks).",
  "worker_workload_status": {
    "current_tasks": 5,
    "max_tasks": 5,
    "utilization_pct": 100.0,
    "shift_status": "ACTIVE"
  },
  "zone_authorization_status": {
    "target_zone": "COLD_STORAGE",
    "worker_authorizations": "AMBIENT,COLD_STORAGE",
    "authorized": true
  },
  "location_status": {
    "location_id": "COLD-A01-R05-B01",
    "status": "ACTIVE",
    "restricted": false
  }
}
```
