import random
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple, Optional

from app.generator.id_generator import (
    customer_id, cart_id, campaign_id, message_id, send_id,
    order_id, product_id, consent_id, session_id, cart_line_id,
    order_line_id, template_id, communication_event_id, attribution_id
)
from app.generator.distributions import FIRST_NAMES, LAST_NAMES, PRODUCTS_CATALOG, DEVICE_TYPES, DEVICE_WEIGHTS
from app.generator.anomaly_fixtures import AnomalyFixtureBuilder
from app.services.abandonment_engine import AbandonmentDetectionEngine
from app.services.consent_suppression_engine import ConsentAndSuppressionEngine, SuppressionReason
from app.services.attribution_engine import AttributionEngine
from app.services.simulated_provider import SimulatedCommunicationProvider
from app.services.campaign_engine import CampaignPersonalizationEngine


class SyntheticDataGenerator:
    """
    High-fidelity deterministic synthetic data generator for E-Commerce Cart Recovery.
    Supports 'starter' and 'full' scale modes with deterministic seeding.
    """

    def __init__(self, seed: int = 20261022, scale: str = "starter"):
        self.seed = seed
        self.scale = scale.lower()
        self.rng = random.Random(seed)
        self.abandonment_engine = AbandonmentDetectionEngine()
        self.suppression_engine = ConsentAndSuppressionEngine()
        self.attribution_engine = AttributionEngine()
        self.simulated_provider = SimulatedCommunicationProvider(self.rng)

        # Scale parameters
        if self.scale == "full":
            self.num_customers = 25000
            self.num_carts = 50000
            self.target_abandoned = 20000
            self.target_sends = 10000
        else: # starter
            self.num_customers = 1000
            self.num_carts = 2000
            self.target_abandoned = 800
            self.target_sends = 400

        # Simulated timeline: fixed base time in 2026
        self.base_time = datetime(2026, 10, 1, 8, 0, 0, tzinfo=timezone.utc)

    def generate_dataset(self) -> Dict[str, Any]:
        """Executes full dependency-ordered generation."""
        # 1. Customers & Products
        customers = self._generate_customers()
        products = self._generate_products()

        # 2. Consents & Sessions
        consents, customer_consent_map = self._generate_consents(customers)
        sessions = self._generate_sessions(customers)

        # 3. Campaigns & Message Templates
        campaigns, templates = self._generate_campaigns_and_templates()

        # 4. Carts & CartLines
        carts, cart_lines, abandoned_cart_candidates = self._generate_carts_and_lines(
            customers, sessions, products
        )

        # 5. Orders (non-campaign organic baseline & early purchases)
        orders, order_lines, purchased_cart_ids = self._generate_baseline_orders(
            customers, carts, cart_lines, products
        )

        # 6. Send Attempts & Simulated Events (evaluating consent, frequency cap, purchase suppression)
        send_attempts, comm_events, qualifying_clicks = self._generate_sends_and_events(
            abandoned_cart_candidates, customer_consent_map, campaigns, templates, purchased_cart_ids
        )

        # 7. Campaign Conversion Orders & Deterministic Attribution
        conversion_orders, conversion_lines, attributions = self._generate_campaign_conversions(
            qualifying_clicks, products
        )
        orders.extend(conversion_orders)
        order_lines.extend(conversion_lines)

        # Update cart statuses based on purchases & campaign scheduling
        self._finalize_cart_statuses(carts, purchased_cart_ids, send_attempts, conversion_orders)

        # 8. Anomaly Fixtures (The 4 mandatory labeled anomalies)
        anomalies, ground_truth = self._inject_and_record_anomalies(
            customers=customers,
            carts=carts,
            cart_lines=cart_lines,
            send_attempts=send_attempts,
            orders=orders,
            order_lines=order_lines,
            attributions=attributions,
            campaigns=campaigns,
            consents=consents,
            comm_events=comm_events,
            templates=templates
        )

        # 9. Complete Ground Truth Decisions
        self._build_ground_truth_records(
            ground_truth, carts, send_attempts, attributions
        )

        return {
            "customers": customers,
            "products": products,
            "consents": consents,
            "sessions": sessions,
            "campaigns": campaigns,
            "message_templates": templates,
            "carts": carts,
            "cart_lines": cart_lines,
            "orders": orders,
            "order_lines": order_lines,
            "send_attempts": send_attempts,
            "communication_events": comm_events,
            "attributions": attributions,
            "anomalies": anomalies,
            "ground_truth": ground_truth
        }

    def _generate_customers(self) -> List[Dict[str, Any]]:
        customers = []
        for i in range(1, self.num_customers + 1):
            c_id = customer_id(i)
            fn = self.rng.choice(FIRST_NAMES)
            ln = self.rng.choice(LAST_NAMES)
            email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
            phone = f"+1{self.rng.randint(200, 999)}{self.rng.randint(200, 999)}{self.rng.randint(1000, 9999)}"
            pref = "EMAIL" if self.rng.random() < 0.65 else "SMS"
            c_time = self.base_time + timedelta(minutes=self.rng.randint(0, 1440 * 10))
            customers.append({
                "customer_id": c_id,
                "first_name": fn,
                "last_name": ln,
                "email": email,
                "phone": phone,
                "preferred_channel": pref,
                "created_at": c_time,
                "updated_at": c_time
            })
        return customers

    def _generate_products(self) -> List[Dict[str, Any]]:
        products = []
        for idx, item in enumerate(PRODUCTS_CATALOG, 1):
            p_id = product_id(idx)
            sku = f"SKU-{item['category'][:3].upper()}-{idx:04d}"
            products.append({
                "product_id": p_id,
                "sku": sku,
                "name": item["name"],
                "category": item["category"],
                "price": round(float(item["price"]), 2),
                "is_active": True
            })
        return products

    def _generate_consents(self, customers: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        consents = []
        consent_counter = 0
        customer_map = {}

        for cust in customers:
            c_id = cust["customer_id"]
            cust_consents = []

            # Email consent (85% opt-in initially)
            consent_counter += 1
            has_email = self.rng.random() < 0.85
            e_time = cust["created_at"]
            c_email = {
                "consent_id": consent_id(consent_counter),
                "customer_id": c_id,
                "channel": "EMAIL",
                "status": "OPT_IN" if has_email else "OPT_OUT",
                "effective_at": e_time,
                "source": "CHECKOUT_CHECKBOX",
                "created_at": e_time
            }
            consents.append(c_email)
            cust_consents.append(c_email)

            # SMS consent (60% opt-in initially)
            consent_counter += 1
            has_sms = self.rng.random() < 0.60
            c_sms = {
                "consent_id": consent_id(consent_counter),
                "customer_id": c_id,
                "channel": "SMS",
                "status": "OPT_IN" if has_sms else "OPT_OUT",
                "effective_at": e_time,
                "source": "CHECKOUT_CHECKBOX",
                "created_at": e_time
            }
            consents.append(c_sms)
            cust_consents.append(c_sms)

            # Consent withdrawal variation (approx 8% withdraw consent later)
            if has_email and self.rng.random() < 0.08:
                consent_counter += 1
                w_time = e_time + timedelta(days=self.rng.randint(1, 15))
                w_email = {
                    "consent_id": consent_id(consent_counter),
                    "customer_id": c_id,
                    "channel": "EMAIL",
                    "status": "OPT_OUT",
                    "effective_at": w_time,
                    "source": "PREFERENCE_CENTER",
                    "created_at": w_time
                }
                consents.append(w_email)
                cust_consents.append(w_email)

            if has_sms and self.rng.random() < 0.08:
                consent_counter += 1
                w_time = e_time + timedelta(days=self.rng.randint(1, 15))
                w_sms = {
                    "consent_id": consent_id(consent_counter),
                    "customer_id": c_id,
                    "channel": "SMS",
                    "status": "OPT_OUT",
                    "effective_at": w_time,
                    "source": "UNSUBSCRIBE_LINK",
                    "created_at": w_time
                }
                consents.append(w_sms)
                cust_consents.append(w_sms)

            customer_map[c_id] = cust_consents

        return consents, customer_map

    def _generate_sessions(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sessions = []
        for i in range(1, self.num_carts + 1):
            s_id = session_id(i)
            cust = self.rng.choice(customers)
            dev = self.rng.choices(DEVICE_TYPES, weights=DEVICE_WEIGHTS)[0]
            start = cust["created_at"] + timedelta(minutes=self.rng.randint(10, 1440 * 5))
            duration_min = self.rng.randint(2, 45)
            sessions.append({
                "session_id": s_id,
                "customer_id": cust["customer_id"],
                "device_type": dev,
                "ip_address": f"192.168.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}",
                "user_agent": f"Mozilla/5.0 ({dev}) AppleWebKit/537.36",
                "started_at": start,
                "ended_at": start + timedelta(minutes=duration_min)
            })
        return sessions

    def _generate_campaigns_and_templates(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        campaigns = [
            {
                "campaign_id": campaign_id(1),
                "name": "Standard Cart Recovery Email (10% Off)",
                "channel": "EMAIL",
                "trigger_delay_minutes": 60,
                "discount_percent": 10.0,
                "is_active": True,
                "created_at": self.base_time
            },
            {
                "campaign_id": campaign_id(2),
                "name": "Express SMS Flash Recovery (15% Off)",
                "channel": "SMS",
                "trigger_delay_minutes": 60,
                "discount_percent": 15.0,
                "is_active": True,
                "created_at": self.base_time
            },
            {
                "campaign_id": campaign_id(3),
                "name": "VIP Cart Re-engagement Email (15% Off)",
                "channel": "EMAIL",
                "trigger_delay_minutes": 120,
                "discount_percent": 15.0,
                "is_active": True,
                "created_at": self.base_time
            }
        ]

        templates = [
            {
                "template_id": template_id(1),
                "campaign_id": campaign_id(1),
                "channel": "EMAIL",
                "variant": "A",
                "subject": "Hey {{first_name}}, you left items in your cart!",
                "body_template": "Hi {{first_name}}, your {{product_name}} is waiting! Complete your order for {{cart_value}} and get {{campaign_offer}}: {{cart_recovery_url}}",
                "is_active": True
            },
            {
                "template_id": template_id(2),
                "campaign_id": campaign_id(1),
                "channel": "EMAIL",
                "variant": "B",
                "subject": "Don't miss out on {{product_name}} - {{campaign_offer}} inside",
                "body_template": "Hello {{first_name}}, your cart worth {{cart_value}} is about to expire. Click here to resume: {{cart_recovery_url}}",
                "is_active": True
            },
            {
                "template_id": template_id(3),
                "campaign_id": campaign_id(2),
                "channel": "SMS",
                "variant": "A",
                "subject": None,
                "body_template": "ShopAlert: {{first_name}}, complete your order of {{product_name}} with {{campaign_offer}}! Tap {{cart_recovery_url}}",
                "is_active": True
            },
            {
                "template_id": template_id(4),
                "campaign_id": campaign_id(3),
                "channel": "EMAIL",
                "variant": "A",
                "subject": "VIP Special: Finish your order today!",
                "body_template": "Dear {{first_name}}, items in your cart ({{product_name}}) are reserved. Use code VIP15 at checkout: {{cart_recovery_url}}",
                "is_active": True
            }
        ]

        return campaigns, templates

    def _generate_carts_and_lines(
        self,
        customers: List[Dict[str, Any]],
        sessions: List[Dict[str, Any]],
        products: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        carts = []
        cart_lines = []
        abandoned_candidates = []

        # Determine exact target ratio for abandonment
        # Target: self.target_abandoned abandoned carts out of self.num_carts
        is_abandoned_flags = [True] * self.target_abandoned + [False] * (self.num_carts - self.target_abandoned)
        self.rng.shuffle(is_abandoned_flags)

        for i in range(1, self.num_carts + 1):
            c_id = cart_id(i)
            session = sessions[i - 1]
            c_time = session["started_at"] + timedelta(minutes=self.rng.randint(1, 10))
            is_abandoned = is_abandoned_flags[i - 1]

            # Inactivity simulation:
            # If abandoned -> inactivity > 60 minutes
            # If active -> inactivity < 60 minutes
            if is_abandoned:
                inactivity_min = self.rng.randint(65, 1440 * 3)
                last_act = c_time + timedelta(minutes=self.rng.randint(2, 30))
                abandoned_at = last_act + timedelta(minutes=60)
                status = "ABANDONED"
            else:
                inactivity_min = self.rng.randint(5, 50)
                last_act = c_time + timedelta(minutes=self.rng.randint(2, 20))
                abandoned_at = None
                status = "ACTIVE"

            # Generate 1 to 4 cart lines
            num_lines = self.rng.choices([1, 2, 3, 4], weights=[0.55, 0.25, 0.15, 0.05])[0]
            chosen_prods = self.rng.sample(products, num_lines)
            subtotal = 0.0

            for l_idx, prod in enumerate(chosen_prods, 1):
                qty = self.rng.randint(1, 3)
                u_price = prod["price"]
                tot_price = round(qty * u_price, 2)
                subtotal += tot_price

                cart_lines.append({
                    "cart_line_id": cart_line_id(c_id, l_idx),
                    "cart_id": c_id,
                    "product_id": prod["product_id"],
                    "quantity": qty,
                    "unit_price": u_price,
                    "total_price": tot_price
                })

            subtotal = round(subtotal, 2)
            cart_record = {
                "cart_id": c_id,
                "customer_id": session["customer_id"],
                "session_id": session["session_id"],
                "status": status,
                "subtotal": subtotal,
                "discount_total": 0.00,
                "total_amount": subtotal,
                "created_at": c_time,
                "updated_at": last_act,
                "last_activity_at": last_act,
                "abandoned_at": abandoned_at,
                "recovered_at": None,
                "primary_product_name": chosen_prods[0]["name"]
            }
            carts.append(cart_record)

            if is_abandoned:
                abandoned_candidates.append(cart_record)

        return carts, cart_lines, abandoned_candidates

    def _generate_baseline_orders(
        self,
        customers: List[Dict[str, Any]],
        carts: List[Dict[str, Any]],
        cart_lines: List[Dict[str, Any]],
        products: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], set]:
        """
        Generates organic non-campaign orders (e.g. from ACTIVE carts converted immediately,
        or direct purchases).
        """
        orders = []
        order_lines = []
        purchased_cart_ids = set()
        cart_lines_map = {}
        for cl in cart_lines:
            cart_lines_map.setdefault(cl["cart_id"], []).append(cl)

        order_idx = 0
        # Convert approx 40% of ACTIVE carts into immediate organic orders
        for cart in carts:
            if cart["status"] == "ACTIVE" and self.rng.random() < 0.40:
                order_idx += 1
                o_id = order_id(order_idx)
                purchased_cart_ids.add(cart["cart_id"])
                o_time = cart["last_activity_at"] + timedelta(minutes=self.rng.randint(2, 25))

                lines = cart_lines_map.get(cart["cart_id"], [])
                tot = sum(l["total_price"] for l in lines)
                tot = round(tot, 2)

                orders.append({
                    "order_id": o_id,
                    "customer_id": cart["customer_id"],
                    "cart_id": cart["cart_id"],
                    "total_amount": tot,
                    "order_timestamp": o_time,
                    "status": "COMPLETED"
                })

                for l_idx, cl in enumerate(lines, 1):
                    order_lines.append({
                        "order_line_id": order_line_id(o_id, l_idx),
                        "order_id": o_id,
                        "product_id": cl["product_id"],
                        "quantity": cl["quantity"],
                        "unit_price": cl["unit_price"],
                        "total_price": cl["total_price"]
                    })

        return orders, order_lines, purchased_cart_ids

    def _generate_sends_and_events(
        self,
        abandoned_candidates: List[Dict[str, Any]],
        customer_consent_map: Dict[str, List[Dict[str, Any]]],
        campaigns: List[Dict[str, Any]],
        templates: List[Dict[str, Any]],
        purchased_cart_ids: set
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Evaluates consent, frequency caps, and suppression rules for abandoned carts.
        Generates approximately target_sends send attempts (or proportionate for starter).
        """
        send_attempts = []
        comm_events = []
        qualifying_clicks = []
        global_event_counter = [0]
        customer_past_sends: Dict[str, List[Dict[str, Any]]] = {}

        # Limit attempts to match target_sends approximately
        candidate_sample = abandoned_candidates[:int(self.target_sends * 1.35)]
        candidate_sample.sort(key=lambda c: (c["abandoned_at"], c["cart_id"]))

        send_idx = 0
        for cart in candidate_sample:
            send_idx += 1
            s_id = send_id(send_idx)
            c_id = cart["customer_id"]
            cust_consents = customer_consent_map.get(c_id, [])

            # Choose campaign (Email or SMS)
            camp = self.rng.choice(campaigns)
            channel = camp["channel"]
            attempt_time = cart["abandoned_at"] + timedelta(minutes=camp["trigger_delay_minutes"])

            past_sends = customer_past_sends.get(c_id, [])
            is_purchased = cart["cart_id"] in purchased_cart_ids
            is_abandoned = True

            # Evaluate suppression rules deterministically
            is_eligible, suppression_reason = self.suppression_engine.evaluate_send_eligibility(
                channel=channel,
                attempt_timestamp=attempt_time,
                customer_consents=cust_consents,
                past_customer_sends=past_sends,
                is_cart_purchased=is_purchased,
                is_cart_abandoned=is_abandoned,
                prior_cart_campaign_ids=[],
                proposed_campaign_id=camp["campaign_id"]
            )

            # Pick template matching campaign & channel
            matching_templates = [t for t in templates if t["campaign_id"] == camp["campaign_id"]]
            template = self.rng.choice(matching_templates) if matching_templates else None

            if is_eligible:
                status = "SENT"
                sent_at = attempt_time + timedelta(seconds=self.rng.randint(5, 60))
                supp_reason = None
            else:
                status = "SUPPRESSED"
                sent_at = None
                supp_reason = suppression_reason

            attempt = {
                "send_id": s_id,
                "message_id": message_id(cart["cart_id"], 1),
                "campaign_id": camp["campaign_id"],
                "template_id": template["template_id"] if template else None,
                "cart_id": cart["cart_id"],
                "customer_id": c_id,
                "channel": channel,
                "status": status,
                "suppression_reason": supp_reason,
                "scheduled_at": attempt_time,
                "sent_at": sent_at,
                "created_at": attempt_time
            }
            send_attempts.append(attempt)
            customer_past_sends.setdefault(c_id, []).append(attempt)

            # If successfully sent, simulate communication event lifecycle
            if status == "SENT":
                events = self.simulated_provider.simulate_events(
                    send_id=s_id,
                    channel=channel,
                    sent_at=sent_at,
                    global_event_counter_ref=global_event_counter
                )
                comm_events.extend(events)

                # Collect qualifying clicks for attribution
                clicks = [e for e in events if e["event_type"] == "CLICKED"]
                for clk in clicks:
                    qualifying_clicks.append({
                        "send_id": s_id,
                        "campaign_id": camp["campaign_id"],
                        "cart_id": cart["cart_id"],
                        "customer_id": c_id,
                        "cart_total": cart["total_amount"],
                        "clicked_at": clk["timestamp"]
                    })

            # Check stop condition if full target reached
            if len([s for s in send_attempts if s["status"] == "SENT"]) >= self.target_sends:
                break

        return send_attempts, comm_events, qualifying_clicks

    def _generate_campaign_conversions(
        self,
        qualifying_clicks: List[Dict[str, Any]],
        products: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generates converted orders from campaign clicks and attributes them deterministically.
        Applies Last-Click Attribution within 7-day window.
        """
        orders = []
        order_lines = []
        attributions = []

        # Approx 45% of clickers complete an order within 1 to 72 hours
        order_start_idx = 100000 # offset from baseline orders
        attr_idx = 0

        # Group clicks by cart_id / customer_id
        clicks_by_cart: Dict[str, List[Dict[str, Any]]] = {}
        for c in qualifying_clicks:
            clicks_by_cart.setdefault(c["cart_id"], []).append(c)

        for cart_id_key, clicks in clicks_by_cart.items():
            if self.rng.random() < 0.45:
                order_start_idx += 1
                attr_idx += 1
                o_id = order_id(order_start_idx)
                
                # Pick winning click: last click
                clicks.sort(key=lambda x: x["clicked_at"])
                winning_click = clicks[-1]
                
                # Order placed between 15 mins and 48 hours after click
                latency_minutes = self.rng.randint(15, 2880)
                order_time = winning_click["clicked_at"] + timedelta(minutes=latency_minutes)
                
                # Reconciled total
                prod = self.rng.choice(products)
                qty = self.rng.randint(1, 2)
                price = prod["price"]
                line_tot = round(qty * price, 2)

                orders.append({
                    "order_id": o_id,
                    "customer_id": winning_click["customer_id"],
                    "cart_id": cart_id_key,
                    "total_amount": line_tot,
                    "order_timestamp": order_time,
                    "status": "COMPLETED"
                })

                order_lines.append({
                    "order_line_id": order_line_id(o_id, 1),
                    "order_id": o_id,
                    "product_id": prod["product_id"],
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": line_tot
                })

                latency_hrs = self.attribution_engine.calculate_latency_hours(
                    winning_click["clicked_at"], order_time
                )

                attributions.append({
                    "attribution_id": attribution_id(attr_idx),
                    "order_id": o_id,
                    "send_id": winning_click["send_id"],
                    "campaign_id": winning_click["campaign_id"],
                    "cart_id": cart_id_key,
                    "order_timestamp": order_time,
                    "qualifying_click_at": winning_click["clicked_at"],
                    "latency_hours": latency_hrs,
                    "attributed_revenue": line_tot,
                    "model": "LAST_CLICK",
                    "created_at": order_time
                })

        return orders, order_lines, attributions

    def _finalize_cart_statuses(
        self,
        carts: List[Dict[str, Any]],
        purchased_cart_ids: set,
        send_attempts: List[Dict[str, Any]],
        conversion_orders: List[Dict[str, Any]]
    ):
        """Finalizes lifecycle states and recovered timestamps."""
        conversion_cart_map = {o["cart_id"]: o["order_timestamp"] for o in conversion_orders}
        scheduled_cart_ids = {s["cart_id"] for s in send_attempts if s["status"] in ("QUEUED", "SENT")}
        suppressed_cart_ids = {s["cart_id"] for s in send_attempts if s["status"] == "SUPPRESSED"}

        for cart in carts:
            cid = cart["cart_id"]
            if cid in conversion_cart_map:
                cart["status"] = "RECOVERED"
                cart["recovered_at"] = conversion_cart_map[cid]
            elif cid in purchased_cart_ids:
                cart["status"] = "RECOVERED"
            elif cart["status"] == "ABANDONED":
                if cid in scheduled_cart_ids:
                    cart["status"] = "CAMPAIGN_SCHEDULED"
                elif cid in suppressed_cart_ids:
                    cart["status"] = "SUPPRESSED"
                else:
                    cart["status"] = "ELIGIBLE"

    def _inject_and_record_anomalies(
        self,
        customers: List[Dict[str, Any]],
        carts: List[Dict[str, Any]],
        cart_lines: List[Dict[str, Any]],
        send_attempts: List[Dict[str, Any]],
        orders: List[Dict[str, Any]],
        order_lines: List[Dict[str, Any]],
        attributions: List[Dict[str, Any]],
        campaigns: List[Dict[str, Any]],
        consents: List[Dict[str, Any]],
        comm_events: List[Dict[str, Any]],
        templates: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Injects the 4 mandatory labeled anomalies directly into generated data tables:
        1. MESSAGE_AFTER_OPTOUT: Real send attempt dispatched post opt-out in send_attempts & consents
        2. CART_ABANDONED_AFTER_PURCHASE: Real cart marked ABANDONED after completed purchase in carts & orders
        3. DUPLICATE_ATTRIBUTION: Real order with duplicate primary attribution claims in orders & attributions
        4. STALE_CART_TOTAL: Real cart with desynchronized total_amount vs cart_lines in carts
        """
        anomalies = []
        ground_truth = []
        ano_counter = 0

        # Anomaly 1: MESSAGE_AFTER_OPTOUT
        ano_counter += 1
        purchased_cart_set = {o["cart_id"] for o in orders if o.get("cart_id")}
        existing_send_custs = {s["customer_id"] for s in send_attempts}
        # Choose customer with no other sends and an unpurchased cart to prevent unlabelled extra violations
        valid_candidates = [
            c for c in customers
            if c["customer_id"] not in existing_send_custs
            and any(cart["cart_id"] not in purchased_cart_set for cart in carts if cart["customer_id"] == c["customer_id"])
        ]
        a1_cust = valid_candidates[0] if valid_candidates else customers[10]
        a1_cart = next(cart for cart in carts if cart["customer_id"] == a1_cust["customer_id"] and cart["cart_id"] not in purchased_cart_set)
        a1_send_id = send_id(999901)
        optout_time = a1_cust["created_at"] + timedelta(days=2)
        sent_after_optout_time = optout_time + timedelta(hours=5)

        # 1. Inject opt-out consent into consents table
        consents.append({
            "consent_id": consent_id(999901),
            "customer_id": a1_cust["customer_id"],
            "channel": "EMAIL",
            "status": "OPT_OUT",
            "effective_at": optout_time,
            "source": "FOOTER_UNSUBSCRIBE",
            "created_at": optout_time
        })

        # 2. Inject dispatched send attempt into send_attempts table
        used_campaign_ids = {s["campaign_id"] for s in send_attempts if s["cart_id"] == a1_cart["cart_id"]}
        available_email_camps = [c for c in campaigns if c["channel"] == "EMAIL" and c["campaign_id"] not in used_campaign_ids]
        a1_camp = available_email_camps[0] if available_email_camps else campaigns[0]
        a1_tmpl = next((t for t in templates if t["campaign_id"] == a1_camp["campaign_id"]), templates[0] if templates else None)
        send_attempts.append({
            "send_id": a1_send_id,
            "message_id": message_id(a1_cart["cart_id"], 1),
            "campaign_id": a1_camp["campaign_id"],
            "template_id": a1_tmpl["template_id"] if a1_tmpl else "TMPL-000001",
            "cart_id": a1_cart["cart_id"],
            "customer_id": a1_cust["customer_id"],
            "channel": "EMAIL",
            "status": "SENT",
            "suppression_reason": None,
            "scheduled_at": sent_after_optout_time - timedelta(minutes=1),
            "sent_at": sent_after_optout_time,
            "created_at": sent_after_optout_time - timedelta(minutes=1)
        })

        # 3. Inject communication events
        comm_events.append({
            "event_id": f"EVT-{a1_send_id}-01",
            "send_id": a1_send_id,
            "event_type": "SEND",
            "timestamp": sent_after_optout_time,
            "metadata_json": json.dumps({"provider": "SendGrid", "status": "dispatched"})
        })
        comm_events.append({
            "event_id": f"EVT-{a1_send_id}-02",
            "send_id": a1_send_id,
            "event_type": "DELIVERED",
            "timestamp": sent_after_optout_time + timedelta(seconds=14),
            "metadata_json": json.dumps({"provider": "SendGrid", "status": "delivered"})
        })

        a1 = AnomalyFixtureBuilder.create_message_after_optout(
            counter=ano_counter,
            customer_id=a1_cust["customer_id"],
            send_id=a1_send_id,
            sent_at=sent_after_optout_time,
            optout_time=optout_time
        )
        anomalies.append(a1)
        ground_truth.append({
            "record_id": a1_send_id,
            "entity": "SendAttempt",
            "anomaly_type": "MESSAGE_AFTER_OPTOUT",
            "issue_type": "MESSAGE_AFTER_OPTOUT",
            "expected_decision": "SUPPRESS_SEND",
            "actual_decision": "DISPATCHED_MESSAGE",
            "ground_truth_label": "UNLAWFUL_SEND_POST_WITHDRAWAL"
        })

        # Anomaly 2: CART_ABANDONED_AFTER_PURCHASE
        ano_counter += 1
        a2_cart = carts[15]
        a2_order_id = order_id(999902)
        purch_time = a2_cart["created_at"] + timedelta(hours=1)
        abandon_after_purch = purch_time + timedelta(hours=2)

        # 1. Inject completed order into orders table
        orders.append({
            "order_id": a2_order_id,
            "customer_id": a2_cart["customer_id"],
            "cart_id": a2_cart["cart_id"],
            "total_amount": a2_cart["total_amount"],
            "order_timestamp": purch_time,
            "status": "COMPLETED"
        })

        # 2. Inject matching order lines so order total reconciles
        c16_lines = [cl for cl in cart_lines if cl["cart_id"] == a2_cart["cart_id"]]
        for idx, cl in enumerate(c16_lines, 1):
            order_lines.append({
                "order_line_id": order_line_id(a2_order_id, idx),
                "order_id": a2_order_id,
                "product_id": cl["product_id"],
                "quantity": cl["quantity"],
                "unit_price": cl["unit_price"],
                "total_price": cl["total_price"]
            })

        # 3. Update cart status to ABANDONED after purchase
        a2_cart["status"] = "ABANDONED"
        a2_cart["abandoned_at"] = abandon_after_purch
        a2_cart["last_activity_at"] = abandon_after_purch - timedelta(minutes=60)

        a2 = AnomalyFixtureBuilder.create_cart_abandoned_after_purchase(
            counter=ano_counter,
            cart_id=a2_cart["cart_id"],
            order_id=a2_order_id,
            purchase_time=purch_time,
            abandonment_time=abandon_after_purch
        )
        anomalies.append(a2)
        ground_truth.append({
            "record_id": a2_cart["cart_id"],
            "entity": "Cart",
            "anomaly_type": "CART_ABANDONED_AFTER_PURCHASE",
            "issue_type": "CART_ABANDONED_AFTER_PURCHASE",
            "expected_decision": "MARK_RECOVERED",
            "actual_decision": "MARK_ABANDONED",
            "ground_truth_label": "FALSE_ABANDONMENT_AFTER_PURCHASE"
        })

        # Anomaly 3: DUPLICATE_ATTRIBUTION
        ano_counter += 1
        a3_order_id = order_id(999903)
        attr_a = attribution_id(999901)
        attr_b = attribution_id(999902)
        camp_a = campaigns[0]["campaign_id"]
        camp_b = campaigns[1]["campaign_id"] if len(campaigns) > 1 else campaigns[0]["campaign_id"]
        send_a = send_attempts[0]["send_id"]
        send_b = send_attempts[1]["send_id"] if len(send_attempts) > 1 else send_attempts[0]["send_id"]

        a3_cart = carts[30]
        a3_order_time = a3_cart["created_at"] + timedelta(days=1)

        # 1. Inject order into orders table
        orders.append({
            "order_id": a3_order_id,
            "customer_id": a3_cart["customer_id"],
            "cart_id": a3_cart["cart_id"],
            "total_amount": a3_cart["total_amount"],
            "order_timestamp": a3_order_time,
            "status": "COMPLETED"
        })

        # 2. Inject order lines so order total reconciles
        c30_lines = [cl for cl in cart_lines if cl["cart_id"] == a3_cart["cart_id"]]
        for idx, cl in enumerate(c30_lines, 1):
            order_lines.append({
                "order_line_id": order_line_id(a3_order_id, idx),
                "order_id": a3_order_id,
                "product_id": cl["product_id"],
                "quantity": cl["quantity"],
                "unit_price": cl["unit_price"],
                "total_price": cl["total_price"]
            })

        # 3. Inject duplicate primary attribution claims into attributions table
        attributions.append({
            "attribution_id": attr_a,
            "order_id": a3_order_id,
            "send_id": send_a,
            "campaign_id": camp_a,
            "cart_id": a3_cart["cart_id"],
            "order_timestamp": a3_order_time,
            "qualifying_click_at": a3_order_time - timedelta(hours=4),
            "latency_hours": 4.0,
            "attributed_revenue": a3_cart["total_amount"],
            "model": "LAST_CLICK",
            "created_at": a3_order_time
        })
        attributions.append({
            "attribution_id": attr_b,
            "order_id": a3_order_id,
            "send_id": send_b,
            "campaign_id": camp_b,
            "cart_id": a3_cart["cart_id"],
            "order_timestamp": a3_order_time,
            "qualifying_click_at": a3_order_time - timedelta(hours=2),
            "latency_hours": 2.0,
            "attributed_revenue": a3_cart["total_amount"],
            "model": "LAST_CLICK",
            "created_at": a3_order_time
        })

        a3 = AnomalyFixtureBuilder.create_duplicate_attribution(
            counter=ano_counter,
            order_id=a3_order_id,
            first_attr_id=attr_a,
            second_attr_id=attr_b,
            first_campaign=camp_a,
            second_campaign=camp_b
        )
        anomalies.append(a3)
        ground_truth.append({
            "record_id": a3_order_id,
            "entity": "Attribution",
            "anomaly_type": "DUPLICATE_ATTRIBUTION",
            "issue_type": "DUPLICATE_ATTRIBUTION",
            "expected_decision": "SINGLE_PRIMARY_ATTRIBUTION",
            "actual_decision": "DUPLICATE_MULTI_CLAIM",
            "ground_truth_label": "DOUBLE_COUNTED_ORDER_REVENUE"
        })

        # Anomaly 4: STALE_CART_TOTAL
        ano_counter += 1
        a4_cart = carts[20]
        calculated_total = a4_cart["total_amount"]
        stale_stored_total = round(calculated_total + 45.00, 2)

        # Mutate cart stored total so it desynchronizes from cart_lines
        a4_cart["total_amount"] = stale_stored_total

        a4 = AnomalyFixtureBuilder.create_stale_cart_total(
            counter=ano_counter,
            cart_id=a4_cart["cart_id"],
            stored_total=stale_stored_total,
            calculated_total=calculated_total
        )
        anomalies.append(a4)
        ground_truth.append({
            "record_id": a4_cart["cart_id"],
            "entity": "Cart",
            "anomaly_type": "STALE_CART_TOTAL",
            "issue_type": "STALE_CART_TOTAL",
            "expected_decision": "RECONCILE_LINE_SUM",
            "actual_decision": "STALE_TOTAL_PERSISTED",
            "ground_truth_label": "DESYNCHRONIZED_CART_LINE_PRICE"
        })

        return anomalies, ground_truth

    def _build_ground_truth_records(
        self,
        ground_truth: List[Dict[str, Any]],
        carts: List[Dict[str, Any]],
        send_attempts: List[Dict[str, Any]],
        attributions: List[Dict[str, Any]]
    ):
        """Builds comprehensive ground truth labels for suppression, abandonment, and attribution."""
        known_anomalous_record_ids = {gt["record_id"] for gt in ground_truth}

        # Ground truth for sample non-anomalous carts (50 baseline)
        baseline_carts = [c for c in carts if c["cart_id"] not in known_anomalous_record_ids][:50]
        for cart in baseline_carts:
            is_abandoned = cart["abandoned_at"] is not None
            ground_truth.append({
                "record_id": cart["cart_id"],
                "entity": "Cart",
                "anomaly_type": "NONE_BASELINE",
                "issue_type": "NONE_BASELINE",
                "expected_decision": "ABANDONED" if is_abandoned else "ACTIVE",
                "actual_decision": cart["status"],
                "ground_truth_label": "QUALIFIED_ABANDONMENT" if is_abandoned else "ORGANIC_ACTIVE"
            })

        # Ground truth for sample non-anomalous sends (50 baseline)
        baseline_sends = [s for s in send_attempts if s["send_id"] not in known_anomalous_record_ids][:50]
        for send in baseline_sends:
            ground_truth.append({
                "record_id": send["send_id"],
                "entity": "SendAttempt",
                "anomaly_type": "NONE_BASELINE",
                "issue_type": "NONE_BASELINE",
                "expected_decision": "DISPATCH" if send["status"] == "SENT" else "SUPPRESS",
                "actual_decision": send["status"],
                "ground_truth_label": send["suppression_reason"] or "LEGITIMATE_SEND"
            })

        # Ground truth for sample non-anomalous attributions (50 baseline)
        baseline_attrs = [a for a in attributions if a["order_id"] not in known_anomalous_record_ids][:50]
        for attr in baseline_attrs:
            ground_truth.append({
                "record_id": attr["order_id"],
                "entity": "Order",
                "anomaly_type": "NONE_BASELINE",
                "issue_type": "NONE_BASELINE",
                "expected_decision": "ATTRIBUTE_LAST_CLICK",
                "actual_decision": attr["campaign_id"],
                "ground_truth_label": "VALID_LAST_CLICK_CONVERSION"
            })

