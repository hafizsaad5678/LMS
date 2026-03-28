"""RAG (document retrieval) utilities."""

from .utils import (
    build_vector_store,
    get_embeddings,
    get_faiss_cls,
    get_or_load_vector_store,
    invalidate_user_docs_vector_store,
    invalidate_vector_store,
    load_vector_store,
    normalize_similarity_score,
    process_and_index_document,
    process_document_to_chunks,
)

__all__ = [
    "get_embeddings",
    "get_faiss_cls",
    "process_document_to_chunks",
    "build_vector_store",
    "load_vector_store",
    "get_or_load_vector_store",
    "invalidate_vector_store",
    "invalidate_user_docs_vector_store",
    "normalize_similarity_score",
    "process_and_index_document",
]
