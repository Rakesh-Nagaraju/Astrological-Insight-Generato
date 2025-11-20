# Optional Variants Implementation

I implemented all three optional variants from the requirements. Here's how they work and how to use them.

## 1. Hindi Translation (IndicTrans2/NLLB)

I added a translation module that supports multiple backends. The idea was to make it easy to plug in real translation models later.

**Location:** `app/translation.py`

**How it works:**
- Tries IndicTrans2 first (if installed)
- Falls back to NLLB (if installed)  
- Falls back to Google Translate (if installed)
- Finally falls back to stub translation (always works)

The stub translation is pretty basic - just returns a placeholder. But the structure is there so you can drop in real models and it'll work.

**To use real translation:**
```bash
# For IndicTrans2
pip install indic-trans

# For NLLB  
pip install transformers torch

# For Google Translate
pip install googletrans==4.0.0rc1
```

Then set in `.env`:
```bash
TRANSLATION_METHOD=auto  # or indictrans2, nllb, google, stub
```

The API automatically uses this when `language="hi"` in the request. No code changes needed.

## 2. Vector Store Retrieval

I built a mock vector store with a small corpus of astrological texts. Each zodiac sign has an entry with relevant themes.

**Location:** `app/vector_store.py`

**The corpus:**
- 12 entries, one per zodiac sign
- Each has text, theme, and keywords
- Covers things like leadership (Leo), stability (Taurus), etc.

**How it works:**
- When generating an insight, it searches the corpus
- Matches based on zodiac sign and keywords
- Returns top-k relevant contexts
- These get added to the LLM prompt

The similarity calculation is pretty simple (keyword overlap + zodiac matching). For production, you'd want real embeddings and a proper vector DB.

**To enable:**
```bash
ENABLE_VECTOR_STORE=True
```

**Extending it:**
The `MockVectorStore` class can be replaced with real implementations:
- Use sentence-transformers for embeddings
- Store in Pinecone, Weaviate, or Chroma
- The `retrieve_astrological_context()` interface stays the same

## 3. User Profiles

I added a user profile system that tracks preferences and request history.

**Location:** `app/user_profiles.py`

**What it tracks:**
- Preferences: language, style (warm/formal/casual), length
- History: request count, last request date, request history
- Patterns: favorite zodiac themes, common keywords, preferred insight types

**How it works:**
- Creates a profile based on name + birth_date (hashed to user_id)
- Tracks every request
- Extracts keywords from insights
- Builds personalization context from profile
- Uses this context in LLM prompts

The profiles are in-memory right now. For production, you'd want to store them in a database.

**To enable:**
```bash
ENABLE_USER_PROFILES=True
```

**What happens:**
1. First request creates a profile
2. Each request updates the profile
3. Profile context is included in prompts
4. Insights get more personalized over time

The keyword extraction is pretty basic (just common words filtering). Could be improved with proper NLP, but it works for now.

## Integration

All three features integrate automatically when enabled:

1. **Translation**: Used automatically when `language="hi"` in API request
2. **Vector Store**: Retrieves contexts and adds to prompt when `ENABLE_VECTOR_STORE=True`
3. **User Profiles**: Tracks requests and uses profile context in prompts when `ENABLE_USER_PROFILES=True`

No code changes needed - just set the env vars and they work.

## Testing

You can test each one:

```python
# Translation
from app.translation import translate_to_hindi
hindi = translate_to_hindi("Your leadership will shine", method="stub")

# Vector store
from app.vector_store import retrieve_astrological_context
contexts = retrieve_astrological_context("Leo", "confident, warm", top_k=2)

# User profiles
from app.user_profiles import get_user_profile, get_user_id
user_id = get_user_id("Test", "2000-01-01")
profile = get_user_profile(user_id, "Test")
profile.record_request("Leo", "Your insight", "en")
context = profile.get_personalization_context()
```

## Notes

- All three are optional and disabled by default
- They all have fallbacks so the system still works if they fail
- The implementations are basic but functional
- Easy to extend with real backends (vector DB, translation models, user DB)

I kept them simple because the assignment said "stub" or "basic" - but the structure is there to make them production-ready later.
