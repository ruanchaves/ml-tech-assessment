# Add Async Method to LLm Port Interface

**Severity:** High
**Category:** Architecture
**Affected Files:** `app/ports/llm.py`

## Description

The abstract `LLm` base class only defines `run_completion()` but the OpenAI adapter implements `run_completion_async()`. This violates the port interface contract - the interface should be explicit about all required methods. Any new LLM adapter would need to guess that async support is required.

## Current Behavior

```python
class LLm(ABC):
    @abstractmethod
    def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        pass
    # Missing: run_completion_async
```

## Expected Behavior

The interface should define all methods that adapters must implement, including async variants.

## Acceptance Criteria

- [ ] Add abstract `run_completion_async()` method to `LLm` class
- [ ] Ensure method signature matches the sync version
- [ ] Update any type hints or documentation
- [ ] Verify OpenAI adapter implements the interface correctly
- [ ] Add tests that verify interface compliance

## Suggested Implementation

```python
class LLm(ABC):
    @abstractmethod
    def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        pass

    @abstractmethod
    async def run_completion_async(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        pass
```
