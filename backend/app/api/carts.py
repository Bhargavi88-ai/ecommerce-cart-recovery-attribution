from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database import get_db
from app.models.cart import Cart
from app.schemas.cart import CartBase, CartDetail, CartListResponse

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.get("", response_model=CartListResponse)
def list_carts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Cart)
    if status:
        query = query.filter(Cart.status == status.upper())
    if customer_id:
        query = query.filter(Cart.customer_id == customer_id)

    total = query.count()
    items = query.order_by(Cart.last_activity_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/abandoned", response_model=CartListResponse)
def list_abandoned_carts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Cart).filter(
        Cart.status.in_(["ABANDONED", "ELIGIBLE", "SUPPRESSED", "CAMPAIGN_SCHEDULED"])
    )
    total = query.count()
    items = query.order_by(Cart.abandoned_at.desc().nullslast()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/eligible", response_model=CartListResponse)
def list_eligible_carts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Cart).filter(Cart.status == "ELIGIBLE")
    total = query.count()
    items = query.order_by(Cart.last_activity_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/suppressed", response_model=CartListResponse)
def list_suppressed_carts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Cart).filter(Cart.status == "SUPPRESSED")
    total = query.count()
    items = query.order_by(Cart.last_activity_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{cart_id}", response_model=CartDetail)
def get_cart(cart_id: str, db: Session = Depends(get_db)):
    cart = db.query(Cart).options(joinedload(Cart.cart_lines)).filter(Cart.cart_id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart
