from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class CommunicationEvent(Base):
    __tablename__ = "communication_events"

    event_id = Column(String(32), primary_key=True, index=True)  # EVT-2026-000001
    send_id = Column(String(32), ForeignKey("send_attempts.send_id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(32), nullable=False, index=True)  # SEND, DELIVERED, OPENED, CLICKED, FAILED, BOUNCED
    timestamp = Column(DateTime, nullable=False, index=True)
    metadata_json = Column(Text, nullable=True)

    # Relationships
    send_attempt = relationship("SendAttempt", back_populates="communication_events")

    __table_args__ = (
        Index("ix_comm_events_send_type_time", "send_id", "event_type", "timestamp"),
    )
