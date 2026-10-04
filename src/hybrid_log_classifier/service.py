from time import perf_counter

import httpx

from .domain import Category, Classification, ClassificationTier, LogEvent
from .llm import LLMClassifier
from .ml import MLClassifier
from .persistence import ClassificationStore
from .rules import classify


class ClassifierService:
    def __init__(
        self,
        ml: MLClassifier,
        store: ClassificationStore | None = None,
        llm: LLMClassifier | None = None,
    ) -> None:
        self._ml = ml
        self._store = store
        self._llm = llm

    def classify(self, event: LogEvent) -> Classification:
        started = perf_counter()
        rule_match = classify(event.text)
        if rule_match:
            result = Classification(rule_match.category, ClassificationTier.RULE, 1.0, rule_match.reason, self._elapsed(started))
            self._save(event.text, result)
            return result

        category, confidence = self._ml.predict(event.text)
        if category is not None:
            result = Classification(category, ClassificationTier.ML, confidence, "local model cleared the confidence threshold", self._elapsed(started))
        elif self._llm is not None:
            try:
                output = self._llm.classify(event.text)
                result = Classification(output.category, ClassificationTier.LLM, output.confidence, output.reason, self._elapsed(started))
            except (RuntimeError, ValueError, httpx.HTTPError):
                result = Classification(Category.UNKNOWN, ClassificationTier.UNKNOWN, confidence, "LLM classification failed; request was not guessed", self._elapsed(started))
        else:
            result = Classification(Category.UNKNOWN, ClassificationTier.UNKNOWN, confidence, "local model abstained; no LLM provider was configured", self._elapsed(started))
        self._save(event.text, result)
        return result

    def _save(self, text: str, result: Classification) -> None:
        if self._store:
            self._store.save(text, result)

    @staticmethod
    def _elapsed(started: float) -> float:
        return (perf_counter() - started) * 1000
