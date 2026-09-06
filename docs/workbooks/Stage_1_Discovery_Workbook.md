# Stage 1 — Discovery Workbook

**Client:** CloudServe Solutions  
**Author:** Forward Deployed AI Engineer  
**Date:** September 2026  

---

## 1. Stakeholder Interview Findings

| Stakeholder | Key Insights & Pain Points | Quote / Evidence |
| :--- | :--- | :--- |
| **Head of Support** | Support queue is overwhelmed (>500 tickets/week). First reply takes 8-12 hours vs. 2-hr SLA target. CSAT dropped to 3.2/5. Staff attrition is rising due to burnout. | *"We are drowning. Half our senior engineers' time is spent re-answering basic setup questions."* |
| **Tier 1 Support Agent** | High ticket volume consists of repetitive documentation lookups. Agents waste time switching tabs to copy-paste links. Live chat users abandon queue quickly. | *"80% of what I answer is in DOC-AUTH-001 or DOC-DEP-002, but customers don't read docs."* |
| **Tier 2 Senior Engineer** | Interrupted constantly by poorly escalated tickets lacking context, log snippets, or basic troubleshooting steps already attempted. | *"Tickets get tossed over the wall with zero context. I have to restart discovery from scratch."* |
| **Technical Writer** | Documentation is comprehensive across 29 articles (8 categories), but customers struggle with search keywords and non-fluent language barriers. | *"The information is all there, but if customers search 'login broken' instead of 'credential resolution', they miss it."* |
| **Corporate Customer** | Frustrated by long wait times for standard configuration issues and unhelpful template responses. | *"We waited 10 hours for a 2-line API key fix. That almost made us cancel our renewal."* |

---

## 2. Ticket Data Analysis Summary

- **Total Development Tickets Analyzed:** 500
- **Answerable from Documentation:** ~75% (374 / 500 tickets)
- **Language Fluency Distribution:** 25% Non-Fluent customers, requiring clear, direct language without complex jargon.
- **Channel Breakdown:**
  - **Email:** Long, unstructured tickets, higher complexity.
  - **Live Chat:** Fast expectation, short queries, high drop-off risk.
  - **Docs Comment:** Narrow, specific technical questions.
  - **Forum:** Community pre-existing context; support arrives mid-thread.
- **Intent Classes (22 Categories):** Includes `authentication_failure`, `rate_limit`, `deployment_timeout`, `billing_dispute`, `feature_request`, `unclear_request`, etc.
- **Critical Safety Intent:** `billing_dispute`, `security_vulnerability`, `account_cancellation` carry `must_not_auto_respond = True` and MUST escalate.

---

## 3. Problem Statement

> **CloudServe Solutions' support team is failing SLA targets (8-12 hr reply vs 2 hr SLA) and customer satisfaction (3.2/5) not due to a lack of documentation, but because incoming customer tickets across 4 channels are not automatically resolved using existing knowledge base content, while complex tickets escalate without diagnostic context.**
> 
> **Solution Required:** An intelligent customer support automation and escalation system powered by **LangChain**, **FAISS**, **LangSmith**, and **Google Gemini** that automatically answers document-grounded tickets with precise citations (`FCR >= 65%`, `Response Time < 5 mins`) while deterministically routing complex/sensitive cases to human agents with pre-filled context and diagnostic summaries.
