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
import os
import logging


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

def query_documents(user_id, question):
    """
    Searches the user’s uploaded documents for an answer.
    Returns chunks with context and confidence.
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
        
        # Search with similarity score
        results = vector_store.similarity_search_with_score(question, k=k_val)
        
        filtered_results = []
        confidence_scores = []
        
        for doc, score in results:
            # Normalize and check threshold
            norm_score = normalize_similarity_score(score)
            if norm_score >= current_threshold:
                confidence_scores.append(norm_score)
                # Meta usually contains doc_id and chunk_id for citations
                filtered_results.append({
                    "text": doc.page_content,
                    "score": round(norm_score, RETRIEVAL_SCORE_ROUND_DIGITS),
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
