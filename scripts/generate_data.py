import os
import random
import json
import csv
from datetime import datetime, timedelta

# Fix random seed for reproducibility
random.seed(42)

# Root path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SEED_DIR = os.path.join(DATA_DIR, "seed")

os.makedirs(SEED_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "raw"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "processed"), exist_ok=True)

# Zones and temperature/product definitions
ZONES = ["AMBIENT", "COLD_STORAGE", "QUARANTINE", "HIGH_VALUE", "CONTROLLED_ACCESS"]
STORAGE_TYPES = {
    "AMBIENT": "SHELF",
    "COLD_STORAGE": "COLD_VAULT",
    "QUARANTINE": "SECURE_BIN",
    "HIGH_VALUE": "SECURE_BIN",
    "CONTROLLED_ACCESS": "COLD_VAULT"
}
TEMP_CLASSES = {
    "AMBIENT": "AMBIENT_20C",
    "COLD_STORAGE": "COLD_4C",
    "QUARANTINE": "AMBIENT_20C",
    "HIGH_VALUE": "CONTROLLED_15C",
    "CONTROLLED_ACCESS": "COLD_4C"
}
ALLOWED_PRODUCTS = {
    "AMBIENT": "GENERAL",
    "COLD_STORAGE": "VACCINE",
    "QUARANTINE": "HAZARDOUS",
    "HIGH_VALUE": "BIOLOGIC",
    "CONTROLLED_ACCESS": "CONTROLLED_SUBSTANCE"
}

ROLES = ["PICKER", "INSPECTOR", "WAREHOUSE_LEAD", "FORKLIFT_OPERATOR"]
SHIFTS = ["DAY_SHIFT", "NIGHT_SHIFT", "SWIFT_SHIFT"]

# Common Pharma SKUs with storage requirements
MEDICINES = [
    ("MED-1001", "Amoxicillin 500mg Caps", "AMBIENT"),
    ("MED-1002", "Insulin Glargine 100U/ml", "COLD_STORAGE"),
    ("MED-1003", "Pfizer COVID-19 Vaccine BNT162b2", "COLD_STORAGE"),
    ("MED-1004", "Morphine Sulfate 10mg Inj", "CONTROLLED_ACCESS"),
    ("MED-1005", "Adalimumab 40mg Syringe", "HIGH_VALUE"),
    ("MED-1006", "Paracetamol 500mg Tabs", "AMBIENT"),
    ("MED-1007", "Fentanyl Patch 25mcg/h", "CONTROLLED_ACCESS"),
    ("MED-1008", "Erythropoietin 4000IU Inj", "COLD_STORAGE"),
    ("MED-1009", "Expired Batch Isolation SKU", "QUARANTINE"),
    ("MED-1010", "Pembrolizumab 100mg/4ml", "HIGH_VALUE"),
]

def generate_locations(num_locations=40):
    locations = []
    zone_counts = {z: 0 for z in ZONES}
    
    for i in range(1, num_locations + 1):
        zone = ZONES[i % len(ZONES)]
        zone_counts[zone] += 1
        aisle = f"A{(zone_counts[zone] // 5) + 1:02d}"
        rack = f"R{(zone_counts[zone] % 5) + 1:02d}"
        bin_num = f"B{(i % 4) + 1:02d}"
        loc_code = f"{zone[:4]}-{aisle}-{rack}-{bin_num}"
        
        # Make a couple locations BLOCKED or RESTRICTED for testing
        status = "BLOCKED" if i in [5, 17] else "RESTRICTED" if i in [9, 23] else "ACTIVE"
        restricted = True if zone in ["HIGH_VALUE", "CONTROLLED_ACCESS"] or status == "RESTRICTED" else False
        
        locations.append({
            "location_id": loc_code,
            "location_code": loc_code,
            "zone": zone,
            "aisle": aisle,
            "rack": rack,
            "bin_number": bin_num,
            "temperature_class": TEMP_CLASSES[zone],
            "storage_type": STORAGE_TYPES[zone],
            "capacity": 500,
            "current_utilization": random.randint(50, 420),
            "status": status,
            "restricted": restricted,
            "allowed_product_type": ALLOWED_PRODUCTS[zone]
        })
    return locations

