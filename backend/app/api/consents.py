from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.consent import Consent
from app.schemas.consent import ConsentListResponse

router = APIRouter(prefix="/consents", tags=["Consents"])


@router.get("", response_model=ConsentListResponse)
def list_consents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    channel: Optional[str] = None,
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Consent)
    if customer_id:
        query = query.filter(Consent.customer_id == customer_id)
    if channel:
        query = query.filter(Consent.channel == channel.upper())
    if status:
        query = query.filter(Consent.status == status.upper())

    total = query.count()
    items = query.order_by(Consent.effective_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}
