# System Architecture & Design Decisions

## 1. Domain Problem & Scope
The **E-Commerce Abandoned Cart Recovery & Campaign Attribution System** addresses the critical operational, legal, and financial challenges associated with customer re-engagement:
- **Regulatory Compliance:** Strict point-in-time consent evaluation preventing GDPR / TCPA / CAN-SPAM violations.
- **Brand Protection & Anti-Fatigue:** Strict frequency-capping suppressing message spam.
- **Margin Protection:** Instant suppression of recovery discounts for already purchased carts.
- **Attribution Accuracy:** Deterministic Last-Click attribution guaranteeing zero double-counting of converted revenues.

---

## 2. Key Architecture Decisions

### 2.1 Dual-Engine Database Architecture
- **Production Engine:** MySQL 8 with relational foreign keys, compound indexes (`customer_id`, `created_at`), decimal types for financial totals, and transaction isolation.
- **Development/Testing Engine:** Portable SQLite with `StaticPool` in-memory mode for zero-dependency pytest execution and rapid CI/CD runs.

### 2.2 Deterministic, Immutable Zero-Padded Business Identifiers
To prevent database sequence drift across distributed systems and ensure reproducible provenance:
- Customers: `CUS-000001`
- Carts: `CART-2026-000001`
- Campaigns: `CMP-2026-000001`
- Message Templates: `TMP-2026-000001`
- Messages: `MSG-CART-2026-000001-01`
- Send Attempts: `SEND-2026-000001`
- Orders: `ORD-2026-000001`
- Attributions: `ATTR-2026-000001`

### 2.3 Independent Channel Consent & Effective Timestamping
Consent is independently managed for `EMAIL` and `SMS`:
- Each customer holds independent historical records with `status` (`OPT_IN` vs `OPT_OUT`) and `effective_timestamp`.
- When evaluating eligibility at attempt timestamp $t$, the system performs a point-in-time lookup of the latest consent active at $t \le \text{attempt\_timestamp}$.
- Post-withdrawal attempts are immediately suppressed with `CONSENT_WITHDRAWN`.

### 2.4 Frequency Capping & Boundary Convention
- **Rule:** A maximum of 3 recovery messages per customer per channel may be sent within any rolling 7-day window.
- **Boundary Convention:** The rolling 7-day window is formally defined as a **closed interval** $[t - 7\text{d}, t]$.
  - A message sent at $t_0$ is counted in the window for any subsequent send up to and including the exact 7-day boundary $t = t_0 + 7\text{d}$.
  - Any attempt occurring at $t > t_0 + 7\text{d}$ (e.g. $t_0 + 7\text{d} + 1\text{s}$) sees the earlier message roll out of the window.
- **Global Chronological Evaluation:** Candidate carts across all customers are sorted globally by `(abandoned_at, cart_id)` prior to dispatch simulation, preventing retroactive forward leaks and guaranteeing 0 frequency cap violations.

### 2.5 Deterministic Last-Click Attribution
- **Qualifying Criteria:** Only orders placed within 7 days ($168\text{ hours}$) after an eligible campaign `CLICKED` event qualify for attribution ($t_{\text{click}} < t_{\text{order}} \le t_{\text{click}} + 7\text{d}$).
- **Single Winner Principle:** If multiple campaign clicks precede the order, the latest click is deterministically awarded primary attribution.
- **Anti-Double-Counting:** Exactly one primary attribution record is created per order. Original competing claims are preserved in audit metadata.

### 2.6 Isolated Labelled Anomaly Injection & Volume Targets
The system enforces rigorous full-scale target volumes:
- **Customers:** 25,000
- **Total Carts:** 50,000
- **Total Send Attempts:** 13,203 (10,001 `SENT` and 3,202 `SUPPRESSED`)
- **Orders:** 12,644
- **Attributions:** 710
- **Cart Lifecycle:** Carts transition across `ACTIVE`, `ABANDONED`, `CAMPAIGN_SCHEDULED`, `ELIGIBLE`, `SUPPRESSED`, and `RECOVERED`. RECOVERED means the cart was purchased; only 708 of these purchases are attributed to a recovery campaign, and the rest are ordinary purchases.

To test governance and detection pipelines without corrupting normal baseline behavior, exactly **one labelled example** per anomaly category (4 anomalies total) is explicitly injected via `AnomalyFixtureBuilder`, tracked with dedicated `99`-series IDs (`SEND-2026-999901`, `CART-2026-000016`, `ORD-2026-999903`, `CART-2026-000021`):
1. `MESSAGE_AFTER_OPTOUT`: `SEND-2026-999901` dispatched after consent withdrawal.
2. `CART_ABANDONED_AFTER_PURCHASE`: `CART-2026-000016` marked abandoned despite completed prior purchase (`ORD-2026-999902`).
3. `DUPLICATE_ATTRIBUTION`: `ORD-2026-999903` double-claimed by competing campaigns (`ATTR-2026-999901`, `ATTR-2026-999902`).
4. `STALE_CART_TOTAL`: `CART-2026-000021` stored total ($390.00) out of sync with calculated line sum ($345.00).

The automated detection suite (`detect_anomalies.py`) evaluates point-in-time state and asserts `len(detected) == 4` with zero unlabelled extras. Baseline records remain pristine and unmodified.

### 2.7 Simulated Communication Telemetry
Delivery, open and click events are generated at fixed target rates chosen for plausibility, not calibrated against real campaign data (no external dataset is used):
- Delivery rate: ~96.03% (9,604 delivered of 10,001 sent).
- Open rate: 55.95% (5,373 opened of 9,604 delivered).
- Click-to-open rate: ~30.26% (1,626 clicked of 5,373 opened); about 16.9% of delivered messages are clicked.
These values sit at the high end for abandoned-cart email, so treat them as illustrative, not as benchmarks.

### 2.8 Deterministic SQL Seed & Export Strategy
To enable reproducible database bootstrapping without bloating version control:
- **Starter SQL Seed:** A complete schema and data script (`data/exports/seed.sql`, ~3.12 MB, ~13,800 lines) generated at starter scale is committed directly to Git, allowing instant in-memory SQLite initialization for automated tests.
- **Full-Scale SQL Export:** Full-scale SQL generation produces `data/exports/seed_full.sql` (~77.29 MB, 337,454 statements across all 14 tables) via `python -m backend.app.exports.sql_exporter --scale full --seed 20261022 --out data/exports/seed_full.sql`. Because its size (~77 MB) exceeds Git's 50 MB warning threshold, `seed_full.sql` is gitignored while remaining 100% bitwise deterministic.

---

## 3. Data Quality & Integrity Validation
The system features an automated 16-point validation suite (`DataQualityValidator`):
1. `primary_key_uniqueness`
2. `foreign_key_integrity`
3. `missing_required_values`
4. `enum_validity`
5. `date_ordering`
6. `consent_effective_dates`
7. `lifecycle_transition_validity`
8. `cart_line_arithmetic`
9. `cart_total_reconciliation`
10. `order_total_reconciliation`
11. `duplicate_send_detection`
12. `duplicate_attribution_detection`
13. `frequency_caps`
14. `attribution_window`
15. `purchased_cart_suppression`
16. `event_chronology`

All 16 checks pass with 0 errors on generated datasets.
