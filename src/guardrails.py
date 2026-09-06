"""
Safety and Governance Guardrails Engine.
Satisfies Acceptance Criterion A7 and Governance Framework requirements.
"""
import re
from typing import List
from src.schemas import GuardrailResult, RetrievalPassage

# Regex patterns for detecting private data (PII) leakage
PII_PATTERNS = [
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email address detected"),
    (r'\b(?:sk_live|sk_test|api_key|secret_key)_[0-9a-zA-Z]{16,}\b', "Secret API Key detected"),
    (r'\b(?:\d[ -]*?){13,16}\b', "Credit Card / Account Number pattern detected"),
    (r'password\s*=\s*[\'"][^\'"]+[\'"]', "Plaintext password detected")
]


def evaluate_guardrails(
    draft_response: str,
    passages: List[RetrievalPassage]
) -> GuardrailResult:
    """
    Evaluates outbound draft response for PII leakage and claim grounding.
    Returns GuardrailResult with passed/blocked status.
    """
    reasons: List[str] = []
    pii_detected = False
    unsupported_claims_detected = False

    if not draft_response:
        return GuardrailResult(
            passed=False,
            blocked=True,
            reasons=["Draft response is empty."],
            pii_detected=False,
            unsupported_claims_detected=True
        )

    # 1. PII Check
    for pattern, description in PII_PATTERNS:
        # Ignore standard generic help email placeholders if any
        matches = re.findall(pattern, draft_response, re.IGNORECASE)
        filtered_matches = [m for m in matches if not m.endswith("@cloudserve.com") and not m.endswith("@example.com")]
        if filtered_matches:
            pii_detected = True
            reasons.append(f"PII Violation: {description} ({filtered_matches[0][:8]}...)")

    # 2. Unsupported Claim / Refund Check
    unsafe_keywords = ["refund issued", "free upgrade", "100% money back", "guaranteed credit"]
    for kw in unsafe_keywords:
        if kw in draft_response.lower():
            unsupported_claims_detected = True
            reasons.append(f"Policy Violation: Unauthorized commitment '{kw}'.")

    # 3. Citation Check
    if passages and not any(p.doc_id in draft_response for p in passages):
        # Warning if doc citation missing despite passages being retrieved
        reasons.append("Grounding Warning: Document citation tag missing from output text.")

    blocked = pii_detected or unsupported_claims_detected
    passed = not blocked

    return GuardrailResult(
        passed=passed,
        blocked=blocked,
        reasons=reasons,
        pii_detected=pii_detected,
        unsupported_claims_detected=unsupported_claims_detected
    )
