import pytest
from datetime import datetime, timedelta, timezone
from app.services.abandonment_engine import AbandonmentDetectionEngine
from app.models.cart import Cart


def test_abandonment_boundary_threshold():
    engine = AbandonmentDetectionEngine(inactivity_minutes=60)
    now = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Inactive for 59 minutes -> NOT abandoned
    cart_59m = Cart(
        cart_id="CART-2026-000001",
        status="ACTIVE",
        last_activity_at=now - timedelta(minutes=59)
    )
    assert engine.is_cart_abandoned(cart_59m, reference_time=now, has_lines=True) is False

    # Inactive for 60 minutes -> Abandoned
    cart_60m = Cart(
        cart_id="CART-2026-000002",
        status="ACTIVE",
        last_activity_at=now - timedelta(minutes=60)
    )
    assert engine.is_cart_abandoned(cart_60m, reference_time=now, has_lines=True) is True

    # Inactive for 61 minutes -> Abandoned
    cart_61m = Cart(
        cart_id="CART-2026-000003",
        status="ACTIVE",
        last_activity_at=now - timedelta(minutes=61)
    )
    assert engine.is_cart_abandoned(cart_61m, reference_time=now, has_lines=True) is True


def test_empty_cart_never_abandoned():
    engine = AbandonmentDetectionEngine(inactivity_minutes=60)
    now = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    cart = Cart(
        cart_id="CART-2026-000004",
        status="ACTIVE",
        last_activity_at=now - timedelta(hours=5)
    )
    # has_lines = False
    assert engine.is_cart_abandoned(cart, reference_time=now, has_lines=False) is False


def test_purchased_cart_never_abandoned():
    engine = AbandonmentDetectionEngine(inactivity_minutes=60)
    now = datetime(2026, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    cart = Cart(
        cart_id="CART-2026-000005",
        status="ACTIVE",
        last_activity_at=now - timedelta(hours=5)
    )
    # is_purchased = True
    assert engine.is_cart_abandoned(cart, reference_time=now, has_lines=True, is_purchased=True) is False
