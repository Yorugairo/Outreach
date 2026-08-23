"""Canonical artifact hashing and IO shared by the paste-lane services.

Mirrors the hashing contract already used by ``style_board.canonical_json`` and
``editorial_motion._artifact_hash`` without importing either — ``style_board``
pulls Pillow and ``editorial_motion`` pulls the full motion compiler, neither of
which the paste lane needs.

The hash always excludes the ``artifact_hash`` key itself so an artifact can
carry its own digest.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")
SAFE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def canonical_json(value: Any) -> bytes:
    """Serialize deterministically: sorted keys, compact separators, UTF-8."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def artifact_hash(payload: Mapping[str, Any]) -> str:
    """Digest of ``payload`` with any existing ``artifact_hash`` removed."""

    body = {key: value for key, value in payload.items() if key != "artifact_hash"}
    return sha256_json(body)


def stamp_artifact_hash(payload: dict[str, Any]) -> dict[str, Any]:
    payload["artifact_hash"] = artifact_hash(payload)
    return payload


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    """Accept an in-memory mapping or a path to a JSON document."""

    if isinstance(value, Mapping):
        return dict(value)
    path = Path(value)
    if not path.is_file():
        raise ValueError(f"{label} not found: {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} must be a JSON object")
    return loaded


def write_artifact(path: Path, payload: Mapping[str, Any]) -> Path:
    """Write a canonical, hash-stamped artifact and return its path."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(payload) + b"\n")
    return path
