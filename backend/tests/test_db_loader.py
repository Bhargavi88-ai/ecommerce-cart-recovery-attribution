import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.generator.db_loader import rebuild_database
from app.generator.synthetic_data_generator import SyntheticDataGenerator


def test_db_loader_rebuild_starter():
    """Verify that rebuild_database correctly populates SQLite database and counts match generated dataset."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    seed = 20261022
    scale = "starter"
    counts = rebuild_database(seed=seed, scale=scale, engine=engine, session_factory=TestingSessionLocal)

    # Compare against generator dataset
    gen = SyntheticDataGenerator(scale=scale, seed=seed)
    expected_data = gen.generate_dataset()

    assert counts["customers"] == len(expected_data["customers"])
    assert counts["carts"] == len(expected_data["carts"])
    assert counts["send_attempts"] == len(expected_data["send_attempts"])
    assert counts["orders"] == len(expected_data["orders"])
    assert counts["attributions"] == len(expected_data["attributions"])
    assert counts["products"] == len(expected_data["products"])
    assert counts["consents"] == len(expected_data["consents"])
    assert counts["sessions"] == len(expected_data["sessions"])
    assert counts["campaigns"] == len(expected_data["campaigns"])
    assert counts["message_templates"] == len(expected_data["message_templates"])
    assert counts["cart_lines"] == len(expected_data["cart_lines"])
    assert counts["order_lines"] == len(expected_data["order_lines"])
    assert counts["communication_events"] == len(expected_data["communication_events"])
    assert counts["anomaly_records"] == len(expected_data["anomalies"])

