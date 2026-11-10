from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields, validate

class ProductInSchema(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True)
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    price_cents = fields.Int()

mock_db = [
    {"id": 1, "sku": "KEY-001", "name": "Bàn phím cơ", "price_cents": 1500000}
]

blp = Blueprint("products", __name__, url_prefix="/products")

class ProductList(MethodView):
    @blp.arguments(ProductInSchema)
    @blp.response(201, ProductSchema)
    def post(self, data):
        new_id = mock_db[-1]["id"] + 1 if mock_db else 1
        p = {"id": new_id, **data}
        
        mock_db.append(p)
        return p

    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return mock_db

blp.add_url_rule("", view_func=ProductList.as_view("product_list"))