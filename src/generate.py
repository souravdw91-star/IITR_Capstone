"""
RAG Response Generation Module using LangChain and Google Gemini.
Satisfies Acceptance Criterion A6 and A11.
"""
import os
import json
import re
from typing import List, Tuple
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from src.schemas import NormalisedTicket, RetrievalPassage

load_dotenv()


def rule_based_fallback_generate(
    ticket: NormalisedTicket,
    passages: List[RetrievalPassage]
) -> Tuple[str, List[str]]:
    """Grounded fallback generator used when LLM is unavailable."""
    if not passages:
        return (
            "I do not have sufficient information in our documentation to resolve this specific issue.",
            []
        )

    doc_ids = list(set(p.doc_id for p in passages))
    primary_doc = passages[0]

    # Clean excerpt from primary document content
    content_snippet = primary_doc.content.strip().split("\n\n")[0]
    if len(content_snippet) > 300:
        content_snippet = content_snippet[:300] + "..."

    answer = (
        f"Hello {ticket.customer_name},\n\n"
        f"Thank you for contacting CloudServe support regarding '{ticket.subject}'.\n\n"
        f"Based on our documentation [{primary_doc.doc_id}], here are the steps to resolve your issue:\n"
        f"{content_snippet} [{primary_doc.doc_id}]\n\n"
        f"If you require further assistance, please let us know."
    )

    return answer, doc_ids


class ResponseGenerator:
    def __init__(self):
        raw_key = os.getenv("GOOGLE_API_KEY", "")
        self.api_key = raw_key.strip("'\" ") if raw_key else None
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        self.llm = None


        if self.api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.1
                )
            except Exception as e:
                print(f"Warning: Failed to initialize ChatGoogleGenerativeAI generator: {e}")

        # Load prompt template
        prompt_path = os.path.join("prompts", "build", "generator_v1.prompt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt_template_str = f.read()
        else:
            self.prompt_template_str = "Generate grounded response for ticket {subject}: {body}. Passages: {retrieved_context}"

        self.prompt = PromptTemplate.from_template(self.prompt_template_str)

    def generate(
        self,
        ticket: NormalisedTicket,
        passages: List[RetrievalPassage]
    ) -> Tuple[str, List[str]]:
        """
        Generates a customer answer grounded in retrieved passages with bracketed citations [DOC-XXX-YYY].
        Returns (answer_text, cited_doc_ids).
        """
        if not passages:
            return (
                "I do not have sufficient information in our documentation to resolve this specific issue.",
                []
            )

        if not self.llm:
            return rule_based_fallback_generate(ticket, passages)

        # Format context passages
        formatted_context_list = []
        for p in passages:
            formatted_context_list.append(f"--- Document ID: {p.doc_id} (Title: {p.title}) ---\n{p.content}")
        retrieved_context = "\n\n".join(formatted_context_list)

        try:
            prompt_value = self.prompt.format(
                channel=ticket.channel,
                customer_name=ticket.customer_name,
                subject=ticket.subject,
                body=ticket.body,
                retrieved_context=retrieved_context
            )
            response = self.llm.invoke(prompt_value)
            content = response.content

            # Parse JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                answer = data.get("answer", "")
                cited = data.get("cited_doc_ids", [])
                if answer:
                    return answer, cited

            # Fallback text extract
            return content.strip(), [p.doc_id for p in passages]

        except Exception as e:
            print(f"Generation API error (falling back): {e}")

        return rule_based_fallback_generate(ticket, passages)
