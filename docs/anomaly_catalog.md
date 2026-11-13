# Anomaly Catalog & Exception Reference
## Labelled Production Anomaly Fixtures

### 1. Overview
Section 10 of the system specification mandates the injection and detection of 4 explicit labelled anomalies. These test cases ensure that the business engine, data quality validator, and frontend dashboard correctly surface non-compliant edge cases rather than silently discarding them.

---

### 2. Anomaly 1: `MESSAGE_AFTER_OPTOUT`

- **Issue Classification:** Regulatory Privacy Violation (CAN-SPAM / GDPR / TCPA).
- **Affected Entity:** `SendAttempt` (e.g. `SEND-2026-999901`).
- **Observed Behavior:** A marketing recovery message was dispatched to a consumer whose communication consent status was `OPT_OUT` prior to the send timestamp.
- **Expected Policy Decision:** The send attempt must be suppressed with reason code `CONSENT_WITHDRAWN`.
- **Ground Truth Label:** `UNLAWFUL_SEND_POST_WITHDRAWAL`.
- **Detection Logic:**
  ```sql
  SELECT s.send_id, s.customer_id, s.sent_at, c.effective_at
  FROM send_attempts s
  JOIN consents c ON s.customer_id = c.customer_id AND s.channel = c.channel
  WHERE s.status = 'SENT'
    AND c.status = 'OPT_OUT'
    AND c.effective_at <= s.sent_at;
  ```
- **Resolution Path:** Cancel pending scheduled messages, set suppression code `CONSENT_WITHDRAWN`, and mark anomaly `RESOLVED`.

---

### 3. Anomaly 2: `CART_ABANDONED_AFTER_PURCHASE`

- **Issue Classification:** Cart Lifecycle Desynchronization.
- **Affected Entity:** `Cart` (e.g. `CART-2026-000016`).
- **Observed Behavior:** A shopping cart was marked as `ABANDONED` after an order was already completed for that same cart.
- **Expected Policy Decision:** The cart must transition directly to `RECOVERED` or `PURCHASED`, with `abandoned_at = NULL`.
- **Ground Truth Label:** `FALSE_ABANDONMENT_AFTER_PURCHASE`.
- **Detection Logic:**
  ```sql
  SELECT c.cart_id, c.abandoned_at, o.order_id, o.order_timestamp
  FROM carts c
  JOIN orders o ON c.cart_id = o.cart_id
  WHERE c.status = 'ABANDONED'
    AND o.order_timestamp <= c.abandoned_at;
  ```
- **Resolution Path:** Update cart status to `RECOVERED`, nullify `abandoned_at`, and mark anomaly `RESOLVED`.

---

### 4. Anomaly 3: `DUPLICATE_ATTRIBUTION`

- **Issue Classification:** Revenue Accounting Inaccuracy / Multi-Claim Overcount.
- **Affected Entity:** `Attribution` (e.g. Order `ORD-2026-999903`).
- **Observed Behavior:** A single order has multiple competing primary attribution claims across different campaigns.
- **Expected Policy Decision:** Apply deterministic Last-Click Attribution to choose the single winning click with the latest timestamp.
- **Ground Truth Label:** `DOUBLE_COUNTED_ORDER_REVENUE`.
- **Detection Logic:**
  ```sql
  SELECT order_id, COUNT(attribution_id) AS claim_count
  FROM attributions
  GROUP BY order_id
  HAVING COUNT(attribution_id) > 1;
  ```
- **Resolution Path:** Delete secondary competing claims, preserving only the winning Last-Click record, and mark anomaly `RESOLVED`.

---

### 5. Anomaly 4: `STALE_CART_TOTAL`

- **Issue Classification:** Arithmetic Integrity Failure.
- **Affected Entity:** `Cart` (e.g. `CART-2026-000021`).
- **Observed Behavior:** The cart's stored `total_amount` desynchronized from the actual sum of its associated `cart_lines`.
- **Expected Policy Decision:** Cart total must always equal $\sum (\text{quantity} \times \text{unit\_price}) - \text{discount\_total}$.
- **Ground Truth Label:** `DESYNCHRONIZED_CART_LINE_PRICE`.
- **Detection Logic:**
  ```sql
  SELECT c.cart_id, c.total_amount, SUM(cl.total_price) AS calculated_sum
  FROM carts c
  JOIN cart_lines cl ON c.cart_id = cl.cart_id
  GROUP BY c.cart_id
  HAVING ABS(c.total_amount - (SUM(cl.total_price) - c.discount_total)) > 0.01;
  ```
- **Resolution Path:** Recalculate and update `total_amount = sum(cart_lines.total_price)`, and mark anomaly `RESOLVED`.

