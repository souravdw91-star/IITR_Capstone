# Stage 5 — PRD Revision Log

**Document Control:**  
- **Initial Version:** 1.0 (End of Week 1)  
- **Revised Version:** 1.1 (Mid Week 2 - Post Initial Build & Validation)  

---

## Log of Requirements Changes

| Change ID | Original Requirement | Revised Requirement | Rationale / Discovery Evidence |
| :--- | :--- | :--- | :--- |
| **REV-01** | FR-4: Fixed Routing Threshold ($0.85$). | FR-4: Calibrated Routing Threshold ($0.80$) + Safety Override Rule. | Initial testing showed $0.85$ caused an unnecessarily high escalation rate ($48\%$). Lowering to $0.80$ balanced auto-response ($FCR = 68\%$) while maintaining high precision. |
| **REV-02** | FR-5: Single document citation requirement. | FR-5: Multi-passage chunk citations with exact `doc_id` tags. | Technical documentation articles contained multi-step guides spanning multiple sections. Including exact passage chunk context improved answer clarity. |
| **REV-03** | FR-6: Warning log on PII detection. | FR-6: Hard blocking (`block_response=True`) on PII detection. | Warning-only guardrails allowed sensitive customer data (tokens, emails) to leak into automated outputs. Hard blocking ensures zero tolerance (NFR-3). |

---

## Reflection

Key lesson learned during contact with real data:
> *Routing thresholds cannot be guessed in isolation. A threshold set too high neutralizes automation benefits, while a threshold set too low risks customer dissatisfaction. Deterministic safety rules (`must_not_auto_respond`) combined with empirical confidence thresholds provide the safest operational boundary.*
