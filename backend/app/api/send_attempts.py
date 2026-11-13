from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database import get_db
from app.models.send_attempt import SendAttempt
from app.schemas.send_attempt import SendAttemptBase, SendAttemptDetail, SendAttemptListResponse

router = APIRouter(prefix="/send-attempts", tags=["Send Attempts"])


@router.get("", response_model=SendAttemptListResponse)
def list_send_attempts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    channel: Optional[str] = None,
    campaign_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    suppression_reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SendAttempt)
    if status:
        query = query.filter(SendAttempt.status == status.upper())
    if channel:
        query = query.filter(SendAttempt.channel == channel.upper())
    if campaign_id:
        query = query.filter(SendAttempt.campaign_id == campaign_id)
    if customer_id:
        query = query.filter(SendAttempt.customer_id == customer_id)
    if suppression_reason:
        query = query.filter(SendAttempt.suppression_reason == suppression_reason)

    total = query.count()
    items = query.order_by(SendAttempt.scheduled_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{send_id}", response_model=SendAttemptDetail)
def get_send_attempt(send_id: str, db: Session = Depends(get_db)):
    attempt = db.query(SendAttempt).options(
        joinedload(SendAttempt.communication_events)
    ).filter(SendAttempt.send_id == send_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Send attempt not found")
    return attempt
