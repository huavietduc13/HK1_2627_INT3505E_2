from flask import Blueprint, jsonify
from sqlalchemy import text
from extensions import db

health_bp = Blueprint("health", __name__, url_prefix="")

# Liveness probe: Kiểm tra tiến trình có đang sống không (không phụ thuộc DB)
@health_bp.get("/healthz")
def liveness():
    return jsonify({"status": "ok"}), 200

# Readiness probe: Kiểm tra kết nối DB để biết đã sẵn sàng nhận request chưa
@health_bp.get("/ready")
def readiness():
    checks = {}
    try:
        db.session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception:
        checks["db"] = "err"

    ok = all(v == "ok" for v in checks.values())
    return jsonify({
        "status": "ok" if ok else "degraded",
        "checks": checks
    }), (200 if ok else 503)

