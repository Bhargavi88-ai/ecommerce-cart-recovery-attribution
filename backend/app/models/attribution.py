from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Attribution(Base):
    __tablename__ = "attributions"

    attribution_id = Column(String(32), primary_key=True, index=True)  # ATTR-2026-000001
    order_id = Column(String(32), ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False, index=True)
    send_id = Column(String(32), ForeignKey("send_attempts.send_id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(String(32), ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False, index=True)
    cart_id = Column(String(32), ForeignKey("carts.cart_id", ondelete="SET NULL"), nullable=True, index=True)
    
    order_timestamp = Column(DateTime, nullable=False, index=True)
    qualifying_click_at = Column(DateTime, nullable=False, index=True)
    latency_hours = Column(Integer, nullable=False, default=0)
    attributed_revenue = Column(Numeric(10, 2), nullable=False)
    model = Column(String(32), nullable=False, default="LAST_CLICK")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Order", back_populates="attribution")
    send_attempt = relationship("SendAttempt", back_populates="attributions")
    campaign = relationship("Campaign", back_populates="attributions")

    __table_args__ = (
        Index("ix_attributions_campaign_order_time", "campaign_id", "order_timestamp"),
    )

