import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.generator.id_generator import communication_event_id


class SimulatedCommunicationProvider:
    """
    Simulates delivery provider event lifecycle:
    SEND -> DELIVERED (or BOUNCED/FAILED) -> OPENED -> CLICKED.
    Strict chronological guarantee:
    sent_at <= delivered_at <= opened_at <= clicked_at
    """

    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random(20261022)

    def simulate_events(
        self,
        send_id: str,
        channel: str,
        sent_at: datetime,
        global_event_counter_ref: List[int]
    ) -> List[Dict[str, Any]]:
        events = []

        # 1. SEND event
        global_event_counter_ref[0] += 1
        events.append({
            "event_id": communication_event_id(global_event_counter_ref[0]),
            "send_id": send_id,
            "event_type": "SEND",
            "timestamp": sent_at,
            "metadata_json": '{"status": "dispatched"}'
        })

        # Failure / bounce check (approx 4%)
        is_bounce = self.rng.random() < 0.04
        if is_bounce:
            global_event_counter_ref[0] += 1
            bounce_time = sent_at + timedelta(seconds=self.rng.randint(5, 60))
            events.append({
                "event_id": communication_event_id(global_event_counter_ref[0]),
                "send_id": send_id,
                "event_type": "BOUNCED",
                "timestamp": bounce_time,
                "metadata_json": '{"reason": "mailbox_unavailable"}'
            })
            return events

        # 2. DELIVERED event (within 1 to 5 minutes)
        delivery_time = sent_at + timedelta(seconds=self.rng.randint(15, 300))
        global_event_counter_ref[0] += 1
        events.append({
            "event_id": communication_event_id(global_event_counter_ref[0]),
            "send_id": send_id,
            "event_type": "DELIVERED",
            "timestamp": delivery_time,
            "metadata_json": '{"delivery_latency_sec": 45}'
        })

        # 3. OPENED event (higher for SMS ~85%, email ~45%)
        open_rate = 0.85 if channel.upper() == "SMS" else 0.45
        if self.rng.random() < open_rate:
            open_time = delivery_time + timedelta(seconds=self.rng.randint(60, 3600))
            global_event_counter_ref[0] += 1
            events.append({
                "event_id": communication_event_id(global_event_counter_ref[0]),
                "send_id": send_id,
                "event_type": "OPENED",
                "timestamp": open_time,
                "metadata_json": '{"client": "mobile_app"}'
            })

            # 4. CLICKED event (approx 30% of openers click)
            if self.rng.random() < 0.30:
                click_time = open_time + timedelta(seconds=self.rng.randint(10, 600))
                global_event_counter_ref[0] += 1
                events.append({
                    "event_id": communication_event_id(global_event_counter_ref[0]),
                    "send_id": send_id,
                    "event_type": "CLICKED",
                    "timestamp": click_time,
                    "metadata_json": '{"link": "recovery_cta"}'
                })

        return events
