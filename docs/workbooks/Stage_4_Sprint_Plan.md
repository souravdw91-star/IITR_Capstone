# Stage 4 — Sprint Plan & Backlog

**Sprint Length:** 2 Weeks  
**Primary Stack:** Python 3.11, LangChain, FAISS, LangSmith, Google Gemini, FastAPI  

---

## Daily Schedule & Checkpoints

| Day | Focus Area | Deliverable | Definition of Done (DoD) |
| :--- | :--- | :--- | :--- |
| **Day 1** | Ingest Module | `src/ingest.py` | Ingests tickets from all 4 channels (`email`, `chat`, `docs_comment`, `forum`) into `NormalisedTicket` without schema errors. |
| **Day 2** | Retrieval Module | `src/retrieve.py` | FAISS index built over `documentation.json` using Gemini / MiniLM embeddings; search returns ranked passages with doc IDs. |
| **Day 3** | Classification & Routing | `src/classify.py`, `src/route.py`, `src/logging_store.py` | Classifies intent (22 categories) + urgency, applies confidence threshold ($0.80$) & safety overrides, logs to `decisions.db`. |
| **Day 4** | Generation & Guardrails | `src/generate.py`, `src/guardrails.py` | RAG responses with citations (`[DOC-XXX-YYY]`); PII & unsupported claim guardrails block invalid responses. |
| **Day 5** | Unattended Evaluation | `evaluation/harness.py` | Harness runs against full validation set unattended, producing `metrics_report.json` without crashing. Passes Acceptance Criterion A9. |

---

## Scope Reduction Contingency Plan

If time or rate limits require scope reduction:
1. **Primary Defense:** Cache vector retrieval and LLM calls locally during development.
2. **Fallback:** If multi-intent classification degrades, consolidate obscure categories while keeping high-volume categories (`authentication_failure`, `deployment_timeout`, `api_rate_limit`, `billing_dispute`) 100% active.
3. **Core Rule:** Never drop the unattended evaluation harness or decision logging engine.
