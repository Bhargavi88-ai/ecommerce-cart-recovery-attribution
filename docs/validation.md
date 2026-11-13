# Data Quality Validation Suite
## 16-Point Automated Relational and Integrity Auditor

### 1. Overview
The automated validation module (`app.validation.validator`) evaluates in-memory datasets and live database states against 16 structural, relational, arithmetic, and chronological rules.

---

### 2. Evaluated Rules Matrix

| Rule # | Rule Identifier | Validation Scope | Pass Criteria |
|---|---|---|---|
| 1 | `primary_key_uniqueness` | All 12 tables | Zero duplicate PK values across any entity. |
| 2 | `foreign_key_integrity` | Carts, CartLines, Consents, Sends, Orders, Attributions | 100% of foreign keys resolve to existing parent master records. |
| 3 | `missing_required_values`| Critical attributes | No NULL values in required fields (`first_name`, `email`, `total_amount`). |
| 4 | `enum_validity` | Carts, Consents, Sends, Events | All status and channel columns match documented enum sets. |
| 5 | `date_ordering` | Lifecycle timestamps | `created_at <= last_activity <= abandoned_at`, `scheduled_at <= sent_at`. |
| 6 | `consent_effective_dates`| Consents | Every consent record has a valid effective timestamp. |
| 7 | `lifecycle_transition_validity`| Carts | Recovered carts have corresponding completed purchase records. |
| 8 | `cart_line_arithmetic` | CartLines | `quantity > 0`, `unit_price > 0`, and `total_price == quantity * unit_price`. |
| 9 | `cart_total_reconciliation`| Carts vs CartLines | `cart.total_amount == sum(cart_lines.total_price) - discount_total`. |
| 10| `order_total_reconciliation`| Orders vs OrderLines | `order.total_amount == sum(order_lines.total_price)`. |
| 11| `duplicate_send_detection` | SendAttempts | No cart receives duplicate sends for the same campaign. |
| 12| `duplicate_attribution_detection`| Attributions | Exactly 1 attribution per order ID. |
| 13| `frequency_caps` | SendAttempts | No customer receives &gt;3 recovery sends per channel within any 7-day rolling window. |
| 14| `attribution_window` | Attributions | Converted orders occur strictly after qualifying clicks and within 7 days. |
| 15| `purchased_cart_suppression`| Carts & Sends | No recovery messages sent after an order is placed for the cart. |
| 16| `event_chronology` | CommunicationEvents | `SEND <= DELIVERED/BOUNCED <= OPENED <= CLICKED`. |

---

### 3. Generated Artifacts
1. **`validation_summary.json`:** Structured report containing overall status (`PASS` / `FAIL_WITH_WARNINGS`), pass/fail counts, and violation tallies.
2. **`validation_report.csv`:** Tabular report listing every rule and specific violation messages for audit logging.
