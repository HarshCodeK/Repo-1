# Architecture and decision record

## Pipeline

The service follows: HTTP or Streamlit -> validation -> rules -> local ML -> optional LLM -> unknown on failed escalation.

The important boundary is known, cheap evidence before uncertain, expensive evidence.

## Why rules first?

Explicit operational patterns can be detected deterministically. Calling a model for these cases adds latency and cost without adding useful information.

## Why character TF-IDF + logistic regression?

The corpus is small and the labels are operational categories rather than open-ended language understanding. Character n-grams work well with log-like tokens and modest wording variation while remaining cheap to train and serve. Logistic regression provides class probabilities, which makes abstention explicit. A transformer could improve semantic coverage later, but it would add model weight and runtime cost before the dataset justifies it.

## Why SQLite?

The project records local classification history for a single-process demonstration. SQLite requires no server and keeps the failure surface small. PostgreSQL becomes the better choice when multiple application instances, concurrent writers across hosts, backups, or operational database features become requirements.

## Why no vector database?

There is no semantic retrieval problem in this service. ChromaDB, FAISS, or pgvector would add infrastructure without supporting the core classification decision.

## Why no LangChain?

The routing policy is a small deterministic state machine. Direct Python keeps the control flow visible and reduces dependencies.

## Why an optional LLM?

The LLM is a last resort, not the default classifier. Rule and confident ML paths do not require a provider call. If the provider fails, the service returns unknown rather than manufacturing certainty.

## Security boundaries

- API input is length-bounded.
- LLM input is separately length-bounded.
- Provider output is schema-validated.
- Provider failures fail closed to unknown.
- Secrets are read from environment variables and never persisted by the classification store.
- The LLM prompt treats log content as data, not instructions.

This is application-level hardening, not a complete security boundary for arbitrary hostile logs or a production public service.
