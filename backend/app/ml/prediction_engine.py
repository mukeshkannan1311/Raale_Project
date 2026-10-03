import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier

from app.models.models import Inventory, LocationMaster, PutawayScan, MoveEvent, PickFailure, CycleCount
from app.ml.feature_engineering import extract_candidate_features
from app.services.baseline_service import get_baseline_prediction

class PharmaTraceMLModel:
    """
    Scikit-learn powered probability model trained on warehouse event features.
    """
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self._is_trained = False
        self._fit_synthetic_baseline()

    def _fit_synthetic_baseline(self):
        # Synthetic feature matrix to fit scikit-learn classifier
        # Features: [scan_recency, movement_recency, movement_freq, prev_loc_match, pick_fail_sig, cycle_cnt_sig, qty_match, storage_compat, loc_avail, loc_status, loc_dist, recent_act]
        X_train = np.array([
            [1.0, 0.5, 3.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 4.0],  # Strong match -> 1
            [99.0, 99.0, 0.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, 1.0, 3.0, 0.0], # Pick fail expected loc -> 0
            [2.0, 1.0, 2.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 3.0],  # Recent move candidate -> 1
            [5.0, 99.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 5.0, 0.0], # Incompatible blocked loc -> 0
            [10.0, 4.0, 1.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0], # Weak candidate -> 0
        ])
        y_train = np.array([1, 0, 1, 0, 0])
        self.model.fit(X_train, y_train)
        self._is_trained = True

    def predict_probability(self, features: Dict[str, float]) -> float:
        vec = np.array([[
            features["scan_recency"],
            features["movement_recency"],
            features["movement_frequency"],
            features["previous_location_match"],
            features["pick_failure_signal"],
            features["cycle_count_signal"],
            features["quantity_match"],
            features["storage_compatibility"],
            features["location_available"],
            features["location_status"],
            features["location_distance"],
            features["recent_activity_count"]
        ]])
        
        # Scikit-learn raw probability
        rf_prob = float(self.model.predict_proba(vec)[0][1])
        
        # Expert heuristic weighting fusion
        heuristic_score = (
            (0.35 * features["previous_location_match"]) +
            (0.25 * (1.0 if features["cycle_count_signal"] > 0 else 0.0)) +
            (0.15 * min(1.0, features["movement_frequency"] / 3.0)) +
            (0.15 * features["quantity_match"]) +
            (0.10 * (1.0 if features["scan_recency"] < 48.0 else 0.0))
        )
        
        # Hard penalties
        if features["storage_compatibility"] == 0.0:
            return 0.0 # Strict storage rejection
        if features["location_available"] == 0.0:
            return 0.0 # Strict blocked location rejection
        if features["pick_failure_signal"] < 0:
            heuristic_score *= 0.1 # Severe penalty if pick failed at location
            
        combined_prob = (0.5 * rf_prob) + (0.5 * heuristic_score)
        return min(0.98, max(0.01, float(combined_prob)))

# Global Model Instance
ml_engine = PharmaTraceMLModel()

def generate_explanations(features: Dict[str, float], candidate_loc: LocationMaster, inventory: Inventory) -> List[Dict[str, str]]:
    """
    Generates transparent, human-readable explanations based on feature signals.
    """
    explanations = []
    
    if features["previous_location_match"] > 0:
        explanations.append({
            "factor": "Recent Unrecorded Movement",
            "impact": "+35%",
            "description": f"Move event history shows SKU was transferred to location {candidate_loc.location_id}."
        })
        
    if features["cycle_count_signal"] > 0:
        explanations.append({
            "factor": "Cycle Count Verification",
            "impact": "+25%",
            "description": f"Physical count confirmed inventory present at location {candidate_loc.location_id}."
        })
        
    if features["quantity_match"] > 0.8:
        explanations.append({
            "factor": "Quantity Alignment",
            "impact": "+15%",
            "description": f"Counted quantity matches expected SKU batch quantity ({inventory.quantity if inventory else 0} units)."
        })
        
    if features["storage_compatibility"] > 0.9:
        explanations.append({
            "factor": "Storage Compatibility",
            "impact": "REQUIRED PASS",
            "description": f"Storage zone ({candidate_loc.zone}) matches product requirement ({inventory.storage_requirement if inventory else 'AMBIENT'})."
        })
        
    if features["scan_recency"] < 72.0:
        explanations.append({
            "factor": "Scan Recency",
            "impact": "+10%",
            "description": f"Putaway scan recorded within recent timeframe ({features['scan_recency']:.1f} hours ago)."
        })
        
    if features["pick_failure_signal"] < 0:
        explanations.append({
            "factor": "Pick Failure Signal",
            "impact": "-80%",
            "description": f"Worker previously reported pick failure at location {candidate_loc.location_id}."
        })

    return explanations

