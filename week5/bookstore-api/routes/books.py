import base64
import binascii
import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from sqlalchemy import and_, or_

from models import Author, Book, Category, Review, db


books_bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

SCHEMA_PATH = Path(__file__).resolve().parent.parent /"schemas"/"book.json"
with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
    BOOK_CREATE_SCHEMA = json.load(schema_file)

DEFAULT_LIMIT = 20
MAX_LIMIT = 100
SORT_COLUMNS = {
    "id": Book.id,
    "title": Book.title,
    "isbn": Book.isbn,
    "price_vnd": Book.price_vnd,
    "stock": Book.stock,
}


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


def parse_int_param(name, default, *, minimum):
    raw_value = request.args.get(name)
    if raw_value is None or raw_value.strip() == "":
        return default, None
    try:
        value = int(raw_value)
    except ValueError:
        return None, f"{name} must be an integer."
    if value < minimum:
        return None, f"{name} must be at least {minimum}."
    return value, None


def parse_sort(raw_sort):
    raw_keys = [k.strip() for k in raw_sort.split(",") if k.strip()]
    if not raw_keys:
        raw_keys = ["-id"]

    sort_specs = []
    seen_fields = set()

    for raw_key in raw_keys:
        descending = raw_key.startswith("-")
        field = raw_key[1:] if descending else raw_key

        if field not in SORT_COLUMNS:
            return None, f"Unsupported sort field: {field or raw_key}."
        if field in seen_fields:
            return None, f"Sort field appears more than once: {field}."

        seen_fields.add(field)
        sort_specs.append((field, descending, SORT_COLUMNS[field]))

    if "id" not in seen_fields:
        sort_specs.append(("id", False, SORT_COLUMNS["id"]))

    return sort_specs, None


def encode_cursor(book, sort_specs, genre):
    state = {
        "sort": [f"{'-' if desc else ''}{field}" for field, desc, _ in sort_specs],
        "genre": genre,
        "values": [getattr(book, field) for field, _, _ in sort_specs],
    }
    raw = json.dumps(state, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(raw_cursor, sort_specs, genre):
    if not raw_cursor or len(raw_cursor) > 4096:
        return None, "Cursor is empty or too long."

    try:
        padding = "=" * (-len(raw_cursor) % 4)
        state = json.loads(base64.urlsafe_b64decode(raw_cursor + padding))
    except (ValueError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
        return None, "Cursor is not valid base64-encoded JSON."

    if not isinstance(state, dict):
        return None, "Cursor payload must be an object."

    expected_sort = [f"{'-' if desc else ''}{field}" for field, desc, _ in sort_specs]
    if state.get("sort") != expected_sort:
        return None, "Cursor does not match the requested sort."
    if state.get("genre") != genre:
        return None, "Cursor does not match the requested genre filter."

    values = state.get("values")
    if not isinstance(values, list) or len(values) != len(sort_specs):
        return None, "Cursor has invalid sort values."

    for value, (field, _, _) in zip(values, sort_specs):
        expected_type = int if field in {"id", "price_vnd", "stock"} else str
        if type(value) is not expected_type:
            return None, "Cursor has invalid sort values."

    return values, None


def build_cursor_filter(sort_specs, values):

    conditions = []
    equal_prefix = []
    for (_, descending, column), val in zip(sort_specs, values):
        compare_op = column < val if descending else column > val
        conditions.append(and_(*equal_prefix, compare_op))
        equal_prefix.append(column == val)
    return or_(*conditions)


def paginate_by_offset(query, order_by, limit):
    offset, error = parse_int_param("offset", default=0, minimum=0)
    if error:
        return jsonify({"error": "invalid_pagination", "message": error}), 400

    total = query.count()
    books = query.order_by(*order_by).offset(offset).limit(limit).all()

    return jsonify({
        "data": [book.to_dict() for book in books],
        "pagination": {
            "strategy": "offset",
            "offset": offset,
            "limit": limit,
            "total": total,
            "has_more": (offset + len(books)) < total,
        },
    }), 200


def paginate_by_cursor(query, order_by, sort_specs, genre, limit):
    raw_cursor = request.args.get("cursor")
    if raw_cursor and raw_cursor.strip():
        cursor_values, error = decode_cursor(raw_cursor.strip(), sort_specs, genre)
        if error:
            return jsonify({"error": "invalid_cursor", "message": error}), 400
        query = query.filter(build_cursor_filter(sort_specs, cursor_values))

    books = query.order_by(*order_by).limit(limit + 1).all()
    has_more = len(books) > limit
    books = books[:limit]

    next_cursor = encode_cursor(books[-1], sort_specs, genre) if (books and has_more) else None

    return jsonify({
        "data": [book.to_dict() for book in books],
        "pagination": {
            "strategy": "cursor",
            "limit": limit,
            "next_cursor": next_cursor,
            "has_more": has_more,
        },
    }), 200

@books_bp.get("")
def list_books():
    strategy = request.args.get("strategy", "offset").strip().lower()
    if strategy not in {"offset", "cursor"}:
        return jsonify({
            "error": "invalid_strategy",
            "message": "strategy must be 'offset' or 'cursor'."
        }), 400

    limit, error = parse_int_param("limit", default=DEFAULT_LIMIT, minimum=1)
    if error:
        return jsonify({"error": "invalid_pagination", "message": error}), 400
    limit = min(limit, MAX_LIMIT)

    raw_sort = request.args.get("sort", "-id").strip() or "-id"
    sort_specs, error = parse_sort(raw_sort)
    if error:
        return jsonify({"error": "invalid_sort", "message": error}), 400
    order_by = [col.desc() if desc else col.asc() for _, desc, col in sort_specs]

    raw_genre = request.args.get("genre")
    genre = raw_genre.strip().lower() if raw_genre and raw_genre.strip() else None

    query = Book.query
    if genre:
        query = query.join(Book.category).filter(Category.slug == genre)

    if strategy == "offset":
        return paginate_by_offset(query, order_by, limit)
    else:
        return paginate_by_cursor(query, order_by, sort_specs, genre, limit)


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
