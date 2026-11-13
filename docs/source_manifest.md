# Source Provenance & Data Manifest
## E-Commerce Cart Recovery Synthetic Dataset

### 1. Lawful Synthetic Notice
**IMPORTANT NOTICE:** All data contained within this application and its export packages is **100% synthetically generated** using deterministic pseudorandom algorithmic distributions (Seed: `20261022`).
- No personally identifiable information (PII) or real consumer transaction records are included.
- All names, email addresses, phone numbers, and browsing records are fictitious and engineered strictly for technical demonstration, architectural validation, and compliance benchmarking.

---

### 2. Manifest Schema (`source_manifest.json`)
The source manifest located at `data/exports/source_manifest.json` documents the provenance of all exported files:

```json
{
  "dataset_name": "E-Commerce Abandoned Cart Recovery Dataset",
  "synthetic_notice": "ALL DATA CONTAINED HEREIN IS 100% SYNTHETIC AND DOES NOT REPRESENT REAL INDIVIDUALS.",
  "generator_version": "2.0.0",
  "scale": "starter",
  "seed": 20261022,
  "generated_at_utc": "2026-11-13T15:30:56.554032+00:00",
  "provenance": {
    "author": "Antigravity Solution Architecture",
    "rules": "E-Commerce Inactivity Abandonment + Multi-Channel Consent & Frequency Capping + Last-Click Attribution",
    "attribution_window_days": 7,
    "inactivity_threshold_minutes": 60
  },
  "files": {
    "customers.csv": {
      "sha256": "4b92b67f...",
      "row_count": 1000,
      "size_bytes": 113475
    },
    "carts.csv": {
      "sha256": "81f7ea51...",
      "row_count": 2000,
      "size_bytes": 349025
    },
    "cart_lines.csv": {
      "sha256": "27c5bb17...",
      "row_count": 3399,
      "size_bytes": 206106
    },
    "consents.csv": {
      "sha256": "d412ab34...",
      "row_count": 2124,
      "size_bytes": 198279
    },
    "send_attempts.csv": {
      "sha256": "63a8bc12...",
      "row_count": 540,
      "size_bytes": 92126
    },
    "orders.csv": {
      "sha256": "1290fe34...",
      "row_count": 523,
      "size_bytes": 42556
    },
    "attributions.csv": {
      "sha256": "9b12cf54...",
      "row_count": 23,
      "size_bytes": 3896
    },
    "ground_truth.csv": {
      "sha256": "3a78bc91...",
      "row_count": 127,
      "size_bytes": 10401
    },
    "seed.sql": {
      "sha256": "88ae9021...",
      "row_count": 26,
      "size_bytes": 4933
    }
  }
}
```

