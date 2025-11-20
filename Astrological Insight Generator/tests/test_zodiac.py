"""
Tests for zodiac sign calculation.
"""
import pytest
from app.zodiac import get_zodiac_sign, get_zodiac_info, get_daily_prediction_base


class TestZodiacCalculation:
    """Test zodiac sign calculation from birth dates."""
    
    def test_leo_sign(self):
        """Test Leo sign calculation."""
        assert get_zodiac_sign("1995-08-20") == "Leo"
        assert get_zodiac_sign("2000-08-10") == "Leo"
        assert get_zodiac_sign("1990-08-22") == "Leo"
    
    def test_aries_sign(self):
        """Test Aries sign calculation."""
        assert get_zodiac_sign("1995-04-15") == "Aries"
        assert get_zodiac_sign("2000-03-21") == "Aries"
        assert get_zodiac_sign("1990-04-19") == "Aries"
    
    def test_capricorn_sign(self):
        """Test Capricorn sign calculation (spans year boundary)."""
        assert get_zodiac_sign("2000-01-15") == "Capricorn"
        assert get_zodiac_sign("1995-12-25") == "Capricorn"
        assert get_zodiac_sign("2000-01-19") == "Capricorn"
    
    def test_all_zodiac_signs(self):
        """Test all zodiac signs."""
        test_cases = [
            ("2000-01-20", "Aquarius"),
            ("2000-02-19", "Pisces"),
            ("2000-03-21", "Aries"),
            ("2000-04-20", "Taurus"),
            ("2000-05-21", "Gemini"),
            ("2000-06-21", "Cancer"),
            ("2000-07-23", "Leo"),
            ("2000-08-23", "Virgo"),
            ("2000-09-23", "Libra"),
            ("2000-10-23", "Scorpio"),
            ("2000-11-22", "Sagittarius"),
            ("2000-12-22", "Capricorn"),
        ]
        
        for date_str, expected_sign in test_cases:
            assert get_zodiac_sign(date_str) == expected_sign, f"Failed for {date_str}"
    
    def test_invalid_date_format(self):
        """Test invalid date format handling."""
        with pytest.raises(ValueError):
            get_zodiac_sign("invalid-date")
        
        with pytest.raises(ValueError):
            get_zodiac_sign("1995/08/20")
        
        with pytest.raises(ValueError):
            get_zodiac_sign("08-20-1995")


class TestZodiacInfo:
    """Test zodiac information retrieval."""
    
    def test_get_zodiac_info(self):
        """Test getting zodiac information."""
        info = get_zodiac_info("Leo")
        assert "traits" in info
        assert "element" in info
        assert "strengths" in info
        assert info["element"] == "Fire"
    
    def test_unknown_zodiac(self):
        """Test handling of unknown zodiac sign."""
        info = get_zodiac_info("Unknown")
        assert "traits" in info
        assert info["element"] == "Unknown"
    
    def test_all_zodiac_info(self):
        """Test info for all zodiac signs."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        for sign in signs:
            info = get_zodiac_info(sign)
            assert "traits" in info
            assert "element" in info
            assert "strengths" in info


class TestDailyPrediction:
    """Test daily prediction generation."""
    
    def test_daily_prediction_base(self):
        """Test base daily prediction generation."""
        prediction = get_daily_prediction_base("Leo")
        assert isinstance(prediction, str)
        assert len(prediction) > 0
        # Prediction should contain some relevant keywords
        prediction_lower = prediction.lower()
        assert any(keyword in prediction_lower for keyword in ["leadership", "warmth", "fire", "energy", "today", "nature"])
    
    def test_all_signs_have_predictions(self):
        """Test that all signs have predictions."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        for sign in signs:
            prediction = get_daily_prediction_base(sign)
            assert isinstance(prediction, str)
            assert len(prediction) > 0

