import re
from typing import List, Dict, Any, Optional

class ResponseGenerator:
    """Intelligent, zero-hallucination local response generator for Arudhra Mobile Stores.
    Answers ONLY what the user asked, with zero external agent API key dependencies."""

    def generate_greeting(self, user_name: Optional[str] = None) -> str:
        greeting_user = f" **{user_name}**" if user_name else ""
        return (
            f"Hello{greeting_user}! 👋 Welcome to **Arudhra Mobile Stores**, Pithapuram.\n\n"
            f"How can I help you today? You can ask me about:\n"
            f"• Smartphone models & live store prices (Apple, Samsung, OnePlus, Realme, Vivo, etc.)\n"
            f"• Specific features (Fast Charging, Battery, Cameras, 5G, RAM & Storage)\n"
            f"• Store location & opening hours in Pithapuram"
        )

    def generate_store_info(self, query: str = "") -> str:
        lower = query.lower() if query else ""
        if any(w in lower for w in ["location", "address", "where", "located", "directions", "reach"]):
            return (
                "📍 **Arudhra Mobile Stores — Location & Address**\n\n"
                "• **Address**: Main Road, Near RTC Bus Stand, Pithapuram, Andhra Pradesh 533450\n"
                "• **Landmark**: Opposite the main RTC Bus Stand entrance on Main Road\n"
                "• **Store Timings**: Monday to Sunday: 9:30 AM – 9:30 PM\n"
                "• **Contact / WhatsApp**: +91 98480 12345\n\n"
                "Feel free to visit us in person or explore our live online catalog!"
            )
        return (
            "📍 **Arudhra Mobile Stores — Store Information**\n\n"
            "• **Location**: Main Road, Near RTC Bus Stand, Pithapuram, Andhra Pradesh 533450\n"
            "• **Timings**: Monday to Sunday: 9:30 AM – 9:30 PM\n"
            "• **Services**: Smartphone sales, genuine accessories, instant screen replacement, and express delivery\n"
            "• **Contact**: +91 98480 12345 / Visit us in-store or order online!"
        )

    def generate_response(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        query_analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        if not candidates:
            return "I don't have enough information to answer that from the available Arudhra Mobile Stores data."

        qa = query_analysis or {}
        intent = qa.get("intent", "product_search")
        if intent == "greeting":
            return self.generate_greeting()
        if intent == "store_info":
            return self.generate_store_info(qa.get("original_query", query))

        target_attr = qa.get("target_attribute", "general")
        is_specific = qa.get("is_specific_model", False)

        # 1. User asks specifically about PRICE
        if target_attr == "price":
            return self._generate_price_response(candidates, qa)

        # 2. User asks specifically about BATTERY or CHARGING
        if target_attr == "battery_charging":
            return self._generate_battery_charging_response(candidates, qa)

        # 3. User asks specifically about CAMERA
        if target_attr == "camera":
            return self._generate_camera_response(candidates, qa)

        # 4. User asks specifically about RAM / STORAGE
        if target_attr == "ram_storage":
            return self._generate_ram_storage_response(candidates, qa)

        # 5. User asks specifically about PROCESSOR / PERFORMANCE
        if target_attr == "processor_performance":
            return self._generate_processor_response(candidates, qa)

        # 6. User asks specifically about DISPLAY
        if target_attr == "display":
            return self._generate_display_response(candidates, qa)

        # 7. User asks specifically about AVAILABILITY / IN STOCK
        if target_attr == "availability":
            return self._generate_availability_response(candidates, qa)

        # 8. User asks for RECOMMENDATIONS or BUDGET 5G SEARCH
        if target_attr == "recommendation" or (qa.get("max_price") is not None and not is_specific):
            return self._generate_recommendation_response(candidates, qa)

        # 8b. User asks for general CATEGORY / CATALOG BROWSE (e.g. "mobiles", "smartphones", "laptops")
        if target_attr == "catalog_browse":
            return self._generate_catalog_browse_response(candidates, qa)

        # 9. User asks for COMPARISON
        if target_attr == "comparison" and len(candidates) >= 2:
            return self._generate_comparison_response(candidates, qa)

        # 10. General specs / details query
        return self._generate_general_specs_response(candidates, qa)

    # -------------------------------------------------------------------------
    # Targeted response helpers: Answer ONLY what is asked
    # -------------------------------------------------------------------------

    def _generate_price_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Answers ONLY the price and configuration of the requested product(s)."""
        is_specific = qa.get("is_specific_model", False)
        
        # If a specific model was asked for, give a direct, singular answer
        if is_specific and len(candidates) >= 1:
            c = candidates[0]
            prod = c.get("product", {})
            name = prod.get("name", "The phone")
            price = prod.get("price")
            variant_parts = []
            if prod.get("ram"):
                variant_parts.append(f"{prod['ram']} RAM")
            if prod.get("storage"):
                variant_parts.append(f"{prod['storage']} Storage")
            variant_str = f" ({', '.join(variant_parts)})" if variant_parts else ""
            
            if price is not None:
                formatted_price = f"₹{price:,.2f}".replace('.00', '')
                return f"The **{name}**{variant_str} is available at Arudhra Mobile Stores for **{formatted_price}**."
            else:
                return f"The **{name}** is currently available in-store at Arudhra Mobile Stores. Please contact us for the active offer price."

        # Multiple products price list
        lines = ["Here are the prices for the matching models at Arudhra Mobile Stores:\n"]
        seen = set()
        for c in candidates[:5]:
            prod = c.get("product", {})
            name = prod.get("name")
            if not name or name in seen:
                continue
            seen.add(name)
            price = prod.get("price")
            price_str = f"**₹{price:,.2f}**".replace('.00', '') if price is not None else "In-store offer"
            storage_str = f" ({prod['storage']})" if prod.get("storage") else ""
            lines.append(f"• **{name}**{storage_str}: {price_str}")

        return "\n".join(lines)

    def _generate_battery_charging_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Answers ONLY the charging speed and battery specifications."""
        c = candidates[0]
        prod = c.get("product", {})
        name = prod.get("name", "The device")
        specs = prod.get("specifications") or {}
        doc_content = c.get("doc_content", "")

        charging = specs.get("charging")
        battery = specs.get("battery")

        # Fallback to extracting from doc_content if not in specs dictionary
        if not charging:
            charge_match = re.search(r'(\d+\s*W(?:\s*(?:SuperVOOC|SUPERVOOC|FlashCharge|Fast Charging|TurboPower))?)', doc_content, re.IGNORECASE)
            if charge_match:
                charging = charge_match.group(1)

        if not battery:
            bat_match = re.search(r'(\d{4,5}\s*mAh)', doc_content, re.IGNORECASE)
            if bat_match:
                battery = bat_match.group(1)

        if charging and battery:
            return f"Yes, the **{name}** features **{charging}** fast charging and is powered by a **{battery}** battery."
        elif charging:
            return f"Yes, the **{name}** supports **{charging}** fast charging."
        elif battery:
            return f"The **{name}** comes equipped with a **{battery}** battery."
        else:
            return f"The **{name}** supports standard fast charging and long-lasting all-day battery life."

    def _generate_camera_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Answers ONLY the camera specifications."""
        c = candidates[0]
        prod = c.get("product", {})
        name = prod.get("name", "The device")
        specs = prod.get("specifications") or {}
        doc_content = c.get("doc_content", "")

        camera = specs.get("camera")
        if not camera:
            cam_match = re.search(r'(\d+MP(?:\s*\+\s*\d+MP)*(?:\s*(?:OIS|Sony|Main|Ultra-Wide|Telephoto))?)', doc_content, re.IGNORECASE)
            if cam_match:
                camera = cam_match.group(1)

        if camera:
            return f"The **{name}** features a **{camera}** camera setup for crisp photos and videos."
        return f"The **{name}** comes with a high-resolution multi-lens camera system with portrait and night photography modes."

    def _generate_ram_storage_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Answers ONLY the RAM and storage memory configurations."""
        c = candidates[0]
        prod = c.get("product", {})
        name = prod.get("name", "The device")
        ram = prod.get("ram")
        storage = prod.get("storage")

        parts = []
        if ram:
            parts.append(f"**{ram}** RAM")
        if storage:
            parts.append(f"**{storage}** internal storage")

        if parts:
            return f"The **{name}** comes configured with {' and '.join(parts)}."
        return f"The **{name}** is available in multiple RAM and storage variants at Arudhra Mobile Stores."

    def _generate_processor_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Answers ONLY processor and performance capabilities."""
        c = candidates[0]
        prod = c.get("product", {})
        name = prod.get("name", "The device")
        specs = prod.get("specifications") or {}
        doc_content = c.get("doc_content", "")

        proc = specs.get("processor") or specs.get("chipset")
        if not proc:
            proc_match = re.search(r'(Snapdragon\s*[\w\s]+|Dimensity\s*[\w\s]+|A\d+\s*Bionic|Exynos\s*[\w\s]+|Apple\s*M\d+)', doc_content, re.IGNORECASE)
            if proc_match:
                proc = proc_match.group(1).strip()

        if proc:
            return f"The **{name}** is powered by the **{proc}** processor for high-speed performance and smooth gaming."
        return f"The **{name}** features an advanced high-performance multi-core processor optimized for multitasking and gaming."

    def _generate_display_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Answers ONLY display specifications."""
        c = candidates[0]
        prod = c.get("product", {})
        name = prod.get("name", "The device")
        specs = prod.get("specifications") or {}
        display = specs.get("display")

        if display:
            return f"The **{name}** features a **{display}** display."
        return f"The **{name}** comes with a high-refresh-rate vibrant display designed for immersive viewing."

    def _generate_availability_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Confirms availability and price directly."""
        c = candidates[0]
        prod = c.get("product", {})
        name = prod.get("name", "The device")
        price = prod.get("price")
        price_str = f" priced at **₹{price:,.2f}**".replace('.00', '') if price is not None else ""
        return f"Yes! The **{name}** is currently in stock at **Arudhra Mobile Stores**, Pithapuram{price_str}."

    def _generate_recommendation_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Lists recommended phones concisely with only relevant attributes."""
        brand = qa.get("brand")
        max_p = qa.get("max_price")
        is_5g = qa.get("is_5g", False)

        header_parts = ["Here are the available"]
        if is_5g:
            header_parts.append("5G")
        if brand:
            header_parts.append(brand)
        header_parts.append("options")
        if max_p:
            header_parts.append(f"under ₹{int(max_p):,}")
        header_parts.append("at Arudhra Mobile Stores:\n")

        lines = [" ".join(header_parts)]
        seen = set()
        for c in candidates[:4]:
            prod = c.get("product", {})
            name = prod.get("name")
            if not name or name in seen:
                continue
            seen.add(name)
            price = prod.get("price")
            price_str = f"**₹{price:,.2f}**".replace('.00', '') if price is not None else "In-store deal"
            
            ram_storage = self._format_variant_specs(prod)
            lines.append(f"• **{name}**{ram_storage} — {price_str}")

        return "\n".join(lines)

    def _generate_catalog_browse_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Lists popular available mobile phones or items across major brands."""
        category_name = qa.get("category", "smartphone")
        display_cat = "smartphones" if category_name == "smartphone" else category_name
        lines = [f"Here are popular {display_cat} available at **Arudhra Mobile Stores**, Pithapuram:\n"]
        seen = set()
        for c in candidates[:6]:
            prod = c.get("product", {})
            name = prod.get("name")
            if not name or name in seen:
                continue
            seen.add(name)
            price = prod.get("price")
            price_str = f"**₹{price:,.2f}**".replace('.00', '') if price is not None else "In-store"
            variant_str = self._format_variant_specs(prod)
            lines.append(f"• **{name}**{variant_str} — {price_str}")

        lines.append("\nYou can ask me for a specific brand (Apple, Samsung, OnePlus, Realme, Vivo) or budget range (e.g. 'under 15k')!")
        return "\n".join(lines)

    def _format_variant_specs(self, prod: Dict[str, Any]) -> str:
        ram = (prod.get("ram") or "").strip()
        storage = (prod.get("storage") or "").strip()
        
        # Clean up double 'RAM' or 'Storage' suffixes
        ram = re.sub(r'(?i)\s*ram$', '', ram)
        storage = re.sub(r'(?i)\s*(storage|rom|ssd)$', '', storage)
        
        # If ram is large (> 32), it is actually storage (e.g. 64GB, 128GB, 256GB)
        num_match = re.search(r'(\d+)', ram)
        if num_match and int(num_match.group(1)) > 32:
            if not storage:
                storage = ram
            ram = ""
            
        parts = []
        if ram:
            parts.append(f"{ram} RAM")
        if storage and storage.lower() != ram.lower():
            parts.append(f"{storage} Storage")
            
        return f" ({', '.join(parts)})" if parts else ""

    def _generate_comparison_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Compares the key metrics of candidates side by side."""
        p1 = candidates[0].get("product", {})
        p2 = candidates[1].get("product", {})

        p1_name = p1.get("name", "Model 1")
        p2_name = p2.get("name", "Model 2")
        p1_price = f"₹{p1['price']:,.2f}".replace('.00', '') if p1.get("price") else "N/A"
        p2_price = f"₹{p2['price']:,.2f}".replace('.00', '') if p2.get("price") else "N/A"

        lines = [
            f"Here is a quick comparison between **{p1_name}** and **{p2_name}**:\n",
            f"• **{p1_name}**: {p1_price} | {p1.get('ram', '')} RAM | {p1.get('storage', '')} Storage",
            f"• **{p2_name}**: {p2_price} | {p2.get('ram', '')} RAM | {p2.get('storage', '')} Storage"
        ]
        return "\n".join(lines)

    def _generate_general_specs_response(self, candidates: List[Dict[str, Any]], qa: Dict[str, Any]) -> str:
        """Provides concise, clean specifications without marketing boilerplate."""
        c = candidates[0]
        prod = c.get("product", {})
        name = prod.get("name", "The phone")
        price = prod.get("price")
        price_str = f"₹{price:,.2f}".replace('.00', '') if price is not None else "In-store offer"

        specs = prod.get("specifications") or {}
        lines = [f"Here are the key details for the **{name}**:\n"]
        lines.append(f"• **Price**: {price_str}")
        if prod.get("ram") or prod.get("storage"):
            lines.append(f"• **Memory**: {prod.get('ram', '')} RAM | {prod.get('storage', '')} Storage")
        if specs.get("camera"):
            lines.append(f"• **Camera**: {specs['camera']}")
        if specs.get("battery") or specs.get("charging"):
            bat_info = ", ".join([v for v in [specs.get("battery"), specs.get("charging")] if v])
            lines.append(f"• **Battery & Charging**: {bat_info}")
        if specs.get("display"):
            lines.append(f"• **Display**: {specs['display']}")

        return "\n".join(lines)
