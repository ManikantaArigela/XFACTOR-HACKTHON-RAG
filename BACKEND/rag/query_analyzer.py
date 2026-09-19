import re
from typing import Dict, Any, List, Optional

KNOWN_BRANDS = [
    "Samsung", "Apple", "iPhone", "Vivo", "Realme", "OnePlus", "Redmi", "Xiaomi",
    "Oppo", "Poco", "iQOO", "Motorola", "Lenovo", "Asus", "HP", "Acer", "Dell", "Huawei"
]

GREETING_PATTERNS = [
    r'^(hi|hello|hey|heya|howdy|namaste|namaskar|namaskaram|vanakkam|sup|yo)\b',
    r'\b(good\s+(morning|afternoon|evening|day))\b',
    r'^(how\s+are\s+you|who\s+are\s+you|what\s+can\s+you\s+do|help|help\s+me)\b',
    r'\b(thank\s+you|thanks|thank\s+u)\b',
    r'^(bye|goodbye|see\s+you|tata)\b'
]

STORE_INFO_PATTERNS = [
    r'\b(where\b.*(location|located|store|shop|place|branch|it)|location|address|how\s+to\s+reach|directions?|store\s+location|shop\s+location|pithapuram\s+store)\b',
    r'\b(store\s+timings?|opening\s+hours?|open\s+time|closing\s+time|working\s+hours?|when\s+do\s+you\s+open|when\s+do\s+you\s+close)\b',
    r'\b(contact\s+number|phone\s+number|call\s+you|store\s+phone|helpline|support\s+number)\b',
]

