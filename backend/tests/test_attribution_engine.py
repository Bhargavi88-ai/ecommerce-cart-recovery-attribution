import pytest
from datetime import datetime, timedelta, timezone
from app.services.attribution_engine import AttributionEngine


def test_last_click_deterministic_selection():
    engine = AttributionEngine(attribution_window_days=7)
    order_time = datetime(2026, 10, 5, 14, 0, 0, tzinfo=timezone.utc)

    # 3 clicks from different campaigns
    clicks = [
        {"send_id": "SEND-001", "campaign_id": "CMP-001", "clicked_at": order_time - timedelta(days=5)},
        {"send_id": "SEND-002", "campaign_id": "CMP-002", "clicked_at": order_time - timedelta(days=2)},  # WINNER (latest)
        {"send_id": "SEND-003", "campaign_id": "CMP-003", "clicked_at": order_time - timedelta(days=4)},
    ]

    winner, competing = engine.find_qualifying_attribution(order_time, clicks)
    assert winner is not None
    assert winner["campaign_id"] == "CMP-002"
    assert winner["send_id"] == "SEND-002"
    assert len(competing) == 2


def test_click_outside_lookback_window():
    engine = AttributionEngine(attribution_window_days=7)
    order_time = datetime(2026, 10, 15, 14, 0, 0, tzinfo=timezone.utc)

    # Click was 8 days prior (outside 7-day lookback)
    clicks = [
        {"send_id": "SEND-001", "campaign_id": "CMP-001", "clicked_at": order_time - timedelta(days=8)}
    ]

    winner, competing = engine.find_qualifying_attribution(order_time, clicks)
    assert winner is None
    assert len(competing) == 0


def test_click_after_order_never_attributed():
    engine = AttributionEngine(attribution_window_days=7)
    order_time = datetime(2026, 10, 5, 14, 0, 0, tzinfo=timezone.utc)

    # Click occurred 1 hour after the order was already placed
    clicks = [
        {"send_id": "SEND-001", "campaign_id": "CMP-001", "clicked_at": order_time + timedelta(hours=1)}
    ]

    winner, _ = engine.find_qualifying_attribution(order_time, clicks)
    assert winner is None
