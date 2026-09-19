import json
import os
from typing import List, Dict, Any

class InstagramDataLoader:
    """Loader for raw Instagram posts JSON data."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Instagram data file not found at: {self.file_path}")
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Expected JSON root to be a list of post objects.")

        validated_posts = []
        for index, item in enumerate(data):
            if "instagram_post_id" not in item or "caption" not in item:
                print(f"[WARN] Skipping item at index {index}: Missing required fields ('instagram_post_id' or 'caption').")
                continue
            validated_posts.append(item)

        print(f"[INFO] Successfully loaded {len(validated_posts)} valid Instagram posts from {self.file_path}")
        return validated_posts
