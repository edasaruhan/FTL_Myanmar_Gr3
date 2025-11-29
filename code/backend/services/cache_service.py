import hashlib
from typing import Optional, Dict, Any

# In-memory cache: key -> (result, timestamp)
_cache: Dict[str, Any] = {}

def get_cache_key(text: str, operation: str) -> str:
    """Generate SHA256 cache key from text and operation type."""
    content = f"{operation}:{text}"
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def get_cached_result(text: str, operation: str) -> Optional[Any]:
    """Retrieve cached result if exists."""
    key = get_cache_key(text, operation)
    return _cache.get(key)

def set_cached_result(text: str, operation: str, result: Any) -> None:
    """Store result in cache."""
    key = get_cache_key(text, operation)
    _cache[key] = result

def clear_cache() -> None:
    """Clear all cached results."""
    _cache.clear()
