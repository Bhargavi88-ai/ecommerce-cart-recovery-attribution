import pytest
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # Ensure all models are registered in Base.metadata
from app.database import Base, get_db
from app.main import app
from app.generator.synthetic_data_generator import SyntheticDataGenerator
from app.generator.db_loader import populate_database_from_dataset


@pytest.fixture(scope="session")
def test_dataset():
    gen = SyntheticDataGenerator(seed=20261022, scale="starter")
    return gen.generate_dataset()


@pytest.fixture(scope="session")
def db_session(test_dataset):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    populate_database_from_dataset(db, test_dataset)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
