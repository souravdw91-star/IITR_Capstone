"""
Test runner script executing all unit and integration tests.
Usage: python run_tests.py
"""
import sys
import unittest

from tests.test_ingest import test_ingest_all_four_channels
from tests.test_classify import test_classification_output
from tests.test_retrieve import test_faiss_retrieval
from tests.test_route import test_routing_mandatory_escalation, test_routing_auto_respond
from tests.test_guardrails import test_guardrail_pii_blocking, test_guardrail_unsupported_claim_blocking
from tests.test_pipeline import test_pipeline_execution


def run_all_tests():
    tests = [
        ("Ingestion (A2)", test_ingest_all_four_channels),
        ("Classification (A3)", test_classification_output),
        ("FAISS Retrieval (A4)", test_faiss_retrieval),
        ("Routing Mandatory Escalation (A5)", test_routing_mandatory_escalation),
        ("Routing Auto Respond (A5)", test_routing_auto_respond),
        ("Guardrails PII Blocking (A7)", test_guardrail_pii_blocking),
        ("Guardrails Unsupported Claim (A7)", test_guardrail_unsupported_claim_blocking),
        ("Pipeline & Decision Log (A1-A8)", test_pipeline_execution),
    ]

    passed = 0
    failed = 0

    print("=== Running CloudServe Support System Test Suite ===")
    for name, test_func in tests:
        try:
            test_func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print(f"\nTest Summary: {passed} PASSED, {failed} FAILED.")
    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
