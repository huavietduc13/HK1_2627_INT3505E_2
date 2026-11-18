from blueprints.users_data import USERS
from flask import Blueprint
from .users_data import get_user
bp = Blueprint("v2", __name__, url_prefix="/users")
@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u:
        return {"error": "nf"}, 404
    return {
        "id": uid,
        "first_name": u["first_name"],
        "last_name": u["last_name"],
        "email": u["email"]
    }

def create_user(first_name, last_name, email):
    new_id = max(USERS.keys(), 0) + 1
    user = {
        "id": new_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }
    USERS[new_id] = user
    return user