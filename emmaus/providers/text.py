from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from urllib import error, parse, request

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
        payload = json.loads(self.file_path.read_text(encoding="utf-8-sig"))
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


class ESVBibleTextProvider(BibleTextProvider):
    api_url = "https://api.esv.org/v3/passage/text/"

    def __init__(
        self,
        source_id: str = "esv",
        name: str = "ESV",
        api_key: str | None = None,
        license_name: str = "Crossway API Terms",
    ) -> None:
        self.api_key = api_key or ""
        self.descriptor = TextSourceDescriptor(
            source_id=source_id,
            name=name,
            provider_type="remote_api",
            license_name=license_name,
            supports_api_key=True,
            metadata={
                "base_url": self.api_url,
                "vendor": "esv",
                "status": "configured" if self.api_key else "missing_api_key",
            },
        )

    def get_passage(self, reference: PassageReference) -> PassageText:
        if not self.api_key:
            raise RuntimeError("No ESV API key has been configured for this source.")

        ref = f"{reference.book} {reference.chapter}:{reference.start_verse}"
        if reference.end_verse:
            ref = f"{ref}-{reference.end_verse}"

        query = parse.urlencode(
            {
                "q": ref,
                "include-headings": "false",
                "include-footnotes": "false",
                "include-verse-numbers": "false",
                "include-short-copyright": "false",
                "include-passage-references": "false",
            }
        )
        req = request.Request(
            f"{self.api_url}?{query}",
            headers={"Authorization": f"Token {self.api_key}"},
        )
        try:
            with request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError) as exc:
            raise RuntimeError("Unable to reach the ESV API right now.") from exc

        passages = data.get("passages") or []
        if not passages:
            raise KeyError(f"Passage '{ref}' was not returned by the ESV API.")

        text = re.sub(r"\s+", " ", " ".join(segment.strip() for segment in passages if segment.strip())).strip()
        return PassageText(
            source_id=self.descriptor.source_id,
            translation_name=self.descriptor.name,
            reference=reference,
            text=text,
            copyright_notice="English Standard Version (ESV), copyright 2001 by Crossway Bibles. All rights reserved.",
        )
