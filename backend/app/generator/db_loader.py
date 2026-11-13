from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.customer import Customer
from app.models.product import Product
from app.models.consent import Consent
from app.models.session import Session as DbSession
from app.models.cart import Cart, CartLine
from app.models.campaign import Campaign, MessageTemplate
from app.models.send_attempt import SendAttempt
from app.models.communication_event import CommunicationEvent
from app.models.order import Order, OrderLine
from app.models.attribution import Attribution
from app.models.anomaly import AnomalyRecord


def populate_database_from_dataset(db: Session, dataset: Dict[str, Any]):
    """Bulk populates the database session from generated in-memory dataset."""
    # 1. Customers
    cust_objs = [
        Customer(
            customer_id=c["customer_id"],
            first_name=c["first_name"],
            last_name=c["last_name"],
            email=c["email"],
            phone=c["phone"],
            preferred_channel=c["preferred_channel"],
            created_at=c["created_at"],
            updated_at=c["updated_at"]
        )
        for c in dataset.get("customers", [])
    ]
    db.bulk_save_objects(cust_objs)

    # 2. Products
    prod_objs = [
        Product(
            product_id=p["product_id"],
            sku=p["sku"],
            name=p["name"],
            category=p["category"],
            price=p["price"],
            is_active=p["is_active"]
        )
        for p in dataset.get("products", [])
    ]
    db.bulk_save_objects(prod_objs)

    # 3. Consents
    consent_objs = [
        Consent(
            consent_id=c["consent_id"],
            customer_id=c["customer_id"],
            channel=c["channel"],
            status=c["status"],
            effective_at=c["effective_at"],
            source=c["source"],
            created_at=c["created_at"]
        )
        for c in dataset.get("consents", [])
    ]
    db.bulk_save_objects(consent_objs)

    # 4. Sessions
    session_objs = [
        DbSession(
            session_id=s["session_id"],
            customer_id=s["customer_id"],
            device_type=s["device_type"],
            ip_address=s["ip_address"],
            user_agent=s["user_agent"],
            started_at=s["started_at"],
            ended_at=s["ended_at"]
        )
        for s in dataset.get("sessions", [])
    ]
    db.bulk_save_objects(session_objs)

    # 5. Campaigns & Templates
    camp_objs = [
        Campaign(
            campaign_id=c["campaign_id"],
            name=c["name"],
            channel=c["channel"],
            trigger_delay_minutes=c["trigger_delay_minutes"],
            discount_percent=c["discount_percent"],
            is_active=c["is_active"],
            created_at=c["created_at"]
        )
        for c in dataset.get("campaigns", [])
    ]
    db.bulk_save_objects(camp_objs)

    tmpl_objs = [
        MessageTemplate(
            template_id=t["template_id"],
            campaign_id=t["campaign_id"],
            channel=t["channel"],
            variant=t["variant"],
            subject=t["subject"],
            body_template=t["body_template"],
            is_active=t["is_active"]
        )
        for t in dataset.get("message_templates", [])
    ]
    db.bulk_save_objects(tmpl_objs)

    # 6. Carts & CartLines
    cart_objs = [
        Cart(
            cart_id=c["cart_id"],
            customer_id=c["customer_id"],
            session_id=c["session_id"],
            status=c["status"],
            subtotal=c["subtotal"],
            discount_total=c["discount_total"],
            total_amount=c["total_amount"],
            created_at=c["created_at"],
            updated_at=c["updated_at"],
            last_activity_at=c["last_activity_at"],
            abandoned_at=c["abandoned_at"],
            recovered_at=c["recovered_at"]
        )
        for c in dataset.get("carts", [])
    ]
    db.bulk_save_objects(cart_objs)

    cl_objs = [
        CartLine(
            cart_line_id=cl["cart_line_id"],
            cart_id=cl["cart_id"],
            product_id=cl["product_id"],
            quantity=cl["quantity"],
            unit_price=cl["unit_price"],
            total_price=cl["total_price"]
        )
        for cl in dataset.get("cart_lines", [])
    ]
    db.bulk_save_objects(cl_objs)

    # 7. Orders & OrderLines
    order_objs = [
        Order(
            order_id=o["order_id"],
            customer_id=o["customer_id"],
            cart_id=o["cart_id"],
            total_amount=o["total_amount"],
            order_timestamp=o["order_timestamp"],
            status=o["status"]
        )
        for o in dataset.get("orders", [])
    ]
    db.bulk_save_objects(order_objs)

    ol_objs = [
        OrderLine(
            order_line_id=ol["order_line_id"],
            order_id=ol["order_id"],
            product_id=ol["product_id"],
            quantity=ol["quantity"],
            unit_price=ol["unit_price"],
            total_price=ol["total_price"]
        )
        for ol in dataset.get("order_lines", [])
    ]
    db.bulk_save_objects(ol_objs)

    # 8. Send Attempts & Comm Events
    send_objs = [
        SendAttempt(
            send_id=s["send_id"],
            message_id=s["message_id"],
            campaign_id=s["campaign_id"],
            template_id=s["template_id"],
            cart_id=s["cart_id"],
            customer_id=s["customer_id"],
            channel=s["channel"],
            status=s["status"],
            suppression_reason=s["suppression_reason"],
            scheduled_at=s["scheduled_at"],
            sent_at=s["sent_at"],
            created_at=s["created_at"]
        )
        for s in dataset.get("send_attempts", [])
    ]
    db.bulk_save_objects(send_objs)

    event_objs = [
        CommunicationEvent(
            event_id=e["event_id"],
            send_id=e["send_id"],
            event_type=e["event_type"],
            timestamp=e["timestamp"],
            metadata_json=e["metadata_json"]
        )
        for e in dataset.get("communication_events", [])
    ]
    db.bulk_save_objects(event_objs)

    # 9. Attributions
    attr_objs = [
        Attribution(
            attribution_id=a["attribution_id"],
            order_id=a["order_id"],
            send_id=a["send_id"],
            campaign_id=a["campaign_id"],
            cart_id=a["cart_id"],
            order_timestamp=a["order_timestamp"],
            qualifying_click_at=a["qualifying_click_at"],
            latency_hours=a["latency_hours"],
            attributed_revenue=a["attributed_revenue"],
            model=a["model"],
            created_at=a["created_at"]
        )
        for a in dataset.get("attributions", [])
    ]
    db.bulk_save_objects(attr_objs)

    # 10. Anomalies
    ano_objs = [
        AnomalyRecord(
            anomaly_id=an["anomaly_id"],
            issue_type=an["issue_type"],
            affected_entity=an["affected_entity"],
            affected_record_id=an["affected_record_id"],
            detected_at=an["detected_at"],
            observed_value=an["observed_value"],
            expected_value=an["expected_value"],
            ground_truth_label=an["ground_truth_label"],
            expected_decision=an["expected_decision"],
            actual_decision=an["actual_decision"],
            resolution_status=an["resolution_status"]
        )
        for an in dataset.get("anomalies", [])
    ]
    db.bulk_save_objects(ano_objs)

    db.commit()
