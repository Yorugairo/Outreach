"""Strict contracts for History of BJJ episode and research artifacts.

The history lane intentionally has a hard boundary between evidence and
rendering.  This module validates JSON intake, computes a stable content hash,
and returns a renderer-neutral copy.  It never follows a URL, resolves an
archive asset, or mutates a caller-owned mapping.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft7Validator, FormatChecker


HISTORY_EPISODE_VERSION = "history_episode.v1"
RESEARCH_PACKET_VERSION = "research_packet.v1"

_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_REMOTE_PATH_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_HASH_KEYS = {
    "artifact_hash",
    "canonical_sha256",
    "content_hash",
    "research_hash",
}
_NON_FACTUAL_SOURCE_KINDS = {
    "study",
    "reference_study",
    "creative_study",
    "consultant",
    "consultant_outline",
    "reference-study",
    "consultant-outline",
}
_QUALIFIER_RE = re.compile(
    r"\b(?:contested|disputed|debated|uncertain|accounts? differ|"
    r"some sources|evidence is mixed|tradition holds|reported(?:ly)?|"
    r"not settled|scholars disagree)\b",
    re.IGNORECASE,
)


class HistoryContractValidationError(ValueError):
    """Raised when a history contract fails closed."""

    def __init__(self, errors: Iterable[str], *, contract: str | None = None):
        self.errors = list(errors)
        self.contract = contract
        label = f"invalid {contract}" if contract else "invalid history contract"
        super().__init__(f"{label}: {'; '.join(self.errors) or label}")


# Domain-specific aliases make error handling symmetrical with art_direction.
HistoryContractError = HistoryContractValidationError
HistoryEpisodeValidationError = HistoryContractValidationError
ResearchPacketValidationError = HistoryContractValidationError


def canonical_json(value: Any) -> str:
    """Return canonical JSON bytes' text for deterministic artifact hashing.

    A top-level artifact digest is excluded before hashing so validating a
    previously hashed artifact produces the same digest.  Nested hashes (for
    example a research reference in an episode) remain part of the digest.
    ``allow_nan=False`` prevents non-portable JSON values from entering the
    evidence contract.
    """

    if isinstance(value, Mapping):
        payload = dict(value)
        for key in _HASH_KEYS:
            payload.pop(key, None)
    else:
        payload = value
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise TypeError(f"value is not canonical JSON: {exc}") from exc


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


stable_sha256 = canonical_sha256
canonical_hash = canonical_sha256
hash_canonical_json = canonical_sha256
sha256_json = canonical_sha256


def _engine_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _schema_path(name: str, explicit: str | Path | None = None) -> Path:
    return Path(explicit) if explicit is not None else _engine_root() / "configs" / name


def _format_schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "root"
    return f"schema {path}: {error.message}"


def _schema_errors(payload: Mapping[str, Any], path: Path) -> list[str]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"schema: unable to load {path}: {exc}"]
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda error: (tuple(str(item) for item in error.absolute_path), error.message),
    )
    return [_format_schema_error(error) for error in errors]


def _reject_remote_or_unsafe_path(value: str) -> None:
    candidate = value.strip()
    if not candidate:
        raise ValueError("contract path cannot be empty")
    if _REMOTE_PATH_RE.match(candidate) or candidate.startswith(("//", "\\\\")):
        raise ValueError("contract path must be a local file, not a remote URL")


def _load_json(
    value: Mapping[str, Any] | str | Path,
    label: str,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Load an object without allowing a path to escape ``root``.

    ``root`` is optional for compatibility with direct operator calls.  When
    supplied, both relative and absolute paths must resolve beneath it; this
    also prevents symlinks from escaping the approved workspace.
    """

    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    if not isinstance(value, (str, Path)):
        raise TypeError(f"{label} must be a mapping or JSON path")
    raw_path = str(value)
    _reject_remote_or_unsafe_path(raw_path)
    path = Path(raw_path)
    root_path = Path(root).resolve() if root is not None else None
    if not path.is_absolute():
        path = (root_path if root_path is not None else Path.cwd()) / path
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise FileNotFoundError(f"{label} does not exist: {path}") from exc
    if root_path is not None:
        try:
            resolved.relative_to(root_path)
        except ValueError as exc:
            raise ValueError(f"{label} path must stay within {root_path}") from exc
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} is not a file: {resolved}")
    try:
        decoded = json.loads(resolved.read_bytes().decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HistoryContractValidationError(
            [f"{label} is not valid JSON: {exc}"], contract=label
        ) from exc
    if not isinstance(decoded, Mapping):
        raise HistoryContractValidationError(
            [f"{label} root must be an object"], contract=label
        )
    return copy.deepcopy(dict(decoded))


def _hash_errors(payload: Mapping[str, Any]) -> tuple[list[str], str]:
    expected = canonical_sha256(payload)
    errors: list[str] = []
    provided = payload.get("artifact_hash")
    if provided is not None:
        if not isinstance(provided, str) or not _HASH_RE.fullmatch(provided):
            errors.append("artifact_hash must be a 64-character lowercase SHA-256")
        elif provided != expected:
            errors.append(
                f"artifact_hash {provided!r} does not match canonical SHA-256 {expected!r}"
            )
    for alias in ("canonical_sha256", "content_hash", "research_hash"):
        if alias not in payload:
            continue
        candidate = payload[alias]
        if not isinstance(candidate, str) or not _HASH_RE.fullmatch(candidate):
            errors.append(f"{alias} must be a 64-character lowercase SHA-256")
        elif candidate != expected:
            errors.append(f"{alias} does not match canonical SHA-256 {expected!r}")
    return errors, expected


def _with_hash(payload: Mapping[str, Any], *, contract: str) -> dict[str, Any]:
    result = copy.deepcopy(dict(payload))
    errors, expected = _hash_errors(result)
    if errors:
        raise HistoryContractValidationError(errors, contract=contract)
    result["artifact_hash"] = expected
    return result


def _unique_ids(items: Any, field: str, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(items, list):
        return {}
    values: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str):
            continue
        if identifier in values:
            errors.append(f"{field}[{index}] duplicates id {identifier!r}")
        values[identifier] = item
    return values


def _history_rules(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    chapters = payload.get("chapters") or []
    chapter_map = _unique_ids(chapters, "chapters", errors)
    try:
        target_duration = float(payload.get("target_duration_s", 0))
    except (TypeError, ValueError):
        target_duration = 0.0
    if target_duration < 480 or target_duration > 720:
        errors.append("target_duration_s must be within the 8–12 minute documentary range (480–720s)")
    chapter_total = 0.0
    for chapter in chapters:
        if not isinstance(chapter, Mapping):
            continue
        try:
            chapter_total += float(chapter.get("target_duration_s", 0))
        except (TypeError, ValueError):
            continue
        for key in ("claim_ids", "research_claim_ids"):
            for claim_id in chapter.get(key, []) or []:
                if not isinstance(claim_id, str) or not _ID_RE.fullmatch(claim_id):
                    errors.append(f"chapter {chapter.get('id', '?')!r} has invalid {key} id {claim_id!r}")
    if chapter_total > target_duration * 1.1:
        errors.append("chapter target durations exceed episode target duration")
    outputs = payload.get("outputs") or payload.get("output_targets") or []
    output_map = _unique_ids(outputs, "outputs", errors)
    if output_map:
        landscape = [item for item in outputs if isinstance(item, Mapping) and item.get("format") == "landscape"]
        vertical = [item for item in outputs if isinstance(item, Mapping) and item.get("format") == "vertical"]
        if len(landscape) != 1:
            errors.append("outputs must contain exactly one landscape master")
        if len(vertical) != 2:
            errors.append("outputs must contain exactly two native vertical clips")
        chapter_outputs = [
            item
            for item in outputs
            if isinstance(item, Mapping)
            and item.get("format") in {"chapter", "chapter_subvideo"}
        ]
        if len(chapter_outputs) < len(chapters):
            errors.append(
                "outputs must include at least one chapter-level subvideo per chapter"
            )
        for item in outputs:
            if not isinstance(item, Mapping):
                continue
            width, height = item.get("width"), item.get("height")
            if item.get("format") == "landscape" and width and height and width < height:
                errors.append(f"output {item.get('id', '?')!r} landscape dimensions are not landscape")
            if item.get("format") == "vertical" and width and height:
                ratio = float(width) / float(height)
                if abs(ratio - 9 / 16) > 0.03:
                    errors.append(f"output {item.get('id', '?')!r} is not a native 9:16 vertical output")
    # A duplicated reference is allowed only when its identity and digest agree.
    for left, right in (("research_packet", "research_packet_ref"), ("asset_manifest", "asset_manifest_ref")):
        if isinstance(payload.get(left), Mapping) and isinstance(payload.get(right), Mapping):
            if payload[left].get("id") != payload[right].get("id") or payload[left].get("hash") != payload[right].get("hash"):
                errors.append(f"{left} and {right} references disagree")
    return errors


def _source_kind(source: Mapping[str, Any]) -> str:
    return str(source.get("source_kind") or source.get("kind") or "").strip().casefold().replace(" ", "_")


def _source_group(source: Mapping[str, Any]) -> str:
    explicit = str(source.get("independence_group") or "").strip().casefold()
    if explicit:
        return explicit
    publisher = str(source.get("publisher") or "").strip().casefold()
    if publisher:
        return f"publisher:{publisher}"
    author = str(source.get("author") or "").strip().casefold()
    if author:
        return f"author:{author}"
    return f"source:{source.get('id', '')}"


def _research_rules(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = payload.get("sources") or []
    citations = payload.get("citations") or []
    claims = payload.get("claims") or []
    source_map = _unique_ids(sources, "sources", errors)
    citation_map = _unique_ids(citations, "citations", errors)
    claim_map = _unique_ids(claims, "claims", errors)
    non_factual: set[str] = set()
    for source_id, source in source_map.items():
        kind = _source_kind(source)
        role = str(source.get("role") or "").strip().casefold()
        factual_flag = source.get("is_factual_source") is True or source.get("factual_eligible") is True or role == "factual"
        if kind in _NON_FACTUAL_SOURCE_KINDS:
            non_factual.add(source_id)
            if factual_flag:
                errors.append(f"source {source_id!r} is {kind} material and cannot be a factual source")
        if source.get("render_eligible") is True:
            errors.append(f"source {source_id!r} cannot be render eligible research provenance")
    for citation_id, citation in citation_map.items():
        source_id = str(citation.get("source_id") or "")
        if source_id not in source_map:
            errors.append(f"citation {citation_id!r} references missing source {source_id!r}")
    for claim_id, claim in claim_map.items():
        raw_citations = claim.get("citation_ids")
        if not isinstance(raw_citations, list) or not raw_citations:
            errors.append(f"claim {claim_id!r} requires at least one citation")
            continue
        referenced: list[Mapping[str, Any]] = []
        for citation_id in raw_citations:
            citation = citation_map.get(str(citation_id))
            if citation is None:
                errors.append(f"claim {claim_id!r} references missing citation {citation_id!r}")
                continue
            referenced.append(citation)
            source_id = str(citation.get("source_id") or "")
            if source_id in non_factual:
                errors.append(f"claim {claim_id!r} cites study/consultant material {source_id!r} as factual evidence")
        direct_quote = bool(claim.get("direct_quote") or claim.get("quote") or claim.get("direct_quote_text"))
        if direct_quote:
            claim_locator = str(claim.get("quote_locator") or "").strip()
            citation_locator = any(
                str(item.get("locator") or item.get("quote_locator") or "").strip()
                for item in referenced
            )
            if not claim_locator and not citation_locator:
                errors.append(f"claim {claim_id!r} is a direct quote and requires a quote locator")
        contested = bool(claim.get("contested")) or str(claim.get("status") or "").casefold() == "contested"
        if contested:
            groups: set[str] = set()
            qualification = str(
                claim.get("qualified_narration")
                or claim.get("qualification")
                or claim.get("narration")
                or ""
            ).strip()
            for citation in referenced:
                source = source_map.get(str(citation.get("source_id") or ""))
                if source is not None and str(citation.get("source_id")) not in non_factual:
                    groups.add(_source_group(source))
            if len(groups) < 2:
                errors.append(f"contested claim {claim_id!r} requires at least two independent citations")
            if not qualification or not _QUALIFIER_RE.search(qualification):
                errors.append(f"contested claim {claim_id!r} requires explicitly qualified narration")
        source_ids = claim.get("source_ids")
        if isinstance(source_ids, list):
            for source_id in source_ids:
                if str(source_id) not in source_map:
                    errors.append(f"claim {claim_id!r} references missing source {source_id!r}")
    return errors


class HistoryContractService:
    """Load, validate, and hash history contracts without side effects."""

    def __init__(self, *, configs_root: str | Path | None = None, root: str | Path | None = None):
        self.configs_root = Path(configs_root) if configs_root is not None else _engine_root() / "configs"
        self.root = Path(root) if root is not None else None

    def validate_history_episode(
        self,
        value: Mapping[str, Any] | str | Path,
        *,
        root: str | Path | None = None,
    ) -> dict[str, Any]:
        payload = _load_json(value, "history episode", root=root or self.root)
        errors = _schema_errors(payload, self.configs_root / "history_episode.schema.json")
        errors.extend(_history_rules(payload))
        if errors:
            raise HistoryContractValidationError(errors, contract=HISTORY_EPISODE_VERSION)
        return _with_hash(payload, contract=HISTORY_EPISODE_VERSION)

    def validate_research_packet(
        self,
        value: Mapping[str, Any] | str | Path,
        *,
        root: str | Path | None = None,
    ) -> dict[str, Any]:
        payload = _load_json(value, "research packet", root=root or self.root)
        errors = _schema_errors(payload, self.configs_root / "research_packet.schema.json")
        errors.extend(_research_rules(payload))
        if errors:
            raise HistoryContractValidationError(errors, contract=RESEARCH_PACKET_VERSION)
        return _with_hash(payload, contract=RESEARCH_PACKET_VERSION)

    validate_history = validate_history_episode
    validate_research = validate_research_packet

    def load_history_episode(self, value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
        return self.validate_history_episode(value, root=root)

    def load_research_packet(self, value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
        return self.validate_research_packet(value, root=root)

    check_history_episode = lambda self, value, **kwargs: _check(value, self.validate_history_episode, **kwargs)
    check_research_packet = lambda self, value, **kwargs: _check(value, self.validate_research_packet, **kwargs)
    check_history = check_history_episode
    check_research = check_research_packet

    @staticmethod
    def hash_artifact(value: Any) -> str:
        return canonical_sha256(value)

    canonical_sha256 = staticmethod(canonical_sha256)
    stable_hash = staticmethod(canonical_sha256)


def _check(value: Any, validator: Any, **kwargs: Any) -> list[str]:
    try:
        validator(value, **kwargs)
    except (HistoryContractValidationError, FileNotFoundError, OSError, TypeError, ValueError) as exc:
        if isinstance(exc, HistoryContractValidationError):
            return list(exc.errors)
        return [str(exc)]
    return []


_DEFAULT_SERVICE = HistoryContractService()


def validate_history_episode(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    return _DEFAULT_SERVICE.validate_history_episode(value, root=root)


def validate_research_packet(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    return _DEFAULT_SERVICE.validate_research_packet(value, root=root)


def load_history_episode(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    return _DEFAULT_SERVICE.load_history_episode(value, root=root)


def load_research_packet(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    return _DEFAULT_SERVICE.load_research_packet(value, root=root)


def check_history_episode(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> list[str]:
    return _check(value, _DEFAULT_SERVICE.validate_history_episode, root=root)


def check_research_packet(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> list[str]:
    return _check(value, _DEFAULT_SERVICE.validate_research_packet, root=root)


def validate_history(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    return validate_history_episode(value, root=root)


def validate_research(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> dict[str, Any]:
    return validate_research_packet(value, root=root)


def check_history(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> list[str]:
    return check_history_episode(value, root=root)


def check_research(value: Mapping[str, Any] | str | Path, *, root: str | Path | None = None) -> list[str]:
    return check_research_packet(value, root=root)


__all__ = [
    "HISTORY_EPISODE_VERSION",
    "RESEARCH_PACKET_VERSION",
    "HistoryContractService",
    "HistoryContractError",
    "HistoryContractValidationError",
    "HistoryEpisodeValidationError",
    "ResearchPacketValidationError",
    "canonical_json",
    "canonical_sha256",
    "canonical_hash",
    "stable_sha256",
    "hash_canonical_json",
    "sha256_json",
    "validate_history_episode",
    "validate_research_packet",
    "load_history_episode",
    "load_research_packet",
    "check_history_episode",
    "check_research_packet",
    "validate_history",
    "validate_research",
    "check_history",
    "check_research",
]
