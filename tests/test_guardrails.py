"""
Unit tests for safety guardrails and blocking.
Satisfies Acceptance Criterion A7.
"""
from src.schemas import RetrievalPassage
from src.guardrails import evaluate_guardrails


def test_guardrail_pii_blocking():
    passages = [RetrievalPassage(doc_id="DOC-AUTH-001", title="Auth", category="auth", content="Auth text", score=0.9)]
    draft_pii = "Here is your key: sk_live_1234567890abcdef123456 [DOC-AUTH-001]"

    res = evaluate_guardrails(draft_pii, passages)
    assert res.blocked is True
    assert res.pii_detected is True


def test_guardrail_unsupported_claim_blocking():
    passages = [RetrievalPassage(doc_id="DOC-AUTH-001", title="Auth", category="auth", content="Auth text", score=0.9)]
    draft_unsupported = "Don't worry, a full refund issued for your account. [DOC-AUTH-001]"

    res = evaluate_guardrails(draft_unsupported, passages)
    assert res.blocked is True
    assert res.unsupported_claims_detected is True
