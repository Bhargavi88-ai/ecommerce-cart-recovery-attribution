from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import pandas as pd
from app.validation.rules import ValidationRuleResult


class DataQualityValidator:
    """
    Automated 16-point Data Quality Validation Suite.
    Validates integrity, relational constraints, business rules, and chronology.
    Produces validation_summary.json and validation_report.csv.
    """

    def __init__(self, dataset: Dict[str, Any]):
        self.dataset = dataset
        self.results: List[ValidationRuleResult] = []

    def run_all_validations(self) -> Dict[str, Any]:
        self.results = [
            self._validate_primary_key_uniqueness(),
            self._validate_foreign_key_integrity(),
            self._validate_missing_required_values(),
            self._validate_enum_validity(),
            self._validate_date_ordering(),
            self._validate_consent_effective_dates(),
            self._validate_lifecycle_transitions(),
            self._validate_cart_line_arithmetic(),
            self._validate_cart_total_reconciliation(),
            self._validate_order_total_reconciliation(),
            self._validate_duplicate_sends(),
            self._validate_duplicate_attributions(),
            self._validate_frequency_caps(),
            self._validate_attribution_window(),
            self._validate_purchased_cart_suppression(),
            self._validate_event_chronology()
        ]

        total_rules = len(self.results)
        passed_rules = sum(1 for r in self.results if r.passed)
        failed_rules = total_rules - passed_rules
        total_violations = sum(r.error_count for r in self.results)

        summary = {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "total_violations": total_violations,
            "overall_status": "PASS" if failed_rules == 0 else "FAIL_WITH_WARNINGS",
            "rule_results": [r.to_dict() for r in self.results]
        }
        return summary

    def get_validation_report_rows(self) -> List[Dict[str, Any]]:
        rows = []
        for r in self.results:
            if not r.passed and r.errors:
                for err in r.errors:
                    rows.append({
                        "rule_name": r.rule_name,
                        "status": "FAIL",
                        "error_message": err
                    })
            else:
                rows.append({
                    "rule_name": r.rule_name,
                    "status": "PASS",
                    "error_message": "All records compliant"
                })
        return rows

    # 1. Primary-Key Uniqueness
    def _validate_primary_key_uniqueness(self) -> ValidationRuleResult:
        errors = []
        entities = [
            ("customers", "customer_id"),
            ("products", "product_id"),
            ("consents", "consent_id"),
            ("sessions", "session_id"),
            ("carts", "cart_id"),
            ("cart_lines", "cart_line_id"),
            ("campaigns", "campaign_id"),
            ("message_templates", "template_id"),
            ("send_attempts", "send_id"),
            ("orders", "order_id"),
            ("order_lines", "order_line_id"),
            ("attributions", "attribution_id")
        ]
        for name, pk in entities:
            records = self.dataset.get(name, [])
            seen = set()
            for r in records:
                val = r.get(pk)
                if val in seen:
                    errors.append(f"Duplicate primary key {val} in table {name}")
                seen.add(val)
        return ValidationRuleResult("primary_key_uniqueness", len(errors) == 0, len(errors), errors)

    # 2. Foreign-Key Integrity
    def _validate_foreign_key_integrity(self) -> ValidationRuleResult:
        errors = []
        cust_ids = {c["customer_id"] for c in self.dataset.get("customers", [])}
        prod_ids = {p["product_id"] for p in self.dataset.get("products", [])}
        cart_ids = {c["cart_id"] for c in self.dataset.get("carts", [])}
        order_ids = {o["order_id"] for o in self.dataset.get("orders", [])}
        camp_ids = {c["campaign_id"] for c in self.dataset.get("campaigns", [])}
        send_ids = {s["send_id"] for s in self.dataset.get("send_attempts", [])}

        for c in self.dataset.get("carts", []):
            if c["customer_id"] not in cust_ids:
                errors.append(f"Cart {c['cart_id']} references unknown customer {c['customer_id']}")
        for cl in self.dataset.get("cart_lines", []):
            if cl["cart_id"] not in cart_ids:
                errors.append(f"CartLine {cl['cart_line_id']} references unknown cart {cl['cart_id']}")
            if cl["product_id"] not in prod_ids:
                errors.append(f"CartLine {cl['cart_line_id']} references unknown product {cl['product_id']}")
        for s in self.dataset.get("send_attempts", []):
            if s["customer_id"] not in cust_ids:
                errors.append(f"SendAttempt {s['send_id']} references unknown customer {s['customer_id']}")
            if s["campaign_id"] not in camp_ids:
                errors.append(f"SendAttempt {s['send_id']} references unknown campaign {s['campaign_id']}")
            if s["cart_id"] not in cart_ids:
                errors.append(f"SendAttempt {s['send_id']} references unknown cart {s['cart_id']}")
        for a in self.dataset.get("attributions", []):
            if a["order_id"] not in order_ids:
                errors.append(f"Attribution {a['attribution_id']} references unknown order {a['order_id']}")
            if a["send_id"] not in send_ids:
                errors.append(f"Attribution {a['attribution_id']} references unknown send {a['send_id']}")
        return ValidationRuleResult("foreign_key_integrity", len(errors) == 0, len(errors), errors)

    # 3. Missing Required Values
    def _validate_missing_required_values(self) -> ValidationRuleResult:
        errors = []
        for c in self.dataset.get("customers", []):
            if not c.get("first_name") or not c.get("email"):
                errors.append(f"Customer {c.get('customer_id')} has missing required fields")
        for cart in self.dataset.get("carts", []):
            if cart.get("status") is None or cart.get("total_amount") is None:
                errors.append(f"Cart {cart.get('cart_id')} has missing required status or amount")
        return ValidationRuleResult("missing_required_values", len(errors) == 0, len(errors), errors)

    # 4. Enum Validity
    def _validate_enum_validity(self) -> ValidationRuleResult:
        errors = []
        valid_cart_statuses = {"ACTIVE", "ABANDONED", "ELIGIBLE", "SUPPRESSED", "CAMPAIGN_SCHEDULED", "RECOVERED", "EXPIRED"}
        valid_send_statuses = {"QUEUED", "SENT", "SUPPRESSED", "FAILED"}
        valid_channels = {"EMAIL", "SMS"}

        for cart in self.dataset.get("carts", []):
            if cart["status"] not in valid_cart_statuses:
                errors.append(f"Invalid cart status '{cart['status']}' in {cart['cart_id']}")
        for s in self.dataset.get("send_attempts", []):
            if s["status"] not in valid_send_statuses:
                errors.append(f"Invalid send status '{s['status']}' in {s['send_id']}")
            if s["channel"] not in valid_channels:
                errors.append(f"Invalid channel '{s['channel']}' in {s['send_id']}")
        return ValidationRuleResult("enum_validity", len(errors) == 0, len(errors), errors)

    # 5. Date Ordering
    def _validate_date_ordering(self) -> ValidationRuleResult:
        errors = []
        for cart in self.dataset.get("carts", []):
            if cart["last_activity_at"] < cart["created_at"]:
                errors.append(f"Cart {cart['cart_id']} last_activity_at precedes created_at")
            if cart["abandoned_at"] and cart["abandoned_at"] < cart["last_activity_at"]:
                errors.append(f"Cart {cart['cart_id']} abandoned_at precedes last_activity_at")
        for s in self.dataset.get("send_attempts", []):
            if s["sent_at"] and s["sent_at"] < s["scheduled_at"]:
                errors.append(f"SendAttempt {s['send_id']} sent_at precedes scheduled_at")
        return ValidationRuleResult("date_ordering", len(errors) == 0, len(errors), errors)

    # 6. Consent Effective Dates
    def _validate_consent_effective_dates(self) -> ValidationRuleResult:
        errors = []
        for c in self.dataset.get("consents", []):
            if c["effective_at"] is None:
                errors.append(f"Consent {c['consent_id']} missing effective_at timestamp")
        return ValidationRuleResult("consent_effective_dates", len(errors) == 0, len(errors), errors)

    # 7. Lifecycle Transition Validity
    def _validate_lifecycle_transitions(self) -> ValidationRuleResult:
        errors = []
        for cart in self.dataset.get("carts", []):
            if cart["status"] == "RECOVERED" and cart["recovered_at"] is None and cart["cart_id"] not in {o.get("cart_id") for o in self.dataset.get("orders", [])}:
                errors.append(f"Recovered cart {cart['cart_id']} missing recovery confirmation")
        return ValidationRuleResult("lifecycle_transition_validity", len(errors) == 0, len(errors), errors)

    # 8. Cart-Line Quantity and Price
    def _validate_cart_line_arithmetic(self) -> ValidationRuleResult:
        errors = []
        for cl in self.dataset.get("cart_lines", []):
            if cl["quantity"] <= 0:
                errors.append(f"CartLine {cl['cart_line_id']} has non-positive quantity {cl['quantity']}")
            if cl["unit_price"] <= 0:
                errors.append(f"CartLine {cl['cart_line_id']} has non-positive unit_price {cl['unit_price']}")
            expected = round(cl["quantity"] * cl["unit_price"], 2)
            if abs(cl["total_price"] - expected) > 0.01:
                errors.append(f"CartLine {cl['cart_line_id']} total {cl['total_price']} != {expected}")
        return ValidationRuleResult("cart_line_arithmetic", len(errors) == 0, len(errors), errors)

    # 9. Cart-Total Reconciliation
    def _validate_cart_total_reconciliation(self) -> ValidationRuleResult:
        errors = []
        line_sums = {}
        for cl in self.dataset.get("cart_lines", []):
            line_sums[cl["cart_id"]] = line_sums.get(cl["cart_id"], 0.0) + cl["total_price"]

        for cart in self.dataset.get("carts", []):
            expected = round(line_sums.get(cart["cart_id"], 0.0), 2)
            if abs(cart["total_amount"] - expected) > 0.01:
                # If this cart is in anomaly fixtures (STALE_CART_TOTAL), it's recorded as an anomaly
                errors.append(f"Cart {cart['cart_id']} total {cart['total_amount']} != lines sum {expected}")
        return ValidationRuleResult("cart_total_reconciliation", len(errors) == 0, len(errors), errors)

    # 10. Order-Total Reconciliation
    def _validate_order_total_reconciliation(self) -> ValidationRuleResult:
        errors = []
        line_sums = {}
        for ol in self.dataset.get("order_lines", []):
            line_sums[ol["order_id"]] = line_sums.get(ol["order_id"], 0.0) + ol["total_price"]

        for o in self.dataset.get("orders", []):
            expected = round(line_sums.get(o["order_id"], 0.0), 2)
            if abs(o["total_amount"] - expected) > 0.01:
                errors.append(f"Order {o['order_id']} total {o['total_amount']} != lines sum {expected}")
        return ValidationRuleResult("order_total_reconciliation", len(errors) == 0, len(errors), errors)

    # 11. Duplicate Send Detection
    def _validate_duplicate_sends(self) -> ValidationRuleResult:
        errors = []
        seen = set()
        for s in self.dataset.get("send_attempts", []):
            if s["status"] == "SENT":
                key = (s["cart_id"], s["campaign_id"])
                if key in seen:
                    errors.append(f"Duplicate send attempt for cart {s['cart_id']} and campaign {s['campaign_id']}")
                seen.add(key)
        return ValidationRuleResult("duplicate_send_detection", len(errors) == 0, len(errors), errors)

    # 12. Duplicate Attribution Detection
    def _validate_duplicate_attributions(self) -> ValidationRuleResult:
        errors = []
        seen = set()
        for a in self.dataset.get("attributions", []):
            oid = a["order_id"]
            if oid in seen:
                errors.append(f"Duplicate attribution detected for order {oid}")
            seen.add(oid)
        return ValidationRuleResult("duplicate_attribution_detection", len(errors) == 0, len(errors), errors)

    # 13. Frequency Caps
    def _validate_frequency_caps(self) -> ValidationRuleResult:
        errors = []
        # Group sent attempts by customer and channel
        cust_channel_sends = {}
        for s in self.dataset.get("send_attempts", []):
            if s["status"] == "SENT" and s["sent_at"]:
                key = (s["customer_id"], s["channel"])
                cust_channel_sends.setdefault(key, []).append(s["sent_at"])

        for (cid, ch), timestamps in cust_channel_sends.items():
            timestamps.sort()
            for idx, t1 in enumerate(timestamps):
                window_end = t1 + timedelta(days=7)
                sends_in_win = sum(1 for t2 in timestamps[idx:] if t1 <= t2 <= window_end)
                if sends_in_win > 3:
                    errors.append(f"Customer {cid} exceeded 7-day cap on channel {ch}: {sends_in_win} sends")
        return ValidationRuleResult("frequency_caps", len(errors) == 0, len(errors), errors)

    # 14. Attribution Window
    def _validate_attribution_window(self) -> ValidationRuleResult:
        errors = []
        for a in self.dataset.get("attributions", []):
            click_time = a["qualifying_click_at"]
            order_time = a["order_timestamp"]
            if order_time < click_time:
                errors.append(f"Attribution {a['attribution_id']} order_timestamp precedes click")
            if (order_time - click_time).days > 7:
                errors.append(f"Attribution {a['attribution_id']} exceeds 7-day window")
        return ValidationRuleResult("attribution_window", len(errors) == 0, len(errors), errors)

    # 15. Purchased-Cart Suppression
    def _validate_purchased_cart_suppression(self) -> ValidationRuleResult:
        errors = []
        purchased_carts = {o["cart_id"]: o["order_timestamp"] for o in self.dataset.get("orders", []) if o.get("cart_id")}
        for s in self.dataset.get("send_attempts", []):
            if s["status"] == "SENT" and s["cart_id"] in purchased_carts:
                purch_time = purchased_carts[s["cart_id"]]
                if s["sent_at"] and s["sent_at"] > purch_time:
                    errors.append(f"SendAttempt {s['send_id']} sent after cart {s['cart_id']} purchase")
        return ValidationRuleResult("purchased_cart_suppression", len(errors) == 0, len(errors), errors)

    # 16. Event Chronology
    def _validate_event_chronology(self) -> ValidationRuleResult:
        errors = []
        events_by_send = {}
        for e in self.dataset.get("communication_events", []):
            events_by_send.setdefault(e["send_id"], []).append(e)

        order_map = {"SEND": 1, "DELIVERED": 2, "BOUNCED": 2, "FAILED": 2, "OPENED": 3, "CLICKED": 4}
        for sid, evts in events_by_send.items():
            evts.sort(key=lambda x: x["timestamp"])
            prev_rank = 0
            for ev in evts:
                rank = order_map.get(ev["event_type"], 0)
                if rank < prev_rank:
                    errors.append(f"Send {sid} chronological anomaly: {ev['event_type']} out of sequence")
                prev_rank = rank
        return ValidationRuleResult("event_chronology", len(errors) == 0, len(errors), errors)
