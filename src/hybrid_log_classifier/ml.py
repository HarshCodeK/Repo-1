from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .domain import Category


@dataclass(slots=True)
class ModelBundle:
    vectorizer: TfidfVectorizer
    classifier: LogisticRegression


class MLClassifier:
    def __init__(self, bundle: ModelBundle, threshold: float = 0.30) -> None:
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self._bundle = bundle
        self.threshold = threshold

    def predict(self, text: str) -> tuple[Category | None, float]:
        features = self._bundle.vectorizer.transform([text])
        probabilities = self._bundle.classifier.predict_proba(features)[0]
        index = int(probabilities.argmax())
        confidence = float(probabilities[index])
        if confidence < self.threshold:
            return None, confidence
        return Category(self._bundle.classifier.classes_[index]), confidence

    @classmethod
    def load(cls, path: Path, threshold: float = 0.30) -> "MLClassifier":
        bundle = joblib.load(path)
        if not isinstance(bundle, dict) or "vectorizer" not in bundle or "classifier" not in bundle:
            raise ValueError("invalid classifier artifact")
        return cls(ModelBundle(bundle["vectorizer"], bundle["classifier"]), threshold)


def train_model(rows: list[dict[str, str]], output: Path) -> dict[str, Any]:
    texts = [row["text"] for row in rows]
    labels = [row["category"] for row in rows]
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    features = vectorizer.fit_transform(texts)
    classifier = LogisticRegression(max_iter=500, random_state=42)
    classifier.fit(features, labels)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"vectorizer": vectorizer, "classifier": classifier}, output)
    return {"rows": len(rows), "classes": list(classifier.classes_), "features": len(vectorizer.vocabulary_)}
