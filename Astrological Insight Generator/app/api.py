"""
FastAPI application for Astrological Insight Generator.
REST API that takes birth details and returns personalized astrological insights.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.models import BirthDetails, AstrologicalInsight, HealthCheck
from app.zodiac import get_zodiac_sign
from app.llm_generator import LLMGenerator
from app.utils import (
    get_cache_key,
    cache_insight,
    get_cached_insight,
    get_personalization_score
)
from app.config import Config
from app.user_profiles import (
    get_user_id,
    get_user_profile,
    update_user_profile
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    version=Config.API_VERSION,
    description=Config.API_DESCRIPTION
)

# Initialize LLM generator with auto-selection
llm_generator = LLMGenerator(provider=Config.LLM_PROVIDER)


@app.get("/", response_model=HealthCheck)
async def root():
    """
    Root endpoint - health check.
    """
    return HealthCheck(status="healthy", version=Config.API_VERSION)


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint.
    """
    return HealthCheck(status="healthy", version=Config.API_VERSION)


@app.post("/predict", response_model=AstrologicalInsight)
async def predict_insight(birth_details: BirthDetails):
    """
    Generate personalized daily astrological insight based on birth details.
    
    Args:
        birth_details: Birth details including name, date, time, place, and language
        
    Returns:
        Astrological insight with zodiac sign and personalized message
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        logger.info(f"Processing request for {birth_details.name}")
        
        # Calculate zodiac sign
        zodiac_sign = get_zodiac_sign(birth_details.birth_date)
        logger.info(f"Calculated zodiac sign: {zodiac_sign} for {birth_details.name}")
        
        # Check cache if enabled
        cache_key = None
        cached_insight = None
        if Config.ENABLE_CACHE:
            cache_key = get_cache_key(
                birth_details.name,
                birth_details.birth_date,
                zodiac_sign,
                birth_details.language or "en"
            )
            cached_insight = get_cached_insight(cache_key)
        
        if cached_insight:
            logger.info(f"Returning cached insight for {birth_details.name}")
            return AstrologicalInsight(
                zodiac=zodiac_sign,
                insight=cached_insight,
                language=birth_details.language or "en",
                name=birth_details.name
            )
        
        # Get or create user profile for personalization
        user_id = get_user_id(birth_details.name, birth_details.birth_date)
        user_profile = get_user_profile(user_id, birth_details.name)
        user_context = user_profile.get_personalization_context() if Config.ENABLE_USER_PROFILES else None
        
        # Generate personalized insight using LLM with optional features
        insight = llm_generator.generate_insight(
            name=birth_details.name,
            zodiac_sign=zodiac_sign,
            birth_place=birth_details.birth_place,
            language=birth_details.language or "en",
            use_vector_store=Config.ENABLE_VECTOR_STORE,
            user_context=user_context
        )
        
        # Update user profile with this request
        if Config.ENABLE_USER_PROFILES:
            update_user_profile(
                user_id,
                zodiac_sign,
                insight,
                birth_details.language or "en"
            )
        
        # Cache the insight if caching is enabled
        if Config.ENABLE_CACHE and cache_key:
            cache_insight(cache_key, insight)
        
        # Calculate personalization score (bonus feature)
        personalization_score = get_personalization_score(
            birth_details.name,
            zodiac_sign
        )
        logger.info(f"Personalization score: {personalization_score:.2f} for {birth_details.name}")
        
        return AstrologicalInsight(
            zodiac=zodiac_sign,
            insight=insight,
            language=birth_details.language or "en",
            name=birth_details.name
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/zodiac/{birth_date}")
async def get_zodiac(birth_date: str):
    """
    Get zodiac sign for a given birth date.
    
    Args:
        birth_date: Birth date in YYYY-MM-DD format
        
    Returns:
        JSON with zodiac sign
    """
    try:
        zodiac_sign = get_zodiac_sign(birth_date)
        return {
            "birth_date": birth_date,
            "zodiac": zodiac_sign
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/insight", response_model=AstrologicalInsight)
async def get_insight_cli(
    name: str = Query(..., description="Name of the person"),
    birth_date: str = Query(..., description="Birth date in YYYY-MM-DD format"),
    birth_time: str = Query(..., description="Birth time in HH:MM format"),
    birth_place: str = Query(..., description="Birth place"),
    language: Optional[str] = Query("en", description="Output language (en/hi)")
):
    """
    CLI-friendly endpoint for getting insights via GET request.
    Useful for testing with curl.
    
    Example:
        curl "http://localhost:8000/insight?name=Ritika&birth_date=1995-08-20&birth_time=14:30&birth_place=Jaipur,India&language=en"
    """
    birth_details = BirthDetails(
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        language=language
    )
    return await predict_insight(birth_details)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)

