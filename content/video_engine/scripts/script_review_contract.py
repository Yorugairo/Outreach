"""Stage-aware inventory for complete script review.

This module does not judge prose. It answers the mechanical question the old
runner could not answer: which review obligations apply, when are they due,
and what source owns each obligation? A missing semantic result is therefore
INCOMPLETE instead of being laundered into a mechanical PASS.

The inventory is derived from the existing responsibility contract and the
generated craft map. It is not a second writing doctrine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

import beat_tags


SCHEMA = "script_review_contract.v1"
STAGES = ("diagnostic", "scratch", "text-review", "prefix-preview", "recording")
Stage = Literal["diagnostic", "scratch", "text-review", "prefix-preview", "recording"]
STAGE_ORDER = {stage: index for index, stage in enumerate(STAGES)}

ROOT = Path(__file__).resolve().parents[3]
CRAFT_MAP = ROOT / "docs/CRAFT-MAP.jsonl"
RESPONSIBILITIES = "docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md"
FULL_MAP = "docs/content-video-engine/patterns/FULL-VIDEO-MAP.md"


@dataclass(frozen=True)
class Obligation:
    id: str
    owner: str
    due_stage: Stage
    evidence: str
    source: str
    forms: tuple[str, ...] = ("long", "short")


def _obligation(id_: str, owner: str, stage: Stage, evidence: str, source: str,
                forms: tuple[str, ...] = ("long", "short")) -> Obligation:
    return Obligation(id_, owner, stage, evidence, source, forms)


_STATIC: tuple[Obligation, ...] = (
    _obligation("tool:lint", "tool", "diagnostic", "raw checker result", f"{RESPONSIBILITIES}#2"),
    _obligation("tool:audit", "tool", "diagnostic", "raw checker result", f"{RESPONSIBILITIES}#2"),
    _obligation("tool:opening", "tool", "diagnostic", "raw checker result", f"{RESPONSIBILITIES}#2"),
    _obligation("tool:screens", "tool", "diagnostic", "enumerated screen artifact", f"{RESPONSIBILITIES}#2"),
    _obligation("mechanical:G36-broad-beat-activity", "tool", "diagnostic", "timed broad-cycle diagnostic", f"{RESPONSIBILITIES}#2"),
    *(_obligation(f"opening:{row}", "judge", "text-review", "quoted individual verdict", f"{RESPONSIBILITIES}#3b", ("long",))
      for row in (f"J{i:02d}" for i in range(1, 15))),
    *(_obligation(f"opening:{row}", "judge", "text-review", "quoted individual verdict", f"{RESPONSIBILITIES}#3b", ("short",))
      for row in ("J50", "J51")),
    *(_obligation(f"viewer:{row}", "blind-viewer", "text-review", "source-bound blind-viewer result", f"{RESPONSIBILITIES}#2")
      for row in ("V01", "V02", "V03", "V04", "V05")),
    *(_obligation(f"classical:{slug}", "judge", "text-review", "quoted semantic verdict", f"{RESPONSIBILITIES}#3c", ("long",))
      for slug in (
          "battle", "self-revelation", "new-equilibrium", "midpoint", "mckee-gap-engine",
          "glass-ratios", "ring-close", "counterpoint-modes", "foreshadow-delivery",
          "anaphora-arc", "tell-four-parts", "savor-and-dips", "best-evidence-position")),
    *(_obligation(f"roster:{slug}", "judge", "text-review", "count and verdict", f"{RESPONSIBILITIES}#3d", ("long",))
      for slug in (
          "foreshadows", "macro-loops", "str-micros-outside-p2", "callback-tokens",
          "head-fake-demolition", "dips", "savor-beats", "tricolon-terminality",
          "anaphora", "glass-ratio-per-phase")),
    *(_obligation(f"loop:{slug}", "judge", "text-review", "scale finding", f"{RESPONSIBILITIES}#3e")
      for slug in ("l1", "l2", "l3", "l6", "x1", "x2", "x3", "x4", "x5")),
    *(_obligation(f"reader:{row}", "judge", "text-review", "sentence-strength log", f"{RESPONSIBILITIES}#3f")
      for row in ("S1", "S4", "S6", "S8", "S10")),
    _obligation("surface:per-window-choice", "judge", "prefix-preview", "shot-table verdict per window", f"{RESPONSIBILITIES}#3g"),
    *(_obligation(f"editorial:{slug}", "judge", "text-review", "named verdict", f"{RESPONSIBILITIES}#3h")
      for slug in (
          "evidence-trace", "quotes-verbatim", "persona", "thesis-lens", "dated-references",
          "self-promises", "number-density", "register-read-aloud", "humanizer")),
    _obligation("ear:scratch-read", "judge", "recording", "hash-bound scratch and ear verdict", f"{RESPONSIBILITIES}#3h"),
    _obligation("map:narrative-map", "judge", "text-review", "validated narrative_map.v1", f"{FULL_MAP}#0", ("long",)),
    _obligation("map:first-180-continuity", "independent-reviewer", "text-review", "setup-tension-payoff-next-question review", f"{FULL_MAP}#0", ("long",)),
    _obligation("map:macro-phases", "independent-reviewer", "text-review", "phase relationship review", f"{FULL_MAP}#1", ("long",)),
    _obligation("timing:measured-word-clock", "tool", "recording", "hash-bound normalized word clock", f"{RESPONSIBILITIES}#R8"),
)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def annotated_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_spoken(text: str) -> str:
    return re.sub(r"\s+", " ", beat_tags.strip_marks(text)).strip()


def spoken_hash(text: str) -> str:
    return sha256_bytes(canonical_spoken(text).encode("utf-8"))


def load_craft_obligations(path: Path = CRAFT_MAP) -> list[Obligation]:
    """One review obligation per current craft-map row.

    The craft map may say a device has a mechanical gate. That gate remains
    useful, but it cannot replace the existing reader responsibility to decide
    whether the device works in this script.
    """
    rows: list[Obligation] = []
    if not path.is_file():
        raise FileNotFoundError(f"craft map missing: {path}")
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        item = json.loads(line)
        device = str(item.get("device") or "").strip()
        if not device:
            raise ValueError(f"craft map row {line_number} has no device")
        rows.append(_obligation(
            f"craft:{slug(device)}", "judge", "text-review", "device verdict with cited span",
            f"docs/CRAFT-MAP.jsonl:{line_number}",
        ))
    return rows


def declared_beat_obligations(text: str) -> list[Obligation]:
    counts: dict[str, int] = {}
    rows: list[Obligation] = []
    for tag, _offset in beat_tags.find_beats(text):
        counts[tag] = counts.get(tag, 0) + 1
        rows.append(_obligation(
            f"declared:{tag}:{counts[tag]}", "judge", "text-review",
            "exact quote and true/laundered verdict", f"{RESPONSIBILITIES}#3a",
        ))
    return rows


def screen_obligations(path: Path) -> list[Obligation]:
    """One judge obligation for every emitted strength-screen candidate."""
    if not path.is_file():
        raise FileNotFoundError(f"strength screens missing: {path}")
    section = ""
    rows: list[Obligation] = []
    section_names = {"X1": "x1", "P6": "deixis", "P1J": "junction",
                     "P5A": "phonetic", "P4C": "cadence"}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        heading = re.match(r"^##\s+(X1|P6|P1J|P5A|P4C)\b", line)
        if heading:
            section = section_names[heading.group(1)]
            continue
        item = re.match(r"^-\s+(?:\[(\d+)\]|¶(\d+):)", line)
        if section and item:
            identity = item.group(1) or item.group(2)
            rows.append(_obligation(
                f"screen:{section}:{identity}", "judge", "text-review",
                "per-item screen verdict", f"{path.as_posix()}:{line_number}",
            ))
    return rows


def obligations(text: str, form: str = "long", craft_map: Path = CRAFT_MAP,
                screens: Path | None = None) -> list[Obligation]:
    if form not in {"long", "short"}:
        raise ValueError("form must be 'long' or 'short'")
    rows = [row for row in _STATIC if form in row.forms]
    rows.extend(declared_beat_obligations(text))
    rows.extend(load_craft_obligations(craft_map))
    if screens is not None:
        rows.extend(screen_obligations(screens))
    ids = [row.id for row in rows]
    duplicates = sorted({id_ for id_ in ids if ids.count(id_) > 1})
    if duplicates:
        raise ValueError("duplicate obligation id(s): " + ", ".join(duplicates))
    return rows


def due_by(rows: Iterable[Obligation], stage: Stage) -> list[Obligation]:
    if stage not in STAGE_ORDER:
        raise ValueError(f"unknown stage: {stage}")
    return [row for row in rows if STAGE_ORDER[row.due_stage] <= STAGE_ORDER[stage]]


def contract_digest(rows: Iterable[Obligation]) -> str:
    payload = [asdict(row) for row in rows]
    return sha256_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def coverage_manifest(text: str, form: str = "long", craft_map: Path = CRAFT_MAP,
                      screens: Path | None = None) -> dict:
    rows = obligations(text, form, craft_map, screens)
    by_owner: dict[str, int] = {}
    by_stage: dict[str, int] = {}
    for row in rows:
        by_owner[row.owner] = by_owner.get(row.owner, 0) + 1
        by_stage[row.due_stage] = by_stage.get(row.due_stage, 0) + 1
    return {
        "schema": SCHEMA,
        "form": form,
        "annotated_script_hash": annotated_hash(text),
        "spoken_script_hash": spoken_hash(text),
        "contract_digest": contract_digest(rows),
        "counts": {"total": len(rows), "by_owner": by_owner, "by_stage": by_stage},
        "obligations": [asdict(row) for row in rows],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the stage-aware script review obligation inventory")
    parser.add_argument("script", type=Path)
    parser.add_argument("--form", choices=("long", "short"), default="long")
    parser.add_argument("--craft-map", type=Path, default=CRAFT_MAP)
    parser.add_argument("--screens", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    manifest = coverage_manifest(args.script.read_text(encoding="utf-8"), args.form, args.craft_map, args.screens)
    body = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(body, encoding="utf-8")
        print(f"{args.out}: {manifest['counts']['total']} obligations, {manifest['contract_digest']}")
    else:
        print(body, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
