# Tech Debt Tickets

This directory contains technical debt tickets identified in the codebase. Each ticket is a markdown file with detailed description, acceptance criteria, and suggested implementation.

## Scope Classification

Based on `assessment.md`, tickets are classified as:
- **In Scope**: Directly related to assessment requirements (error handling, testability, architecture, Swagger, basic validation)
- **Out of Scope**: Production-ready enhancements not required by assessment (auth, rate limiting, logging, caching, etc.)

---

## In-Scope Tickets (Assessment Requirements)

These tickets address requirements explicitly mentioned in `assessment.md`:

| Ticket | Title | Category | Requirement |
|--------|-------|----------|-------------|
| [001](001-add-exception-handling-openai-adapter.md) | Add Exception Handling to OpenAI Adapter | Error Handling | "Clear error handling and appropriate HTTP response statuses" |
| [002](002-add-exception-handling-service-layer.md) | Add Exception Handling to Service Layer | Error Handling | "Clear error handling and appropriate HTTP response statuses" |
| [003](003-add-exception-handling-api-routes.md) | Add Exception Handling to API Routes | Error Handling | "Clear error handling and appropriate HTTP response statuses" |
| [004](004-add-async-method-to-llm-port.md) | Add Async Method to LLm Port Interface | Architecture | "Adhere strictly to the interfaces defined in the provided ports file" |
| [005](005-fix-thread-safety-memory-repository.md) | Fix Thread Safety in Memory Repository | Concurrency | "Functional correctness of the API" |
| [010](010-add-input-validation-limits.md) | Add Input Validation Limits | Validation | "Perform basic input validation" |
| [011](011-add-error-scenario-tests.md) | Add Error Scenario Test Coverage | Testing | "Testability of the code" |
| [012](012-add-concurrent-access-tests.md) | Add Concurrent Access Tests | Testing | "Testability of the code" + optional async |
| [013](013-extract-duplicate-prompt-logic.md) | Extract Duplicate Prompt Logic | Code Quality | "Code readability, modularity" |
| [014](014-extract-shared-test-fixtures.md) | Extract Shared Test Fixtures | Code Quality | "Testability of the code" |
| [017](017-add-type-hints-openai-adapter.md) | Add Complete Type Hints | Code Quality | "Code readability" |
| [021](021-add-async-repository-interface.md) | Add Async Methods to Repository Interface | Architecture | "Adhere strictly to the interfaces" + optional async |
| [023](023-add-integration-tests.md) | Add Integration Tests | Testing | "Testability of the code" |
| [025](025-add-module-exports.md) | Add __all__ Exports to Modules | Code Quality | "Code readability, modularity" |
| [029](029-http-method-discrepancy-get-vs-post.md) | HTTP Method Discrepancy: GET vs POST | API Compliance | "accepts GET requests" vs current POST |

---

## Out-of-Scope Tickets (Production Enhancements)

These tickets address production-ready concerns **not required** by the assessment. Each ticket includes a disclaimer.

### Security (Not Required)
| Ticket | Title | Why Out of Scope |
|--------|-------|------------------|
| [006](006-add-rate-limiting.md) | Add Rate Limiting | Assessment doesn't require rate limiting |
| [007](007-add-authentication.md) | Add Authentication | Assessment doesn't require auth |
| [022](022-add-api-key-validation.md) | Add API Key Validation | Assessment assumes valid API key provided |
| [027](027-add-security-tests.md) | Add Security Tests | Beyond basic validation requirements |

### Reliability (Not Required)
| Ticket | Title | Why Out of Scope |
|--------|-------|------------------|
| [008](008-add-retry-logic-openai.md) | Add Retry Logic | Assessment uses provided adapter as-is |
| [015](015-add-request-timeout-configuration.md) | Add Request Timeout | Production reliability concern |
| [028](028-add-circuit-breaker.md) | Add Circuit Breaker | Production resilience pattern |

### Observability (Not Required)
| Ticket | Title | Why Out of Scope |
|--------|-------|------------------|
| [009](009-add-comprehensive-logging.md) | Add Comprehensive Logging | Assessment doesn't require logging |
| [020](020-add-health-check-details.md) | Enhance Health Check | Basic health check is sufficient |

### Performance (Not Required)
| Ticket | Title | Why Out of Scope |
|--------|-------|------------------|
| [016](016-limit-batch-concurrency.md) | Limit Batch Concurrency | Basic async is sufficient |
| [026](026-add-transcript-caching.md) | Add Transcript Caching | Optimization not required |

### Configuration (Not Required)
| Ticket | Title | Why Out of Scope |
|--------|-------|------------------|
| [018](018-add-dependency-version-bounds.md) | Add Dependency Version Bounds | Production dependency management |
| [019](019-make-prompts-configurable.md) | Make Prompts Configurable | Assessment says prompts are "hardcoded" |

### Documentation (Not Required)
| Ticket | Title | Why Out of Scope |
|--------|-------|------------------|
| [024](024-add-deployment-documentation.md) | Add Deployment Documentation | Production operations concern |

---

## Summary

| Classification | Count |
|----------------|-------|
| **In Scope** | 15 |
| **Out of Scope** | 14 |
| **Total** | 29 |

## Recommended Priority for Assessment

Focus on in-scope tickets in this order:

1. **API Compliance** (029) - Review GET vs POST discrepancy with assessment
2. **Error Handling** (001, 002, 003) - Required by success criteria
3. **Architecture** (004, 005, 021) - Port interface compliance and correctness
4. **Testing** (011, 012, 023) - Testability requirement
5. **Code Quality** (013, 014, 017, 025) - Readability and modularity
6. **Validation** (010) - Basic input validation

## Working with Tickets

When starting work on a ticket:
1. Move to `tickets/in-progress/` directory
2. Create a branch: `git checkout -b fix/001-exception-handling`
3. Reference ticket in commit messages

When completing a ticket:
1. Move to `tickets/completed/` directory
2. Add completion date to ticket
3. Create PR referencing the ticket
