# RESTful API Documentation
## E-Commerce Abandoned Cart Recovery & Attribution System

### Base URL
`http://localhost:8000/api`

Interactive Swagger UI: `http://localhost:8000/docs`
ReDoc Interface: `http://localhost:8000/redoc`

---

### 1. Customers
- `GET /api/customers`
  - Query parameters: `skip` (int, default 0), `limit` (int, default 50), `search` (str), `preferred_channel` (`EMAIL` | `SMS`).
  - Response: `{ total: int, items: Customer[] }`.
- `GET /api/customers/{customer_id}`
  - Response: `CustomerDetail` with consents and lifetime status.

---

### 2. Consents
- `GET /api/consents`
  - Query parameters: `skip`, `limit`, `channel` (`EMAIL` | `SMS`), `status` (`OPT_IN` | `OPT_OUT`), `customer_id`.
  - Response: `{ total: int, items: Consent[] }`.

---

### 3. Shopping Carts
- `GET /api/carts`
  - Query parameters: `skip`, `limit`, `status`, `customer_id`.
  - Response: `{ total: int, items: Cart[] }`.
- `GET /api/carts/abandoned`
  - Returns carts where `status` in `['ABANDONED', 'ELIGIBLE', 'SUPPRESSED', 'CAMPAIGN_SCHEDULED']`.
- `GET /api/carts/eligible`
  - Returns carts where `status == 'ELIGIBLE'`.
- `GET /api/carts/suppressed`
  - Returns carts where `status == 'SUPPRESSED'`.
- `GET /api/carts/{cart_id}`
  - Returns detailed cart record including all nested `cart_lines`.

---

### 4. Campaigns
- `GET /api/campaigns`
  - Query parameters: `skip`, `limit`, `channel`, `is_active`.
  - Response: `{ total: int, items: Campaign[] }`.
- `POST /api/campaigns`
  - Request body: `{ name: string, channel: string, trigger_delay_minutes: int, discount_percent: float, is_active: bool }`.
  - Response: `201 Created` with new `Campaign`.
- `GET /api/campaigns/{campaign_id}`
  - Returns campaign details with associated `message_templates`.

---

### 5. Send Attempts
- `GET /api/send-attempts`
  - Query parameters: `skip`, `limit`, `status`, `channel`, `campaign_id`, `customer_id`, `suppression_reason`.
  - Response: `{ total: int, items: SendAttempt[] }`.
- `GET /api/send-attempts/{send_id}`
  - Returns detailed send attempt with chronological `communication_events`.

---

### 6. Orders & Attribution
- `GET /api/orders`
  - Query parameters: `skip`, `limit`, `customer_id`, `cart_id`, `status`.
  - Response: `{ total: int, items: Order[] }`.
- `GET /api/orders/{order_id}`
  - Returns order details with all nested `order_lines`.
- `GET /api/attributions`
  - Query parameters: `skip`, `limit`, `campaign_id`, `order_id`.
  - Response: `{ total: int, items: Attribution[] }`.

---

### 7. Analytics
- `GET /api/analytics/overview`
  - Returns all 14 KPI card values, plus lifecycle, channel, suppression, and anomaly chart data.
- `GET /api/analytics/campaign-performance`
  - Returns per-campaign send volume, delivery rate, open rate, click rate, conversions, and revenue.
- `GET /api/analytics/recovery`
  - Returns recovery rates and revenue trends.
- `GET /api/analytics/revenue`
  - Returns revenue totals grouped by campaign and channel.
- `GET /api/analytics/attribution`
  - Returns attribution model audit metadata.

---

### 8. Anomalies
- `GET /api/anomalies`
  - Query parameters: `skip`, `limit`, `issue_type`, `affected_entity`, `resolution_status`.
  - Response: `{ total: int, items: AnomalyRecord[] }`.
- `PATCH /api/anomalies/{anomaly_id}`
  - Request body: `{ status: "RESOLVED" | "DETECTED" | "IGNORED" }`.
  - Updates anomaly resolution status.

---

### 9. Validation
- `POST /api/validation/run`
  - Triggers the 16-point automated data validation suite and updates reports.
- `GET /api/validation/report`
  - Returns the latest validation summary report.

---

### 10. Synthetic Generator & Exports
- `POST /api/generator/run`
  - Request body: `{ scale: "starter" | "full", seed: 20261022, populate_db: true }`.
  - Runs synthetic data generation as a background task.
- `GET /api/generator/status`
  - Returns current generator state (`IDLE`, `RUNNING`, `COMPLETED`, `FAILED`).
- `GET /api/exports`
  - Returns list of exported CSV/JSON/SQL files and source manifest.
- `GET /api/exports/{filename}`
  - Downloads the requested export artifact.

