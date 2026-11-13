from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class AttributionBase(BaseModel):
    attribution_id: str
    order_id: str
    send_id: str
    campaign_id: str
    cart_id: Optional[str]
    order_timestamp: datetime
    qualifying_click_at: datetime
    latency_hours: int
    attributed_revenue: Decimal
    model: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttributionListResponse(BaseModel):
    total: int
    items: List[AttributionBase]

