from dataclasses import dataclass
import re

from .domain import Category


@dataclass(frozen=True, slots=True)
class RuleMatch:
    category: Category
    reason: str
    entities: tuple[str, ...]


_RULES: tuple[tuple[Category, str, tuple[str, ...]], ...] = (
    (Category.SECURITY, "authentication or access failure", (r"\bfailed login\b", r"\bauthentication failure\b", r"\bunauthorized\b", r"\bpermission denied\b")),
    (Category.PERFORMANCE, "latency or resource saturation signal", (r"\blatency\b", r"\bslow request\b", r"\bcpu (?:usage|utilization)\b", r"\bmemory (?:usage|utilization)\b", r"\bcache hit ratio\b")),
    (Category.AVAILABILITY, "service availability signal", (r"\bservice unavailable\b", r"\bconnection refused\b", r"\bhealth check failed\b", r"\btimeout\b")),
    (Category.DEPLOYMENT, "deployment or orchestration signal", (r"\bdeployment failed\b", r"\brollout failed\b", r"\bcontainer restart\b", r"\bpod .* restarted\b")),
    (Category.DATA, "data integrity or storage signal", (r"\bconstraint violation\b", r"\bduplicate key\b", r"\bcorrupt(?:ed|ion)?\b", r"\bchecksum mismatch\b")),
)

_ENTITY_PATTERNS = (
    re.compile(r"\b(?:user|account)=([A-Za-z0-9_.-]+)\b", re.I),
    re.compile(r"\b(?:host|node)=([A-Za-z0-9_.-]+)\b", re.I),
    re.compile(r"\b(?:service|app)=([A-Za-z0-9_.-]+)\b", re.I),
    re.compile(r"\b(?:ip|client_ip)=((?:\d{1,3}\.){3}\d{1,3})\b", re.I),
)


def classify(text: str) -> RuleMatch | None:
    for category, reason, patterns in _RULES:
        if any(re.search(pattern, text, re.I) for pattern in patterns):
            return RuleMatch(category, reason, extract_entities(text))
    return None


def extract_entities(text: str) -> tuple[str, ...]:
    entities: list[str] = []
    for pattern in _ENTITY_PATTERNS:
        entities.extend(match.group(1).lower() for match in pattern.finditer(text))
    return tuple(dict.fromkeys(entities))
