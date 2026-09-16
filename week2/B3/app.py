from flask import Flask, jsonify, request, make_response
app = Flask(__name__)
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "1984", "author": "George Orwell"},
    {"id": 3, "title": "Animal Farm", "author": "George Orwell"},
    {"id": 4, "title": "The Pragmatic Programmer", "author": "Andrew Hunt"},
    {"id": 5, "title": "Refactoring", "author": "Martin Fowler"},
    {"id": 6, "title": "Design Patterns", "author": "Erich Gamma"},
    {"id": 7, "title": "Introduction to Algorithms", "author": "Thomas H. Cormen"},
    {"id": 8, "title": "Head First Design Patterns", "author": "Eric Freeman"},
    {"id": 9, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"id": 10, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"}
]

DEFAULT_SIZE, MAX_SIZE = 20, 100
@app.get("/books")
def list_book():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400
    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    flt = BOOKS
    a = request.args.get("author")
    if a:
        flt = [b for b in flt if a.lower() in b["author"].lower()]
    q = request.args.get("q") or ""
    q = q.lower()
    if q:
        flt = [b for b in flt if q in b["title"].lower()]

    total = len(flt)
    start = (page-1)*size
    end = start+size
    items = flt[start:end]
    last = (total+size-1)//size

    def u(p):
        return f"/books?page={p}&size={size}"
    links = {"self":{"href":u(page)},
            "first":{"href":u(1)},
            "last":{"href":u(max(last,1))}
             }
    if page > 1: links["prev"]={"href":u(page-1)}
    if end < total: links["next"]={"href":u(page+1)}
    body = {"data":items,
    "pagination":{"page":page,"size":size,"total":total,"total_pages":last},
    "_links":links}
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"]="public, max-age=30"
    return resp

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)