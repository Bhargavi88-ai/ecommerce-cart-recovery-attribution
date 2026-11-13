from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(32), primary_key=True, index=True)  # CUS-000001
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(128), nullable=False, index=True)
    phone = Column(String(32), nullable=False, index=True)
    preferred_channel = Column(String(16), nullable=False, default="EMAIL")  # EMAIL, SMS
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    consents = relationship("Consent", back_populates="customer", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="customer", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    send_attempts = relationship("SendAttempt", back_populates="customer", cascade="all, delete-orphan")
