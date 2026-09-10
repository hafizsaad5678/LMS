import logging
import os
import re

from ..rag.utils import get_or_load_vector_store, normalize_similarity_score
from ..config import (
    CHAT_MIN_SIMILARITY_SCORE,
    CHAT_TOP_K,
    FAISS_INDEX_DIR,
    RETRIEVAL_SHORT_QUERY_LEN_FOR_THRESHOLD,
    RETRIEVAL_SHORT_QUERY_LEN_FOR_TOP_K,
    RETRIEVAL_SHORT_QUERY_MIN_SCORE,
    RETRIEVAL_SHORT_QUERY_TOP_K,
    RETRIEVAL_SCORE_ROUND_DIGITS,
    RETRIEVAL_CONFIDENCE_ROUNDED,
)
from ...models.chatbot import UploadedFile
from ..utils import compact_text

logger = logging.getLogger(__name__)


def _retrieval_policy(question: str) -> tuple[int, float]:
    """Centralized retriever policy for top-k and min score by query length."""
    q_len = len((question or "").strip())
    top_k = CHAT_TOP_K
    min_score = CHAT_MIN_SIMILARITY_SCORE

    if q_len < RETRIEVAL_SHORT_QUERY_LEN_FOR_TOP_K:
        top_k = RETRIEVAL_SHORT_QUERY_TOP_K
    if q_len < RETRIEVAL_SHORT_QUERY_LEN_FOR_THRESHOLD:
        min_score = RETRIEVAL_SHORT_QUERY_MIN_SCORE

    return top_k, min_score


def _get_active_file_names(user_id: int, session_id: str | None = None) -> list[str]:
    """Retrieve active or most recently indexed filenames for the user to prioritize retrieval."""
    try:
        qs = UploadedFile.objects.filter(
            user_id=user_id,
            index_status=UploadedFile.IndexStatus.INDEXED
        ).order_by('-created_at')
        
        filenames = [f.filename for f in qs[:3]]
        return filenames
    except Exception as e:
        logger.debug("Failed getting active file names: %s", e)
        return []


def query_documents(user_id, question, session_id=None):
    """
    Searches the user’s uploaded documents for an answer.
    Prioritizes the active/latest uploaded document and ensures diversity across documents.
    """
    index_dir = os.path.join(FAISS_INDEX_DIR, f'user_docs_lc_{user_id}')
    
    # Try to load existing user index
    if not os.path.exists(os.path.join(index_dir, "index.faiss")):
        return {"status": "no_index", "results": []}
        
    try:
        vector_store = get_or_load_vector_store(index_dir)
        if vector_store is None:
            return {"status": "no_index", "results": []}
        
        k_val, current_threshold = _retrieval_policy(question)
        compact_question = compact_text(question).strip("?")

        filtered_results = []
        confidence_scores = []
        seen_texts = set()

        # 1. Exact string match across ALL chunks (bypassing embeddings)
        if compact_question and len(compact_question) >= 2:
            try:
                if hasattr(vector_store, "docstore") and hasattr(vector_store.docstore, "_dict"):
                    for doc_id, doc in vector_store.docstore._dict.items():
                        doc_text = doc.page_content or ""
                        if compact_question in compact_text(doc_text):
                            if doc_text not in seen_texts:
                                seen_texts.add(doc_text)
                                filtered_results.append({
                                    "text": doc_text,
                                    "score": 1.0,
                                    "file_name": doc.metadata.get("original_filename") or doc.metadata.get("source") or "Uploaded File",
                                    "page": doc.metadata.get("page_number") if doc.metadata.get("page_number") is not None else "N/A"
                                })
                                confidence_scores.append(1.0)
            except Exception as e:
                logger.error("Exact match scan failed: %s", e)

        # 2. Similarity search with a wider candidate pool to avoid single-doc dominance
        candidate_k = max(k_val * 4, 30)
        raw_results = vector_store.similarity_search_with_score(question, k=candidate_k)

        # Find latest/active file to boost relevance if asking about "document" / "file"
        active_filenames = _get_active_file_names(user_id, session_id)
        latest_filename = active_filenames[0] if active_filenames else None

        # Group candidate chunks by document
        by_doc: dict[str, list[tuple[any, float]]] = {}
        for doc, score in raw_results:
            doc_text = (doc.page_content or "").strip()
            if not doc_text or doc_text in seen_texts:
                continue

            norm_score = normalize_similarity_score(score)
            doc_file = doc.metadata.get("original_filename") or doc.metadata.get("source") or "Uploaded File"
            doc_session = doc.metadata.get("session_id")

            # Boost active / recently uploaded document
            if session_id and doc_session and str(doc_session) == str(session_id):
                norm_score = min(1.0, norm_score * 1.4 + 0.1)
            elif latest_filename and doc_file == latest_filename:
                norm_score = min(1.0, norm_score * 1.35 + 0.05)

            by_doc.setdefault(doc_file, []).append((doc, norm_score))

        # Collect top chunks with document diversity (max 4 chunks per doc in preliminary pool)
        candidates = []
        for doc_file, hits in by_doc.items():
            hits.sort(key=lambda x: x[1], reverse=True)
            for doc, norm_score in hits[:4]:
                candidates.append((doc, norm_score))

        # Sort combined candidates by final score descending
        candidates.sort(key=lambda x: x[1], reverse=True)

        for doc, norm_score in candidates:
            doc_text = doc.page_content or ""
            if doc_text in seen_texts:
                continue

            is_exact_text_match = bool(compact_question and compact_question in compact_text(doc_text))
            if norm_score >= current_threshold or is_exact_text_match:
                seen_texts.add(doc_text)
                confidence_scores.append(norm_score)
                filtered_results.append({
                    "text": doc_text,
                    "score": round(norm_score, RETRIEVAL_SCORE_ROUND_DIGITS),
                    "file_name": doc.metadata.get("original_filename") or doc.metadata.get("source") or "Uploaded File",
                    "page": doc.metadata.get("page_number") if doc.metadata.get("page_number") is not None else "N/A"
                })

        # Cap results to top-k
        filtered_results = filtered_results[:CHAT_TOP_K]

        # If no chunks passed threshold, take top candidates
        if not filtered_results and candidates:
            for doc, norm_score in candidates[:CHAT_TOP_K]:
                doc_text = doc.page_content or ""
                if doc_text.strip() and doc_text not in seen_texts:
                    seen_texts.add(doc_text)
                    boosted_score = max(norm_score, 0.5)
                    confidence_scores.append(boosted_score)
                    filtered_results.append({
                        "text": doc_text,
                        "score": round(boosted_score, RETRIEVAL_SCORE_ROUND_DIGITS),
                        "file_name": doc.metadata.get("original_filename") or doc.metadata.get("source") or "Uploaded File",
                        "page": doc.metadata.get("page_number") if doc.metadata.get("page_number") is not None else "N/A"
                    })

        if not confidence_scores:
            confidence_value = 0.0
        elif RETRIEVAL_CONFIDENCE_ROUNDED:
            confidence_value = max(item["score"] for item in filtered_results)
        else:
            confidence_value = max(confidence_scores)
        
        return {
            "status": "success",
            "results": filtered_results,
            "confidence": confidence_value,
        }
    except Exception as e:
        logger.error("Document search failed: %s", e)
        return {"status": "error", "message": str(e), "results": []}


