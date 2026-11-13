import pytest
from app.generator.anomaly_fixtures import AnomalyFixtureBuilder


def test_mandatory_anomaly_fixtures_structure():
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    # 1. MESSAGE_AFTER_OPTOUT
    a1 = AnomalyFixtureBuilder.create_message_after_optout(
        1, "CUS-000001", "SEND-000001", now, now
    )
    assert a1["issue_type"] == "MESSAGE_AFTER_OPTOUT"
    assert a1["affected_entity"] == "SendAttempt"
    assert a1["expected_decision"] == "SUPPRESS_SEND"
    assert a1["resolution_status"] == "DETECTED"

    # 2. CART_ABANDONED_AFTER_PURCHASE
    a2 = AnomalyFixtureBuilder.create_cart_abandoned_after_purchase(
        2, "CART-2026-000001", "ORD-2026-000001", now, now
    )
    assert a2["issue_type"] == "CART_ABANDONED_AFTER_PURCHASE"
    assert a2["affected_entity"] == "Cart"
    assert a2["expected_decision"] == "MARK_RECOVERED"

    # 3. DUPLICATE_ATTRIBUTION
    a3 = AnomalyFixtureBuilder.create_duplicate_attribution(
        3, "ORD-2026-000001", "ATTR-01", "ATTR-02", "CMP-01", "CMP-02"
    )
    assert a3["issue_type"] == "DUPLICATE_ATTRIBUTION"
    assert a3["affected_entity"] == "Attribution"
    assert a3["expected_decision"] == "SINGLE_PRIMARY_ATTRIBUTION"

    # 4. STALE_CART_TOTAL
    a4 = AnomalyFixtureBuilder.create_stale_cart_total(
        4, "CART-2026-000001", 150.00, 105.00
    )
    assert a4["issue_type"] == "STALE_CART_TOTAL"
    assert a4["affected_entity"] == "Cart"
    assert a4["expected_decision"] == "RECONCILE_LINE_SUM"


def test_message_after_optout_anomaly_semantics():
    from datetime import datetime, timezone, timedelta
    t_optout = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    t_send = t_optout + timedelta(hours=2)
    a = AnomalyFixtureBuilder.create_message_after_optout(
        1, "CUS-000002", "SEND-2026-000099", t_send, t_optout
    )
    assert a["ground_truth_label"] == "UNLAWFUL_SEND_POST_WITHDRAWAL"
    assert a["expected_decision"] == "SUPPRESS_SEND"
    assert "Message sent" in a["observed_value"]


def test_cart_abandoned_after_purchase_semantics():
    from datetime import datetime, timezone, timedelta
    t_purch = datetime(2026, 10, 2, 8, 0, 0, tzinfo=timezone.utc)
    t_aband = t_purch + timedelta(hours=3)
    a = AnomalyFixtureBuilder.create_cart_abandoned_after_purchase(
        2, "CART-2026-000099", "ORD-2026-000099", t_purch, t_aband
    )
    assert a["ground_truth_label"] == "FALSE_ABANDONMENT_AFTER_PURCHASE"
    assert a["expected_decision"] == "MARK_RECOVERED"
    assert "Cart marked ABANDONED" in a["observed_value"]


def test_duplicate_attribution_semantics():
    a = AnomalyFixtureBuilder.create_duplicate_attribution(
        3, "ORD-2026-000099", "ATTR-0001", "ATTR-0002", "CMP-2026-000001", "CMP-2026-000002"
    )
    assert a["ground_truth_label"] == "DOUBLE_COUNTED_ORDER_REVENUE"
    assert a["expected_decision"] == "SINGLE_PRIMARY_ATTRIBUTION"
    assert "double-attributed" in a["observed_value"]


def test_stale_cart_total_semantics():
    a = AnomalyFixtureBuilder.create_stale_cart_total(
        4, "CART-2026-000099", stored_total=250.00, calculated_total=200.00
    )
    assert a["ground_truth_label"] == "DESYNCHRONIZED_CART_LINE_PRICE"
    assert a["expected_decision"] == "RECONCILE_LINE_SUM"
    assert "Stored total_amount=250.00" in a["observed_value"]
    assert "Calculated lines sum=200.00" in a["expected_value"]

