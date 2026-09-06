"""
Integration tests for the complete SupportPipeline.
Satisfies Acceptance Criteria A1-A8, A12.
"""
import os
from src.pipeline import SupportPipeline


def test_pipeline_execution():
    test_db = "./storage/test_decisions.db"
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass

    pipeline = SupportPipeline(db_path=test_db)

    ticket_data = {
        "ticket_id": "TEST-PIPE-001",
        "channel": "email",
        "subject": "Resolving invalid credential errors on login",
        "body": "The console returns Invalid credentials when attempting to log in.",
        "received_at": "2026-09-06T12:00:00Z",
        "customer_id": "CUST-1001"
    }

    res = pipeline.process_ticket(ticket_data)

    assert res.ticket_id == "TEST-PIPE-001"
    assert res.action_taken in ["auto_respond", "escalate", "blocked"]
    assert res.decision_id is not None
    assert pipeline.logger.get_decision_count() >= 1

    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass
