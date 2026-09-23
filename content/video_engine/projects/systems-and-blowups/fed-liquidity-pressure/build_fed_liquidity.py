"""Preflight and episode-local assembly for the Fed liquidity prefix.

The input door stays fail-closed: a segment is assembled only after the
current script, same-take word clock, source objects, and explicit HG2 asset
custody all pass.  Assembly then uses the existing authoring kit and compiler
to write a private bed/unit/pilot build; it never creates a take, approves an
asset, or changes shared engine code.  ``SELECTED-ASSETS.json`` remains an
operator-authored input.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable


EPISODE_ROOT = Path(__file__).resolve().parent
TAKE_STEM = "scratch-kokoro"
CLAIMS_NAME = "claims.v1.json"
ASSET_SPEC_NAME = "ASSET-CLAIM-SPEC.json"
SELECTED_ASSETS_NAME = "SELECTED-ASSETS.json"
SCRIPT_NAME = "SCRIPT-VO.txt"
GATES_NAME = "SCRIPT-GATES.md"
VIEWER_NAME = "SCRIPT-VIEWER.md"
VIEWER_WINDOWS_NAME = "SCRIPT-VIEWER-WINDOWS.json"
VIEWER_REPORTS_NAME = "SCRIPT-VIEWER-REPORTS.json"
WORDS_NAME = "scratch-kokoro.words.json"
AUDIO_NAME = "scratch-kokoro.mp3"
RECEIPT_NAME = "BUILD-RECEIPT.json"
TABLE_NAME = "SHOT-TABLE-PILOT.py"
TABLE_NAMES = {
    "bed": TABLE_NAME,
    "unit": TABLE_NAME,
    "pilot": TABLE_NAME,
    "minute": "SHOT-TABLE-MINUTE.py",
}
TIMELINE_NAMES = {
    "bed": "fed-liquidity-bed.timeline.json",
    "unit": "fed-liquidity-unit.timeline.json",
    "pilot": "fed-liquidity-pilot.timeline.json",
    "minute": "fed-liquidity-minute.timeline.json",
}
BUILD_NAMES = {segment: f"build-{segment}" for segment in TIMELINE_NAMES}
ASSEMBLY_SEGMENTS = frozenset(TIMELINE_NAMES)
# The prefix keeps a short, real-silence tail after its closing word.  The
# following measured onset (or measured media duration at a final word) must
# prove that this tail exists; it is never stretched or padded into existence.
SILENCE_TAIL_S = 0.45
LEGACY_TAKE_NAMES = frozenset({"vo-scratch-r131", "vo-scratch-r1337", "vo-scratch-r135", "vo-scratch-r138"})
SOURCE_OBJECT_IDS = (
    "fed-assets-reserves-history",
    "fed-assets-reserves-change",
    "fed-on-rrp-history",
    "debt-wall-2025-2027",
    "fed-runoff-offsets",
)

_SCRIPT_HASH_RE = re.compile(r"^script_hash:\s*([0-9a-f]{64})\s*$", re.I | re.M)
_RESULT_FAIL_RE = re.compile(r"RESULT:\s*(\d+)\s+FAIL\b", re.I)
_SCREEN_LINE_RE = re.compile(r"^\s*\[screen\].*$", re.M)

# The approved logical scope is fixed here.  The episode spec remains useful
# for prompts and semantics, but it must not be able to redefine the custody
# obligation by changing its slots.  The former registered-layer IDs are kept
# only so a stale manifest fails with an explicit superseded-contract error.
APPROVED_ASSET_IDS = (
    "w2-owner-workshop-world-v1",
    "w4-finance-evidence-hall-v1",
    "p2-owner-loan-folio-v1",
)
SUPERSEDED_LAYER_ASSET_IDS = frozenset(
    {
        "w2-owner-workshop-background-v1",
        "w2-owner-workshop-mid-v1",
        "w2-owner-workshop-subject-v1",
        "w4-repo-counter-background-v1",
        "w4-repo-counter-mid-v1",
        "w4-repo-counter-subject-v1",
    }
)
VIEWER_WINDOWS_SCHEMA = "viewer_windows.v1"
VIEWER_REPORTS_SCHEMA = "viewer_reports.v1"
SELECTED_ASSETS_SCHEMA = "mp-fed-liquidity.selected-assets.v1"
ASSET_APPROVAL_SCHEMA = "mp-fed-liquidity.asset-approval.v1"
ASSET_APPROVAL_KEYS = frozenset(
    {
        "schema_version",
        "episode_id",
        "asset_id",
        "asset_path",
        "asset_sha256",
        "operator_decision",
        "approved_at",
        "approval_basis",
        "render_eligible",
        "artifact_hash",
    }
)
BUILD_RECEIPT_SCHEMA = "fed-liquidity.build-receipt.v1"

_REPO_ROOT = Path(__file__).resolve().parents[5]
_SCRIPTS_DIR = _REPO_ROOT / "content" / "video_engine" / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import beat_tags  # type: ignore  # noqa: E402
import viewer_windows  # type: ignore  # noqa: E402
from authoring import Project  # type: ignore  # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W  # type: ignore  # noqa: E402


_SHOT_TABLE_SPEC = importlib.util.spec_from_file_location(
    "fed_liquidity_shot_table_pilot", EPISODE_ROOT / TABLE_NAME
)
if _SHOT_TABLE_SPEC is None or _SHOT_TABLE_SPEC.loader is None:
    raise ImportError(f"cannot load episode shot table {EPISODE_ROOT / TABLE_NAME}")
SHOT_TABLE_PILOT = importlib.util.module_from_spec(_SHOT_TABLE_SPEC)
sys.modules[_SHOT_TABLE_SPEC.name] = SHOT_TABLE_PILOT
_SHOT_TABLE_SPEC.loader.exec_module(SHOT_TABLE_PILOT)

# Keep the existing pilot module eagerly loaded for byte-identical bed/unit/
# pilot behavior.  The minute table is parent-authored and is deliberately
# loaded only when the minute segment is requested.
_SHOT_TABLES: dict[str, Any] = {
    "bed": SHOT_TABLE_PILOT,
    "unit": SHOT_TABLE_PILOT,
    "pilot": SHOT_TABLE_PILOT,
}


def _shot_table_for(segment: str) -> Any:
    """Return the authored table for one segment, loading minute lazily."""
    table = _SHOT_TABLES.get(segment)
    if table is not None:
        return table
    table_name = TABLE_NAMES.get(segment)
    if table_name is None:
        raise ValueError(f"assembly: unsupported segment {segment!r}")
    path = EPISODE_ROOT / table_name
    spec = importlib.util.spec_from_file_location(
        f"fed_liquidity_shot_table_{segment}", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load episode shot table {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise ImportError(f"cannot load episode shot table {path}: {exc}") from exc
    _SHOT_TABLES[segment] = module
    return module


def _validate_segment_table(segment: str, result: PreflightResult) -> None:
    """Fail closed when a segment table is missing its compiler-facing API."""
    if segment != "minute":
        return
    try:
        table = _shot_table_for(segment)
        required = (
            "SEGMENT_GROUPS",
            "AUTHORING_STATUS",
            "specs_for",
            "build_rows",
            "group_ranges",
            "group_end_phrase",
        )
        missing = [name for name in required if not hasattr(table, name)]
        if missing:
            result.add(f"minute shot table: missing interface ({', '.join(missing)})")
            return
        groups = table.SEGMENT_GROUPS.get(segment)
        if not isinstance(groups, tuple) or not groups:
            result.add("minute shot table: SEGMENT_GROUPS['minute'] must be a non-empty tuple")
    except (AttributeError, ImportError, OSError, SyntaxError, TypeError, ValueError) as exc:
        result.add(f"minute shot table: cannot load ({exc})")

_PILOT_SCRIPT_REVIEW_SPEC = importlib.util.spec_from_file_location(
    "fed_liquidity_pilot_script_review", EPISODE_ROOT / "pilot_script_review.py"
)
if _PILOT_SCRIPT_REVIEW_SPEC is None or _PILOT_SCRIPT_REVIEW_SPEC.loader is None:
    raise ImportError(f"cannot load episode pilot script review {EPISODE_ROOT / 'pilot_script_review.py'}")
PILOT_SCRIPT_REVIEW = importlib.util.module_from_spec(_PILOT_SCRIPT_REVIEW_SPEC)
sys.modules[_PILOT_SCRIPT_REVIEW_SPEC.name] = PILOT_SCRIPT_REVIEW
_PILOT_SCRIPT_REVIEW_SPEC.loader.exec_module(PILOT_SCRIPT_REVIEW)

_PILOT_VIEWER_REVIEW_SPEC = importlib.util.spec_from_file_location(
    "fed_liquidity_pilot_viewer_review", EPISODE_ROOT / "pilot_viewer_review.py"
)
if _PILOT_VIEWER_REVIEW_SPEC is None or _PILOT_VIEWER_REVIEW_SPEC.loader is None:
    raise ImportError(f"cannot load episode pilot viewer review {EPISODE_ROOT / 'pilot_viewer_review.py'}")
PILOT_VIEWER_REVIEW = importlib.util.module_from_spec(_PILOT_VIEWER_REVIEW_SPEC)
sys.modules[_PILOT_VIEWER_REVIEW_SPEC.name] = PILOT_VIEWER_REVIEW
_PILOT_VIEWER_REVIEW_SPEC.loader.exec_module(PILOT_VIEWER_REVIEW)


@dataclass
class PreflightResult:
    """Structured, non-mutating result suitable for the CLI and tests."""

    segment: str
    blockers: list[str] = field(default_factory=list)
    facts: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.blockers

    def add(self, message: str) -> None:
        if message not in self.blockers:
            self.blockers.append(message)

    def lines(self) -> list[str]:
        lines = [f"segment: {self.segment}"]
        if self.facts:
            lines.append("facts:")
            lines.extend(f"  {key}: {value}" for key, value in self.facts.items())
        if self.blockers:
            lines.append("blockers:")
            lines.extend(f"  - {message}" for message in self.blockers)
        else:
            lines.append("preflight: PASS")
        return lines


@dataclass(frozen=True)
class SegmentBoundary:
    """A prefix cut bound to the selected take's measured word clock."""

    end_s: float
    end_word_index: int
    closing_phrase: str
    spoken_end_s: float
    next_word_start_s: float | None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _relative_path(root: Path, raw: Any, label: str, result: PreflightResult) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        result.add(f"{label}: relative path is missing")
        return None
    supplied = Path(raw)
    if supplied.is_absolute():
        result.add(f"{label}: path must be episode-relative ({raw})")
        return None
    candidate = (root / supplied).resolve()
    if not _inside(root.resolve(), candidate):
        result.add(f"{label}: path escapes episode root ({raw})")
        return None
    return candidate


