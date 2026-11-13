from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(32), primary_key=True, index=True)  # SES-2026-000001
    customer_id = Column(String(32), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    device_type = Column(String(32), nullable=False, default="DESKTOP")  # DESKTOP, MOBILE, TABLET
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    started_at = Column(DateTime, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="sessions")
    carts = relationship("Cart", back_populates="session")

