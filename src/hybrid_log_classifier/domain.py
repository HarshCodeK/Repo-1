from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum


class ClassificationTier(StrEnum):
    RULE = "rule"
    ML = "ml"
    LLM = "llm"
    UNKNOWN = "unknown"


class Category(StrEnum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    DEPLOYMENT = "deployment"
    DATA = "data"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class LogEvent:
    text: str
    timestamp: datetime | None = None

    def normalized_timestamp(self) -> datetime:
        value = self.timestamp or datetime.now(timezone.utc)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class Classification:
    category: Category
    tier: ClassificationTier
    confidence: float
    reason: str
    latency_ms: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")
