from typing import List, Dict, Any, Optional
from config.settings import settings
from generation.prompt import SYSTEM_PROMPT_TEMPLATE
from generation.context_builder import ContextBuilder

class ResponseGenerator:
    """Configurable LLM response generator supporting Google Gemini, OpenAI, or direct context synthesis."""

    def __init__(self):
        self.context_builder = ContextBuilder()

    def generate_response(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        context_text = self.context_builder.build_context(candidates)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context_text=context_text)

        # Provider: Gemini
        if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                prompt_content = f"{system_prompt}\n\nUser Query: {query}"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_content,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[LLM ERROR] Gemini API call failed: {e}. Falling back to grounded template synthesis.")

        # Default Grounded Template Synthesizer (Zero-hallucination fallback)
        return self._synthesize_grounded_template(query, candidates)

    def _synthesize_grounded_template(self, query: str, candidates: List[Dict[str, Any]]) -> str:
        if not candidates:
            return "I don't have enough information to answer that from the available Arudhra store data."

        lines = ["Here are the details from Arudhra Mobile Stores, Pithapuram:\n"]
        seen_names = set()

        for c in candidates:
            prod = c.get("product", {})
            name = prod.get("name") or "Smartphone"
            if name in seen_names:
                continue
            seen_names.add(name)

            price_str = f"₹{prod['price']:,.2f}" if prod.get("price") else "Contact store for price"
            ram_str = f" | {prod['ram']} RAM" if prod.get("ram") else ""
            storage_str = f" | {prod['storage']} Storage" if prod.get("storage") else ""

            lines.append(f"• **{name}** ({prod.get('brand', '')}){ram_str}{storage_str}")
            lines.append(f"  Price: {price_str}")
            if c.get("source_url"):
                lines.append(f"  Instagram Post: {c['source_url']}")
            lines.append("")

        lines.append("Visit Arudhra Mobile Stores in Pithapuram or contact us for stock availability!")
        return "\n".join(lines)
