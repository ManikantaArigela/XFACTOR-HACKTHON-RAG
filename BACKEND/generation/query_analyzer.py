import re
from typing import Dict, Any, List, Optional

KNOWN_BRANDS = [
    "Samsung", "Apple", "iPhone", "Vivo", "Realme", "OnePlus", "Redmi", "Xiaomi",
    "Oppo", "Poco", "iQOO", "Motorola", "Lenovo", "Asus", "HP", "Acer", "Dell", "Huawei"
]

class QueryAnalyzer:
    """Analyzes user questions to extract structured intent, filters, and semantic search strings."""

    def analyze(self, query: str) -> Dict[str, Any]:
        cleaned_q = query.strip()
        
        is_adversarial = self._is_adversarial(cleaned_q)
        is_unsupported = self._is_unsupported(cleaned_q)
        
        brand = self._extract_brand(cleaned_q)
        max_price, min_price = self._extract_price(cleaned_q)
        ram = self._extract_ram(cleaned_q)
        storage = self._extract_storage(cleaned_q)
        category = self._extract_category(cleaned_q)
        
        requirements = self._extract_requirements(cleaned_q)
        semantic_query = cleaned_q

        return {
            "intent": "product_search",
            "category": category,
            "brand": brand,
            "max_price": max_price,
            "min_price": min_price,
            "ram": ram,
            "storage": storage,
            "requirements": requirements,
            "semantic_query": semantic_query,
            "original_query": cleaned_q,
            "is_adversarial": is_adversarial,
            "is_unsupported": is_unsupported
        }

    def _is_adversarial(self, text: str) -> bool:
        patterns = [
            r'\bignore\b.*\b(previous|all|system)\b.*\b(instructions|rules|prompts)\b',
            r'\bpretend\b',
            r'\bassume\b.*\b(sells?|has|stocks?|offers?|store)\b',
            r'\bjailbreak\b',
            r'\bdisregard\b',
            r'\bsystem\s+prompt\b',
            r'\byou\s+are\s+now\b',
            r'\broleplay\b'
        ]
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False

    def _is_unsupported(self, text: str) -> bool:
        patterns = [
            r'\b(smart\s*tvs?|tvs?|televisions?|oled\s*tv|qled\s*tv)\b',
            r'\b(refrigerators?|fridges?)\b',
            r'\b(playstations?|ps[45]|xboxes?|nintendos?|gaming\s*consoles?)\b',
            r'\b(washing\s*machines?)\b',
            r'\b(air\s*conditioners?|acs?)\b',
            r'\b(microwaves?|ovens?)\b',
            r'\b(return\s*policy|refund\s*policy|money\s*back)\b'
        ]
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        return False

    def _extract_brand(self, text: str) -> Optional[str]:
        for b in KNOWN_BRANDS:
            if re.search(r'\b' + re.escape(b) + r'\b', text, re.IGNORECASE):
                return "Apple" if b.lower() == "iphone" else b
        return None

    def _extract_category(self, text: str) -> Optional[str]:
        if re.search(r'\b(laptops?|macbooks?|notebooks?)\b', text, re.IGNORECASE):
            return "laptop"
        if re.search(r'\b(mobiles?|phones?|smartphones?|cellphones?)\b', text, re.IGNORECASE):
            return "smartphone"
        if re.search(r'\b(watch(es)?|smartwatch(es)?|bands?)\b', text, re.IGNORECASE):
            return "watch"
        return None

    def _extract_price(self, text: str) -> tuple[Optional[float], Optional[float]]:
        max_price = None
        min_price = None

        under_match = re.search(r'(?:under|below|less than|within|upto)\s*(?:₹|Rs\.?)?\s*(\d+(?:,\d+)?)\s*(k|thousand)?', text, re.IGNORECASE)
        if under_match:
            val = float(under_match.group(1).replace(',', ''))
            if under_match.group(2) and under_match.group(2).lower() == 'k':
                val *= 1000
            max_price = val

        above_match = re.search(r'(?:above|more than|starting from|over)\s*(?:₹|Rs\.?)?\s*(\d+(?:,\d+)?)\s*(k|thousand)?', text, re.IGNORECASE)
        if above_match:
            val = float(above_match.group(1).replace(',', ''))
            if above_match.group(2) and above_match.group(2).lower() == 'k':
                val *= 1000
            min_price = val

        return max_price, min_price

    def _extract_ram(self, text: str) -> Optional[str]:
        match = re.search(r'\b(\d+)\s*gb\s*ram\b', text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}GB"
        return None

    def _extract_storage(self, text: str) -> Optional[str]:
        match = re.search(r'\b(\d+)\s*(gb|tb)\s*(?:storage|rom|ssd)?\b', text, re.IGNORECASE)
        if match and "ram" not in text[match.start():match.end() + 5].lower():
            return f"{match.group(1)}{match.group(2).upper()}"
        return None

    def _extract_requirements(self, text: str) -> List[str]:
        reqs = []
        if re.search(r'\b(camera|portrait|nightography)\b', text, re.IGNORECASE):
            reqs.append("camera")
        if re.search(r'\b(battery|charging|fast charge)\b', text, re.IGNORECASE):
            reqs.append("battery")
        if re.search(r'\b(gaming|processor|fast|speed|snapdragon)\b', text, re.IGNORECASE):
            reqs.append("performance")
        if re.search(r'\b(cheap|cheapest|budget|low price)\b', text, re.IGNORECASE):
            reqs.append("budget")
        return reqs