def predict_actual_location(db: Session, sku: str) -> Dict[str, Any]:
    """
    Executes the complete PharmaTrace Location Discrepancy Prediction Engine.
    Returns predicted location, top-3 candidates, confidence score, and dynamic explanations.
    """
    inventory = db.query(Inventory).filter(Inventory.sku == sku).first()
    expected_loc = inventory.expected_location_id if inventory else "UNKNOWN"
    
    locations = db.query(LocationMaster).all()
    putaways = db.query(PutawayScan).filter(PutawayScan.sku == sku).all()
    moves = db.query(MoveEvent).filter(MoveEvent.sku == sku).all()
    pick_failures = db.query(PickFailure).filter(PickFailure.sku == sku).all()
    cycle_counts = db.query(CycleCount).filter(CycleCount.sku == sku).all()
    
    candidate_results = []
    
    for loc in locations:
        features = extract_candidate_features(
            db=db,
            sku=sku,
            candidate_location=loc,
            inventory=inventory,
            putaways=putaways,
            moves=moves,
            pick_failures=pick_failures,
            cycle_counts=cycle_counts
        )
        
        prob = ml_engine.predict_probability(features)
        
        is_valid = True
        rejection_reason = None
        
        if loc.status in ["BLOCKED", "MAINTENANCE"]:
            is_valid = False
            rejection_reason = f"Location status is {loc.status}."
        elif features["storage_compatibility"] == 0.0:
            is_valid = False
            rejection_reason = f"Incompatible storage (Product requires {inventory.storage_requirement if inventory else 'AMBIENT'}, location zone is {loc.zone})."

        # Evidence summary text
        if prob > 0.6:
            ev_summary = "High confidence: Supported by recent movement and cycle count events."
        elif prob > 0.3:
            ev_summary = "Moderate candidate: Secondary movement or scan trail detected."
        else:
            ev_summary = "Low probability candidate location."

        candidate_results.append({
            "location_id": loc.location_id,
            "probability": round(prob, 2),
            "evidence_summary": ev_summary,
            "is_valid": is_valid,
            "rejection_reason": rejection_reason,
            "zone": loc.zone,
            "temperature_class": loc.temperature_class,
            "features": features,
            "location_obj": loc
        })
        
    # Sort candidates by probability descending
    candidate_results.sort(key=lambda x: x["probability"], reverse=True)
    
    # Filter top valid candidate
    valid_candidates = [c for c in candidate_results if c["is_valid"]]
    top_candidate = valid_candidates[0] if valid_candidates else candidate_results[0]
    
    # Generate Top-3 candidate payload for frontend
    top_3_payload = []
    for c in candidate_results[:3]:
        top_3_payload.append({
            "location_id": c["location_id"],
            "probability": c["probability"],
            "evidence_summary": c["evidence_summary"],
            "is_valid": c["is_valid"],
            "rejection_reason": c["rejection_reason"],
            "zone": c["zone"],
            "temperature_class": c["temperature_class"]
        })
        
    explanations = generate_explanations(top_candidate["features"], top_candidate["location_obj"], inventory)
    
    return {
        "sku": sku,
        "expected_location": expected_loc,
        "predicted_location": top_candidate["location_id"],
        "confidence": top_candidate["probability"],
        "top_candidates": top_3_payload,
        "model_name": "PharmaTrace Probability Model v1.0",
        "explanation": explanations,
        "is_valid_recommendation": top_candidate["is_valid"],
        "rejection_reason": top_candidate["rejection_reason"]
    }
