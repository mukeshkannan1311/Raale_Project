from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.models import Worker, Driver, LocationMaster, Discrepancy

class SafetyFairnessService:
    @staticmethod
    def validate_worker_safety(
        worker: Worker,
        location: LocationMaster,
        discrepancy: Discrepancy
    ) -> Tuple[bool, str]:
        """Validate worker workload, shift status, zone authorization, and distance limits."""
        # 1. Shift Status
        if worker.shift_status != "ACTIVE":
            return False, f"Worker {worker.name} ({worker.worker_id}) is currently OFF_SHIFT / ON_BREAK."

        # 2. Workload capacity
        if worker.current_tasks >= worker.max_tasks:
            return False, f"Worker {worker.name} has reached maximum task capacity ({worker.current_tasks}/{worker.max_tasks} tasks)."

        # 3. Accumulated Distance limit
        if worker.current_distance >= worker.max_distance:
            return False, f"Worker {worker.name} has exceeded shift walking distance limit ({worker.current_distance:.1f}/{worker.max_distance:.1f} km)."

        # 4. Zone Authorization
        allowed_zones = [z.strip() for z in worker.zone_authorization.split(",")]
        if location.zone not in allowed_zones:
            return False, f"Worker {worker.name} lacks security/safety clearance for {location.zone} zone."

        # 5. Restricted Location clearance
        if location.restricted and worker.role not in ["WAREHOUSE_LEAD", "INSPECTOR"]:
            return False, f"Restricted location {location.location_id} requires WAREHOUSE_LEAD or INSPECTOR credentials."

        # 6. Location Blocked check
        if location.status == "BLOCKED":
            return False, f"Location {location.location_id} is BLOCKED due to physical hazard or maintenance."

        return True, "Safety check passed."

    @staticmethod
    def validate_driver_safety(driver: Driver) -> Tuple[bool, str]:
        """Validate driver route distance, assignment count, and shift status."""
        if driver.shift_status != "ACTIVE":
            return False, f"Driver {driver.name} is OFF_SHIFT."
        if driver.current_assignments >= driver.max_assignments:
            return False, f"Driver {driver.name} has reached max route assignments ({driver.current_assignments}/{driver.max_assignments})."
        if driver.route_distance >= driver.max_route_distance:
            return False, f"Driver {driver.name} has reached max daily route distance ({driver.route_distance:.1f}/{driver.max_route_distance:.1f} km)."
        return True, "Driver safety check passed."

    @staticmethod
    def compute_fairness_panel(db: Session, discrepancy_id: str) -> List[Dict[str, Any]]:
        """Generate a fairness evaluation table across all warehouse workers for a discrepancy."""
        discrepancy = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
        if not discrepancy:
            return []

        target_loc_id = discrepancy.predicted_location or discrepancy.expected_location
        location = db.query(LocationMaster).filter(LocationMaster.location_id == target_loc_id).first()
        
        workers = db.query(Worker).all()
        panel = []

        for w in workers:
            is_safe, reason = SafetyFairnessService.validate_worker_safety(w, location, discrepancy) if location else (True, "Passed")
            
            workload_pct = round((w.current_tasks / float(w.max_tasks)) * 100.0, 1) if w.max_tasks > 0 else 100.0
            
            # Compute fairness ranking score (higher score = more fair/recommended candidate)
            # Low workload % + high distance budget + safe = high fairness score
            fairness_score = 0.0
            if is_safe:
                fairness_score = (100.0 - workload_pct) * 0.6 + ((w.max_distance - w.current_distance) / w.max_distance * 100.0) * 0.4
            
            panel.append({
                "worker_id": w.worker_id,
                "name": w.name,
                "role": w.role,
                "current_tasks": w.current_tasks,
                "max_tasks": w.max_tasks,
                "workload_pct": workload_pct,
                "current_distance_km": w.current_distance,
                "max_distance_km": w.max_distance,
                "shift_status": w.shift_status,
                "zone_authorization": w.zone_authorization,
                "eligible": is_safe,
                "reason": reason,
                "fairness_score": round(fairness_score, 1)
            })

        # Sort by fairness score descending (eligible workers first)
        panel.sort(key=lambda x: (x["eligible"], x["fairness_score"]), reverse=True)
        return panel
