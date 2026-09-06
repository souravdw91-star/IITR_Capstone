"""
Ticket ingestion and normalization module across four channels.
Satisfies Acceptance Criterion A2.
"""
import re
from typing import Dict, Any
from src.schemas import RawTicket, NormalisedTicket


def normalise_ticket(raw_data: Dict[str, Any]) -> NormalisedTicket:
    """
    Normalises raw ticket dictionary into a clean NormalisedTicket.
    Handles missing fields, empty subjects for chat, and cleans whitespace.
    """
    ticket_id = raw_data.get("ticket_id", "UNKNOWN-000")
    channel = raw_data.get("channel", "email").lower()
    subject = raw_data.get("subject", "").strip()
    body = raw_data.get("body", "").strip()

    # Channel-specific normalization quirks
    if channel == "chat" and not subject:
        # Chat tickets often have empty subject
        subject = f"Live Chat Request ({ticket_id})"
    elif channel == "docs_comment" and not subject:
        subject = f"Documentation Comment ({ticket_id})"
    elif channel == "forum" and not subject:
        subject = f"Community Forum Post ({ticket_id})"

    clean_body = re.sub(r'\s+', ' ', body)
    clean_text = f"Subject: {subject}\nBody: {clean_body}".strip()

    raw_obj = RawTicket(
        ticket_id=ticket_id,
        channel=channel,
        subject=subject,
        body=body,
        received_at=raw_data.get("received_at", ""),
        customer_id=raw_data.get("customer_id", "CUST-0000"),
        customer_name=raw_data.get("customer_name", "Customer"),
        customer_tier=raw_data.get("customer_tier", "standard"),
        customer_region=raw_data.get("customer_region", "north_america"),
        language_fluency=raw_data.get("language_fluency", "fluent"),
        labels=raw_data.get("labels"),
        history=raw_data.get("history")
    )

    return NormalisedTicket(
        ticket_id=ticket_id,
        channel=channel,
        subject=subject if subject else "General Support Ticket",
        body=body,
        clean_text=clean_text,
        received_at=raw_data.get("received_at", ""),
        customer_id=raw_data.get("customer_id", "CUST-0000"),
        customer_name=raw_data.get("customer_name", "Customer"),
        customer_tier=raw_data.get("customer_tier", "standard"),
        customer_region=raw_data.get("customer_region", "north_america"),
        language_fluency=raw_data.get("language_fluency", "fluent"),
        raw_ticket=raw_obj
    )
