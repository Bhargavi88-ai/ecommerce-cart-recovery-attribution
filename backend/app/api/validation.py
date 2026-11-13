import os
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.validation.validator import DataQualityValidator
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
from app.schemas.validation import ValidationSummaryResponse

router = APIRouter(prefix="/validation", tags=["Validation"])


@router.post("/run", response_model=ValidationSummaryResponse)
def run_validation(db: Session = Depends(get_db)):
    # Build dataset dict from current database tables
    dataset = {
        "customers": [c.__dict__ for c in db.query(Customer).all()],
        "products": [p.__dict__ for p in db.query(Product).all()],
        "consents": [c.__dict__ for c in db.query(Consent).all()],
        "sessions": [s.__dict__ for s in db.query(DbSession).all()],
        "carts": [c.__dict__ for c in db.query(Cart).all()],
        "cart_lines": [cl.__dict__ for cl in db.query(CartLine).all()],
        "campaigns": [c.__dict__ for c in db.query(Campaign).all()],
        "message_templates": [t.__dict__ for t in db.query(MessageTemplate).all()],
        "send_attempts": [s.__dict__ for s in db.query(SendAttempt).all()],
        "communication_events": [e.__dict__ for e in db.query(CommunicationEvent).all()],
        "orders": [o.__dict__ for o in db.query(Order).all()],
        "order_lines": [ol.__dict__ for ol in db.query(OrderLine).all()],
        "attributions": [a.__dict__ for a in db.query(Attribution).all()],
    }

    validator = DataQualityValidator(dataset)
    summary = validator.run_all_validations()

    # Save summary to exports dir
    summary_path = os.path.join(settings.EXPORTS_DIR, "validation_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


@router.get("/report")
def get_validation_report():
    summary_path = os.path.join(settings.EXPORTS_DIR, "validation_summary.json")
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=404, detail="Validation summary report not generated yet.")
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
