# Add __all__ Exports to Modules

**Severity:** Low
**Category:** Code Quality
**Affected Files:** `app/__init__.py`, `app/api/__init__.py`, `app/services/__init__.py`

## Description

Not all modules define `__all__` for explicit public API. This makes it unclear what should be imported from each module and can lead to unintended imports of internal components.

## Current Behavior

```python
# app/__init__.py
# Empty file

# app/api/__init__.py
# Empty file
```

## Expected Behavior

All package `__init__.py` files should define `__all__` to explicitly declare the public API.

## Acceptance Criteria

- [ ] Add `__all__` to `app/__init__.py`
- [ ] Add `__all__` to `app/api/__init__.py`
- [ ] Verify imports work correctly after changes
- [ ] Update any import statements if needed

## Suggested Implementation

```python
# app/__init__.py
from app.domain import TranscriptAnalysis, TranscriptAnalysisDTO
from app.services import TranscriptAnalysisService

__all__ = [
    "TranscriptAnalysis",
    "TranscriptAnalysisDTO",
    "TranscriptAnalysisService",
]

# app/api/__init__.py
from app.api.main import app
from app.api.routes import router

__all__ = ["app", "router"]

# app/services/__init__.py
from app.services.transcript_service import TranscriptAnalysisService

__all__ = ["TranscriptAnalysisService"]
```

## Benefits

1. Clear public API definition
2. Better IDE autocomplete
3. Prevents accidental import of internal modules
4. Documentation for module users
