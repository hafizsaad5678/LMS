import hashlib
import json
import logging
import os
import re
import time

from django.core.cache import cache
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ..config import (
    CHAT_CACHE_TTL_SECONDS,
    CHAT_GREETING_KEYWORDS,
    CHAT_GREETING_RESPONSE,
    CHAT_SERVICE_VERSION,
    RAG_CONFIDENCE_SWITCH_THRESHOLD,
    RAG_MAX_CONTEXT_CHARS,
    SOURCE_LABEL_DOC_PREFIX,
    SOURCE_LABEL_LLM_FALLBACK,
    SOURCE_LABEL_LLM_GENERAL,
)
from ..llm.provider import call_llm, get_chat_model, stream_llm
from ..llm.prompts import CHATBOT_SYSTEM_PROMPT, RAG_DOC_ANSWER_PROMPT
from ..tools.docs import query_documents
from ..utils import compact_text, get_doc_mode_cache_key

logger = logging.getLogger(__name__)
logger.debug("Loaded chatbot service %s", CHAT_SERVICE_VERSION)


def _is_greeting(query: str) -> bool:
    cleaned = (query or "").strip().lower()
    if not cleaned:
        return False
    compact = compact_text(cleaned)
    return any(compact == compact_text(item) for item in CHAT_GREETING_KEYWORDS)


def _extract_exact_line_answer(question: str, results: list[dict]) -> str:
    """Prefer exact line matches for symbolic/equation-style queries ONLY."""
    # Only apply this extreme bypass for very short mathematical or symbolic expressions
    is_symbolic = bool(re.search(r"^[a-zA-Z0-9\s=+\-*/^.?]+$", question.strip())) and "=" in question and len(question.strip()) <= 30
    if not is_symbolic:
        return ""

    q = compact_text(question).strip("?")
    if not q or len(q) < 2:
        return ""
    
    for r in results:
        text = r.get("text") or ""
        for line in text.splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            
            compact_candidate = compact_text(candidate)
            if q in compact_candidate:
                if len(candidate) < 100:
                    return candidate
    return ""


def _build_rag_context(results: list[dict]) -> str:
    seen_texts = set()
    context_parts = []
    current_chars = 0

    for r in results:
        text = r.get("text") or ""
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)
        chunk_str = f"- {text} (Source: {r.get('file_name', 'Uploaded File')}, Page: {r.get('page', 'N/A')})"
        if current_chars + len(chunk_str) > RAG_MAX_CONTEXT_CHARS:
            break
        context_parts.append(chunk_str)
        current_chars += len(chunk_str)

    return "\n".join(context_parts)


def _query_terms(question: str) -> set[str]:
    normalized = re.sub(r"[^a-z0-9\s]", " ", (question or "").lower())
    return {tok for tok in normalized.split() if len(tok) >= 3}


def _has_contextual_overlap(question: str, results: list[dict], min_overlap_ratio: float = 0.2) -> bool:
    """Guardrail to avoid forcing RAG when retrieved chunks are semantically weak for the query."""
    terms = _query_terms(question)
    if not terms:
        return True

    for item in results:
        text = item.get("text") or ""
        normalized_text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
        text_terms = {tok for tok in normalized_text.split() if len(tok) >= 3}
        if not text_terms:
            continue
        overlap = len(terms & text_terms) / max(1, len(terms))
        if overlap >= min_overlap_ratio:
            return True
    return False


def _general_fallback_response(query: str, history=None, confidence: float = 0.0) -> dict:
    llm_ans = call_llm(query, history=history or [], system_prompt=CHATBOT_SYSTEM_PROMPT)
    return {
        "text": llm_ans,
        "source": SOURCE_LABEL_LLM_GENERAL,
        "confidence": confidence,
    }


def _stream_rag_answer(context: str, question: str):
    prompt = ChatPromptTemplate.from_template(RAG_DOC_ANSWER_PROMPT)
    chain = prompt | get_chat_model() | StrOutputParser()
    yield from chain.stream({"context": context, "question": question})


def _has_user_document_index(user_id: int, session_id: str | None = None) -> bool:
    from ..config import FAISS_INDEX_DIR
    from ...models.chatbot import UploadedFile

    # Require explicit doc-mode activation in this runtime to avoid unexpectedly
    # loading embedding models from old historical uploads.
    if not cache.get(get_doc_mode_cache_key(user_id, session_id)):
        return False

    # Do not attempt doc-RAG until this user has at least one successfully indexed upload.
    try:
        has_indexed_upload = UploadedFile.objects.filter(user_id=user_id, index_status=UploadedFile.IndexStatus.INDEXED).exists()
    except Exception:
        return False
    if not has_indexed_upload:
        return False

    index_file = os.path.join(str(FAISS_INDEX_DIR), f"user_docs_lc_{user_id}", "index.faiss")
    return os.path.exists(index_file)


