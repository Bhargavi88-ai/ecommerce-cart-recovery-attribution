# Data Dictionary
## E-Commerce Abandoned Cart Recovery and Campaign Attribution System

### Overview
This data dictionary documents every table, column, data type, constraints, nullability, allowed enum values, units, and validation rules for the relational data store.

---

### 1. `customers` (Master Entity)
Represents registered individual consumers who create shopping carts and receive marketing communications.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `customer_id` | VARCHAR(32) | NO | PK | `^CUS-[0-9]{6}$` | Deterministic identifier, zero-padded, immutable. |
| `first_name` | VARCHAR(64) | NO | - | Text string | Consumer's first given name. Cannot be empty. |
| `last_name` | VARCHAR(64) | NO | - | Text string | Consumer's surname. Cannot be empty. |
| `email` | VARCHAR(128) | NO | - | Valid RFC 5322 email | Primary email address. Indexed for suppression lookup. |
| `phone` | VARCHAR(32) | NO | - | E.164 phone format | Mobile contact number for SMS recovery. |
| `preferred_channel` | VARCHAR(16) | NO | - | `EMAIL`, `SMS` | Customer's stated communication preference. |
| `created_at` | DATETIME | NO | - | UTC ISO-8601 | Account creation timestamp. |
| `updated_at` | DATETIME | NO | - | UTC ISO-8601 | Profile last modification timestamp. |

---

### 2. `products` (Supporting Master Entity)
Catalog of items available for merchandising and shopping cart insertion.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `product_id` | VARCHAR(32) | NO | PK | `^PRD-[0-9]{6}$` | Unique product identifier. |
| `sku` | VARCHAR(64) | NO | - | Unique alphanumeric | Stock Keeping Unit code. Must be globally unique. |
| `name` | VARCHAR(128) | NO | - | Text string | Commercial product title. |
| `category` | VARCHAR(64) | NO | - | `Electronics`, `Apparel`, `Home`, etc. | Product merchandise category. |
| `price` | DECIMAL(10,2)| NO | - | &gt; 0.00 USD | Base retail unit price. Must be positive. |
| `is_active` | BOOLEAN | NO | - | `TRUE`, `FALSE` | Availability flag for storefront listing. |

---

### 3. `consents` (Audit / Transactional Entity)
Independent point-in-time opt-in and opt-out history for privacy compliance (GDPR/TCPA/CAN-SPAM).

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `consent_id` | VARCHAR(32) | NO | PK | `^CNS-[0-9]{6}$` | Unique consent event identifier. |
| `customer_id` | VARCHAR(32) | NO | FK | References `customers.customer_id` | Target consumer profile. |
| `channel` | VARCHAR(16) | NO | - | `EMAIL`, `SMS` | Independent communication channel. |
| `status` | VARCHAR(16) | NO | - | `OPT_IN`, `OPT_OUT` | Consent disposition state. |
| `effective_at` | DATETIME | NO | - | UTC ISO-8601 | Exact wall-clock timestamp when consent took effect. |
| `source` | VARCHAR(64) | NO | - | `CHECKOUT_CHECKBOX`, `PREFERENCE_CENTER`, `UNSUBSCRIBE_LINK` | Provenance of the consent decision. |
| `created_at` | DATETIME | NO | - | UTC ISO-8601 | Record creation timestamp. |

---

### 4. `sessions` (Behavioral Entity)
Browsing and device engagement sessions initiated by consumers.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `session_id` | VARCHAR(32) | NO | PK | `^SES-2026-[0-9]{6}$` | Web/App session identifier. |
| `customer_id` | VARCHAR(32) | NO | FK | References `customers.customer_id` | Authenticated session customer. |
| `device_type` | VARCHAR(32) | NO | - | `DESKTOP`, `MOBILE`, `TABLET` | Hardware device class. |
| `ip_address` | VARCHAR(45) | YES | - | IPv4 / IPv6 | Originating client network address. |
| `user_agent` | VARCHAR(255)| YES | - | Browser user agent string | Client platform fingerprint. |
| `started_at` | DATETIME | NO | - | UTC ISO-8601 | Session initiation timestamp. |
| `ended_at` | DATETIME | YES | - | UTC ISO-8601 | Session termination timestamp. Must be &gt;= started_at. |

