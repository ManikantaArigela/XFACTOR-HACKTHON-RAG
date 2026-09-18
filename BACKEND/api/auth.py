from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from db.connection import SessionLocal
from db.models import User


auth_bp = Blueprint("auth_bp", __name__)


def create_user_account(email: str, password: str, full_name: str = None):
    normalized_email = (email or "").strip().lower()
    if not normalized_email or not password:
        return None

    session = SessionLocal()
    try:
        existing = session.query(User).filter(User.email == normalized_email).first()
        if existing:
            return None

        user = User(
            email=normalized_email,
            password_hash=generate_password_hash(password),
            full_name=full_name.strip() if full_name else None,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        session.rollback()
        return None
    finally:
        session.close()


def authenticate_user(email: str, password: str):
    normalized_email = (email or "").strip().lower()
    if not normalized_email or not password:
        return None

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == normalized_email).first()
        if not user:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user
    finally:
        session.close()


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    user = authenticate_user(email, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        },
    }), 200


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    full_name = data.get("full_name", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = create_user_account(email, password, full_name)
    if not user:
        return jsonify({"success": False, "message": "User already exists or registration failed."}), 409

    return jsonify({
        "success": True,
        "message": "User registered successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        },
    }), 201


@auth_bp.route("/login", methods=["GET"])
def login_page():
    return """
    <html>
      <head><title>Backend Login</title></head>
      <body>
        <h2>Backend Login</h2>
        <form method="post" action="/api/login">
          <input type="email" name="email" placeholder="Email" required /><br/><br/>
          <input type="password" name="password" placeholder="Password" required /><br/><br/>
          <button type="submit">Login</button>
        </form>
      </body>
    </html>
    """
