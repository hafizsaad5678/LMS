"""Centralized provider-agnostic LLM wrapper and factory."""

from __future__ import annotations

import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List

from openai import OpenAI

from ..config import AI_PROVIDER_ALIASES, AI_PROVIDER_DEFAULT_BASE_URLS, AI_PROVIDER_ENFORCE_PATH_SUFFIX
from .prompts import JSON_ENFORCER

logger = logging.getLogger(__name__)


def _canonical_provider_name(provider_name: str) -> str:
	name = (provider_name or "").lower().strip()
	for canonical, aliases in AI_PROVIDER_ALIASES.items():
		if name in aliases:
			return canonical
	return "openai"


class LLMProvider(ABC):
	@abstractmethod
	def call(self, prompt: str, system_prompt: str, history: List[Dict], **kwargs) -> str:
		raise NotImplementedError

	@abstractmethod
	def stream(self, prompt: str, system_prompt: str, history: List[Dict], **kwargs) -> Generator[str, None, None]:
		raise NotImplementedError

	@abstractmethod
	def get_langchain_model(self, **kwargs) -> Any:
		raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
	def __init__(self) -> None:
		self.provider_name = _canonical_provider_name(os.getenv("AI_PROVIDER", "pollinations"))
		self.api_key = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("POLLINATIONS_API_KEY")
		self.base_url = self._resolve_base_url()
		self.model = os.getenv("AI_MODEL", "openai")
		self.timeout = int(os.getenv("AI_TIMEOUT", "30"))
		self.max_retries = int(os.getenv("AI_MAX_RETRIES", "2"))
		self.retry_delay = float(os.getenv("AI_RETRY_DELAY_SECONDS", "0.35"))

		self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

	def _resolve_base_url(self) -> str:
		configured = (os.getenv("AI_BASE_URL") or os.getenv("POLLINATIONS_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "").strip()
		base = configured or AI_PROVIDER_DEFAULT_BASE_URLS.get(self.provider_name) or AI_PROVIDER_DEFAULT_BASE_URLS.get("openai", "https://api.openai.com/v1")
		normalized = base.rstrip("/")
		suffix = (AI_PROVIDER_ENFORCE_PATH_SUFFIX.get(self.provider_name) or "").strip()
		if suffix:
			clean_suffix = suffix if suffix.startswith("/") else f"/{suffix}"
			if not normalized.endswith(clean_suffix):
				normalized = f"{normalized}{clean_suffix}"
		return normalized

	def _request(self, stream: bool, **request_kwargs):
		request_retries = int(request_kwargs.pop("request_retries", self.max_retries))
		request_timeout = request_kwargs.pop("request_timeout", self.timeout)
		last_exc: Exception | None = None
		for attempt in range(1, request_retries + 1):
			try:
				return self.client.chat.completions.create(stream=stream, timeout=request_timeout, **request_kwargs)
			except Exception as exc:
				last_exc = exc
				if attempt >= request_retries:
					break
				time.sleep(self.retry_delay)
		if last_exc:
			raise last_exc
		raise RuntimeError("LLM request failed with no exception details.")

	def _prepare_messages(self, prompt: str, system_prompt: str, history: List[Dict]) -> List[Dict[str, str]]:
		messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
		for msg in history or []:
			role = msg.get("role", "user")
			if role == "bot":
				role = "assistant"
			messages.append({"role": role, "content": msg.get("content", "")})
		messages.append({"role": "user", "content": prompt})
		return messages

	def call(self, prompt: str, system_prompt: str, history: List[Dict], **kwargs) -> str:
		temperature = kwargs.pop("temperature", float(os.getenv("AI_TEMPERATURE", "0.7")))
		response = self._request(
			stream=False,
			model=self.model,
			messages=self._prepare_messages(prompt, system_prompt, history),
			temperature=temperature,
			**kwargs,
		)
		return response.choices[0].message.content or ""

	def stream(self, prompt: str, system_prompt: str, history: List[Dict], **kwargs) -> Generator[str, None, None]:
		temperature = kwargs.pop("temperature", float(os.getenv("AI_TEMPERATURE", "0.7")))
		stream = self._request(
			stream=True,
			model=self.model,
			messages=self._prepare_messages(prompt, system_prompt, history),
			temperature=temperature,
			**kwargs,
		)
		for chunk in stream:
			delta = chunk.choices[0].delta.content
			if delta:
				yield delta

	def get_langchain_model(self, **kwargs) -> Any:
		from langchain_openai import ChatOpenAI

		temperature = kwargs.pop("temperature", float(os.getenv("AI_TEMPERATURE", "0.7")))
		max_retries = kwargs.pop("max_retries", 3)
		return ChatOpenAI(
			openai_api_key=self.api_key,
			base_url=self.base_url,
			model=self.model,
			temperature=temperature,
			max_retries=max_retries,
			timeout=self.timeout,
			**kwargs,
		)


_PROVIDER_CACHE: Dict[str, LLMProvider] = {}


def get_provider() -> LLMProvider:
	provider_name = _canonical_provider_name(os.getenv("AI_PROVIDER", "pollinations"))
	if provider_name not in _PROVIDER_CACHE:
		_PROVIDER_CACHE[provider_name] = OpenAICompatibleProvider()
	return _PROVIDER_CACHE[provider_name]


def call_llm(
	prompt: str,
	system_prompt: str = JSON_ENFORCER,
	history: List[Dict] | None = None,
	temperature: float | None = None,
	**kwargs,
) -> str:
	if temperature is not None:
		kwargs["temperature"] = temperature
	try:
		return get_provider().call(prompt=prompt, system_prompt=system_prompt, history=history or [], **kwargs)
	except Exception as exc:
		logger.error("call_llm failed: %s", exc)
		raise


def stream_llm(
	prompt: str,
	system_prompt: str = JSON_ENFORCER,
	history: List[Dict] | None = None,
	temperature: float | None = None,
	**kwargs,
) -> Generator[str, None, None]:
	if temperature is not None:
		kwargs["temperature"] = temperature
	try:
		yield from get_provider().stream(prompt=prompt, system_prompt=system_prompt, history=history or [], **kwargs)
	except Exception as exc:
		logger.error("stream_llm failed: %s", exc)
		raise


def get_chat_model(**kwargs) -> Any:
	try:
		return get_provider().get_langchain_model(**kwargs)
	except Exception as exc:
		logger.error("get_chat_model failed: %s", exc)
		raise


# Backward compatibility alias.
call_llm_stream = stream_llm