---

### 5. `carts` (Core Transactional Entity)
Shopping cart instances tracking current status, value, and abandonment.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `cart_id` | VARCHAR(32) | NO | PK | `^CART-2026-[0-9]{6}$` | Shopping cart primary identifier. |
| `customer_id` | VARCHAR(32) | NO | FK | References `customers.customer_id` | Owner customer ID. |
| `session_id` | VARCHAR(32) | YES | FK | References `sessions.session_id` | Associating session. |
| `status` | VARCHAR(32) | NO | - | `ACTIVE`, `ABANDONED`, `ELIGIBLE`, `SUPPRESSED`, `CAMPAIGN_SCHEDULED`, `RECOVERED`, `EXPIRED` | Current cart lifecycle phase. |
| `subtotal` | DECIMAL(10,2)| NO | - | &gt;= 0.00 USD | Sum of cart lines (`quantity * unit_price`). |
| `discount_total` | DECIMAL(10,2)| NO | - | &gt;= 0.00 USD | Total discount deductions applied. |
| `total_amount` | DECIMAL(10,2)| NO | - | &gt;= 0.00 USD | Net cart value (`subtotal - discount_total`). Must reconcile with line sums. |
| `created_at` | DATETIME | NO | - | UTC ISO-8601 | Cart creation timestamp. |
| `updated_at` | DATETIME | NO | - | UTC ISO-8601 | Cart update timestamp. |
| `last_activity_at` | DATETIME | NO | - | UTC ISO-8601 | Latest line item modification or navigation timestamp. |
| `abandoned_at` | DATETIME | YES | - | UTC ISO-8601 | Calculated timestamp when cart crossed 60-min inactivity threshold. |
| `recovered_at` | DATETIME | YES | - | UTC ISO-8601 | Timestamp when cart was purchased following recovery. |

---

### 6. `cart_lines` (Line-Item Entity)
Individual products and quantities contained within a shopping cart.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `cart_line_id` | VARCHAR(48) | NO | PK | `^CL-[A-Z0-9-]+-[0-9]{2}$` | Line item identifier. |
| `cart_id` | VARCHAR(32) | NO | FK | References `carts.cart_id` | Parent shopping cart. |
| `product_id` | VARCHAR(32) | NO | FK | References `products.product_id` | Merchandise product item. |
| `quantity` | INTEGER | NO | - | &gt;= 1 | Units in cart. Must be integer &gt; 0. |
| `unit_price` | DECIMAL(10,2)| NO | - | &gt; 0.00 USD | Price per single unit at time of insertion. |
| `total_price` | DECIMAL(10,2)| NO | - | &gt; 0.00 USD | Arithmetic reconciliation: `quantity * unit_price`. |

---

### 7. `campaigns` (Master Entity)
Marketing campaigns configured to recover abandoned shopping carts.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `campaign_id` | VARCHAR(32) | NO | PK | `^CMP-2026-[0-9]{6}$` | Unique campaign identifier. |
| `name` | VARCHAR(128) | NO | - | Text string | Descriptive title for the campaign. |
| `channel` | VARCHAR(16) | NO | - | `EMAIL`, `SMS` | Communication dispatch channel. |
| `trigger_delay_minutes` | INTEGER | NO | - | &gt;= 0 | Minutes of inactivity before trigger schedule (default 60). |
| `discount_percent` | DECIMAL(5,2)| NO | - | 0.00 to 100.00 | Promotional percentage discount offered. |
| `is_active` | BOOLEAN | NO | - | `TRUE`, `FALSE` | Operational enable flag. |
| `created_at` | DATETIME | NO | - | UTC ISO-8601 | Campaign creation timestamp. |

