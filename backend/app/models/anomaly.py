from sqlalchemy import Column, String, DateTime, Text, Index
from datetime import datetime, timezone
from app.database import Base


class AnomalyRecord(Base):
    __tablename__ = "anomaly_records"

    anomaly_id = Column(String(32), primary_key=True, index=True)  # ANO-000001
    issue_type = Column(String(64), nullable=False, index=True)  # MESSAGE_AFTER_OPTOUT, CART_ABANDONED_AFTER_PURCHASE, DUPLICATE_ATTRIBUTION, STALE_CART_TOTAL
    affected_entity = Column(String(64), nullable=False, index=True)  # Customer, Cart, SendAttempt, Attribution
    affected_record_id = Column(String(64), nullable=False, index=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    observed_value = Column(Text, nullable=False)
    expected_value = Column(Text, nullable=False)
    ground_truth_label = Column(String(64), nullable=False, index=True)
    expected_decision = Column(String(128), nullable=False)
    actual_decision = Column(String(128), nullable=False)
    resolution_status = Column(String(32), nullable=False, default="DETECTED", index=True)  # DETECTED, RESOLVED, IGNORED

    __table_args__ = (
        Index("ix_anomalies_issue_entity", "issue_type", "affected_entity"),
    )

