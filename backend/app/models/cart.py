from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(String(32), primary_key=True, index=True)  # CART-2026-000001
    customer_id = Column(String(32), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(32), ForeignKey("sessions.session_id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Lifecycle: ACTIVE, ABANDONED, ELIGIBLE, SUPPRESSED, CAMPAIGN_SCHEDULED, RECOVERED, EXPIRED
    status = Column(String(32), nullable=False, default="ACTIVE", index=True)
    
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.00)
    discount_total = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_activity_at = Column(DateTime, nullable=False, index=True)
    abandoned_at = Column(DateTime, nullable=True, index=True)
    recovered_at = Column(DateTime, nullable=True, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="carts")
    session = relationship("Session", back_populates="carts")
    cart_lines = relationship("CartLine", back_populates="cart", cascade="all, delete-orphan")
    send_attempts = relationship("SendAttempt", back_populates="cart")
    order = relationship("Order", back_populates="cart", uselist=False)

    __table_args__ = (
        Index("ix_carts_customer_status", "customer_id", "status"),
        Index("ix_carts_status_last_activity", "status", "last_activity_at"),
    )


class CartLine(Base):
    __tablename__ = "cart_lines"

    cart_line_id = Column(String(48), primary_key=True, index=True)  # CL-2026-000001-01
    cart_id = Column(String(32), ForeignKey("carts.cart_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(32), ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="cart_lines")
    product = relationship("Product", back_populates="cart_lines")

    __table_args__ = (
        Index("ix_cart_lines_cart_product", "cart_id", "product_id"),
    )
