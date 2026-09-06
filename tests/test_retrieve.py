"""
Unit tests for FAISS vector search document retrieval.
Satisfies Acceptance Criterion A4.
"""
from src.retrieve import DocumentationRetriever


def test_faiss_retrieval():
    retriever = DocumentationRetriever()
    results = retriever.search("invalid credential login error", top_k=2)

    assert len(results) > 0
    top_doc = results[0]
    assert top_doc.doc_id.startswith("DOC-")
    assert len(top_doc.content) > 0
    assert top_doc.score > 0.0
