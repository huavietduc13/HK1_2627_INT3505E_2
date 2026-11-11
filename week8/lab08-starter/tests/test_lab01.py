import pytest
from jsonschema import validate
from tools import get_book_schema


def test_get_books_empty(client):
    r = client.get("/books")
    assert r.status_code == 200
    assert r.content_type == "application/json"
    data = r.get_json()
    assert data is not None
    assert data == []

def test_get_book_not_found(client):
    r = client.get("/books/9999")
    assert r.status_code == 404
    data = r.get_json()
    assert data is not None
    assert data.get("code") == "NOT_FOUND"

def test_post_book_missing_title(client):
    r = client.post("/books", json={"author": "Clean Code Author", "year": 2020})
    assert r.status_code == 400
    data = r.get_json()
    assert "errors" in data
    fields = {e.get("field") for e in data.get("errors", [])}
    assert "title" in fields

def test_delete_then_get_404(client, sample_book):
    del_res = client.delete(f"/books/{sample_book}")
    assert del_res.status_code == 204

    get_res = client.get(f"/books/{sample_book}")
    assert get_res.status_code == 404


def test_response_extra_field_blocked(client, sample_book):
    schema = get_book_schema()

    if "year" in schema.get("properties", {}):
        schema["properties"]["year"]["type"] = ["integer", "null"]
    if "isbn" in schema.get("properties", {}):
        schema["properties"]["isbn"]["type"] = ["string", "null"]

    r = client.get(f"/books/{sample_book}")
    assert r.status_code == 200
    book_data = r.get_json()

    validate(instance=book_data, schema=schema)

    tampered_data = dict(book_data)
    tampered_data["password_hash"] = "argon2id$v=19$m=65536..."
    from jsonschema.exceptions import ValidationError
    with pytest.raises(ValidationError):
        validate(instance=tampered_data, schema=schema)

