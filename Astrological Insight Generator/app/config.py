"""
Configuration settings for the application.
"""
import os
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass


class Config:
    """Application configuration."""
    
    # API Settings
    API_TITLE: str = "Astrological Insight Generator"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "A service that generates personalized daily astrological insights"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")  # auto, gemini, huggingface, openai, mock
    AUTO_SELECT_LLM: bool = os.getenv("AUTO_SELECT_LLM", "True").lower() == "true"
    
    # Google Gemini (Free tier available)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # HuggingFace Inference API (Free tier available)
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
    
    # OpenAI (Optional - paid)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # LLM Timeout Settings (in seconds)
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))  # Default 30 seconds
    GEMINI_TIMEOUT: int = int(os.getenv("GEMINI_TIMEOUT", "30"))
    HUGGINGFACE_TIMEOUT: int = int(os.getenv("HUGGINGFACE_TIMEOUT", "30"))
    OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "30"))
    
    # Caching Settings
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Translation Settings
    ENABLE_TRANSLATION: bool = os.getenv("ENABLE_TRANSLATION", "True").lower() == "true"
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    TRANSLATION_METHOD: str = os.getenv("TRANSLATION_METHOD", "auto")  # auto, indictrans2, nllb, google, stub
    
    # Vector Store Settings
    ENABLE_VECTOR_STORE: bool = os.getenv("ENABLE_VECTOR_STORE", "False").lower() == "true"
    
    # User Profile Settings
    ENABLE_USER_PROFILES: bool = os.getenv("ENABLE_USER_PROFILES", "False").lower() == "true"

