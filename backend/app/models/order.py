from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(32), primary_key=True, index=True)  # ORD-2026-000001
    customer_id = Column(String(32), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    cart_id = Column(String(32), ForeignKey("carts.cart_id", ondelete="SET NULL"), nullable=True, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    order_timestamp = Column(DateTime, nullable=False, index=True)
    status = Column(String(32), nullable=False, default="COMPLETED", index=True)  # COMPLETED, CANCELLED

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    cart = relationship("Cart", back_populates="order")
    order_lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    attribution = relationship("Attribution", back_populates="order", uselist=False)

    __table_args__ = (
        Index("ix_orders_customer_timestamp", "customer_id", "order_timestamp"),
    )


class OrderLine(Base):
    __tablename__ = "order_lines"

    order_line_id = Column(String(48), primary_key=True, index=True)  # OL-2026-000001-01
    order_id = Column(String(32), ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(32), ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_lines")
    product = relationship("Product", back_populates="order_lines")