def generate_workers(num_workers=18):
    workers = []
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Avery", "Dakota", "Reese", "Quinn", "Skyler", "Cameron", "Rowan", "Hayden", "Emerson"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore"]
    
    for i in range(1, num_workers + 1):
        w_id = f"WRK-{i:03d}"
        name = f"{first_names[i-1]} {last_names[i-1]}"
        role = ROLES[i % len(ROLES)]
        shift = SHIFTS[i % len(SHIFTS)]
        max_tasks = 5
        # Give worker WRK-003 and WRK-007 max tasks (5/5) to test workload enforcement
        current_tasks = 5 if i in [3, 7] else random.randint(1, 4)
        
        # Authorizations
        if i % 3 == 0:
            auth_zones = "AMBIENT,COLD_STORAGE,QUARANTINE,HIGH_VALUE,CONTROLLED_ACCESS"
        elif i % 2 == 0:
            auth_zones = "AMBIENT,COLD_STORAGE"
        else:
            auth_zones = "AMBIENT"
            
        workers.append({
            "worker_id": w_id,
            "id": w_id,
            "name": name,
            "worker_name": name,
            "role": role,
            "shift": shift,
            "max_tasks": max_tasks,
            "current_tasks": current_tasks,
            "current_distance": round(random.uniform(1.2, 8.5), 1),
            "max_distance": 10.0,
            "shift_status": "ACTIVE" if i != 18 else "OFF_SHIFT",
            "status": "ACTIVE" if i != 18 else "INACTIVE",
            "authorized_zones": auth_zones,
            "zone_authorization": auth_zones
        })
    return workers

