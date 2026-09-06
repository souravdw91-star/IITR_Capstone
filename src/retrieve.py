"""
FAISS Vector Store Document Retrieval Module.
Satisfies Acceptance Criterion A4.
"""
import os
import json
from typing import List, Optional
from dotenv import load_dotenv

import os
import json
import re
from typing import List, Optional
from dotenv import load_dotenv

from src.schemas import RetrievalPassage

load_dotenv()

# Robust imports for LangChain / FAISS text splitting and retrieval
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        class RecursiveCharacterTextSplitter:
            def __init__(self, chunk_size=600, chunk_overlap=100):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap

            def split_text(self, text: str) -> List[str]:
                chunks = []
                start = 0
                while start < len(text):
                    end = start + self.chunk_size
                    chunks.append(text[start:end])
                    start = end - self.chunk_overlap
                return chunks



# Robust FAISS and Embeddings import
try:
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    FAISS = None
    HuggingFaceEmbeddings = None


class DocumentationRetriever:
    def __init__(
        self,
        docs_path: str = "FDE_Capstone_Docs/05_Datasets/documentation.json",
        index_dir: str = "./storage/faiss_index"
    ):
        self.docs_path = docs_path
        self.index_dir = index_dir
        self.vector_store: Optional[Any] = None
        self.documents_raw = []

        if HAS_FAISS:
            try:
                self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                self._initialize_vector_store()
            except Exception as e:
                print(f"FAISS initialization fallback: {e}")
                self._initialize_raw_docs()
        else:
            self._initialize_raw_docs()

    def _initialize_raw_docs(self) -> None:
        """Fallback raw document indexing."""
        if os.path.exists(self.docs_path):
            with open(self.docs_path, "r", encoding="utf-8") as f:
                self.documents_raw = json.load(f)

    def _initialize_vector_store(self) -> None:
        """Loads FAISS index from storage or builds it from documentation.json."""
        if os.path.exists(self.index_dir) and os.path.exists(os.path.join(self.index_dir, "index.faiss")):
            try:
                self.vector_store = FAISS.load_local(
                    self.index_dir,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return
            except Exception as e:
                print(f"Loading FAISS index failed, re-building index: {e}")

        # Build index from docs_path
        if not os.path.exists(self.docs_path):
            print(f"Warning: Documentation file not found at {self.docs_path}")
            return

        with open(self.docs_path, "r", encoding="utf-8") as f:
            documents = json.load(f)
            self.documents_raw = documents

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100
        )

        texts = []
        metadatas = []

        for doc in documents:
            doc_id = doc.get("doc_id", doc.get("id", "DOC-000"))
            title = doc.get("title", "Untitled Document")
            category = doc.get("category", "general")
            content = doc.get("content", "")

            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append({
                    "doc_id": doc_id,
                    "title": title,
                    "category": category,
                    "full_content": content
                })

        if texts:
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            os.makedirs(self.index_dir, exist_ok=True)
            self.vector_store.save_local(self.index_dir)

    def search(self, query: str, top_k: int = 3, score_threshold: float = 0.35) -> List[RetrievalPassage]:
        """
        Searches FAISS vector store for passages relevant to query.
        Returns ranked RetrievalPassage list.
        """
        if self.vector_store:
            try:
                results = self.vector_store.similarity_search_with_score(query, k=top_k)
                passages = []

                for doc, score in results:
                    norm_score = max(0.0, 1.0 - (score / 2.0))
                    if norm_score >= score_threshold:
                        passages.append(RetrievalPassage(
                            doc_id=doc.metadata.get("doc_id", "DOC-UNKNOWN"),
                            title=doc.metadata.get("title", ""),
                            category=doc.metadata.get("category", ""),
                            content=doc.page_content,
                            score=round(norm_score, 4)
                        ))
                if passages:
                    return passages
            except Exception as e:
                print(f"Retrieval error: {e}")

        # Fallback text search
        if not self.documents_raw and os.path.exists(self.docs_path):
            self._initialize_raw_docs()

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        scored_docs = []

        for doc in self.documents_raw:
            doc_id = doc.get("doc_id", doc.get("id", "DOC-000"))
            content = doc.get("content", "")
            title = doc.get("title", "")
            category = doc.get("category", "")

            matches = sum(1 for term in query_terms if term in content.lower() or term in title.lower())
            if matches > 0:
                score = round(min(0.95, 0.40 + (matches * 0.15)), 4)
                scored_docs.append((score, RetrievalPassage(
                    doc_id=doc_id,
                    title=title,
                    category=category,
                    content=content[:500],
                    score=score
                )))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_docs[:top_k]]

