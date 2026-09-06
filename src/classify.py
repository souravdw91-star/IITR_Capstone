"""
Intent and urgency classification module using LangChain and Google Gemini.
Satisfies Acceptance Criterion A3 and A11.
"""
import os
import json
import re
from typing import Dict, Any, List
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from src.schemas import NormalisedTicket, IntentClassification

load_dotenv()

VALID_INTENTS = [
    "authentication_failure", "deployment_timeout", "api_rate_limit", "billing_dispute",
    "feature_request", "unclear_request", "security_vulnerability", "account_cancellation",
    "database_connection", "sdk_error", "console_ui", "networking_dns", "storage_quota",
    "performance_degradation", "integration_webhook", "onboarding_help", "ssl_certificate",
    "log_drain", "monitoring_alerts", "permission_denied", "region_outage", "general_inquiry"
]

KEYWORDS_TO_INTENT: Dict[str, str] = {
    "login": "authentication_failure",
    "credential": "authentication_failure",
    "password": "authentication_failure",
    "auth": "authentication_failure",
    "sign in": "authentication_failure",
    "token": "authentication_failure",
    "deploy": "deployment_timeout",
    "build": "deployment_timeout",
    "timeout": "deployment_timeout",
    "pipeline": "deployment_timeout",
    "rate limit": "api_rate_limit",
    "429": "api_rate_limit",
    "quota": "api_rate_limit",
    "bill": "billing_dispute",
    "charge": "billing_dispute",
    "invoice": "billing_dispute",
    "refund": "billing_dispute",
    "feature": "feature_request",
    "request": "feature_request",
    "enhancement": "feature_request",
    "security": "security_vulnerability",
    "cve": "security_vulnerability",
    "breach": "security_vulnerability",
    "cancel": "account_cancellation",
    "close account": "account_cancellation",
    "database": "database_connection",
    "postgres": "database_connection",
    "connection refused": "database_connection",
    "sdk": "sdk_error",
    "dns": "networking_dns",
    "domain": "networking_dns",
    "ssl": "ssl_certificate",
    "tls": "ssl_certificate",
    "cert": "ssl_certificate",
}


def rule_based_fallback_classify(ticket: NormalisedTicket) -> IntentClassification:
    """Deterministic heuristic classifier used when LLM is unavailable or for rapid fallback."""
    text_lower = (ticket.subject + " " + ticket.body).lower()

    detected_intent = "general_inquiry"
    for kw, intent in KEYWORDS_TO_INTENT.items():
        if kw in text_lower:
            detected_intent = intent
            break

    # Urgency heuristics
    urgency = "low"
    if any(w in text_lower for w in ["urgent", "down", "critical", "outage", "production"]):
        urgency = "high"
    elif any(w in text_lower for w in ["fail", "error", "broken", "blocked"]):
        urgency = "medium"

    return IntentClassification(
        intent=detected_intent,
        urgency=urgency,
        confidence=0.85 if detected_intent != "general_inquiry" else 0.60,
        considered_alternatives=["general_inquiry", "unclear_request"],
        reasoning="Heuristic keyword fallback classifier."
    )


class TicketClassifier:
    def __init__(self):
        raw_key = os.getenv("GOOGLE_API_KEY", "")
        self.api_key = raw_key.strip("'\" ") if raw_key else None
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        self.llm = None


        if self.api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.0
                )
            except Exception as e:
                print(f"Warning: Failed to initialize ChatGoogleGenerativeAI: {e}")

        # Load prompt template
        prompt_path = os.path.join("prompts", "build", "classifier_v1.prompt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt_template_str = f.read()
        else:
            self.prompt_template_str = "Classify this ticket: Channel: {channel}, Subject: {subject}, Body: {body}"

        self.prompt = PromptTemplate.from_template(self.prompt_template_str)

    def classify(self, ticket: NormalisedTicket) -> IntentClassification:
        """Classifies ticket using Gemini via LangChain, or falls back to rules if unavailable."""
        if not self.llm:
            return rule_based_fallback_classify(ticket)

        try:
            prompt_value = self.prompt.format(
                channel=ticket.channel,
                customer_tier=ticket.customer_tier,
                subject=ticket.subject,
                body=ticket.body
            )
            response = self.llm.invoke(prompt_value)
            content = response.content

            # Parse JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                intent = data.get("intent", "general_inquiry")
                if intent not in VALID_INTENTS:
                    intent = "general_inquiry"

                return IntentClassification(
                    intent=intent,
                    urgency=data.get("urgency", "medium"),
                    confidence=float(data.get("confidence", 0.80)),
                    considered_alternatives=data.get("considered_alternatives", []),
                    reasoning=data.get("reasoning", "LLM classification.")
                )
        except Exception as e:
            print(f"Classification API exception (falling back): {e}")

        return rule_based_fallback_classify(ticket)
