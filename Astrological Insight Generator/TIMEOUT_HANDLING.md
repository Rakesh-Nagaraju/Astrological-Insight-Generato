# Timeout Handling

I added timeout handling because LLM APIs can be slow or hang sometimes. The system now has timeouts for all LLM calls and automatically falls back to the next provider if one times out.

## How it works

When a request times out, it just tries the next LLM in the chain:

1. Gemini (30s timeout) → 
2. HuggingFace (30s timeout) → 
3. OpenAI (30s timeout) → 
4. Mock LLM (always works, no timeout)

So even if all the real APIs are slow, you still get a response from the mock.

## Configuration

Timeouts are configurable per provider:

```bash
GEMINI_TIMEOUT=30
HUGGINGFACE_TIMEOUT=30
OPENAI_TIMEOUT=30
```

Default is 30 seconds, which seems reasonable for most APIs. You can adjust if needed - some providers might need more time, others less.

## What happens

**Example: Gemini times out**
- Request starts
- After 30s, timeout error
- Logs: "Google Gemini timeout after 30s"
- Automatically tries HuggingFace
- If that works, returns the insight
- If that also times out, tries OpenAI
- If everything fails, uses Mock LLM

**Worst case: All APIs timeout**
- Gemini → timeout
- HuggingFace → timeout  
- OpenAI → timeout
- Mock LLM → works (always)
- User still gets a response

The mock LLM is template-based, so it's instant and never fails. Not as good as real AI, but better than an error.

## Implementation details

**Gemini:**
- The SDK doesn't have built-in timeout, so I added manual timeout checking
- Tracks start time and raises TimeoutError if it exceeds the limit

**HuggingFace:**
- Uses `requests.post()` with `timeout` parameter
- Automatically raises `requests.exceptions.Timeout` which gets converted to `TimeoutError`

**OpenAI:**
- New API (v1.0+) has built-in timeout support
- Old API (v0.x) needs manual checking (I handle both)

All timeout errors are caught and logged, then the fallback chain continues.

## Logging

The system logs what's happening:
```
INFO: Attempting to use Google Gemini...
WARNING: Google Gemini timeout after 30s: ...
INFO: Attempting to use HuggingFace Inference API...
INFO: Successfully generated insight using HuggingFace (took 2.34s)
```

This helps debug issues and see which provider actually worked.

## Why this matters

- **Resilience**: System never completely fails
- **Performance**: Don't wait forever on slow APIs
- **User experience**: Always get a response, even if it's from mock
- **Cost**: Timeouts prevent hanging requests that might get charged

The 30-second default seems to work well in practice. Most LLM APIs respond faster than that, but if they're having issues, we don't want to wait forever.
