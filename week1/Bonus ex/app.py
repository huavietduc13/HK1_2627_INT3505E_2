from flask import Flask, jsonify, request
app = Flask(__name__)
_next = 1
BOOKS = [
    {
    "id":1,
    "title":"Clean Code",
    "author":"R. Martin"
    }
    ]

def find(bid):
    return next((b for b in BOOKS if b["id"] == bid), None)

@app.route("/books", methods=["GET"])
def list_books():
    #(a)
    limit = int(request.args.get("limit", 100))
    q = request.args.get("q", "").lower()
    _sort = request.args.get("sort")

    items = BOOKS
    if q:
        items = [b for b in BOOKS if (q in b["author"].lower() or q in b["title"].lower())]

    if _sort:
        items = sorted(items, key=lambda x: x[_sort])


    return jsonify(items[:limit]), 200

@app.route("/books/<int:bid>", methods=["GET"])
def get_books(bid):
    book = find(bid)
    if not book:
        return jsonify({"error": "not found"}), 404
    return jsonify(book), 200

@app.route("/books", methods=["POST"])
def create_books():
    global _next
    body = request.get_json(silent=True) or {}
    t, a = body.get("title"), body.get("author")
    if not t or not a:
        return jsonify({"error": "need title+author"}), 400

    #(c)
    year = body.get("year")
    if year != None and (not isinstance(year, int) or year < 1900):
        return jsonify({"error": "year phai la so nguyen >= 1900"}), 400
    
    _next+=1
    book = {"id":_next, "title":t, "author":a}
    BOOKS.append(book)
    return jsonify(book), 201, {"Location":f"/books/{book['id']}"}

@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book:
        return jsonify({"error": "not found"}), 404
    if request.method == "PUT":
        #(c)
        body = request.get_json(silent=True) or {}
        if "year" in body:
            year = body["year"]
            if year != None and (not isinstance(year, int) or year < 1900):
                    return jsonify({"error": "year phai la so nguyen >= 1900"}), 400
        book.update(body)
        return jsonify(book), 200
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)