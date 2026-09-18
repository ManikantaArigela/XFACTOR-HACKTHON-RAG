from typing import List, Dict, Any, Optional
from db.connection import SessionLocal
from db.models import Product

class StructuredSearchService:
    """Performs structured SQL queries on products table based on explicit filters."""

    def search(
        self,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        ram: Optional[str] = None,
        storage: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        session = SessionLocal()
        try:
            query = session.query(Product).filter(Product.availability == True)

            if brand:
                pattern = f"%{brand}%"
                query = query.filter((Product.brand.ilike(pattern)) | (Product.name.ilike(pattern)))
            
            if category:
                if category in ["smartphone", "mobile", "phone"]:
                    query = query.filter(
                        (Product.category.ilike("%smartphone%")) |
                        (Product.category.ilike("%mobile%")) |
                        (Product.category.ilike("%phone%"))
                    )
                else:
                    query = query.filter(Product.category.ilike(f"%{category}%"))

            if max_price is not None:
                query = query.filter(Product.price <= max_price)

            if min_price is not None:
                query = query.filter(Product.price >= min_price)

            if ram:
                query = query.filter(Product.ram.ilike(f"%{ram}%"))

            if storage:
                query = query.filter(Product.storage.ilike(f"%{storage}%"))

            products = query.all()

            results = []
            for p in products:
                post_id = p.source_post.instagram_post_id if p.source_post else None
                source_url = p.source_post.post_url if p.source_post else None
                poster_img = p.poster_image_path or (p.source_post.image_path if p.source_post else None) or p.image_path
                results.append({
                    "id": str(p.id),
                    "name": p.name,
                    "brand": p.brand,
                    "category": p.category,
                    "model": p.model,
                    "description": p.description,
                    "price": float(p.price) if p.price else None,
                    "ram": p.ram,
                    "storage": p.storage,
                    "specifications": p.specifications or {},
                    "image_path": p.image_path,
                    "poster_image_path": poster_img,
                    "source_id": str(p.source_id) if p.source_id else None,
                    "post_id": post_id,
                    "source_url": source_url
                })

            return results
        finally:
            session.close()
