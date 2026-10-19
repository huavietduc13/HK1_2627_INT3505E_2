from flask import Blueprint, jsonify, request

from models import Author, db


authors_bp = Blueprint("authors", __name__, url_prefix="/api/v1/authors")


@authors_bp.get("")
def list_authors():
    authors = Author.query.order_by(Author.id).all()
    return jsonify([author.to_dict() for author in authors]), 200


@authors_bp.post("")
def create_author():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "validation_failed", "message": "Expected a JSON object."}), 400

    name = payload.get("name")
    bio = payload.get("bio")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "validation_failed", "message": "name is required."}), 400
    if bio is not None and not isinstance(bio, str):
        return jsonify({"error": "validation_failed", "message": "bio must be a string or null."}), 400

    author = Author(name=name.strip(), bio=bio)
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201
