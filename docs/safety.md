# PharmaTrace - Safety & Fairness Engine Documentation

## 1. Safety Principles & Policy
In pharmaceutical logistics, operational efficiency must **never** compromise worker safety, product temperature integrity, or regulatory security compliance.

The PharmaTrace Safety Engine enforces strict, deterministic rules that override recommendation algorithms.

---

## 2. Implemented Safety Checks

### 2.1 Worker Workload Cap
- **Rule**: `current_tasks < max_tasks`.
- **Enforcement**: If a worker has reached maximum task capacity (e.g. 5/5 tasks), assignment requests return an HTTP 400 rejection with `allowed: false`.

### 2.2 Zone Authorization
- **Rule**: Target location zone must be present in worker `authorized_zones`.
- **Enforcement**: Prevents unauthorized personnel from accessing restricted zones (e.g. `CONTROLLED_ACCESS` or `HIGH_VALUE`).

### 2.3 Physical Location Status
- **Rule**: `location.status == "ACTIVE"`.
- **Enforcement**: Bin locations marked as `BLOCKED` or `MAINTENANCE` (e.g. due to chemical spill, physical damage, or temperature failure) are immediately rejected.

### 2.4 Temperature & Storage Compatibility
- **Rule**: Product `storage_requirement` must match candidate bin `zone`.
- **Enforcement**: Cold Storage SKUs (e.g. Insulin, Vaccines) are rejected from Ambient recommendations to prevent spoilage.

---

## 3. Workload-Aware Fair Assignment Panel
When dispatching investigation tasks, the system evaluates all active warehouse personnel:
$$\text{Fairness Score} = 0.6 \times (100 - \text{Workload \%}) + 0.4 \times \left( \frac{\text{Max Dist} - \text{Current Dist}}{\text{Max Dist}} \times 100 \right)$$
- Prioritizes eligible workers with lower workload utilization and available walking budget.
