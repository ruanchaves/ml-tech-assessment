# Extract Duplicate Prompt Formatting Logic

**Severity:** Medium
**Category:** Code Quality
**Affected Files:** `app/services/transcript_service.py`

## Description

The same prompt formatting pattern `RAW_USER_PROMPT.format(transcript=transcript)` is repeated in both `analyze()` and `analyze_async()` methods. This duplication increases maintenance burden and risk of inconsistency.

## Current Behavior

```python
def analyze(self, transcript: str) -> TranscriptAnalysis:
    user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
    # ... rest of method

async def analyze_async(self, transcript: str) -> TranscriptAnalysis:
    user_prompt = RAW_USER_PROMPT.format(transcript=transcript)
    # ... rest of method (duplicated logic)
```

## Expected Behavior

Common logic should be extracted to reduce duplication.

## Acceptance Criteria

- [ ] Extract prompt formatting to helper method
- [ ] Extract analysis creation logic to helper method
- [ ] Reduce duplication between sync and async methods
- [ ] Maintain identical behavior
- [ ] Update tests if method signatures change

## Suggested Implementation

```python
class TranscriptAnalysisService:
    def _prepare_user_prompt(self, transcript: str) -> str:
        """Prepare user prompt with transcript content."""
        return RAW_USER_PROMPT.format(transcript=transcript)

    def _create_analysis(self, llm_response: TranscriptAnalysisDTO) -> TranscriptAnalysis:
        """Create and persist analysis from LLM response."""
        analysis = TranscriptAnalysis(
            id=str(uuid.uuid4()),
            summary=llm_response.summary,
            action_items=llm_response.action_items,
        )
        self._repository.save(analysis)
        return analysis

    def analyze(self, transcript: str) -> TranscriptAnalysis:
        user_prompt = self._prepare_user_prompt(transcript)
        llm_response = self._llm.run_completion(SYSTEM_PROMPT, user_prompt, TranscriptAnalysisDTO)
        return self._create_analysis(llm_response)

    async def analyze_async(self, transcript: str) -> TranscriptAnalysis:
        user_prompt = self._prepare_user_prompt(transcript)
        llm_response = await self._llm.run_completion_async(SYSTEM_PROMPT, user_prompt, TranscriptAnalysisDTO)
        return self._create_analysis(llm_response)
```
