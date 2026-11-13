import pytest
from datetime import datetime, timedelta, timezone
from app.services.consent_suppression_engine import ConsentAndSuppressionEngine, SuppressionReason


def test_independent_email_sms_consent():
    engine = ConsentAndSuppressionEngine()
    t0 = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)

    # Customer opted-in to Email, but not SMS
    consents = [
        {"channel": "EMAIL", "status": "OPT_IN", "effective_at": t0},
        {"channel": "SMS", "status": "OPT_OUT", "effective_at": t0}
    ]

    has_email, reason_email = engine.evaluate_consent_at(consents, "EMAIL", t0 + timedelta(hours=1))
    assert has_email is True
    assert reason_email is None

    has_sms, reason_sms = engine.evaluate_consent_at(consents, "SMS", t0 + timedelta(hours=1))
    assert has_sms is False
    assert reason_sms == SuppressionReason.CONSENT_WITHDRAWN


def test_consent_withdrawal_suppression():
    engine = ConsentAndSuppressionEngine()
    t0 = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    t_optout = datetime(2026, 10, 3, 10, 0, 0, tzinfo=timezone.utc)

    consents = [
        {"channel": "EMAIL", "status": "OPT_IN", "effective_at": t0},
        {"channel": "EMAIL", "status": "OPT_OUT", "effective_at": t_optout}
    ]

    # Before opt-out -> eligible
    has_consent_before, _ = engine.evaluate_consent_at(consents, "EMAIL", t0 + timedelta(days=1))
    assert has_consent_before is True

    # After opt-out -> suppressed with CONSENT_WITHDRAWN
    has_consent_after, reason = engine.evaluate_consent_at(consents, "EMAIL", t_optout + timedelta(hours=2))
    assert has_consent_after is False
    assert reason == SuppressionReason.CONSENT_WITHDRAWN


def test_frequency_cap_enforcement():
    engine = ConsentAndSuppressionEngine(max_sends_per_window=3, frequency_window_days=7)
    t0 = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 3 past sends in past 4 days
    past_sends = [
        {"channel": "EMAIL", "status": "SENT", "sent_at": t0 - timedelta(days=4)},
        {"channel": "EMAIL", "status": "SENT", "sent_at": t0 - timedelta(days=3)},
        {"channel": "EMAIL", "status": "SENT", "sent_at": t0 - timedelta(days=1)},
    ]

    # Attempt send at t0 -> Should be capped
    assert engine.check_frequency_cap(past_sends, "EMAIL", t0) is True

    # But SMS has 0 sends -> Should NOT be capped
    assert engine.check_frequency_cap(past_sends, "SMS", t0) is False

    # Attempt after 8 days -> Window expired -> NOT capped
    t_future = t0 + timedelta(days=8)
    assert engine.check_frequency_cap(past_sends, "EMAIL", t_future) is False


def test_purchased_cart_suppression():
    engine = ConsentAndSuppressionEngine()
    t0 = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    consents = [{"channel": "EMAIL", "status": "OPT_IN", "effective_at": t0}]

    is_eligible, reason = engine.evaluate_send_eligibility(
        channel="EMAIL",
        attempt_timestamp=t0,
        customer_consents=consents,
        past_customer_sends=[],
        is_cart_purchased=True,
        is_cart_abandoned=True,
        prior_cart_campaign_ids=[],
        proposed_campaign_id="CMP-2026-000001"
    )
    assert is_eligible is False
    assert reason == SuppressionReason.CART_PURCHASED


def test_duplicate_campaign_variant_suppression():
    engine = ConsentAndSuppressionEngine()
    t0 = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    consents = [{"channel": "EMAIL", "status": "OPT_IN", "effective_at": t0}]

    is_eligible, reason = engine.evaluate_send_eligibility(
        channel="EMAIL",
        attempt_timestamp=t0,
        customer_consents=consents,
        past_customer_sends=[],
        is_cart_purchased=False,
        is_cart_abandoned=True,
        prior_cart_campaign_ids=["CMP-2026-000001"],
        proposed_campaign_id="CMP-2026-000001"
    )
    assert is_eligible is False
    assert reason == SuppressionReason.DUPLICATE_CAMPAIGN


def test_unabandoned_cart_suppression():
    engine = ConsentAndSuppressionEngine()
    t0 = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    consents = [{"channel": "EMAIL", "status": "OPT_IN", "effective_at": t0}]

    is_eligible, reason = engine.evaluate_send_eligibility(
        channel="EMAIL",
        attempt_timestamp=t0,
        customer_consents=consents,
        past_customer_sends=[],
        is_cart_purchased=False,
        is_cart_abandoned=False,
        prior_cart_campaign_ids=[],
        proposed_campaign_id="CMP-2026-000001"
    )
    assert is_eligible is False
    assert reason == SuppressionReason.CART_NOT_ABANDONED


