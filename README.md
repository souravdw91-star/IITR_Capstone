# CloudServe Intelligent Support Automation System

An enterprise customer support automation, retrieval (RAG), classification, routing, and escalation engine built using **LangChain**, **FAISS**, **LangSmith**, and **Google Gemini**.

Designed for **CloudServe Solutions** to automate ticket resolution across 4 channels (`email`, `chat`, `docs_comment`, `forum`), achieve SLA compliance (Time-to-first-reply < 5 mins, FCR >= 65%), and maintain strict safety guardrails and audit decision logging.

---

## 1. Required API Keys

To run and evaluate the system, set the following environment variables in `.env`:

| API Key | Purpose | Required? | Where to Get |
| :--- | :--- | :--- | :--- |
| `GOOGLE_API_KEY` | Powers **Google Gemini** LLM (`gemini-2.5-flash` / `gemini-1.5-flash`) for intent classification and RAG response generation. | **Yes** | [Google AI Studio](https://aistudio.google.com/) |
| `LANGCHAIN_API_KEY` | Enables **LangSmith** tracing, debugging, and LLM call observability. | **Optional / Recommended** | [LangSmith Console](https://smith.langchain.com/) |

---

## 2. Environment Setup

### Step 1: Create and Activate Virtual Environment
```bash
python -m venv .venv

# On Windows PowerShell:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Pinned Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

Example `.env`:
```env
GOOGLE_API_KEY=AIzaSy...your_gemini_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt...your_langsmith_key
LANGCHAIN_PROJECT=cloudserve-support-system

MODEL_NAME=gemini-2.5-flash
EMBEDDING_MODEL=models/text-embedding-004
FAISS_INDEX_PATH=./storage/faiss_index
DATABASE_URL=sqlite:///./storage/decisions.db
CONFIDENCE_THRESHOLD=0.80
LOG_LEVEL=INFO
KILL_SWITCH_ACTIVE=false
```

---

## 3. Running Tests (Acceptance Criterion A12)

Run the full automated test suite with a single command:
```bash
python -m pytest tests/ -v
```

---

## 4. Unattended Evaluation Run (Acceptance Criteria A9 & A10)

Process any ticket validation or hidden test set unattended in a single run:

```bash
python -m evaluation.harness --input FDE_Capstone_Docs/05_Datasets/validation_tickets.json --output evaluation/results/
```

This generates `evaluation/results/metrics_report.json` containing Volume, Business (FCR %, Latency), Technical (Precision, Citation Accuracy), and Governance metrics.

---

## 5. Launching the Interactive Streamlit Web App & FastAPI

### Option A: Launch Interactive Streamlit UI (Recommended for Testing)
```bash
streamlit run streamlit_app.py
```
This opens the **CloudServe Support AI Hub** in your browser (`http://localhost:8501`) featuring:
- Live ticket testing across all 4 channels (`email`, `chat`, `docs_comment`, `forum`).
- Real-time intent classification & confidence breakdown.
- FAISS vector passage retrieval viewer.
- Safety guardrail intercept audit.
- SQLite decision log table viewer (`storage/decisions.db`).
- Emergency Kill Switch control toggle.

### Option B: Launch FastAPI Backend Server
```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive API Documentation (Swagger UI):** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/health`
- **Prometheus Metrics Endpoint:** `http://localhost:8000/metrics`


---

## 6. System Architecture & Component Mapping

- **Channel Ingestion (`src/ingest.py`):** Normalizes tickets from email, chat, docs comment, and community forum into unified `NormalisedTicket` schema.
- **Intent & Urgency Classifier (`src/classify.py`):** LangChain chain querying Google Gemini to predict intent (22 categories), urgency (`high`, `medium`, `low`), and numeric confidence ($0.0 \le c \le 1.0$).
- **FAISS Vector Store Retriever (`src/retrieve.py`):** FAISS semantic search index built over 29 knowledge base articles (`documentation.json`).
- **Deterministic Router (`src/route.py`):** Applies confidence threshold ($0.80$) and safety rules (`must_not_auto_respond`).
- **Grounded Answer Generator (`src/generate.py`):** RAG pipeline generating answers strictly grounded in retrieved documentation with doc citation tags `[DOC-XXX-YYY]`.
- **Guardrails Engine (`src/guardrails.py`):** Scans outbound responses for PII (emails, keys, credit cards) and unsupported claims; hard blocks invalid responses.
- **Decision Audit Store (`src/logging_store.py`):** SQLite database (`storage/decisions.db`) capturing audit trails for all decisions.

---

## 7. Project Documentation

- [Stage 1 Discovery Workbook](file:///c:/Sourav/Study/FDE/IITR_Capstone/docs/workbooks/Stage_1_Discovery_Workbook.md)
- [Stage 2 Product Requirements Document (PRD v1)](file:///c:/Sourav/Study/FDE/IITR_Capstone/docs/workbooks/Stage_2_PRD.md)
- [Stage 3 Prompt Library](file:///c:/Sourav/Study/FDE/IITR_Capstone/docs/workbooks/Stage_3_Prompt_Library.md)
- [Stage 4 Sprint Plan](file:///c:/Sourav/Study/FDE/IITR_Capstone/docs/workbooks/Stage_4_Sprint_Plan.md)
- [Stage 5 PRD Revision Log](file:///c:/Sourav/Study/FDE/IITR_Capstone/docs/workbooks/Stage_5_PRD_Revision_Log.md)
- [Governance Framework & Risk Register](file:///c:/Sourav/Study/FDE/IITR_Capstone/docs/governance/Governance_Framework.md)
