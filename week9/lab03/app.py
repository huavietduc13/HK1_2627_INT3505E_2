from datetime import datetime, timezone
from flask import Flask, jsonify
from sunset import deprecate_at
import logging

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = Flask(__name__)
V1_SUNSET = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

EXPIRED_SUNSET = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


@app.route("/api/v1/users/<int:uid>")
@deprecate_at(V1_SUNSET, replacement="/api/v2/users")
def get_v1(uid):
    return {"id": uid, "full_name": "Nguyễn Văn A"}


@app.route("/api/v1/expired-users/<int:uid>")
@deprecate_at(EXPIRED_SUNSET, replacement="/api/v2/users")
def get_v1_expired(uid):
    return {"id": uid, "full_name": "Nguyễn Văn A"}


@app.route("/api/v2/users/<int:uid>")
def get_v2(uid):
    return {"id": uid, "first_name": "Văn", "last_name": "Nguyễn"}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
