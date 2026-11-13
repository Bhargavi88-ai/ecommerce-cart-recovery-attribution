from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.anomaly import AnomalyRecord
from app.schemas.validation import AnomalyRecordResponse, AnomalyListResponse

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("", response_model=AnomalyListResponse)
def list_anomalies(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    issue_type: Optional[str] = None,
    affected_entity: Optional[str] = None,
    resolution_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnomalyRecord)
    if issue_type:
        query = query.filter(AnomalyRecord.issue_type == issue_type)
    if affected_entity:
        query = query.filter(AnomalyRecord.affected_entity == affected_entity)
    if resolution_status:
        query = query.filter(AnomalyRecord.resolution_status == resolution_status.upper())

    total = query.count()
    items = query.order_by(AnomalyRecord.detected_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.patch("/{anomaly_id}", response_model=AnomalyRecordResponse)
def update_anomaly_status(
    anomaly_id: str,
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    ano = db.query(AnomalyRecord).filter(AnomalyRecord.anomaly_id == anomaly_id).first()
    if not ano:
        raise HTTPException(status_code=404, detail="Anomaly record not found")
    ano.resolution_status = status.upper()
    db.commit()
    db.refresh(ano)
    return ano
