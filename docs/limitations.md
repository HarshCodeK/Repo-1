# Limitations

- Training data is synthetic and small.
- Grouped validation reduces template leakage but does not establish production accuracy.
- Rule patterns and entity extraction cover only a narrow log vocabulary.
- SQLite is intended for local/single-process use.
- The LLM adapter depends on provider availability and credentials.
- Log text is untrusted input; the LLM prompt is not a complete prompt-injection defense.
- No authentication or rate limiting is included in the local API.
- Incident grouping is heuristic and is not a canonical incident-management system.
