"""
Tests for LLM generator functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.llm_generator import LLMGenerator


class TestLLMGenerator:
    """Test LLM generator."""
    
    def test_initialization(self):
        """Test LLM generator initialization."""
        generator = LLMGenerator(provider="auto")
        assert generator.provider == "auto"
        assert generator.auto_select is True
    
    def test_build_prompt(self):
        """Test prompt building."""
        generator = LLMGenerator()
        prompt = generator._build_prompt(
            name="Ritika",
            zodiac_sign="Leo",
            zodiac_info={"traits": "confident", "element": "Fire", "strengths": "leadership"},
            birth_place="Jaipur",
            base_prediction="Test prediction"
        )
        assert "Ritika" in prompt
        assert "Leo" in prompt
        assert "Jaipur" in prompt
    
    def test_mock_llm_generation(self):
        """Test mock LLM insight generation."""
        generator = LLMGenerator(provider="mock")
        insight = generator.generate_insight(
            name="Ritika",
            zodiac_sign="Leo",
            birth_place="Jaipur",
            language="en"
        )
        assert isinstance(insight, str)
        assert len(insight) > 0
        assert "Ritika" in insight or "Leo" in insight or "leadership" in insight.lower()
    
    def test_mock_llm_all_signs(self):
        """Test mock LLM for all zodiac signs."""
        generator = LLMGenerator(provider="mock")
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        for sign in signs:
            insight = generator.generate_insight(
                name="Test",
                zodiac_sign=sign,
                language="en"
            )
            assert isinstance(insight, str)
            assert len(insight) > 0
    
    @patch('app.llm_generator.Config.GEMINI_API_KEY', 'test-key')
    def test_gemini_call_with_mock(self):
        """Test Gemini API call with mocked response."""
        generator = LLMGenerator(provider="gemini")
        
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_response = MagicMock()
            mock_response.text = "Test insight from Gemini"
            mock_instance = MagicMock()
            mock_instance.generate_content.return_value = mock_response
            mock_model.return_value = mock_instance
            
            insight = generator._call_gemini("Test prompt", "en")
            assert insight == "Test insight from Gemini"
    
    @patch('app.llm_generator.Config.HUGGINGFACE_API_KEY', 'test-key')
    def test_huggingface_call_with_mock(self):
        """Test HuggingFace API call with mocked response."""
        generator = LLMGenerator(provider="huggingface")
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = [{"generated_text": "Test insight from HuggingFace"}]
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            insight = generator._call_huggingface("Test prompt", "en")
            assert "Test insight from HuggingFace" in insight
    
    def test_auto_selection_fallback(self):
        """Test auto-selection with fallback to mock."""
        generator = LLMGenerator(provider="auto")
        
        # Without API keys, should fall back to mock
        insight = generator.generate_insight(
            name="Test",
            zodiac_sign="Leo",
            language="en"
        )
        assert isinstance(insight, str)
        assert len(insight) > 0