def test_frequency_cap_rolling_7_day_sliding_window():
    engine = ConsentAndSuppressionEngine(max_sends_per_window=3, frequency_window_days=7)
    t_base = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
    consents = [{"channel": "EMAIL", "status": "OPT_IN", "effective_at": t_base - timedelta(days=20)}]

    # Customer already has 3 past sends in the last 5 days
    past_sends = [
        {"channel": "EMAIL", "status": "SENT", "sent_at": t_base - timedelta(days=4)},
        {"channel": "EMAIL", "status": "SENT", "sent_at": t_base - timedelta(days=2)},
        {"channel": "EMAIL", "status": "SENT", "sent_at": t_base - timedelta(days=1)},
    ]

    # 4th send attempt at t_base -> Suppressed with FREQUENCY_CAP_REACHED
    is_eligible, reason = engine.evaluate_send_eligibility(
        channel="EMAIL",
        attempt_timestamp=t_base,
        customer_consents=consents,
        past_customer_sends=past_sends,
        is_cart_purchased=False,
        is_cart_abandoned=True,
        prior_cart_campaign_ids=[],
        proposed_campaign_id="CMP-2026-000002"
    )
    assert is_eligible is False
    assert reason == SuppressionReason.FREQUENCY_CAP_REACHED


def test_frequency_cap_4_in_7_days():
    """Verify that a customer receiving 3 sends cannot receive a 4th within rolling 7 days."""
    engine = ConsentAndSuppressionEngine(max_sends_per_window=3, frequency_window_days=7)
    t_start = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    consents = [{"channel": "EMAIL", "status": "OPT_IN", "effective_at": t_start - timedelta(days=5)}]

    sends = []
    # Send 1 on day 1 -> eligible
    ok1, r1 = engine.evaluate_send_eligibility("EMAIL", t_start, consents, sends, False, True, [], "C1")
    assert ok1 is True
    sends.append({"channel": "EMAIL", "status": "SENT", "sent_at": t_start})

    # Send 2 on day 3 -> eligible
    t2 = t_start + timedelta(days=2)
    ok2, r2 = engine.evaluate_send_eligibility("EMAIL", t2, consents, sends, False, True, [], "C2")
    assert ok2 is True
    sends.append({"channel": "EMAIL", "status": "SENT", "sent_at": t2})

    # Send 3 on day 5 -> eligible
    t3 = t_start + timedelta(days=4)
    ok3, r3 = engine.evaluate_send_eligibility("EMAIL", t3, consents, sends, False, True, [], "C3")
    assert ok3 is True
    sends.append({"channel": "EMAIL", "status": "SENT", "sent_at": t3})

    # Send 4 on day 6 (within 7 days of Send 1) -> SUPPRESSED
    t4 = t_start + timedelta(days=5)
    ok4, r4 = engine.evaluate_send_eligibility("EMAIL", t4, consents, sends, False, True, [], "C4")
    assert ok4 is False
    assert r4 == SuppressionReason.FREQUENCY_CAP_REACHED


def test_frequency_cap_exact_7_day_boundary():
    """Verify exact 7-day boundary condition: send at t0 + 7 days is still inside window, t0 + 7d + 1s rolls out."""
    engine = ConsentAndSuppressionEngine(max_sends_per_window=3, frequency_window_days=7)
    t0 = datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    consents = [{"channel": "EMAIL", "status": "OPT_IN", "effective_at": t0 - timedelta(days=1)}]

    # 3 past sends starting at t0
    past_sends = [
        {"channel": "EMAIL", "status": "SENT", "sent_at": t0},
        {"channel": "EMAIL", "status": "SENT", "sent_at": t0 + timedelta(days=1)},
        {"channel": "EMAIL", "status": "SENT", "sent_at": t0 + timedelta(days=2)},
    ]

    # At exact 7-day boundary (t0 + 7 days): past send at t0 is inside [t_attempt - 7d, t_attempt]
    t_exact_7d = t0 + timedelta(days=7)
    ok_exact, r_exact = engine.evaluate_send_eligibility("EMAIL", t_exact_7d, consents, past_sends, False, True, [], "C4")
    assert ok_exact is False
    assert r_exact == SuppressionReason.FREQUENCY_CAP_REACHED

    # Just 1 second past 7 days (t0 + 7 days + 1 second): first send at t0 falls out of rolling window -> only 2 sends remain -> eligible!
    t_past_boundary = t0 + timedelta(days=7, seconds=1)
    ok_past, r_past = engine.evaluate_send_eligibility("EMAIL", t_past_boundary, consents, past_sends, False, True, [], "C4")
    assert ok_past is True
    assert r_past is None

