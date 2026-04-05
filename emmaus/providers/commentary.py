from __future__ import annotations

from abc import ABC, abstractmethod

from emmaus.domain.models import CommentaryNote, PassageReference


class CommentaryProvider(ABC):
    source_id: str
    name: str

    @abstractmethod
    def get_commentary(self, reference: PassageReference) -> list[CommentaryNote]:
        raise NotImplementedError


class CommentaryProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, CommentaryProvider] = {}

    def register(self, provider: CommentaryProvider) -> None:
        self._providers[provider.source_id] = provider

    def list(self) -> list[dict[str, str]]:
        return [
            {"source_id": provider.source_id, "name": provider.name}
            for provider in self._providers.values()
        ]

    def get(self, source_id: str) -> CommentaryProvider:
        try:
            return self._providers[source_id]
        except KeyError as exc:
            raise KeyError(f"Unknown commentary source '{source_id}'.") from exc


class NotesPlaceholderCommentaryProvider(CommentaryProvider):
    def __init__(self, source_id: str, name: str) -> None:
        self.source_id = source_id
        self.name = name

    def get_commentary(self, reference: PassageReference) -> list[CommentaryNote]:
        return [
            CommentaryNote(
                source_id=self.source_id,
                title="Commentary integration placeholder",
                body=(
                    "No bundled commentary is included. Plug in your own public-domain or licensed "
                    "commentary provider here and keep licensing isolated from app logic."
                ),
                reference=reference,
                metadata={"integration_status": "placeholder"},
            )
        ]