def _canonical_relative_path(root: Path, raw: Any, label: str, result: PreflightResult) -> tuple[Path | None, str | None]:
    """Resolve a contained episode path and its stable manifest spelling."""
    path = _relative_path(root, raw, label, result)
    if path is None:
        return None, None
    return path, path.relative_to(root.resolve()).as_posix()


class _DuplicateJsonKey(ValueError):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


class _NonFiniteJsonConstant(ValueError):
    def __init__(self, literal: str) -> None:
        self.literal = literal
        super().__init__(literal)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in pairs:
        if key in values:
            raise _DuplicateJsonKey(key)
        values[key] = value
    return values


def _finite_json_float(raw: str) -> float:
    value = float(raw)
    if not math.isfinite(value):
        raise _NonFiniteJsonConstant(raw)
    return value


def _reject_json_constant(raw: str) -> None:
    raise _NonFiniteJsonConstant(raw)


def _json(path: Path, label: str, result: PreflightResult) -> Any | None:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
            parse_float=_finite_json_float,
            parse_constant=_reject_json_constant,
        )
    except FileNotFoundError:
        result.add(f"{label}: missing ({path.name})")
    except _DuplicateJsonKey as exc:
        result.add(f"{label}: duplicate JSON key {exc.key!r}")
    except _NonFiniteJsonConstant as exc:
        result.add(f"{label}: non-finite JSON constant {exc.literal!r}")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result.add(f"{label}: invalid JSON ({exc})")
    return None


def _hash_reference(root: Path, raw_path: Any, expected: Any, label: str, result: PreflightResult) -> None:
    path = _relative_path(root, raw_path, label, result)
    if path is None:
        return
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        result.add(f"{label}: sha256 must be 64 hexadecimal characters")
        return
    if not path.is_file():
        result.add(f"{label}: file missing ({raw_path})")
        return
    try:
        actual = _sha256(path)
    except OSError as exc:
        result.add(f"{label}: cannot read file ({exc})")
        return
    if actual.lower() != expected.lower():
        result.add(f"{label}: sha256 mismatch (expected {expected}, got {actual})")


