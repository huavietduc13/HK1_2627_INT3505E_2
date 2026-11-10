from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db

class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def __init__(self,sku: str = "", name: str = "",price_cents: int = 0, quantity_in_stock: int = 0, description: Optional[str] = None, archived: bool = False, **kwargs):
        super().__init__()
        self.sku = sku
        self.name = name
        self.price_cents = price_cents
        self.quantity_in_stock = quantity_in_stock
        self.description = description
        self.archived = archived
        for k, v in kwargs.items():
            setattr(self, k, v)

class Order(db.Model):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __init__(self, customer_name: str = "", status: str = "pending", **kwargs):
        super().__init__()
        self.customer_name = customer_name
        self.status = status
        for k, v in kwargs.items():
            setattr(self, k, v)

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")

    def __init__(self, product: Optional["Product"] = None, quantity: int = 1, price_cents: int = 0, order_id: Optional[int] = None, product_id: Optional[int] = None, **kwargs):
        super().__init__()
        self.product = product
        self.quantity = quantity
        self.price_cents = price_cents
        if order_id is not None:
            self.order_id = order_id
        if product_id is not None:
            self.product_id = product_id
        for k, v in kwargs.items():
            setattr(self, k, v)