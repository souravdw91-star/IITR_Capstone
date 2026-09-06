"""
FastAPI Server for CloudServe Support Engine.
Exposes endpoints for ticket ingestion, processing, health, and Prometheus metrics.
"""
import os
import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app
from dotenv import load_dotenv

from src.schemas import OutboundResponse
from src.pipeline import SupportPipeline

load_dotenv()

app = FastAPI(
    title="CloudServe Support Automation Engine API",
    version="1.0.0",
    description="Intelligent Customer Support Engine powered by LangChain, FAISS, LangSmith, and Google Gemini."
)

# Prometheus Metrics Definition
TICKETS_COUNTER = Counter(
    "tickets_processed_total",
    "Total tickets processed",
    ["channel", "outcome"]
)
RESPONSE_LATENCY = Histogram(
    "response_seconds",
    "End to end pipeline response time in seconds"
)
GUARDRAIL_BLOCKS = Counter(
    "guardrail_blocks_total",
    "Total responses blocked by safety guardrails",
    ["type"]
)

# Mount Prometheus metrics endpoint at /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Pipeline instance
pipeline = SupportPipeline()


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CloudServe Support System",
        "kill_switch_active": os.getenv("KILL_SWITCH_ACTIVE", "false")
    }


@app.post("/process-ticket", response_model=OutboundResponse)
def process_ticket(ticket_data: Dict[str, Any]):
    start_time = time.time()
    try:
        response = pipeline.process_ticket(ticket_data)
        elapsed = time.time() - start_time

        RESPONSE_LATENCY.observe(elapsed)
        channel = ticket_data.get("channel", "unknown")
        TICKETS_COUNTER.labels(channel=channel, outcome=response.action_taken).inc()

        if response.action_taken == "blocked":
            GUARDRAIL_BLOCKS.labels(type="pii_or_unsupported").inc()

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kill-switch")
def toggle_kill_switch(active: bool):
    os.environ["KILL_SWITCH_ACTIVE"] = "true" if active else "false"
    return {"kill_switch_active": os.environ["KILL_SWITCH_ACTIVE"]}
