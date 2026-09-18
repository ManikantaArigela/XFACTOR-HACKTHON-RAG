import os
import random
import string
from datetime import datetime, timezone
from decimal import Decimal
from flask import Blueprint, request, jsonify

from db.connection import SessionLocal
from db.models import Order, User
from api.auth import verify_user_token

orders_bp = Blueprint("orders", __name__)


def generate_order_number() -> str:
    """Generate human-readable order number like ARU-20260919-4821."""
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = "".join(random.choices(string.digits, k=4))
    return f"ARU-{date_part}-{random_part}"


@orders_bp.route("/api/orders", methods=["POST", "OPTIONS"])
def create_order():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    payload = request.get_json(silent=True) or {}

    # Extract customer info
    customer_name = (payload.get("customer_name") or payload.get("name") or "").strip()
    customer_phone = (payload.get("customer_phone") or payload.get("phone") or "").strip()
    shipping_address = (payload.get("shipping_address") or payload.get("address") or "").strip()
    city = (payload.get("city") or "Pithapuram").strip()
    pincode = (payload.get("pincode") or "533450").strip()
    payment_method = (payload.get("payment_method") or "Cash on Delivery").strip()
    delivery_method = (payload.get("delivery_method") or "Standard Store Delivery").strip()
    notes = (payload.get("notes") or payload.get("order_notes") or "").strip()
    items = payload.get("items") or []

    # Validations
    if not customer_name:
        return jsonify({"success": False, "message": "Customer name is required."}), 400

    if not customer_phone or len(customer_phone) < 7:
        return jsonify({"success": False, "message": "A valid customer phone number is required."}), 400

    if not shipping_address:
        return jsonify({"success": False, "message": "Delivery shipping address is required."}), 400

    if not items or not isinstance(items, list):
        return jsonify({"success": False, "message": "Order must contain at least one item."}), 400

    # Calculate or validate total amount
    calculated_total = Decimal("0.0")
    formatted_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id") or item.get("product_id") or "")
        item_name = str(item.get("name") or "Mobile / Electronic Item")
        try:
            item_price = Decimal(str(item.get("price") or 0))
        except Exception:
            item_price = Decimal("0.0")
        try:
            item_qty = max(1, int(item.get("qty") or item.get("quantity") or 1))
        except Exception:
            item_qty = 1
        item_image = item.get("image") or item.get("image_path") or ""

        calculated_total += item_price * item_qty
        formatted_items.append({
            "id": item_id,
            "name": item_name,
            "price": float(item_price),
            "qty": item_qty,
            "image": item_image
        })

    if not formatted_items:
        return jsonify({"success": False, "message": "Invalid item format provided."}), 400

    req_total = payload.get("total_amount") or payload.get("total")
    if req_total:
        try:
            total_amount = Decimal(str(req_total))
        except Exception:
            total_amount = calculated_total
    else:
        total_amount = calculated_total

    # Check authentication token if present
    auth_header = request.headers.get("Authorization", "")
    token = request.args.get("token") or payload.get("token") or auth_header
    token_data = verify_user_token(token) if token else None

    user_id = token_data["user_id"] if token_data else None
    customer_email = (payload.get("customer_email") or payload.get("email") or (token_data["email"] if token_data else "")).strip()

    order_number = generate_order_number()

    session = SessionLocal()
    try:
        order = Order(
            order_number=order_number,
            user_id=user_id,
            customer_name=customer_name,
            customer_email=customer_email or None,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            city=city,
            pincode=pincode,
            payment_method=payment_method,
            delivery_method=delivery_method,
            items=formatted_items,
            total_amount=total_amount,
            status="Confirmed",
            notes=notes or None,
            created_at=datetime.now(timezone.utc),
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        return jsonify({
            "success": True,
            "message": "Order placed successfully! Arudhra Mobile Stores team will process your order.",
            "order": {
                "id": str(order.id),
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "customer_phone": order.customer_phone,
                "shipping_address": order.shipping_address,
                "city": order.city,
                "pincode": order.pincode,
                "payment_method": order.payment_method,
                "delivery_method": order.delivery_method,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "items": order.items,
                "notes": order.notes,
                "created_at": order.created_at.isoformat() if order.created_at else None,
            }
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({"success": False, "message": f"Database error creating order: {str(e)}"}), 500
    finally:
        session.close()


@orders_bp.route("/api/orders", methods=["GET", "OPTIONS"])
def list_orders():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    auth_header = request.headers.get("Authorization", "")
    token = request.args.get("token") or auth_header
    token_data = verify_user_token(token) if token else None

    session = SessionLocal()
    try:
        query = session.query(Order)

        if token_data:
            # Match by user_id or email
            query = query.filter(
                (Order.user_id == token_data["user_id"]) | 
                (Order.customer_email == token_data["email"])
            )
        else:
            email_param = request.args.get("email")
            phone_param = request.args.get("phone")
            if email_param:
                query = query.filter(Order.customer_email == email_param.strip())
            elif phone_param:
                query = query.filter(Order.customer_phone == phone_param.strip())
            else:
                return jsonify({
                    "success": False, 
                    "message": "Authentication token or customer email/phone query parameter is required to view orders."
                }), 401

        orders = query.order_by(Order.created_at.desc()).all()

        return jsonify({
            "success": True,
            "orders": [
                {
                    "id": str(o.id),
                    "order_number": o.order_number,
                    "customer_name": o.customer_name,
                    "customer_email": o.customer_email,
                    "customer_phone": o.customer_phone,
                    "shipping_address": o.shipping_address,
                    "city": o.city,
                    "pincode": o.pincode,
                    "payment_method": o.payment_method,
                    "delivery_method": o.delivery_method,
                    "total_amount": float(o.total_amount),
                    "status": o.status,
                    "items": o.items,
                    "notes": o.notes,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                }
                for o in orders
            ]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to retrieve orders: {str(e)}"}), 500
    finally:
        session.close()


@orders_bp.route("/api/orders/<order_ref>", methods=["GET", "OPTIONS"])
def get_order_by_ref(order_ref: str):
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    session = SessionLocal()
    try:
        order = session.query(Order).filter(
            (Order.order_number == order_ref) | (Order.id == order_ref)
        ).first()

        if not order:
            return jsonify({"success": False, "message": "Order not found."}), 404

        return jsonify({
            "success": True,
            "order": {
                "id": str(order.id),
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "customer_phone": order.customer_phone,
                "shipping_address": order.shipping_address,
                "city": order.city,
                "pincode": order.pincode,
                "payment_method": order.payment_method,
                "delivery_method": order.delivery_method,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "items": order.items,
                "notes": order.notes,
                "created_at": order.created_at.isoformat() if order.created_at else None,
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error retrieving order: {str(e)}"}), 500
    finally:
        session.close()