def generate_data():
    print("Generating PharmaTrace realistic dataset...")
    locations = generate_locations(40)
    workers = generate_workers(18)
    
    loc_by_zone = {}
    for loc in locations:
        loc_by_zone.setdefault(loc["zone"], []).append(loc["location_code"])
        
    all_loc_codes = [l["location_code"] for l in locations]
    active_loc_codes = [l["location_code"] for l in locations if l["status"] == "ACTIVE"]
    
    inventory_items = []
    putaway_scans = []
    move_events = []
    pick_failures = []
    cycle_counts = []
    discrepancy_test_cases = []
    
    start_time = datetime.utcnow() - timedelta(days=14)
    
    # 1. Generate 110 Inventory SKUs
    for i in range(1, 111):
        med_template = MEDICINES[i % len(MEDICINES)]
        sku = f"{med_template[0]}-{i:03d}"
        batch_id = f"BAT-2026-{(i % 25) + 1:03d}"
        req_zone = med_template[2]
        
        # Assign expected location compatible with zone
        expected_loc = random.choice(loc_by_zone.get(req_zone, active_loc_codes))
        qty = random.randint(20, 200)
        
        status = "AVAILABLE"
        inventory_items.append({
            "id": f"INV-{i:04d}",
            "sku": sku,
            "product_name": f"{med_template[1]} (Lot {i})",
            "batch_id": batch_id,
            "quantity": qty,
            "expected_location_id": expected_loc,
            "storage_requirement": req_zone,
            "status": status,
            "created_at": (start_time + timedelta(hours=i*2)).isoformat(),
            "updated_at": (start_time + timedelta(hours=i*2)).isoformat()
        })
        
    # Pick 12 ground-truth discrepancy test cases
    discrepant_skus = [inv["sku"] for inv in inventory_items[:12]]
    
    # 2. Putaway Scans (320 records)
    scan_idx = 1
    for inv in inventory_items:
        # 3 scans per SKU on average
        for s in range(3):
            scan_time = start_time + timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))
            w = random.choice(workers)["worker_id"]
            
            if inv["sku"] in discrepant_skus and s == 2:
                # Putaway placed it in actual physical location different from expected!
                # For cold storage, put in cold storage location; for ambient in ambient
                actual_loc = random.choice([l for l in loc_by_zone[inv["storage_requirement"]] if l != inv["expected_location_id"]])
                dest_loc = actual_loc
            else:
                dest_loc = inv["expected_location_id"]
                
            putaway_scans.append({
                "scan_id": f"PUT-{scan_idx:05d}",
                "id": f"PUT-{scan_idx:05d}",
                "sku": inv["sku"],
                "batch_id": inv["batch_id"],
                "quantity": inv["quantity"],
                "source_location": "RECEIVING-BAY-01",
                "destination_location": dest_loc,
                "from_location": "RECEIVING-BAY-01",
                "to_location": dest_loc,
                "worker_id": w,
                "timestamp": scan_time.isoformat(),
                "zone": inv["storage_requirement"]
            })
            scan_idx += 1

    # 3. Move Events (340 records)
    move_idx = 1
    for inv in inventory_items:
        for m in range(3):
            move_time = start_time + timedelta(days=random.randint(3, 13), hours=random.randint(0, 23))
            w = random.choice(workers)["worker_id"]
            
            if inv["sku"] in discrepant_skus:
                # For discrepant SKUs, latest move shows where it actually moved
                # E.g. WRK moved it to candidate actual location
                cand_locs = loc_by_zone[inv["storage_requirement"]]
                actual_loc = cand_locs[(hash(inv["sku"]) + m) % len(cand_locs)]
                src_loc = inv["expected_location_id"]
                dest_loc = actual_loc
                reason = "UNRECORDED_MOVE" if m == 2 else "RELOCATION"
            else:
                src_loc = inv["expected_location_id"]
                dest_loc = inv["expected_location_id"]
                reason = "REPLENISHMENT"
                
            move_events.append({
                "move_id": f"MOV-{move_idx:05d}",
                "id": f"MOV-{move_idx:05d}",
                "sku": inv["sku"],
                "batch_id": inv["batch_id"],
                "quantity": inv["quantity"],
                "source_location": src_loc,
                "destination_location": dest_loc,
                "worker_id": w,
                "timestamp": move_time.isoformat(),
                "reason": reason
            })
            move_idx += 1
            
    # 4. Pick Failures (65 records)
    fail_idx = 1
    for sku in discrepant_skus:
        inv = next(item for item in inventory_items if item["sku"] == sku)
        for f in range(2):
            fail_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            w = random.choice(workers)["worker_id"]
            pick_failures.append({
                "failure_id": f"FAIL-{fail_idx:05d}",
                "id": f"FAIL-{fail_idx:05d}",
                "sku": sku,
                "batch_id": inv["batch_id"],
                "expected_location": inv["expected_location_id"],
                "worker_id": w,
                "timestamp": fail_time.isoformat(),
                "failure_reason": "NOT_FOUND"
            })
            fail_idx += 1

    # 5. Cycle Counts (120 records)
    count_idx = 1
    for inv in inventory_items:
        if inv["sku"] in discrepant_skus:
            # Expected location count shows 0 actual quantity (missing!)
            c_time = datetime.utcnow() - timedelta(hours=random.randint(2, 36))
            w = random.choice(workers)["worker_id"]
            cycle_counts.append({
                "count_id": f"CNT-{count_idx:05d}",
                "id": f"CNT-{count_idx:05d}",
                "location_id": inv["expected_location_id"],
                "sku": inv["sku"],
                "counted_quantity": 0,
                "actual_quantity": 0,
                "system_quantity": inv["quantity"],
                "variance": -inv["quantity"],
                "worker_id": w,
                "timestamp": c_time.isoformat()
            })
            count_idx += 1
            
            # Actual location count shows system_quantity present!
            actual_loc = [m["destination_location"] for m in move_events if m["sku"] == inv["sku"]][-1]
            cycle_counts.append({
                "count_id": f"CNT-{count_idx:05d}",
                "id": f"CNT-{count_idx:05d}",
                "location_id": actual_loc,
                "sku": inv["sku"],
                "counted_quantity": inv["quantity"],
                "actual_quantity": inv["quantity"],
                "system_quantity": 0,
                "variance": inv["quantity"],
                "worker_id": w,
                "timestamp": (c_time + timedelta(minutes=15)).isoformat()
            })
            count_idx += 1
        else:
            if random.random() < 0.3:
                c_time = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                w = random.choice(workers)["worker_id"]
                cycle_counts.append({
                    "count_id": f"CNT-{count_idx:05d}",
                    "id": f"CNT-{count_idx:05d}",
                    "location_id": inv["expected_location_id"],
                    "sku": inv["sku"],
                    "counted_quantity": inv["quantity"],
                    "actual_quantity": inv["quantity"],
                    "system_quantity": inv["quantity"],
                    "variance": 0,
                    "worker_id": w,
                    "timestamp": c_time.isoformat()
                })
                count_idx += 1

    # Build discrepancy test cases with ground truth verified actual locations
    for idx, sku in enumerate(discrepant_skus):
        inv = next(item for item in inventory_items if item["sku"] == sku)
        moves = [m for m in move_events if m["sku"] == sku]
        verified_actual_loc = moves[-1]["destination_location"] if moves else inv["expected_location_id"]
        
        discrepancy_test_cases.append({
            "id": f"DISC-{idx+1:04d}",
            "sku": sku,
            "batch_id": inv["batch_id"],
            "quantity": inv["quantity"],
            "expected_location": inv["expected_location_id"],
            "predicted_location": verified_actual_loc,
            "verified_location": verified_actual_loc,
            "baseline_location": inv["expected_location_id"],
            "confidence": 0.92,
            "priority": "HIGH" if idx < 6 else "CRITICAL",
            "sla_deadline": (datetime.utcnow() + timedelta(hours=12)).isoformat(),
            "status": "OPEN",
            "correction_status": "PENDING",
            "safety_blocked": False,
            "created_at": (datetime.utcnow() - timedelta(hours=idx*3)).isoformat()
        })
        # Mark status in inventory
        inv["status"] = "DISCREPANT"

    # Save to seed files
    def save_csv(filename, data, fieldnames):
        filepath = os.path.join(SEED_DIR, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        # Also copy to data/raw for reference
        with open(os.path.join(DATA_DIR, "raw", filename), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    save_csv("locations.csv", locations, list(locations[0].keys()))
    save_csv("workers.csv", workers, list(workers[0].keys()))
    save_csv("inventory.csv", inventory_items, list(inventory_items[0].keys()))
    save_csv("putaway_scans.csv", putaway_scans, list(putaway_scans[0].keys()))
    save_csv("move_events.csv", move_events, list(move_events[0].keys()))
    save_csv("pick_failures.csv", pick_failures, list(pick_failures[0].keys()))
    save_csv("cycle_counts.csv", cycle_counts, list(cycle_counts[0].keys()))
    save_csv("discrepancies.csv", discrepancy_test_cases, list(discrepancy_test_cases[0].keys()))

    print(f"Data generation complete!")
    print(f" - Locations: {len(locations)}")
    print(f" - Workers: {len(workers)}")
    print(f" - Inventory SKUs: {len(inventory_items)}")
    print(f" - Putaway Scans: {len(putaway_scans)}")
    print(f" - Move Events: {len(move_events)}")
    print(f" - Pick Failures: {len(pick_failures)}")
    print(f" - Cycle Counts: {len(cycle_counts)}")
    print(f" - Ground-Truth Discrepancies: {len(discrepancy_test_cases)}")

if __name__ == "__main__":
    generate_data()
