"""
Tests for Pydantic models and data validation.
"""
import pytest
from pydantic import ValidationError
from app.models import BirthDetails, AstrologicalInsight


class TestBirthDetails:
    """Test BirthDetails model validation."""
    
    def test_valid_birth_details(self):
        """Test valid birth details."""
        details = BirthDetails(
            name="Ritika",
            birth_date="1995-08-20",
            birth_time="14:30",
            birth_place="Jaipur, India",
            language="en"
        )
        assert details.name == "Ritika"
        assert details.birth_date == "1995-08-20"
        assert details.language == "en"
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError):
            BirthDetails(
                name="Test",
                birth_date="1995/08/20",  # Wrong format
                birth_time="14:30",
                birth_place="Test",
                language="en"
            )
    
    def test_invalid_time_format(self):
        """Test invalid time format."""
        with pytest.raises(ValidationError):
            BirthDetails(
                name="Test",
                birth_date="1995-08-20",
                birth_time="2:30 PM",  # Wrong format
                birth_place="Test",
                language="en"
            )
    
    def test_invalid_language(self):
        """Test invalid language code."""
        with pytest.raises(ValidationError):
            BirthDetails(
                name="Test",
                birth_date="1995-08-20",
                birth_time="14:30",
                birth_place="Test",
                language="fr"  # Not supported
            )
    
    def test_empty_name(self):
        """Test empty name validation."""
        with pytest.raises(ValidationError):
            BirthDetails(
                name="",  # Empty name
                birth_date="1995-08-20",
                birth_time="14:30",
                birth_place="Test",
                language="en"
            )
    
    def test_default_language(self):
        """Test default language."""
        details = BirthDetails(
            name="Test",
            birth_date="1995-08-20",
            birth_time="14:30",
            birth_place="Test"
            # language not provided, should default to "en"
        )
        assert details.language == "en"
    
    def test_hindi_language(self):
        """Test Hindi language support."""
        details = BirthDetails(
            name="Test",
            birth_date="1995-08-20",
            birth_time="14:30",
            birth_place="Test",
            language="hi"
        )
        assert details.language == "hi"


class TestAstrologicalInsight:
    """Test AstrologicalInsight model."""
    
    def test_valid_insight(self):
        """Test valid insight model."""
        insight = AstrologicalInsight(
            zodiac="Leo",
            insight="Your insight here",
            language="en",
            name="Ritika"
        )
        assert insight.zodiac == "Leo"
        assert insight.insight == "Your insight here"
        assert insight.language == "en"
        assert insight.name == "Ritika"
    
    def test_insight_without_name(self):
        """Test insight without name (optional field)."""
        insight = AstrologicalInsight(
            zodiac="Leo",
            insight="Your insight here",
            language="en"
        )
        assert insight.name is None

