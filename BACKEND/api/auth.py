import os
import re
import hmac
import hashlib
import time
import base64
from flask import Blueprint, jsonify, request, redirect
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from db.connection import SessionLocal
from db.models import User

auth_bp = Blueprint("auth_bp", __name__)

AUTH_SECRET = os.getenv("AUTH_SECRET", "arudhra-mobile-stores-secret-key-pithapuram-2026")


def generate_user_token(user_id: str, email: str) -> str:
    """Generate a tamper-proof signed bearer token."""
    payload = f"{user_id}:{email}:{int(time.time())}"
    encoded_payload = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")
    sig = hmac.new(AUTH_SECRET.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"amt.{encoded_payload}.{sig}"


def verify_user_token(token: str):
    """Verify signed bearer token and return user payload or None."""
    if not token or not isinstance(token, str):
        return None
    token = token.strip()
    if token.startswith("Bearer "):
        token = token[7:].strip()
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "amt":
        return None
    _, encoded_payload, sig = parts
    expected_sig = hmac.new(AUTH_SECRET.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None
    try:
        decoded = base64.urlsafe_b64decode(encoded_payload.encode("utf-8")).decode("utf-8")
        user_id, email, issued_at = decoded.split(":")
        return {"user_id": user_id, "email": email, "issued_at": int(issued_at)}
    except Exception:
        return None


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


@auth_bp.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = authenticate_user(email, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    token = generate_user_token(str(user.id), user.email)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        },
    }), 200


@auth_bp.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400

    # Validate email format
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, email):
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    if not password:
        return jsonify({"success": False, "message": "Password is required."}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    user = create_user_account(email, password, full_name)
    if not user:
        return jsonify({"success": False, "message": "An account with this email already exists. Please log in."}), 409

    token = generate_user_token(str(user.id), user.email)

    return jsonify({
        "success": True,
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        },
    }), 201


@auth_bp.route("/api/me", methods=["GET", "OPTIONS"])
def get_current_user():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    auth_header = request.headers.get("Authorization", "")
    token = request.args.get("token") or auth_header

    token_data = verify_user_token(token)
    if not token_data:
        return jsonify({"success": False, "message": "Invalid or expired session token."}), 401

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == token_data["user_id"]).first()
        if not user or not user.is_active:
            return jsonify({"success": False, "message": "User account not found or inactive."}), 401

        return jsonify({
            "success": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
            }
        }), 200
    finally:
        session.close()


@auth_bp.route("/api/logout", methods=["POST", "OPTIONS"])
def logout():
    return jsonify({"success": True, "message": "Logged out successfully"}), 200


@auth_bp.route("/login", methods=["GET"])
def login_page():
    # If accessed directly in browser, redirect to frontend login page
    return redirect("http://localhost:8000/login-tailwind.html", code=302)
