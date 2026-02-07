# Add OpenAI API Key Validation

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses configuration robustness. The assessment.md assumes a valid OpenAI API key is provided - format validation is not required. This is a future enhancement for better developer experience.

**Severity:** Medium
**Category:** Security
**Affected Files:** `app/configurations.py`

## Description

The `OPENAI_API_KEY` configuration is required but has no format validation. Invalid keys will only fail at runtime when making API calls, providing poor developer experience and confusing error messages.

## Current Behavior

```python
class EnvConfigs(pydantic_settings.BaseSettings):
    OPENAI_API_KEY: str  # No validation
```

## Expected Behavior

- Validate API key format at startup
- Provide clear error message if key is invalid
- Optionally verify key works with a test API call

## Acceptance Criteria

- [ ] Add regex validation for API key format
- [ ] Provide helpful error message for invalid format
- [ ] Add optional startup validation (lightweight API call)
- [ ] Document expected key format

## Suggested Implementation

```python
import re
from pydantic import field_validator

class EnvConfigs(pydantic_settings.BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-2024-08-06"
    VALIDATE_API_KEY_ON_STARTUP: bool = False

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_api_key_format(cls, v: str) -> str:
        # OpenAI keys typically start with 'sk-' and are 51 characters
        # or start with 'sk-proj-' for project keys
        if not v:
            raise ValueError("OPENAI_API_KEY cannot be empty")

        if not (v.startswith("sk-") or v.startswith("sk-proj-")):
            raise ValueError(
                "OPENAI_API_KEY must start with 'sk-' or 'sk-proj-'. "
                "Get your key from https://platform.openai.com/api-keys"
            )

        if len(v) < 20:
            raise ValueError("OPENAI_API_KEY appears to be too short")

        return v
```

## Optional: Startup Validation

```python
# app/api/main.py
@app.on_event("startup")
async def validate_openai_connection():
    if settings.VALIDATE_API_KEY_ON_STARTUP:
        try:
            # Lightweight API call to verify key works
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            client.models.list()
            logger.info("OpenAI API key validated successfully")
        except openai.AuthenticationError:
            logger.error("Invalid OpenAI API key")
            raise SystemExit(1)
```
