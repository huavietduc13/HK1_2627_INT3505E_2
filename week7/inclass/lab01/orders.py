from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload
from extensions import db
from models import *
from errors import *
from schemas import *

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

@orders_bp.get("")
def list_orders():
    stmt = db.select(Order).options(selectinload(Order.items)).order_by(Order.id.desc())
    orders = db.session.execute(stmt).scalars().all()

    return jsonify(OrderOut(many=True).dump(orders)), 200

@orders_bp.get("/<int:id>")
def get_order(id):
    stmt = db.select(Order).options(selectinload(Order.items)).where(Order.id == id)
    order = db.session.execute(stmt).scalar_one_or_none()
    if not order:
        raise NotFound(message="Order not found")
    return OrderOut().dump(order), 200

@orders_bp.post("")
def create_order():
    data = OrderIn().load(request.json)
    
    order = Order(customer_name=data["customer_name"])
    db.session.add(order)

    for item_data in data["items"]:
        product = db.session.get(Product, item_data["product_id"])
        if not product or product.archived:
            db.session.rollback()
            raise NotFound(message=f"Product {item_data['product_id']} not found")

        if product.quantity_in_stock < item_data["quantity"]:
            db.session.rollback()
            raise OutOfStock(
                message=f"Product '{product.name}' only has {product.quantity_in_stock} in stock"
            )

        product.quantity_in_stock -= item_data["quantity"]

        order_item = OrderItem(
            product=product,
            quantity=item_data["quantity"],
            price_cents=product.price_cents
        )
        order.items.append(order_item)

    db.session.commit()
    return OrderOut().dump(order), 201