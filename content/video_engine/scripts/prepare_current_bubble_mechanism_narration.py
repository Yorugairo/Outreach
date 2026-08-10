"""Compile the finance pilot's exact spoken master for ElevenLabs.

Packaging, section timings, Short boundary markers, and primary-source notes
remain editorial controls. Only prose inside ``## Narration`` is emitted into
the canonical ``history_narration.v1`` contract used by the existing
single-master ElevenLabs path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.history_narration import validate_history_narration


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PILOT = (
    ROOT
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "current-bubble-mechanism"
)
SECTION = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
WORD = re.compile(r"\b[\w'’-]+\b", re.UNICODE)


def _safe_id(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return normalized or "narration"


def _narration_region(markdown: str) -> str:
    start_marker = "## Narration"
    end_marker = "## Primary claim locators"
    if start_marker not in markdown or end_marker not in markdown:
        raise ValueError("script must contain Narration and Primary claim locators sections")
    return markdown.split(start_marker, 1)[1].split(end_marker, 1)[0]


def _spoken_text(markdown: str) -> str:
    lines: list[str] = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line or line.startswith("**[SHORT CAPSULE "):
            continue
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        lines.append(line)
    return " ".join(lines)


def compile_narration(
    pilot: Path,
    output: Path,
    *,
    episode_id: str = "systems-and-blowups:current-bubble-mechanism",
    target_duration_s: float = 870.0,
) -> dict[str, Any]:
    script_path = pilot / "script-draft.v1.md"
    script = script_path.read_text(encoding="utf-8")
    narration = _narration_region(script)
    matches = list(SECTION.finditer(narration))
    if not matches:
        raise ValueError("narration section has no level-three chapter headings")

    segments: list[dict[str, Any]] = []
    for index, match in enumerate(matches, start=1):
        end = matches[index].start() if index < len(matches) else len(narration)
        heading = match.group(1)
        text = _spoken_text(narration[match.end() : end])
        if not text:
            raise ValueError(f"chapter {heading!r} has no spoken narration")
        segments.append(
            {
                "segment_id": f"cbm-{index:02d}-{_safe_id(heading)}",
                "scene_id": index,
                "chapter_id": _safe_id(heading),
                "claim_refs": [],
                "citation_refs": [],
                "text": text,
                "word_count": len(WORD.findall(text)),
                "char_count": len(text),
            }
        )

    full_text = " ".join(segment["text"] for segment in segments)
    normalized = " ".join(full_text.split())
    script_sha256 = hashlib.sha256(script_path.read_bytes()).hexdigest()
    narration_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    core = {
        "schema_version": "history_narration.v1",
        "episode_id": episode_id,
        "source_storyboard_hash": canonical_sha256(
            {
                "source_script_path": script_path.as_posix(),
                "source_script_sha256": script_sha256,
            }
        ),
        "source_script_path": script_path.relative_to(ROOT.parent.parent).as_posix(),
        "source_script_sha256": script_sha256,
        "base_narration_hash": narration_hash,
        "research_hash": "",
        "source_kind": "finance_current_mechanism_script",
        "target_duration_s": target_duration_s,
        "segments": segments,
        "full_text": normalized,
        "total_words": len(WORD.findall(normalized)),
        "total_chars": len(normalized),
        "policy": {
            "canonical_text_owner": "script_draft_markdown",
            "packaging_and_source_notes_are_not_tts_input": True,
            "production_controls_are_not_tts_input": True,
            "single_continuous_take_required": True,
            "shorts_are_contiguous_windows_of_master": True,
        },
        "narration_hash": narration_hash,
    }
    payload = {**core, "artifact_hash": canonical_sha256(core)}
    validate_history_narration(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--episode-id", default="systems-and-blowups:current-bubble-mechanism")
    parser.add_argument("--target-duration-s", type=float, default=870.0)
    args = parser.parse_args()
    pilot = args.pilot.resolve()
    output = (
        args.output
        or pilot / "audio" / "current-bubble-mechanism-narration-master.v1.json"
    ).resolve()
    payload = compile_narration(
        pilot,
        output,
        episode_id=args.episode_id,
        target_duration_s=args.target_duration_s,
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "narration_hash": payload["narration_hash"],
                "total_words": payload["total_words"],
                "total_chars": payload["total_chars"],
                "segment_count": len(payload["segments"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
