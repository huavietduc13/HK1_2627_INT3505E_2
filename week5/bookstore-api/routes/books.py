import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate

from models import Author, Book, Category, Review, db


books_bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

SCHEMA_PATH = Path(__file__).resolve().parent.parent /"schemas"/"book.json"
with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
    BOOK_CREATE_SCHEMA = json.load(schema_file)


def validate_payload(payload, *, partial=False):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."

    schema = BOOK_CREATE_SCHEMA
    if partial:
        schema = {**BOOK_CREATE_SCHEMA, "required": []}

    try:
        validate(instance=payload, schema=schema)
    except ValidationError as error:
        return error.message
    return None


def resolve_related(payload):
    category = None
    if "category_id" in payload:
        category = db.session.get(Category, payload["category_id"])
        if category is None:
            return None, [], "Category does not exist."

    author_ids = payload.get("author_ids", [])
    authors = [db.session.get(Author, author_id) for author_id in author_ids]
    if any(author is None for author in authors):
        return None, [], "One or more authors do not exist."

    return category, authors, None


@books_bp.get("")
def list_books():
    books = Book.query.order_by(Book.id).all()
    return jsonify([book.to_dict() for book in books]), 200


@books_bp.post("")
def create_book():
    payload = request.get_json(silent=True)
    error = validate_payload(payload)
    if error:
        return jsonify({"error": "validation_failed", "message": error}), 400

    category, authors, error = resolve_related(payload)
    if error:
        return jsonify({"error": "related_resource_not_found", "message": error}), 400

    book = Book(
        title=payload["title"],
        isbn=payload.get("isbn"),
        price_vnd=payload["price_vnd"],
        stock=payload.get("stock", 0),
        category=category,
        authors=authors,
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@books_bp.get("/<int:book_id>")
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        return jsonify({"error": "not_found", "message": "Book not found."}), 404
    return jsonify(book.to_dict()), 200


@books_bp.patch("/<int:book_id>")
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        return jsonify({"error": "not_found", "message": "Book not found."}), 404

    payload = request.get_json(silent=True)
    error = validate_payload(payload, partial=True)
    if error:
        return jsonify({"error": "validation_failed", "message": error}), 400
    if not payload:
        return jsonify({"error": "validation_failed", "message": "Request body is empty."}), 400

    category, authors, error = resolve_related(payload)
    if error:
        return jsonify({"error": "related_resource_not_found", "message": error}), 400

    for field in ("title", "isbn", "price_vnd", "stock"):
        if field in payload:
            setattr(book, field, payload[field])
    if "category_id" in payload:
        book.category = category
    if "author_ids" in payload:
        book.authors = authors

    db.session.commit()
    return jsonify(book.to_dict()), 200


@books_bp.delete("/<int:book_id>")
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        return jsonify({"error": "not_found", "message": "Book not found."}), 404

    if Review.query.filter_by(book_id=book_id).first() is not None:
        return jsonify({
            "error": "conflict",
            "message": "Cannot delete a book that has reviews.",
        }), 409

    db.session.delete(book)
    db.session.commit()
    return "", 204
