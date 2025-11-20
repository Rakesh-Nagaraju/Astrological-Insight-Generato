"""
Zodiac sign calculation logic based on birth date.
"""
from datetime import date
from typing import Dict, Tuple


# Zodiac sign date ranges (simplified - using month/day)
ZODIAC_RANGES = [
    ("Capricorn", (12, 22), (1, 19)),
    ("Aquarius", (1, 20), (2, 18)),
    ("Pisces", (2, 19), (3, 20)),
    ("Aries", (3, 21), (4, 19)),
    ("Taurus", (4, 20), (5, 20)),
    ("Gemini", (5, 21), (6, 20)),
    ("Cancer", (6, 21), (7, 22)),
    ("Leo", (7, 23), (8, 22)),
    ("Virgo", (8, 23), (9, 22)),
    ("Libra", (9, 23), (10, 22)),
    ("Scorpio", (10, 23), (11, 21)),
    ("Sagittarius", (11, 22), (12, 21)),
]

# Zodiac traits for generating insights
ZODIAC_TRAITS: Dict[str, Dict[str, str]] = {
    "Aries": {
        "traits": "bold, energetic, and pioneering",
        "element": "Fire",
        "strengths": "leadership, courage, determination"
    },
    "Taurus": {
        "traits": "grounded, reliable, and sensual",
        "element": "Earth",
        "strengths": "patience, stability, practicality"
    },
    "Gemini": {
        "traits": "curious, adaptable, and communicative",
        "element": "Air",
        "strengths": "versatility, wit, social skills"
    },
    "Cancer": {
        "traits": "intuitive, nurturing, and emotional",
        "element": "Water",
        "strengths": "empathy, loyalty, imagination"
    },
    "Leo": {
        "traits": "confident, warm, and charismatic",
        "element": "Fire",
        "strengths": "leadership, creativity, generosity"
    },
    "Virgo": {
        "traits": "analytical, practical, and detail-oriented",
        "element": "Earth",
        "strengths": "precision, reliability, problem-solving"
    },
    "Libra": {
        "traits": "diplomatic, balanced, and harmonious",
        "element": "Air",
        "strengths": "fairness, charm, cooperation"
    },
    "Scorpio": {
        "traits": "intense, passionate, and transformative",
        "element": "Water",
        "strengths": "determination, resourcefulness, depth"
    },
    "Sagittarius": {
        "traits": "adventurous, optimistic, and philosophical",
        "element": "Fire",
        "strengths": "enthusiasm, honesty, open-mindedness"
    },
    "Capricorn": {
        "traits": "ambitious, disciplined, and responsible",
        "element": "Earth",
        "strengths": "perseverance, organization, wisdom"
    },
    "Aquarius": {
        "traits": "innovative, independent, and humanitarian",
        "element": "Air",
        "strengths": "originality, idealism, friendliness"
    },
    "Pisces": {
        "traits": "compassionate, intuitive, and artistic",
        "element": "Water",
        "strengths": "empathy, creativity, adaptability"
    }
}


def get_zodiac_sign(birth_date: str) -> str:
    """
    Calculate zodiac sign from birth date.
    
    Args:
        birth_date: Date string in YYYY-MM-DD format
        
    Returns:
        Zodiac sign name as string
    """
    try:
        birth = date.fromisoformat(birth_date)
        month = birth.month
        day = birth.day
    except ValueError:
        raise ValueError(f"Invalid date format: {birth_date}. Expected YYYY-MM-DD")
    
    # Check each zodiac range
    for sign, start, end in ZODIAC_RANGES:
        start_month, start_day = start
        end_month, end_day = end
        
        # Handle year boundary (Capricorn spans Dec 22 - Jan 19)
        if start_month == 12:
            if (month == 12 and day >= start_day) or (month == 1 and day <= end_day):
                return sign
        else:
            if (month == start_month and day >= start_day) or \
               (month == end_month and day <= end_day):
                return sign
    
    # Fallback (shouldn't reach here)
    return "Unknown"


def get_zodiac_info(zodiac_sign: str) -> Dict[str, str]:
    """
    Get zodiac sign information and traits.
    
    Args:
        zodiac_sign: Name of the zodiac sign
        
    Returns:
        Dictionary with zodiac traits and information
    """
    return ZODIAC_TRAITS.get(zodiac_sign, {
        "traits": "unique and special",
        "element": "Unknown",
        "strengths": "versatility and adaptability"
    })


def get_daily_prediction_base(zodiac_sign: str) -> str:
    """
    Get a base daily prediction template for the zodiac sign.
    This is a simplified rule-based approach.
    
    Args:
        zodiac_sign: Name of the zodiac sign
        
    Returns:
        Base prediction string
    """
    info = get_zodiac_info(zodiac_sign)
    traits = info["traits"]
    element = info["element"]
    
    # Simple rule-based predictions based on element
    predictions = {
        "Fire": "Your passionate energy will drive you forward today. Channel your enthusiasm into productive endeavors.",
        "Earth": "Your grounded nature will help you handle unexpected work pressure. Stay practical and focused.",
        "Air": "Your communication skills will be highlighted today. Share your ideas and connect with others.",
        "Water": "Your intuition will guide you through emotional situations. Trust your inner voice."
    }
    
    base_prediction = predictions.get(element, "Today brings opportunities for growth and self-discovery.")
    
    return f"Your {traits} nature suggests that {base_prediction}"