class QueryAnalyzer:
    """Analyzes user questions to extract structured intent, filters, target models, specific attributes, and conversation context."""

    def analyze(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        cleaned_q = query.strip()
        
        is_adversarial = self._is_adversarial(cleaned_q)
        is_unsupported = self._is_unsupported(cleaned_q)
        
        # 1. Greeting / conversational detection
        if not is_adversarial and not is_unsupported and self._is_greeting(cleaned_q):
            return {
                "intent": "greeting",
                "category": None,
                "brand": None,
                "max_price": None,
                "min_price": None,
                "ram": None,
                "storage": None,
                "is_5g": False,
                "target_attribute": "greeting",
                "requirements": [],
                "target_model": None,
                "model_tokens": [],
                "is_specific_model": False,
                "semantic_query": cleaned_q,
                "original_query": cleaned_q,
                "is_adversarial": False,
                "is_unsupported": False
            }

        # 2. Store info detection
        if not is_adversarial and not is_unsupported and self._is_store_info(cleaned_q):
            return {
                "intent": "store_info",
                "category": None,
                "brand": None,
                "max_price": None,
                "min_price": None,
                "ram": None,
                "storage": None,
                "is_5g": False,
                "target_attribute": "store_info",
                "requirements": [],
                "target_model": None,
                "model_tokens": [],
                "is_specific_model": False,
                "semantic_query": cleaned_q,
                "original_query": cleaned_q,
                "is_adversarial": False,
                "is_unsupported": False
            }

        brand = self._extract_brand(cleaned_q)
        max_price, min_price = self._extract_price(cleaned_q)
        ram = self._extract_ram(cleaned_q)
        storage = self._extract_storage(cleaned_q)
        category = self._extract_category(cleaned_q)
        requirements = self._extract_requirements(cleaned_q)
        is_5g = bool(re.search(r'\b5g\b', cleaned_q, re.IGNORECASE))
        if is_5g and "5g" not in requirements:
            requirements.append("5g")
        
        # 3. Specific model extraction
        target_model, model_tokens, is_specific_model = self._extract_target_model(cleaned_q, brand)

        # 4. Multi-turn reference resolution from conversation history
        if not is_specific_model and history and self._has_contextual_reference(cleaned_q):
            hist_brand, hist_model, hist_tokens = self._resolve_context_from_history(history)
            if hist_brand and not brand:
                brand = hist_brand
            if hist_model:
                target_model = hist_model
                model_tokens = hist_tokens
                is_specific_model = True

        # 5. Extract specific attribute requested by the user
        target_attribute = self._extract_target_attribute(cleaned_q)
        
        # 6. Recognize general catalog / category browsing requests (e.g. "mobiles", "smartphones", "laptops")
        lower_q = cleaned_q.lower().strip()
        is_pure_category_query = lower_q in [
            "mobiles", "mobile", "phones", "phone", "smartphones", "smartphone",
            "all mobiles", "show mobiles", "list mobiles", "view mobiles", "available mobiles",
            "laptops", "laptop", "smartwatches", "smartwatch", "watches", "watch"
        ]
        
        if is_pure_category_query or (category and not brand and not is_specific_model and not max_price and not min_price and target_attribute in ["general", "general_specs", "recommendation"]):
            category = category or "smartphone"
            target_attribute = "catalog_browse"
            semantic_query = f"{category} available at Arudhra Mobile Stores Pithapuram"
        else:
            semantic_query = cleaned_q

        return {
            "intent": "product_search",
            "category": category,
            "brand": brand,
            "max_price": max_price,
            "min_price": min_price,
            "ram": ram,
            "storage": storage,
            "is_5g": is_5g,
            "target_attribute": target_attribute,
            "requirements": requirements,
            "target_model": target_model,
            "model_tokens": model_tokens,
            "is_specific_model": is_specific_model,
            "semantic_query": semantic_query,
            "original_query": cleaned_q,
            "is_adversarial": is_adversarial,
            "is_unsupported": is_unsupported
        }

    def _is_greeting(self, text: str) -> bool:
        lower_q = text.lower().strip()
        for gp in GREETING_PATTERNS:
            if re.search(gp, lower_q):
                has_brand = any(re.search(r'\b' + re.escape(b.lower()) + r'\b', lower_q) for b in KNOWN_BRANDS)
                has_product_word = bool(re.search(r'\b(phone|mobile|smartphone|laptop|macbook|price|cost|buy|shop|specs?|deal|offer)\b', lower_q))
                if not has_brand and not has_product_word:
                    return True
        return False

    def _is_store_info(self, text: str) -> bool:
        lower_q = text.lower().strip()
        for sip in STORE_INFO_PATTERNS:
            if re.search(sip, lower_q):
                return True
        return False

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

        under_match = re.search(r'(?:under|below|less than|within|upto)\s*(?:₹|Rs\.?|inr)?\s*(\d+(?:,\d+)?)\s*(k|thousand)?', text, re.IGNORECASE)
        if under_match:
            val = float(under_match.group(1).replace(',', ''))
            if under_match.group(2) and under_match.group(2).lower() == 'k':
                val *= 1000
            max_price = val

        above_match = re.search(r'(?:above|more than|starting from|over)\s*(?:₹|Rs\.?|inr)?\s*(\d+(?:,\d+)?)\s*(k|thousand)?', text, re.IGNORECASE)
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
        if re.search(r'\b(camera|portrait|nightography|selfie|megapixels?|\bmp\b)\b', text, re.IGNORECASE):
            reqs.append("camera")
        if re.search(r'\b(battery|charging|fast charge|mah|\bwatt\b|\bw\b charger)\b', text, re.IGNORECASE):
            reqs.append("battery")
        if re.search(r'\b(gaming|processor|fast|speed|snapdragon|dimensity|performance)\b', text, re.IGNORECASE):
            reqs.append("performance")
        if re.search(r'\b(cheap|cheapest|budget|low price|affordable)\b', text, re.IGNORECASE):
            reqs.append("budget")
        return reqs

    def _extract_target_attribute(self, text: str) -> str:
        """Determines the specific information requested by the user."""
        lower = text.lower()
        if re.search(r'\b(price|cost|how much|rate|pricing|worth|cheap|cheapest|budget|expensive)\b', lower):
            return "price"
        if re.search(r'\b(charging|fast charge|fast charging|battery|mah|watt|\bw\b charger|battery life|backup)\b', lower):
            return "battery_charging"
        if re.search(r'\b(camera|megapixels?|\bmp\b|portrait|selfie|photos?|video|nightography|lens|sensors?|zoom)\b', lower):
            return "camera"
        if re.search(r'\b(ram|storage|rom|memory|internal memory)\b', lower):
            return "ram_storage"
        if re.search(r'\b(processor|chipset|soc|cpu|gpu|snapdragon|dimensity|bionic|gaming|performance|speed|antutu)\b', lower):
            return "processor_performance"
        if re.search(r'\b(display|screen|amoled|oled|refresh rate|\bhz\b|inches|resolution)\b', lower):
            return "display"
        if re.search(r'\b(colors?|colours?|shades?)\b', lower):
            return "colors"
        if re.search(r'\b(vs|compare|difference between|which is better|which one)\b', lower):
            return "comparison"
        if re.search(r'\b(suggest|recommend|best phone|which phone should i buy|top phones?)\b', lower):
            return "recommendation"
        if re.search(r'\b(specs|specifications|features|details|tell me about)\b', lower):
            return "general_specs"
        if re.search(r'\b(available|in stock|stock|do you have|can i buy|got|sell)\b', lower):
            return "availability"
        return "general"

    def _extract_target_model(self, text: str, brand: Optional[str]) -> tuple[Optional[str], List[str], bool]:
        """Extracts specific model keywords, identifiers, and flags whether this is a specific model query."""
        # 1. Strip common inquiry fluff
        stripped = re.sub(
            r'\b(what\s+is\s+the\s+price\s+of|what\s+is\s+the\s+cost\s+of|price\s+of|cost\s+of|how\s+much\s+is|how\s+much\s+does|show\s+me|do\s+you\s+have|does|have\s+fast\s+charging|fast\s+charging|is\s+available|available|details\s+of|tell\s+me\s+about|buy|features\s+of|specs\s+of|information\s+on|phones?\s+do\s+you\s+have|list|give\s+me|find|recommend|suggest|what\s+about|which\s+is\s+better)\b',
            '',
            text,
            flags=re.IGNORECASE
        )

        # 2. Strip price conditions cleanly so budget amounts are not mistaken for model numbers
        stripped = re.sub(
            r'(?:under|below|less than|within|upto|above|more than|starting from|over|around|between|budget of)\s*(?:₹|rs\.?|inr)?\s*\d+(?:,\d+)?\s*(?:k|thousand)?(?:\s*(?:to|and|-)\s*(?:₹|rs\.?|inr)?\s*\d+(?:,\d+)?\s*(?:k|thousand)?)?',
            '',
            stripped,
            flags=re.IGNORECASE
        )
        stripped = re.sub(r'(?:₹|rs\.?|inr)\s*\d+(?:,\d+)?\s*(?:k|thousand)?', '', stripped, flags=re.IGNORECASE)

        # 3. Strip generic descriptors
        stripped = re.sub(r'\b(5g|4g|cheap|cheapest|budget|best|good|new|latest|flagship|affordable|mobiles?|smartphones?|phones?|laptops?|devices?)\b', '', stripped, flags=re.IGNORECASE)
        stripped = re.sub(r'[?!.,;:\-—]', ' ', stripped).strip()

        model_candidate = stripped
        if brand:
            # Remove brand name / variations
            model_candidate = re.sub(r'\b' + re.escape(brand) + r'\b', '', model_candidate, flags=re.IGNORECASE)
            if brand.lower() == "apple":
                model_candidate = re.sub(r'\biphone\b', '', model_candidate, flags=re.IGNORECASE)

        core_model = model_candidate.strip()

        # Check if contains a specific model number (e.g. 15, 18, 12, s24, s23, m14, 13c) or specific series (nord, edge, neo, ultra, pro, mini, etc.)
        has_number = bool(re.search(r'\b([a-zA-Z]?\d+[a-zA-Z]*)\b', core_model))
        has_series = bool(re.search(r'\b(nord|edge|ultra|pro|plus|lite|neo|fold|flip|max|victus|air|mini|open|omen|ideapad|tuf|vivobook|yoga|loq|aspire)\b', core_model, flags=re.IGNORECASE))
        
        is_specific = has_number or has_series

        if not is_specific or not core_model:
            return None, [], False

        # Build clean search tokens
        STOP_TOKENS = {
            "the", "a", "an", "and", "or", "in", "at", "for", "with", "have", "has", "is", "are",
            "of", "to", "yes", "no", "sure", "here", "there", "it", "its", "we", "you", "they",
            "our", "their", "currently", "stock", "features", "available", "hello", "hi", "sorry"
        }
        tokens = [t.lower() for t in core_model.split() if len(t) > 0 and t.lower() not in STOP_TOKENS]
        if not tokens:
            return None, [], False

        return core_model, tokens, True

    def _has_contextual_reference(self, text: str) -> bool:
        """Checks if text contains pronouns or attribute requests needing conversational context."""
        lower = text.lower()
        if re.search(r'\b(it|its|that|this|the phone|that one|this one|the same)\b', lower):
            return True
        # Attribute question without a brand or model name (e.g. "what is the price?", "fast charging?", "camera?")
        has_attr = bool(re.search(r'\b(price|cost|charging|battery|camera|specs|ram|storage|color|colours?)\b', lower))
        has_brand = any(re.search(r'\b' + re.escape(b.lower()) + r'\b', lower) for b in KNOWN_BRANDS)
        return has_attr and not has_brand

    def _resolve_context_from_history(self, history: List[Dict[str, str]]) -> tuple[Optional[str], Optional[str], List[str]]:
        """Extracts the most recent brand and product mentioned in previous conversation turns, prioritizing user queries."""
        # 1. First search user turns in reverse for cleanest model signal
        for turn in reversed(history):
            if turn.get("role") == "user":
                content = turn.get("content", "")
                brand = self._extract_brand(content)
                model, tokens, is_spec = self._extract_target_model(content, brand)
                if is_spec and tokens:
                    return brand, model, tokens
                if brand:
                    return brand, None, []

        # 2. Check assistant turns as fallback
        for turn in reversed(history):
            content = turn.get("content", "")
            brand = self._extract_brand(content)
            model, tokens, is_spec = self._extract_target_model(content, brand)
            if is_spec and tokens:
                return brand, model, tokens
            if brand:
                return brand, None, []
        return None, None, []
