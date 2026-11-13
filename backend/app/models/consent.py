from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Consent(Base):
    __tablename__ = "consents"

    consent_id = Column(String(32), primary_key=True, index=True)  # CNS-000001
    customer_id = Column(String(32), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(16), nullable=False)  # EMAIL, SMS
    status = Column(String(16), nullable=False)   # OPT_IN, OPT_OUT
    effective_at = Column(DateTime, nullable=False, index=True)
    source = Column(String(64), nullable=False)   # CHECKOUT_CHECKBOX, PREFERENCE_CENTER, UNSUBSCRIBE_LINK
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    customer = relationship("Customer", back_populates="consents")

    __table_args__ = (
        Index("ix_consents_customer_channel_effective", "customer_id", "channel", "effective_at"),
    )

