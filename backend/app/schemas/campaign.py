from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class MessageTemplateResponse(BaseModel):
    template_id: str
    campaign_id: str
    channel: str
    variant: str
    subject: Optional[str]
    body_template: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CampaignBase(BaseModel):
    campaign_id: str
    name: str
    channel: str
    trigger_delay_minutes: int
    discount_percent: Decimal
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignCreate(BaseModel):
    name: str
    channel: str
    trigger_delay_minutes: int = 60
    discount_percent: Decimal = Decimal("0.00")
    is_active: bool = True


class CampaignDetail(CampaignBase):
    templates: List[MessageTemplateResponse] = []


class CampaignListResponse(BaseModel):
    total: int
    items: List[CampaignBase]

