from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(String(32), primary_key=True, index=True)  # CMP-2026-000001
    name = Column(String(128), nullable=False)
    channel = Column(String(16), nullable=False)  # EMAIL, SMS
    trigger_delay_minutes = Column(Integer, nullable=False, default=60)
    discount_percent = Column(Numeric(5, 2), nullable=False, default=0.00)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    templates = relationship("MessageTemplate", back_populates="campaign", cascade="all, delete-orphan")
    send_attempts = relationship("SendAttempt", back_populates="campaign")
    attributions = relationship("Attribution", back_populates="campaign")


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    template_id = Column(String(32), primary_key=True, index=True)  # TMPL-000001
    campaign_id = Column(String(32), ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(16), nullable=False)  # EMAIL, SMS
    variant = Column(String(8), nullable=False, default="A")  # A, B
    subject = Column(String(255), nullable=True)
    body_template = Column(String(1024), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="templates")
    send_attempts = relationship("SendAttempt", back_populates="template")
