from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class OrderLineResponse(BaseModel):
    order_line_id: str
    order_id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    order_id: str
    customer_id: str
    cart_id: Optional[str]
    total_amount: Decimal
    order_timestamp: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class OrderDetail(OrderBase):
    order_lines: List[OrderLineResponse] = []


class OrderListResponse(BaseModel):
    total: int
    items: List[OrderBase]

