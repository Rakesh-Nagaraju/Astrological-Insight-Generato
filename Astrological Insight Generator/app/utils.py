"""
Utility functions for translation, caching, and other helpers.
"""
from typing import Optional, Dict
from functools import lru_cache
import hashlib
import json


# Simple in-memory cache (can be replaced with Redis, etc.)
_insight_cache: Dict[str, str] = {}


def translate_to_hindi(text: str, method: str = "auto") -> str:
    """
    Translate English text to Hindi with automatic fallback.
    Uses the new translation module with IndicTrans2/NLLB support.
    
    Args:
        text: English text to translate
        method: Translation method ("auto", "indictrans2", "nllb", "google", "stub")
        
    Returns:
        Hindi translation
    """
    try:
        from app.translation import translate_to_hindi as translate_hindi
        return translate_hindi(text, method=method)
    except ImportError:
        # Fallback to simple stub if translation module not available
        return _translate_simple_stub(text)


def _translate_simple_stub(text: str) -> str:
    """
    Simple stub translation (fallback).
    
    Args:
        text: English text
        
    Returns:
        Hindi placeholder
    """
    hindi_placeholder = f"आज आपकी ज्योतिषीय अंतर्दृष्टि: {text[:50]}..."
    return hindi_placeholder


def get_cache_key(name: str, birth_date: str, zodiac_sign: str, language: str) -> str:
    """
    Generate a cache key for insights.
    
    Args:
        name: Person's name
        birth_date: Birth date
        zodiac_sign: Zodiac sign
        language: Language code
        
    Returns:
        Cache key string
    """
    key_string = f"{name}:{birth_date}:{zodiac_sign}:{language}"
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_insight(key: str, insight: str) -> None:
    """
    Cache an insight.
    
    Args:
        key: Cache key
        insight: Insight text to cache
    """
    _insight_cache[key] = insight


def get_cached_insight(key: str) -> Optional[str]:
    """
    Retrieve a cached insight.
    
    Args:
        key: Cache key
        
    Returns:
        Cached insight or None
    """
    return _insight_cache.get(key)


def clear_cache() -> None:
    """Clear the insight cache."""
    global _insight_cache
    _insight_cache = {}


@lru_cache(maxsize=128)
def get_personalization_score(name: str, zodiac_sign: str) -> float:
    """
    Calculate a personalization score based on user data.
    This is a simple scoring mechanism - can be extended with ML models.
    
    Args:
        name: Person's name
        zodiac_sign: Zodiac sign
        
    Returns:
        Personalization score (0.0 to 1.0)
    """
    # Simple scoring based on name length and zodiac
    base_score = 0.5
    name_factor = min(len(name) / 20.0, 0.3)  # Longer names = slightly higher score
    zodiac_factor = 0.2  # Fixed factor for zodiac
    
    score = base_score + name_factor + zodiac_factor
    return min(score, 1.0)

