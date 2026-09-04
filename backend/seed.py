import os
import random
import csv
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.models import (
    LocationMaster, PutawayScan, MoveEvent, PickFailure, CycleCount,
    Worker, Driver, Discrepancy, AuditLog
)

# Set seed for reproducible synthetic data
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

ZONES = ["AMBIENT", "COLD_STORAGE", "QUARANTINE", "HIGH_VALUE", "CONTROLLED_ACCESS"]
TEMP_CLASSES = {
    "AMBIENT": "AMBIENT_20C",
    "COLD_STORAGE": "COLD_4C",
    "QUARANTINE": "AMBIENT_20C",
    "HIGH_VALUE": "CONTROLLED_15C",
    "CONTROLLED_ACCESS": "FROZEN_20C"
}
PRODUCT_TYPES = {
    "AMBIENT": "GENERAL",
    "COLD_STORAGE": "VACCINE",
    "QUARANTINE": "GENERAL",
    "HIGH_VALUE": "BIOLOGIC",
    "CONTROLLED_ACCESS": "CONTROLLED_SUBSTANCE"
}

def generate_locations():
    locations = []
    # Explicit demo locations
    demo_locs = [
        ("A-03-R02-B04", "AMBIENT", "A", "R02", "AMBIENT_20C", 100, 40, "ACTIVE", False, "GENERAL"),
        ("COLD-02-R01-B03", "COLD_STORAGE", "COLD-02", "R01", "COLD_4C", 150, 75, "ACTIVE", False, "VACCINE"),
        ("Q-01-R01-B02", "QUARANTINE", "Q", "R01", "AMBIENT_20C", 80, 20, "BLOCKED", True, "GENERAL"),
        ("HV-01-R03-B01", "HIGH_VALUE", "HV", "R03", "CONTROLLED_15C", 50, 45, "RESTRICTED", True, "BIOLOGIC"),
        ("CTRL-01-R01-B01", "CONTROLLED_ACCESS", "CTRL", "R01", "FROZEN_20C", 60, 30, "RESTRICTED", True, "CONTROLLED_SUBSTANCE")
    ]
    for loc in demo_locs:
        locations.append({
            "location_id": loc[0], "zone": loc[1], "aisle": loc[2], "rack": loc[3],
            "temperature_class": loc[4], "capacity": loc[5], "current_utilization": loc[6],
            "status": loc[7], "restricted": loc[8], "allowed_product_type": loc[9]
        })
    
    # General locations across zones
    for zone in ZONES:
        prefix = zone[:4].upper()
        for aisle in range(1, 5):
            for rack in range(1, 6):
                for bin_num in range(1, 5):
                    loc_id = f"{prefix}-{aisle:02d}-R{rack:02d}-B{bin_num:02d}"
                    if any(l["location_id"] == loc_id for l in locations):
                        continue
                    status = "BLOCKED" if random.random() < 0.05 else ("RESTRICTED" if zone in ["HIGH_VALUE", "CONTROLLED_ACCESS"] else "ACTIVE")
                    locations.append({
                        "location_id": loc_id,
                        "zone": zone,
                        "aisle": f"{prefix}-{aisle:02d}",
                        "rack": f"R{rack:02d}",
                        "temperature_class": TEMP_CLASSES[zone],
                        "capacity": random.choice([80, 100, 150, 200]),
                        "current_utilization": random.randint(10, 70),
                        "status": status,
                        "restricted": zone in ["HIGH_VALUE", "CONTROLLED_ACCESS"] or status == "RESTRICTED",
                        "allowed_product_type": PRODUCT_TYPES[zone]
                    })
    return locations

def generate_workers():
    workers = [
        {"worker_id": "W-101", "name": "Sarah Jenkins", "role": "PICKER", "current_tasks": 2, "max_tasks": 5, "current_distance": 3.2, "max_distance": 10.0, "shift_status": "ACTIVE", "zone_authorization": "AMBIENT,COLD_STORAGE,QUARANTINE"},
        {"worker_id": "W-102", "name": "Marcus Vance", "role": "INSPECTOR", "current_tasks": 1, "max_tasks": 4, "current_distance": 1.5, "max_distance": 8.0, "shift_status": "ACTIVE", "zone_authorization": "AMBIENT,COLD_STORAGE,HIGH_VALUE,CONTROLLED_ACCESS"},
        {"worker_id": "W-103", "name": "Elena Rostova", "role": "WAREHOUSE_LEAD", "current_tasks": 0, "max_tasks": 6, "current_distance": 0.8, "max_distance": 12.0, "shift_status": "ACTIVE", "zone_authorization": "AMBIENT,COLD_STORAGE,QUARANTINE,HIGH_VALUE,CONTROLLED_ACCESS"},
        {"worker_id": "W-104", "name": "David Chen", "role": "FORKLIFT_OPERATOR", "current_tasks": 4, "max_tasks": 4, "current_distance": 9.5, "max_distance": 10.0, "shift_status": "ACTIVE", "zone_authorization": "AMBIENT,QUARANTINE"}, # Overloaded worker
        {"worker_id": "W-105", "name": "Rachel Adams", "role": "PICKER", "current_tasks": 0, "max_tasks": 5, "current_distance": 0.0, "max_distance": 10.0, "shift_status": "OFF_SHIFT", "zone_authorization": "AMBIENT,COLD_STORAGE"}
    ]
    return workers

