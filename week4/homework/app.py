from pathlib import Path
from uuid import UUID

import yaml
from flask import Flask, jsonify, request

app = Flask(__name__)
SPEC_PATH = Path(__file__).with_name("openapi.yaml")
TASKS = {}


def error(code, message, status):
    return jsonify({"code": code, "message": message}), status


@app.before_request
def require_bearer_token():
    if request.path in {"/docs", "/openapi.json"}:
        return None
    if not request.headers.get("Authorization", "").startswith("Bearer "):
        return error("unauthorized", "Provide a bearer token", 401)
    return None


@app.get("/openapi.json")
def openapi_json():
    return jsonify(yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8")))


@app.get("/docs")
def docs():
    return '''<!doctype html><html><head><title>Tasks API docs</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"></head>
<body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui'});</script></body></html>'''


def find_task(task_id):
    try:
        normalized = str(UUID(task_id))
    except ValueError:
        return None, error("not_found", "Task not found", 404)
    task = TASKS.get(normalized)
    return (task, None) if task else (None, error("not_found", "Task not found", 404))


@app.get("/v1/tasks/<task_id>")
def get_task(task_id):
    task, failure = find_task(task_id)
    return failure or jsonify(task)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
