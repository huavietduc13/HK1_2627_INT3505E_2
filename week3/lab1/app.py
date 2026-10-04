from flask import Flask, jsonify, request

app = Flask(__name__)

posts = [
    {"id": 1, "title": "title1", "content": "conten1", "author_id": 101, "tags": ["tech", "api"]},
    {"id": 2, "title": "title2", "content": "content2", "author_id": 102, "tags": ["python", "flask"]}
]

@app.route("/posts", methods=["GET"])
def get_posts():
    tag = request.args.get("tag")
    author_id = request.args.get("author_id", type=int)

    filtered_posts = posts
    if tag:
        filtered_posts = [p for p in filtered_posts if tag in p["tags"]]
    if author_id:
        filtered_posts = [p for p in filtered_posts if p["author_id"] == author_id]

    return jsonify(filtered_posts), 200


@app.route("posts", methods=["POST"])
def create_post():
    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"title": "Bad Request", "detail": "Missing title or content"}), 400

    new_post = {
        "id": len(posts) + 1,
        "title": data["title"],
        "content": data["content"],
        "author_id": data.get("author_id", 1),
        "tags": data.get("tags", [])
    }
    posts.append(new_post)
    return jsonify(new_post), 201


@app.route("/posts/<int:id>", methods=["GET"])
def get_post_detail(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return jsonify({"title": "Not Found", "detail": f"Post {id} not found"}), 404
    return jsonify(post), 200


@app.route("/posts/<int:id>", methods=["PATCH"])
def update_post(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return jsonify({"title": "Not Found", "detail": f"Post {id} not found"}), 404

    data = request.get_json() or {}
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    if "tags" in data:
        post["tags"] = data["tags"]

    return jsonify(post), 200


@app.route("/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    global posts
    posts = [p for p in posts if p["id"] != id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)