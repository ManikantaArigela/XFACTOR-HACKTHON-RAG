import re
from datetime import datetime
from typing import Dict, Any, List, Tuple

class TextCleaner:
    """Cleaner for normalizing Instagram caption text and extracting hashtags."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        
        # Normalize newline characters
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Normalize price currency text (Rs., INR -> ₹)
        text = re.sub(r'\b(Rs\.?|INR)\s*', '₹', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces while keeping sentence flow
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    @staticmethod
    def extract_hashtags(caption: str) -> Tuple[List[str], str]:
        """Extract hashtags list and clean caption without trailing hashtags."""
        hashtags = re.findall(r'#(\w+)', caption)
        
        # Remove hashtags from main content for cleaner embedding document
        cleaned_caption = re.sub(r'#\w+', '', caption).strip()
        cleaned_caption = re.sub(r'[ \t]+', ' ', cleaned_caption)
        
        return hashtags, cleaned_caption

    def process_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """Process and clean raw instagram post dictionary."""
        cleaned_caption = self.clean_text(raw_post.get("caption", ""))
        hashtags, caption_body = self.extract_hashtags(cleaned_caption)
        
        processed_post = dict(raw_post)
        processed_post["caption"] = cleaned_caption
        processed_post["caption_body"] = caption_body
        processed_post["hashtags"] = hashtags
        
        posted_at_str = raw_post.get("posted_at")
        if isinstance(posted_at_str, str) and posted_at_str:
            try:
                processed_post["posted_at"] = datetime.fromisoformat(posted_at_str.replace("Z", "+00:00"))
            except Exception:
                processed_post["posted_at"] = datetime.utcnow()
        elif not isinstance(posted_at_str, datetime):
            processed_post["posted_at"] = datetime.utcnow()

        return processed_post
