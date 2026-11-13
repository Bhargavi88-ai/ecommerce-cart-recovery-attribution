import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    APP_NAME: str = "E-Commerce Abandoned Cart Recovery & Attribution System"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../cart_recovery.db'))}"
    )
    
    # Business Rules
    ABANDONMENT_INACTIVITY_MINUTES: int = 60
    ATTRIBUTION_WINDOW_DAYS: int = 7
    FREQUENCY_CAP_MAX_SENDS: int = 3
    FREQUENCY_CAP_WINDOW_DAYS: int = 7

    # Generator Seeds & Scales
    DEFAULT_SEED: int = 20261022
    STARTER_CUSTOMERS: int = 1000
    STARTER_CARTS: int = 2000
    FULL_CUSTOMERS: int = 25000
    FULL_CARTS: int = 50000
    FULL_ABANDONED_TARGET: int = 20000
    FULL_SENDS_TARGET: int = 10000

    # Paths
    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    EXPORTS_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, "data/exports"))
    REPORTS_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, "data/reports"))
    MANIFESTS_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, "data/manifests"))

    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }


settings = Settings()
