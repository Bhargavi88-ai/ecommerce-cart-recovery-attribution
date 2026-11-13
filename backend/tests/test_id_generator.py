import pytest
from app.generator.id_generator import (
    customer_id, cart_id, campaign_id, message_id, send_id, order_id, product_id
)


def test_customer_id_formatting():
    assert customer_id(1) == "CUS-000001"
    assert customer_id(99999) == "CUS-099999"


def test_cart_id_formatting():
    assert cart_id(1, 2026) == "CART-2026-000001"
    assert cart_id(50000, 2026) == "CART-2026-050000"


def test_campaign_id_formatting():
    assert campaign_id(1, 2026) == "CMP-2026-000001"
    assert campaign_id(2, 2026) == "CMP-2026-000002"


def test_message_id_formatting():
    assert message_id("CART-2026-000001", 1) == "MSG-CART-2026-000001-01"


def test_send_id_formatting():
    assert send_id(1, 2026) == "SEND-2026-000001"
    assert send_id(10000, 2026) == "SEND-2026-010000"


def test_order_id_formatting():
    assert order_id(1, 2026) == "ORD-2026-000001"


def test_product_id_formatting():
    assert product_id(1) == "PRD-000001"

