# Threat model

## Assets

- classification results
- local classification history
- provider credentials
- application availability

## Threats and controls

| Threat | Control | Remaining risk |
|---|---|---|
| oversized input | API and LLM length limits | limits are application-level |
| malformed model output | Pydantic validation | provider may still return semantically wrong data |
| provider outage | bounded HTTP timeout and fail-closed unknown | no automatic queue or retry |
| prompt injection in log text | log is explicitly treated as data in the prompt | not a complete isolation boundary |
| secret persistence | credentials come from environment and are not stored | host/process environment remains sensitive |
| arbitrary SQL | parameterized SQLite writes | local DB permissions still matter |
| public API abuse | no authentication or rate limiting | intended only for controlled use |

## Explicit non-claims

This project does not claim OS-level sandboxing, production-grade authentication, multi-tenant isolation, or prompt-injection immunity.
