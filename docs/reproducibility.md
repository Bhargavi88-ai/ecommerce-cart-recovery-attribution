# Reproducibility Verification Guide
## Deterministic Synthetic Generation (Fixed Seed: 20261022)

### 1. Architectural Determinism
All pseudorandom selections (customer names, products, timestamps, device types, suppression decisions, campaign assignments, delivery latencies, and conversion orders) are driven by Python's Mersenne Twister initialized with a fixed default seed:
```python
DEFAULT_SEED = 20261022
```

The generator executes in strict dependency order:
1. Customers and Products
2. Consent records and Sessions
3. Carts and CartLines
4. Campaigns and Templates
5. Baseline Orders
6. Send Attempts and Communication Events
7. Campaign Conversion Orders and Attributions
8. Labelled Anomaly Fixtures
9. Ground Truth Decisions

---

### 2. Running Reproducibility Verification

Execute the automated reproducibility suite:
```bash
python scripts/run_reproducibility_test.py
```

This script:
1. Runs Generation Run 1 with seed `20261022`.
2. Runs Generation Run 2 with seed `20261022`.
3. Normalizes datetime representations and compares row counts and SHA-256 checksums across all generated CSV and SQL files.
4. Generates a formal verification report in `data/reports/reproducibility_report.json`.

---

### 3. Verification Report Output
```
============================================================
 Reproducibility Verification Test
 Scale: STARTER | Seed: 20261022
============================================================
[1/3] Generating Run 1...
[2/3] Generating Run 2...
[3/3] Comparing row counts and deterministic checksums...
      - customers.csv            Rows: 1000   HashMatch: True
      - products.csv             Rows: 20     HashMatch: True
      - consents.csv             Rows: 2124   HashMatch: True
      - sessions.csv             Rows: 2000   HashMatch: True
      - carts.csv                Rows: 2000   HashMatch: True
      - cart_lines.csv           Rows: 3399   HashMatch: True
      - campaigns.csv            Rows: 3      HashMatch: True
      - message_templates.csv    Rows: 4      HashMatch: True
      - send_attempts.csv        Rows: 540    HashMatch: True
      - orders.csv               Rows: 523    HashMatch: True
      - attributions.csv         Rows: 23     HashMatch: True
      - ground_truth.csv         Rows: 127    HashMatch: True
      - seed.sql                 Rows: 26     HashMatch: True
============================================================
 Reproducibility Result: PASSED (100% IDENTICAL)
 Report written to: data/reports/reproducibility_report.json
============================================================
```

Any run with the same seed and scale produces identical output files with zero discrepancy.

