from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

posts = [
    {"id": 1, "title": "post 1", "content": "nd 1"},
    {"id": 2, "title": "post viết 2", "content": "nd 2"}
]

def problem_details(status: int, title: str, detail: str, errors: list = None):
    payload = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path
    }
    if errors:
        payload["errors"] = errors
    
    response = make_response(jsonify(payload), status)
    response.headers["Content-Type"] = "application/problem+json"
    return response


@app.route("/posts", methods=["GET"])
def get_posts():
    return jsonify(posts), 200


@app.route("/posts", methods=["POST"])
def create_post():
    if not request.is_json:
        return problem_details(
            status=400,
            title="Bad Request",
            detail="Request body must be application/json."
        )

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return problem_details(
            status=400,
            title="Bad Request",
            detail="JSON not valid"
        )

    validation_errors = []
    title = str(data.get("title") or "").strip()
    content = str(data.get("content") or "").strip()

    if not title:
        validation_errors.append({"field": "title", "reason": "Field cant be empty"})

    if not content:
        validation_errors.append({"field": "content", "reason": "content cant be empty"})

    if validation_errors:
        return problem_details(
            status=422,
            title="Unprocessable Content",
            detail="Data not valid",
            errors=validation_errors
        )

    new_post = {
        "id": len(posts) + 1 if posts else 1,
        "title": title,
        "content": content
    }
    posts.append(new_post)

    response = make_response(jsonify(new_post), 201)
    response.headers["Location"] = f"/posts/{new_post['id']}"
    return response


@app.route("/posts/<int:id>", methods=["GET"])
def get_post(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return problem_details(
            status=404,
            title="Not Found",
            detail=f"not found post with id = {id}."
        )
    return jsonify(post), 200


@app.route("/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    global posts
    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return problem_details(
            status=404,
            title="Not Found",
            detail=f"not found post with id = {id} to delete"
        )

    posts = [p for p in posts if p["id"] != id]
    return "", 204


@app.errorhandler(404)
def handle_404(e):
    return problem_details(
        status=404,
        title="Not Found",
        detail="endpoint not exist"
    )

@app.errorhandler(405)
def handle_405(e):
    return problem_details(
        status=405,
        title="Method Not Allowed",
        detail=f"Method {request.method} not supported"
    )

@app.errorhandler(500)
def handle_500(e):
    return problem_details(
        status=500,
        title="Internal Server Error",
        detail="Error at server"
    )


if __name__ == "__main__":
    app.run(debug=True)