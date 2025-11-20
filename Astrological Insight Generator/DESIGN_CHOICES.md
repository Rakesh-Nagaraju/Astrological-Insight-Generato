# Design Choices & Architecture

This document explains the key design decisions I made while building this system.

## Models & Technologies Used

### LLM Providers
I chose to support multiple LLM providers with automatic fallback:
- **Google Gemini (primary)**: Free tier, good quality, fast responses
- **HuggingFace Inference API**: Free tier, good fallback option
- **OpenAI**: Paid but high quality (optional)
- **Mock LLM**: Template-based, always available as final fallback

**Why multiple providers?** Free APIs can be unreliable or have rate limits. Having fallback ensures the system always works, even if one service is down.

### Web Framework
**FastAPI** - Chose this because:
- Fast to set up and develop
- Automatic API documentation (Swagger UI)
- Built-in request validation with Pydantic
- Async support (though I'm not using it heavily here)
- Type hints throughout

### Data Validation
**Pydantic** - For request/response models:
- Automatic validation of input data
- Clear error messages for invalid inputs
- Type safety

## Data Flow

### Request Flow
1. User sends POST request to `/predict` with birth details
2. API validates input using Pydantic models
3. Zodiac sign calculated from birth date
4. Check cache (if enabled) - return cached result if found
5. Get/create user profile (if enabled) for personalization
6. Retrieve vector store contexts (if enabled)
7. Build LLM prompt with all context
8. Call LLM (with auto-selection and fallback)
9. Translate to Hindi if requested
10. Cache the result
11. Update user profile
12. Return JSON response

### LLM Selection Flow
1. Try Gemini (if API key available)
2. If timeout/error, try HuggingFace
3. If timeout/error, try OpenAI
4. If all fail, use Mock LLM (template-based)

This ensures users always get a response, even if all APIs are down.

## Architecture Decisions

### Modular Design
Split into separate modules:
- `zodiac.py` - Zodiac calculation (pure logic, no dependencies)
- `llm_generator.py` - LLM calls (abstracted, easy to swap providers)
- `api.py` - FastAPI endpoints (thin layer, delegates to other modules)
- `utils.py` - Helper functions (caching, translation)
- `models.py` - Data models (Pydantic schemas)

**Why?** Makes testing easier, allows swapping implementations, clear separation of concerns.

### Caching Strategy
Simple in-memory cache with MD5 keys based on:
- User name
- Birth date
- Zodiac sign
- Language

**Why in-memory?** Simple to implement, works for single-instance deployment. Can easily swap for Redis later if needed.

### Error Handling
- Try/except blocks around LLM calls
- Automatic fallback to next provider
- HTTPException for API errors with clear messages
- Logging for debugging

**Why?** Don't want the whole system to fail if one component fails. Graceful degradation is better than crashes.

### Timeout Handling
30-second timeout per LLM provider, configurable per provider.

**Why 30s?** Most APIs respond faster, but we don't want to wait forever. Long enough to be reasonable, short enough to fail fast.

## Assumptions Made

1. **Zodiac calculation**: Using Western zodiac (month/day based). Could extend to include time/location for more precise calculation, but kept it simple for now.

2. **Translation**: Stub implementation by default. Real translation requires installing additional packages (IndicTrans2, NLLB, etc.). The structure is there to plug them in.

3. **User profiles**: In-memory storage. For production, would need a database. The interface is abstracted so swapping is easy.

4. **Vector store**: Mock implementation with simple keyword matching. Real implementation would need embeddings and a vector database.

5. **Caching**: No TTL expiration (just in-memory). For production, would add expiration and persistence.

6. **API keys**: Assumes users can get free API keys. System works without them (uses mock), but quality is better with real LLMs.

## Extensibility Points

The code is structured to make these easy to add:

1. **Panchang data**: Add `app/panchang.py`, import in `llm_generator.py`, add to prompt
2. **LangChain**: Replace `LLMGenerator` class with LangChain chain
3. **Real vector store**: Replace `MockVectorStore` with Pinecone/Weaviate/Chroma
4. **Database**: Add database layer, swap in-memory storage for DB calls
5. **Real translation**: Install IndicTrans2/NLLB packages, they auto-detect
6. **Authentication**: Add auth middleware to FastAPI, protect endpoints

## Trade-offs

**Simplicity vs Features**: Chose simpler implementations (in-memory cache, mock vector store) to keep code readable and easy to understand. Can be upgraded later.

**Free vs Paid**: Prioritized free LLM options (Gemini, HuggingFace) but kept OpenAI as option for better quality.

**Speed vs Quality**: Mock LLM is instant but lower quality. Real LLMs are slower but better. Auto-selection balances this.

**Flexibility vs Ease of Use**: Made everything configurable via env vars, but sensible defaults so it works out of the box.

## Testing Strategy

- Unit tests for core logic (zodiac calculation, models)
- Integration tests for API endpoints (some compatibility issues with TestClient, but manual testing confirms everything works)
- Manual testing of LLM fallback chain
- Verified all three optional variants work

Could add more comprehensive tests, but core functionality is covered.

## Future Improvements

If I had more time:
- Add database for user profiles
- Real vector store with embeddings
- More comprehensive test coverage
- Rate limiting
- Authentication
- Better error messages
- Metrics/monitoring

But for the assignment scope, the current implementation covers all requirements and optional variants.