---

### 8. `message_templates` (Configuration Entity)
Content copy and variants for marketing campaigns.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `template_id` | VARCHAR(32) | NO | PK | `^TMPL-[0-9]{6}$` | Template identifier. |
| `campaign_id` | VARCHAR(32) | NO | FK | References `campaigns.campaign_id` | Associated campaign. |
| `channel` | VARCHAR(16) | NO | - | `EMAIL`, `SMS` | Channel formatting type. |
| `variant` | VARCHAR(8) | NO | - | `A`, `B` | A/B testing variant code. |
| `subject` | VARCHAR(255)| YES | - | Text string | Email subject line (NULL for SMS). |
| `body_template` | VARCHAR(1024)| NO| - | Template string with tokens | Copy with tokens: `{{first_name}}`, `{{cart_value}}`, etc. |
| `is_active` | BOOLEAN | NO | - | `TRUE`, `FALSE` | Active status of template variant. |

---

### 9. `send_attempts` (Operational / Transactional Entity)
Log of every scheduled recovery message attempt and its suppression decision.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `send_id` | VARCHAR(32) | NO | PK | `^SEND-2026-[0-9]{6}$` | Send attempt primary identifier. |
| `message_id` | VARCHAR(64) | NO | - | `^MSG-[A-Z0-9-]+-[0-9]{2}$` | Message identifier tracking cart and sequence. |
| `campaign_id` | VARCHAR(32) | NO | FK | References `campaigns.campaign_id` | Dispatched campaign. |
| `template_id` | VARCHAR(32) | YES | FK | References `message_templates.template_id` | Variant template used. |
| `cart_id` | VARCHAR(32) | NO | FK | References `carts.cart_id` | Target shopping cart. |
| `customer_id` | VARCHAR(32) | NO | FK | References `customers.customer_id` | Target consumer recipient. |
| `channel` | VARCHAR(16) | NO | - | `EMAIL`, `SMS` | Delivery medium. |
| `status` | VARCHAR(32) | NO | - | `QUEUED`, `SENT`, `SUPPRESSED`, `FAILED` | Attempt outcome disposition. |
| `suppression_reason` | VARCHAR(64) | YES | - | `NO_EMAIL_CONSENT`, `NO_SMS_CONSENT`, `CONSENT_WITHDRAWN`, `CART_PURCHASED`, `FREQUENCY_CAP_REACHED`, `DUPLICATE_CAMPAIGN` | Mandatory reason code when status is `SUPPRESSED`. |
| `scheduled_at` | DATETIME | NO | - | UTC ISO-8601 | Intended dispatch timestamp. |
| `sent_at` | DATETIME | YES | - | UTC ISO-8601 | Actual provider dispatch timestamp (NULL if suppressed). |
| `created_at` | DATETIME | NO | - | UTC ISO-8601 | Log creation timestamp. |

---

### 10. `communication_events` (Telemetry Entity)
Simulated webhook events tracking transmission through the carrier/provider network.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `event_id` | VARCHAR(32) | NO | PK | `^EVT-2026-[0-9]{6}$` | Unique telemetry event identifier. |
| `send_id` | VARCHAR(32) | NO | FK | References `send_attempts.send_id` | Corresponding send attempt. |
| `event_type` | VARCHAR(32) | NO | - | `SEND`, `DELIVERED`, `OPENED`, `CLICKED`, `FAILED`, `BOUNCED` | Telemetry event lifecycle stage. |
| `timestamp` | DATETIME | NO | - | UTC ISO-8601 | Event wall-clock timestamp. Must follow chronology. |
| `metadata_json` | TEXT | YES | - | Valid JSON | Supplemental provider metadata. |

---

