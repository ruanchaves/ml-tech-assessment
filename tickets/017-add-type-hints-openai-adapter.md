# Add Complete Type Hints to OpenAI Adapter

**Severity:** Low
**Category:** Code Quality
**Affected Files:** `app/adapters/openai.py`

## Description

The OpenAI adapter has incomplete type hints. Constructor parameters and class attributes lack proper type annotations, reducing code clarity and IDE support.

## Current Behavior

```python
class OpenAIAdapter(ports.LLm):
    def __init__(self, api_key: str, model: str) -> None:
        self._model = model  # No type annotation
        self._client = openai.OpenAI(api_key=api_key)  # No type annotation
        self._aclient = openai.AsyncOpenAI(api_key=api_key)  # No type annotation
```

## Expected Behavior

All class attributes should have explicit type annotations.

## Acceptance Criteria

- [ ] Add type annotations for all class attributes
- [ ] Add return type hints where missing
- [ ] Verify type checking passes with mypy
- [ ] Update any related documentation

## Suggested Implementation

```python
import openai
import pydantic
from app import ports


class OpenAIAdapter(ports.LLm):
    """OpenAI LLM adapter implementation."""

    _model: str
    _client: openai.OpenAI
    _aclient: openai.AsyncOpenAI

    def __init__(self, api_key: str, model: str) -> None:
        """Initialize the OpenAI adapter.

        Args:
            api_key: OpenAI API key for authentication.
            model: Model identifier (e.g., 'gpt-4o-2024-08-06').
        """
        self._model = model
        self._client = openai.OpenAI(api_key=api_key)
        self._aclient = openai.AsyncOpenAI(api_key=api_key)
```

## Future Consideration

Add mypy to dev dependencies and CI pipeline:
```toml
[tool.poetry.group.dev.dependencies]
mypy = "^1.8.0"
```
