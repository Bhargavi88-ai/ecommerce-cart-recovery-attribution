from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from decimal import Decimal


class OverviewKpis(BaseModel):
    total_customers: int
    total_carts: int
    abandoned_carts: int
    eligible_carts: int
    suppressed_carts: int
    campaigns: int
    send_attempts: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    recovered_orders: int
    recovered_revenue: float
    recovery_rate: float
    conversion_rate: float
    abandonment_rate: float
    revenue_per_recovered_cart: float
    suppression_rate: float


class ChartDataPoint(BaseModel):
    name: str
    value: float
    secondary_value: Optional[float] = None


class OverviewAnalyticsResponse(BaseModel):
    kpis: OverviewKpis
    cart_lifecycle_distribution: List[ChartDataPoint]
    channel_performance: List[ChartDataPoint]
    suppression_reasons: List[ChartDataPoint]
    revenue_recovery_trends: List[ChartDataPoint]
    anomaly_distribution: List[ChartDataPoint]


class CampaignPerformanceMetric(BaseModel):
    campaign_id: str
    name: str
    channel: str
    sends: int
    delivered: int
    opens: int
    clicks: int
    conversions: int
    revenue: float
    conversion_rate: float
