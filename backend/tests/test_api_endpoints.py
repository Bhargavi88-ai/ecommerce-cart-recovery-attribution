import pytest


def test_healthcheck(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"


def test_customers_api(client):
    res = client.get("/api/customers?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert len(data["items"]) == 10

    # Single customer
    cust_id = data["items"][0]["customer_id"]
    single_res = client.get(f"/api/customers/{cust_id}")
    assert single_res.status_code == 200
    assert single_res.json()["customer_id"] == cust_id


def test_carts_api(client):
    res = client.get("/api/carts?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0

    # Abandoned carts
    ab_res = client.get("/api/carts/abandoned?limit=10")
    assert ab_res.status_code == 200
    assert ab_res.json()["total"] > 0

    # Eligible carts
    el_res = client.get("/api/carts/eligible?limit=10")
    assert el_res.status_code == 200

    # Suppressed carts
    sup_res = client.get("/api/carts/suppressed?limit=10")
    assert sup_res.status_code == 200


def test_campaigns_api(client):
    res = client.get("/api/campaigns")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 3

    # Create new campaign
    payload = {
        "name": "Spring Special Push",
        "channel": "EMAIL",
        "trigger_delay_minutes": 90,
        "discount_percent": 20.0,
        "is_active": True
    }
    create_res = client.post("/api/campaigns", json=payload)
    assert create_res.status_code == 201
    assert create_res.json()["name"] == "Spring Special Push"


def test_send_attempts_api(client):
    res = client.get("/api/send-attempts?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0


def test_orders_and_attributions_api(client):
    res = client.get("/api/orders?limit=10")
    assert res.status_code == 200
    assert res.json()["total"] > 0

    attr_res = client.get("/api/attributions?limit=10")
    assert attr_res.status_code == 200
    assert attr_res.json()["total"] > 0


def test_analytics_overview_api(client):
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    kpis = data["kpis"]
    assert kpis["total_customers"] > 0
    assert kpis["total_carts"] > 0
    assert kpis["recovered_revenue"] > 0
    assert "cart_lifecycle_distribution" in data
    assert "channel_performance" in data


def test_anomalies_api(client):
    res = client.get("/api/anomalies")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 4
    issue_types = {item["issue_type"] for item in data["items"]}
    assert "MESSAGE_AFTER_OPTOUT" in issue_types
    assert "CART_ABANDONED_AFTER_PURCHASE" in issue_types
    assert "DUPLICATE_ATTRIBUTION" in issue_types
    assert "STALE_CART_TOTAL" in issue_types


def test_exports_api(client):
    res = client.get("/api/exports")
    assert res.status_code == 200
    data = res.json()
    assert "files" in data

