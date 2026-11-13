from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models.campaign import Campaign, MessageTemplate
from app.schemas.campaign import CampaignBase, CampaignCreate, CampaignDetail, CampaignListResponse
from app.generator.id_generator import campaign_id, template_id

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("", response_model=CampaignListResponse)
def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    channel: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Campaign)
    if channel:
        query = query.filter(Campaign.channel == channel.upper())
    if is_active is not None:
        query = query.filter(Campaign.is_active == is_active)

    total = query.count()
    items = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.post("", response_model=CampaignBase, status_code=201)
def create_campaign(campaign_in: CampaignCreate, db: Session = Depends(get_db)):
    next_id = campaign_id(db.query(Campaign).count() + 1)
    new_camp = Campaign(
        campaign_id=next_id,
        name=campaign_in.name,
        channel=campaign_in.channel.upper(),
        trigger_delay_minutes=campaign_in.trigger_delay_minutes,
        discount_percent=campaign_in.discount_percent,
        is_active=campaign_in.is_active,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_camp)
    db.commit()
    db.refresh(new_camp)
    return new_camp


@router.get("/{c_id}", response_model=CampaignDetail)
def get_campaign(c_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).options(joinedload(Campaign.templates)).filter(Campaign.campaign_id == c_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

