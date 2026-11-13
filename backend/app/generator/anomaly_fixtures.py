from datetime import datetime, timezone
from typing import Dict, Any, List
from app.generator.id_generator import anomaly_id


class AnomalyFixtureBuilder:
    """
    Creates explicitly labeled anomaly fixtures with full metadata
    as mandated by Section 10 of specification:
    1. MESSAGE_AFTER_OPTOUT
    2. CART_ABANDONED_AFTER_PURCHASE
    3. DUPLICATE_ATTRIBUTION
    4. STALE_CART_TOTAL
    """

    @staticmethod
    def create_message_after_optout(
        counter: int,
        customer_id: str,
        send_id: str,
        sent_at: datetime,
        optout_time: datetime
    ) -> Dict[str, Any]:
        return {
            "anomaly_id": anomaly_id(counter),
            "issue_type": "MESSAGE_AFTER_OPTOUT",
            "affected_entity": "SendAttempt",
            "affected_record_id": send_id,
            "detected_at": datetime.now(timezone.utc),
            "observed_value": f"Message sent at {sent_at.isoformat()} after consent opt-out at {optout_time.isoformat()}",
            "expected_value": "SendAttempt suppressed with reason CONSENT_WITHDRAWN",
            "ground_truth_label": "UNLAWFUL_SEND_POST_WITHDRAWAL",
            "expected_decision": "SUPPRESS_SEND",
            "actual_decision": "DISPATCHED_MESSAGE",
            "resolution_status": "DETECTED"
        }

    @staticmethod
    def create_cart_abandoned_after_purchase(
        counter: int,
        cart_id: str,
        order_id: str,
        purchase_time: datetime,
        abandonment_time: datetime
    ) -> Dict[str, Any]:
        return {
            "anomaly_id": anomaly_id(counter),
            "issue_type": "CART_ABANDONED_AFTER_PURCHASE",
            "affected_entity": "Cart",
            "affected_record_id": cart_id,
            "detected_at": datetime.now(timezone.utc),
            "observed_value": f"Cart marked ABANDONED at {abandonment_time.isoformat()} despite order {order_id} placed at {purchase_time.isoformat()}",
            "expected_value": "Cart status RECOVERED with abandoned_at = NULL",
            "ground_truth_label": "FALSE_ABANDONMENT_AFTER_PURCHASE",
            "expected_decision": "MARK_RECOVERED",
            "actual_decision": "MARK_ABANDONED",
            "resolution_status": "DETECTED"
        }

    @staticmethod
    def create_duplicate_attribution(
        counter: int,
        order_id: str,
        first_attr_id: str,
        second_attr_id: str,
        first_campaign: str,
        second_campaign: str
    ) -> Dict[str, Any]:
        return {
            "anomaly_id": anomaly_id(counter),
            "issue_type": "DUPLICATE_ATTRIBUTION",
            "affected_entity": "Attribution",
            "affected_record_id": order_id,
            "detected_at": datetime.now(timezone.utc),
            "observed_value": f"Order {order_id} double-attributed to {first_campaign} ({first_attr_id}) and {second_campaign} ({second_attr_id})",
            "expected_value": "Order attributed strictly once to winning last-click campaign",
            "ground_truth_label": "DOUBLE_COUNTED_ORDER_REVENUE",
            "expected_decision": "SINGLE_PRIMARY_ATTRIBUTION",
            "actual_decision": "DUPLICATE_MULTI_CLAIM",
            "resolution_status": "DETECTED"
        }

    @staticmethod
    def create_stale_cart_total(
        counter: int,
        cart_id: str,
        stored_total: float,
        calculated_total: float
    ) -> Dict[str, Any]:
        return {
            "anomaly_id": anomaly_id(counter),
            "issue_type": "STALE_CART_TOTAL",
            "affected_entity": "Cart",
            "affected_record_id": cart_id,
            "detected_at": datetime.now(timezone.utc),
            "observed_value": f"Stored total_amount={stored_total:.2f}",
            "expected_value": f"Calculated lines sum={calculated_total:.2f}",
            "ground_truth_label": "DESYNCHRONIZED_CART_LINE_PRICE",
            "expected_decision": "RECONCILE_LINE_SUM",
            "actual_decision": "STALE_TOTAL_PERSISTED",
            "resolution_status": "DETECTED"
        }

