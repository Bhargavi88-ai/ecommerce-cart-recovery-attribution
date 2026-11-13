from datetime import datetime, timedelta, timezone
from typing import List, Optional
from app.models.cart import Cart
from app.config import settings


class AbandonmentDetectionEngine:
    def __init__(self, inactivity_minutes: int = settings.ABANDONMENT_INACTIVITY_MINUTES):
        self.inactivity_minutes = inactivity_minutes

    def is_cart_abandoned(
        self,
        cart: Cart,
        reference_time: Optional[datetime] = None,
        has_lines: bool = True,
        is_purchased: bool = False
    ) -> bool:
        """
        A cart is abandoned only when:
        1. It contains at least one valid product line.
        2. It has not been purchased.
        3. It is not already recovered.
        4. Its latest activity exceeds the configured inactivity period relative to reference_time.
        5. It meets applicable lifecycle conditions (not already cancelled/expired).
        """
        if not has_lines:
            return False
        if is_purchased or cart.status == "RECOVERED":
            return False
        if cart.status == "EXPIRED":
            return False

        now = reference_time or datetime.now(timezone.utc)
        inactivity_threshold = timedelta(minutes=self.inactivity_minutes)
        time_elapsed = now - cart.last_activity_at
        return time_elapsed >= inactivity_threshold

    def calculate_abandonment_timestamp(self, last_activity_at: datetime) -> datetime:
        """Deterministic abandonment timestamp calculated strictly from cart activity."""
        return last_activity_at + timedelta(minutes=self.inactivity_minutes)

    def evaluate_cart_status(
        self,
        cart: Cart,
        reference_time: Optional[datetime] = None,
        has_lines: bool = True,
        is_purchased: bool = False,
        is_suppressed: bool = False,
        is_scheduled: bool = False
    ) -> str:
        if is_purchased or cart.recovered_at is not None:
            return "RECOVERED"
        if not self.is_cart_abandoned(cart, reference_time, has_lines, is_purchased):
            return "ACTIVE"
        if is_scheduled:
            return "CAMPAIGN_SCHEDULED"
        if is_suppressed:
            return "SUPPRESSED"
        return "ELIGIBLE"

