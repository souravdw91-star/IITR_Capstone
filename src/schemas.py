"""
Data schemas and Pydantic models for the CloudServe Support System.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RawTicket(BaseModel):
    ticket_id: str
    channel: str  # email, chat, docs_comment, forum
    subject: Optional[str] = ""
    body: str
    received_at: str
    customer_id: str
    customer_name: Optional[str] = "Customer"
    customer_tier: str = "standard"  # enterprise, business, standard
    customer_region: str = "north_america"
    language_fluency: str = "fluent"
    labels: Optional[Dict[str, Any]] = None
    history: Optional[Dict[str, Any]] = None


class NormalisedTicket(BaseModel):
    ticket_id: str
    channel: str
    subject: str
    body: str
    clean_text: str
    received_at: str
    customer_id: str
    customer_name: str
    customer_tier: str
    customer_region: str
    language_fluency: str
    raw_ticket: RawTicket


class IntentClassification(BaseModel):
    intent: str
    urgency: str  # high, medium, low
    confidence: float  # 0.0 to 1.0
    considered_alternatives: List[str] = Field(default_factory=list)
    reasoning: str = ""


class RetrievalPassage(BaseModel):
    doc_id: str
    title: str
    category: str
    content: str
    score: float


class RoutingDecision(BaseModel):
    action: str  # auto_respond | escalate
    reason: str
    confidence: float
    threshold: float
    must_escalate: bool = False


class GuardrailResult(BaseModel):
    passed: bool
    blocked: bool
    reasons: List[str] = Field(default_factory=list)
    pii_detected: bool = False
    unsupported_claims_detected: bool = False


class OutboundResponse(BaseModel):
    ticket_id: str
    action_taken: str  # auto_respond | escalate | blocked
    answer: Optional[str] = None
    cited_doc_ids: List[str] = Field(default_factory=list)
    escalation_reason: Optional[str] = None
    confidence: float
    intent: str
    urgency: str
    guardrail_result: Optional[GuardrailResult] = None
    decision_id: Optional[str] = None
