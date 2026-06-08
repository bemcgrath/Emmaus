"""Build emmaus/data/topics/{openbible,naves}.json from public datasets.

Run from the repo root:
    python -m emmaus.scripts.download_topics
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

OPENBIBLE_URL = "https://a.openbible.info/data/topic-scores.zip"
NAVES_URL = (
    "https://raw.githubusercontent.com/BradyStephenson/bible-data/main/"
    "NavesTopicalDictionary.csv"
)
TOP_N = 50
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "topics"

OSIS_TO_BOOK = {
    "Gen": "Genesis", "Exod": "Exodus", "Lev": "Leviticus", "Num": "Numbers",
    "Deut": "Deuteronomy", "Josh": "Joshua", "Judg": "Judges", "Ruth": "Ruth",
    "1Sam": "1 Samuel", "2Sam": "2 Samuel", "1Kgs": "1 Kings", "2Kgs": "2 Kings",
    "1Chr": "1 Chronicles", "2Chr": "2 Chronicles", "Ezra": "Ezra", "Neh": "Nehemiah",
    "Esth": "Esther", "Job": "Job", "Ps": "Psalms", "Prov": "Proverbs",
    "Eccl": "Ecclesiastes", "Song": "Song of Solomon", "Isa": "Isaiah",
    "Jer": "Jeremiah", "Lam": "Lamentations", "Ezek": "Ezekiel", "Dan": "Daniel",
    "Hos": "Hosea", "Joel": "Joel", "Amos": "Amos", "Obad": "Obadiah",
    "Jonah": "Jonah", "Mic": "Micah", "Nah": "Nahum", "Hab": "Habakkuk",
    "Zeph": "Zephaniah", "Hag": "Haggai", "Zech": "Zechariah", "Mal": "Malachi",
    "Matt": "Matthew", "Mark": "Mark", "Luke": "Luke", "John": "John",
    "Acts": "Acts", "Rom": "Romans", "1Cor": "1 Corinthians", "2Cor": "2 Corinthians",
    "Gal": "Galatians", "Eph": "Ephesians", "Phil": "Philippians", "Col": "Colossians",
    "1Thess": "1 Thessalonians", "2Thess": "2 Thessalonians", "1Tim": "1 Timothy",
    "2Tim": "2 Timothy", "Titus": "Titus", "Phlm": "Philemon", "Heb": "Hebrews",
    "Jas": "James", "1Pet": "1 Peter", "2Pet": "2 Peter", "1John": "1 John",
    "2John": "2 John", "3John": "3 John", "Jude": "Jude", "Rev": "Revelation",
}

NAVES_ABBREV_TO_BOOK = {
    "GEN": "Genesis", "EXO": "Exodus", "LEV": "Leviticus", "NUM": "Numbers",
    "DEU": "Deuteronomy", "JOS": "Joshua", "JDG": "Judges", "RUT": "Ruth",
    "1SA": "1 Samuel", "2SA": "2 Samuel", "1KI": "1 Kings", "2KI": "2 Kings",
    "1CH": "1 Chronicles", "2CH": "2 Chronicles", "EZR": "Ezra", "NEH": "Nehemiah",
    "EST": "Esther", "JOB": "Job", "PSA": "Psalms", "PRO": "Proverbs",
    "ECC": "Ecclesiastes", "SNG": "Song of Solomon", "SON": "Song of Solomon",
    "ISA": "Isaiah", "JER": "Jeremiah", "LAM": "Lamentations", "EZE": "Ezekiel",
    "DAN": "Daniel", "HOS": "Hosea", "JOL": "Joel", "JOE": "Joel",
    "AMO": "Amos", "OBA": "Obadiah", "JON": "Jonah", "MIC": "Micah",
    "NAH": "Nahum", "HAB": "Habakkuk", "ZEP": "Zephaniah", "HAG": "Haggai",
    "ZEC": "Zechariah", "MAL": "Malachi", "MAT": "Matthew", "MAR": "Mark",
    "MRK": "Mark", "LUK": "Luke", "JHN": "John", "JOH": "John", "ACT": "Acts",
    "ROM": "Romans", "1CO": "1 Corinthians", "2CO": "2 Corinthians",
    "GAL": "Galatians", "EPH": "Ephesians", "PHP": "Philippians",
    "PHI": "Philippians", "COL": "Colossians", "1TH": "1 Thessalonians",
    "2TH": "2 Thessalonians", "1TI": "1 Timothy", "2TI": "2 Timothy",
    "TIT": "Titus", "PHM": "Philemon", "HEB": "Hebrews", "JAM": "James",
    "JAS": "James", "1PE": "1 Peter", "2PE": "2 Peter", "1JO": "1 John",
    "1JN": "1 John", "2JO": "2 John", "2JN": "2 John", "3JO": "3 John",
    "3JN": "3 John", "JUD": "Jude", "JDE": "Jude", "REV": "Revelation",
}

_OSIS_PART_RE = re.compile(r"^([1-3]?[A-Za-z]+)\.(\d+)\.(\d+)$")


def fetch(url: str) -> bytes:
    print(f"  fetching {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": "emmaus-topic-downloader/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def parse_osis_passage(osis: str) -> dict | None:
    """Parse 'Exod.20.1' or 'Exod.20.1-Exod.20.26' into a PassageReference dict."""
    parts = osis.split("-", 1)
    start = _OSIS_PART_RE.match(parts[0])
    if not start:
        return None
    book_code, chapter, start_verse = start.group(1), int(start.group(2)), int(start.group(3))
    book = OSIS_TO_BOOK.get(book_code)
    if not book:
        return None
    end_verse: int | None = None
    if len(parts) == 2:
        end = _OSIS_PART_RE.match(parts[1])
        if end and end.group(1) == book_code and int(end.group(2)) == chapter:
            end_verse = int(end.group(3))
    return {"book": book, "chapter": chapter, "start_verse": start_verse, "end_verse": end_verse}


def build_openbible() -> dict:
    raw = fetch(OPENBIBLE_URL)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        with zf.open("topic-scores.txt") as fh:
            text = fh.read().decode("utf-8")

    topics: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for line in text.splitlines():
        if not line or line.startswith("Topic") or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        topic, osis, score_str = parts[0].strip(), parts[1].strip(), parts[2].strip()
        try:
            score = int(score_str)
        except ValueError:
            continue
        passage = parse_osis_passage(osis)
        if passage is None:
            continue
        topics[topic].append((score, passage))

    result_topics = []
    for topic, refs in sorted(topics.items()):
        refs.sort(key=lambda pair: pair[0], reverse=True)
        top_refs = [passage for _score, passage in refs[:TOP_N]]
        if not top_refs:
            continue
        result_topics.append(
            {
                "topic_id": slugify(topic),
                "name": topic,
                "verses": top_refs,
            }
        )

    return {
        "source": "openbible",
        "name": "OpenBible Topics",
        "license": "CC-BY 4.0",
        "attribution": "OpenBible.info topic scores (https://www.openbible.info/labs/topics/)",
        "topics": result_topics,
    }


_NAVES_REF_RE = re.compile(
    r"\b(?P<book>[1-3]?[A-Z]{2,3})\s+(?P<chapter>\d+):(?P<verses>[0-9,\-]+)"
)


def parse_naves_refs(entry: str) -> list[dict]:
    refs: list[dict] = []
    seen: set[tuple[str, int, int, int | None]] = set()
    for match in _NAVES_REF_RE.finditer(entry):
        book = NAVES_ABBREV_TO_BOOK.get(match.group("book"))
        if not book:
            continue
        try:
            chapter = int(match.group("chapter"))
        except ValueError:
            continue
        for chunk in match.group("verses").split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "-" in chunk:
                lo_str, hi_str = chunk.split("-", 1)
                try:
                    start_v = int(lo_str)
                    end_v: int | None = int(hi_str)
                except ValueError:
                    continue
            else:
                try:
                    start_v = int(chunk)
                except ValueError:
                    continue
                end_v = None
            key = (book, chapter, start_v, end_v)
            if key in seen:
                continue
            seen.add(key)
            refs.append(
                {"book": book, "chapter": chapter, "start_verse": start_v, "end_verse": end_v}
            )
    return refs


def build_naves() -> dict:
    raw = fetch(NAVES_URL).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))

    result_topics = []
    for row in reader:
        subject = (row.get("subject") or "").strip()
        entry = row.get("entry") or ""
        if not subject:
            continue
        refs = parse_naves_refs(entry)
        if not refs:
            continue
        result_topics.append(
            {
                "topic_id": slugify(subject),
                "name": subject.title(),
                "section": (row.get("section") or "").strip().upper() or None,
                "verses": refs[:TOP_N],
            }
        )

    return {
        "source": "naves",
        "name": "Nave's Topical Bible",
        "license": "Public Domain",
        "attribution": "Nave's Topical Bible (1897), public domain",
        "topics": result_topics,
    }


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("building OpenBible topics...", file=sys.stderr)
    openbible = build_openbible()
    (DATA_DIR / "openbible.json").write_text(
        json.dumps(openbible, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  wrote {len(openbible['topics'])} topics", file=sys.stderr)

    print("building Nave's topics...", file=sys.stderr)
    naves = build_naves()
    (DATA_DIR / "naves.json").write_text(
        json.dumps(naves, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  wrote {len(naves['topics'])} topics", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
