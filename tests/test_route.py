"""
Unit tests for deterministic routing and thresholds.
Satisfies Acceptance Criterion A5.
"""
from src.schemas import IntentClassification, RetrievalPassage
from src.route import decide_routing


def test_routing_mandatory_escalation():
    cls = IntentClassification(
        intent="billing_dispute",
        urgency="high",
        confidence=0.95,
        reasoning="Billing issue"
    )
    passages = [RetrievalPassage(doc_id="DOC-BILL-001", title="Billing", category="billing", content="Bill info", score=0.9)]

    decision = decide_routing(cls, passages, override_threshold=0.80)
    assert decision.action == "escalate"
    assert decision.must_escalate is True


def test_routing_auto_respond():
    cls = IntentClassification(
        intent="authentication_failure",
        urgency="medium",
        confidence=0.88,
        reasoning="Auth failure"
    )
    passages = [RetrievalPassage(doc_id="DOC-AUTH-001", title="Auth", category="auth", content="Auth info", score=0.9)]

    decision = decide_routing(cls, passages, override_threshold=0.80)
    assert decision.action == "auto_respond"