def doc_rag_tool(user, query, history=None):
    docs_res = query_documents(user.id, query)
    results = docs_res.get("results") or []
    confidence = float(docs_res.get("confidence", 0.0) or 0.0)

    # If retrieval confidence is weak, skip doc-grounded prompting and answer
    # through the general assistant path directly.
    if confidence < RAG_CONFIDENCE_SWITCH_THRESHOLD:
        return _general_fallback_response(query, history=history, confidence=confidence)

    if not results:
        return _general_fallback_response(query, history=history, confidence=confidence)

    # Even with non-trivial vector scores, if lexical overlap is too weak,
    # prefer the general model instead of producing potentially off-topic doc answers.
    if not _has_contextual_overlap(query, results):
        return _general_fallback_response(query, history=history, confidence=confidence)

    # First, test for exact symbolic or short line match
    exact_line = _extract_exact_line_answer(query, results)
    if exact_line:
        unique_files = sorted({r.get("file_name") or "Uploaded File" for r in results})
        return {
            "text": exact_line,
            "source": f"{SOURCE_LABEL_DOC_PREFIX}: {', '.join(unique_files)}",
            "citation": results,
            "confidence": confidence,
        }

    # Our RAG prompt will automatically handle fallback to general knowledge
    # if the context lacks the answer.
    context = _build_rag_context(results)

    unique_files = sorted({r.get("file_name") or "Uploaded File" for r in results})
    return {
        "text": None, # Signal to use stream
        "stream_generator": lambda: _stream_rag_answer(context=context, question=query),
        "prefix_text": "",
        "source": f"{SOURCE_LABEL_DOC_PREFIX}: {', '.join(unique_files)}",
        "citation": results,
        "confidence": confidence,
    }


def _get_cache_key(user, intent, query, history):
    docs_ver = 0
    if intent == "rag":
        try:
            from ..config import FAISS_INDEX_DIR
            idx_file = os.path.join(str(FAISS_INDEX_DIR), f"user_docs_lc_{user.id}", "index.faiss")
            docs_ver = int(os.path.getmtime(idx_file)) if os.path.exists(idx_file) else 0
        except Exception:
            pass
    h = hashlib.md5(f"{query}{json.dumps(history or [])}{docs_ver}".encode()).hexdigest()
    return f"chat_{user.id}_{intent}_{h}"

def orchestrate_response(user, query, history=None, **kwargs):
    """Main entry point for chatbot logic with RAG support."""
    start = time.time()

    # Fast-path common greetings so no LLM call is made.
    if _is_greeting(query):
        return {
            "text": CHAT_GREETING_RESPONSE,
            "source": SOURCE_LABEL_LLM_GENERAL,
            "intent": "general",
            "confidence": 1.0,
            "latency": round(time.time() - start, 2),
        }

    has_user_docs = _has_user_document_index(user.id, kwargs.get("session_id"))
    conf = 1.0 if has_user_docs else 0.5
    intent = "rag" if has_user_docs else "general"
    use_doc_retrieval = has_user_docs
    
    ckey = _get_cache_key(user, intent, query, history)
    if not kwargs.get("streaming") and (cached := cache.get(ckey)): return cached

    res = {"text": "", "source": SOURCE_LABEL_LLM_GENERAL, "intent": intent, "confidence": conf}
    
    if use_doc_retrieval:
        try:
            res.update(doc_rag_tool(user, query, history=history))
            if kwargs.get("streaming") and res.get("stream_generator") and res.get("prefix_text"):
                base_gen = res["stream_generator"]

                def _with_prefix():
                    yield res["prefix_text"]
                    yield from base_gen()

                res["stream_generator"] = _with_prefix
            if not kwargs.get("streaming") and not res.get("text") and res.get("stream_generator"):
                generated = "".join(list(res["stream_generator"]()))
                res["text"] = f"{res.get('prefix_text', '')}{generated}"
                res.pop("stream_generator", None)
        except Exception as e:
            logger.error(f"RAG fail: {e}")
            if kwargs.get("streaming"):
                res["stream_generator"] = lambda: stream_llm(query, system_prompt=CHATBOT_SYSTEM_PROMPT, history=history)
                res["source"] = SOURCE_LABEL_LLM_FALLBACK
            else:
                res["text"] = call_llm(query, history=history, system_prompt=CHATBOT_SYSTEM_PROMPT)
                res["source"] = SOURCE_LABEL_LLM_FALLBACK
    else:
        if kwargs.get("streaming"):
            res["stream_generator"] = lambda: stream_llm(query, system_prompt=CHATBOT_SYSTEM_PROMPT, history=history)
        else:
            res["text"] = call_llm(query, history=history, system_prompt=CHATBOT_SYSTEM_PROMPT)

    res["latency"] = round(time.time() - start, 2)
    if not kwargs.get("streaming") and res.get("text"):
        res.pop("stream_generator", None)
        cacheable_res = {k: v for k, v in res.items() if not callable(v)}
        cache.set(ckey, cacheable_res, CHAT_CACHE_TTL_SECONDS)
    return res