### 11. `orders` & `order_lines` (Commerce Entity)
Completed purchase transactions.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `order_id` | VARCHAR(32) | NO | PK | `^ORD-2026-[0-9]{6}$` | Order primary key. |
| `customer_id` | VARCHAR(32) | NO | FK | References `customers.customer_id` | Buyer customer ID. |
| `cart_id` | VARCHAR(32) | YES | FK | References `carts.cart_id` | Cart converted into order (NULL for direct/organic). |
| `total_amount` | DECIMAL(10,2)| NO | - | &gt; 0.00 USD | Total order value. Must match sum of order lines. |
| `order_timestamp`| DATETIME | NO | - | UTC ISO-8601 | Checkout completion timestamp. |
| `status` | VARCHAR(32) | NO | - | `COMPLETED`, `CANCELLED` | Order fulfillment status. |

---

### 12. `attributions` (Analytical Entity)
Deterministic last-click campaign attribution ledger.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `attribution_id` | VARCHAR(32) | NO | PK | `^ATTR-2026-[0-9]{6}$` | Unique attribution record identifier. |
| `order_id` | VARCHAR(32) | NO | FK, UNIQUE | References `orders.order_id` | Converted order. Enforces 1:1 attribution. |
| `send_id` | VARCHAR(32) | NO | FK | References `send_attempts.send_id` | Winning qualifying message send attempt. |
| `campaign_id` | VARCHAR(32) | NO | FK | References `campaigns.campaign_id` | Credited marketing campaign. |
| `cart_id` | VARCHAR(32) | YES | FK | References `carts.cart_id` | Recovered cart ID. |
| `order_timestamp`| DATETIME | NO | - | UTC ISO-8601 | Timestamp order was placed. |
| `qualifying_click_at` | DATETIME | NO | - | UTC ISO-8601 | Timestamp of latest qualifying campaign click. Must be &lt; order_timestamp and within 7 days. |
| `latency_hours` | INTEGER | NO | - | &gt;= 0 | Elapsed hours between click and order. |
| `attributed_revenue` | DECIMAL(10,2)| NO | - | &gt; 0.00 USD | Total revenue credited to campaign. |
| `model` | VARCHAR(32) | NO | - | `LAST_CLICK` | Attribution algorithm used. |
| `created_at` | DATETIME | NO | - | UTC ISO-8601 | Attribution calculation timestamp. |

---

### 13. `anomaly_records` (Quality & Audit Entity)
Explicitly labeled anomaly fixture records for system testing and validation audits.

| Column Name | Data Type | Nullable | PK/FK | Allowed Values / Format | Description & Validation Rules |
|---|---|---|---|---|---|
| `anomaly_id` | VARCHAR(32) | NO | PK | `^ANO-[0-9]{6}$` | Anomaly record primary key. |
| `issue_type` | VARCHAR(64) | NO | - | `MESSAGE_AFTER_OPTOUT`, `CART_ABANDONED_AFTER_PURCHASE`, `DUPLICATE_ATTRIBUTION`, `STALE_CART_TOTAL` | Mandatory anomaly category. |
| `affected_entity`| VARCHAR(64) | NO | - | `SendAttempt`, `Cart`, `Attribution` | Impacted data model. |
| `affected_record_id` | VARCHAR(64) | NO | - | Primary Key value | ID of the specific record exhibiting anomaly. |
| `detected_at` | DATETIME | NO | - | UTC ISO-8601 | Timestamp when anomaly was flagged. |
| `observed_value` | TEXT | NO | - | Detailed description | Actual erroneous value/behavior found. |
| `expected_value` | TEXT | NO | - | Detailed description | Correct expected value under business rules. |
| `ground_truth_label`| VARCHAR(64)| NO | - | Label identifier | Synthetic ground truth classification label. |
| `expected_decision` | VARCHAR(128)| NO| - | Policy string | What rule engine was supposed to decide. |
| `actual_decision` | VARCHAR(128)| NO | - | Policy string | What erroneous action occurred. |
| `resolution_status` | VARCHAR(32)| NO | - | `DETECTED`, `RESOLVED`, `IGNORED` | Lifecycle status of exception investigation. |

