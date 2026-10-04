import sqlite3
from pathlib import Path

from .domain import Classification


class ClassificationStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reason TEXT NOT NULL,
                    latency_ms REAL NOT NULL
                )
                """
            )

    def save(self, text: str, result: Classification) -> None:
        with sqlite3.connect(self._path) as connection:
            connection.execute(
                "INSERT INTO classifications(text, category, tier, confidence, reason, latency_ms) VALUES (?, ?, ?, ?, ?, ?)",
                (text, result.category.value, result.tier.value, result.confidence, result.reason, result.latency_ms),
            )