def generate_drivers():
    drivers = [
        {"driver_id": "D-201", "name": "Robert Taylor", "current_assignments": 3, "max_assignments": 8, "route_distance": 18.5, "max_route_distance": 50.0, "shift_status": "ACTIVE"},
        {"driver_id": "D-202", "name": "Anita Patel", "current_assignments": 8, "max_assignments": 8, "route_distance": 48.0, "max_route_distance": 50.0, "shift_status": "ACTIVE"},
        {"driver_id": "D-203", "name": "Carlos Gomez", "current_assignments": 1, "max_assignments": 6, "route_distance": 12.0, "max_route_distance": 40.0, "shift_status": "ACTIVE"}
    ]
    return drivers

def generate_warehouse_data(locations, workers):
    now = datetime.utcnow()

    # Create 110 SKUs
    skus = [f"MED-{1000 + i}" for i in range(1, 111)]
    worker_ids = [w["worker_id"] for w in workers]
    
    putaways = []
    moves = []
    failures = []
    cycle_counts = []
    
    loc_by_zone = {}
    for loc in locations:
        loc_by_zone.setdefault(loc["zone"], []).append(loc["location_id"])

    all_loc_ids = [l["location_id"] for l in locations]

    # Generate normal trail data for SKUs
    event_counter = 1
    for sku in skus:
        batch_id = f"BATCH-{sku}-01"
        zone = random.choice(ZONES)
        candidate_locs = loc_by_zone[zone]
        
        orig_loc = random.choice(candidate_locs)
        putaway_time = now - timedelta(days=random.randint(10, 30), hours=random.randint(0, 23))
        
        # 1. Putaway scan
        putaways.append({
            "scan_id": f"PUT-{event_counter:05d}",
            "sku": sku,
            "batch_id": batch_id,
            "quantity": random.choice([50, 100, 200, 500]),
            "from_location": "RECEIVING-DOCK-1",
            "to_location": orig_loc,
            "worker_id": random.choice(worker_ids),
            "timestamp": putaway_time,
            "zone": zone
        })
        event_counter += 1
        
        # 80% of SKUs have 1-3 move events
        current_loc = orig_loc
        if random.random() < 0.8:
            num_moves = random.randint(1, 3)
            for m in range(num_moves):
                dest_loc = random.choice(candidate_locs)
                move_time = putaway_time + timedelta(days=m*3 + 1, hours=random.randint(1, 12))
                moves.append({
                    "move_id": f"MOV-{event_counter:05d}",
                    "sku": sku,
                    "batch_id": batch_id,
                    "quantity": random.choice([50, 100, 200]),
                    "source_location": current_loc,
                    "destination_location": dest_loc,
                    "worker_id": random.choice(worker_ids),
                    "timestamp": move_time,
                    "reason": random.choice(["RELOCATION", "REPLENISHMENT", "ISOLATION"])
                })
                current_loc = dest_loc
                event_counter += 1

        # 30% of SKUs have cycle counts
        if random.random() < 0.3:
            cycle_counts.append({
                "count_id": f"CYC-{event_counter:05d}",
                "location_id": current_loc,
                "sku": sku,
                "counted_quantity": random.choice([50, 100, 200]),
                "system_quantity": random.choice([50, 100, 200]),
                "variance": 0,
                "worker_id": random.choice(worker_ids),
                "timestamp": now - timedelta(days=random.randint(1, 5))
            })
            event_counter += 1

    # --- INJECT DEMO SPECIFIC DISCREPANCY: MED-1042 ---
    med1042_sku = "MED-1042"
    med1042_batch = "BATCH-MED1042-01"
    med1042_expected = "A-03-R02-B04"       # System location (Ambient)
    med1042_actual = "COLD-02-R01-B03"      # Physical actual location (Cold Storage)
    
    putaways.append({
        "scan_id": "PUT-MED1042",
        "sku": med1042_sku,
        "batch_id": med1042_batch,
        "quantity": 100,
        "from_location": "RECEIVING-DOCK-1",
        "to_location": med1042_expected,
        "worker_id": "W-101",
        "timestamp": now - timedelta(days=14),
        "zone": "AMBIENT"
    })
    
    # Move event from Expected -> Cold Storage
    moves.append({
        "move_id": "MOV-MED1042",
        "sku": med1042_sku,
        "batch_id": med1042_batch,
        "quantity": 100,
        "source_location": med1042_expected,
        "destination_location": med1042_actual,
        "worker_id": "W-102",
        "timestamp": now - timedelta(hours=6),
        "reason": "UNRECORDED_MOVE"
    })
    
    # Pick failure at expected location
    failures.append({
        "failure_id": "FAIL-MED1042",
        "sku": med1042_sku,
        "batch_id": med1042_batch,
        "expected_location": med1042_expected,
        "worker_id": "W-101",
        "timestamp": now - timedelta(hours=2),
        "failure_reason": "NOT_FOUND"
    })
    
    # Cycle count confirming stock at actual location
    cycle_counts.append({
        "count_id": "CYC-MED1042",
        "location_id": med1042_actual,
        "sku": med1042_sku,
        "counted_quantity": 100,
        "system_quantity": 0,
        "variance": 100,
        "worker_id": "W-103",
        "timestamp": now - timedelta(hours=1)
    })

    # --- INJECT 15 OTHER SYNTHETIC DISCREPANCIES ---
    discrepancy_skus = random.sample([s for s in skus if s != med1042_sku], 15)
    for d_sku in discrepancy_skus:
        d_batch = f"BATCH-{d_sku}-01"
        sys_loc = random.choice(all_loc_ids)
        act_loc = random.choice([l for l in all_loc_ids if l != sys_loc])
        
        moves.append({
            "move_id": f"MOV-DISC-{d_sku}",
            "sku": d_sku,
            "batch_id": d_batch,
            "quantity": 150,
            "source_location": sys_loc,
            "destination_location": act_loc,
            "worker_id": random.choice(worker_ids),
            "timestamp": now - timedelta(hours=random.randint(4, 24)),
            "reason": "UNRECORDED_MOVE"
        })
        failures.append({
            "failure_id": f"FAIL-DISC-{d_sku}",
            "sku": d_sku,
            "batch_id": d_batch,
            "expected_location": sys_loc,
            "worker_id": random.choice(worker_ids),
            "timestamp": now - timedelta(hours=random.randint(1, 3)),
            "failure_reason": "NOT_FOUND"
        })
        if random.random() < 0.6:
            cycle_counts.append({
                "count_id": f"CYC-DISC-{d_sku}",
                "location_id": act_loc,
                "sku": d_sku,
                "counted_quantity": 150,
                "system_quantity": 0,
                "variance": 150,
                "worker_id": random.choice(worker_ids),
                "timestamp": now - timedelta(hours=random.randint(1, 12))
            })

    return putaways, moves, failures, cycle_counts, discrepancy_skus

