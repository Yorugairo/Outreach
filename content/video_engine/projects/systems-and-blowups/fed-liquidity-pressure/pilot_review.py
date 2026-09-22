"""Episode-local, read-only PREFIX review adapter for Fed liquidity.

The adapter consumes reports produced by the existing gates.  It does not run
those gates, choose a timeline, or turn an excerpt into a whole-episode
verdict.  ``--check-inputs`` is intentionally side-effect free; normal mode
writes only the build-local ``PILOT-REVIEW.md``.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any


EPISODE_ROOT = Path(__file__).resolve().parent
SCOPE_NAME = "PILOT-CHECK-SCOPE.md"
RECEIPT_NAME = "BUILD-RECEIPT.json"
REVIEW_NAME = "PILOT-REVIEW.md"
TIMELINE_NAME = "fed-liquidity-pilot.timeline.json"
PILOT_SCENES_NAME = "PILOT-SCENES.md"
REPORT_NAMES = ("GATES-MOTION.md", "SELF-WATCH.md", "layout-probe.json", "seam-frames.json")
DEFERRED_IDS = frozenset({"M35", "M37", "M38", "M39"})
PRESERVED_IDS = frozenset({"M40", "M42"})
APPLICABLE_IDS = frozenset({f"M{i:02d}" for i in range(1, 35)} | {"M36", "M41"})
_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_TIME_RE = re.compile(r"(?<![A-Za-z0-9])(?:(?P<minute>\d{1,3}):(?P<second>\d{2}(?:\.\d+)?)|(?P<seconds>\d+(?:\.\d+)?)\s*s)\b")
_ANCHOR_TIME_RE = re.compile(
    r"\b(?:at|from|start(?:s|ing)?|t)\s*(?:=|:)??\s*"
    r"(?:(?P<minute>\d{1,3}):(?P<second>\d{2}(?:\.\d+)?)|(?P<seconds>\d+(?:\.\d+)?)\s*s)\b",
    re.I,
)
_RANGE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:\d{1,3}:\d{2}(?:\.\d+)?|\d+(?:\.\d+)?\s*s)\s*[-–]\s*"
    r"(?:\d{1,3}:\d{2}(?:\.\d+)?|\d+(?:\.\d+)?\s*s)",
    re.I,
)
_BRACKET_RE = re.compile(
    r"\[(?P<level>PASS|FAIL|WARN|JUDGE|INFO)\s*\]\s*"
    r"(?P<id>[A-Z]\d{2})\b(?P<detail>.*)",
    re.I,
)
_BRACKET_LEVEL_RE = re.compile(r"\[(?P<level>PASS|FAIL|WARN|JUDGE|INFO)\s*\]", re.I)
_TABLE_PAREN_RE = re.compile(
    r"\|\s*[^|]*\((?P<id>M\d{2})\)\s*\|\s*"
    r"(?P<level>PASS|FAIL|WARN|JUDGE|INFO)\s*\|\s*(?P<detail>[^|]*)",
    re.I,
)
_TABLE_LABEL_RE = re.compile(
    r"\|\s*(?P<label>[^|]*?\b(?P<id>M\d{2})\b[^|]*)\|\s*"
    r"(?P<level>PASS|FAIL|WARN|JUDGE|INFO)\s*\|\s*(?P<detail>[^|]*)",
    re.I,
)
_GATE_BUILD_RE = re.compile(r"^===\s*MOTION DENSITY GATE:\s*(?P<path>.+?)\s*===\s*$", re.I | re.M)
_GATE_TIMELINE_RE = re.compile(
    r"^TIMELINE:\s*(?P<name>\S+)\s+sha256:(?P<sha>[0-9a-fA-F]{64})\s*$", re.I | re.M
)
_SELF_HEADER_RE = re.compile(
    r"^#\s+SELF-WATCH\s+-\s+.+?\s+-\s+(?P<build>[^\s]+)\s+-\s+",
    re.I | re.M,
)
_SELF_META_RE = re.compile(
    r"^player\.html\s+sha256\s+(?P<player>[0-9a-fA-F]{12,64})\s+-\s+"
    r"timeline\s+(?P<timeline>\S+)\s+-\s+runtime\s+(?P<minutes>\d+):(?P<seconds>\d{2}(?:\.\d+)?)\b",
    re.I | re.M,
)
_SCENE_ROW_RE = re.compile(r"^\|\s*(?P<group>P0[1-6])\s*\|[^|]*\|\s*(?P<opening>[^|]+?)\s*\|\s*(?P<closing>[^|]+?)\s*\|", re.I)


@dataclass(frozen=True)
class RawRow:
    source: str
    line: int
    level: str
    row_id: str | None
    detail: str
    raw: str


@dataclass
class ReviewResult:
    build: Path
    mode: str
    status: str = "PREFIX BLOCKED"
    blockers: list[str] = field(default_factory=list)
    custody: list[dict[str, Any]] = field(default_factory=list)
    reports: list[dict[str, Any]] = field(default_factory=list)
    rows: list[dict[str, Any]] = field(default_factory=list)
    prefix: dict[str, Any] = field(default_factory=dict)
    timeline_runtime_s: float | None = None
    parent_reads: dict[str, Any] = field(default_factory=dict)
    word_clock: dict[str, Any] = field(default_factory=dict)
    report_bindings: dict[str, str] = field(default_factory=dict)
    script_path: Path | None = None
    timeline_sha256: str | None = None
    player_sha256: str | None = None

    @property
    def ok(self) -> bool:
        return not self.blockers and self.status == "PREFIX READY_FOR_PARENT_READ"

    def add(self, message: str) -> None:
        if message not in self.blockers:
            self.blockers.append(message)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "fed-liquidity.prefix-review.v1",
            "status": self.status,
            "mode": self.mode,
            "build": self.build.name,
            "prefix": self.prefix,
            "timeline_runtime_s": self.timeline_runtime_s,
            "word_clock_duration_s": self.word_clock.get("duration_s"),
            "parent_reads": self.parent_reads,
            "custody": self.custody,
            "reports": self.reports,
            "rows": self.rows,
            "blockers": self.blockers,
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, ValueError):
        return False


def _read_json(path: Path, label: str, result: ReviewResult) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result.add(f"{label}: missing ({path.name})")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result.add(f"{label}: invalid JSON ({exc})")
    return None


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_ref(root: Path, raw: Any, label: str, result: ReviewResult) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        result.add(f"{label}: relative path is missing")
        return None
    supplied = Path(raw)
    if supplied.is_absolute():
        result.add(f"{label}: path must be episode-relative")
        return None
    candidate = (root / supplied).resolve()
    if not _inside(root.resolve(), candidate):
        result.add(f"{label}: path escapes episode root")
        return None
    return candidate


def _check_ref(root: Path, value: Any, label: str, result: ReviewResult) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        result.add(f"{label}: custody object is missing")
        return None
    path = _resolve_ref(root, value.get("path"), f"{label}.path", result)
    expected = value.get("sha256")
    if not isinstance(expected, str) or not _HASH_RE.fullmatch(expected):
        result.add(f"{label}.sha256: must be 64 hexadecimal characters")
        expected = None
    if path is None or expected is None:
        return None
    if not path.is_file():
        result.add(f"{label}: file missing ({value.get('path')})")
        return None
    try:
        actual = _sha256(path)
    except OSError as exc:
        result.add(f"{label}: cannot read ({exc})")
        return None
    if actual.lower() != expected.lower():
        result.add(f"{label}: sha256 mismatch (expected {expected.lower()}, got {actual})")
    return {"label": label, "path": path.relative_to(root).as_posix(), "sha256": actual}


def _normalised_tokens(text: str) -> list[str]:
    """Return the spoken token shape used by the episode's word-clock check."""
    text = re.sub(r"`?\[[^\]]+\]`?", " ", text)
    text = text.replace("’", "'")
    return [token.lower() for token in re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", text.lower())]


def _word_clock_tokens(words: list[dict[str, Any]]) -> tuple[list[str], list[int]]:
    tokens: list[str] = []
    word_indices: list[int] = []
    for index, item in enumerate(words):
        item_tokens = _normalised_tokens(str(item.get("w", "")))
        tokens.extend(item_tokens)
        word_indices.extend([index] * len(item_tokens))
    return tokens, word_indices


def _load_word_clock(path: Path, label: str, script_path: Path | None, result: ReviewResult) -> dict[str, Any] | None:
    data = _read_json(path, label, result)
    if not isinstance(data, dict):
        result.add(f"{label}: word clock must be a JSON object")
        return None
    words = data.get("words")
    duration = data.get("duration_s", data.get("runtime_s"))
    valid = True
    if not isinstance(words, list) or not words:
        result.add(f"{label}: words must be a non-empty array")
        valid = False
        words = []
    if not _finite(duration) or float(duration) <= 0:
        result.add(f"{label}: duration_s/runtime_s must be a finite positive number")
        valid = False
        duration_value = None
    else:
        duration_value = float(duration)
    previous_start = -math.inf
    previous_end = -math.inf
    clean_words: list[dict[str, Any]] = []
    for index, item in enumerate(words):
        if not isinstance(item, dict):
            result.add(f"{label}: word {index} must be an object")
            valid = False
            continue
        if not str(item.get("w", "")).strip():
            result.add(f"{label}: word {index} text is required")
            valid = False
        start = item.get("start_s")
        end = item.get("end_s")
        if not _finite(start) or not _finite(end):
            result.add(f"{label}: word {index} has non-finite timing")
            valid = False
            continue
        start_value, end_value = float(start), float(end)
        if start_value < 0 or end_value < start_value:
            result.add(f"{label}: word {index} has invalid span")
            valid = False
        if start_value < previous_start or end_value < previous_end:
            result.add(f"{label}: word {index} is not monotone")
            valid = False
        if duration_value is not None and end_value > duration_value + 1e-6:
            result.add(f"{label}: word {index} ends after duration_s")
            valid = False
        previous_start, previous_end = start_value, end_value
        clean_words.append(item)
    if script_path is not None and script_path.is_file() and clean_words:
        try:
            expected = _normalised_tokens(script_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            result.add(f"{label}: cannot read bound script ({exc})")
            valid = False
        else:
            actual, _ = _word_clock_tokens(clean_words)
            if expected != actual:
                result.add(f"{label}: spoken tokens do not match bound script")
                valid = False
    if not valid:
        return None
    result.word_clock = {"duration_s": duration_value, "words": clean_words}
    return data


def _derive_prefix_interval(root: Path, result: ReviewResult) -> dict[str, Any] | None:
    """Resolve S09's original closing anchor on the bound selected take clock."""
    path = root / PILOT_SCENES_NAME
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        result.add(f"prefix interval: missing ({PILOT_SCENES_NAME})")
        return None
    except (OSError, UnicodeError) as exc:
        result.add(f"prefix interval: cannot read ({exc})")
        return None
    rows: dict[str, tuple[str, str, str]] = {}
    for line in text.splitlines():
        match = _SCENE_ROW_RE.match(line)
        if match:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 5:
                rows[match.group("group").upper()] = (cells[1], cells[2], cells[3])
    p06 = rows.get("P06")
    if p06 is None:
        result.add("prefix interval: P06/S09 anchor row is missing")
        return None
    beats, opening, closing = p06
    if beats != "S09":
        result.add("prefix interval: P06 must bind original S09")
        return None
    words = result.word_clock.get("words")
    if not isinstance(words, list) or not words:
        result.add("prefix interval: bound word clock is unavailable")
        return None
    tokens, word_indices = _word_clock_tokens(words)

    def locate(phrase: str, label: str) -> tuple[int, int] | None:
        wanted = _normalised_tokens(phrase)
        if not wanted:
            result.add(f"prefix interval: {label} anchor is empty")
            return None
        hits = [
            index
            for index in range(len(tokens) - len(wanted) + 1)
            if tokens[index:index + len(wanted)] == wanted
        ]
        if len(hits) != 1:
            result.add(f"prefix interval: {label} anchor is not unique ({len(hits)} matches)")
            return None
        start = hits[0]
        return start, start + len(wanted)

    opening_span = locate(opening, "P06 opening")
    closing_span = locate(closing, "P06 closing")
    if opening_span is None or closing_span is None:
        return None
    opening_start, opening_end = opening_span
    closing_start, closing_end = closing_span
    if closing_start < opening_start or closing_end <= opening_end:
        result.add("prefix interval: P06 closing anchor precedes opening anchor")
        return None
    try:
        start_word = words[word_indices[opening_start]]
        end_word = words[word_indices[closing_end - 1]]
        start_s = float(start_word["start_s"])
        end_s = float(end_word["end_s"])
    except (KeyError, TypeError, ValueError, IndexError):
        result.add("prefix interval: anchor has no measured word span")
        return None
    if not _finite(start_s) or not _finite(end_s) or end_s <= start_s:
        result.add("prefix interval: measured S09 span is invalid")
        return None
    closing_word_index = word_indices[closing_end - 1]
    next_start_s = None
    if closing_word_index + 1 < len(words):
        next_word = words[closing_word_index + 1]
        next_start_s = float(next_word["start_s"])
    else:
        next_start_s = float(result.word_clock["duration_s"])
    if next_start_s < end_s - 1e-6:
        result.add("prefix interval: next spoken word overlaps P06 closing word")
    result.prefix["derived_start_s"] = start_s
    result.prefix["derived_spoken_end_s"] = end_s
    result.prefix["derived_end_word_index"] = closing_word_index
    result.prefix["derived_next_word_start_s"] = next_start_s
    return {
        "spoken_end_s": end_s,
        "end_word_index": closing_word_index,
        "next_start_s": next_start_s,
    }


def _load_scope(path: Path, result: ReviewResult) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        result.add(f"scope: missing ({path.name})")
        return
    except (OSError, UnicodeError) as exc:
        result.add(f"scope: cannot read ({exc})")
        return
    required_markers = (
        "fed-liquidity.prefix-scope.v1",
        TIMELINE_NAME,
        "M01-M34",
        "M36",
        "M41",
        "M35",
        "M37",
        "M38",
        "M39",
        "M40",
        "M42",
    )
    for marker in required_markers:
        if marker not in text:
            result.add(f"scope: required policy marker missing ({marker})")


def _read_parent_read_evidence(path: Path, label: str, result: ReviewResult) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        result.add(f"{label}: missing ({path.name})")
        return None
    except (OSError, UnicodeError) as exc:
        result.add(f"{label}: cannot read ({exc})")
        return None
    if not text.strip():
        result.add(f"{label}: evidence must be non-empty JSON")
        return None
    try:
        data = json.loads(text)
    except (UnicodeError, json.JSONDecodeError) as exc:
        result.add(f"{label}: invalid JSON ({exc})")
        return None
    if not isinstance(data, dict):
        result.add(f"{label}: evidence must be a JSON object")
        return None
    return data


def _validate_parent_read_evidence(
    data: dict[str, Any],
    *,
    kind: str,
    receipt_hashes: dict[str, str],
    label: str,
    result: ReviewResult,
) -> None:
    if data.get("schema") != "fed-liquidity.parent-read.v1":
        result.add(f"{label}.schema: must be fed-liquidity.parent-read.v1")
    if data.get("kind") != kind:
        result.add(f"{label}.kind: must be {kind}")
    observations = data.get("observations")
    if not isinstance(observations, list) or not observations:
        result.add(f"{label}.observations: must be a non-empty array")

    digest_fields = (
        ("timeline_sha256", "timeline"),
        ("script_sha256", "script"),
        ("audio_sha256", "take.audio"),
    )
    for field_name, receipt_label in digest_fields:
        value = data.get(field_name)
        if not isinstance(value, str) or not _HASH_RE.fullmatch(value):
            result.add(f"{label}.{field_name}: must be 64 hexadecimal characters")
            continue
        expected = receipt_hashes.get(receipt_label)
        if expected is not None and value.lower() != expected.lower():
            result.add(f"{label}.{field_name}: must match receipt {receipt_label} sha256")


def _load_receipt(build: Path, root: Path, receipt_path: Path, result: ReviewResult) -> dict[str, Any] | None:
    data = _read_json(receipt_path, "build receipt", result)
    if not isinstance(data, dict):
        return None
    if data.get("schema") != "fed-liquidity.build-receipt.v1":
        result.add("build receipt: schema must be fed-liquidity.build-receipt.v1")

    refs: list[tuple[str, Any]] = [
        ("script", data.get("script")),
        ("take.audio", data.get("take", {}).get("audio") if isinstance(data.get("take"), dict) else None),
        ("take.words", data.get("take", {}).get("words") if isinstance(data.get("take"), dict) else None),
        ("timeline", data.get("timeline")),
        ("player", data.get("player")),
        (
            "assets.manifest",
            data.get("assets", {}).get("manifest") if isinstance(data.get("assets"), dict) else None,
        ),
    ]
    receipt_hashes: dict[str, str] = {}
    if not isinstance(data.get("take"), dict) or not isinstance(data["take"].get("id"), str) or not data["take"]["id"].strip():
        result.add("build receipt: take.id is required")
    for label, value in refs:
        checked = _check_ref(root, value, label, result)
        if checked:
            result.custody.append(checked)
            receipt_hashes[label] = checked["sha256"]
            if label == "script":
                result.script_path = root / checked["path"]
            elif label == "timeline":
                result.timeline_sha256 = checked["sha256"]
            elif label == "player":
                result.player_sha256 = checked["sha256"]

    report_refs = data.get("reports")
    if not isinstance(report_refs, list) or not report_refs:
        result.add("build receipt: reports must be a non-empty array of raw report custody refs")
    else:
        seen_reports: set[str] = set()
        for index, value in enumerate(report_refs):
            label = f"reports[{index}]"
            checked = _check_ref(root, value, label, result)
            if checked is None:
                continue
            path = Path(checked["path"])
            if path.parent != build.resolve().relative_to(root.resolve()) or path.name not in REPORT_NAMES:
                result.add(f"{label}: path must name a declared report directly in the build")
                continue
            if path.name in seen_reports:
                result.add(f"build receipt: duplicate raw report custody ref ({path.name})")
                continue
            seen_reports.add(path.name)
            result.report_bindings[path.name] = checked["sha256"]
            result.custody.append(checked)
        for name in REPORT_NAMES:
            if name not in seen_reports:
                result.add(f"build receipt: raw report custody missing ({name})")

    words_ref = data.get("take", {}).get("words") if isinstance(data.get("take"), dict) else None
    if isinstance(words_ref, dict):
        words_path = _resolve_ref(root, words_ref.get("path"), "take.words.path", result)
        if words_path is not None and result.script_path is not None:
            _load_word_clock(words_path, "take word clock", result.script_path, result)

    for field_name in ("source_custody", "asset_custody"):
        entries = data.get(field_name)
        if not isinstance(entries, list) or not entries:
            result.add(f"build receipt: {field_name} must be a non-empty array")
            continue
        for index, value in enumerate(entries):
            checked = _check_ref(root, value, f"{field_name}[{index}]", result)
            if checked:
                result.custody.append(checked)

    prefix = data.get("prefix")
    if not isinstance(prefix, dict):
        result.add("build receipt: prefix object is required")
    else:
        expected_sections = [f"S{i:02d}" for i in range(1, 10)]
        if prefix.get("sections") != expected_sections:
            result.add("build receipt: prefix.sections must be S01 through S09 in order")
        if prefix.get("start_s") != 0:
            result.add("build receipt: prefix.start_s must be zero")
        if not _finite(prefix.get("end_s")) or float(prefix["end_s"]) <= 0:
            result.add("build receipt: prefix.end_s must be a finite measured positive number")
        if not _finite(prefix.get("spoken_end_s")) or float(prefix["spoken_end_s"]) <= 0:
            result.add("build receipt: prefix.spoken_end_s must be a finite measured positive number")
        if isinstance(prefix.get("end_word_index"), bool) or not isinstance(prefix.get("end_word_index"), int) or prefix.get("end_word_index") < 0:
            result.add("build receipt: prefix.end_word_index must be a non-negative integer")
        if prefix.get("measured_from") != "take-word-clock":
            result.add("build receipt: prefix.measured_from must be take-word-clock")
        result.prefix = {
            "sections": prefix.get("sections"),
            "start_s": prefix.get("start_s"),
            "end_s": prefix.get("end_s"),
            "spoken_end_s": prefix.get("spoken_end_s"),
            "end_word_index": prefix.get("end_word_index"),
            "measured_from": prefix.get("measured_from"),
        }

    reads = data.get("parent_reads")
    if not isinstance(reads, dict):
        result.add("build receipt: parent_reads object is required")
    else:
        result.parent_reads = reads
        for kind in ("visual", "audio"):
            read = reads.get(kind)
            if not isinstance(read, dict) or read.get("status") != "READ":
                result.add(f"parent read: {kind} must have status READ")
                continue
            evidence = read.get("evidence")
            evidence_label = f"parent read: {kind}.evidence"
            if not isinstance(evidence, dict):
                result.add(f"{evidence_label}: custody object is required")
            else:
                checked = _check_ref(root, evidence, evidence_label, result)
                if checked:
                    result.custody.append(checked)
                    evidence_data = _read_parent_read_evidence(root / checked["path"], evidence_label, result)
                    if evidence_data is not None:
                        _validate_parent_read_evidence(
                            evidence_data,
                            kind=kind,
                            receipt_hashes=receipt_hashes,
                            label=evidence_label,
                            result=result,
                        )
            if not isinstance(read.get("read_at"), str) or not read["read_at"].strip():
                result.add(f"parent read: {kind}.read_at is required")

    timeline_ref = data.get("timeline")
    if isinstance(timeline_ref, dict) and isinstance(timeline_ref.get("path"), str):
        timeline_path = _resolve_ref(root, timeline_ref["path"], "timeline.path", result)
        if timeline_path is not None and (timeline_path.parent != build.resolve() or timeline_path.name != TIMELINE_NAME):
            result.add(f"timeline: receipt must name {TIMELINE_NAME} directly in the build")
    return data


def _validate_timeline(build: Path, root: Path, receipt: dict[str, Any] | None, result: ReviewResult) -> None:
    candidates = sorted(build.glob("*.timeline.json")) if build.is_dir() else []
    if len(candidates) != 1:
        result.add(f"timeline: expected exactly one *.timeline.json, found {len(candidates)}")
        return
    timeline_path = candidates[0]
    if timeline_path.name != TIMELINE_NAME:
        result.add(f"timeline: expected {TIMELINE_NAME}, found {timeline_path.name}")
    if receipt is not None:
        ref = receipt.get("timeline")
        if not isinstance(ref, dict) or ref.get("path") is None:
            result.add("timeline: receipt path is missing")
        else:
            resolved = _resolve_ref(root, ref.get("path"), "timeline.path", result)
            if resolved is not None and resolved != timeline_path.resolve():
                result.add("timeline: receipt path does not match the sole compiled timeline")
    timeline_data = _read_json(timeline_path, "compiled timeline", result)
    if not isinstance(timeline_data, dict):
        return
    runtime = timeline_data.get("runtime_s", timeline_data.get("duration_s"))
    if not _finite(runtime) or float(runtime) <= 0:
        result.add("compiled timeline: runtime_s/duration_s must be finite and positive")
    else:
        result.timeline_runtime_s = float(runtime)
    if timeline_data.get("schema_version") is not None and timeline_data.get("schema_version") != "scene_evidence_timeline.v1":
        result.add("compiled timeline: schema_version must be scene_evidence_timeline.v1")
    interval = _derive_prefix_interval(root, result)
    reported_end = result.prefix.get("end_s")
    if interval is not None:
        spoken_end = interval["spoken_end_s"]
        end_word_index = interval["end_word_index"]
        upper_bound = interval["next_start_s"]
        supplied_spoken_end = result.prefix.get("spoken_end_s")
        supplied_word_index = result.prefix.get("end_word_index")
        if not _finite(supplied_spoken_end) or abs(float(supplied_spoken_end) - spoken_end) > 1e-6:
            result.add("prefix: spoken_end_s does not match measured P06/S09 closing word")
        if isinstance(supplied_word_index, bool) or not isinstance(supplied_word_index, int) or supplied_word_index != end_word_index:
            result.add("prefix: end_word_index does not match measured P06/S09 closing word")
        if not _finite(reported_end):
            result.add("prefix: end_s must be finite")
        else:
            reported_end_value = float(reported_end)
            if reported_end_value < spoken_end - 1e-6:
                result.add("prefix: end_s precedes measured spoken end")
            if _finite(upper_bound) and reported_end_value > float(upper_bound) + 1e-6:
                result.add("prefix: end_s crosses the next spoken word or take duration")
    if result.timeline_runtime_s is not None and _finite(reported_end) and float(reported_end) > result.timeline_runtime_s + 1e-6:
        result.add("prefix: measured end exceeds reviewed timeline runtime")


def _validate_reports(build: Path, result: ReviewResult) -> dict[str, str]:
    digests: dict[str, str] = {}
    for name in REPORT_NAMES:
        path = build / name
        if not path.is_file():
            result.add(f"raw report: missing ({name})")
            continue
        try:
            digest = _sha256(path)
        except OSError as exc:
            result.add(f"raw report: cannot read {name} ({exc})")
            continue
        digests[name] = digest
        result.reports.append({"path": name, "sha256": digest})
        expected_digest = result.report_bindings.get(name)
        if expected_digest is None:
            result.add(f"raw report {name}: receipt custody binding is missing")
        elif digest.lower() != expected_digest.lower():
            result.add(f"raw report {name}: sha256 does not match receipt custody")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            result.add(f"raw report {name}: cannot parse ({exc})")
            continue
        if not text.strip():
            result.add(f"raw report {name}: report is empty")
            continue
        if name in {"GATES-MOTION.md", "SELF-WATCH.md"}:
            try:
                rows = _parse_rows(path)
            except (OSError, UnicodeError) as exc:
                result.add(f"raw report {name}: cannot parse ({exc})")
                rows = []
            if not rows:
                result.add(f"raw report {name}: no parseable gate rows")
        if name == "GATES-MOTION.md":
            gate_build = _GATE_BUILD_RE.search(text)
            if gate_build is None:
                result.add("raw report GATES-MOTION.md: build binding is missing")
            else:
                supplied = re.split(r"[\\/]", gate_build.group("path").rstrip("\\/"))[-1]
                if supplied != build.name:
                    result.add("raw report GATES-MOTION.md: build binding does not match reviewed build")
            timeline = _GATE_TIMELINE_RE.findall(text)
            if len(timeline) != 1:
                result.add("raw report GATES-MOTION.md: exact timeline binding is missing")
            else:
                timeline_name, timeline_sha = timeline[0]
                if timeline_name != TIMELINE_NAME:
                    result.add(f"raw report GATES-MOTION.md: timeline must be {TIMELINE_NAME}")
                if result.timeline_sha256 is not None and timeline_sha.lower() != result.timeline_sha256.lower():
                    result.add("raw report GATES-MOTION.md: timeline sha256 does not match receipt")
            if not re.search(r"^RESULT:\s*\d+\s+FAIL\b", text, re.I | re.M):
                result.add("raw report GATES-MOTION.md: RESULT line is missing")
        elif name == "SELF-WATCH.md":
            header = _SELF_HEADER_RE.search(text)
            if header is None or header.group("build") != build.name:
                result.add("raw report SELF-WATCH.md: build binding does not match reviewed build")
            meta = _SELF_META_RE.search(text)
            if meta is None:
                result.add("raw report SELF-WATCH.md: timeline/player binding is missing")
            else:
                if meta.group("timeline") != TIMELINE_NAME:
                    result.add(f"raw report SELF-WATCH.md: timeline must be {TIMELINE_NAME}")
                player = meta.group("player").lower()
                if result.player_sha256 is not None and not result.player_sha256.lower().startswith(player):
                    result.add("raw report SELF-WATCH.md: player sha256 does not match receipt")
                runtime = float(meta.group("minutes")) * 60.0 + float(meta.group("seconds"))
                if result.timeline_runtime_s is not None and abs(runtime - result.timeline_runtime_s) > 1.1:
                    result.add("raw report SELF-WATCH.md: runtime does not match bound word clock")
        elif path.suffix.lower() == ".json":
            data = _read_json(path, f"raw report {name}", result)
            if data in ({}, [], ""):
                result.add(f"raw report {name}: JSON must be non-empty")
            if not isinstance(data, dict):
                result.add(f"raw report {name}: JSON must be an object")
            else:
                if name == "layout-probe.json" and data.get("timeline") != TIMELINE_NAME:
                    result.add(f"raw report {name}: timeline must be {TIMELINE_NAME}")
                if name == "layout-probe.json":
                    player = data.get("player_sha256")
                    if not isinstance(player, str) or not _HASH_RE.fullmatch(player):
                        result.add("raw report layout-probe.json: player_sha256 is missing or invalid")
                    elif result.player_sha256 is not None and player.lower() != result.player_sha256.lower():
                        result.add("raw report layout-probe.json: player sha256 does not match receipt")
                elif name == "seam-frames.json":
                    if data.get("build") != build.name:
                        result.add("raw report seam-frames.json: build binding does not match reviewed build")
                    runtime = data.get("runtime_s")
                    if not _finite(runtime) or float(runtime) <= 0:
                        result.add("raw report seam-frames.json: runtime_s is missing or invalid")
                    elif result.timeline_runtime_s is not None and abs(float(runtime) - result.timeline_runtime_s) > 1e-6:
                        result.add("raw report seam-frames.json: runtime does not match bound word clock")
    return digests


def _time_value(match: re.Match[str]) -> float:
    if match.group("minute") is not None:
        return float(match.group("minute")) * 60.0 + float(match.group("second"))
    return float(match.group("seconds"))


def _failure_time(detail: str) -> tuple[float | None, str | None]:
    """Return a clearly anchored time, or an explicit ambiguity reason."""
    anchored = list(_ANCHOR_TIME_RE.finditer(detail))
    if anchored:
        return _time_value(anchored[0]), None
    if _RANGE_RE.search(detail):
        return None, "time range is ambiguous"
    candidates = list(_TIME_RE.finditer(detail))
    if len(candidates) == 1:
        return _time_value(candidates[0]), None
    if not candidates:
        return None, "no explicit timestamp"
    return None, "multiple unanchored timestamps"


def _parse_rows(path: Path) -> list[RawRow]:
    rows: list[RawRow] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        known = False
        for match in _BRACKET_RE.finditer(line):
            known = True
            rows.append(RawRow(path.name, line_number, match.group("level").upper(), match.group("id").upper(), match.group("detail").strip(), line))
        table_match = _TABLE_PAREN_RE.search(line) or _TABLE_LABEL_RE.search(line)
        if table_match and not re.search(r"M\d{2}\s*[-–]\s*M\d{2}", table_match.group(0), re.I):
            known = True
            rows.append(RawRow(path.name, line_number, table_match.group("level").upper(), table_match.group("id").upper(), table_match.group("detail").strip(), line))
        if not known and _BRACKET_LEVEL_RE.search(line):
            level = _BRACKET_LEVEL_RE.search(line).group("level").upper()
            rows.append(RawRow(path.name, line_number, level, None, line.strip(), line))
        if not known and re.search(r"\|\s*(?:[^|]*\bFAIL\b)\s*\|", line, re.I) and not line.lstrip().upper().startswith(("RESULT", "VERDICT")):
            rows.append(RawRow(path.name, line_number, "FAIL", None, line.strip(), line))
    return rows


def _classify_rows(build: Path, mode: str, result: ReviewResult) -> None:
    all_rows: list[RawRow] = []
    for report in REPORT_NAMES[:2]:
        path = build / report
        if path.is_file():
            try:
                all_rows.extend(_parse_rows(path))
            except (OSError, UnicodeError) as exc:
                result.add(f"raw report {report}: cannot parse ({exc})")
    prefix_end = float(result.prefix["end_s"]) if _finite(result.prefix.get("end_s")) else None
    for row in all_rows:
        classification = "PRESERVED"
        reason = "raw row retained"
        row_id = row.row_id
        if row_id in DEFERRED_IDS:
            classification = "FULL_EPISODE_DEFERRED" if mode == "prefix" else "FULL_SCOPE"
            reason = "whole-cut floor; not a prefix passing row" if mode == "prefix" else "full mode must evaluate this row"
            if mode == "full":
                result.add(f"full mode: prefix deferral is forbidden ({row_id})")
        elif row_id in PRESERVED_IDS:
            expected = "JUDGE" if row_id == "M40" else "INFO"
            if row.level != expected:
                result.add(f"{row_id}: expected {expected}, found {row.level}")
            classification = "PRESERVED_SEMANTICS"
            reason = f"{row_id} remains {expected}"
        elif row.level == "FAIL" and row_id is None:
            classification = "UNKNOWN_FAIL"
            reason = "failure has no recognized row id"
            result.add(f"{row.source}:{row.line}: unknown FAIL")
        elif row.level == "FAIL" and row_id not in APPLICABLE_IDS:
            classification = "UNEXPECTED_FAIL"
            reason = "failure is outside the named prefix policy"
            result.add(f"{row.source}:{row.line}: unexpected FAIL {row_id or '<unknown>'}")
        elif row.level == "FAIL" and row_id in APPLICABLE_IDS:
            at_s, time_reason = _failure_time(row.detail)
            if time_reason is not None or at_s is None or prefix_end is None:
                classification = "UNKNOWN_LOCATION"
                reason = time_reason or "prefix boundary unavailable"
                result.add(f"{row.source}:{row.line}: {row_id} FAIL location is not explicit ({reason})")
            elif at_s <= prefix_end:
                classification = "WITHIN_PREFIX_FAIL"
                reason = f"failure at {at_s:.3f}s is within prefix end {prefix_end:.3f}s"
                result.add(f"{row_id} FAIL occurs inside measured prefix at {at_s:.3f}s")
            else:
                classification = "OUTSIDE_PREFIX"
                reason = f"explicit failure at {at_s:.3f}s is outside prefix"
        result.rows.append({
            "source": row.source,
            "line": row.line,
            "id": row_id,
            "level": row.level,
            "classification": classification,
            "reason": reason,
            "detail": row.detail,
        })


def inspect_build(
    build: Path,
    *,
    mode: str = "prefix",
    scope_path: Path | None = None,
    receipt_path: Path | None = None,
) -> ReviewResult:
    """Inspect existing artifacts only; no gate, renderer, or subprocess call is made."""
    build = Path(build).resolve()
    result = ReviewResult(build=build, mode=mode)
    if mode not in {"prefix", "full"}:
        result.add(f"mode: unsupported value {mode}")
    if not build.is_dir():
        result.add(f"build: missing directory ({build})")
        return result
    root = build.parent
    scope = (scope_path or (root / SCOPE_NAME)).resolve()
    receipt = (receipt_path or (build / RECEIPT_NAME)).resolve()
    _load_scope(scope, result)
    receipt_data = _load_receipt(build, root, receipt, result)
    _validate_timeline(build, root, receipt_data, result)
    _validate_reports(build, result)
    _classify_rows(build, mode, result)
    if result.blockers:
        result.status = "PREFIX BLOCKED"
    elif any(row["classification"] == "WITHIN_PREFIX_FAIL" for row in result.rows):
        result.status = "PREFIX FAIL"
    else:
        result.status = "PREFIX READY_FOR_PARENT_READ"
    return result


def render_report(result: ReviewResult) -> str:
    """Render deterministic review output while leaving all source reports untouched."""
    lines = [
        "# PREFIX — Fed liquidity pilot review",
        "",
        f"VERDICT: {result.status}",
        f"build: {result.build.name}",
        f"mode: {result.mode}",
        "raw reports: read-only; no raw report was rewritten",
        "",
        "## measured prefix",
        f"sections: {','.join(result.prefix.get('sections') or [])}",
        f"start_s: {result.prefix.get('start_s')}",
        f"end_s: {result.prefix.get('end_s')}",
        f"spoken_end_s: {result.prefix.get('spoken_end_s')}",
        f"end_word_index: {result.prefix.get('end_word_index')}",
        f"derived_next_word_start_s: {result.prefix.get('derived_next_word_start_s')}",
        f"measured_from: {result.prefix.get('measured_from')}",
        f"timeline_runtime_s: {result.timeline_runtime_s}",
        "",
        "## custody",
    ]
    for item in result.custody + result.reports:
        lines.append(f"- {item['path']} sha256:{item['sha256']}")
    lines.extend(["", "## parent reads"])
    for kind in ("visual", "audio"):
        read = result.parent_reads.get(kind, {}) if isinstance(result.parent_reads, dict) else {}
        evidence = read.get("evidence", "")
        if isinstance(evidence, dict):
            evidence = evidence.get("path", "")
        lines.append(f"- {kind}: {read.get('status', 'MISSING')} — {evidence}")
    lines.extend(["", "## raw row classification", "| source | line | id | level | classification | detail |", "|---|---:|---|---|---|---|"])
    for row in result.rows:
        detail = str(row["detail"]).replace("|", "\\|")
        lines.append(f"| {row['source']} | {row['line']} | {row['id'] or 'UNKNOWN'} | {row['level']} | {row['classification']} | {detail} |")
    lines.extend(["", "## blockers"])
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")
    lines.extend(["", "This is an episode-prefix diagnostic artifact; whole-cut floors remain for the full episode.", ""])
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Fed liquidity PREFIX review adapter")
    parser.add_argument("--build", type=Path, required=True, help="build directory containing named raw reports")
    parser.add_argument("--mode", choices=("prefix", "full"), default="prefix")
    parser.add_argument("--scope", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--receipt", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--check-inputs", action="store_true", help="validate without writing PILOT-REVIEW.md")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = inspect_build(args.build, mode=args.mode, scope_path=args.scope, receipt_path=args.receipt)
    if args.check_inputs:
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
        return 0 if result.ok else 1
    if result.build.is_dir():
        (result.build / REVIEW_NAME).write_text(render_report(result), encoding="utf-8", newline="\n")
        print(f"{result.status}: {result.build / REVIEW_NAME}")
    else:
        print(f"{result.status}: build directory is missing", file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
