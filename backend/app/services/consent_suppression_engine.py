from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from app.models.consent import Consent
from app.models.send_attempt import SendAttempt
from app.config import settings


class SuppressionReason:
    NO_EMAIL_CONSENT = "NO_EMAIL_CONSENT"
    NO_SMS_CONSENT = "NO_SMS_CONSENT"
    CONSENT_WITHDRAWN = "CONSENT_WITHDRAWN"
    CART_PURCHASED = "CART_PURCHASED"
    FREQUENCY_CAP_REACHED = "FREQUENCY_CAP_REACHED"
    DUPLICATE_CAMPAIGN = "DUPLICATE_CAMPAIGN"
    CART_NOT_ABANDONED = "CART_NOT_ABANDONED"
    INVALID_CONTACT = "INVALID_CONTACT"


class ConsentAndSuppressionEngine:
    def __init__(
        self,
        max_sends_per_window: int = settings.FREQUENCY_CAP_MAX_SENDS,
        frequency_window_days: int = settings.FREQUENCY_CAP_WINDOW_DAYS
    ):
        self.max_sends_per_window = max_sends_per_window
        self.frequency_window_days = frequency_window_days

    def evaluate_consent_at(
        self,
        customer_consents: List[Any],
        channel: str,
        target_timestamp: datetime
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluates independent channel consent at a given point in time.
        Finds the most recent consent record for this channel where effective_at <= target_timestamp.
        Supports both dict and ORM model instances.
        """
        def get_field(item: Any, field: str):
            return item.get(field) if isinstance(item, dict) else getattr(item, field)

        relevant = [
            c for c in customer_consents
            if get_field(c, "channel").upper() == channel.upper()
            and get_field(c, "effective_at") <= target_timestamp
        ]
        if not relevant:
            reason = SuppressionReason.NO_EMAIL_CONSENT if channel.upper() == "EMAIL" else SuppressionReason.NO_SMS_CONSENT
            return False, reason

        # Sort by effective_at descending
        relevant.sort(key=lambda x: get_field(x, "effective_at"), reverse=True)
        latest_consent = relevant[0]
        st = get_field(latest_consent, "status").upper()

        if st == "OPT_OUT":
            return False, SuppressionReason.CONSENT_WITHDRAWN
        elif st == "OPT_IN":
            return True, None
        else:
            reason = SuppressionReason.NO_EMAIL_CONSENT if channel.upper() == "EMAIL" else SuppressionReason.NO_SMS_CONSENT
            return False, reason

    def check_frequency_cap(
        self,
        past_sends: List[Any],
        channel: str,
        attempt_timestamp: datetime
    ) -> bool:
        """
        Enforce max recovery messages (default 3) per customer per channel within rolling 7-day window.
        Returns True if cap reached (i.e. should suppress), False if eligible.
        Only counts successfully sent messages (status == 'SENT').
        Supports both dict and ORM model instances.
        """
        def get_field(item: Any, field: str):
            return item.get(field) if isinstance(item, dict) else getattr(item, field)

        window_start = attempt_timestamp - timedelta(days=self.frequency_window_days)
        recent_sends = [
            s for s in past_sends
            if get_field(s, "channel").upper() == channel.upper()
            and get_field(s, "status") == "SENT"
            and get_field(s, "sent_at") is not None
            and window_start <= get_field(s, "sent_at") <= attempt_timestamp
        ]
        return len(recent_sends) >= self.max_sends_per_window

    def evaluate_send_eligibility(
        self,
        channel: str,
        attempt_timestamp: datetime,
        customer_consents: List[Consent],
        past_customer_sends: List[SendAttempt],
        is_cart_purchased: bool,
        is_cart_abandoned: bool,
        prior_cart_campaign_ids: List[str],
        proposed_campaign_id: str,
        contact_valid: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Master deterministic suppression evaluator.
        Returns (is_eligible, suppression_reason).
        """
        if not contact_valid:
            return False, SuppressionReason.INVALID_CONTACT

        if is_cart_purchased:
            return False, SuppressionReason.CART_PURCHASED

        if not is_cart_abandoned:
            return False, SuppressionReason.CART_NOT_ABANDONED

        if proposed_campaign_id in prior_cart_campaign_ids:
            return False, SuppressionReason.DUPLICATE_CAMPAIGN

        # Consent evaluation
        has_consent, consent_reason = self.evaluate_consent_at(
            customer_consents, channel, attempt_timestamp
        )
        if not has_consent:
            return False, consent_reason

        # Frequency cap evaluation
        if self.check_frequency_cap(past_customer_sends, channel, attempt_timestamp):
            return False, SuppressionReason.FREQUENCY_CAP_REACHED

        return True, None