def seed_all():
    print("Generating synthetic datasets...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    locations = generate_locations()
    workers = generate_workers()
    drivers = generate_drivers()
    putaways, moves, failures, cycle_counts, discrepancy_skus = generate_warehouse_data(locations, workers)

    # Save to CSV files
    pd.DataFrame(locations).to_csv(os.path.join(DATA_DIR, "location_master.csv"), index=False)
    pd.DataFrame(putaways).to_csv(os.path.join(DATA_DIR, "putaway_scans.csv"), index=False)
    pd.DataFrame(moves).to_csv(os.path.join(DATA_DIR, "move_events.csv"), index=False)
    pd.DataFrame(failures).to_csv(os.path.join(DATA_DIR, "pick_failures.csv"), index=False)
    pd.DataFrame(cycle_counts).to_csv(os.path.join(DATA_DIR, "cycle_counts.csv"), index=False)

    print(f"CSV files created in {DATA_DIR}:")
    print(f"  - location_master.csv: {len(locations)} rows")
    print(f"  - putaway_scans.csv: {len(putaways)} rows")
    print(f"  - move_events.csv: {len(moves)} rows")
    print(f"  - pick_failures.csv: {len(failures)} rows")
    print(f"  - cycle_counts.csv: {len(cycle_counts)} rows")

    # Insert into database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        for l in locations:
            db.add(LocationMaster(**l))
        for w in workers:
            db.add(Worker(**w))
        for d in drivers:
            db.add(Driver(**d))
        for p in putaways:
            db.add(PutawayScan(**p))
        for m in moves:
            db.add(MoveEvent(**m))
        for f in failures:
            db.add(PickFailure(**f))
        for c in cycle_counts:
            db.add(CycleCount(**c))
        
        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Database seed error: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
