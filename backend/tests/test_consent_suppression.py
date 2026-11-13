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
