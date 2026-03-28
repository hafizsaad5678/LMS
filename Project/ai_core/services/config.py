"""Centralized ai_core configuration.

All runtime constants and heuristics should come from this module so behavior
can be tuned through environment variables without code edits.
"""

from __future__ import annotations

import os

from django.conf import settings


def _env_int(name: str, default: int) -> int:
	try:
		return int(os.getenv(name, str(default)))
	except (TypeError, ValueError):
		return default


def _env_float(name: str, default: float) -> float:
	try:
		return float(os.getenv(name, str(default)))
	except (TypeError, ValueError):
		return default


def _env_bool(name: str, default: bool) -> bool:
	raw = os.getenv(name)
	if raw is None:
		return default
	return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _env_csv(name: str, default: list[str]) -> list[str]:
	raw = os.getenv(name)
	if not raw:
		return default
	return [item.strip() for item in raw.split(",") if item.strip()]


def _env_str(name: str, default: str) -> str:
	raw = os.getenv(name)
	if raw is None:
		return default
	value = str(raw).strip()
	return value if value else default


# Evaluation & Metrics
CHAT_EVAL_ENABLED = _env_bool("CHAT_EVAL_ENABLED", True)

# Shared chat behavior
CHAT_HISTORY_LIMIT = _env_int("CHAT_HISTORY_LIMIT", 5)
CHAT_CACHE_TTL_SECONDS = _env_int("CHAT_CACHE_TTL_SECONDS", 300)
CHAT_SERVICE_VERSION = _env_str("CHAT_SERVICE_VERSION", "v2")
CHAT_GREETING_KEYWORDS = _env_csv(
	"CHAT_GREETING_KEYWORDS",
	[
		"hi",
		"hello",
		"hey",
		
	],
)
CHAT_GREETING_RESPONSE = _env_str(
	"CHAT_GREETING_RESPONSE",
	"Hello! I am your academic assistant. Ask me about assignments, quizzes, attendance, or your uploaded documents.",
)
RAG_CONFIDENCE_SWITCH_THRESHOLD = _env_float("RAG_CONFIDENCE_SWITCH_THRESHOLD", 0.3)
RAG_MAX_CONTEXT_CHARS = _env_int("RAG_MAX_CONTEXT_CHARS", 4000)
SOURCE_LABEL_LLM_GENERAL = os.getenv("SOURCE_LABEL_LLM_GENERAL", "LLM General")
SOURCE_LABEL_LLM_FALLBACK = os.getenv("SOURCE_LABEL_LLM_FALLBACK", "LLM Fallback")
SOURCE_LABEL_DOC_PREFIX = os.getenv("SOURCE_LABEL_DOC_PREFIX", "Document")
LOW_CONFIDENCE_MESSAGE = os.getenv(
	"LOW_CONFIDENCE_MESSAGE",
	"Data me clear answer nahi mila, ye nearest info hai...",
)

# Retrieval policy
CHAT_MIN_SIMILARITY_SCORE = _env_float("CHAT_MIN_SIMILARITY_SCORE", 0.1)
CHAT_TOP_K = _env_int("CHAT_TOP_K", 5)
RETRIEVAL_SHORT_QUERY_LEN_FOR_TOP_K = _env_int("RETRIEVAL_SHORT_QUERY_LEN_FOR_TOP_K", 15)
RETRIEVAL_SHORT_QUERY_TOP_K = _env_int("RETRIEVAL_SHORT_QUERY_TOP_K", 50)
RETRIEVAL_SHORT_QUERY_LEN_FOR_THRESHOLD = _env_int("RETRIEVAL_SHORT_QUERY_LEN_FOR_THRESHOLD", 10)
RETRIEVAL_SHORT_QUERY_MIN_SCORE = _env_float("RETRIEVAL_SHORT_QUERY_MIN_SCORE", 0.05)
RETRIEVAL_SCORE_ROUND_DIGITS = _env_int("RETRIEVAL_SCORE_ROUND_DIGITS", 3)
RETRIEVAL_CONFIDENCE_ROUNDED = _env_bool("RETRIEVAL_CONFIDENCE_ROUNDED", False)

