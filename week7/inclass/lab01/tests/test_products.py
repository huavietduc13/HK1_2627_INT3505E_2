from extensions import db
from models import Product

def test_create_product_success(client, app):
    payload = {
        "sku": "PROD-101",
        "name": "Bàn phím cơ không dây",
        "price_cents": 1500000,
        "quantity_in_stock": 20
    }
    response = client.post("/api/v1/products", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["sku"] == "PROD-101"
    assert data["id"] is not None
    assert data["archived"] is False


def test_create_product_duplicate_sku(client, app):
    payload = {
        "sku": "PROD-UNIQUE",
        "name": "Chuột Gaming",
        "price_cents": 400000,
        "quantity_in_stock": 5
    }
    res1 = client.post("/api/v1/products", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/products", json=payload)
    assert res2.status_code == 409
    assert res2.get_json()["code"] == "conflict"


def test_product_soft_delete(client, app):
    with app.app_context():
        p = Product(sku="PROD-DEL", name="Tai nghe", price_cents=300000, quantity_in_stock=10)
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    res_del = client.delete(f"/api/v1/products/{p_id}")
    assert res_del.status_code == 204

    res_get = client.get(f"/api/v1/products/{p_id}")
    assert res_get.status_code == 404

    with app.app_context():
        prod_in_db = db.session.get(Product, p_id)
        assert prod_in_db is not None
        assert prod_in_db.archived is True

