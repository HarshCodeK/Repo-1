from datetime import datetime, timedelta, timezone

from hybrid_log_classifier.domain import Category, Classification, ClassificationTier, LogEvent
from hybrid_log_classifier.incidents import group_incidents


def result(category: Category) -> Classification:
    return Classification(category, ClassificationTier.RULE, 1.0, "rule", 0.1)


def test_shared_entity_within_window_is_one_incident() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = [
        (LogEvent("failed login user=alice", start), result(Category.SECURITY)),
        (LogEvent("failed login user=alice", start + timedelta(seconds=60)), result(Category.SECURITY)),
    ]
    incidents = group_incidents(events)
    assert len(incidents) == 1
    assert len(incidents[0].events) == 2


def test_same_entity_outside_window_stays_separate() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = [
        (LogEvent("failed login user=alice", start), result(Category.SECURITY)),
        (LogEvent("failed login user=alice", start + timedelta(seconds=301)), result(Category.SECURITY)),
    ]
    assert len(group_incidents(events)) == 2
