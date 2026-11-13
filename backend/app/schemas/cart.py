from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class CartLineResponse(BaseModel):
    cart_line_id: str
    cart_id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class CartBase(BaseModel):
    cart_id: str
    customer_id: str
    session_id: Optional[str]
    status: str
    subtotal: Decimal
    discount_total: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    abandoned_at: Optional[datetime]
    recovered_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CartDetail(CartBase):
    cart_lines: List[CartLineResponse] = []


class CartListResponse(BaseModel):
    total: int
    items: List[CartBase]

