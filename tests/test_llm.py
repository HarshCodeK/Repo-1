from hybrid_log_classifier.domain import Category, ClassificationTier, LogEvent
from hybrid_log_classifier.llm import LLMOutput
from hybrid_log_classifier.service import ClassifierService
from hybrid_log_classifier.ml import MLClassifier, train_model


class FakeLLM:
    def classify(self, text: str) -> LLMOutput:
        return LLMOutput(category=Category.SECURITY, confidence=0.91, reason="ambiguous access wording")


def test_ml_abstention_can_reach_llm(tmp_path) -> None:
    rows = [
        {"text": "login failed", "category": "security"},
        {"text": "cpu high", "category": "performance"},
        {"text": "service unavailable", "category": "availability"},
        {"text": "deployment failed", "category": "deployment"},
        {"text": "duplicate key", "category": "data"},
    ] * 2
    model_path = tmp_path / "model.joblib"
    train_model(rows, model_path)
    service = ClassifierService(MLClassifier.load(model_path, threshold=0.9999), llm=FakeLLM())
    result = service.classify(LogEvent("strange access event"))
    assert result.tier is ClassificationTier.LLM
    assert result.category is Category.SECURITY


def test_llm_failure_becomes_unknown(tmp_path) -> None:
    class BrokenLLM:
        def classify(self, text: str) -> LLMOutput:
            raise ValueError("bad provider output")

    rows = [
        {"text": "login failed", "category": "security"},
        {"text": "cpu high", "category": "performance"},
        {"text": "service unavailable", "category": "availability"},
        {"text": "deployment failed", "category": "deployment"},
        {"text": "duplicate key", "category": "data"},
    ] * 2
    model_path = tmp_path / "model.joblib"
    train_model(rows, model_path)
    service = ClassifierService(MLClassifier.load(model_path, threshold=0.9999), llm=BrokenLLM())
    result = service.classify(LogEvent("novel input"))
    assert result.tier is ClassificationTier.UNKNOWN
