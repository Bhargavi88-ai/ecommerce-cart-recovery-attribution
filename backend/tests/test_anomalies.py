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
