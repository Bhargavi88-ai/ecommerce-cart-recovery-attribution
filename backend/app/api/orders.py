from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database import get_db
from app.models.order import Order
from app.schemas.order import OrderBase, OrderDetail, OrderListResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=OrderListResponse)
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    customer_id: Optional[str] = None,
    cart_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    if cart_id:
        query = query.filter(Order.cart_id == cart_id)
    if status:
        query = query.filter(Order.status == status.upper())

    total = query.count()
    items = query.order_by(Order.order_timestamp.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{order_id}", response_model=OrderDetail)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).options(joinedload(Order.order_lines)).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
