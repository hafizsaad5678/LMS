import json
import re

from pydantic import BaseModel, Field

from ..config import (
    INTENT_KEYWORDS_RAG,
    INTENT_SYMBOLIC_MAX_LEN,
    INTENT_CONFIDENCE_KEYWORD_RAG,
    INTENT_CONFIDENCE_SYMBOLIC_RAG,
    INTENT_CONFIDENCE_LLM,
    INTENT_CONFIDENCE_FALLBACK,
)
from ..llm.provider import call_llm

INTENT_ROUTER_PROMPT = """
Analyze the user query and classify it into one of the following intents:

1. rag - Questions that should be answered from the user's uploaded documents.
2. general - Everything else.

Return only a JSON object with:
- \"intent\": \"rag\" or \"general\"
- \"slots\": {{}} (keep empty for now)
- \"reason\": A brief 1-sentence reason for this classification.

User Query: \"{query}\"
"""


class IntentResponse(BaseModel):
    intent: str = Field(default="general")
    slots: dict = Field(default_factory=dict)


def classify_intent(query: str):
    """Classify the user query into 'rag' or 'general'."""
    q = (query or "").strip().lower()

    # Fast routing for explicit doc queries.
    if any(w in q for w in INTENT_KEYWORDS_RAG):
        return {"intent": "rag", "slots": {}, "confidence": INTENT_CONFIDENCE_KEYWORD_RAG}

    # Symbolic/short equation-like queries are often from uploaded docs.
    if len(q) <= INTENT_SYMBOLIC_MAX_LEN and re.search(r"[=+\-*/^]", q):
        return {"intent": "rag", "slots": {}, "confidence": INTENT_CONFIDENCE_SYMBOLIC_RAG}

    try:
        res = call_llm(INTENT_ROUTER_PROMPT.format(query=query), temperature=0.0)
        data = json.loads(res.replace("```json", "").replace("```", "").strip())
        parsed = IntentResponse(**data)
        intent = parsed.intent
        if intent not in {"rag", "general"}:
            intent = "general"
        return {"intent": intent, "slots": parsed.slots, "confidence": INTENT_CONFIDENCE_LLM}
    except Exception:
        return {"intent": "general", "slots": {}, "confidence": INTENT_CONFIDENCE_FALLBACK}
