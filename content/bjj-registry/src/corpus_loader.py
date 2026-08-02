"""corpus_loader.py — load technique facts from the corpus (videos w/ transcripts + metadata).

Expected input shapes (all optional except a name/slug):

  1. A directory of JSON/MD files, one per video:
     { "name", "slug", "position", "belt", "category", "summary",
       "transcript": "...", "metadata": { "common_errors": [...], "key_terms": [...] },
       "related": [ {"name","slug"} ] }

  2. A single JSON/JSONL file listing such records.

  3. A YouTube caption file (.vtt/.srt/.txt) paired with a sidecar .json metadata.

NOTE: academy attribution ("taught_at" / "where to train") is intentionally NOT
ingested or rendered. Technique pages are transcript-derived only; attribution
stays out until a real join to the registry exists. Don't re-add it here.

The transcript is the authoritative fact source. Step extraction is a conservative
heuristic: split on paragraph/numbered breaks; keep chunks that read as instruction
("grip", "pull", "hip", "insert", "rotate", "control"). Operators can override with
explicit `steps` in metadata — that wins over the heuristic.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, Optional

from technique_facts import TechniqueFacts, TechniqueRef


def _load_record(rec: dict) -> TechniqueFacts:
    meta = rec.get("metadata") or {}
    transcript = rec.get("transcript") or meta.get("transcript") or ""
    steps = rec.get("steps") or meta.get("steps") or _extract_steps(transcript)
    common_errors = rec.get("common_errors") or meta.get("common_errors") or []
    key_terms = rec.get("key_terms") or meta.get("key_terms") or _extract_terms(transcript)
    related = [
        TechniqueRef(name=r["name"], slug=r["slug"],
                     position=r.get("position"), belt=r.get("belt"), verified=True)
        for r in (rec.get("related") or [])
        if r.get("name") and r.get("slug")
    ]
    return TechniqueFacts(
        name=rec["name"], slug=rec["slug"], position=rec.get("position"),
        belt=rec.get("belt", "all levels"), category=rec.get("category"),
        summary=rec.get("summary") or (transcript[:240].strip() if transcript else None),
        transcript=transcript, transcript_verified=bool(transcript),
        steps=steps, common_errors=common_errors, key_terms=key_terms,
        related_techniques=related,
        sources={"transcript": "corpus"},
    )


def _extract_steps(transcript: str, cap: int = 10) -> list[str]:
    """Conservative heuristic: sentence/clause chunks that read as instruction.

    Splits on sentence boundaries ('. '), not just blank lines, so a single-paragraph
    transcript still yields steps. Keeps chunks with instructional verbs and reasonable length.
    """
    if not transcript:
        return []
    chunks = [c.strip() for c in re.split(r"(?:\n{2,}|\.\s+|\n\d+[\.\)]|[;])", transcript) if c.strip()]
    verbs = ("grip", "pull", "push", "hip", "insert", "rotate", "control", "step",
             "sit", "scoot", "bridge", "frame", "cross", "thumb", "wrap", "swim", "shoot",
             "swing", "lock", "finish", "break", "thread", "use", "keep", "point")
    out = []
    for c in chunks:
        low = c.lower()
        if any(v in low for v in verbs) and 20 <= len(c) <= 260:
            # strip a leading lowercase artifact and capitalize for readability
            out.append(c[:1].upper() + c[1:] if c else c)
        if len(out) >= cap:
            break
    return out


def _extract_terms(transcript: str, cap: int = 10) -> list[str]:
    if not transcript:
        return []
    found = set()
    for m in re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", transcript):
        if m.lower() in {"the", "and", "you", "your", "this", "that", "with", "from", "when", "what"}:
            continue
        found.add(m)
        if len(found) >= cap:
            break
    return sorted(find for find in found if find.lower() not in {"gracie", "barra"})


def load_corpus(path: str) -> list[TechniqueFacts]:
    """Load techniques from a file (json/jsonl) or a directory of files."""
    p = Path(path)
    if p.is_dir():
        recs = []
        for fp in sorted(p.glob("*.json")):
            try:
                recs.append(json.loads(fp.read_text(encoding="utf-8")))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid corpus JSON record {fp}: {exc}") from exc
        for fp in sorted(p.glob("*.md")):
            txt = fp.read_text(encoding="utf-8")
            # naive frontmatter-ish: name from first H1, transcript from rest
            m = re.match(r"#\s*(.+)\n+([\s\S]+)", txt)
            if m:
                recs.append({"name": m.group(1).strip(), "slug": fp.stem,
                             "transcript": m.group(2).strip()})
        return [_load_record(r) for r in recs]
    # single file: json or jsonl
    text = p.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return [_load_record(data)]
        if isinstance(data, list):
            return [_load_record(r) for r in data]
    except json.JSONDecodeError:
        return [_load_record(json.loads(l)) for l in text.splitlines() if l.strip()]
    return []