# RAG indexing configuration
CHAT_CHUNK_SIZE = _env_int("CHAT_CHUNK_SIZE", 800)
CHAT_CHUNK_OVERLAP = _env_int("CHAT_CHUNK_OVERLAP", 100)
CHAT_EMBEDDING_MODEL = os.getenv("CHAT_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHAT_EMBEDDING_DEVICE = os.getenv("CHAT_EMBEDDING_DEVICE", "cpu")
CHAT_EMBEDDING_NORMALIZE = _env_bool("CHAT_EMBEDDING_NORMALIZE", False)

# Intent routing heuristics
INTENT_KEYWORDS_RAG = _env_csv(
	"INTENT_KEYWORDS_RAG",
	["doc", "pdf", "file", "upload", "notes", "material", "page", "chapter"],
)
INTENT_SYMBOLIC_MAX_LEN = _env_int("INTENT_SYMBOLIC_MAX_LEN", 30)
INTENT_CONFIDENCE_KEYWORD_RAG = _env_float("INTENT_CONFIDENCE_KEYWORD_RAG", 0.9)
INTENT_CONFIDENCE_SYMBOLIC_RAG = _env_float("INTENT_CONFIDENCE_SYMBOLIC_RAG", 0.8)
INTENT_CONFIDENCE_LLM = _env_float("INTENT_CONFIDENCE_LLM", 0.7)
INTENT_CONFIDENCE_FALLBACK = _env_float("INTENT_CONFIDENCE_FALLBACK", 0.5)

# Provider registry configuration
AI_PROVIDER_ALIASES = {
	"pollinations": {"pollinations", "pollin"},
	"openai": {"openai"},
}
AI_PROVIDER_DEFAULT_BASE_URLS = {
	"pollinations": _env_str("POLLINATIONS_BASE_URL_DEFAULT", "https://gen.pollinations.ai/v1"),
	"openai": _env_str("OPENAI_BASE_URL_DEFAULT", "https://api.openai.com/v1"),
}
AI_PROVIDER_ENFORCE_PATH_SUFFIX = {
	"pollinations": _env_str("POLLINATIONS_BASE_URL_SUFFIX", "/v1"),
	"openai": _env_str("OPENAI_BASE_URL_SUFFIX", ""),
}

# Prompt/version metadata
PROMPT_VERSION = _env_str("PROMPT_VERSION", "2026-03-20.v2")

# Quiz defaults and policies
QUIZ_DEFAULT_NUM_QUESTIONS = _env_int("QUIZ_DEFAULT_NUM_QUESTIONS", 10)
QUIZ_DEFAULT_QUESTION_TYPE = _env_str("QUIZ_DEFAULT_QUESTION_TYPE", "MCQ")
QUIZ_DEFAULT_DIFFICULTY = _env_str("QUIZ_DEFAULT_DIFFICULTY", "Medium")
QUIZ_DEFAULT_TOTAL_MARKS = _env_int("QUIZ_DEFAULT_TOTAL_MARKS", 100)
QUIZ_DEFAULT_QUESTION_MARKS = _env_int("QUIZ_DEFAULT_QUESTION_MARKS", 1)
QUIZ_DEFAULT_TEMPERATURE = _env_float("QUIZ_DEFAULT_TEMPERATURE", 0.7)
QUIZ_LLM_TIMEOUT_SECONDS = _env_int("QUIZ_LLM_TIMEOUT_SECONDS", 90)
QUIZ_LLM_REQUEST_RETRIES = _env_int("QUIZ_LLM_REQUEST_RETRIES", 3)
QUIZ_DUPLICATE_WINDOW_SECONDS = _env_int("QUIZ_DUPLICATE_WINDOW_SECONDS", 10)
QUIZ_GRADE_COMPONENT_WEIGHTAGE = _env_int("QUIZ_GRADE_COMPONENT_WEIGHTAGE", 5)
QUIZ_GRADE_COMPONENT_STATUS = _env_str("QUIZ_GRADE_COMPONENT_STATUS", "published")

# FAISS safety controls
FAISS_ALLOW_DANGEROUS_DESERIALIZATION = _env_bool("FAISS_ALLOW_DANGEROUS_DESERIALIZATION", True)
FAISS_REQUIRE_INTEGRITY_MANIFEST = _env_bool("FAISS_REQUIRE_INTEGRITY_MANIFEST", True)

# Paths
FAISS_INDEX_DIR = settings.FAISS_INDEX_DIR
DOCS_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads")
