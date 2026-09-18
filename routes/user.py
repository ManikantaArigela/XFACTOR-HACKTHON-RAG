from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from models.user import User
from services.database import db
from utils.responses import failure, success
from utils.validation import require_json_fields

user_bp = Blueprint("user", __name__)


@user_bp.post("/users")
def create_user():
    payload = require_json_fields(request.get_json(silent=True), "email", "display_name")
    user = User(email=payload["email"].strip().lower(), display_name=payload["display_name"].strip())
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return failure("A user with that email already exists", 409)
    return success(user.to_dict(), "User created successfully", 201)


@user_bp.get("/users/<uuid:user_id>")
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return failure("User not found", 404)
    return success(user.to_dict())
