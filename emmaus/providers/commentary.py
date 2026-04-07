from __future__ import annotations

import html
import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from urllib import error, parse, request

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

    def has(self, source_id: str) -> bool:
        return source_id in self._providers

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


class LocalJsonCommentaryProvider(CommentaryProvider):
    def __init__(
        self,
        source_id: str,
        name: str,
        file_path: Path,
        license_name: str = "Public Domain",
    ) -> None:
        self.source_id = source_id
        self.name = name
        self.file_path = Path(file_path)
        self.license_name = license_name

    def get_commentary(self, reference: PassageReference) -> list[CommentaryNote]:
        payload = self._load_payload()
        matches = []
        for entry in payload.get("entries", []):
            if not self._matches_reference(entry, reference):
                continue
            matches.append(
                CommentaryNote(
                    source_id=self.source_id,
                    title=entry.get("title") or f"{self.name} note",
                    body=entry.get("body") or "",
                    reference=reference,
                    metadata={
                        "kind": "commentary",
                        "source_name": self.name,
                        "license_name": payload.get("license_name", self.license_name),
                        **(entry.get("metadata") or {}),
                    },
                )
            )
        if matches:
            return matches
        return [
            CommentaryNote(
                source_id=self.source_id,
                title=f"{self.name} not available for this passage yet",
                body=(
                    "Emmaus does not have a bundled note for this exact passage yet. "
                    "Add more public-domain commentary entries to extend coverage without changing app logic."
                ),
                reference=reference,
                metadata={"kind": "commentary", "status": "unavailable"},
            )
        ]

    def _load_payload(self) -> dict:
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8-sig"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"entries": []}

    def _matches_reference(self, entry: dict, reference: PassageReference) -> bool:
        if self._normalize_book(entry.get("book")) != self._normalize_book(reference.book):
            return False
        if int(entry.get("chapter", 0)) != reference.chapter:
            return False
        start = int(entry.get("start_verse", 1))
        end = int(entry.get("end_verse") or start)
        ref_end = reference.end_verse or reference.start_verse
        return not (end < reference.start_verse or start > ref_end)

    def _normalize_book(self, value: str | None) -> str:
        return re.sub(r"[^a-z0-9]", "", (value or "").lower())


class ESVPassageHelpsProvider(CommentaryProvider):
    api_url = "https://api.esv.org/v3/passage/html/"

    def __init__(
        self,
        source_id: str = "esv_passage_helps",
        name: str = "ESV Passage Helps",
        api_key: str | None = None,
    ) -> None:
        self.source_id = source_id
        self.name = name
        self.api_key = api_key or ""

    def get_commentary(self, reference: PassageReference) -> list[CommentaryNote]:
        if not self.api_key:
            return [
                CommentaryNote(
                    source_id=self.source_id,
                    title="ESV passage helps unavailable",
                    body="Add an ESV API key to load footnotes, headings, and cross-reference cues from the ESV API.",
                    reference=reference,
                    metadata={"kind": "passage_helps", "status": "missing_api_key"},
                )
            ]

        ref = self._format_reference(reference)
        query = parse.urlencode(
            {
                "q": ref,
                "include-passage-references": "false",
                "include-footnotes": "true",
                "include-footnote-body": "true",
                "include-headings": "true",
                "include-subheadings": "true",
                "include-crossrefs": "true",
                "include-short-copyright": "false",
                "include-copyright": "false",
                "include-audio-link": "false",
            }
        )
        req = request.Request(
            f"{self.api_url}?{query}",
            headers={"Authorization": f"Token {self.api_key}"},
        )

        try:
            with request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            return [
                CommentaryNote(
                    source_id=self.source_id,
                    title="Passage helps could not be loaded",
                    body="Emmaus could not reach the ESV passage helps right now, so this session will continue without them.",
                    reference=reference,
                    metadata={"kind": "passage_helps", "status": "unavailable"},
                )
            ]

        html_payload = "\n".join(data.get("passages") or [])
        if not html_payload.strip():
            return []

        notes: list[CommentaryNote] = []
        headings = self._extract_headings(html_payload, reference)
        if headings:
            notes.append(
                CommentaryNote(
                    source_id=self.source_id,
                    title="Passage structure",
                    body="Section headings in the ESV: " + "; ".join(headings[:4]),
                    reference=reference,
                    metadata={"kind": "passage_helps", "section": "headings"},
                )
            )

        footnotes = self._extract_class_text(html_payload, "footnote")
        if footnotes:
            notes.append(
                CommentaryNote(
                    source_id=self.source_id,
                    title="ESV footnotes",
                    body=footnotes,
                    reference=reference,
                    metadata={"kind": "passage_helps", "section": "footnotes"},
                )
            )

        crossrefs = self._extract_class_text(html_payload, "crossref")
        if crossrefs:
            notes.append(
                CommentaryNote(
                    source_id=self.source_id,
                    title="Cross-reference cues",
                    body=crossrefs,
                    reference=reference,
                    metadata={"kind": "passage_helps", "section": "crossrefs"},
                )
            )

        if notes:
            return notes

        fallback = self._summarize_plain_text(html_payload)
        if not fallback:
            fallback = "The ESV API did not return extra headings, footnotes, or cross-reference cues for this passage."
        return [
            CommentaryNote(
                source_id=self.source_id,
                title="Passage helps from ESV",
                body=fallback,
                reference=reference,
                metadata={"kind": "passage_helps", "section": "summary"},
            )
        ]

    def _format_reference(self, reference: PassageReference) -> str:
        formatted = f"{reference.book} {reference.chapter}:{reference.start_verse}"
        if reference.end_verse:
            formatted = f"{formatted}-{reference.end_verse}"
        return formatted

    def _extract_headings(self, html_payload: str, reference: PassageReference) -> list[str]:
        formatted_reference = self._format_reference(reference).lower()
        headings: list[str] = []
        seen: set[str] = set()
        for raw in re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", html_payload, flags=re.IGNORECASE | re.DOTALL):
            cleaned = self._clean_html(raw)
            cleaned = cleaned.replace("Listen", "").strip(" -:\u00a0")
            if not cleaned:
                continue
            normalized = cleaned.lower()
            if formatted_reference in normalized:
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            headings.append(cleaned)
        return headings

    def _extract_class_text(self, html_payload: str, class_fragment: str) -> str:
        matches = re.findall(
            rf"<(div|section|aside|p)[^>]*class=\"[^\"]*{class_fragment}[^\"]*\"[^>]*>(.*?)</\1>",
            html_payload,
            flags=re.IGNORECASE | re.DOTALL,
        )
        chunks: list[str] = []
        seen: set[str] = set()
        for _, inner in matches:
            cleaned = self._clean_html(inner)
            if not cleaned:
                continue
            normalized = cleaned.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            chunks.append(cleaned)
        joined = " ".join(chunks).strip()
        return self._limit(joined, 420)

    def _summarize_plain_text(self, html_payload: str) -> str:
        cleaned = self._clean_html(html_payload)
        return self._limit(cleaned, 320)

    def _clean_html(self, value: str) -> str:
        text = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
        text = re.sub(r"</p>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _limit(self, value: str, limit: int) -> str:
        if len(value) <= limit:
            return value
        shortened = value[: limit - 1]
        if " " in shortened:
            shortened = shortened.rsplit(" ", 1)[0]
        return shortened + "..."
