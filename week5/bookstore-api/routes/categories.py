from flask import Blueprint, jsonify, request

from models import Category, db


categories_bp = Blueprint("categories", __name__, url_prefix="/api/v1/categories")


@categories_bp.get("")
def list_categories():
    categories = Category.query.order_by(Category.id).all()
    return jsonify([category.to_dict() for category in categories]), 200


@categories_bp.post("")
def create_category():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "validation_failed", "message": "Expected a JSON object."}), 400

    name = payload.get("name")
    slug = payload.get("slug")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "validation_failed", "message": "name is required."}), 400
    if not isinstance(slug, str) or not slug.strip():
        return jsonify({"error": "validation_failed", "message": "slug is required."}), 400
    if Category.query.filter_by(slug=slug).first() is not None:
        return jsonify({"error": "conflict", "message": "Category slug already exists."}), 409

    category = Category(name=name.strip(), slug=slug.strip())
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201
