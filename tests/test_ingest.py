"""
Unit tests for channel ingestion and normalization.
Satisfies Acceptance Criterion A2.
"""
from src.ingest import normalise_ticket


def test_ingest_all_four_channels():
    channels = ["email", "chat", "docs_comment", "forum"]

    for channel in channels:
        raw_data = {
            "ticket_id": f"TEST-{channel.upper()}-001",
            "channel": channel,
            "subject": "Unable to deploy" if channel != "chat" else "",
            "body": "Building pipeline fails with error code 500.",
            "received_at": "2026-09-06T12:00:00Z",
            "customer_id": "CUST-9999"
        }
        norm = normalise_ticket(raw_data)

        assert norm.ticket_id == f"TEST-{channel.upper()}-001"
        assert norm.channel == channel
        assert len(norm.subject) > 0
        assert "500" in norm.clean_text
