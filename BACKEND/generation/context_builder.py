from typing import List, Dict, Any

class ContextBuilder:
    """Formats retrieved candidates into a structured context block for the LLM prompt."""

    def build_context(self, candidates: List[Dict[str, Any]]) -> str:
        if not candidates:
            return "No relevant store information found."

        context_blocks = []
        for idx, candidate in enumerate(candidates, 1):
            product = candidate.get("product", {})
            doc_content = candidate.get("doc_content", "")
            source_url = candidate.get("source_url")

            block_lines = [f"[Document #{idx}]"]
            if product.get("name"):
                block_lines.append(f"Product: {product.get('name')}")
            if product.get("brand"):
                block_lines.append(f"Brand: {product.get('brand')}")
            if product.get("price"):
                block_lines.append(f"Price: ₹{product.get('price'):,.2f}")
            if product.get("ram"):
                block_lines.append(f"RAM: {product.get('ram')}")
            if product.get("storage"):
                block_lines.append(f"Storage: {product.get('storage')}")
            if source_url:
                block_lines.append(f"Source URL: {source_url}")
            
            block_lines.append("Details:")
            block_lines.append(doc_content)
            
            context_blocks.append("\n".join(block_lines))

        return "\n\n--------------------------------------------------\n\n".join(context_blocks)
