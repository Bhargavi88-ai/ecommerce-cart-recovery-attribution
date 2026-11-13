from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from app.models.customer import Customer
from app.models.cart import Cart
from app.models.campaign import Campaign
from app.models.send_attempt import SendAttempt
from app.models.communication_event import CommunicationEvent
from app.models.order import Order
from app.models.attribution import Attribution
from app.models.anomaly import AnomalyRecord


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview_kpis(self) -> Dict[str, Any]:
        total_customers = self.db.query(Customer).count()
        total_carts = self.db.query(Cart).count()
        
        abandoned_carts = self.db.query(Cart).filter(
            Cart.status.in_(["ABANDONED", "ELIGIBLE", "SUPPRESSED", "CAMPAIGN_SCHEDULED"])
        ).count()
        
        eligible_carts = self.db.query(Cart).filter(Cart.status == "ELIGIBLE").count()
        suppressed_carts = self.db.query(Cart).filter(Cart.status == "SUPPRESSED").count()
        recovered_carts = self.db.query(Cart).filter(Cart.status == "RECOVERED").count()
        
        total_campaigns = self.db.query(Campaign).count()
        total_sends = self.db.query(SendAttempt).count()
        sent_attempts = self.db.query(SendAttempt).filter(SendAttempt.status == "SENT").count()
        suppressed_sends = self.db.query(SendAttempt).filter(SendAttempt.status == "SUPPRESSED").count()
        
        delivered_count = self.db.query(CommunicationEvent).filter(
            CommunicationEvent.event_type == "DELIVERED"
        ).count()
        opened_count = self.db.query(CommunicationEvent).filter(
            CommunicationEvent.event_type == "OPENED"
        ).count()
        clicked_count = self.db.query(CommunicationEvent).filter(
            CommunicationEvent.event_type == "CLICKED"
        ).count()
        
        recovered_orders = self.db.query(Attribution).count()
        recovered_rev = float(
            self.db.query(func.coalesce(func.sum(Attribution.attributed_revenue), 0.0)).scalar() or 0.0
        )

        delivery_rate = round((delivered_count / max(1, sent_attempts)) * 100, 2)
        open_rate = round((opened_count / max(1, delivered_count)) * 100, 2)
        click_rate = round((clicked_count / max(1, opened_count)) * 100, 2)
        recovery_rate = round((recovered_orders / max(1, abandoned_carts + recovered_orders)) * 100, 2)
        conversion_rate = round((recovered_orders / max(1, sent_attempts)) * 100, 2)
        abandonment_rate = round((abandoned_carts / max(1, total_carts)) * 100, 2)
        rev_per_cart = round(recovered_rev / max(1, recovered_orders), 2)
        suppression_rate = round((suppressed_sends / max(1, total_sends)) * 100, 2)

        return {
            "total_customers": total_customers,
            "total_carts": total_carts,
            "abandoned_carts": abandoned_carts,
            "eligible_carts": eligible_carts,
            "suppressed_carts": suppressed_carts,
            "campaigns": total_campaigns,
            "send_attempts": total_sends,
            "delivery_rate": delivery_rate,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "recovered_orders": recovered_orders,
            "recovered_revenue": round(recovered_rev, 2),
            "recovery_rate": recovery_rate,
            "conversion_rate": conversion_rate,
            "abandonment_rate": abandonment_rate,
            "revenue_per_recovered_cart": rev_per_cart,
            "suppression_rate": suppression_rate
        }

    def get_lifecycle_distribution(self) -> List[Dict[str, Any]]:
        rows = self.db.query(Cart.status, func.count(Cart.cart_id)).group_by(Cart.status).all()
        return [{"name": r[0], "value": r[1]} for r in rows]

    def get_suppression_reasons(self) -> List[Dict[str, Any]]:
        rows = self.db.query(
            SendAttempt.suppression_reason, func.count(SendAttempt.send_id)
        ).filter(SendAttempt.suppression_reason.isnot(None)).group_by(SendAttempt.suppression_reason).all()
        return [{"name": r[0], "value": r[1]} for r in rows]

    def get_channel_performance(self) -> List[Dict[str, Any]]:
        channels = ["EMAIL", "SMS"]
        result = []
        for ch in channels:
            sends = self.db.query(SendAttempt).filter(SendAttempt.channel == ch, SendAttempt.status == "SENT").count()
            # Join events
            clicks = self.db.query(CommunicationEvent).join(SendAttempt).filter(
                SendAttempt.channel == ch, CommunicationEvent.event_type == "CLICKED"
            ).count()
            rev = float(
                self.db.query(func.coalesce(func.sum(Attribution.attributed_revenue), 0.0))
                .join(SendAttempt, Attribution.send_id == SendAttempt.send_id)
                .filter(SendAttempt.channel == ch).scalar() or 0.0
            )
            result.append({
                "name": ch,
                "value": sends,
                "secondary_value": round(rev, 2)
            })
        return result

    def get_anomaly_distribution(self) -> List[Dict[str, Any]]:
        rows = self.db.query(
            AnomalyRecord.issue_type, func.count(AnomalyRecord.anomaly_id)
        ).group_by(AnomalyRecord.issue_type).all()
        return [{"name": r[0], "value": r[1]} for r in rows]

    def get_revenue_recovery_trends(self) -> List[Dict[str, Any]]:
        # Group by campaign
        campaigns = self.db.query(Campaign).all()
        result = []
        for cmp in campaigns:
            rev = float(
                self.db.query(func.coalesce(func.sum(Attribution.attributed_revenue), 0.0))
                .filter(Attribution.campaign_id == cmp.campaign_id).scalar() or 0.0
            )
            conversions = self.db.query(Attribution).filter(Attribution.campaign_id == cmp.campaign_id).count()
            result.append({
                "name": cmp.name[:25],
                "value": round(rev, 2),
                "secondary_value": conversions
            })
        return result

    def get_campaign_performance_list(self) -> List[Dict[str, Any]]:
        campaigns = self.db.query(Campaign).all()
        metrics = []
        for c in campaigns:
            sends = self.db.query(SendAttempt).filter(SendAttempt.campaign_id == c.campaign_id, SendAttempt.status == "SENT").count()
            delivered = self.db.query(CommunicationEvent).join(SendAttempt).filter(
                SendAttempt.campaign_id == c.campaign_id, CommunicationEvent.event_type == "DELIVERED"
            ).count()
            opens = self.db.query(CommunicationEvent).join(SendAttempt).filter(
                SendAttempt.campaign_id == c.campaign_id, CommunicationEvent.event_type == "OPENED"
            ).count()
            clicks = self.db.query(CommunicationEvent).join(SendAttempt).filter(
                SendAttempt.campaign_id == c.campaign_id, CommunicationEvent.event_type == "CLICKED"
            ).count()
            conversions = self.db.query(Attribution).filter(Attribution.campaign_id == c.campaign_id).count()
            revenue = float(
                self.db.query(func.coalesce(func.sum(Attribution.attributed_revenue), 0.0))
                .filter(Attribution.campaign_id == c.campaign_id).scalar() or 0.0
            )
            conv_rate = round((conversions / max(1, sends)) * 100, 2)
            metrics.append({
                "campaign_id": c.campaign_id,
                "name": c.name,
                "channel": c.channel,
                "sends": sends,
                "delivered": delivered,
                "opens": opens,
                "clicks": clicks,
                "conversions": conversions,
                "revenue": round(revenue, 2),
                "conversion_rate": conv_rate
            })
        return metrics
