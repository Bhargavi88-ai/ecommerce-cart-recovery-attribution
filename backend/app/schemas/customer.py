from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class CustomerBase(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    preferred_channel: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerDetail(CustomerBase):
    pass


class CustomerListResponse(BaseModel):
    total: int
    items: List[CustomerBase]

