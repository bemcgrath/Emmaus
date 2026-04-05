from __future__ import annotations

from abc import ABC, abstractmethod


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
