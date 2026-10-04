from pathlib import Path

from hybrid_log_classifier.domain import Category
from hybrid_log_classifier.ml import MLClassifier, train_model


def test_training_produces_predictable_classifier(tmp_path: Path) -> None:
    rows = [
        {"text": "failed login for admin", "category": "security"},
        {"text": "unauthorized access", "category": "security"},
        {"text": "cpu utilization is high", "category": "performance"},
        {"text": "request latency is high", "category": "performance"},
        {"text": "service unavailable", "category": "availability"},
        {"text": "connection timeout", "category": "availability"},
        {"text": "deployment failed", "category": "deployment"},
        {"text": "container restart", "category": "deployment"},
        {"text": "duplicate key", "category": "data"},
        {"text": "checksum mismatch", "category": "data"},
    ]
    path = tmp_path / "model.joblib"
    train_model(rows, path)
    model = MLClassifier.load(path, threshold=0.01)
    category, confidence = model.predict("admin authentication rejected")
    assert category is Category.SECURITY
    assert confidence > 0.01


def test_low_confidence_abstains(tmp_path: Path) -> None:
    rows = [
        {"text": "login failed", "category": "security"},
        {"text": "login rejected", "category": "security"},
        {"text": "cache slow", "category": "performance"},
        {"text": "high cpu", "category": "performance"},
    ]
    path = tmp_path / "model.joblib"
    train_model(rows, path)
    model = MLClassifier.load(path, threshold=0.9999)
    category, confidence = model.predict("something completely novel")
    assert category is None
    assert 0.0 <= confidence <= 1.0
