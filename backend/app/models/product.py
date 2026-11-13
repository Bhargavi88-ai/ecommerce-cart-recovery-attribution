from sqlalchemy import Column, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(32), primary_key=True, index=True)  # PRD-000001
    sku = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    cart_lines = relationship("CartLine", back_populates="product")
    order_lines = relationship("OrderLine", back_populates="product")

