# Make Prompts Configurable

> **⚠️ OUT OF SCOPE FOR ASSESSMENT**
> This ticket addresses extensibility concerns. The assessment.md explicitly states that prompts are "predefined, hardcoded" and provided - configurability is not required. This is a future enhancement for production flexibility.

**Severity:** Medium
**Category:** Architecture
**Affected Files:** `app/prompts.py`, `app/services/transcript_service.py`, `app/configurations.py`

## Description

Prompts are hardcoded in `app/prompts.py` and directly imported by the service. This tight coupling prevents customization per use case or domain without code changes.

## Current Behavior

```python
# app/prompts.py
SYSTEM_PROMPT = """You are an expert business coach..."""
RAW_USER_PROMPT = """Given the transcript below, generate:..."""

# app/services/transcript_service.py
from app.prompts import RAW_USER_PROMPT, SYSTEM_PROMPT

class TranscriptAnalysisService:
    def analyze(self, transcript: str):
        user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
        self._llm.run_completion(SYSTEM_PROMPT, user_prompt, ...)
```

## Expected Behavior

- Prompts should be injectable/configurable
- Different prompts for different domains should be possible
- Prompt changes shouldn't require code deployment

## Acceptance Criteria

- [ ] Create prompt configuration abstraction
- [ ] Inject prompts into service via dependency injection
- [ ] Allow prompts to be overridden via environment or config file
- [ ] Maintain backward compatibility with current defaults
- [ ] Document prompt customization

## Suggested Implementation

Option 1: Configuration-based prompts
```python
# app/configurations.py
class EnvConfigs(pydantic_settings.BaseSettings):
    SYSTEM_PROMPT: str = """You are an expert business coach..."""
    USER_PROMPT_TEMPLATE: str = """Given the transcript below, generate:..."""

# app/services/transcript_service.py
class TranscriptAnalysisService:
    def __init__(self, llm: LLm, repository: TranscriptRepository,
                 system_prompt: str, user_prompt_template: str):
        self._system_prompt = system_prompt
        self._user_prompt_template = user_prompt_template
```

Option 2: Prompt provider abstraction
```python
# app/ports/prompt_provider.py
class PromptProvider(ABC):
    @abstractmethod
    def get_system_prompt(self) -> str: ...

    @abstractmethod
    def get_user_prompt(self, transcript: str) -> str: ...

# app/adapters/default_prompts.py
class DefaultPromptProvider(PromptProvider):
    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def get_user_prompt(self, transcript: str) -> str:
        return RAW_USER_PROMPT.format(transcript=transcript)
```

## Future Considerations

- Store prompts in database for runtime updates
- A/B testing different prompts
- Prompt versioning
