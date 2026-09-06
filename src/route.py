"""
Routing engine module applying confidence threshold and safety intent constraints.
Satisfies Acceptance Criterion A5.
"""
import os
from typing import List
from dotenv import load_dotenv

from src.schemas import IntentClassification, RetrievalPassage, RoutingDecision

load_dotenv()

# Intents that must ALWAYS escalate for safety/policy reasons
MUST_ESCALATE_INTENTS = {
    "billing_dispute",
    "security_vulnerability",
    "account_cancellation",
    "feature_request",
    "unclear_request"
}


def decide_routing(
    classification: IntentClassification,
    retrieved_passages: List[RetrievalPassage],
    override_threshold: float = None
) -> RoutingDecision:
    """
    Deterministically decides whether to auto-respond or escalate.
    Returns RoutingDecision.
    """
    threshold = override_threshold if override_threshold is not None else float(os.getenv("CONFIDENCE_THRESHOLD", 0.80))
    intent = classification.intent.lower()
    confidence = classification.confidence

    # Rule 1: Mandatory Escalation Intents
    if intent in MUST_ESCALATE_INTENTS:
        return RoutingDecision(
            action="escalate",
            reason=f"Policy requirement: '{intent}' issues must be reviewed by human support.",
            confidence=confidence,
            threshold=threshold,
            must_escalate=True
        )

    # Rule 2: Confidence Threshold Check
    if confidence < threshold:
        return RoutingDecision(
            action="escalate",
            reason=f"Classification confidence ({confidence:.2f}) is below threshold ({threshold:.2f}).",
            confidence=confidence,
            threshold=threshold,
            must_escalate=False
        )

    # Rule 3: Retrieval Grounding Check
    if not retrieved_passages:
        return RoutingDecision(
            action="escalate",
            reason="No relevant documentation passages found to ground an automated answer.",
            confidence=confidence,
            threshold=threshold,
            must_escalate=False
        )

    # Auto-Respond Decision
    top_doc_ids = ", ".join(list(set(p.doc_id for p in retrieved_passages)))
    return RoutingDecision(
        action="auto_respond",
        reason=f"High confidence ({confidence:.2f} >= {threshold:.2f}) with supporting docs ({top_doc_ids}).",
        confidence=confidence,
        threshold=threshold,
        must_escalate=False
    )
