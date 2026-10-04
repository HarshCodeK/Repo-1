# ML tuning note

The first evaluation used a word-level TF-IDF representation and the default confidence gate did not accept unseen templates reliably. That was treated as a model-design problem, not hidden behind a higher headline accuracy.

The implementation was changed to character n-grams with a 3–5 character window. The confidence threshold was then evaluated as a coverage-versus-precision trade-off.

On the included grouped five-fold corpus, threshold 0.30 produced approximately:

- 30.5% accepted coverage
- 92.0% accuracy on accepted predictions
- 87.3% macro F1 on accepted predictions

The overall grouped accuracy remains 48.9% because the model abstains on many held-out templates. That is intentional: the system prefers escalation or unknown over a forced low-confidence prediction.

These values are corpus-specific and must be regenerated after changing the dataset, feature representation, classifier, or threshold.
