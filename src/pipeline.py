from src.schemas import OutboundResponse
from src.ingest import normalise_ticket
from src.classify import TicketClassifier
from src.retrieve import DocumentationRetriever
from src.route import decide_routing
from src.generate import ResponseGenerator
from src.guardrails import evaluate_guardrails
from src.logging_store import DecisionLogger

load_dotenv()

# Optional LangSmith traceable decorator
try:
    from langsmith import traceable
    HAS_LANGSMITH = True
except ImportError:
    HAS_LANGSMITH = False
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator



class SupportPipeline:
    def __init__(
        self,
        docs_path: str = "FDE_Capstone_Docs/05_Datasets/documentation.json",
        db_path: str = None
    ):
        self.classifier = TicketClassifier()
        self.retriever = DocumentationRetriever(docs_path=docs_path)
        self.generator = ResponseGenerator()
        self.logger = DecisionLogger(db_path=db_path)

    @traceable(name="CloudServe_Support_Pipeline")
    def process_ticket(self, raw_ticket_data: Dict[str, Any]) -> OutboundResponse:

        """
        Executes the end-to-end processing pipeline on a raw ticket dictionary.
        """
        # Step 1: Ingest & Normalise
        ticket = normalise_ticket(raw_ticket_data)

        # Check Kill Switch
        if os.getenv("KILL_SWITCH_ACTIVE", "false").lower() == "true":
            decision_id = self.logger.log_decision(
                ticket_id=ticket.ticket_id,
                channel=ticket.channel,
                customer_tier=ticket.customer_tier,
                stage="routing",
                prediction="kill_switch",
                confidence=1.0,
                threshold=0.80,
                action_taken="escalate",
                reason="System Kill Switch is currently ACTIVE. All tickets routed to human agents."
            )
            return OutboundResponse(
                ticket_id=ticket.ticket_id,
                action_taken="escalate",
                escalation_reason="Kill Switch ACTIVE. Escalated to human queue.",
                confidence=1.0,
                intent="system_kill_switch",
                urgency="high",
                decision_id=decision_id
            )

        # Step 2: Classify
        classification = self.classifier.classify(ticket)

        # Step 3: Retrieve
        query = f"{classification.intent} {ticket.subject} {ticket.body[:150]}"
        passages = self.retriever.search(query=query, top_k=3)

        # Step 4: Route
        routing = decide_routing(classification, passages)

        # Log routing decision
        doc_ids = [p.doc_id for p in passages]
        decision_id = self.logger.log_decision(
            ticket_id=ticket.ticket_id,
            channel=ticket.channel,
            customer_tier=ticket.customer_tier,
            stage="routing",
            prediction=classification.intent,
            confidence=classification.confidence,
            threshold=routing.threshold,
            action_taken=routing.action,
            reason=routing.reason,
            sources_used=doc_ids
        )

        if routing.action == "escalate":
            return OutboundResponse(
                ticket_id=ticket.ticket_id,
                action_taken="escalate",
                escalation_reason=routing.reason,
                confidence=classification.confidence,
                intent=classification.intent,
                urgency=classification.urgency,
                cited_doc_ids=doc_ids,
                decision_id=decision_id
            )

        # Step 5: Generate Answer
        draft_answer, cited_docs = self.generator.generate(ticket, passages)

        # Step 6: Validate Guardrails
        guardrail_res = evaluate_guardrails(draft_answer, passages)

        if guardrail_res.blocked:
            # Blocked by guardrails -> convert to escalation
            block_reason = f"Blocked by Guardrails: {'; '.join(guardrail_res.reasons)}"
            self.logger.log_decision(
                ticket_id=ticket.ticket_id,
                channel=ticket.channel,
                customer_tier=ticket.customer_tier,
                stage="guardrails",
                prediction=classification.intent,
                confidence=classification.confidence,
                threshold=routing.threshold,
                action_taken="blocked",
                reason=block_reason,
                sources_used=cited_docs,
                guardrails=guardrail_res.dict()
            )
            return OutboundResponse(
                ticket_id=ticket.ticket_id,
                action_taken="blocked",
                escalation_reason=block_reason,
                confidence=classification.confidence,
                intent=classification.intent,
                urgency=classification.urgency,
                guardrail_result=guardrail_res,
                decision_id=decision_id
            )

        # Auto-response successful
        return OutboundResponse(
            ticket_id=ticket.ticket_id,
            action_taken="auto_respond",
            answer=draft_answer,
            cited_doc_ids=cited_docs if cited_docs else doc_ids,
            confidence=classification.confidence,
            intent=classification.intent,
            urgency=classification.urgency,
            guardrail_result=guardrail_res,
            decision_id=decision_id
        )
