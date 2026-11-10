from sqlalchemy import event
from extensions import db
from models import Product, Order, OrderItem

class QueryCounter:
    def __init__(self, engine):
        self.engine = engine
        self.select_queries = []

    def __enter__(self):
        self.select_queries = []
        event.listen(self.engine, "before_cursor_execute", self._callback)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        event.remove(self.engine, "before_cursor_execute", self._callback)

    def _callback(self, conn, cursor, statement, parameters, context, executemany):
        clean_stmt = statement.strip().upper()
        if clean_stmt.startswith("SELECT"):
            self.select_queries.append(statement)


def test_create_order_success(client, app):
    with app.app_context():
        p1 = Product(sku="KEYBOARD-01", name="Bàn phím cơ", price_cents=100000, quantity_in_stock=10)
        p2 = Product(sku="MOUSE-01", name="Chuột quang", price_cents=50000, quantity_in_stock=5)
        db.session.add_all([p1, p2])
        db.session.commit()
        p1_id, p2_id = p1.id, p2.id

    payload = {
        "customer_name": "Nguyễn Văn A",
        "items": [
            {"product_id": p1_id, "quantity": 2},
            {"product_id": p2_id, "quantity": 1}
        ]
    }
    response = client.post("/api/v1/orders", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["customer_name"] == "Nguyễn Văn A"
    assert data["status"] == "pending"
    assert len(data["items"]) == 2

    with app.app_context():
        prod1 = db.session.get(Product, p1_id)
        prod2 = db.session.get(Product, p2_id)
        assert prod1.quantity_in_stock == 8   # 10 - 2 = 8
        assert prod2.quantity_in_stock == 4   # 5 - 1 = 4


def test_create_order_out_of_stock(client, app):
    with app.app_context():
        p = Product(sku="LAPTOP-01", name="Laptop Gaming", price_cents=20000000, quantity_in_stock=1)
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    payload = {
        "customer_name": "Trần Thị B",
        "items": [{"product_id": p_id, "quantity": 5}]
    }
    response = client.post("/api/v1/orders", json=payload)

    assert response.status_code == 409
    data = response.get_json()
    assert data["code"] == "out_of_stock"


def test_get_orders_eager_loading_prevents_n_plus_one(client, app):
    total_orders = 5
    with app.app_context():
        p = Product(sku="ITEM-01", name="Sách SOA", price_cents=50000, quantity_in_stock=100)
        db.session.add(p)
        db.session.commit()

        for i in range(total_orders):
            order = Order(customer_name=f"Khách hàng {i+1}")
            item = OrderItem(product=p, quantity=1, price_cents=50000)
            order.items.append(item)
            db.session.add(order)
        db.session.commit()

    with app.app_context():
        with QueryCounter(db.engine) as counter:
            response = client.get("/api/v1/orders")

    assert response.status_code == 200
    orders_data = response.get_json()
    assert len(orders_data) == total_orders

    assert len(counter.select_queries) == 2, (
        f"lỗi N+1 query, chạy {len(counter.select_queries)} queries."
    )

