# CloudServe Prompt Register

This directory contains version-controlled system prompts for the CloudServe Intelligent Support System.

| Prompt File | Purpose | Version | Target Component |
| :--- | :--- | :--- | :--- |
| `build/classifier_v1.prompt` | Structured JSON intent & urgency classification | 1.0 | `src/classify.py` |
| `build/generator_v1.prompt` | Grounded RAG answer generation with citations | 1.0 | `src/generate.py` |
| `build/guardrail_evaluator_v1.prompt` | LLM-as-a-judge claim grounding validator | 1.0 | `src/guardrails.py` |
