from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class CommunicationEventResponse(BaseModel):
    event_id: str
    send_id: str
    event_type: str
    timestamp: datetime
    metadata_json: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SendAttemptBase(BaseModel):
    send_id: str
    message_id: str
    campaign_id: str
    template_id: Optional[str]
    cart_id: str
    customer_id: str
    channel: str
    status: str
    suppression_reason: Optional[str]
    scheduled_at: datetime
    sent_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SendAttemptDetail(SendAttemptBase):
    communication_events: List[CommunicationEventResponse] = []


class SendAttemptListResponse(BaseModel):
    total: int
    items: List[SendAttemptBase]
