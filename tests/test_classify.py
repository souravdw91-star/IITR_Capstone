"""
Unit tests for ticket classification.
Satisfies Acceptance Criterion A3.
"""
from src.ingest import normalise_ticket
from src.classify import TicketClassifier


def test_classification_output():
    classifier = TicketClassifier()
    raw_data = {
        "ticket_id": "TEST-CLASS-001",
        "channel": "email",
        "subject": "Invalid credential login error",
        "body": "I cannot login to console using my password.",
        "received_at": "2026-09-06T12:00:00Z"
    }
    ticket = normalise_ticket(raw_data)
    res = classifier.classify(ticket)

    assert res.intent == "authentication_failure"
    assert 0.0 <= res.confidence <= 1.0
    assert res.urgency in ["high", "medium", "low"]
