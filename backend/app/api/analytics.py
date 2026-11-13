from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    OverviewAnalyticsResponse, OverviewKpis, CampaignPerformanceMetric, ChartDataPoint
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewAnalyticsResponse)
def get_overview_analytics(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    kpis = svc.get_overview_kpis()
    lifecycle = svc.get_lifecycle_distribution()
    channels = svc.get_channel_performance()
    suppression = svc.get_suppression_reasons()
    rev_trends = svc.get_revenue_recovery_trends()
    anomalies = svc.get_anomaly_distribution()

    return {
        "kpis": kpis,
        "cart_lifecycle_distribution": lifecycle,
        "channel_performance": channels,
        "suppression_reasons": suppression,
        "revenue_recovery_trends": rev_trends,
        "anomaly_distribution": anomalies
    }


@router.get("/campaign-performance", response_model=List[CampaignPerformanceMetric])
def get_campaign_performance(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return svc.get_campaign_performance_list()


@router.get("/recovery")
def get_recovery_analytics(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    kpis = svc.get_overview_kpis()
    return {
        "recovered_orders": kpis["recovered_orders"],
        "recovered_revenue": kpis["recovered_revenue"],
        "recovery_rate": kpis["recovery_rate"],
        "revenue_per_recovered_cart": kpis["revenue_per_recovered_cart"],
        "trends": svc.get_revenue_recovery_trends()
    }


@router.get("/revenue")
def get_revenue_analytics(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    kpis = svc.get_overview_kpis()
    return {
        "total_revenue_recovered": kpis["recovered_revenue"],
        "by_campaign": svc.get_revenue_recovery_trends(),
        "by_channel": svc.get_channel_performance()
    }


@router.get("/attribution")
def get_attribution_analytics(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return {
        "attribution_model": "LAST_CLICK",
        "lookback_window_days": 7,
        "total_attributed_revenue": svc.get_overview_kpis()["recovered_revenue"],
        "campaign_attribution": svc.get_campaign_performance_list()
    }

