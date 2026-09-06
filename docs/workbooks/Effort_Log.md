# Capstone Project Effort Log

**Engineer:** Forward Deployed AI Engineer  
**Project:** CloudServe Support Automation Engine  
**Period:** 24 August 2026 – 13 September 2026  

---

## Stage-by-Stage Hour Summary

| Stage | Planned Hours | Actual Hours | Variance | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **1. Discovery** | 12.0 hrs | 14.5 hrs | +2.5 hrs | Additional time spent cross-referencing stakeholder interviews with ticket dataset to identify documentation overlap (~75%). |
| **2. Requirements (PRD)** | 8.0 hrs | 7.0 hrs | -1.0 hrs | Efficient mapping using Discovery Workbook traceability tags. |
| **3. Prompt Library** | 10.0 hrs | 11.5 hrs | +1.5 hrs | Iterative prompt engineering for structured JSON output and citation formatting. |
| **4. Sprint Plan** | 4.0 hrs | 4.0 hrs | 0.0 hrs | Aligned backlog to 5-day week 2 build checkpoints. |
| **5. Build & Revision** | 30.0 hrs | 34.0 hrs | +4.0 hrs | Built FAISS vector retriever, LangChain pipeline, guardrails, and Streamlit testing UI; resolved SQLite file locking. |
| **6. Evaluation & Governance** | 16.0 hrs | 15.0 hrs | -1.0 hrs | Automated evaluation harness generated metrics report seamlessly. |
| **Total Effort** | **80.0 hrs** | **86.0 hrs** | **+6.0 hrs** | Thorough build and verification ensured 100% acceptance criteria pass. |

---

## Granular Daily Log Entries

### Week 1: Understanding & Requirements
- **Day 1 (24 Aug):** Environment setup, Python 3.11 virtualenv configuration, package dependency management (`requirements.txt`). (Planned: 4.0h, Actual: 4.5h)
- **Day 2 (25 Aug):** Stakeholder interview analysis (Head of Support, Tier 1/2 Agents, Technical Writer, Customer). (Planned: 4.0h, Actual: 5.0h)
- **Day 3 (26 Aug):** Ticket dataset exploration (`development_tickets.json`), channel quirk analysis, Stage 1 Discovery Workbook completion. (Planned: 4.0h, Actual: 5.0h)
- **Day 4 (27 Aug):** Authoring PRD v1 (`Stage_2_PRD.md`), establishing traceability matrix connecting FRs to discovery evidence. (Planned: 4.0h, Actual: 3.5h)
- **Day 5 (28 Aug):** Finalizing PRD non-functional requirements and target metrics (FCR >= 65%, P95 Latency < 3s). (Planned: 4.0h, Actual: 3.5h)

### Week 2: Build & Execution
- **Day 6 (31 Aug):** Authoring versioned prompts (`classifier_v1`, `generator_v1`, `guardrail_eval_v1`) in Stage 3 Prompt Library. (Planned: 5.0h, Actual: 6.0h)
- **Day 7 (01 Sep):** Sprint backlog creation (`Stage_4_Sprint_Plan.md`), DoD definition, scope reduction contingency planning. (Planned: 4.0h, Actual: 4.0h)
- **Day 8 (02 Sep):** Implementation of multi-channel ingestion (`src/ingest.py`) and FAISS vector retriever (`src/retrieve.py`). (Planned: 6.0h, Actual: 7.5h)
- **Day 9 (03 Sep):** Implementation of LangChain Gemini classifier (`src/classify.py`) and deterministic router (`src/route.py`). (Planned: 6.0h, Actual: 6.5h)
- **Day 10 (04 Sep):** RAG answer generator with citations (`src/generate.py`) and PII/unsupported claim guardrails (`src/guardrails.py`). (Planned: 6.0h, Actual: 7.0h)

### Week 3: Governance, Evaluation & Submission
- **Day 11 (07 Sep):** SQLite audit decision logger (`src/logging_store.py`) and end-to-end pipeline (`src/pipeline.py`). (Planned: 6.0h, Actual: 7.0h)
- **Day 12 (08 Sep):** Unattended evaluation harness (`evaluation/harness.py`), running 80 validation tickets. (Planned: 5.0h, Actual: 5.0h)
- **Day 13 (09 Sep):** PRD Revision Log (`Stage_5_PRD_Revision_Log.md`) and Governance Framework (`Governance_Framework.md`). (Planned: 5.0h, Actual: 4.5h)
- **Day 14 (10 Sep):** Interactive Streamlit web application (`streamlit_app.py`) for live ticket testing lab. (Planned: 4.0h, Actual: 5.5h)
- **Day 15 (11 Sep):** Authoring comprehensive project report (`docs/Project_Report.md`) and final submission packaging. (Planned: 7.0h, Actual: 7.5h)
