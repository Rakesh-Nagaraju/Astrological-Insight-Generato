"""
User profile management system.
Tracks user preferences, past behavior, and history to influence output personalization.
"""
from typing import Dict, Optional, List
from datetime import datetime, date
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


# In-memory user profiles (can be replaced with database)
_user_profiles: Dict[str, Dict] = {}


class UserProfile:
    """
    User profile for personalization.
    Tracks preferences, history, and behavior patterns.
    """
    
    def __init__(self, user_id: str, name: str):
        """
        Initialize user profile.
        
        Args:
            user_id: Unique user identifier
            name: User's name
        """
        self.user_id = user_id
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        # Preferences
        self.preferred_language = "en"
        self.preferred_style = "warm"  # warm, formal, casual, spiritual
        self.preferred_length = "medium"  # short, medium, long
        
        # History
        self.request_count = 0
        self.last_request_date = None
        self.request_history: List[Dict] = []
        
        # Behavior patterns
        self.favorite_zodiac_themes: List[str] = []
        self.common_keywords: List[str] = []
        self.preferred_insight_types: List[str] = []  # daily, weekly, career, love, etc.
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "preferences": {
                "language": self.preferred_language,
                "style": self.preferred_style,
                "length": self.preferred_length
            },
            "history": {
                "request_count": self.request_count,
                "last_request_date": self.last_request_date,
                "request_history": self.request_history[-10:]  # Last 10 requests
            },
            "patterns": {
                "favorite_zodiac_themes": self.favorite_zodiac_themes,
                "common_keywords": self.common_keywords,
                "preferred_insight_types": self.preferred_insight_types
            }
        }
    
    def update_preferences(
        self,
        language: Optional[str] = None,
        style: Optional[str] = None,
        length: Optional[str] = None
    ):
        """
        Update user preferences.
        
        Args:
            language: Preferred language
            style: Preferred style
            length: Preferred length
        """
        if language:
            self.preferred_language = language
        if style:
            self.preferred_style = style
        if length:
            self.preferred_length = length
        self.updated_at = datetime.now().isoformat()
    
    def record_request(
        self,
        zodiac_sign: str,
        insight: str,
        language: str = "en"
    ):
        """
        Record a request in user history.
        
        Args:
            zodiac_sign: Zodiac sign requested
            insight: Generated insight
            language: Language used
        """
        self.request_count += 1
        self.last_request_date = datetime.now().isoformat()
        
        # Extract keywords from insight
        keywords = self._extract_keywords(insight)
        self.common_keywords.extend(keywords)
        
        # Track zodiac themes
        if zodiac_sign not in self.favorite_zodiac_themes:
            self.favorite_zodiac_themes.append(zodiac_sign)
        
        # Record request
        request_record = {
            "date": self.last_request_date,
            "zodiac_sign": zodiac_sign,
            "language": language,
            "insight_length": len(insight),
            "keywords": keywords[:5]  # Top 5 keywords
        }
        
        self.request_history.append(request_record)
        
        # Keep only last 50 requests
        if len(self.request_history) > 50:
            self.request_history = self.request_history[-50:]
        
        self.updated_at = datetime.now().isoformat()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text (simple implementation).
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (can be enhanced with NLP)
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "your", "you", "will", "today", "this", "that"}
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in common_words]
        return keywords[:10]  # Top 10 keywords
    
    def get_personalization_context(self) -> Dict[str, any]:
        """
        Get personalization context for generating insights.
        
        Returns:
            Dictionary with personalization context
        """
        return {
            "preferred_style": self.preferred_style,
            "preferred_length": self.preferred_length,
            "common_keywords": list(set(self.common_keywords[-20:])),  # Last 20 unique keywords
            "favorite_themes": self.favorite_zodiac_themes[-5:],  # Last 5 zodiac signs
            "request_frequency": "frequent" if self.request_count > 10 else "occasional"
        }


def get_user_id(name: str, birth_date: str) -> str:
    """
    Generate a user ID from name and birth date.
    
    Args:
        name: User's name
        birth_date: Birth date
        
    Returns:
        User ID (hash)
    """
    key = f"{name}:{birth_date}"
    return hashlib.md5(key.encode()).hexdigest()


def get_user_profile(user_id: str, name: str) -> UserProfile:
    """
    Get or create a user profile.
    
    Args:
        user_id: User identifier
        name: User's name
        
    Returns:
        UserProfile instance
    """
    if user_id not in _user_profiles:
        _user_profiles[user_id] = UserProfile(user_id, name)
        logger.info(f"Created new user profile for {name} ({user_id})")
    else:
        logger.debug(f"Retrieved existing user profile for {name} ({user_id})")
    
    return _user_profiles[user_id]


def update_user_profile(
    user_id: str,
    zodiac_sign: str,
    insight: str,
    language: str = "en"
):
    """
    Update user profile with new request.
    
    Args:
        user_id: User identifier
        zodiac_sign: Zodiac sign
        insight: Generated insight
        language: Language used
    """
    if user_id in _user_profiles:
        _user_profiles[user_id].record_request(zodiac_sign, insight, language)
        logger.debug(f"Updated user profile {user_id}")


def get_all_profiles() -> Dict[str, Dict]:
    """
    Get all user profiles (for debugging/admin).
    
    Returns:
        Dictionary of all profiles
    """
    return {uid: profile.to_dict() for uid, profile in _user_profiles.items()}


def clear_profiles():
    """Clear all user profiles (for testing)."""
    global _user_profiles
    _user_profiles = {}

