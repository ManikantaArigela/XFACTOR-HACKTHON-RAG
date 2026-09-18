from typing import Dict, Any
from config.settings import settings

class RAGDocumentBuilder:
    """Builds standardized RAG knowledge documents with rich metadata headers."""

    def build_document(self, post: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
        """Combine instagram post and structured product data into a single grounded document."""
        
        lines = [
            f"Store: {settings.STORE_NAME}",
            f"Location: {settings.STORE_LOCATION}",
            f"Source: Instagram Post (ID: {post.get('instagram_post_id')})",
        ]
        
        if post.get("post_url"):
            lines.append(f"Source URL: {post.get('post_url')}")
            
        if post.get("posted_at"):
            lines.append(f"Post Date: {post.get('posted_at')}")
            
        lines.append("") # Blank separator
        lines.append(f"Product Name: {product.get('name')}")
        
        if product.get("brand"):
            lines.append(f"Brand: {product.get('brand')}")
            
        if product.get("category"):
            lines.append(f"Category: {product.get('category')}")
            
        if product.get("price"):
            lines.append(f"Price: ₹{product.get('price'):,.2f}")
            
        if product.get("ram"):
            lines.append(f"RAM: {product.get('ram')}")
            
        if product.get("storage"):
            lines.append(f"Storage: {product.get('storage')}")
            
        if product.get("availability"):
            lines.append("Availability: Available in store (Arudhra Mobile Stores, Pithapuram)")

        if product.get("specifications"):
            specs_str = ", ".join([f"{k}: {v}" for k, v in product["specifications"].items()])
            lines.append(f"Key Specifications: {specs_str}")

        lines.append("") # Blank separator
        lines.append("Post Caption & Store Details:")
        lines.append(post.get("caption", ""))

        content = "\n".join(lines)

        posted_at_val = str(post.get("posted_at")) if post.get("posted_at") else None
        metadata = {
            "store_name": settings.STORE_NAME,
            "location": settings.STORE_LOCATION,
            "instagram_post_id": post.get("instagram_post_id"),
            "post_url": post.get("post_url"),
            "posted_at": posted_at_val,
            "brand": product.get("brand"),
            "name": product.get("name"),
            "category": product.get("category"),
            "price": product.get("price"),
            "ram": product.get("ram"),
            "storage": product.get("storage"),
            "image_path": product.get("image_path"),
            "poster_image_path": product.get("poster_image_path") or post.get("poster_image_url") or post.get("image_url")
        }

        return {
            "content": content,
            "source_type": "instagram_post",
            "source_id": post.get("instagram_post_id"),
            "metadata": metadata
        }
