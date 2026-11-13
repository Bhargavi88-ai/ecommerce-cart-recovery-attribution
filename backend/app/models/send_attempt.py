from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class SendAttempt(Base):
    __tablename__ = "send_attempts"

    send_id = Column(String(32), primary_key=True, index=True)  # SEND-2026-000001
    message_id = Column(String(64), nullable=False, index=True)  # MSG-CART-2026-000001-01
    campaign_id = Column(String(32), ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(String(32), ForeignKey("message_templates.template_id", ondelete="SET NULL"), nullable=True, index=True)
    cart_id = Column(String(32), ForeignKey("carts.cart_id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(32), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    
    channel = Column(String(16), nullable=False)  # EMAIL, SMS
    status = Column(String(32), nullable=False, default="QUEUED", index=True)  # QUEUED, SENT, SUPPRESSED, FAILED
    suppression_reason = Column(String(64), nullable=True, index=True)
    
    scheduled_at = Column(DateTime, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    campaign = relationship("Campaign", back_populates="send_attempts")
    template = relationship("MessageTemplate", back_populates="send_attempts")
    cart = relationship("Cart", back_populates="send_attempts")
    customer = relationship("Customer", back_populates="send_attempts")
    communication_events = relationship("CommunicationEvent", back_populates="send_attempt", cascade="all, delete-orphan")
    attributions = relationship("Attribution", back_populates="send_attempt")

    __table_args__ = (
        Index("ix_send_attempts_customer_channel_sent", "customer_id", "channel", "sent_at"),
        Index("ix_send_attempts_cart_campaign", "cart_id", "campaign_id"),
    )

