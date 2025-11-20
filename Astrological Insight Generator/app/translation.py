"""
Translation module with support for IndicTrans2 and NLLB.
Provides Hindi translation with multiple backend options.
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def translate_to_hindi_indictrans2(text: str) -> Optional[str]:
    """
    Translate English text to Hindi using IndicTrans2.
    
    Args:
        text: English text to translate
        
    Returns:
        Hindi translation or None if translation fails
    """
    try:
        # Try to import IndicTrans2
        from indicTrans.inference.engine import Model
        import torch
        
        # Initialize model (lazy loading - cache the model)
        if not hasattr(translate_to_hindi_indictrans2, '_model'):
            logger.info("Loading IndicTrans2 model...")
            translate_to_hindi_indictrans2._model = Model(
                expdir="indicTrans2-en-indic",  # Model directory
                src="en",
                tgt="hi"
            )
            logger.info("IndicTrans2 model loaded")
        
        # Translate
        translated = translate_to_hindi_indictrans2._model.translate_paragraph(
            text,
            src="en",
            tgt="hi"
        )
        return translated
        
    except ImportError:
        logger.warning("IndicTrans2 not installed. Install with: pip install indic-trans")
        return None
    except Exception as e:
        logger.error(f"IndicTrans2 translation error: {str(e)}")
        return None


def translate_to_hindi_nllb(text: str) -> Optional[str]:
    """
    Translate English text to Hindi using NLLB (No Language Left Behind).
    
    Args:
        text: English text to translate
        
    Returns:
        Hindi translation or None if translation fails
    """
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        # Initialize model (lazy loading)
        if not hasattr(translate_to_hindi_nllb, '_tokenizer'):
            logger.info("Loading NLLB model...")
            model_name = "facebook/nllb-200-distilled-600M"
            translate_to_hindi_nllb._tokenizer = AutoTokenizer.from_pretrained(model_name)
            translate_to_hindi_nllb._model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            logger.info("NLLB model loaded")
        
        # Hindi language code for NLLB: "hin_Deva"
        tokenizer = translate_to_hindi_nllb._tokenizer
        model = translate_to_hindi_nllb._model
        
        # Tokenize and translate
        tokenizer.src_lang = "eng_Latn"
        inputs = tokenizer(text, return_tensors="pt")
        
        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id["hin_Deva"],
            max_length=512
        )
        
        translated = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return translated
        
    except ImportError:
        logger.warning("transformers not installed. Install with: pip install transformers torch")
        return None
    except Exception as e:
        logger.error(f"NLLB translation error: {str(e)}")
        return None


def translate_to_hindi_google(text: str) -> Optional[str]:
    """
    Translate English text to Hindi using Google Translate API (fallback).
    
    Args:
        text: English text to translate
        
    Returns:
        Hindi translation or None if translation fails
    """
    try:
        from googletrans import Translator
        
        translator = Translator()
        result = translator.translate(text, src='en', dest='hi')
        return result.text
        
    except ImportError:
        logger.warning("googletrans not installed. Install with: pip install googletrans==4.0.0rc1")
        return None
    except Exception as e:
        logger.error(f"Google Translate error: {str(e)}")
        return None


def translate_to_hindi(text: str, method: str = "auto") -> str:
    """
    Translate English text to Hindi with automatic fallback.
    
    Tries methods in order:
    1. IndicTrans2 (if available)
    2. NLLB (if available)
    3. Google Translate (if available)
    4. Stub translation (always available)
    
    Args:
        text: English text to translate
        method: Translation method ("auto", "indictrans2", "nllb", "google", "stub")
        
    Returns:
        Hindi translation
    """
    if method == "stub":
        return _translate_stub(text)
    
    if method == "indictrans2" or method == "auto":
        result = translate_to_hindi_indictrans2(text)
        if result:
            return result
    
    if method == "nllb" or method == "auto":
        result = translate_to_hindi_nllb(text)
        if result:
            return result
    
    if method == "google" or method == "auto":
        result = translate_to_hindi_google(text)
        if result:
            return result
    
    # Fallback to stub
    logger.info("Falling back to stub translation")
    return _translate_stub(text)


def _translate_stub(text: str) -> str:
    """
    Stub translation function (always available).
    
    Args:
        text: English text
        
    Returns:
        Hindi placeholder text
    """
    # Simple word mapping for common astrological terms
    translations = {
        "today": "आज",
        "your": "आपका",
        "will": "होगा",
        "help": "मदद",
        "leadership": "नेतृत्व",
        "warmth": "गर्मजोशी",
        "embrace": "अपनाएं",
        "spontaneity": "सहजता",
        "avoid": "बचें",
        "overthinking": "अधिक सोचना",
        "dear": "प्रिय",
        "innate": "सहज",
        "shine": "चमकें",
        "natural": "स्वाभाविक",
        "charisma": "आकर्षण"
    }
    
    # Return a Hindi placeholder with key terms translated
    hindi_placeholder = f"आज आपकी ज्योतिषीय अंतर्दृष्टि: {text[:100]}..."
    return hindi_placeholder

