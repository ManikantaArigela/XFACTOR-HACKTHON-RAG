from flask import Blueprint, request, jsonify
from db.connection import SessionLocal
from db.models import Product

products_bp = Blueprint("products_bp", __name__)

@products_bp.route("/api/products", methods=["GET"])
@products_bp.route("/api/content/", methods=["GET"])
def get_products():
    limit = request.args.get("limit", default=50, type=int)
    session = SessionLocal()
    try:
        products = session.query(Product).filter(Product.availability == True).limit(limit).all()
        items = []
        for p in products:
            items.append({
                "id": str(p.id),
                "name": p.name,
                "title": p.name,
                "brand": p.brand,
                "category": p.category or "smartphone",
                "model": p.model,
                "description": p.description or f"{p.ram or ''} {p.storage or ''}".strip(),
                "price": float(p.price) if p.price else None,
                "ram": p.ram,
                "storage": p.storage,
                "specifications": p.specifications or {},
                "image_path": p.image_path, # Clean mobile hardware showcase image
                "poster_image_path": p.poster_image_path # Poster flyer image (chat only)
            })
        return jsonify({"data": {"items": items}, "total": len(items)}), 200
    except Exception as e:
        print(f"[API ERROR] Failed to fetch products: {e}")
        return jsonify({"data": {"items": []}, "total": 0}), 200
    finally:
        session.close()

@products_bp.route("/api/search", methods=["GET"])
def search_products():
    query_str = request.args.get("q", "").strip()
    limit = request.args.get("limit", default=50, type=int)
    session = SessionLocal()
    try:
        query = session.query(Product).filter(Product.availability == True)
        if query_str:
            pattern = f"%{query_str}%"
            query = query.filter(
                (Product.name.ilike(pattern)) |
                (Product.brand.ilike(pattern)) |
                (Product.description.ilike(pattern)) |
                (Product.ram.ilike(pattern)) |
                (Product.storage.ilike(pattern))
            )
        products = query.limit(limit).all()
        results = []
        for p in products:
            results.append({
                "id": str(p.id),
                "name": p.name,
                "title": p.name,
                "brand": p.brand,
                "category": p.category or "smartphone",
                "model": p.model,
                "description": p.description or f"{p.ram or ''} {p.storage or ''}".strip(),
                "price": float(p.price) if p.price else None,
                "ram": p.ram,
                "storage": p.storage,
                "specifications": p.specifications or {},
                "image_path": p.image_path, # Clean mobile hardware showcase image
                "poster_image_path": p.poster_image_path
            })
        return jsonify({"data": {"results": results}, "total": len(results)}), 200
    except Exception as e:
        print(f"[API ERROR] Failed to search products: {e}")
        return jsonify({"data": {"results": []}, "total": 0}), 200
    finally:
        session.close()

@products_bp.route("/api/products/<product_id>", methods=["GET"])
def get_product_detail(product_id):
    session = SessionLocal()
    try:
        p = session.query(Product).filter_by(id=product_id).first()
        if not p:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({
            "id": str(p.id),
            "name": p.name,
            "title": p.name,
            "brand": p.brand,
            "category": p.category or "smartphone",
            "model": p.model,
            "description": p.description,
            "price": float(p.price) if p.price else None,
            "ram": p.ram,
            "storage": p.storage,
            "specifications": p.specifications or {},
            "image_path": p.image_path,
            "poster_image_path": p.poster_image_path
        }), 200
    finally:
        session.close()
