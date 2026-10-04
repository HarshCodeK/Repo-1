import csv
from pathlib import Path

from hybrid_log_classifier.ml import train_model

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "training.csv"
MODEL = ROOT / "models" / "classifier.joblib"


def main() -> None:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    summary = train_model(rows, MODEL)
    print(f"trained {summary['rows']} rows across {len(summary['classes'])} classes")
    print(f"saved {MODEL}")


if __name__ == "__main__":
    main()
