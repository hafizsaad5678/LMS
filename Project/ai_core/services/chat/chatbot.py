import hashlib
import json
import logging
import os
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
    LOW_CONFIDENCE_MESSAGE,
    SOURCE_LABEL_DOC_PREFIX,
    SOURCE_LABEL_LLM_FALLBACK,
    SOURCE_LABEL_LLM_GENERAL,
)
from ..llm.provider import call_llm, get_chat_model, stream_llm
from ..llm.prompts import CHATBOT_SYSTEM_PROMPT, RAG_DOC_ANSWER_PROMPT
from ..tools.docs import query_documents
from .intent_router import classify_intent

logger = logging.getLogger(__name__)
logger.info("LOADED SAFE CHATBOT SERVICE %s", CHAT_SERVICE_VERSION)


def _compact_text(value: str) -> str:
    import re

    return re.sub(r"\s+", "", (value or "").lower())


def _is_greeting(query: str) -> bool:
    cleaned = (query or "").strip().lower()
    if not cleaned:
        return False
    compact = _compact_text(cleaned)
    return any(compact == _compact_text(item) for item in CHAT_GREETING_KEYWORDS)


def _extract_exact_line_answer(question: str, results: list[dict]) -> str:
    """Prefer exact line matches for symbolic/equation-style queries."""
    q = _compact_text(question).strip("?")
    if not q:
        return ""
    for r in results:
        for line in (r.get("text") or "").splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            if q in _compact_text(candidate):
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


def _stream_rag_answer(context: str, question: str):
    prompt = ChatPromptTemplate.from_template(RAG_DOC_ANSWER_PROMPT)
    chain = prompt | get_chat_model() | StrOutputParser()
    yield from chain.stream({"context": context, "question": question})


def doc_rag_tool(user, student_id, query, slots, history=None):
    docs_res = query_documents(user.id, query)
    results = docs_res.get("results") or []
    confidence = docs_res.get("confidence", 0.0)

    if not results:
        llm_ans = call_llm(
            query,
            history=history or [],
            system_prompt=CHATBOT_SYSTEM_PROMPT,
        )
        return {
            "text": f"{LOW_CONFIDENCE_MESSAGE}\n\n{llm_ans}",
            "source": SOURCE_LABEL_LLM_GENERAL,
            "confidence": confidence,
        }

    # 1) For equation/symbolic questions, try to return the exact matching line from the document.
    import re

    is_symbolic = bool(re.search(r"[=+\-*/^]", query)) and len(query.strip()) <= 30
    if is_symbolic:
        exact_line = _extract_exact_line_answer(query, results)
        if exact_line:
            unique_files = sorted({r.get("file_name") or "Uploaded File" for r in results})
            return {
                "text": exact_line,
                "source": f"{SOURCE_LABEL_DOC_PREFIX}: {', '.join(unique_files)}",
                "citation": results,
                "confidence": confidence,
            }

    # If retrieval confidence is very low, keep the user informed but still ground
    # on retrieved context rather than switching to pure general knowledge.
    low_confidence_note = ""
    if confidence < RAG_CONFIDENCE_SWITCH_THRESHOLD:
        low_confidence_note = f"{LOW_CONFIDENCE_MESSAGE}\n\n"

    context = _build_rag_context(results)

    unique_files = sorted({r.get("file_name") or "Uploaded File" for r in results})
    return {
        "text": None, # Signal to use stream
        "stream_generator": lambda: _stream_rag_answer(context=context, question=query),
        "prefix_text": low_confidence_note,
        "source": f"{SOURCE_LABEL_DOC_PREFIX}: {', '.join(unique_files)}",
        "citation": results,
        "confidence": confidence,
    }


TOOLS = {
    "student": {
        "rag": doc_rag_tool,
    }
}


def _get_cache_key(user, intent, query, history):
    docs_ver = 0
    if intent == "rag":
        try:
            from ..config import FAISS_INDEX_DIR
            idx_file = os.path.join(str(FAISS_INDEX_DIR), f"user_docs_lc_{user.id}", "index.faiss")
            docs_ver = int(os.path.getmtime(idx_file)) if os.path.exists(idx_file) else 0
        except: pass
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

    itnt = classify_intent(query)
    intent, slots, conf = itnt["intent"], itnt.get("slots", {}), itnt.get("confidence", 0.5)
    
    if intent == "rag" and conf < RAG_CONFIDENCE_SWITCH_THRESHOLD:
        intent = "general"
    
    ckey = _get_cache_key(user, intent, query, history)
    if not kwargs.get("streaming") and (cached := cache.get(ckey)): return cached

    res = {"text": "", "source": SOURCE_LABEL_LLM_GENERAL, "intent": intent, "confidence": conf}
    
    if intent == "rag":
        try:
            res.update(doc_rag_tool(user, None, query, slots, history=history))
            if kwargs.get("streaming") and res.get("stream_generator") and res.get("prefix_text"):
                base_gen = res["stream_generator"]

                def _with_prefix():
                    yield res["prefix_text"]
                    yield from base_gen()

                res["stream_generator"] = _with_prefix
            if not kwargs.get("streaming") and not res.get("text") and res.get("stream_generator"):
                generated = "".join(list(res["stream_generator"]()))
                res["text"] = f"{res.get('prefix_text', '')}{generated}"
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
        cache.set(ckey, res, CHAT_CACHE_TTL_SECONDS)
    return res
