import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "training.csv"


def main() -> None:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    texts = [row["text"] for row in rows]
    labels = [row["category"] for row in rows]
    groups = [row["template_id"] for row in rows]
    scores = []
    accepted = []
    for train_idx, test_idx in GroupKFold(n_splits=5).split(texts, labels, groups):
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
        x_train = vectorizer.fit_transform([texts[i] for i in train_idx])
        x_test = vectorizer.transform([texts[i] for i in test_idx])
        model = LogisticRegression(max_iter=500, random_state=42)
        model.fit(x_train, [labels[i] for i in train_idx])
        predictions = model.predict(x_test)
        probabilities = model.predict_proba(x_test)
        confidence = probabilities.max(axis=1)
        keep = confidence >= 0.30
        test_labels = [labels[i] for i in test_idx]
        scores.append((accuracy_score(test_labels, predictions), f1_score(test_labels, predictions, average="macro")))
        if keep.any():
            kept_labels = [label for label, selected in zip(test_labels, keep) if selected]
            accepted.append((keep.mean(), accuracy_score(kept_labels, predictions[keep]), f1_score(kept_labels, predictions[keep], average="macro")))
    print(f"grouped_accuracy={sum(score[0] for score in scores) / len(scores):.3f}")
    print(f"grouped_macro_f1={sum(score[1] for score in scores) / len(scores):.3f}")
    print(f"accepted_coverage_at_0.30={sum(item[0] for item in accepted) / len(accepted):.3f}")
    print(f"accepted_accuracy_at_0.30={sum(item[1] for item in accepted) / len(accepted):.3f}")
    print(f"accepted_macro_f1_at_0.30={sum(item[2] for item in accepted) / len(accepted):.3f}")


if __name__ == "__main__":
    main()
