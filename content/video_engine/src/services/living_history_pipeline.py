"""History V4.1 treatment and Storyboard 2.3 adapters.

Narration remains attached to its original documentary scene. Semantic
coverage slots become visual beats inside that scene so extra cuts never
duplicate spoken audio.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator, FormatChecker

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.services.documentary_treatment import (
    DocumentaryTreatmentService,
    canonical_sha256 as treatment_sha256,
    validate_documentary_treatment,
)
from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.history_pipeline import (
    DocumentaryStoryboardService,
)
from content.video_engine.src.services.living_editorial import (
    validate_editorial_coverage,
)
from content.video_engine.src.services.producer_orchestration import (
    validate_producer_plan,
)


def _read(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain an object")
    return payload


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _coverage_beats(
    coverage: Mapping[str, Any],
    producer_plan: Mapping[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    offsets: dict[str, float] = {}
    producer_by_slot = {
        str(block.get("coverage_slot_id")): block
        for block in (producer_plan or {}).get("blocks") or []
        if isinstance(block, Mapping)
    }
    for slot in coverage.get("slots") or []:
        parent = str(slot["parent_shot_id"])
        beat = {
            "coverage_slot_id": str(slot["slot_id"]),
            "narration_excerpt": str(slot["narration_excerpt"]),
            "parent_offset_s": round(offsets.get(parent, 0.0), 6),
            "duration_s": float(slot["duration_s"]),
            "semantic_purpose": str(slot["semantic_purpose"]),
            "visual_source": str(
                slot.get("selected_visual_source")
                or slot["preferred_visual_source"]
            ),
            "asset_ids": list(
                slot.get("selected_asset_ids") or slot.get("asset_ids") or []
            ),
            "motion_recipe": str(slot["motion_recipe"]),
            "micro_events": copy.deepcopy(list(slot["micro_events"])),
            "transition": str(slot.get("transition") or "hard_cut"),
        }
        producer = producer_by_slot.get(str(slot["slot_id"]))
        if producer is not None:
            beat.update(
                {
                    "producer_block_id": str(producer["block_id"]),
                    "producer_kind": str(producer["producer_kind"]),
                    "provider_duration_s": producer.get("provider_duration_s"),
                    "still_producers": copy.deepcopy(producer["still_producers"]),
                    "motion_producers": copy.deepcopy(producer["motion_producers"]),
                    "producer_prompt": copy.deepcopy(producer["prompt"]),
                }
            )
        grouped.setdefault(parent, []).append(beat)
        offsets[parent] = offsets.get(parent, 0.0) + float(slot["duration_s"])
    return grouped


class LivingDocumentaryTreatmentService:
    """Compile V4 treatment structure and bind deterministic visual beats."""

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        coverage_path = ctx.job_dir / "editorial_coverage.selected.json"
        coverage = _read(coverage_path, "selected editorial coverage")
        errors = validate_editorial_coverage(coverage)
        if errors:
            raise ValueError("selected editorial coverage failed: " + "; ".join(errors))
        assets_path = (
            ctx.job_dir
            / "asset_selection"
            / "resolved"
            / "resolved_assets.json"
        )
        treatment = DocumentaryTreatmentService().compile(
            ctx.job_dir / "shot_plan.json",
            ctx.job_dir / "art_bible.json",
            research_packet=ctx.job_dir / "research_packet.json",
            asset_manifest=assets_path,
        )
        producer_plan_path = ctx.job_dir / "producer_plan.json"
        producer_plan = _read(producer_plan_path, "producer plan") if producer_plan_path.is_file() else None
        if producer_plan is not None:
            expected_coverage_hash = str(
                coverage.get("source_coverage_hash")
                or job.config_snapshot.get("coverage_hash")
                or coverage.get("artifact_hash")
                or ""
            )
            producer_errors = validate_producer_plan(
                producer_plan,
                expected_art_bible_hash=str(
                    job.config_snapshot.get("art_bible_hash") or ""
                )
                or None,
                expected_coverage_hash=expected_coverage_hash,
            )
            if producer_errors:
                raise ValueError("producer plan failed: " + "; ".join(producer_errors))
        grouped = _coverage_beats(coverage, producer_plan)
        treatment["coverage_plan_hash"] = str(
            coverage.get("source_coverage_hash")
            or job.config_snapshot.get("coverage_hash")
            or ""
        )
        treatment["asset_selection_hash"] = str(coverage["asset_selection_hash"])
        for shot in treatment["shots"]:
            shot_id = str(shot["shot_id"])
            beats = grouped.get(shot_id)
            if not beats:
                raise ValueError(f"coverage has no visual beats for shot {shot_id}")
            params = copy.deepcopy(dict(shot.get("parameters") or {}))
            params["visual_beats"] = beats
            shot["parameters"] = params
            shot["asset_ids"] = sorted(
                {
                    *[str(value) for value in shot.get("asset_ids") or []],
                    *[
                        str(asset_id)
                        for beat in beats
                        for asset_id in beat["asset_ids"]
                    ],
                }
            )
            shot["uniqueness_signature"] = (
                f"{shot['uniqueness_signature']}:{beats[0]['motion_recipe']}:"
                f"{len(beats)}"
            )
        treatment["artifact_hash"] = treatment_sha256(treatment)
        errors = validate_documentary_treatment(treatment)
        if errors:
            raise ValueError("living treatment failed: " + "; ".join(errors))
        output = ctx.job_dir / "visual_treatment.v2.json"
        _write(output, treatment)
        return StageOutput(
            {
                "artifact_path": output.name,
                "schema_version": treatment["schema_version"],
                "shot_count": len(treatment["shots"]),
                "visual_beat_count": sum(
                    len(shot["parameters"]["visual_beats"])
                    for shot in treatment["shots"]
                ),
                "coverage_hash": treatment["coverage_plan_hash"],
                "asset_selection_hash": treatment["asset_selection_hash"],
                "asset_manifest_hash": treatment["asset_manifest_hash"],
                "producer_plan_hash": (
                    str(producer_plan["artifact_hash"]) if producer_plan else ""
                ),
                "artifact_hash": treatment["artifact_hash"],
                "cost_usd": 0.0,
            }
        )


class LivingDocumentaryStoryboardService:
    """Upgrade a V4 documentary board into narration-safe Storyboard 2.3."""

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        assets_path = (
            ctx.job_dir
            / "asset_selection"
            / "resolved"
            / "resolved_assets.json"
        )
        if not assets_path.is_file():
            raise ValueError("selected resolved assets are required for Storyboard 2.3")
        DocumentaryStoryboardService().run_stage(job, ctx)

        board = _read(ctx.job_dir / "storyboard.json", "Storyboard 2.2")
        treatment = _read(
            ctx.job_dir / "visual_treatment.v2.json", "visual treatment"
        )
        by_shot = {
            str(shot["shot_id"]): shot for shot in treatment["shots"]
        }
        board["schema_version"] = "2.3.0"
        board["coverage_plan_hash"] = str(treatment["coverage_plan_hash"])
        board["asset_selection_hash"] = str(treatment["asset_selection_hash"])
        board["asset_manifest_hash"] = str(treatment["asset_manifest_hash"])
        board["art_direction"]["treatment_hash"] = treatment["artifact_hash"]
        board["packaging"]["credits_path"] = (
            "asset_selection/resolved/credits.json"
        )
        plan = _read(ctx.job_dir / "shot_plan.json", "shot plan")
        scene_to_shot = {
            index: str(shot["shot_id"])
            for index, shot in enumerate(plan["shots"], start=1)
        }
        for scene in board["scenes"]:
            scene_id = int(scene["scene_id"])
            shot_id = scene_to_shot.get(scene_id)
            if shot_id is None:
                raise ValueError(
                    f"Storyboard 2.3 scene {scene_id} has no source shot"
                )
            treated = by_shot.get(shot_id)
            if treated is None:
                raise ValueError(
                    f"Storyboard 2.3 scene {scene_id} maps to missing "
                    f"treatment shot {shot_id!r}"
                )
            beats = copy.deepcopy(treated["parameters"]["visual_beats"])
            scene["visual_beats"] = beats
            scene["visual_treatment_ids"] = [
                f"{treated['treatment_id']}-beat-{index:02d}"
                for index in range(1, len(beats) + 1)
            ]
            scene["asset_ids"] = sorted(
                {
                    str(asset_id)
                    for beat in beats
                    for asset_id in beat["asset_ids"]
                }
            )
            scene["parameters"]["visual_beats"] = beats
        schema = _read(
            Path(ctx.configs.get("video_engine_root", Path.cwd()))
            / "configs"
            / "storyboard_v2_3.schema.json",
            "Storyboard 2.3 schema",
        )
        errors = sorted(
            Draft7Validator(
                schema, format_checker=FormatChecker()
            ).iter_errors(board),
            key=lambda error: [str(value) for value in error.absolute_path],
        )
        if errors:
            raise ValueError(
                "built Storyboard 2.3 failed schema validation: "
                + "; ".join(error.message for error in errors)
            )
        _write(ctx.job_dir / "storyboard.json", board)
        storyboard_hash = canonical_sha256(board)
        return StageOutput(
            {
                "artifact_path": "storyboard.json",
                "schema_version": "2.3.0",
                "storyboard_hash": storyboard_hash,
                "scene_count": len(board["scenes"]),
                "visual_beat_count": sum(
                    len(scene["visual_beats"]) for scene in board["scenes"]
                ),
                "coverage_hash": board["coverage_plan_hash"],
                "asset_selection_hash": board["asset_selection_hash"],
                "asset_manifest_hash": board["asset_manifest_hash"],
                "cost_usd": 0.0,
            }
        )


__all__ = [
    "LivingDocumentaryStoryboardService",
    "LivingDocumentaryTreatmentService",
]
