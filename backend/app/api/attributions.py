from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any
from app.database import get_db
from app.models.attribution import Attribution
from app.schemas.attribution import AttributionBase, AttributionListResponse

router = APIRouter(prefix="/attributions", tags=["Attribution"])


@router.get("", response_model=AttributionListResponse)
def list_attributions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    campaign_id: Optional[str] = None,
    order_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Attribution)
    if campaign_id:
        query = query.filter(Attribution.campaign_id == campaign_id)
    if order_id:
        query = query.filter(Attribution.order_id == order_id)

    total = query.count()
    items = query.order_by(Attribution.order_timestamp.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}

