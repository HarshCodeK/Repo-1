from hybrid_log_classifier.domain import Category
from hybrid_log_classifier.rules import classify, extract_entities


def test_security_rule_matches_and_extracts_entity() -> None:
    match = classify("failed login user=admin_42 ip=203.0.113.7")
    assert match is not None
    assert match.category is Category.SECURITY
    assert "admin_42" in match.entities
    assert "203.0.113.7" in match.entities


def test_unknown_text_does_not_force_rule_answer() -> None:
    assert classify("the application feels unusual today") is None


def test_entity_extraction_deduplicates() -> None:
    assert extract_entities("host=node-1 host=node-1 service=api") == ("node-1", "api")
