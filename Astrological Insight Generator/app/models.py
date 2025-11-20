"""
Data models and schemas for the Astrological Insight Generator.
"""
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field, validator


class BirthDetails(BaseModel):
    """Input model for birth details."""
    name: str = Field(..., description="Name of the person", min_length=1)
    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    birth_time: str = Field(..., description="Birth time in HH:MM format (24-hour)")
    birth_place: str = Field(..., description="Birth place (city, country)")
    language: Optional[str] = Field("en", description="Preferred output language (en/hi)")

    @validator('birth_date')
    def validate_date(cls, v):
        """Validate date format."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError('birth_date must be in YYYY-MM-DD format')
        return v

    @validator('birth_time')
    def validate_time(cls, v):
        """Validate time format."""
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError('birth_time must be in HH:MM format (24-hour)')
        return v

    @validator('language')
    def validate_language(cls, v):
        """Validate language code."""
        if v not in ['en', 'hi']:
            raise ValueError('language must be either "en" or "hi"')
        return v


class AstrologicalInsight(BaseModel):
    """Output model for astrological insight."""
    zodiac: str = Field(..., description="Zodiac sign")
    insight: str = Field(..., description="Personalized daily astrological insight")
    language: str = Field(..., description="Output language")
    name: Optional[str] = Field(None, description="Name of the person")


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str
    version: str

