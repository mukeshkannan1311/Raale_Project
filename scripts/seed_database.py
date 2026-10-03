import os
import sys
import csv
from datetime import datetime

# Add parent directory to sys.path to enable importing app modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.database import engine, Base, SessionLocal
from app.models.models import (
    LocationMaster, Worker, Inventory, PutawayScan, MoveEvent,
    PickFailure, CycleCount, Discrepancy, User, ValidationFeedback, AuditLog
)

SEED_DIR = os.path.join(BASE_DIR, "data", "seed")

def parse_datetime(dt_str):
    if not dt_str:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return datetime.utcnow()

def seed_database():
    print("Starting PharmaTrace Database Seeding...")
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Seed Locations
        loc_file = os.path.join(SEED_DIR, "locations.csv")
        if os.path.exists(loc_file):
            db.query(LocationMaster).delete()
            with open(loc_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    loc = LocationMaster(
                        location_id=row["location_id"],
                        location_code=row["location_code"],
                        zone=row["zone"],
                        aisle=row["aisle"],
                        rack=row["rack"],
                        bin_number=row.get("bin_number"),
                        temperature_class=row["temperature_class"],
                        storage_type=row["storage_type"],
                        capacity=int(row["capacity"]),
                        current_utilization=int(row["current_utilization"]),
                        status=row["status"],
                        restricted=row["restricted"].lower() == "true",
                        allowed_product_type=row["allowed_product_type"]
                    )
                    db.add(loc)
            print(" - LocationMaster seeded.")

        # 2. Seed Workers
        wrk_file = os.path.join(SEED_DIR, "workers.csv")
        if os.path.exists(wrk_file):
            db.query(Worker).delete()
            with open(wrk_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    wrk = Worker(
                        worker_id=row["worker_id"],
                        id=row.get("id"),
                        name=row["name"],
                        worker_name=row.get("worker_name", row["name"]),
                        role=row["role"],
                        shift=row.get("shift", "DAY_SHIFT"),
                        max_tasks=int(row["max_tasks"]),
                        current_tasks=int(row["current_tasks"]),
                        current_distance=float(row.get("current_distance", 0.0)),
                        max_distance=float(row.get("max_distance", 10.0)),
                        shift_status=row.get("shift_status", "ACTIVE"),
                        status=row.get("status", "ACTIVE"),
                        authorized_zones=row["authorized_zones"],
                        zone_authorization=row.get("zone_authorization", row["authorized_zones"])
                    )
                    db.add(wrk)
            print(" - Workers seeded.")

        # 3. Seed Inventory
        inv_file = os.path.join(SEED_DIR, "inventory.csv")
        if os.path.exists(inv_file):
            db.query(Inventory).delete()
            with open(inv_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    inv = Inventory(
                        id=row["id"],
                        sku=row["sku"],
                        product_name=row["product_name"],
                        batch_id=row["batch_id"],
                        quantity=int(row["quantity"]),
                        expected_location_id=row["expected_location_id"],
                        storage_requirement=row["storage_requirement"],
                        status=row["status"],
                        created_at=parse_datetime(row.get("created_at")),
                        updated_at=parse_datetime(row.get("updated_at"))
                    )
                    db.add(inv)
            print(" - Inventory seeded.")

        # 4. Seed Putaway Scans
        put_file = os.path.join(SEED_DIR, "putaway_scans.csv")
        if os.path.exists(put_file):
            db.query(PutawayScan).delete()
            with open(put_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scan = PutawayScan(
                        scan_id=row["scan_id"],
                        id=row.get("id"),
                        sku=row["sku"],
                        batch_id=row["batch_id"],
                        quantity=int(row["quantity"]),
                        source_location=row["source_location"],
                        destination_location=row["destination_location"],
                        from_location=row.get("from_location"),
                        to_location=row.get("to_location"),
                        worker_id=row["worker_id"],
                        timestamp=parse_datetime(row.get("timestamp")),
                        zone=row.get("zone")
                    )
                    db.add(scan)
            print(" - PutawayScans seeded.")

        # 5. Seed Move Events
        mov_file = os.path.join(SEED_DIR, "move_events.csv")
        if os.path.exists(mov_file):
            db.query(MoveEvent).delete()
            with open(mov_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    mov = MoveEvent(
                        move_id=row["move_id"],
                        id=row.get("id"),
                        sku=row["sku"],
                        batch_id=row["batch_id"],
                        quantity=int(row.get("quantity", 1)),
                        source_location=row["source_location"],
                        destination_location=row["destination_location"],
                        worker_id=row["worker_id"],
                        timestamp=parse_datetime(row.get("timestamp")),
                        reason=row["reason"]
                    )
                    db.add(mov)
            print(" - MoveEvents seeded.")

        # 6. Seed Pick Failures
        fail_file = os.path.join(SEED_DIR, "pick_failures.csv")
        if os.path.exists(fail_file):
            db.query(PickFailure).delete()
            with open(fail_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pf = PickFailure(
                        failure_id=row["failure_id"],
                        id=row.get("id"),
                        sku=row["sku"],
                        batch_id=row["batch_id"],
                        expected_location=row["expected_location"],
                        worker_id=row["worker_id"],
                        timestamp=parse_datetime(row.get("timestamp")),
                        failure_reason=row["failure_reason"]
                    )
                    db.add(pf)
            print(" - PickFailures seeded.")

        # 7. Seed Cycle Counts
        cnt_file = os.path.join(SEED_DIR, "cycle_counts.csv")
        if os.path.exists(cnt_file):
            db.query(CycleCount).delete()
            with open(cnt_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cc = CycleCount(
                        count_id=row["count_id"],
                        id=row.get("id"),
                        location_id=row["location_id"],
                        sku=row["sku"],
                        counted_quantity=int(row["counted_quantity"]),
                        actual_quantity=int(row.get("actual_quantity", row["counted_quantity"])),
                        system_quantity=int(row["system_quantity"]),
                        variance=int(row["variance"]),
                        worker_id=row["worker_id"],
                        timestamp=parse_datetime(row.get("timestamp"))
                    )
                    db.add(cc)
            print(" - CycleCounts seeded.")

        # 8. Seed Discrepancies
        disc_file = os.path.join(SEED_DIR, "discrepancies.csv")
        if os.path.exists(disc_file):
            db.query(Discrepancy).delete()
            with open(disc_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    disc = Discrepancy(
                        id=row["id"],
                        sku=row["sku"],
                        batch_id=row.get("batch_id"),
                        quantity=int(row.get("quantity", 1)),
                        expected_location=row["expected_location"],
                        predicted_location=row["predicted_location"],
                        verified_location=row.get("verified_location"),
                        baseline_location=row.get("baseline_location"),
                        confidence=float(row.get("confidence", 0.85)),
                        priority=row.get("priority", "HIGH"),
                        status=row.get("status", "OPEN"),
                        correction_status=row.get("correction_status", "PENDING"),
                        safety_blocked=row.get("safety_blocked", "false").lower() == "true",
                        created_at=parse_datetime(row.get("created_at"))
                    )
                    db.add(disc)
            print(" - Discrepancies seeded.")

        # 9. Seed Default Demo Users
        db.query(User).delete()
        admin_user = User(
            id="USR-001",
            username="admin",
            name="Warehouse Admin",
            hashed_password="pbkdf2:sha256:password_hash_admin", # Simple demo hash
            role="ADMIN"
        )
        manager_user = User(
            id="USR-002",
            username="manager",
            name="Operations Lead",
            hashed_password="pbkdf2:sha256:password_hash_manager",
            role="WAREHOUSE_MANAGER"
        )
        worker_user = User(
            id="USR-003",
            username="worker",
            name="Alex Smith (Picker)",
            hashed_password="pbkdf2:sha256:password_hash_worker",
            role="WORKER"
        )
        db.add_all([admin_user, manager_user, worker_user])
        print(" - Default Users seeded (admin, manager, worker).")

        # 10. Audit Log Initial Entry
        db.add(AuditLog(
            id="AUD-0001",
            timestamp=datetime.utcnow(),
            user_id="USR-001",
            action="SYSTEM_INITIALIZED",
            entity="DATABASE",
            details_json={"message": "PharmaTrace database successfully seeded with initial datasets"}
        ))

        db.commit()
        print("PharmaTrace Database Seeding Completed Successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
