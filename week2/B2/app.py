from flask import Flask, jsonify, request, make_response
app = Flask(__name__)
BOOKS = [
    {
        "id": 1,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "isbn": "978-0060935467",
        "price": 15.99
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935",
        "price": 12.99
    },
    {
        "id": 3,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "978-0743273565",
        "price": 10.99
    },
    {
        "id": 4,
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "isbn": "978-0316769174",
        "price": 11.50
    },
    {
        "id": 5,
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "isbn": "978-1503290563",
        "price": 9.99
    }
]

# GET /books/<bid> (cache 60s)
@app.get("/books/<int:bid>")
def fetch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404
    resp = make_response(jsonify(BOOKS[i]), 200)
    resp.headers["Cache-Control"]="max-age=60"
    return resp

# PUT
@app.put("/books/<int:bid>")
def put(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    print("Dữ liệu Flask nhận được là:", p)
    a = p.get("author")
    t = p.get("title")
    if not a or not t:
        return jsonify(error="need author + title"), 422
    BOOKS[i] = {
        "id": bid,
        "title": t.strip(),
        "author": a.strip(),
        "isbn": p.get("isbn"),
        "price": p.get("price")
    }

    return jsonify(BOOKS[i]), 200

# PATCH
@app.patch("/books/<int:bid>")
def patch(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}
    if p.get("price") < 0:
        return jsonify(error="price must be positive"), 422
    for k in "title author isbn price".split():
        if k in p:
            BOOKS[i][k] = p[k]
    return jsonify(BOOKS[i]), 200

@app.delete("/books/<int:bid>")
def delete(bid):
    i = next((k for k, b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None:
        return jsonify(error="not found"), 404

    BOOKS.pop(i)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)