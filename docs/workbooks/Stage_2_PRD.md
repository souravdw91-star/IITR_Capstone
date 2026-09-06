# Stage 2 — Product Requirements Document (PRD v1)

**Product:** CloudServe Support Automation Engine  
**Version:** 1.0  
**Status:** Approved  

---

## 1. Objectives & Business Goals

- **First Contact Resolution (FCR):** Increase from 42% baseline to **>= 65%**.
- **Average Time to First Reply:** Reduce from 8-12 hours to **< 5 minutes** (under 3 seconds for automated replies).
- **Escalation Rate:** Reduce from 58% to **<= 30%**.
- **CSAT Rating:** Improve from 3.2/5 to **>= 4.0/5**.

---

## 2. Functional Requirements (FR)

| Req ID | Title | Description | Traceability Evidence |
| :--- | :--- | :--- | :--- |
| **FR-1** | Channel Ingestion & Normalization | System must ingest tickets from `email`, `chat`, `docs_comment`, and `forum`, converting them into a unified internal `NormalisedTicket` structure without losing original text or metadata. | Discovery Workbook Section 2; Acceptance Criterion A2. |
| **FR-2** | Intent & Urgency Classification | System must classify each ticket into one of 22 intent categories and assign an urgency level (`high`, `medium`, `low`) along with a calibrated numerical confidence score ($0.0 \le c \le 1.0$). | Stakeholder Interview (Head of Support); Acceptance Criterion A3. |
| **FR-3** | FAISS Vector Document Retrieval | System must index CloudServe's 29 knowledge base articles (`documentation.json`) using FAISS vector store and return relevant passages with doc IDs and titles. | Stakeholder Interview (Tier 1 Agent); Acceptance Criterion A4. |
| **FR-4** | Deterministic Routing Engine | System must apply a calibrated confidence threshold ($c \ge 0.80$) and enforce safety override rules (`must_not_auto_respond`) to route between auto-response and escalation. | Project Brief Section 5; Acceptance Criterion A5. |
| **FR-5** | Citation-Grounded Answer Generation | System must generate RAG responses using **Google Gemini**, strictly grounded in retrieved passages, appending inline bracket citations `[DOC-XXX-YYY]`. | Stakeholder Interview (Customer); Acceptance Criterion A6. |
| **FR-6** | Execution Guardrails | System must evaluate outbound responses against active guardrails (PII detection and unsupported claim verification) and BLOCK responses if violated. | Governance Framework; Acceptance Criterion A7. |
| **FR-7** | SQLite Audit Decision Logging | System must persist every automated classification, retrieval, routing decision, and guardrail check into `storage/decisions.db`. | Governance Framework; Acceptance Criterion A8. |
| **FR-8** | Unattended Evaluation Harness | System must process any input validation/test JSON set unattended via CLI arguments (`--input` and `--output`), producing `metrics_report.json`. | Acceptance Criteria A9 & A10. |

---

## 3. Non-Functional Requirements (NFR)

| Req ID | Category | Requirement | Target |
| :--- | :--- | :--- | :--- |
| **NFR-1** | Performance | 95th percentile response latency for auto-responses. | $< 3.0$ seconds |
| **NFR-2** | Reliability | Graceful handling of LLM provider timeout, empty retrieval, or malformed input without crashing. | 99.5% uptime / 0 unhandled exceptions (A11) |
| **NFR-3** | Safety & Privacy | Outbound auto-responses containing private customer data (emails, API keys, passwords, credit cards). | **0 occurrences** (Zero tolerance) |
| **NFR-4** | Grounding | Hallucination rate on automated answers. | $< 5\%$ unsupported claims |
| **NFR-5** | Citation Accuracy | Citations pointing to correct supporting document passages. | $\ge 95\%$ accuracy |
| **NFR-6** | Observability | Full trace logging and latency tracking via LangSmith. | `LANGCHAIN_TRACING_V2=true` |
