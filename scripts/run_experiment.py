import os
import sys
import json

# Add backend directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.database import SessionLocal
from app.routers.experiments import run_empirical_experiment

def main():
    print("===============================================================")
    print(" PHARMATRACE - EMPIRICAL BENCHMARK & EXPERIMENT EVALUATION")
    print("===============================================================\n")
    
    db = SessionLocal()
    try:
        results = run_empirical_experiment(db)
        
        base = results["baseline"]
        proto = results["prototype"]
        imp = results["improvement_pct"]
        ttl = results["time_to_locate_experiment"]
        
        print(f"Total Test Cases Evaluated: {ttl['total_test_cases']}")
        print(f"---------------------------------------------------------------")
        print(f" METRIC                       BASELINE     PHARMATRACE   IMPROVEMENT")
        print(f"---------------------------------------------------------------")
        print(f" Top-1 Accuracy:              {base['top1_accuracy']:>5.1f}%       {proto['top1_accuracy']:>5.1f}%       +{imp['accuracy_boost_pct']:.1f}%")
        print(f" Top-3 Accuracy:              {base['top3_accuracy']:>5.1f}%       {proto['top3_accuracy']:>5.1f}%       +{proto['top3_accuracy'] - base['top3_accuracy']:.1f}%")
        print(f" Avg Search Time:             {base['avg_locate_time_mins']:>5.1f} min     {proto['avg_locate_time_mins']:>5.1f} min     -{imp['search_time_reduction_pct']:.1f}%")
        print(f" F1-Score:                     0.450        {imp['f1_score']:>5.3f}       +{imp['f1_score'] - 0.450:.3f}")
        print(f" False Positive Rate:         {base['false_positive_rate']*100:>5.1f}%       {proto['false_positive_rate']*100:>5.1f}%       -{ (base['false_positive_rate'] - proto['false_positive_rate'])*100:.1f}%")
        print(f"---------------------------------------------------------------\n")
        
        print("TIME-TO-LOCATE DETAILED TEST CASES:")
        print("SKU          Expected Loc      Actual Loc        Base (min)  PT (min)  Saved (min) Status")
        print("-" * 80)
        for c in ttl["cases"]:
            status = "MATCH [PASS]" if c["is_correct"] else "MISMATCH [FAIL]"
            print(f"{c['sku']:<12} {c['expected_location']:<17} {c['ground_truth_actual']:<17} {c['baseline_search_time_mins']:<11} {c['pharmatrace_search_time_mins']:<9} {c['time_saved_mins']:<11} {status}")
            
        print("\nERROR ANALYSIS BREAKDOWN:")
        for err in results["error_analysis"]:
            print(f" - [{err['sku']}] Pred: {err['predicted_location']} vs Actual: {err['actual_location']} ({err['failure_category']})")
            
        # Write JSON output to data/processed/experiment_results.json
        out_path = os.path.join(BASE_DIR, "data", "processed", "experiment_results.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved full benchmark report to: {out_path}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