def _walk_hash_references(root: Path, value: Any, result: PreflightResult, label: str = "claims") -> None:
    """Verify every path-bearing reference has a matching hash."""
    if isinstance(value, dict):
        if "path" in value or "sha256" in value:
            if "path" in value and "sha256" in value:
                _hash_reference(root, value.get("path"), value.get("sha256"), f"{label}.path", result)
            elif "path" in value:
                result.add(f"{label}: sha256 is missing")
            elif "sha256" in value:
                result.add(f"{label}: path is missing")
        if "metadata_path" in value or "metadata_sha256" in value:
            if "metadata_path" in value and "metadata_sha256" in value:
                _hash_reference(root, value.get("metadata_path"), value.get("metadata_sha256"), f"{label}.metadata_path", result)
            elif "metadata_path" in value:
                result.add(f"{label}: metadata_sha256 is missing")
            else:
                result.add(f"{label}: metadata_path is missing")
        for key, child in value.items():
            _walk_hash_references(root, child, result, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_hash_references(root, child, result, f"{label}[{index}]")


def _window_matches(value: Any, expected: tuple[str, str]) -> bool:
    return isinstance(value, dict) and value.get("start") == expected[0] and value.get("end") == expected[1]


def _validate_claims(root: Path, result: PreflightResult) -> dict[str, Any] | None:
    path = root / CLAIMS_NAME
    data = _json(path, "claims manifest", result)
    if not isinstance(data, dict):
        return None
    if data.get("schema") != "mp-fed-liquidity.claims.v1":
        result.add("claims manifest: schema must be mp-fed-liquidity.claims.v1")
    claims = data.get("claims")
    if not isinstance(claims, list):
        result.add("claims manifest: claims must be an array")
        return data

    _walk_hash_references(root, data, result)
    by_id: dict[str, dict[str, Any]] = {}
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            result.add(f"claims manifest: claim {index} must be an object")
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            result.add(f"claims manifest: claim {index} is missing id")
            continue
        if claim_id in by_id:
            result.add(f"claims manifest: duplicate claim_id {claim_id}")
            continue
        by_id[claim_id] = claim
    required = {"C1-C2", "C3", "C5-funding-data"}
    missing = sorted(required - by_id.keys())
    if missing:
        result.add(f"claims manifest: missing required claims {', '.join(missing)}")

    c1 = by_id.get("C1-C2")
    if isinstance(c1, dict):
        if c1.get("units") != "USD billions":
            result.add("C1-C2: units must be USD billions")
        if c1.get("cutoff") != "2026-09-18":
            result.add("C1-C2: cutoff must be 2026-09-18")

    c3 = by_id.get("C3")
    if isinstance(c3, dict):
        if c3.get("units") != "USD billions":
            result.add("C3: units must be USD billions")
        if not _window_matches(c3.get("window"), ("2022-06-01", "2025-06-11")):
            result.add("C3: window must be 2022-06-01 through 2025-06-11")

    c5 = by_id.get("C5-funding-data")
    if isinstance(c5, dict):
        rates = c5.get("rates")
        if not isinstance(rates, dict) or not _window_matches(rates.get("window"), ("2025-09-02", "2026-09-17")):
            result.add("C5 funding rates: window must be 2025-09-02 through 2026-09-17")
        repo = c5.get("repo_take_up")
        if not isinstance(repo, dict) or repo.get("units") != "USD":
            result.add("C5 repo take-up: units must be USD")
        if not isinstance(repo, dict) or not _window_matches(repo.get("window"), ("2026-09-01", "2026-09-18")):
            result.add("C5 repo take-up: window must be 2026-09-01 through 2026-09-18")
    return data


def _slot_ids(spec: Any, result: PreflightResult) -> list[str]:
    if not isinstance(spec, dict) or not isinstance(spec.get("slots"), list):
        result.add("asset claim spec: slots must be an array")
        return []
    ids: list[str] = []
    for index, slot in enumerate(spec["slots"]):
        if not isinstance(slot, dict) or not isinstance(slot.get("asset_id"), str) or not slot["asset_id"].strip():
            result.add(f"asset claim spec: slot {index} has no asset_id")
            continue
        ids.append(slot["asset_id"])
    if SUPERSEDED_LAYER_ASSET_IDS.intersection(ids):
        result.add(
            "asset claim spec: superseded seven-layer contract is not accepted; "
            "use the three complete-world asset IDs"
        )
    if len(ids) != len(set(ids)):
        result.add("asset claim spec: asset_id values must be unique")
    if len(ids) != len(APPROVED_ASSET_IDS):
        result.add(f"asset claim spec: expected {len(APPROVED_ASSET_IDS)} logical asset IDs, found {len(ids)}")
    if set(ids) != set(APPROVED_ASSET_IDS):
        result.add("asset claim spec: logical asset IDs must match approved scope")
    return list(APPROVED_ASSET_IDS)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _approval_artifact_hash(payload: dict[str, Any]) -> str:
    unsigned = dict(payload)
    unsigned.pop("artifact_hash", None)
    return hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()


def _timezone_iso_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _validate_approval_artifact(
    asset_id: str,
    asset_path: Path | None,
    asset_relative_path: str | None,
    asset_sha256: Any,
    approval_path: Path | None,
    result: PreflightResult,
) -> None:
    """Validate the explicit operator artifact, never a worker completion flag."""
    if approval_path is None or not approval_path.is_file():
        return
    approval = _json(approval_path, f"selected approval {asset_id} artifact", result)
    if not isinstance(approval, dict):
        return
    if set(approval) != ASSET_APPROVAL_KEYS:
        result.add(f"selected approval {asset_id}: fields must match the operator approval contract")
    if approval.get("schema_version") != ASSET_APPROVAL_SCHEMA:
        result.add(f"selected approval {asset_id}: schema_version must be {ASSET_APPROVAL_SCHEMA}")
    if approval.get("episode_id") != "fed-liquidity-pressure":
        result.add(f"selected approval {asset_id}: episode_id binding is invalid")
    if approval.get("asset_id") != asset_id:
        result.add(f"selected approval {asset_id}: asset_id binding is invalid")
    if asset_relative_path is not None and approval.get("asset_path") != asset_relative_path:
        result.add(f"selected approval {asset_id}: asset_path binding is invalid")
    approval_asset_sha256 = approval.get("asset_sha256")
    if not isinstance(approval_asset_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", approval_asset_sha256):
        result.add(f"selected approval {asset_id}: asset_sha256 must be 64 hexadecimal characters")
    elif isinstance(asset_sha256, str) and approval_asset_sha256.lower() != asset_sha256.lower():
        result.add(f"selected approval {asset_id}: asset_sha256 does not match selected manifest")
    if approval.get("operator_decision") != "approved_for_composition":
        result.add(f"selected approval {asset_id}: explicit operator_decision is required")
    if not _timezone_iso_timestamp(approval.get("approved_at")):
        result.add(f"selected approval {asset_id}: approved_at must be an ISO-8601 timestamp with timezone")
    if not isinstance(approval.get("approval_basis"), str) or not approval["approval_basis"].strip():
        result.add(f"selected approval {asset_id}: approval_basis must be non-empty")
    if approval.get("render_eligible") is not True:
        result.add(f"selected approval {asset_id}: render_eligible must be true")
    artifact_hash = approval.get("artifact_hash")
    if not isinstance(artifact_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", artifact_hash):
        result.add(f"selected approval {asset_id}: artifact_hash must be 64 hexadecimal characters")
    else:
        try:
            expected = _approval_artifact_hash(approval)
        except (TypeError, ValueError):
            result.add(f"selected approval {asset_id}: artifact payload is not canonical JSON")
        else:
            if artifact_hash.lower() != expected:
                result.add(f"selected approval {asset_id}: artifact_hash mismatch")
    if asset_path is not None and asset_path.is_file():
        try:
            actual_asset_sha256 = _sha256(asset_path)
        except OSError as exc:
            result.add(f"selected approval {asset_id}: cannot re-read bound asset ({exc})")
        else:
            if isinstance(approval_asset_sha256, str) and approval_asset_sha256.lower() != actual_asset_sha256:
                result.add(f"selected approval {asset_id}: asset_sha256 does not match current asset bytes")


def _validate_selected_assets(root: Path, result: PreflightResult) -> None:
    spec = _json(root / ASSET_SPEC_NAME, "asset claim spec", result)
    required_ids = _slot_ids(spec, result)
    selected_path = root / SELECTED_ASSETS_NAME
    if not selected_path.exists():
        # This exact wording is an operator-facing gate: do not substitute a
        # V5 review package or a quarantined candidate manifest here.
        result.add("selected asset manifest missing; HG2 pending")
        return
    selected = _json(selected_path, "selected asset manifest", result)
    if not isinstance(selected, dict):
        return
    if selected.get("schema") != SELECTED_ASSETS_SCHEMA:
        result.add(f"selected asset manifest: schema must be {SELECTED_ASSETS_SCHEMA}")
    assets = selected.get("assets")
    if not isinstance(assets, list):
        result.add("selected asset manifest: assets must be an array")
        return
    if len(assets) != len(required_ids):
        result.add(f"selected asset manifest: expected {len(required_ids)} assets, found {len(assets)}")
    by_id: dict[str, dict[str, Any]] = {}
    seen_asset_paths: set[str] = set()
    seen_approval_paths: set[str] = set()
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            result.add(f"selected asset manifest: asset {index} must be an object")
            continue
        asset_id = asset.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id:
            result.add(f"selected asset manifest: asset {index} is missing asset_id")
            continue
        if asset_id in by_id:
            result.add(f"selected asset manifest: duplicate asset_id {asset_id}")
            continue
        by_id[asset_id] = asset
        for field_name in ("path", "sha256", "approval_path", "approval_sha256"):
            if field_name not in asset:
                result.add(f"selected asset manifest: {asset_id} missing {field_name}")
        asset_path, asset_relative_path = _canonical_relative_path(
            root, asset.get("path"), f"selected asset {asset_id}", result
        )
        approval_path, approval_relative_path = _canonical_relative_path(
            root, asset.get("approval_path"), f"selected approval {asset_id}", result
        )
        _hash_reference(
            root, asset.get("path"), asset.get("sha256"), f"selected asset {asset_id}", result
        )
        _hash_reference(
            root,
            asset.get("approval_path"),
            asset.get("approval_sha256"),
            f"selected approval {asset_id}",
            result,
        )
        if asset_relative_path is not None:
            if asset_relative_path in seen_asset_paths:
                result.add(f"selected asset manifest: duplicate asset path {asset_relative_path}")
            seen_asset_paths.add(asset_relative_path)
        if approval_relative_path is not None:
            if approval_relative_path in seen_approval_paths:
                result.add(f"selected asset manifest: duplicate approval path {approval_relative_path}")
            seen_approval_paths.add(approval_relative_path)
        _validate_approval_artifact(
            asset_id,
            asset_path,
            asset_relative_path,
            asset.get("sha256"),
            approval_path,
            result,
        )
    actual_ids = set(by_id)
    required_set = set(required_ids)
    if SUPERSEDED_LAYER_ASSET_IDS.intersection(actual_ids):
        result.add(
            "selected asset manifest: superseded seven-layer IDs are not accepted; "
            "use the three complete-world asset IDs"
        )
    for asset_id in sorted(required_set - actual_ids):
        result.add(f"selected asset manifest: missing required asset_id {asset_id}")
    for asset_id in sorted(actual_ids - required_set):
        result.add(f"selected asset manifest: unexpected asset_id {asset_id}")


def _canonical_spoken(text: str) -> str:
    # Match run_script_gates.py: structural tags are removed first, then
    # delivery pause marks are removed before hashing and token comparison.
    text = beat_tags.strip_beat_tags(text)
    text = re.sub(r"`?\[(?:pre|post)-key\]`?", "", text)
    return re.sub(r"\s+", " ", text).strip()


def script_hash(text: str) -> str:
    return hashlib.sha256(_canonical_spoken(text).encode("utf-8")).hexdigest()


def _file_digest(path: Path) -> str | None:
    try:
        return _sha256(path) if path.is_file() else None
    except OSError:
        return None


def _find_script_hash(text: str) -> str | None:
    match = _SCRIPT_HASH_RE.search(text)
    return match.group(1).lower() if match else None


def _scan_optional_hashes(value: Any, names: Iterable[str]) -> list[str]:
    wanted = set(names)
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in wanted and isinstance(child, str):
                found.append(child.lower())
            found.extend(_scan_optional_hashes(child, names))
    elif isinstance(value, list):
        for child in value:
            found.extend(_scan_optional_hashes(child, names))
    return found


def _validate_viewer_pair(root: Path, result: PreflightResult) -> None:
    windows_doc = _json(root / VIEWER_WINDOWS_NAME, "viewer windows", result)
    reports_doc = _json(root / VIEWER_REPORTS_NAME, "viewer reports", result)
    if not isinstance(windows_doc, dict) or not isinstance(reports_doc, dict):
        return
    for doc, schema in ((windows_doc, VIEWER_WINDOWS_SCHEMA), (reports_doc, VIEWER_REPORTS_SCHEMA)):
        if doc.get("schema_version") != schema or doc.get("script") != SCRIPT_NAME:
            result.add(f"viewer: invalid {schema} identity")
    windows, reports = windows_doc.get("windows"), reports_doc.get("reports")
    if not isinstance(windows, list) or not windows or not isinstance(reports, list):
        result.add("viewer: nonempty windows and reports arrays required")
        return
    if len(reports) != len(windows) or reports_doc.get("windows_run") != len(windows):
        result.add("viewer: report count does not cover all windows")
    if reports_doc.get("windows_file") != VIEWER_WINDOWS_NAME:
        result.add("viewer: reports reference a different windows file")
    for label, rows in (("windows", windows), ("reports", reports)):
        if any(not isinstance(row, dict) or type(row.get("i")) is not int or row["i"] != i for i, row in enumerate(rows)):
            result.add(f"viewer: {label} indices must be contiguous and unique")
            return
        if any("error" in row for row in rows):
            result.add(f"viewer: {label} contains an error entry")
    for window, report in zip(windows, reports):
        if not window.get("span") or report.get("span") != window["span"]:
            result.add("viewer: report/window span mismatch")
    if any(not isinstance(row.get("text"), str) for row in windows):
        result.add("viewer: window text is missing")
        return
    script = root / SCRIPT_NAME
    if script.is_file():
        expected = viewer_windows.spoken(script.read_text(encoding="utf-8")).split()
        observed = " ".join(_SCREEN_LINE_RE.sub("", row["text"]) for row in windows).split()
        if expected != observed:
            result.add("viewer: window text does not match current spoken script")
    result.facts["viewer_windows_checked"] = len(windows)


def _validate_script_and_reports(
    root: Path,
    result: PreflightResult,
    segment: str = "episode",
) -> tuple[Path | None, str | None, dict[str, str | None]]:
    script_path = root / SCRIPT_NAME
    current_hash: str | None = None
    if not script_path.is_file():
        result.add(f"script: missing ({SCRIPT_NAME})")
    else:
        try:
            current_hash = script_hash(script_path.read_text(encoding="utf-8"))
            result.facts["script_hash"] = current_hash
        except (OSError, UnicodeError) as exc:
            result.add(f"script: cannot read ({exc})")

    gates_path = root / GATES_NAME
    gate_text = ""
    if not gates_path.is_file():
        result.add(f"script gates: missing ({GATES_NAME})")
    else:
        try:
            gate_text = gates_path.read_text(encoding="utf-8")
            verdicts = re.findall(r"^VERDICT:\s*(PASS|FAIL)\b", gate_text, re.M)
            recorded = _find_script_hash(gate_text)
            if recorded is None:
                result.add("script gates: current script_hash is missing")
            elif current_hash is not None and recorded != current_hash:
                result.add(f"script gates: stale script_hash (expected {current_hash}, got {recorded})")
            fail_counts = [int(match) for match in _RESULT_FAIL_RE.findall(gate_text)]
            gate_failed = verdicts != ["PASS"] or any(count for count in fail_counts)
            exception_accepted = False
            if gate_failed and segment in PILOT_SCRIPT_REVIEW.ELIGIBLE_SEGMENTS:
                review = PILOT_SCRIPT_REVIEW.validate(root, expected_script_hash=current_hash)
                if review.ok:
                    exception_accepted = True
                    result.facts["script_gate_exception"] = (
                        f"{PILOT_SCRIPT_REVIEW.SCHEMA}; accepted_for=pilot_only"
                    )
                else:
                    for error in review.errors:
                        result.add(f"script gates: pilot exception: {error}")
            if not exception_accepted:
                if verdicts != ["PASS"]:
                    result.add("script gates: exactly one explicit PASS verdict is required")
                if any(count for count in fail_counts):
                    result.add("script gates: report contains FAIL")
        except (OSError, UnicodeError) as exc:
            result.add(f"script gates: cannot read ({exc})")

    viewer_path = root / VIEWER_NAME
    viewer_text = ""
    if not viewer_path.is_file():
        result.add(f"script viewer: missing ({VIEWER_NAME})")
    else:
        try:
            viewer_text = viewer_path.read_text(encoding="utf-8")
            viewer_hash = _find_script_hash(viewer_text)
            if viewer_hash is not None and current_hash is not None and viewer_hash != current_hash:
                result.add(f"script viewer: stale script_hash (expected {current_hash}, got {viewer_hash})")
            fail_counts = [int(match) for match in _RESULT_FAIL_RE.findall(viewer_text)]
            viewer_failed = any(count for count in fail_counts)
            viewer_exception_accepted = False
            if viewer_failed and segment in PILOT_VIEWER_REVIEW.ELIGIBLE_SEGMENTS:
                review = PILOT_VIEWER_REVIEW.validate(root, expected_script_hash=current_hash)
                if review.ok:
                    viewer_exception_accepted = True
                    result.facts["viewer_gate_exception"] = (
                        f"{PILOT_VIEWER_REVIEW.SCHEMA}; accepted_for=pilot_only"
                    )
                else:
                    for error in review.errors:
                        result.add(f"script viewer: pilot exception: {error}")
            if viewer_failed and not viewer_exception_accepted:
                result.add("script viewer: report contains FAIL")
        except (OSError, UnicodeError) as exc:
            result.add(f"script viewer: cannot read ({exc})")

    for filename in (VIEWER_WINDOWS_NAME, VIEWER_REPORTS_NAME):
        data = _json(root / filename, f"script viewer {filename}", result)
        if isinstance(data, dict):
            script_ref = data.get("script")
            if script_ref not in (None, SCRIPT_NAME, Path(SCRIPT_NAME).name):
                result.add(f"script viewer {filename}: script must be {SCRIPT_NAME}")
            for recorded in _scan_optional_hashes(data, ("script_hash", "script_sha256")):
                if current_hash is not None and recorded != current_hash:
                    result.add(f"script viewer {filename}: stale script hash ({recorded})")

    _validate_viewer_pair(root, result)
    return script_path, current_hash, {
        "gates_digest": _file_digest(gates_path),
        "viewer_digest": _file_digest(viewer_path),
    }


def ffprobe_duration(path: Path) -> float:
    """Return the media duration without touching the media file."""
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(completed.stdout.strip())


def _normalised_tokens(text: str) -> list[str]:
    # Matching is only a source/clock identity check.  It ignores punctuation
    # and case, but never invents or reorders a spoken token.
    lowered = text.lower().replace("’", "'")
    return [token for token in re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", lowered)]


def _word_tokens(words: list[dict[str, Any]]) -> list[str]:
    return _normalised_tokens(" ".join(str(item.get("w", "")) for item in words))


def _validate_take(
    root: Path,
    take_dir: Path,
    result: PreflightResult,
    script_path: Path | None,
    current_script_hash: str | None,
    report_digests: dict[str, str | None],
) -> list[dict[str, Any]]:
    audio_path = take_dir / AUDIO_NAME
    words_path = take_dir / WORDS_NAME
    if not audio_path.is_file():
        result.add(f"take: audio missing ({audio_path})")
    data = _json(words_path, "take word clock", result)
    if not isinstance(data, dict):
        return []
    words = data.get("words")
    duration = data.get("duration_s")
    if not isinstance(words, list) or not words:
        result.add("take word clock: words must be a non-empty array")
        words = []
    if not _finite_number(duration) or float(duration) <= 0:
        result.add("take word clock: duration_s must be a finite positive number")
        duration_value = None
    else:
        duration_value = float(duration)

    previous_start = -math.inf
    previous_end = -math.inf
    clean_words: list[dict[str, Any]] = []
    for index, item in enumerate(words):
        if not isinstance(item, dict):
            result.add(f"take word clock: word {index} must be an object")
            continue
        start = item.get("start_s")
        end = item.get("end_s")
        if not _finite_number(start) or not _finite_number(end):
            result.add(f"take word clock: word {index} has non-finite timing")
            continue
        start_value, end_value = float(start), float(end)
        if start_value < 0 or end_value < start_value:
            result.add(f"take word clock: word {index} has invalid span")
        if start_value < previous_start or end_value < previous_end:
            result.add(f"take word clock: word {index} is not monotone")
        if duration_value is not None and end_value > duration_value + 1e-6:
            result.add(f"take word clock: word {index} ends after duration_s")
        previous_start, previous_end = start_value, end_value
        clean_words.append(item)
    if duration_value is not None and clean_words:
        first = clean_words[0]
        if _finite_number(first.get("start_s")) and float(first["start_s"]) < 0:
            result.add("take word clock: first word starts before zero")
        measured_wpm = len(clean_words) / duration_value * 60.0
        result.facts["take_words"] = len(clean_words)
        result.facts["take_duration_s"] = round(duration_value, 3)
        result.facts["take_wpm"] = round(measured_wpm, 2)
        if not 170.0 <= measured_wpm <= 180.0:
            result.add(f"take word clock: measured WPM {measured_wpm:.2f} is outside 170–180")

    if script_path is not None:
        try:
            expected_tokens = _normalised_tokens(_canonical_spoken(script_path.read_text(encoding="utf-8")))
            actual_tokens = _word_tokens(clean_words)
            if expected_tokens != actual_tokens:
                mismatch = next((index for index, (left, right) in enumerate(zip(expected_tokens, actual_tokens)) if left != right), min(len(expected_tokens), len(actual_tokens)))
                result.add(f"take: spoken tokens do not match SCRIPT-VO.txt at token {mismatch} ({len(expected_tokens)} vs {len(actual_tokens)})")
            result.facts["take_script_match"] = expected_tokens == actual_tokens
        except (OSError, UnicodeError) as exc:
            result.add(f"take: cannot compare script tokens ({exc})")

    if current_script_hash is not None:
        for field_name in ("script_hash", "script_sha256"):
            if field_name in data and data[field_name] != current_script_hash:
                result.add(f"take: stale {field_name} (expected {current_script_hash}, got {data[field_name]})")
    gate_digest = report_digests.get("gates_digest")
    viewer_digest = report_digests.get("viewer_digest")
    if "gates_hash" in data and data["gates_hash"] not in (gate_digest, current_script_hash):
        result.add("take: stale gates_hash")
    if "gate_hash" in data and data["gate_hash"] not in (gate_digest, current_script_hash):
        result.add("take: stale gate_hash")
    if "viewer_hash" in data and data["viewer_hash"] != viewer_digest:
        result.add("take: stale viewer_hash")
    if "viewer_sha256" in data and data["viewer_sha256"] != viewer_digest:
        result.add("take: stale viewer_sha256")

    if audio_path.is_file() and duration_value is not None:
        try:
            actual_duration = ffprobe_duration(audio_path)
            result.facts["audio_duration_s"] = round(actual_duration, 3)
            tolerance = max(0.15, duration_value * 0.005)
            if not math.isfinite(actual_duration) or actual_duration <= 0:
                result.add("take audio: ffprobe duration is not finite and positive")
            elif abs(actual_duration - duration_value) > tolerance:
                result.add(f"take audio: ffprobe duration {actual_duration:.3f}s disagrees with word-clock {duration_value:.3f}s")
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            result.add(f"take audio: ffprobe failed ({exc})")

    return clean_words


def _anchor_rows(path: Path, result: PreflightResult) -> dict[str, tuple[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        result.add(f"pilot anchors: cannot read ({exc})")
        return {}
    rows: dict[str, tuple[str, str]] = {}
    for line in lines:
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not re.fullmatch(r"P0[1-6]", cells[0]):
            continue
        rows[cells[0]] = (cells[2], cells[3])
    if set(rows) != {f"P0{i}" for i in range(1, 7)}:
        result.add("pilot anchors: P01–P06 opening/closing rows are incomplete")
    return rows


def _find_anchor(tokens: list[str], phrase: str) -> list[tuple[int, int]]:
    wanted = _normalised_tokens(phrase)
    if not wanted:
        return []
    return [(index, index + len(wanted)) for index in range(len(tokens) - len(wanted) + 1) if tokens[index:index + len(wanted)] == wanted]


def _validate_anchors(root: Path, words: list[dict[str, Any]], result: PreflightResult) -> None:
    rows = _anchor_rows(root / "PILOT-SCENES.md", result)
    if not rows or not words:
        return
    tokens = _word_tokens(words)
    # `_word_tokens` can collapse punctuation, so map its normalized token
    # indices back to the source word records for measured times.
    normalized_by_word: list[str] = []
    token_word_indices: list[int] = []
    for word_index, item in enumerate(words):
        tokens_for_word = _normalised_tokens(str(item.get("w", "")))
        normalized_by_word.extend(tokens_for_word)
        token_word_indices.extend([word_index] * len(tokens_for_word))
    if len(normalized_by_word) != len(tokens):
        result.add("pilot anchors: word token normalization is inconsistent")
        return
    resolved: dict[str, dict[str, Any]] = {}
    for group, (opening, closing) in rows.items():
        opening_hits = _find_anchor(tokens, opening)
        closing_hits = _find_anchor(tokens, closing)
        if len(opening_hits) != 1:
            result.add(f"pilot anchors: {group} opening anchor is not unique ({len(opening_hits)} matches)")
            continue
        if len(closing_hits) != 1:
            result.add(f"pilot anchors: {group} closing anchor is not unique ({len(closing_hits)} matches)")
            continue
        opening_start, opening_end = opening_hits[0]
        closing_start, closing_end = closing_hits[0]
        if closing_start < opening_start:
            result.add(f"pilot anchors: {group} closing anchor precedes opening anchor")
            continue
        try:
            opening_word = token_word_indices[opening_start]
            closing_word = token_word_indices[closing_end - 1]
            start_s = float(words[opening_word]["start_s"])
            end_s = float(words[closing_word]["end_s"])
        except (KeyError, TypeError, ValueError, IndexError):
            result.add(f"pilot anchors: {group} has no measured word span")
            continue
        resolved[group] = {
            "opening_index": opening_word,
            "closing_index": closing_word,
            "closing_phrase": closing,
            "start_s": round(start_s, 3),
            "end_s": round(end_s, 3),
            "span_s": round(end_s - start_s, 3),
        }
    if len(resolved) == 6:
        result.facts["pilot_anchors"] = resolved
        p06 = resolved.get("P06")
        if p06:
            result.facts["S09_prefix_duration_s"] = p06["end_s"]


def _assembly_take_path(root: Path, take_dir: Path | None, result: PreflightResult) -> Path | None:
    """Resolve an explicit current take without falling back to old scratch dirs."""
    if take_dir is None:
        result.add("assembly: --take-dir is required; historical scratch fallback is disabled")
        return None
    chosen = Path(take_dir)
    if not chosen.is_absolute():
        chosen = root / chosen
    chosen = chosen.resolve()
    if not _inside(root, chosen):
        result.add("assembly: --take-dir must stay inside the episode root")
        return None
    if chosen.name.lower() in LEGACY_TAKE_NAMES:
        result.add(f"assembly: historical take {chosen.name!r} is not eligible; pass a current same-script take")
    return chosen


def _phrase_end_index(words: list[dict[str, Any]], phrase: str) -> int:
    """Return the last measured word in a phrase, preserving punctuation boundaries."""
    tokens: list[str] = []
    indices: list[int] = []
    for index, word in enumerate(words):
        normalized = _normalised_tokens(str(word.get("w", "")))
        tokens.extend(normalized)
        indices.extend([index] * len(normalized))
    hits = _find_anchor(tokens, phrase)
    if len(hits) != 1:
        raise ValueError(f"assembly: phrase must occur once in the selected take: {phrase!r} ({len(hits)} matches)")
    return indices[hits[0][1] - 1]


def _segment_runtime(
    words: list[dict[str, Any]],
    segment: str,
    *,
    audio_duration_s: float | None,
    anchors: dict[str, Any] | None = None,
) -> SegmentBoundary:
    """Bind a prefix cut to a complete sentence and the next measured onset.

    The end of a compiled prefix is the closing word plus the authored
    ``SILENCE_TAIL_S`` hold, never past the next actual word onset.  That gives
    the preceding sentence a short, real silence while keeping the next word
    out of the prefix.  A final segment may use only a trustworthy measured
    media duration.  All timings are checked here as well as during preflight
    so a direct caller cannot filter a malformed/crossing word into invented
    silence.
    """
    if segment not in ASSEMBLY_SEGMENTS:
        supported = ", ".join(sorted(ASSEMBLY_SEGMENTS))
        raise ValueError(f"assembly: only {supported} are supported (got {segment!r})")
    if audio_duration_s is not None and (
        not _finite_number(audio_duration_s) or float(audio_duration_s) <= 0
    ):
        raise ValueError("assembly: measured audio duration must be finite and positive")
    previous_start = -math.inf
    previous_end = -math.inf
    for index, word in enumerate(words):
        if not isinstance(word, dict):
            raise ValueError(f"assembly: word {index} is not an object")
        start = word.get("start_s")
        end = word.get("end_s")
        if not _finite_number(start) or not _finite_number(end):
            raise ValueError(f"assembly: word {index} has non-finite timing")
        start_value, end_value = float(start), float(end)
        if start_value < 0 or end_value < start_value:
            raise ValueError(f"assembly: word {index} has an invalid measured span")
        if start_value < previous_start or end_value < previous_end:
            raise ValueError(f"assembly: word {index} timing is out of order")
        previous_start, previous_end = start_value, end_value
    shot_table = _shot_table_for(segment)
    groups = shot_table.SEGMENT_GROUPS[segment]
    end_group = groups[-1]
    bound_anchor = anchors.get(end_group) if isinstance(anchors, dict) else None
    if isinstance(bound_anchor, dict) and isinstance(bound_anchor.get("closing_phrase"), str):
        close_phrase = bound_anchor["closing_phrase"]
        close_index = bound_anchor.get("closing_index")
        if isinstance(close_index, bool) or not isinstance(close_index, int) or close_index < 0 or close_index >= len(words):
            raise ValueError(f"assembly: validated {end_group} closing word index is invalid")
        if _phrase_end_index(words, close_phrase) != close_index:
            raise ValueError(f"assembly: selected take no longer matches validated {end_group} closing anchor")
    else:
        close_phrase = shot_table.group_end_phrase(end_group)
        close_index = _phrase_end_index(words, close_phrase)
    close_word = words[close_index]
    # Kokoro word sidecars may omit punctuation from individual tokens.  The
    # authored closing anchor is still bound to the current SCRIPT sentence;
    # its punctuation plus the following measured onset establish the tail.
    anchor_text = close_phrase.rstrip('"”')
    if not anchor_text.endswith(tuple(".!?")):
        raise ValueError(f"assembly: closing anchor for {end_group} is not a hard-stop sentence: {close_phrase!r}")
    close_start = close_word.get("start_s")
    close_end = close_word.get("end_s")
    if not _finite_number(close_start) or not _finite_number(close_end):
        raise ValueError(f"assembly: closing anchor has no finite measured span: {close_phrase!r}")
    close_start, close_end = float(close_start), float(close_end)
    if close_end < close_start:
        raise ValueError(f"assembly: closing anchor has an invalid measured span: {close_phrase!r}")
    next_onset: float | None = None
    if close_index + 1 < len(words):
        next_word = words[close_index + 1]
        next_start = next_word.get("start_s")
        if not _finite_number(next_start):
            raise ValueError("assembly: following word has no finite measured onset")
        next_onset = float(next_start)
        if next_onset <= close_end:
            raise ValueError(
                f"assembly: following word onset {next_onset:g}s crosses closing word end {close_end:g}s "
                "or leaves no measured silence"
            )
        if audio_duration_s is not None and next_onset > float(audio_duration_s) + 1e-9:
            raise ValueError("assembly: following word onset exceeds measured audio duration")
        runtime = close_end + SILENCE_TAIL_S
        if runtime > next_onset + 1e-9:
            raise ValueError(
                f"assembly: {SILENCE_TAIL_S:g}s silence tail reaches {runtime:g}s but the following word starts at "
                f"{next_onset:g}s"
            )
    elif audio_duration_s is None:
        raise ValueError("assembly: no following word onset and no trustworthy measured audio duration")
    else:
        duration = float(audio_duration_s)
        if duration < close_end - 1e-9:
            raise ValueError(
                f"assembly: measured audio duration {duration:g}s precedes closing word end {close_end:g}s"
            )
        runtime = close_end + SILENCE_TAIL_S
        if runtime > duration + 1e-9:
            raise ValueError(
                f"assembly: {SILENCE_TAIL_S:g}s silence tail reaches {runtime:g}s but measured audio ends at "
                f"{duration:g}s"
            )
    return SegmentBoundary(
        end_s=round(runtime, 6),
        end_word_index=close_index,
        closing_phrase=close_phrase,
        spoken_end_s=round(close_end, 6),
        next_word_start_s=round(next_onset, 6) if next_onset is not None else None,
    )


def _assembly_sources(root: Path, result: PreflightResult) -> dict[str, Path]:
    """Require the four existing source objects without rewriting them."""
    out: dict[str, Path] = {}
    for object_id in SOURCE_OBJECT_IDS:
        path = root / "evidence" / "objects" / f"{object_id}.series.json"
        if not path.is_file():
            result.add(f"assembly source object missing: {path.relative_to(root).as_posix()}")
        else:
            out[object_id] = path
    return out


def _selected_asset_bindings(root: Path) -> dict[str, tuple[Path, dict[str, Any]]]:
    """Read already-validated HG2 bindings for in-memory render registration."""
    probe = PreflightResult(segment="assembly")
    selected = _json(root / SELECTED_ASSETS_NAME, "selected asset manifest", probe)
    if probe.blockers or not isinstance(selected, dict):
        raise ValueError("assembly: selected asset manifest changed after preflight")
    entries = selected.get("assets")
    if not isinstance(entries, list):
        raise ValueError("assembly: selected asset manifest changed after preflight")
    bindings: dict[str, tuple[Path, dict[str, Any]]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("asset_id"), str):
            raise ValueError("assembly: selected asset manifest changed after preflight")
        path = _relative_path(root, entry.get("path"), f"selected asset {entry['asset_id']}", probe)
        if path is None:
            raise ValueError("assembly: selected asset manifest changed after preflight")
        bindings[entry["asset_id"]] = (path, entry)
    if probe.blockers or set(bindings) != set(APPROVED_ASSET_IDS):
        raise ValueError("assembly: selected asset manifest changed after preflight")
    return bindings


def _register_segment_assets(segment: str, shot_table: Any) -> None:
    """Allow only the minute table to add its separately validated library assets."""
    if segment != "minute":
        return
    register_assets = getattr(shot_table, "register_assets", None)
    if register_assets is None:
        return
    if not callable(register_assets):
        raise ValueError("minute shot table register_assets must be callable")
    register_assets(D)


def _trim_take_audio(take_dir: Path, build: Path, runtime_s: float) -> Path:
    """Copy only real source audio through the cut; never pad or time-stretch it."""
    source = take_dir / AUDIO_NAME
    output = build / "audio" / "episode.mp3"
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(source), "-t", f"{runtime_s:.3f}",
            "-c:a", "libmp3lame", "-q:a", "2", str(output),
        ],
        check=True,
    )
    return output


def _build_receipt(
    *,
    root: Path,
    build: Path,
    segment: str,
    take_dir: Path,
    words: list[dict[str, Any]],
    boundary: SegmentBoundary,
    result: PreflightResult,
    rows: list[tuple],
    asset_bindings: dict[str, tuple[Path, dict[str, Any]]],
    source_paths: dict[str, Path],
) -> Path:
    """Write a human-readable build receipt only after compile succeeds."""
    script_hash_value = str(result.facts.get("script_hash") or "unknown")
    asset_lines = [
        f"  - `{asset_id}`: `{path.relative_to(root).as_posix()}` sha256 `{_sha256(path)}`"
        for asset_id, (path, _) in sorted(asset_bindings.items())
    ]
    source_lines = [
        f"  - `{path.relative_to(root).as_posix()}` sha256 `{_sha256(path)}`"
        for path in sorted(source_paths.values())
    ]
    shot_table = _shot_table_for(segment)
    ranges = shot_table.group_ranges(rows, segment)
    range_lines = [f"  - {group}: {start:.2f}s–{end:.2f}s" for group, (start, end) in ranges.items()]
    audio_path = build / "audio" / "episode.mp3"
    words_path = take_dir / WORDS_NAME
    next_onset_text = (
        f"{boundary.next_word_start_s:.6f}s"
        if boundary.next_word_start_s is not None
        else "none (measured take duration used)"
    )
    receipt = [
        f"# Fed liquidity {segment} build receipt",
        "",
        "Status: compiled through the existing authoring/compiler path; review and HG3 remain pending.",
        "This receipt records measured inputs only. It does not approve media or claim a release-ready pilot.",
        "",
        "## Clock",
        "",
        f"- take: `{take_dir.relative_to(root).as_posix()}/{TAKE_STEM}`",
        f"- script spoken hash: `{script_hash_value}`",
        f"- words: `{words_path.relative_to(root).as_posix()}` sha256 `{_sha256(words_path)}`",
        f"- audio: `{audio_path.relative_to(root).as_posix()}` sha256 `{_sha256(audio_path)}`",
        f"- closing anchor: `{boundary.closing_phrase}`",
        f"- measured prefix end: `{boundary.end_s:.6f}s` (word index {boundary.end_word_index}; "
        f"{len(words[:boundary.end_word_index + 1])} words retained)",
        f"- spoken end: `{boundary.spoken_end_s:.6f}s` (end word index {boundary.end_word_index}; measured from take-word-clock)",
        f"- silence tail: `{SILENCE_TAIL_S:.2f}s` (accepted only inside measured following onset/duration)",
        f"- following word onset: `{next_onset_text}`",
        "",
        "## Semantic rows",
        "",
        f"- rows: `{len(rows)}` across groups `{', '.join(shot_table.SEGMENT_GROUPS[segment])}`",
        f"- authoring status: `{shot_table.AUTHORING_STATUS}` (not an acceptance or release verdict)",
        *range_lines,
        f"- authored incoming transitions: `{[row[5] for row in rows if row[5]]}`; registered surface arrivals are encoded in plate declarations",
        "- narrative plates: one-direction Ken Burns; compiler `plate_idle_paints` is false",
        "",
        "## Source custody",
        "",
        *source_lines,
        "",
        "## HG2-selected assets",
        "",
        *asset_lines,
        "",
        "## Boundary",
        "",
        "- no provider/voice generation, asset promotion, or approval was performed",
        "- no full render was performed; the private compiled build is for review only",
    ]
    path = build / "BUILD-RECEIPT.md"
    path.write_text("\n".join(receipt) + "\n", encoding="utf-8")
    return path


def _receipt_file_ref(root: Path, path: Path, label: str, result: PreflightResult) -> dict[str, str] | None:
    """Return one episode-relative, byte-bound receipt reference without writing anything."""
    try:
        resolved = Path(path).resolve()
    except OSError as exc:
        result.add(f"finalize: {label}: cannot resolve path ({exc})")
        return None
    if not _inside(root.resolve(), resolved):
        result.add(f"finalize: {label}: path escapes episode root")
        return None
    if not resolved.is_file():
        result.add(f"finalize: {label}: file is missing ({resolved.relative_to(root.resolve()).as_posix()})")
        return None
    try:
        digest = _sha256(resolved)
        relative = resolved.relative_to(root.resolve()).as_posix()
    except (OSError, ValueError) as exc:
        result.add(f"finalize: {label}: cannot hash file ({exc})")
        return None
    return {"path": relative, "sha256": digest}


def _selected_asset_receipt_refs(root: Path, result: PreflightResult) -> list[dict[str, str]]:
    """Capture selected media and explicit approval artifacts after custody preflight."""
    selected = _json(root / SELECTED_ASSETS_NAME, "selected asset manifest", result)
    if not isinstance(selected, dict):
        return []
    entries = selected.get("assets")
    if not isinstance(entries, list):
        result.add("finalize: selected asset manifest assets must be an array")
        return []
    refs: list[dict[str, str]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            result.add(f"finalize: selected asset {index} must be an object")
            continue
        asset_id = entry.get("asset_id", index)
        asset = _receipt_file_ref(root, root / str(entry.get("path", "")), f"asset {asset_id}", result)
        approval = _receipt_file_ref(
            root,
            root / str(entry.get("approval_path", "")),
            f"approval {asset_id}",
            result,
        )
        if asset is not None:
            refs.append(asset)
        if approval is not None:
            refs.append(approval)
    return refs


def _load_pilot_review_module():
    """Load the episode's read-only T16 adapter without creating an import cycle."""
    name = "fed_liquidity_pilot_review_for_receipt"
    cached = sys.modules.get(name)
    if cached is not None:
        return cached
    path = EPISODE_ROOT / "pilot_review.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load pilot review adapter {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _candidate_review(build: Path, candidate: dict[str, Any]):
    """Run the existing T16 consumer against a temporary receipt, never its output writer."""
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".BUILD-RECEIPT.json", delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(candidate, handle, indent=2, sort_keys=True)
            handle.write("\n")
        pilot_review = _load_pilot_review_module()
        return pilot_review.inspect_build(
            build,
            mode="prefix",
            receipt_path=temporary,
        )
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _review_receipt_candidate(
    *,
    root: Path,
    build: Path,
    segment: str,
    take_dir: Path,
    boundary: SegmentBoundary,
    parent_reads: dict[str, Any],
    result: PreflightResult,
) -> dict[str, Any] | None:
    """Assemble the T16 schema from measured files; no value is inferred or generated."""
    script = _receipt_file_ref(root, root / SCRIPT_NAME, "script", result)
    audio = _receipt_file_ref(root, take_dir / AUDIO_NAME, "take audio", result)
    words = _receipt_file_ref(root, take_dir / WORDS_NAME, "take words", result)
    timeline = _receipt_file_ref(root, build / TIMELINE_NAMES[segment], "compiled timeline", result)
    player = _receipt_file_ref(root, build / "player.html", "compiled player", result)
    manifest = _receipt_file_ref(root, root / SELECTED_ASSETS_NAME, "selected asset manifest", result)
    reports: list[dict[str, str]] = []
    for report_name in ("GATES-MOTION.md", "SELF-WATCH.md", "layout-probe.json", "seam-frames.json"):
        reference = _receipt_file_ref(root, build / report_name, f"raw report {report_name}", result)
        if reference is not None:
            reports.append(reference)

    claims = _receipt_file_ref(root, root / CLAIMS_NAME, "claims manifest", result)
    source_paths = _assembly_sources(root, result)
    source_custody: list[dict[str, str]] = []
    if claims is not None:
        source_custody.append(claims)
    for object_id in SOURCE_OBJECT_IDS:
        source = source_paths.get(object_id)
        if source is not None:
            reference = _receipt_file_ref(root, source, f"source object {object_id}", result)
            if reference is not None:
                source_custody.append(reference)
    asset_custody = _selected_asset_receipt_refs(root, result)
    if not all((script, audio, words, timeline, player, manifest)):
        return None
    if len(reports) != 4 or not source_custody or not asset_custody:
        return None
    return {
        "schema": BUILD_RECEIPT_SCHEMA,
        "script": script,
        "take": {
            "id": take_dir.name,
            "audio": audio,
            "words": words,
        },
        "timeline": timeline,
        "player": player,
        "reports": reports,
        "assets": {"manifest": manifest},
        "source_custody": source_custody,
        "asset_custody": asset_custody,
        "prefix": {
            "sections": [f"S{i:02d}" for i in range(1, 10)],
            "start_s": 0,
            "end_s": boundary.end_s,
            "spoken_end_s": boundary.spoken_end_s,
            "end_word_index": boundary.end_word_index,
            "measured_from": "take-word-clock",
        },
        "parent_reads": parent_reads,
    }


def finalize_review_receipt(
    *,
    project_root: Path = EPISODE_ROOT,
    take_dir: Path | None,
    parent_reads_path: Path | None,
    segment: str = "pilot",
) -> int:
    """Finalize one review receipt only after the read-only T16 candidate passes."""
    root = Path(project_root).resolve()
    result = PreflightResult(segment=segment)
    if segment != "pilot":
        result.add("finalize: --finalize-review-receipt supports only --segment pilot")
    chosen_take = _assembly_take_path(root, take_dir, result)
    if parent_reads_path is None:
        result.add("finalize: --parent-reads is required")
    parent_reads: dict[str, Any] | None = None
    parent_path: Path | None = None
    if parent_reads_path is not None:
        parent_raw = parent_reads_path.as_posix() if isinstance(parent_reads_path, Path) else parent_reads_path
        parent_path = _relative_path(root, parent_raw, "parent reads", result)
        if parent_path is not None:
            loaded = _json(parent_path, "parent reads declaration", result)
            if isinstance(loaded, dict):
                parent_reads = loaded
            elif loaded is not None:
                result.add("finalize: parent reads declaration must be a JSON object")
    if result.blockers or chosen_take is None or parent_reads is None:
        print("\n".join(result.lines()))
        return 1

    preflight = check_inputs(project_root=root, take_dir=chosen_take, segment=segment)
    result.facts.update(preflight.facts)
    for blocker in preflight.blockers:
        result.add(blocker)
    # Re-read the operator-bound manifest after preflight.  The receipt must
    # bind the bytes that are actually about to be recorded, not a manifest
    # that changed between the read-only check and candidate construction.
    _validate_selected_assets(root, result)
    build = root / BUILD_NAMES[segment]
    if not build.is_dir():
        result.add(f"finalize: compiled build is missing ({build.relative_to(root).as_posix()})")
    if result.blockers:
        print("\n".join(result.lines()))
        return 1

    words_doc = _json(chosen_take / WORDS_NAME, "finalize take word clock", result)
    words = words_doc.get("words") if isinstance(words_doc, dict) else None
    if not isinstance(words, list) or not words:
        result.add("finalize: selected take word clock has no words")
        words = []
    try:
        boundary = _segment_runtime(
            words,
            segment,
            audio_duration_s=result.facts.get("audio_duration_s"),
            anchors=result.facts.get("pilot_anchors"),
        )
    except (TypeError, ValueError) as exc:
        result.add(str(exc))
        boundary = None
    candidate = None
    if boundary is not None and not result.blockers:
        candidate = _review_receipt_candidate(
            root=root,
            build=build,
            segment=segment,
            take_dir=chosen_take,
            boundary=boundary,
            parent_reads=parent_reads,
            result=result,
        )
    if candidate is None and not result.blockers:
        result.add("finalize: receipt candidate could not be constructed")
    if result.blockers:
        print("\n".join(result.lines()))
        return 1

    try:
        review = _candidate_review(build, candidate)
    except (OSError, TypeError, ValueError, ImportError) as exc:
        result.add(f"finalize: pilot review adapter failed closed ({exc})")
        review = None
    if review is None:
        print("\n".join(result.lines()))
        return 1
    if not review.ok:
        result.add(f"finalize: pilot review rejected candidate ({review.status})")
        for blocker in review.blockers:
            result.add(f"pilot review: {blocker}")
        print("\n".join(result.lines()))
        return 1

    receipt_path = build / RECEIPT_NAME
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", prefix=".BUILD-RECEIPT.",
            dir=build, delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(candidate, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, receipt_path)
        temporary = None
    except OSError as exc:
        result.add(f"finalize: cannot publish {RECEIPT_NAME} atomically ({exc})")
        print("\n".join(result.lines()))
        return 1
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
    print(f"finalize-review-receipt: PASS ({segment})")
    print(f"  receipt: {receipt_path}")
    print(f"  end: {boundary.end_s:.6f}s after {boundary.closing_phrase!r}; spoken end {boundary.spoken_end_s:.6f}s")
    return 0


def assemble(
    *,
    project_root: Path = EPISODE_ROOT,
    take_dir: Path | None,
    segment: str,
) -> int:
    """Preflight, then assemble one bounded prefix segment into a private build."""
    root = Path(project_root).resolve()
    if segment not in ASSEMBLY_SEGMENTS:
        result = PreflightResult(segment=segment)
        supported = ", ".join(sorted(ASSEMBLY_SEGMENTS))
        result.add(f"assembly: only {supported} are supported (got {segment!r})")
        print("\n".join(result.lines()))
        return 1

    # This call is intentionally the first mutating-capable operation.  A
    # missing explicit take uses a non-existent sentinel for diagnostics; it
    # must never make the historical preflight default part of assembly.
    preflight_take = take_dir if take_dir is not None else root / ".current-take-required"
    result = check_inputs(project_root=root, take_dir=preflight_take, segment=segment)
    chosen_take = _assembly_take_path(root, take_dir, result)
    source_paths = _assembly_sources(root, result)
    if result.facts.get("take_script_match") is not True:
        result.add("assembly: selected take words must match the current SCRIPT-VO.txt")
    if not result.ok or chosen_take is None:
        print("\n".join(result.lines()))
        return 1

    try:
        shot_table = _shot_table_for(segment)
        probe = Project(
            here=root,
            build=root / BUILD_NAMES[segment],
            take=chosen_take,
            take_stem=TAKE_STEM,
            script_name=SCRIPT_NAME,
            episode_id=f"fed-liquidity-pressure-{segment}",
            take_name=chosen_take.name,
        )
        words = [dict(word) for word in W.take_words(probe)]
        boundary = _segment_runtime(
            words,
            segment,
            audio_duration_s=result.facts.get("audio_duration_s"),
            anchors=result.facts.get("pilot_anchors"),
        )
        rows = shot_table.build_rows(words[: boundary.end_word_index + 1], boundary.end_s, segment)
        asset_bindings = _selected_asset_bindings(root)
    except (OSError, TypeError, ValueError, SystemExit) as exc:
        result.add(str(exc) or "assembly: source/take validation failed")
        print("\n".join(result.lines()))
        return 1

    build = root / BUILD_NAMES[segment]
    build.mkdir(parents=True, exist_ok=True)
    project = Project(
        here=root,
        build=build,
        take=chosen_take,
        take_stem=TAKE_STEM,
        script_name=SCRIPT_NAME,
        episode_id=f"fed-liquidity-pressure-{segment}",
        take_name=chosen_take.name,
    )
    audio_path = _trim_take_audio(chosen_take, build, boundary.end_s)
    del audio_path  # the receipt hashes the path after the compiler succeeds
    W.write_timeline(project, words[: boundary.end_word_index + 1], boundary.end_s)
    T.caption_pages(build, char_budget=34, max_words=6)
    for asset_id, (asset_path, _) in asset_bindings.items():
        D.register(asset_id, asset_path)
    try:
        _register_segment_assets(segment, shot_table)
    except (OSError, TypeError, ValueError, SystemExit) as exc:
        print(f"assembly: minute asset registration refused: {exc}", file=sys.stderr)
        return 1
    table = build / TABLE_NAMES[segment]
    T.write_shot_table(
        table,
        rows,
        (
            f'"""Fed liquidity pressure — minute rows; generated from the selected take. '
            f'Authoring status: {shot_table.AUTHORING_STATUS}."""\n'
            if segment == "minute"
            else f'"""Fed liquidity pressure — semantic S01-S09 pilot rows; generated from the selected take. '
                 f'Authoring status: {shot_table.AUTHORING_STATUS}."""\n'
        ),
    )
    timeline_name = TIMELINE_NAMES[segment]
    shot_table_file = table.relative_to(root).as_posix()
    try:
        rc = T.compile_timeline(
            root,
            build,
            timeline_name=timeline_name,
            shot_table_file=shot_table_file,
            title="THE HIDDEN FED METRIC BREAKING THE ECONOMY",
            subtitle="Fed liquidity pressure · source-bound prefix",
            episode_id=f"fed-liquidity-pressure-{segment}",
            aspect="16:9",
            form="long",
            caption_style=None,
            kinetics={
                "plate_idle_paints": False,
                "analytic_spring": True,
                "min_jerk": True,
                "area_squash": True,
                "curvature_stroke": True,
            },
            render=False,
        )
    except (OSError, TypeError, ValueError, SystemExit) as exc:
        print(f"assembly: compiler refused: {exc}", file=sys.stderr)
        return 1
    if rc:
        print(f"assembly: compiler returned {rc}", file=sys.stderr)
        return int(rc)
    receipt = _build_receipt(
        root=root,
        build=build,
        segment=segment,
        take_dir=chosen_take,
        words=words,
        boundary=boundary,
        result=result,
        rows=rows,
        asset_bindings=asset_bindings,
        source_paths=source_paths,
    )
    print(f"assembly: PASS ({segment})")
    print(f"  build: {build}")
    print(f"  rows: {len(rows)} across {', '.join(shot_table.SEGMENT_GROUPS[segment])}")
    print(f"  end: {boundary.end_s:.6f}s after {boundary.closing_phrase!r}; "
          f"spoken end {boundary.spoken_end_s:.6f}s; next onset {boundary.next_word_start_s}")
    print(f"  receipt: {receipt}")
    return 0


def check_inputs(
    *,
    project_root: Path = EPISODE_ROOT,
    take_dir: Path | None = None,
    segment: str = "pilot",
) -> PreflightResult:
    """Validate all currently available inputs without creating any files."""
    root = Path(project_root).resolve()
    result = PreflightResult(segment=segment)
    if segment not in {*ASSEMBLY_SEGMENTS, "episode"}:
        result.add(f"segment: unsupported segment {segment}")
    script_path, current_hash, report_digests = _validate_script_and_reports(root, result, segment)
    _validate_claims(root, result)
    _validate_selected_assets(root, result)
    _validate_segment_table(segment, result)
    if take_dir is None:
        result.add("take: --take-dir is required; historical scratch fallback is disabled")
        return result
    chosen_take = Path(take_dir)
    if not chosen_take.is_absolute():
        chosen_take = root / chosen_take
    chosen_take = chosen_take.resolve()
    if not _inside(root, chosen_take):
        result.add("take: --take-dir must stay inside the episode root")
        words: list[dict[str, Any]] = []
    else:
        result.facts["take_dir"] = str(chosen_take.relative_to(root))
        words = _validate_take(root, chosen_take, result, script_path, current_hash, report_digests)
    _validate_anchors(root, words, result)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preflight or assemble the Fed liquidity prefix through the existing engine.")
    parser.add_argument("--segment", choices=(*sorted(ASSEMBLY_SEGMENTS), "episode"), default="pilot")
    parser.add_argument("--check-inputs", action="store_true", help="validate source, selected assets, reports, and an existing same-stem take")
    parser.add_argument(
        "--finalize-review-receipt",
        action="store_true",
        help="validate a completed pilot build and publish its review receipt",
    )
    parser.add_argument("--project-root", type=Path, default=EPISODE_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--take-dir", type=Path, default=None, help="explicit current same-script take directory; assembly has no historical fallback")
    parser.add_argument("--take", dest="finalize_take", type=Path, default=None, help="explicit same-take directory for receipt finalization")
    parser.add_argument("--parent-reads", type=Path, default=None, help="episode-relative parent read declaration for receipt finalization")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.finalize_review_receipt:
        if args.take_dir is not None:
            print("finalize: use --take, not --take-dir, with --finalize-review-receipt", file=sys.stderr)
            return 1
        if args.finalize_take is None or args.parent_reads is None:
            print("finalize: --take and --parent-reads are required with --finalize-review-receipt", file=sys.stderr)
            return 1
        return finalize_review_receipt(
            project_root=args.project_root,
            take_dir=args.finalize_take,
            parent_reads_path=args.parent_reads,
            segment=args.segment,
        )
    if args.finalize_take is not None or args.parent_reads is not None:
        print("finalize: --take and --parent-reads require --finalize-review-receipt", file=sys.stderr)
        return 1
    if args.check_inputs:
        result = check_inputs(project_root=args.project_root, take_dir=args.take_dir, segment=args.segment)
        print("\n".join(result.lines()))
        return 0 if result.ok else 1
    return assemble(project_root=args.project_root, take_dir=args.take_dir, segment=args.segment)


if __name__ == "__main__":
    raise SystemExit(main())
