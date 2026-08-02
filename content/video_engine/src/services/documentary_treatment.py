"""Compile History V4 documentary shots into renderer-safe treatments.

The compiler is deliberately independent of the research and rights services.
It consumes their persisted mappings, copies only claim/citation IDs and
approved asset IDs, and emits a deterministic ``visual_treatment.v2`` record.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.scenes.documentary import (
    DOCUMENTARY_FUNCTIONS,
    scene_factory,
)


TREATMENT_VERSION = "visual_treatment.v2"
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_PROHIBITED_KEYS = {
    "url",
    "source_url",
    "path",
    "source_path",
    "asset_path",
    "media_path",
    "study_path",
    "study_ref",
    "creator",
    "creator_name",
    "creator_id",
    "imitation_prompt",
    "renderer_prompt",
    "negative_prompt",
    "source_frame",
    "source_frames",
}


class DocumentaryTreatmentError(ValueError):
    """Raised when a History V4 treatment cannot be compiled safely."""


def canonical_json(value: Any) -> str:
    """Return stable JSON while excluding the top-level artifact hash."""

    if isinstance(value, Mapping):
        payload = dict(value)
        payload.pop("artifact_hash", None)
    else:
        payload = value
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _load(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    if isinstance(value, (str, Path)):
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(f"{label} does not exist: {path}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise DocumentaryTreatmentError(f"{label} is not valid JSON: {exc}") from exc
        if not isinstance(payload, Mapping):
            raise DocumentaryTreatmentError(f"{label} must be a JSON object")
        return copy.deepcopy(dict(payload))
    raise DocumentaryTreatmentError(f"{label} must be a mapping or JSON path")


def _assert_safe(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key).casefold().replace("-", "_")
            if key in _PROHIBITED_KEYS:
                raise DocumentaryTreatmentError(
                    f"{'.'.join((*path, str(raw_key)))} is prohibited in renderer input"
                )
            _assert_safe(child, (*path, str(raw_key)))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_safe(child, (*path, str(index)))
    elif isinstance(value, str):
        text = value.strip().casefold()
        if any(token in text for token in ("http://", "https://", "file://", "data:", "blob:")):
            raise DocumentaryTreatmentError(
                f"{'.'.join(path) or 'value'} contains a remote or unresolved source"
            )


def _hash_for(value: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        candidate = value.get(key)
        if isinstance(candidate, str) and _HASH_RE.fullmatch(candidate.strip().lower()):
            return candidate.strip().lower()
    candidate = value.get("artifact_hash")
    if isinstance(candidate, str) and _HASH_RE.fullmatch(candidate.strip().lower()):
        return candidate.strip().lower()
    return canonical_sha256(value)


def _asset_records(manifest: Mapping[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    raw = manifest.get("assets") or manifest.get("approved_assets") or manifest.get("items") or []
    if isinstance(raw, Mapping):
        raw = [dict({"asset_id": key}, **(dict(value) if isinstance(value, Mapping) else {})) for key, value in raw.items()]
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        raw = []
    records: dict[str, dict[str, Any]] = {}
    credits: dict[str, Any] = {}
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        record = dict(item)
        asset_id = str(record.get("asset_id") or record.get("id") or "").strip()
        if not _ID_RE.fullmatch(asset_id):
            raise DocumentaryTreatmentError(f"asset manifest contains invalid asset ID: {asset_id!r}")
        if record.get("render_eligible") is not True:
            raise DocumentaryTreatmentError(f"asset {asset_id!r} is not render eligible")
        _assert_safe({key: value for key, value in record.items() if key not in {"local_path", "path"}})
        records[asset_id] = record
        credit_id = str(record.get("credit_id") or f"credit-{asset_id}")
        credits[credit_id] = {
            "credit_id": credit_id,
            "asset_id": asset_id,
            "display": str(record.get("attribution") or record.get("credit") or asset_id),
            "license": str(record.get("license") or record.get("rights") or "operator-approved"),
        }
    return records, credits


def _citation_ids(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (str, Mapping)):
        value = [value]
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        raise DocumentaryTreatmentError("citations must be an array")
    result: list[Any] = []
    for item in value:
        if isinstance(item, str):
            if item.strip():
                result.append(item.strip())
        elif isinstance(item, Mapping):
            citation = dict(item)
            citation_id = str(citation.get("citation_id") or citation.get("id") or "").strip()
            if not citation_id:
                raise DocumentaryTreatmentError("citation objects require citation_id")
            result.append({"citation_id": citation_id, **{key: value for key, value in citation.items() if key not in {"id", "url", "source_url", "path"}}})
        else:
            raise DocumentaryTreatmentError("citation entries must be IDs or objects")
    return result


def _research_citation_ids(packet: Mapping[str, Any]) -> set[str]:
    ids: set[str] = set()
    for key in ("citations", "sources", "claims"):
        raw = packet.get(key) or []
        if isinstance(raw, Mapping):
            raw = list(raw.values())
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            continue
        for item in raw:
            if not isinstance(item, Mapping):
                continue
            for field in ("citation_id", "source_id", "claim_id", "id"):
                value = item.get(field)
                if value:
                    ids.add(str(value))
    return ids


def _function_for(shot: Mapping[str, Any]) -> str:
    for key in ("function", "visual_function", "documentary_function", "visual_type", "composition"):
        value = shot.get(key)
        if value:
            function = str(value).strip().casefold()
            if function in DOCUMENTARY_FUNCTIONS:
                return function
    params = shot.get("parameters")
    if isinstance(params, Mapping):
        value = params.get("documentary_function") or params.get("function")
        if value and str(value).casefold() in DOCUMENTARY_FUNCTIONS:
            return str(value).casefold()
    raise DocumentaryTreatmentError("shot is missing a supported documentary function")


def _shot_list(shot_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = shot_plan.get("shots") or shot_plan.get("scenes") or shot_plan.get("segments") or []
    if isinstance(raw, Mapping):
        raw = list(raw.values())
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        raise DocumentaryTreatmentError("shot plan must contain a shots array")
    result: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise DocumentaryTreatmentError("shot plan entries must be objects")
        result.append(dict(item))
    if not result:
        raise DocumentaryTreatmentError("shot plan must contain at least one shot")
    return result


def _style_atoms(art_bible: Mapping[str, Any], function: str) -> list[str]:
    composition = art_bible.get("composition")
    if isinstance(composition, Mapping):
        functions = composition.get("functions")
        if isinstance(functions, Mapping) and isinstance(functions.get(function), Mapping):
            ids = functions[function].get("atom_ids")
            if isinstance(ids, Sequence) and not isinstance(ids, (str, bytes, bytearray)) and ids:
                return [str(value) for value in ids]
    return [function.replace("_", "-")]


def _palette_roles(art_bible: Mapping[str, Any], function: str) -> list[str]:
    palette = art_bible.get("palette")
    if isinstance(palette, Mapping):
        values = [str(key) for key in palette.keys()]
        if values:
            preferred = [key for key in ("paper", "ink", "rust", "indigo", "jade") if key in values]
            return preferred[:3] or values[:3]
    return ["paper", "ink", "rust"]


def _build_shot(
    raw: Mapping[str, Any],
    *,
    art_bible: Mapping[str, Any],
    assets: Mapping[str, Mapping[str, Any]],
    research: Mapping[str, Any],
    index: int,
) -> dict[str, Any]:
    function = _function_for(raw)
    asset_source = raw.get("asset_ids")
    if asset_source is None and isinstance(raw.get("parameters"), Mapping):
        asset_source = raw["parameters"].get("asset_ids")
    asset_ids = []
    if asset_source is not None:
        if isinstance(asset_source, str):
            asset_source = [asset_source]
        if not isinstance(asset_source, Sequence) or isinstance(asset_source, (bytes, bytearray)):
            raise DocumentaryTreatmentError(f"shot {index} asset_ids must be an array")
        asset_ids = [str(value).strip() for value in asset_source]
    for asset_id in asset_ids:
        if not _ID_RE.fullmatch(asset_id):
            raise DocumentaryTreatmentError(f"shot {index} has invalid asset ID {asset_id!r}")
        if asset_id not in assets:
            raise DocumentaryTreatmentError(f"shot {index} references unknown asset {asset_id!r}")
    citations = _citation_ids(raw.get("citations") if "citations" in raw else (raw.get("parameters") or {}).get("citations") if isinstance(raw.get("parameters"), Mapping) else [])
    known_citations = _research_citation_ids(research)
    for citation in citations:
        citation_id = str(citation.get("citation_id") if isinstance(citation, Mapping) else citation)
        if known_citations and citation_id not in known_citations:
            raise DocumentaryTreatmentError(f"shot {index} references unknown citation {citation_id!r}")
    params = raw.get("parameters")
    if not isinstance(params, Mapping):
        params = {}
    params = dict(params)
    # Remove fields that are promoted to the treatment boundary.
    for key in ("asset_ids", "citations", "source_kind", "scene_class", "manim_class", "function", "visual_type"):
        params.pop(key, None)
    scene = scene_factory(
        function,
        {
            **dict(raw),
            "asset_ids": asset_ids,
            "citations": citations,
            "parameters": params,
            "scene_id": raw.get("shot_id", raw.get("scene_id", index)),
            "style_atom_ids": raw.get("style_atom_ids") or _style_atoms(art_bible, function),
            "palette_roles": raw.get("palette_roles") or _palette_roles(art_bible, function),
            "duration_s": raw.get("duration_s") or (raw.get("timing") or {}).get("target_s", 2.0) if isinstance(raw.get("timing"), Mapping) else raw.get("duration_s", 2.0),
        },
    )
    scene["shot_id"] = raw.get("shot_id", raw.get("scene_id", index))
    scene["treatment_id"] = str(raw.get("treatment_id") or f"treatment-{function.replace('_', '-')}-{index:02d}")
    if not scene["treatment_id"].startswith("treatment-"):
        scene["treatment_id"] = f"treatment-{scene['treatment_id']}"
    scene["asset_ids"] = asset_ids
    scene["citations"] = citations
    scene["credit_ids"] = [str(assets[item].get("credit_id") or f"credit-{item}") for item in asset_ids]
    if function == "illustrated_reconstruction":
        scene["illustration_label"] = str(raw.get("illustration_label") or "ILLUSTRATION / RECONSTRUCTION")
    scene["scene_class"] = "DocumentaryScene"
    scene["manim_class"] = "DocumentaryScene"
    return scene


def validate_documentary_treatment(value: Mapping[str, Any] | str | Path) -> list[str]:
    """Return actionable Draft 7 errors for a treatment artifact."""

    payload = _load(value, "visual treatment")
    schema_path = Path(__file__).resolve().parents[2] / "configs" / "visual_treatment_v2.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"unable to load visual_treatment_v2 schema: {exc}"]
    errors = [
        f"schema {'.'.join(str(part) for part in error.absolute_path) or 'root'}: {error.message}"
        for error in Draft7Validator(schema).iter_errors(payload)
    ]
    try:
        _assert_safe(payload)
    except DocumentaryTreatmentError as exc:
        errors.append(str(exc))
    supplied = payload.get("artifact_hash")
    if supplied and supplied != canonical_sha256(payload):
        errors.append("artifact_hash does not match canonical treatment content")
    return sorted(set(errors))


class DocumentaryTreatmentService:
    """Compile and persist immutable History V4 visual treatments."""

    def __init__(self, *, schema_path: str | Path | None = None) -> None:
        self.schema_path = Path(schema_path) if schema_path is not None else Path(__file__).resolve().parents[2] / "configs" / "visual_treatment_v2.schema.json"

    def compile(
        self,
        shot_plan: Mapping[str, Any] | str | Path,
        art_bible: Mapping[str, Any] | str | Path,
        *,
        research_packet: Mapping[str, Any] | str | Path | None = None,
        asset_manifest: Mapping[str, Any] | str | Path | None = None,
        output_path: str | Path | None = None,
    ) -> dict[str, Any]:
        plan = _load(shot_plan, "shot plan")
        bible = _load(art_bible, "art bible")
        research = _load(research_packet, "research packet")
        manifest = _load(asset_manifest, "asset manifest")
        _assert_safe(plan)
        _assert_safe(bible)
        # Research packets are allowed to retain source URLs and locators in
        # their own evidence domain.  Only their immutable hash and citation
        # IDs are copied below; the packet itself never reaches a renderer.
        assets, credits = _asset_records(manifest)
        shots = _shot_list(plan)
        compiled = [
            _build_shot(
                raw,
                art_bible=bible,
                assets=assets,
                research=research,
                index=index,
            )
            for index, raw in enumerate(shots, start=1)
        ]
        total_duration = sum(float(item.get("duration_s") or 0.0) for item in compiled)
        concept_duration = sum(
            float(item.get("duration_s") or 0.0)
            for item in compiled
            if item.get("function") == "concept_mechanics_cutaway"
        )
        if total_duration <= 0:
            raise DocumentaryTreatmentError("treatment duration must be positive")
        if concept_duration / total_duration > 0.15 + 1e-9:
            raise DocumentaryTreatmentError(
                f"concept mechanics runtime is {concept_duration / total_duration:.1%}; maximum is 15%"
            )
        artifact: dict[str, Any] = {
            "schema_version": TREATMENT_VERSION,
            "source_kind": "documentary",
            "art_bible_id": str(bible.get("id") or "combat-history-longform-cutout-fork-v1"),
            "art_bible_hash": _hash_for(bible, "art_bible_hash"),
            "shot_plan_hash": _hash_for(plan, "shot_plan_hash"),
            "research_hash": _hash_for(research, "research_hash"),
            "asset_manifest_hash": _hash_for(manifest, "asset_manifest_hash"),
            "episode_id": str(plan.get("episode_id") or plan.get("source_id") or "history-of-bjj"),
            "duration_s": round(total_duration, 6),
            "credits": credits,
            "shots": compiled,
        }
        artifact["artifact_hash"] = canonical_sha256(artifact)
        errors = validate_documentary_treatment(artifact)
        if errors:
            raise DocumentaryTreatmentError("; ".join(errors))
        if output_path is not None:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return artifact

    build = compile
    compile_treatments = compile

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        payload = job.input_payload if isinstance(job.input_payload, Mapping) else {}
        configs = ctx.configs if isinstance(ctx.configs, Mapping) else {}
        plan = payload.get("shot_plan") or payload.get("shot_plan_path") or ctx.job_dir / "shot_plan.json"
        bible = payload.get("art_bible") or payload.get("art_bible_path") or configs.get("art_bible") or ctx.job_dir / "art_bible.json"
        research = payload.get("research_packet") or payload.get("research_packet_path") or ctx.job_dir / "research_packet.json"
        assets = (
            payload.get("asset_manifest")
            or payload.get("asset_manifest_path")
            or ctx.job_dir / "resolved_assets.json"
        )
        output = ctx.job_dir / "visual_treatment.v2.json"
        artifact = self.compile(plan, bible, research_packet=research, asset_manifest=assets, output_path=output)
        return StageOutput({"artifact_path": output.name, "schema_version": artifact["schema_version"], "shot_count": len(artifact["shots"]), "duration_s": artifact["duration_s"], "artifact_hash": artifact["artifact_hash"]})


def compile_treatments(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return DocumentaryTreatmentService().compile(*args, **kwargs)


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return DocumentaryTreatmentService().run_stage(job, ctx)


__all__ = [
    "TREATMENT_VERSION",
    "DocumentaryTreatmentError",
    "DocumentaryTreatmentService",
    "canonical_json",
    "canonical_sha256",
    "compile_treatments",
    "validate_documentary_treatment",
    "run_stage",
]
