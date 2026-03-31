import re

def compact_text(value: str) -> str:
    """Normalize and compact text for comparison, stripping out special characters."""
    v = str(value or "").lower()
    v = re.sub(r"[^a-z0-9\s]", " ", v)
    v = re.sub(r"\s+", " ", v).strip()
    return v.replace(" ", "")

def get_doc_mode_cache_key(user_id: int) -> str:
    return f"doc_mode_active_{user_id}"

