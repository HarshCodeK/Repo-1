from pathlib import Path

from hybrid_log_classifier.domain import ClassificationTier, LogEvent
from hybrid_log_classifier.ml import MLClassifier, train_model
from hybrid_log_classifier.persistence import ClassificationStore
from hybrid_log_classifier.service import ClassifierService


def build_service(tmp_path: Path, threshold: float = 0.30) -> ClassifierService:
    rows = [
        {"text": "login failed", "category": "security"},
        {"text": "unauthorized user", "category": "security"},
        {"text": "cpu high", "category": "performance"},
        {"text": "latency high", "category": "performance"},
        {"text": "compute pressure is elevated", "category": "performance"},
        {"text": "service unavailable", "category": "availability"},
        {"text": "timeout upstream", "category": "availability"},
        {"text": "deployment failed", "category": "deployment"},
        {"text": "container restart", "category": "deployment"},
        {"text": "duplicate key", "category": "data"},
        {"text": "checksum mismatch", "category": "data"},
    ]
    model_path = tmp_path / "model.joblib"
    train_model(rows, model_path)
    return ClassifierService(MLClassifier.load(model_path, threshold=threshold), ClassificationStore(tmp_path / "classifications.db"))


def test_rule_wins_before_ml(tmp_path: Path) -> None:
    result = build_service(tmp_path).classify(LogEvent("failed login user=alice"))
    assert result.tier is ClassificationTier.RULE


def test_ml_handles_semantic_variant(tmp_path: Path) -> None:
    result = build_service(tmp_path, threshold=0.40).classify(LogEvent("compute pressure is elevated"))
    assert result.tier is ClassificationTier.ML


def test_abstention_is_visible(tmp_path: Path) -> None:
    result = build_service(tmp_path, threshold=0.9999).classify(LogEvent("something unrelated"))
    assert result.tier is ClassificationTier.UNKNOWN
    assert result.reason.startswith("local model abstained")
