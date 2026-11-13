from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class ConsentBase(BaseModel):
    consent_id: str
    customer_id: str
    channel: str
    status: str
    effective_at: datetime
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsentListResponse(BaseModel):
    total: int
    items: List[ConsentBase]

