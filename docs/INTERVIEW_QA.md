# Interview Q&A

Answers describe the current repository, not an idealized future system.

## Product

1. What problem does this solve?
It classifies operational logs while avoiding unnecessary model calls.

2. Why is this more useful than a single classifier?
Explicit patterns are cheap and reliable, common semantic patterns can use a local model, and ambiguous cases can use a more capable but slower provider.

3. Who would use it?
A small engineering or SRE workflow that needs first-pass categorization before alerting, triage, or incident aggregation.

4. What would make you kill the idea?
If incoming logs are already structured with reliable event codes, deterministic mapping may be sufficient.

## Architecture

5. Why rules before ML?
Rules are deterministic, fast, and easy to audit for known patterns.

6. Why ML before the LLM?
The local model is cheaper and has no provider dependency. The confidence threshold prevents forced guesses.

7. What does abstention mean?
The ML model returns no category when its highest probability is below the configured threshold. That is a routing signal, not a failure.

8. Why logistic regression?
The dataset is small, training is fast, probabilities are available, and the model is easy to inspect and replace.

9. Why character TF-IDF?
Character n-grams preserve useful fragments of log tokens and tolerate modest wording variation without a model download.

10. Why not a transformer?
A transformer is reasonable once the dataset and semantic variability justify it. For this corpus it would add runtime and operational complexity without being necessary.

11. Why SQLite instead of PostgreSQL?
The current workload is local classification history, not a distributed transactional workload. At multiple API replicas or higher write concurrency I would move persistence to PostgreSQL.

12. Why not ChromaDB?
There is no retrieval problem in this service. A vector database would be unnecessary infrastructure.

13. Why not LangChain?
The routing graph is only rules, ML and optional LLM. Direct Python keeps the control flow visible.

14. Why is the LLM optional?
The service should remain useful when provider credentials are absent or the provider is unavailable.

15. What happens when the LLM fails?
The result becomes unknown. The service does not convert provider failure into a confident guess.

## Data and evaluation

16. How did you avoid leakage?
Evaluation groups rows by template_id, so repeated phrasings from one template do not appear on both sides of a validation fold.

17. Why does a random split matter?
Repeated templates can make a random split look artificially strong because near-identical examples can land in train and validation.

18. Are the evaluation numbers production accuracy?
No. The dataset is synthetic and small. The evaluation characterizes behavior on this corpus only.

19. What would you measure in production?
Per-category precision and recall, abstention rate, LLM escalation rate, false-positive rate, latency by tier, provider failure rate, and cost per event.

20. How would you improve the dataset?
Collect representative logs, define labels precisely, preserve rare cases, add unseen phrasings, and maintain a regression set.

## Reliability

21. What is the most important failure mode?
Confidently classifying an unfamiliar log incorrectly. Abstention exists to reduce that risk.

22. What if the model artifact is missing?
The API returns service unavailable with instructions to train the artifact.

23. What if input is huge?
The API and LLM adapter enforce input limits.

24. What if the LLM returns malformed JSON?
Schema validation fails and the service returns unknown.

25. What if the provider times out?
The provider exception is caught and the classification is not guessed.

26. Is the classification store a source of truth?
No. It is local history for observability and demonstration. Production would need retention, access control, backups and operational guarantees.

## Incident grouping

27. Why group by entity and time window?
An entity without a time bound can merge unrelated incidents across days. A time window without a shared entity can merge unrelated failures.

28. What entities are currently extracted?
User or account, host or node, service or app, and IP values in supported formats.

29. What is the limitation?
Real logs contain request IDs, trace IDs, pod IDs, deployment IDs and many other identifiers. The extractor is deliberately small.

## Security

30. Is the LLM prompt injection safe?
No. Logs are untrusted text. The prompt treats them as data, but this is not a complete prompt-injection defense.

31. Are secrets stored in SQLite?
No. The provider key comes from the environment and is not persisted.

32. Is this production-ready?
It is production-shaped but not production-proven. It lacks distributed persistence, authentication, rate limiting, operational telemetry and a representative real-world evaluation corpus.

## Scale

33. What is the complexity?
Rule matching scales with the number of configured patterns and input length. Local inference uses a sparse feature representation. LLM latency is dominated by network and provider behavior.

34. What would you cache?
Only after duplicate traffic is measured. I would not add caching speculatively.

35. How would you scale it?
Keep classification stateless, move persistence to PostgreSQL, put the API behind a load balancer, and treat the provider as an external dependency with timeouts, quotas and observability.

36. What is the first bottleneck?
The LLM path, because it is network-bound and provider-limited.

## Testing

37. What tests exist?
Unit tests for rules, model training and abstention, routing, LLM fallback, incident grouping, API validation and source compilation. CI also builds the container and runs an API smoke test.

38. What is not tested live?
A real provider request is not part of public CI because it requires a secret and creates a paid external dependency. The adapter is exercised through deterministic fakes.

39. Why is that acceptable?
Core correctness should not depend on a paid external service. Live provider checks belong in a controlled environment with credentials and spend limits.

40. What would you change next?
Replace the synthetic corpus with representative logs, add category-specific evaluation, add trace IDs, and introduce PostgreSQL only when deployment requirements justify it.

## Trade-off summary

| Choice | Current decision | Revisit when |
| --- | --- | --- |
| Rules | First tier | Pattern catalog becomes unmaintainable |
| Character TF-IDF + logistic regression | Local ML | Dataset or semantic variance grows materially |
| LLM | Optional fallback | Ambiguous volume justifies provider spend |
| SQLite | Local history | Multi-instance requirements appear |
| Direct HTTP | Simple provider adapter | Provider orchestration becomes genuinely complex |
| Streamlit | Demo surface | A real multi-user frontend is required |
