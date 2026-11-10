mock_db = [
    {"id": 1, "sku": "KEY-067", "name": "Bàn phím cơ", "price_cents": 15000000000}
]

def list_products():
    return mock_db, 200

def create_product(body):
    new_id = mock_db[-1]["id"] + 1 if mock_db else 1
    
    new_product = {
        "id": new_id,
        "sku": body["sku"],
        "name": body["name"],
        "price_cents": body["price_cents"]
    }
    
    mock_db.append(new_product)
    return new_product, 201