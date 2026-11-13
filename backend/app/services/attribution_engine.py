from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from app.config import settings


class AttributionEngine:
    """
    Deterministic Last-Click Attribution Engine.
    Attributes an order to the latest qualifying campaign CLICK event
    occurring strictly before order_timestamp and within the attribution window (default 7 days).
    Enforces 1:1 attribution per order (no revenue double-counting).
    """

    def __init__(self, attribution_window_days: int = settings.ATTRIBUTION_WINDOW_DAYS):
        self.attribution_window_days = attribution_window_days

    def find_qualifying_attribution(
        self,
        order_timestamp: datetime,
        candidate_clicks: List[Dict[str, Any]]
    ) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        candidate_clicks: list of dicts with:
        {
            "send_id": str,
            "campaign_id": str,
            "cart_id": Optional[str],
            "clicked_at": datetime
        }
        Returns:
            (winning_claim, competing_claims)
        """
        window_start = order_timestamp - timedelta(days=self.attribution_window_days)

        # Filter strictly eligible clicks:
        # 1. clicked_at < order_timestamp
        # 2. clicked_at >= window_start
        eligible_clicks = [
            c for c in candidate_clicks
            if window_start <= c["clicked_at"] < order_timestamp
        ]

        if not eligible_clicks:
            return None, []

        # Sort descending by clicked_at -> latest click wins
        eligible_clicks.sort(key=lambda x: x["clicked_at"], reverse=True)
        winner = eligible_clicks[0]
        competing = eligible_clicks[1:]

        return winner, competing

    def calculate_latency_hours(self, clicked_at: datetime, order_timestamp: datetime) -> int:
        delta = order_timestamp - clicked_at
        return max(0, int(delta.total_seconds() // 3600))
