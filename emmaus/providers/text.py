from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from emmaus.domain.models import PassageReference, PassageText, TextSourceDescriptor


class BibleTextProvider(ABC):
    descriptor: TextSourceDescriptor

    @abstractmethod
    def get_passage(self, reference: PassageReference) -> PassageText:
        raise NotImplementedError


class TextProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, BibleTextProvider] = {}

    def register(self, provider: BibleTextProvider) -> None:
        self._providers[provider.descriptor.source_id] = provider

    def list(self) -> list[TextSourceDescriptor]:
        return [provider.descriptor for provider in self._providers.values()]

    def get(self, source_id: str) -> BibleTextProvider:
        try:
            return self._providers[source_id]
        except KeyError as exc:
            raise KeyError(f"Unknown text source '{source_id}'.") from exc


class LocalJsonBibleTextProvider(BibleTextProvider):
    def __init__(self, source_id: str, name: str, file_path: Path, license_name: str) -> None:
        self.file_path = file_path
        self.descriptor = TextSourceDescriptor(
            source_id=source_id,
            name=name,
            provider_type="local_file",
            license_name=license_name,
            supports_local_file=True,
            metadata={"path": str(file_path)},
        )

    def get_passage(self, reference: PassageReference) -> PassageText:
        payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        book_data = payload["books"].get(reference.book)
        if not book_data:
            raise KeyError(f"Book '{reference.book}' not found in source '{self.descriptor.source_id}'.")

        chapter = book_data.get(str(reference.chapter), {})
        end_verse = reference.end_verse or reference.start_verse
        verses = []
        for verse_number in range(reference.start_verse, end_verse + 1):
            verse_text = chapter.get(str(verse_number))
            if verse_text is None:
                raise KeyError(f"Verse {reference.book} {reference.chapter}:{verse_number} not found.")
            verses.append(f"{verse_number}. {verse_text}")

        return PassageText(
            source_id=self.descriptor.source_id,
            translation_name=self.descriptor.name,
            reference=reference,
            text=" ".join(verses),
            copyright_notice=payload.get("copyright"),
        )


class RemoteApiBibleTextProvider(BibleTextProvider):
    def __init__(
        self,
        source_id: str,
        name: str,
        base_url: str,
        api_key: str | None,
        license_name: str,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.descriptor = TextSourceDescriptor(
            source_id=source_id,
            name=name,
            provider_type="remote_api",
            license_name=license_name,
            supports_api_key=True,
            metadata={"base_url": base_url, "status": "placeholder"},
        )

    def get_passage(self, reference: PassageReference) -> PassageText:
        ref = f"{reference.book} {reference.chapter}:{reference.start_verse}"
        if reference.end_verse:
            ref = f"{ref}-{reference.end_verse}"
        return PassageText(
            source_id=self.descriptor.source_id,
            translation_name=self.descriptor.name,
            reference=reference,
            text=(
                "This provider is a placeholder for a user-configured remote Bible API. "
                f"Connect your own service at {self.base_url} and fetch '{ref}' through the adapter."
            ),
            copyright_notice="User-supplied API source",
        )
