"""
Streamlit Web Application for testing CloudServe Intelligent Support System.
Run with: streamlit run streamlit_app.py
"""
import os
import json
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.pipeline import SupportPipeline
from src.ingest import normalise_ticket

load_dotenv()

# Page Setup
st.set_page_config(
    page_title="CloudServe Support AI Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .badge-auto {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .badge-escalate {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .badge-blocked {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_pipeline():
    return SupportPipeline()


pipeline = None
pipeline_error = None
try:
    pipeline = get_pipeline()
except Exception as e:
    pipeline_error = str(e)

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/cloud-lighting.png", width=60)
st.sidebar.title("CloudServe Control")
st.sidebar.caption("LangChain + FAISS + LangSmith + Google Gemini")

nav_choice = st.sidebar.radio(
    "Navigation",
    ["🎫 Ticket Testing Lab", "📊 Decision Audit Logs", "📈 Metrics & Evaluation", "🛡️ Governance & Kill Switch"]
)

# Kill Switch Status Indicator in Sidebar
kill_switch_status = os.getenv("KILL_SWITCH_ACTIVE", "false").lower() == "true"
if kill_switch_status:
    st.sidebar.error("🚨 KILL SWITCH ACTIVE (100% Escalation)")
else:
    st.sidebar.success("🟢 System Operational")

st.sidebar.markdown("---")
st.sidebar.markdown("**API Status**")
api_key_val = os.getenv("GOOGLE_API_KEY", "").strip("'\" ")
if api_key_val:
    st.sidebar.info("🔑 `GOOGLE_API_KEY` Detected")
else:
    st.sidebar.warning("⚠️ No `GOOGLE_API_KEY` (Rule Fallback Active)")

langsmith_val = os.getenv("LANGCHAIN_API_KEY", "").strip("'\" ")
if langsmith_val:
    st.sidebar.info("📊 LangSmith Tracing Active")

if pipeline_error:
    st.sidebar.error(f"Pipeline Error: {pipeline_error}")


# ---------------------------------------------------------
# PAGE 1: TICKET TESTING LAB
# ---------------------------------------------------------
if nav_choice == "🎫 Ticket Testing Lab":
    st.markdown("<div class='main-header'>Support Ticket Testing Lab</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Test real-time ticket ingestion, classification, retrieval, routing, answer generation, and guardrails.</div>", unsafe_allow_html=True)

    col_input, col_preset = st.columns([2, 1])

    preset_ticket = None
    with col_preset:
        st.subheader("Load Preset Ticket")
        sample_tickets = []
        video_demo_path = "data/video_demo_tickets.json"
        dev_tickets_path = "FDE_Capstone_Docs/05_Datasets/development_tickets.json"

        if os.path.exists(video_demo_path):
            with open(video_demo_path, "r", encoding="utf-8") as f:
                sample_tickets.extend(json.load(f))
        if os.path.exists(dev_tickets_path):
            with open(dev_tickets_path, "r", encoding="utf-8") as f:
                sample_tickets.extend(json.load(f)[:15])

        if sample_tickets:
            options = ["-- Select Preset --"] + [
                f"{t['ticket_id']} - {t.get('customer_name', 'Customer')} ({t.get('subject') or t.get('body')[:25]})"
                for t in sample_tickets
            ]
            selected_preset_str = st.selectbox("Select Sample Ticket", options=options)
            if selected_preset_str != "-- Select Preset --":
                selected_id = selected_preset_str.split(" - ")[0]
                preset_ticket = next((t for t in sample_tickets if t["ticket_id"] == selected_id), None)

    default_id = preset_ticket["ticket_id"] if preset_ticket else "DEMO-AUTO-001"
    default_channel = preset_ticket["channel"] if preset_ticket else "email"
    default_subject = preset_ticket.get("subject", "") if preset_ticket else "Resolving invalid credential errors on console login"
    default_body = preset_ticket.get("body", "") if preset_ticket else "We are receiving an Invalid Credentials error when attempting to sign in to the CloudServe Management Console. We verified our password is correct. How can we resolve this?"
    default_name = preset_ticket.get("customer_name", "Priya Sharma") if preset_ticket else "Priya Sharma"
    default_cust_id = preset_ticket.get("customer_id", "CUST-1042") if preset_ticket else "CUST-1042"
    default_tier = preset_ticket.get("customer_tier", "enterprise") if preset_ticket else "enterprise"
    default_region = preset_ticket.get("customer_region", "north_america") if preset_ticket else "north_america"
    default_fluency = preset_ticket.get("language_fluency", "fluent") if preset_ticket else "fluent"

    with col_input:
        st.subheader("Ticket Input")
        with st.form("ticket_form"):
            c1, c2 = st.columns(2)
            with c1:
                ticket_id = st.text_input("Ticket ID", value=default_id)
                channel_idx = ["email", "chat", "docs_comment", "forum"].index(default_channel) if default_channel in ["email", "chat", "docs_comment", "forum"] else 0
                channel = st.selectbox("Channel", ["email", "chat", "docs_comment", "forum"], index=channel_idx)
                tier_idx = ["enterprise", "business", "standard"].index(default_tier) if default_tier in ["enterprise", "business", "standard"] else 0
                customer_tier = st.selectbox("Customer Tier", ["enterprise", "business", "standard"], index=tier_idx)
            with c2:
                customer_name = st.text_input("Customer Name", value=default_name)
                region_idx = ["north_america", "europe", "asia_pacific", "latin_america"].index(default_region) if default_region in ["north_america", "europe", "asia_pacific", "latin_america"] else 0
                customer_region = st.selectbox("Region", ["north_america", "europe", "asia_pacific", "latin_america"], index=region_idx)
                fluency_idx = ["fluent", "non_fluent"].index(default_fluency) if default_fluency in ["fluent", "non_fluent"] else 0
                language_fluency = st.selectbox("Language Fluency", ["fluent", "non_fluent"], index=fluency_idx)

            subject = st.text_input("Subject (Optional for chat)", value=default_subject)
            body = st.text_area("Body", value=default_body, height=120)

            submit_btn = st.form_submit_button("🚀 Process Ticket Through Pipeline", type="primary")

    if submit_btn:
        raw_ticket_data = {
            "ticket_id": ticket_id,
            "channel": channel,
            "subject": subject,
            "body": body,
            "received_at": "2026-09-06T12:00:00Z",
            "customer_id": default_cust_id,
            "customer_name": customer_name,
            "customer_tier": customer_tier,
            "customer_region": customer_region,
            "language_fluency": language_fluency
        }

        if pipeline:
            with st.spinner("Processing ticket through LangChain & Gemini pipeline..."):
                try:
                    response = pipeline.process_ticket(raw_ticket_data)
                    st.session_state["pipeline_response"] = response
                    st.session_state["pipeline_raw_ticket"] = raw_ticket_data
                except Exception as ex:
                    st.error(f"Pipeline execution error: {ex}")
        else:
            st.error("Pipeline is not initialized. Please check backend logs or setup.")

    # Render results if available in session state
    if "pipeline_response" in st.session_state and st.session_state["pipeline_response"]:
        response = st.session_state["pipeline_response"]
        raw_ticket_data = st.session_state.get("pipeline_raw_ticket", {})

        st.markdown("---")
        st.subheader("⚡ Processing Pipeline Execution Results")

        # Overview Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            action_color = "badge-auto" if response.action_taken == "auto_respond" else ("badge-escalate" if response.action_taken == "escalate" else "badge-blocked")
            st.markdown(f"**Action Taken**<br><span class='{action_color}'>{response.action_taken.upper()}</span>", unsafe_allow_html=True)
        with m2:
            st.metric("Predicted Intent", response.intent)
        with m3:
            st.metric("Confidence Score", f"{response.confidence:.2f}")
        with m4:
            st.metric("Urgency", response.urgency.upper())

        # Detailed Tabs
        t_resp, t_ret, t_guard, t_log = st.tabs(["💬 Response & Routing", "📚 FAISS Retrieved Docs", "🛡️ Guardrails Check", "📜 Audit Log Entry"])

        with t_resp:
            if response.action_taken == "auto_respond":
                st.success("✅ **Automated Answer Generated & Grounded**")
                st.write(response.answer)
                st.markdown(f"**Cited Document IDs:** `{', '.join(response.cited_doc_ids)}`")
            elif response.action_taken == "escalate":
                st.warning("⚠️ **Ticket Escalated to Human Support Queue**")
                st.markdown(f"**Escalation Reason:** {response.escalation_reason}")
                if response.cited_doc_ids:
                    st.markdown(f"**Attached Context Docs:** `{', '.join(response.cited_doc_ids)}`")
            else:
                st.error("🚨 **Response BLOCKED by Safety Guardrails**")
                st.markdown(f"**Block Reason:** {response.escalation_reason}")

        with t_ret:
            st.markdown("### Passages Retrieved from `documentation.json`")
            norm_t = normalise_ticket(raw_ticket_data)
            query = f"{response.intent} {norm_t.subject} {norm_t.body[:150]}"
            if pipeline:
                passages = pipeline.retriever.search(query=query, top_k=3)

                if passages:
                    for idx, p in enumerate(passages, 1):
                        with st.expander(f"Passage {idx}: [{p.doc_id}] {p.title} (Score: {p.score})"):
                            st.markdown(f"**Category:** `{p.category}`")
                            st.text(p.content)
                else:
                    st.info("No matching passages retrieved.")

        with t_guard:
            st.markdown("### Guardrails Execution Results")
            if response.guardrail_result:
                gr = response.guardrail_result
                g1, g2 = st.columns(2)
                with g1:
                    st.write(f"**Status:** {'✅ Passed' if gr.passed else '❌ Blocked'}")
                    st.write(f"**PII Detected:** {'YES' if gr.pii_detected else 'NO'}")
                with g2:
                    st.write(f"**Unsupported Claims:** {'YES' if gr.unsupported_claims_detected else 'NO'}")
                if gr.reasons:
                    st.markdown("**Logs / Warnings:**")
                    for r in gr.reasons:
                        st.write(f"- {r}")
            else:
                st.write("Guardrails bypassed due to early escalation.")

        with t_log:
            st.markdown("### Decision Log Reconciliation")
            st.write(f"**Decision ID:** `{response.decision_id}`")
            st.json({
                "ticket_id": response.ticket_id,
                "action_taken": response.action_taken,
                "confidence": response.confidence,
                "intent": response.intent,
                "cited_docs": response.cited_doc_ids,
                "escalation_reason": response.escalation_reason
            })


# ---------------------------------------------------------
# PAGE 2: DECISION AUDIT LOGS
# ---------------------------------------------------------
elif nav_choice == "📊 Decision Audit Logs":
    st.markdown("<div class='main-header'>SQLite Decision Audit Log</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Reconcile and inspect decision records stored in <code>storage/decisions.db</code>.</div>", unsafe_allow_html=True)

    if pipeline:
        db_path = pipeline.logger.db_path
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM decisions ORDER BY created_at DESC", conn)
            conn.close()

            if not df.empty:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Total Logged Decisions", len(df))
                with c2:
                    auto_count = len(df[df["action_taken"] == "auto_respond"])
                    st.metric("Auto Responses", auto_count)
                with c3:
                    esc_count = len(df[df["action_taken"] == "escalate"])
                    st.metric("Escalations", esc_count)

                st.markdown("---")
                action_filter = st.multiselect("Filter by Action", options=df["action_taken"].unique(), default=df["action_taken"].unique())
                filtered_df = df[df["action_taken"].isin(action_filter)]

                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No decision records in database yet. Process a ticket to populate.")
        else:
            st.warning("Database file not created yet.")


# ---------------------------------------------------------
# PAGE 3: METRICS & EVALUATION
# ---------------------------------------------------------
elif nav_choice == "📈 Metrics & Evaluation":
    st.markdown("<div class='main-header'>Evaluation Metrics & Performance</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Results generated from the unattended evaluation harness.</div>", unsafe_allow_html=True)

    metrics_path = "evaluation/results/metrics_report.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        st.caption(f"Last Evaluation Run: {data.get('timestamp')}")

        st.subheader("Business Impact")
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.metric("First Contact Resolution", f"{data['business']['first_contact_resolution_pct']}%", help="Target: >=65%")
        with b2:
            st.metric("Escalation Rate", f"{data['business']['escalation_rate_pct']}%", help="Target: <=30%")
        with b3:
            st.metric("Mean Latency", f"{data['business']['mean_response_time_seconds']}s")
        with b4:
            st.metric("P95 Latency", f"{data['business']['p95_response_time_seconds']}s", help="Target: <3.0s")

        st.subheader("Technical Performance")
        t1, t2, t3 = st.columns(3)
        with t1:
            st.metric("Intent Classification Accuracy", f"{data['technical']['intent_classification_accuracy_pct']}%")
        with t2:
            st.metric("Citation Accuracy", f"{data['technical']['citation_accuracy_pct']}%")
        with t3:
            st.metric("Mean Confidence Score", f"{data['technical']['mean_confidence_score']}")

        st.subheader("Governance Summary")
        st.json(data["governance"])
    else:
        st.info("No evaluation report found. Run `python -m evaluation.harness --input FDE_Capstone_Docs/05_Datasets/validation_tickets.json --output evaluation/results/` first.")


# ---------------------------------------------------------
# PAGE 4: GOVERNANCE & KILL SWITCH
# ---------------------------------------------------------
elif nav_choice == "🛡️ Governance & Kill Switch":
    st.markdown("<div class='main-header'>Governance & Emergency Controls</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>System safety controls, risk management, and kill switch procedures.</div>", unsafe_allow_html=True)

    st.subheader("System Kill Switch")
    st.write("Activating the Kill Switch immediately routes **100% of incoming tickets** to human support queues with context attached.")

    current_ks = os.getenv("KILL_SWITCH_ACTIVE", "false").lower() == "true"
    new_ks = st.toggle("ACTIVATE KILL SWITCH", value=current_ks)

    if new_ks != current_ks:
        os.environ["KILL_SWITCH_ACTIVE"] = "true" if new_ks else "false"
        st.success(f"Kill Switch updated to: {os.environ['KILL_SWITCH_ACTIVE']}")
        st.rerun()

    st.markdown("---")
    st.subheader("Risk Register Summary")
    st.markdown("""
    - **R-01 Private Data Leakage:** Intercepted by regex guardrails in `src/guardrails.py` (0 tolerance).
    - **R-02 Hallucinated Claims:** Grounded RAG + citation checking.
    - **R-03 Sensitive Disputes:** Forced escalation rules for billing, security, and account cancellations.
    """)
