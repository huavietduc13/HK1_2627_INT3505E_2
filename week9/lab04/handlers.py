def v1_create_order(body):
    return {
        "order_id": 101,
        "handler": "v1_legacy",
        "account_id": body.get("account_id"),
        "status": "created"
    }


def v2_create_order(body):
    return {
        "order_id": 101,
        "handler": "v2_modern",
        "account_id": body.get("account_id"),
        "status": "created",
        "features": ["instant_checkout", "loyalty_points"]
    }
