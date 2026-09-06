"""
SQLite Decision Audit Log Store.
Satisfies Acceptance Criterion A8.
"""
import os
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class DecisionLogger:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.getenv("DATABASE_URL", "sqlite:///./storage/decisions.db").replace("sqlite:///", "")

        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id     TEXT PRIMARY KEY,
                    created_at      TEXT NOT NULL,
                    ticket_id       TEXT NOT NULL,
                    channel         TEXT NOT NULL,
                    customer_tier   TEXT NOT NULL,
                    stage           TEXT NOT NULL,
                    prediction      TEXT,
                    confidence      REAL,
                    threshold       REAL,
                    action_taken    TEXT NOT NULL,
                    reason          TEXT NOT NULL,
                    sources_used    TEXT,
                    guardrails      TEXT,
                    prompt_version  TEXT,
                    requirement_ids TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()


    def log_decision(
        self,
        ticket_id: str,
        channel: str,
        customer_tier: str,
        stage: str,
        prediction: str,
        confidence: float,
        threshold: float,
        action_taken: str,
        reason: str,
        sources_used: Optional[list] = None,
        guardrails: Optional[Dict[str, Any]] = None,
        prompt_version: str = "v1.0",
        requirement_ids: str = "FR-2,FR-4,FR-7"
    ) -> str:
        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.utcnow().isoformat() + "Z"

        sources_json = json.dumps(sources_used if sources_used else [])
        guardrails_json = json.dumps(guardrails if guardrails else {})

        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO decisions (
                    decision_id, created_at, ticket_id, channel, customer_tier,
                    stage, prediction, confidence, threshold, action_taken, reason,
                    sources_used, guardrails, prompt_version, requirement_ids
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id, created_at, ticket_id, channel, customer_tier,
                    stage, prediction, confidence, threshold, action_taken, reason,
                    sources_json, guardrails_json, prompt_version, requirement_ids
                )
            )
            conn.commit()
        finally:
            conn.close()

        return decision_id

    def get_decision_count(self) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM decisions")
            count = cursor.fetchone()[0]
            return count
        finally:
            conn.close()

