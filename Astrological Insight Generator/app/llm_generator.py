"""
LLM-based insight generation logic.
This module handles prompt generation and LLM calls for personalized insights.
Supports auto-selection of free LLMs: Google Gemini, HuggingFace, with fallback to mock.
"""
from typing import Dict, Optional, List
import os
import logging
import time
from app.zodiac import get_zodiac_info, get_daily_prediction_base
from app.config import Config

logger = logging.getLogger(__name__)


class LLMGenerator:
    """
    Handles LLM-based insight generation with auto-selection and fallback.
    Supports: Google Gemini (free), HuggingFace Inference API (free), OpenAI (paid), Mock (fallback)
    """
    
    def __init__(self, provider: str = "auto"):
        """
        Initialize LLM generator.
        
        Args:
            provider: LLM provider name ("auto", "gemini", "huggingface", "openai", "mock")
        """
        self.provider = provider
        self.auto_select = provider == "auto" or Config.AUTO_SELECT_LLM
        self.providers_attempted: List[str] = []
        
        # Initialize API keys
        self.gemini_key = Config.GEMINI_API_KEY
        self.huggingface_key = Config.HUGGINGFACE_API_KEY
        self.openai_key = Config.OPENAI_API_KEY
        
    def generate_insight(
        self,
        name: str,
        zodiac_sign: str,
        birth_place: Optional[str] = None,
        language: str = "en",
        use_vector_store: bool = False,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Generate personalized astrological insight using LLM with auto-selection.
        
        Args:
            name: Person's name
            zodiac_sign: Calculated zodiac sign
            birth_place: Birth place (optional)
            language: Output language (en/hi)
            use_vector_store: Whether to use vector store for context
            user_context: Optional user profile context for personalization
            
        Returns:
            Personalized insight string
        """
        # Get zodiac information
        zodiac_info = get_zodiac_info(zodiac_sign)
        base_prediction = get_daily_prediction_base(zodiac_sign)
        
        # Retrieve vector store context if enabled
        vector_context = None
        if use_vector_store:
            try:
                from app.vector_store import retrieve_astrological_context
                vector_context = retrieve_astrological_context(
                    zodiac_sign,
                    zodiac_info.get('traits', ''),
                    top_k=2
                )
                logger.info(f"Retrieved {len(vector_context)} contexts from vector store")
            except Exception as e:
                logger.warning(f"Vector store retrieval failed: {str(e)}")
        
        # Generate prompt with optional context
        prompt = self._build_prompt(
            name, zodiac_sign, zodiac_info, birth_place, base_prediction,
            vector_context=vector_context,
            user_context=user_context
        )
        
        # Auto-select LLM or use specified provider
        if self.auto_select:
            return self._try_llms_with_fallback(prompt, name, zodiac_sign, zodiac_info, base_prediction, language, vector_context, user_context)
        else:
            return self._call_specific_provider(prompt, name, zodiac_sign, zodiac_info, base_prediction, language, vector_context, user_context)
    
    def _try_llms_with_fallback(
        self,
        prompt: str,
        name: str,
        zodiac_sign: str,
        zodiac_info: Dict[str, str],
        base_prediction: str,
        language: str,
        vector_context: Optional[List[str]] = None,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Try multiple LLM providers in order of preference with automatic fallback.
        
        Priority order:
        1. Google Gemini (free, high quality)
        2. HuggingFace Inference API (free)
        3. OpenAI (if API key available)
        4. Mock LLM (always available as fallback)
        
        Args:
            prompt: Generated prompt
            name: Person's name
            zodiac_sign: Zodiac sign
            zodiac_info: Zodiac traits
            base_prediction: Base prediction
            language: Output language
            
        Returns:
            Generated insight
        """
        self.providers_attempted = []
        
        # Try Google Gemini first (free tier, good quality)
        if self.gemini_key:
            try:
                logger.info("Attempting to use Google Gemini...")
                start_time = time.time()
                insight = self._call_gemini(prompt, language)
                elapsed = time.time() - start_time
                logger.info(f"Successfully generated insight using Google Gemini (took {elapsed:.2f}s)")
                return insight
            except TimeoutError as e:
                logger.warning(f"Google Gemini timeout after {Config.GEMINI_TIMEOUT}s: {str(e)}")
                self.providers_attempted.append("gemini (timeout)")
            except Exception as e:
                logger.warning(f"Google Gemini failed: {str(e)}")
                self.providers_attempted.append("gemini")
        
        # Try HuggingFace Inference API (free tier)
        if self.huggingface_key:
            try:
                logger.info("Attempting to use HuggingFace Inference API...")
                start_time = time.time()
                insight = self._call_huggingface(prompt, language)
                elapsed = time.time() - start_time
                logger.info(f"Successfully generated insight using HuggingFace (took {elapsed:.2f}s)")
                return insight
            except TimeoutError as e:
                logger.warning(f"HuggingFace timeout after {Config.HUGGINGFACE_TIMEOUT}s: {str(e)}")
                self.providers_attempted.append("huggingface (timeout)")
            except Exception as e:
                logger.warning(f"HuggingFace failed: {str(e)}")
                self.providers_attempted.append("huggingface")
        
        # Try OpenAI if available (paid, but good quality)
        if self.openai_key:
            try:
                logger.info("Attempting to use OpenAI...")
                start_time = time.time()
                insight = self._call_openai(prompt, language)
                elapsed = time.time() - start_time
                logger.info(f"Successfully generated insight using OpenAI (took {elapsed:.2f}s)")
                return insight
            except TimeoutError as e:
                logger.warning(f"OpenAI timeout after {Config.OPENAI_TIMEOUT}s: {str(e)}")
                self.providers_attempted.append("openai (timeout)")
            except Exception as e:
                logger.warning(f"OpenAI failed: {str(e)}")
                self.providers_attempted.append("openai")
        
        # Fallback to mock LLM (always available)
        logger.info("Falling back to mock LLM (template-based)")
        self.providers_attempted.append("mock")
        return self._call_mock_llm(name, zodiac_sign, zodiac_info, base_prediction, language, user_context)
    
    def _call_specific_provider(
        self,
        prompt: str,
        name: str,
        zodiac_sign: str,
        zodiac_info: Dict[str, str],
        base_prediction: str,
        language: str,
        vector_context: Optional[List[str]] = None,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Call a specific LLM provider based on self.provider.
        
        Args:
            prompt: Generated prompt
            name: Person's name
            zodiac_sign: Zodiac sign
            zodiac_info: Zodiac traits
            base_prediction: Base prediction
            language: Output language
            
        Returns:
            Generated insight
        """
        if self.provider == "gemini":
            return self._call_gemini(prompt, language)
        elif self.provider == "huggingface":
            return self._call_huggingface(prompt, language)
        elif self.provider == "openai":
            return self._call_openai(prompt, language)
        else:
            return self._call_mock_llm(name, zodiac_sign, zodiac_info, base_prediction, language, user_context)
    
    def _build_prompt(
        self,
        name: str,
        zodiac_sign: str,
        zodiac_info: Dict[str, str],
        birth_place: Optional[str],
        base_prediction: str,
        vector_context: Optional[List[str]] = None,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Build prompt for LLM with optional vector store context and user profile.
        
        Args:
            name: Person's name
            zodiac_sign: Zodiac sign
            zodiac_info: Zodiac traits dictionary
            birth_place: Birth place
            base_prediction: Base prediction string
            vector_context: Optional context from vector store
            user_context: Optional user profile context
            
        Returns:
            Formatted prompt string
        """
        # Build base prompt
        prompt_parts = [
            f"Generate a personalized daily astrological insight for {name}.",
            "",
            f"Zodiac Sign: {zodiac_sign}",
            f"Traits: {zodiac_info.get('traits', '')}",
            f"Element: {zodiac_info.get('element', '')}",
            f"Strengths: {zodiac_info.get('strengths', '')}",
            f"Birth Place: {birth_place or 'Not specified'}",
            "",
            f"Base Prediction: {base_prediction}"
        ]
        
        # Add vector store context if available
        if vector_context:
            prompt_parts.append("")
            prompt_parts.append("Relevant Astrological Context:")
            for i, context in enumerate(vector_context, 1):
                prompt_parts.append(f"{i}. {context}")
        
        # Add user profile context if available
        if user_context:
            prompt_parts.append("")
            prompt_parts.append("User Preferences:")
            if user_context.get("preferred_style"):
                prompt_parts.append(f"Style: {user_context['preferred_style']}")
            if user_context.get("preferred_length"):
                prompt_parts.append(f"Length: {user_context['preferred_length']}")
            if user_context.get("common_keywords"):
                keywords = ", ".join(user_context["common_keywords"][:5])
                prompt_parts.append(f"Relevant keywords: {keywords}")
        
        # Add generation instructions
        prompt_parts.extend([
            "",
            f"Generate a natural, personalized insight (2-3 sentences) that:",
            f"1. Addresses {name} directly",
            f"2. Incorporates their zodiac traits naturally",
            f"3. Provides actionable, positive guidance",
            f"4. Sounds warm and authentic",
            "",
            "Insight:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _call_openai(self, prompt: str, language: str) -> str:
        """
        Call OpenAI API (requires API key - paid service).
        
        Args:
            prompt: Generated prompt
            language: Output language
            
        Returns:
            Generated insight
            
        Raises:
            TimeoutError: If the request times out
            Exception: For other API errors
        """
        try:
            import openai
            
            if not self.openai_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            start_time = time.time()
            
            # Support both old and new OpenAI API versions
            try:
                # New API (v1.0+)
                client = openai.OpenAI(api_key=self.openai_key, timeout=Config.OPENAI_TIMEOUT)
                response = client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert astrologer who provides warm, personalized daily insights."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                insight = response.choices[0].message.content.strip()
            except AttributeError:
                # Old API (v0.x) - doesn't support timeout parameter
                openai.api_key = self.openai_key
                response = openai.ChatCompletion.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert astrologer who provides warm, personalized daily insights."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                # Manual timeout check for old API
                elapsed = time.time() - start_time
                if elapsed > Config.OPENAI_TIMEOUT:
                    raise TimeoutError(f"OpenAI request took {elapsed:.2f}s, exceeded timeout of {Config.OPENAI_TIMEOUT}s")
                insight = response.choices[0].message.content.strip()
            except openai.APITimeoutError as e:
                raise TimeoutError(f"OpenAI API timeout: {str(e)}")
            except Exception as e:
                # Check if it's a timeout-related error
                elapsed = time.time() - start_time
                if elapsed >= Config.OPENAI_TIMEOUT:
                    raise TimeoutError(f"OpenAI request timed out after {elapsed:.2f}s")
                raise
            
            # Translate if needed
            if language == "hi":
                from app.utils import translate_to_hindi
                insight = translate_to_hindi(insight)
            
            return insight
            
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
        except TimeoutError:
            raise  # Re-raise timeout errors
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _call_gemini(self, prompt: str, language: str) -> str:
        """
        Call Google Gemini API (free tier available).
        
        Args:
            prompt: Generated prompt
            language: Output language
            
        Returns:
            Generated insight
            
        Raises:
            TimeoutError: If the request times out
            Exception: For other API errors
        """
        try:
            import google.generativeai as genai
            
            if not self.gemini_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel(Config.GEMINI_MODEL)
            
            # Create a more structured prompt for Gemini
            system_prompt = "You are an expert astrologer who provides warm, personalized daily insights. Keep responses to 2-3 sentences, be positive and actionable."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Use timeout wrapper for Gemini (since it doesn't have built-in timeout)
            start_time = time.time()
            try:
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=200,
                        temperature=0.7,
                    )
                )
                
                # Check if we exceeded timeout manually
                elapsed = time.time() - start_time
                if elapsed > Config.GEMINI_TIMEOUT:
                    raise TimeoutError(f"Gemini request took {elapsed:.2f}s, exceeded timeout of {Config.GEMINI_TIMEOUT}s")
                
            except Exception as e:
                # Check if it's a timeout-related error
                elapsed = time.time() - start_time
                if elapsed >= Config.GEMINI_TIMEOUT:
                    raise TimeoutError(f"Gemini request timed out after {elapsed:.2f}s")
                # Re-raise if it's not a timeout
                raise
            
            insight = response.text.strip()
            
            # Translate if needed
            if language == "hi":
                from app.utils import translate_to_hindi
                insight = translate_to_hindi(insight)
            
            return insight
            
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        except TimeoutError:
            raise  # Re-raise timeout errors
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _call_huggingface(self, prompt: str, language: str) -> str:
        """
        Call HuggingFace Inference API (free tier available).
        
        Args:
            prompt: Generated prompt
            language: Output language
            
        Returns:
            Generated insight
        """
        try:
            import requests
            
            if not self.huggingface_key:
                raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
            
            api_url = f"https://api-inference.huggingface.co/models/{Config.HUGGINGFACE_MODEL}"
            headers = {
                "Authorization": f"Bearer {self.huggingface_key}",
                "Content-Type": "application/json"
            }
            
            # Format prompt for instruction-following models
            formatted_prompt = f"""You are an expert astrologer. Generate a warm, personalized daily insight (2-3 sentences).

{prompt}"""
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=Config.HUGGINGFACE_TIMEOUT)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats from HuggingFace
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    insight = result[0]["generated_text"].strip()
                elif isinstance(result[0], dict) and "generated_text" in result[0]:
                    insight = result[0]["generated_text"].strip()
                else:
                    insight = str(result[0]).strip()
            elif isinstance(result, dict):
                if "generated_text" in result:
                    insight = result["generated_text"].strip()
                else:
                    # Try to extract text from any field
                    insight = str(result).strip()
            else:
                insight = str(result).strip()
            
            # Clean up the insight (remove prompt if it was included)
            if formatted_prompt in insight:
                insight = insight.replace(formatted_prompt, "").strip()
            
            # Translate if needed
            if language == "hi":
                from app.utils import translate_to_hindi
                insight = translate_to_hindi(insight)
            
            return insight
            
        except ImportError:
            raise ImportError("requests package not installed. Install with: pip install requests")
        except requests.exceptions.Timeout as e:
            logger.error(f"HuggingFace API timeout after {Config.HUGGINGFACE_TIMEOUT}s: {str(e)}")
            raise TimeoutError(f"HuggingFace request timed out after {Config.HUGGINGFACE_TIMEOUT}s")
        except requests.exceptions.RequestException as e:
            logger.error(f"HuggingFace API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"HuggingFace API error: {str(e)}")
            raise
    
    def _call_mock_llm(
        self,
        name: str,
        zodiac_sign: str,
        zodiac_info: Dict[str, str],
        base_prediction: str,
        language: str,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Mock LLM that generates personalized insights using templates.
        This is used when no real LLM is available.
        
        Args:
            name: Person's name
            zodiac_sign: Zodiac sign
            zodiac_info: Zodiac traits
            base_prediction: Base prediction
            language: Output language
            
        Returns:
            Generated insight
        """
        traits = zodiac_info.get('traits', 'unique and special')
        strengths = zodiac_info.get('strengths', 'versatility')
        
        # Personalized templates based on zodiac
        templates = {
            "Leo": f"Dear {name}, your innate leadership and warmth will shine today. Embrace spontaneity and avoid overthinking. Your natural charisma will help you connect with others.",
            "Aries": f"{name}, your bold and energetic spirit will drive you forward today. Take initiative on projects that matter to you. Your courage will inspire those around you.",
            "Taurus": f"{name}, your grounded nature will help you handle unexpected work pressure today. Stay practical and trust your instincts. Your reliability is your strength.",
            "Gemini": f"{name}, your curiosity and communication skills will be highlighted today. Share your ideas freely and connect with others. Your adaptability will serve you well.",
            "Cancer": f"{name}, your intuition will guide you through emotional situations today. Trust your inner voice and nurture your relationships. Your empathy creates deep connections.",
            "Virgo": f"{name}, your analytical mind will help you solve complex problems today. Focus on details but don't lose sight of the bigger picture. Your precision is valuable.",
            "Libra": f"{name}, your diplomatic nature will help you find balance today. Seek harmony in your relationships and decisions. Your charm will open doors.",
            "Scorpio": f"{name}, your intensity and passion will fuel your pursuits today. Channel your determination into meaningful goals. Your depth of feeling is a gift.",
            "Sagittarius": f"{name}, your adventurous spirit will lead you to new opportunities today. Stay optimistic and open to learning. Your enthusiasm is contagious.",
            "Capricorn": f"{name}, your ambition and discipline will help you achieve your goals today. Stay organized and focused. Your perseverance will pay off.",
            "Aquarius": f"{name}, your innovative thinking will bring fresh perspectives today. Embrace your independence and share your unique ideas. Your idealism inspires others.",
            "Pisces": f"{name}, your compassion and creativity will flow today. Trust your artistic instincts and help those in need. Your empathy makes a difference."
        }
        
        # Get template or use generic
        insight = templates.get(
            zodiac_sign,
            f"Dear {name}, your {traits} nature suggests that {base_prediction} Embrace your {strengths} and trust the journey ahead."
        )
        
        # Translate if needed
        if language == "hi":
            from app.utils import translate_to_hindi
            insight = translate_to_hindi(insight)
        
        return insight

