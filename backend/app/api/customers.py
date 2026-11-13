from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerBase, CustomerDetail, CustomerListResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=CustomerListResponse)
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    preferred_channel: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    if search:
        query = query.filter(
            (Customer.customer_id.ilike(f"%{search}%")) |
            (Customer.first_name.ilike(f"%{search}%")) |
            (Customer.last_name.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )
    if preferred_channel:
        query = query.filter(Customer.preferred_channel == preferred_channel.upper())

    total = query.count()
    items = query.order_by(Customer.customer_id.asc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
