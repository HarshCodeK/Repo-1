from dataclasses import dataclass

from .domain import Classification, LogEvent
from .rules import extract_entities


@dataclass(frozen=True, slots=True)
class Incident:
    id: int
    category: str
    events: tuple[LogEvent, ...]


def group_incidents(
    events: list[tuple[LogEvent, Classification]],
    window_seconds: int = 300,
) -> list[Incident]:
    if window_seconds < 0:
        raise ValueError("window_seconds cannot be negative")

    incidents: list[list[tuple[LogEvent, Classification]]] = []
    for event, result in sorted(events, key=lambda item: item[0].normalized_timestamp()):
        entities = set(extract_entities(event.text))
        target: list[tuple[LogEvent, Classification]] | None = None
        for candidate in incidents:
            previous_event, previous_result = candidate[-1]
            if previous_result.category != result.category:
                continue
            delta = (event.normalized_timestamp() - previous_event.normalized_timestamp()).total_seconds()
            if delta > window_seconds:
                continue
            if entities and entities.intersection(extract_entities(previous_event.text)):
                target = candidate
                break
        if target is None:
            incidents.append([(event, result)])
        else:
            target.append((event, result))

    return [
        Incident(index + 1, candidate[0][1].category.value, tuple(event for event, _ in candidate))
        for index, candidate in enumerate(incidents)
    ]
