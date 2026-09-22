import hashlib
import json
import sqlite3
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
DATABASE = 'shop.db'

def connect_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = connect_db()
    with open('db.sql', mode='r', encoding='utf-8') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

#for ETag hw03
def generate_etag(data_dict: dict) -> str:
    content = json.dumps(data_dict, sort_keys=True)
    return f'"{hashlib.md5(content.encode("utf-8")).hexdigest()}"'


# endpoints
@app.get("/books")
def list_books():
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM books")
    books = [dict(row) for row in cur.fetchall()]
    db.close()
    return jsonify({"data": books, "total": len(books)}), 200

@app.post("/books")
def create_book():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or "").strip()
    a = (p.get("author") or "").strip()
    
    if not t or not a:
        return jsonify(error="need title + author"), 422
    
    db = connect_db()
    cur = db.cursor()
    cur.execute("INSERT INTO books (title, author) VALUES (?, ?)", (t, a))
    db.commit()
    
    book_id = cur.lastrowid
    db.close()
    
    book = {"id": book_id, "title": t, "author": a}
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book_id}"
    return resp

@app.get("/books/<int:bid>")
def get_book(bid):
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM books WHERE id = ?", (bid,))
    book = cur.fetchone()
    db.close()
    
    if not book:
        return jsonify(error="not found"), 404

    #for ETag hw03
    book_dict = dict(book)
    etag = generate_etag(book_dict)
    
    if request.headers.get("If-None-Match") == etag:
        return make_response("", 304)
        
    resp = make_response(jsonify(book_dict), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    resp.headers["ETag"] = etag
    return resp

@app.get("/orders/<oid>")
def get_order(oid):
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (oid,))
    order = cur.fetchone()
    db.close()
    
    if not order:
        return jsonify(error="not found"), 404
    return jsonify(dict(order)), 200

if __name__ == '__main__':
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)