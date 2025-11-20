"""
Tests for utility functions.
"""
import pytest
from app.utils import (
    translate_to_hindi,
    get_cache_key,
    cache_insight,
    get_cached_insight,
    clear_cache,
    get_personalization_score
)


class TestTranslation:
    """Test translation utilities."""
    
    def test_translate_to_hindi(self):
        """Test Hindi translation stub."""
        english_text = "Today is a good day"
        hindi_text = translate_to_hindi(english_text)
        assert isinstance(hindi_text, str)
        assert len(hindi_text) > 0


class TestCaching:
    """Test caching utilities."""
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = get_cache_key("Ritika", "1995-08-20", "Leo", "en")
        key2 = get_cache_key("Ritika", "1995-08-20", "Leo", "en")
        key3 = get_cache_key("Ritika", "1995-08-20", "Leo", "hi")
        
        assert key1 == key2  # Same inputs should generate same key
        assert key1 != key3  # Different language should generate different key
    
    def test_cache_operations(self):
        """Test cache store and retrieve."""
        clear_cache()
        
        key = get_cache_key("Test", "2000-01-01", "Aries", "en")
        insight = "Test insight"
        
        # Cache should be empty initially
        assert get_cached_insight(key) is None
        
        # Store in cache
        cache_insight(key, insight)
        
        # Retrieve from cache
        cached = get_cached_insight(key)
        assert cached == insight
    
    def test_cache_clear(self):
        """Test cache clearing."""
        key = get_cache_key("Test", "2000-01-01", "Aries", "en")
        cache_insight(key, "Test insight")
        
        assert get_cached_insight(key) is not None
        
        clear_cache()
        
        assert get_cached_insight(key) is None


class TestPersonalization:
    """Test personalization scoring."""
    
    def test_personalization_score(self):
        """Test personalization score calculation."""
        score = get_personalization_score("Ritika", "Leo")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_personalization_score_consistency(self):
        """Test that same inputs give same score."""
        score1 = get_personalization_score("Ritika", "Leo")
        score2 = get_personalization_score("Ritika", "Leo")
        assert score1 == score2
    
    def test_personalization_score_different_inputs(self):
        """Test that different inputs may give different scores."""
        score1 = get_personalization_score("Ritika", "Leo")
        score2 = get_personalization_score("John", "Aries")
        # Scores might be different (not guaranteed, but likely)
        assert isinstance(score1, float)
        assert isinstance(score2, float)

