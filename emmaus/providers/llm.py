from __future__ import annotations

import json
import socket
from abc import ABC, abstractmethod
from urllib import error, request


class LLMProvider(ABC):
    source_id: str

    @abstractmethod
    def generate_guidance(self, prompt: str) -> str:
        raise NotImplementedError


class LLMProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {}

    def register(self, provider: LLMProvider) -> None:
        self._providers[provider.source_id] = provider

    def get(self, source_id: str) -> LLMProvider:
        try:
            return self._providers[source_id]
        except KeyError as exc:
            raise KeyError(f"Unknown LLM provider '{source_id}'.") from exc


class NullLLMProvider(LLMProvider):
    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    def generate_guidance(self, prompt: str) -> str:
        return (
            "No external LLM has been configured. The app is using local rule-based guidance, "
            "and this prompt can be forwarded to a real AI adapter later:\n"
            f"{prompt}"
        )


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        source_id: str,
        base_url: str,
        model: str,
        request_timeout_seconds: float = 20.0,
    ) -> None:
        self.source_id = source_id
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.request_timeout_seconds = request_timeout_seconds

    @staticmethod
    def is_available(base_url: str, timeout_seconds: float = 0.25) -> bool:
        tags_url = f"{base_url.rstrip('/')}/api/tags"
        try:
            with request.urlopen(tags_url, timeout=timeout_seconds) as response:
                return getattr(response, "status", 200) == 200
        except (error.URLError, TimeoutError, socket.timeout):
            return False

    def generate_guidance(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        req = request.Request(
            url=f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.request_timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except (error.URLError, TimeoutError, socket.timeout):
            return self._fallback_guidance(prompt)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return self._fallback_guidance(prompt)

        guidance = str(data.get("response", "")).strip()
        if guidance:
            return guidance
        return self._fallback_guidance(prompt)

    def _fallback_guidance(self, prompt: str) -> str:
        return (
            f"Ollama model '{self.model}' could not be reached, so Emmaus is falling back to local rule-based guidance. "
            f"Prompt:\n{prompt}"
        )
