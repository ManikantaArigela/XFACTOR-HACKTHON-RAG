import re
from typing import Dict, Any, Optional

KNOWN_BRANDS = [
    "Samsung", "Apple", "iPhone", "Vivo", "Realme", "OnePlus",
    "Redmi", "Xiaomi", "Oppo", "Poco", "iQOO", "Motorola", "Tecno", "Infinix"
]

class InformationExtractor:
    """Extracts structured product information from Instagram caption text."""

    def extract_brand(self, text: str) -> Optional[str]:
        for brand in KNOWN_BRANDS:
            pattern = r'\b' + re.escape(brand) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                if brand.lower() == "iphone":
                    return "Apple"
                return brand
        return None

    def extract_price(self, text: str) -> Optional[float]:
        # First priority: look for Arudhra price / offer price / deal price
        priority_patterns = [
            r'(?:Arudhra|offer|deal|special|best|discounted|sale)\s*(?:offer|market)?\s*(?:price|deal)?\s*(?:is|at|:)?\s*(?:₹|Rs\.?|INR)\s*([\d,]+)',
            r'(?:for\s+just|just\s+for|just)\s*(?:₹|Rs\.?|INR)\s*([\d,]+)'
        ]
        for pat in priority_patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    val = float(price_str)
                    if 1000 <= val <= 500000:
                        return val
                except ValueError:
                    pass

        # Fallback: find any ₹ match that is not immediately preceded by MRP/Market price
        matches = re.finditer(r'(?:₹|Rs\.?|INR)\s*([\d,]+)', text, re.IGNORECASE)
        for match in matches:
            prefix = text[max(0, match.start() - 20):match.start()].lower()
            if "mrp" in prefix or "market" in prefix or "company" in prefix:
                continue
            price_str = match.group(1).replace(',', '')
            try:
                val = float(price_str)
                if 1000 <= val <= 500000:
                    return val
            except ValueError:
                pass

        # Last fallback: match any price
        match = re.search(r'(?:₹|Rs\.?|INR)\s*([\d,]+)', text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                val = float(price_str)
                if 1000 <= val <= 500000:
                    return val
            except ValueError:
                pass
        return None

    def extract_ram(self, text: str) -> Optional[str]:
        # Match 8GB RAM or 8 GB RAM or (8GB/256GB)
        match = re.search(r'\b(\d+)\s*GB\s*(?:RAM)?\b', text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}GB"
        return None

    def extract_storage(self, text: str) -> Optional[str]:
        # Match 128GB Storage / 256 GB ROM / 1TB
        match = re.search(r'\b(\d+)\s*(GB|TB)\s*(?:Storage|ROM|Internal)?\b', text, re.IGNORECASE)
        if match:
            # Check if this match is not identical to RAM match if both exist
            val = match.group(1)
            unit = match.group(2).upper()
            return f"{val}{unit}"
        return None

    def extract_product_name(self, text: str, brand: Optional[str]) -> Optional[str]:
        # Handle em-dash, en-dash, hyphens, and delimiters
        patterns = [
            r'((?:Samsung|Apple|iPhone|Vivo|Realme|OnePlus|Redmi|Xiaomi|Oppo|Poco|iQOO|Motorola)\s+[A-Za-z0-9\s\+\-\(\)\—\–]+?)(?:\s*[\—\–]|\s*\d+GB|\s*\₹|\s*available|\s*now|\s*at|\!|\,|\n)',
            r'([A-Z][A-Za-z0-9\s\—\–]+(?:5G|4G|Pro|Ultra|Plus|Lite|Watch\s*\d+|Mini))'
        ]
        
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'[\(\s\-\+\—\–]+$', '', name).strip()
                if len(name) > 3 and len(name) < 60:
                    return name
        
        if brand:
            return f"{brand} Smartphone"
        return None

    def extract_specifications(self, text: str) -> Dict[str, Any]:
        specs = {}
        
        # Battery extraction (e.g. 5000mAh)
        battery_match = re.search(r'\b(\d+\s*mAh)\b', text, re.IGNORECASE)
        if battery_match:
            specs["battery"] = battery_match.group(1).replace(" ", "")

        # Camera extraction (e.g. 50MP, 48MP)
        camera_match = re.search(r'\b(\d+\s*MP)\b', text, re.IGNORECASE)
        if camera_match:
            specs["camera"] = camera_match.group(1).replace(" ", "")

        # Processor extraction (e.g. Snapdragon 8 Gen 2, Exynos 1330, A16 Bionic)
        proc_match = re.search(r'\b(Snapdragon\s+[A-Za-z0-9\s]+|Exynos\s+\d+|Dimensity\s+\d+|A\d+\s+Bionic)\b', text, re.IGNORECASE)
        if proc_match:
            specs["processor"] = proc_match.group(1).strip()

        # Fast Charging (e.g. 80W, 67W, 100W)
        charge_match = re.search(r'\b(\d+\s*W)\s*(?:FlashCharge|SUPERVOOC|charging)?\b', text, re.IGNORECASE)
        if charge_match:
            specs["charging"] = charge_match.group(1).replace(" ", "")

        return specs

    def extract_product_data(self, post: Dict[str, Any]) -> Dict[str, Any]:
        caption = post.get("caption", "")
        
        brand = post.get("brand") or self.extract_brand(caption)
        price = float(post["selling_price"]) if post.get("selling_price") is not None else self.extract_price(caption)
        ram = post.get("ram") or self.extract_ram(caption)
        storage = post.get("storage") or self.extract_storage(caption)
        name = post.get("product_name") or self.extract_product_name(caption, brand)
        specs = self.extract_specifications(caption)
        if post.get("features"):
            specs["features"] = post.get("features")

        category = (post.get("category") or "").lower()
        if not category:
            caption_lower = caption.lower()
            if any(k in caption_lower for k in ["laptop", "macbook", "notebook"]):
                category = "laptop"
            elif any(k in caption_lower for k in ["watch", "smartwatch"]):
                category = "watch"
            else:
                category = "smartphone"

        return {
            "name": name or "Mobile Smartphone",
            "brand": brand,
            "category": category,
            "model": name,
            "description": post.get("caption_body", caption),
            "price": price,
            "ram": ram,
            "storage": storage,
            "specifications": specs,
            "availability": True,
            "image_path": post.get("product_image_url") or post.get("image") or post.get("image_url") or post.get("local_image_path"),
            "poster_image_path": post.get("poster_image_url") or post.get("image") or post.get("image_url") or post.get("local_image_path"),
        }
