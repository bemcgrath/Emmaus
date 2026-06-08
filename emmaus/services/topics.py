from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from emmaus.domain.models import PassageReference


class TopicService:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._cache: dict[str, dict[str, Any]] = {}

    def _load(self, source: str) -> dict[str, Any]:
        if source not in {"openbible", "naves", "books"}:
            raise KeyError(f"Unknown topic source '{source}'.")
        if source not in self._cache:
            path = self._data_dir / f"{source}.json"
            if not path.exists():
                raise FileNotFoundError(
                    f"Topic data file '{path}' is missing. "
                    "Run `python -m emmaus.scripts.download_topics` to generate it."
                )
            self._cache[source] = json.loads(path.read_text(encoding="utf-8"))
        return self._cache[source]

    def list_sources(self) -> list[dict[str, Any]]:
        sources = []
        for source in ("openbible", "naves"):
            try:
                data = self._load(source)
            except FileNotFoundError:
                continue
            sources.append(
                {
                    "source": source,
                    "name": data.get("name", source),
                    "license": data.get("license"),
                    "attribution": data.get("attribution"),
                    "topic_count": len(data.get("topics", [])),
                }
            )
        return sources

    def list_topics(self, source: str, query: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        data = self._load(source)
        topics = data.get("topics", [])
        if query:
            needle = query.strip().lower()
            topics = [t for t in topics if needle in t["name"].lower()]
        return [
            {"topic_id": t["topic_id"], "name": t["name"], "verse_count": len(t.get("verses", []))}
            for t in topics[:limit]
        ]

    def get_topic_verses(self, source: str, topic_id: str) -> dict[str, Any]:
        data = self._load(source)
        for topic in data.get("topics", []):
            if topic["topic_id"] == topic_id:
                return {
                    "topic_id": topic["topic_id"],
                    "name": topic["name"],
                    "verses": [PassageReference(**v) for v in topic.get("verses", [])],
                }
        raise LookupError(f"Topic '{topic_id}' not found in {source}.")

    def list_books(self) -> list[dict[str, Any]]:
        data = self._load("books")
        return data.get("books", [])
