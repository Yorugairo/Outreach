from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_dotenv
from content.video_engine.src.guards.storyboard_guard import guard
from content.video_engine.src.models import VideoRun, VideoStageEvent
from content.video_engine.src.pipeline import (
    VideoPipeline,
    VideoPipelineGateApprovalError,
    build_default_stage_fns,
)
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)


VIDEO_ENGINE_ROOT = Path(__file__).resolve().parent
DEFAULT_ARTIFACT_ROOT = VIDEO_ENGINE_ROOT / "runtime" / "jobs"
DEFAULT_SCHEMA = VIDEO_ENGINE_ROOT / "configs" / "storyboard.schema.json"
DEFAULT_DOTENV = PROJECT_ROOT / ".env"
COMMANDS = {
    "run",
    "resume",
    "status",
    "approve",
    "validate",
    "validate-study",
    "validate-art-bible",
    "validate-martial-lanes",
    "validate-martial-style-profile",
    "validate-martial-style-registry",
    "validate-martial-channel-v2",
    "validate-martial-lane-v2",
    "validate-martial-style-selection",
    "validate-content-node",
    "validate-martial-asset-catalog",
    "validate-martial-scene-blocks",
    "plan-content-node",
    "run-content-node",
    "resume-content-node",
    "content-node-status",
    "resolve-martial-asset-demand",
    "schedule-martial-matters",
    "validate-history",
    "validate-research",
    "validate-assets",
    "validate-stock-batch",
    "validate-asset-selection",
    "validate-flow-snapshot",
    "validate-character-pack",
    "validate-producer-plan",
    "inventory-creative-assets",
    "validate-creative-inventory",
    "compile-communication-grammar",
    "validate-communication-grammar",
    "validate-style-packs",
    "validate-asset-map",
    "validate-foundation-review",
    "validate-world-packs",
    "validate-scene-bundle",
    "validate-scene-flow",
    "validate-generated-visuals",
    "validate-generated-block-batch",
    "compile-timestamped-plate-plan",
    "validate-timestamped-plate-plan",
    "replace-timestamped-plate-candidate",
    "promote-timestamped-plates",
    "validate-plate-motion-plan",
    "validate-plate-motion-manifest",
    "validate-editorial-motion",
    "compile-editorial-motion",
    "compile-canonical-visual-coverage",
    "analyze-timestamped-semantic-coverage",
    "render-editorial-motion-revision",
    "compile-higgsfield-blocks",
    "compile-higgsfield-audio-blocks",
    "validate-higgsfield-blocks",
    "compile-history-narration",
    "validate-history-narration",
    "resolve-canonical-audio",
    "validate-canonical-audio",
    "bind-higgsfield-audio",
    "resolve-elevenlabs-audio",
    "validate-elevenlabs-audio",
    "higgsfield-preflight",
    "compile-higgsfield-job",
    "validate-higgsfield-job",
    "record-higgsfield-task",
    "record-higgsfield-output",
    "compile-higgsfield-assembly",
    "media-generate",
    "magnific-video-generate",
    "magnific-image-generate",
}


def _video_dotenv_candidates() -> list[Path]:
    """Return local env candidates from the worktree to its owning checkout."""

    override = (os.environ.get("VIDEO_ENGINE_DOTENV") or "").strip()
    if override:
        return [Path(override)]
    candidates = [DEFAULT_DOTENV, PROJECT_ROOT / "docs" / "local.env"]
    candidates.extend(parent / "docs" / "local.env" for parent in PROJECT_ROOT.parents)
    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def load_video_environment(dotenv_path: str | Path | None = None) -> None:
    """Load ignored provider settings without overriding process values."""

    if dotenv_path is not None:
        load_dotenv(dotenv_path)
        return
    for candidate in _video_dotenv_candidates():
        if candidate.is_file():
            load_dotenv(candidate)


def _repository(artifact_root: str | Path) -> FileBackedVideoJobRepository:
    return FileBackedVideoJobRepository(artifact_root)


def _load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_storyboard(path: str | Path) -> list[str]:
    _ok, violations = guard(path, schema_path=DEFAULT_SCHEMA)
    return violations


def validate_art_bible_contract(path: str | Path) -> list[str]:
    """Dispatch public validation to the artifact's declared contract version."""

    try:
        payload = _load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"art bible could not be read: {exc}"]
    if payload.get("schema_version") != "art_bible.v2":
        from content.video_engine.src.services.art_direction import (
            ArtDirectionService,
        )

        return ArtDirectionService().check_art_bible(path)

    from jsonschema import Draft7Validator

    schema = _load_json(VIDEO_ENGINE_ROOT / "configs" / "art_bible_v2.schema.json")
    errors = [
        (
            "schema "
            + (".".join(str(value) for value in error.absolute_path) or "root")
            + f": {error.message}"
        )
        for error in sorted(
            Draft7Validator(schema).iter_errors(payload),
            key=lambda item: [str(value) for value in item.absolute_path],
        )
    ]
    serialized = json.dumps(payload, ensure_ascii=False).casefold()
    for prohibited in (
        "in the style of",
        "youtube reference pack",
        "consultant outline",
        "creator_name",
        "source_frame",
    ):
        if prohibited in serialized:
            errors.append(
                f"art_bible.v2 contains prohibited renderer input {prohibited!r}"
            )
    derivation = payload.get("profile_derivation")
    if isinstance(derivation, dict):
        profile_id = str(derivation.get("base_profile_id") or "")
        profile_path = (
            VIDEO_ENGINE_ROOT
            / "configs"
            / "production_profiles"
            / f"{profile_id}.json"
        )
        try:
            profile = _load_json(profile_path)
            profile_schema = _load_json(
                VIDEO_ENGINE_ROOT
                / "configs"
                / "production_profile.schema.json"
            )
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"production profile could not be read: {exc}")
        else:
            profile_errors = sorted(
                Draft7Validator(profile_schema).iter_errors(profile),
                key=lambda item: [
                    str(value) for value in item.absolute_path
                ],
            )
            errors.extend(
                "production profile schema "
                + (
                    ".".join(str(value) for value in error.absolute_path)
                    or "root"
                )
                + f": {error.message}"
                for error in profile_errors
            )
            from content.video_engine.src.services.history_contracts import (
                canonical_sha256,
            )

            profile_hash = canonical_sha256(profile)
            if profile.get("artifact_hash") != profile_hash:
                errors.append("production profile artifact_hash is stale")
            if derivation.get("base_profile_hash") != profile_hash:
                errors.append(
                    "art_bible.v2 base_profile_hash does not match "
                    "the production profile"
                )
    return errors


def _pipeline(repository: FileBackedVideoJobRepository) -> VideoPipeline:
    channel_dir = VIDEO_ENGINE_ROOT / "configs" / "channels"
    channel_configs = {
        path.stem: _load_json(path)
        for path in sorted(channel_dir.glob("*.json"))
    }
    return VideoPipeline(
        repository,
        configs={
            "project_root": PROJECT_ROOT,
            "video_engine_root": VIDEO_ENGINE_ROOT,
            "channel_configs": channel_configs,
            "render_profiles": _load_json(
                VIDEO_ENGINE_ROOT / "configs" / "render_profiles.json"
            ),
            "article_url_template": (
                "https://nationalbjjregistry.com/techniques/{position}/{slug}"
            ),
            "registry_url": "https://nationalbjjregistry.com",
            "stock_search_live": bool(os.environ.get("MAGNIFIC_API_KEY")),
            "stock_candidates_per_slot": 3,
        },
        stage_fns=build_default_stage_fns(),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Content video engine control plane")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--source", required=True)
    run_parser.add_argument("--channel", default="combat-science")
    run_parser.add_argument("--targets", default="landscape,vertical")

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("job_id")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("job_id", nargs="?")
    status_parser.add_argument(
        "--json",
        action="store_true",
        help="emit the full machine-readable run payload",
    )

    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("job_id")
    approve_parser.add_argument(
        "--gate",
        required=True,
        choices=["research", "assets", "visual", "a", "b"],
    )
    approve_parser.add_argument(
        "--rubric",
        help="Review rubric JSON; required for research, assets, or visual",
    )

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("storyboard")
    study_parser = subparsers.add_parser("validate-study")
    study_parser.add_argument("file")
    art_bible_parser = subparsers.add_parser("validate-art-bible")
    art_bible_parser.add_argument("file")
    martial_lanes_parser = subparsers.add_parser("validate-martial-lanes")
    martial_lanes_parser.add_argument("file")
    martial_style_profile_parser = subparsers.add_parser(
        "validate-martial-style-profile"
    )
    martial_style_profile_parser.add_argument("file")
    martial_style_registry_parser = subparsers.add_parser(
        "validate-martial-style-registry"
    )
    martial_style_registry_parser.add_argument("file")
    martial_channel_v2_parser = subparsers.add_parser("validate-martial-channel-v2")
    martial_channel_v2_parser.add_argument("file")
    martial_lane_v2_parser = subparsers.add_parser("validate-martial-lane-v2")
    martial_lane_v2_parser.add_argument("file")
    martial_style_selection_parser = subparsers.add_parser("validate-martial-style-selection")
    martial_style_selection_parser.add_argument("file")
    content_node_parser = subparsers.add_parser("validate-content-node")
    content_node_parser.add_argument("file")
    content_node_parser.add_argument("--format-family", required=True)
    martial_catalog_parser = subparsers.add_parser("validate-martial-asset-catalog")
    martial_catalog_parser.add_argument("file")
    martial_catalog_parser.add_argument("--taxonomy", required=True)
    martial_scene_parser = subparsers.add_parser("validate-martial-scene-blocks")
    martial_scene_parser.add_argument("file")
    martial_scene_parser.add_argument("--catalog", required=True)
    martial_scene_parser.add_argument("--taxonomy", required=True)
    plan_content_parser = subparsers.add_parser("plan-content-node")
    plan_content_parser.add_argument("--node", required=True)
    plan_content_parser.add_argument("--format-family", required=True)
    run_content_parser = subparsers.add_parser("run-content-node")
    run_content_parser.add_argument("--node", required=True)
    run_content_parser.add_argument("--format-family", required=True)
    run_content_parser.add_argument("--style-selection")
    run_content_parser.add_argument("--content-node-root", default=str(VIDEO_ENGINE_ROOT / "runtime" / "content_nodes"))
    resume_content_parser = subparsers.add_parser("resume-content-node")
    resume_content_parser.add_argument("--id", required=True)
    resume_content_parser.add_argument("--content-node-root", default=str(VIDEO_ENGINE_ROOT / "runtime" / "content_nodes"))
    content_node_status_parser = subparsers.add_parser("content-node-status")
    content_node_status_parser.add_argument("--id", required=True)
    content_node_status_parser.add_argument("--content-node-root", default=str(VIDEO_ENGINE_ROOT / "runtime" / "content_nodes"))
    content_node_status_parser.add_argument("--require-children-gate-b", action="store_true")
    content_node_status_parser.add_argument("--require-qc-pass", action="store_true")
    resolve_demand_parser = subparsers.add_parser("resolve-martial-asset-demand")
    resolve_demand_parser.add_argument("demand")
    resolve_demand_parser.add_argument("--catalog", required=True)
    resolve_demand_parser.add_argument("--taxonomy", required=True)
    resolve_demand_parser.add_argument("--scene-blocks")
    schedule_martial_parser = subparsers.add_parser("schedule-martial-matters")
    schedule_martial_parser.add_argument("--fixture", required=True)
    schedule_martial_parser.add_argument(
        "--config",
        default=str(VIDEO_ENGINE_ROOT / "configs" / "martial_matters_scheduler.json"),
    )
    schedule_martial_parser.add_argument("--dry-run", action="store_true")
    history_parser = subparsers.add_parser("validate-history")
    history_parser.add_argument("file")
    research_parser = subparsers.add_parser("validate-research")
    research_parser.add_argument("file")
    assets_parser = subparsers.add_parser("validate-assets")
    assets_parser.add_argument("file")
    stock_parser = subparsers.add_parser("validate-stock-batch")
    stock_parser.add_argument("file")
    stock_parser.add_argument("--job-dir")
    selection_parser = subparsers.add_parser("validate-asset-selection")
    selection_parser.add_argument("file")
    selection_parser.add_argument("--batch", required=True)
    selection_parser.add_argument("--coverage-hash", default="")
    flow_parser = subparsers.add_parser("validate-flow-snapshot")
    flow_parser.add_argument("file")
    character_parser = subparsers.add_parser("validate-character-pack")
    character_parser.add_argument("file")
    producer_plan_parser = subparsers.add_parser("validate-producer-plan")
    producer_plan_parser.add_argument("file")
    inventory_parser = subparsers.add_parser("inventory-creative-assets")
    inventory_parser.add_argument(
        "--root",
        action="append",
        required=True,
        help="repeatable inventory root in the form id=path",
    )
    inventory_parser.add_argument("--asset-manifest", action="append", default=[])
    inventory_parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    inventory_parser.add_argument(
        "--default-classification",
        choices=[
            "approved_reusable",
            "reference_only",
            "rejected",
            "superseded",
            "unknown",
        ],
        default="reference_only",
    )
    inventory_parser.add_argument("--output", required=True)
    validate_inventory_parser = subparsers.add_parser("validate-creative-inventory")
    validate_inventory_parser.add_argument("file")
    validate_inventory_parser.add_argument("--skip-files", action="store_true")
    compile_grammar_parser = subparsers.add_parser("compile-communication-grammar")
    compile_grammar_parser.add_argument("--output", required=True)
    validate_grammar_parser = subparsers.add_parser("validate-communication-grammar")
    validate_grammar_parser.add_argument("file")
    validate_style_packs_parser = subparsers.add_parser("validate-style-packs")
    validate_style_packs_parser.add_argument("file")
    validate_style_packs_parser.add_argument("--calibration-inventory")
    validate_style_packs_parser.add_argument("--asset-map")
    validate_style_packs_parser.add_argument("--skip-files", action="store_true")
    validate_asset_map_parser = subparsers.add_parser("validate-asset-map")
    validate_asset_map_parser.add_argument("file")
    validate_asset_map_parser.add_argument("--grammar-hash")
    validate_foundation_parser = subparsers.add_parser("validate-foundation-review")
    validate_foundation_parser.add_argument("file")
    validate_foundation_parser.add_argument("--asset-map", required=True)
    validate_foundation_parser.add_argument("--world-packs", required=True)
    validate_foundation_parser.add_argument("--style-packs", required=True)
    validate_foundation_parser.add_argument("--calibration-inventory", required=True)
    validate_foundation_parser.add_argument("--asset-manifest", required=True)
    validate_foundation_parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    validate_foundation_parser.add_argument("--skip-files", action="store_true")
    validate_world_packs_parser = subparsers.add_parser("validate-world-packs")
    validate_world_packs_parser.add_argument("file")
    validate_world_packs_parser.add_argument("--asset-map")
    validate_world_packs_parser.add_argument("--style-packs")
    validate_world_packs_parser.add_argument("--grammar-hash")
    validate_scene_bundle_parser = subparsers.add_parser("validate-scene-bundle")
    validate_scene_bundle_parser.add_argument("file")
    validate_scene_bundle_parser.add_argument("--asset-map")
    validate_scene_bundle_parser.add_argument("--style-packs")
    validate_scene_flow_parser = subparsers.add_parser("validate-scene-flow")
    validate_scene_flow_parser.add_argument("file")
    validate_scene_flow_parser.add_argument("--asset-map")
    validate_scene_flow_parser.add_argument("--style-packs")
    validate_scene_flow_parser.add_argument("--grammar-hash")
    generated_visuals_parser = subparsers.add_parser(
        "validate-generated-visuals"
    )
    generated_visuals_parser.add_argument("file")
    generated_visuals_parser.add_argument("--job-dir", required=True)
    generated_blocks_parser = subparsers.add_parser(
        "validate-generated-block-batch"
    )
    generated_blocks_parser.add_argument("file")
    generated_blocks_parser.add_argument("--job-dir", required=True)
    generated_blocks_parser.add_argument("--plan")
    timestamped_plate_plan_parser = subparsers.add_parser(
        "compile-timestamped-plate-plan"
    )
    timestamped_plate_plan_parser.add_argument("--coverage", required=True)
    timestamped_plate_plan_parser.add_argument("--prompt-spine", required=True)
    timestamped_plate_plan_parser.add_argument("--art-bible-id", default="")
    timestamped_plate_plan_parser.add_argument("--art-bible-hash", default="")
    timestamped_plate_plan_parser.add_argument("--style-atom", action="append", default=[])
    timestamped_plate_plan_parser.add_argument("--output", required=True)
    validate_timestamped_plate_plan_parser = subparsers.add_parser(
        "validate-timestamped-plate-plan"
    )
    validate_timestamped_plate_plan_parser.add_argument("file")
    validate_timestamped_plate_plan_parser.add_argument("--coverage")
    validate_timestamped_plate_plan_parser.add_argument("--prompt-spine")
    promote_timestamped_plates_parser = subparsers.add_parser(
        "promote-timestamped-plates",
        help="Promote an operator-approved timestamped plate inventory into asset_manifest.v1",
    )
    promote_timestamped_plates_parser.add_argument("--inventory", required=True)
    promote_timestamped_plates_parser.add_argument("--plan", required=True)
    promote_timestamped_plates_parser.add_argument("--job-dir", required=True)
    promote_timestamped_plates_parser.add_argument("--manifest-id", required=True)
    promote_timestamped_plates_parser.add_argument("--project-id", required=True)
    promote_timestamped_plates_parser.add_argument("--episode-id", required=True)
    promote_timestamped_plates_parser.add_argument("--approved-by", required=True)
    promote_timestamped_plates_parser.add_argument("--approved-at", required=True)
    promote_timestamped_plates_parser.add_argument("--output", required=True)
    replace_timestamped_plate_parser = subparsers.add_parser(
        "replace-timestamped-plate-candidate",
        help="Create a new timestamped candidate inventory with one original replacement plate",
    )
    replace_timestamped_plate_parser.add_argument("--inventory", required=True)
    replace_timestamped_plate_parser.add_argument("--plan", required=True)
    replace_timestamped_plate_parser.add_argument("--job-dir", required=True)
    replace_timestamped_plate_parser.add_argument("--order", required=True, type=int)
    replace_timestamped_plate_parser.add_argument("--replacement-path", required=True)
    replace_timestamped_plate_parser.add_argument("--output", required=True)
    plate_motion_plan_parser = subparsers.add_parser("validate-plate-motion-plan")
    plate_motion_plan_parser.add_argument("file")
    plate_motion_plan_parser.add_argument("--job-dir", required=True)
    plate_motion_plan_parser.add_argument("--batch-hash", default="")
    plate_motion_manifest_parser = subparsers.add_parser(
        "validate-plate-motion-manifest"
    )
    plate_motion_manifest_parser.add_argument("file")
    plate_motion_manifest_parser.add_argument("--job-dir", required=True)
    editorial_motion_parser = subparsers.add_parser("validate-editorial-motion")
    editorial_motion_parser.add_argument("file")
    editorial_motion_parser.add_argument("--asset-map")
    editorial_motion_sample_parser = subparsers.add_parser(
        "sample-editorial-motion",
        help="Create an immutable review sample ending on an authored cut boundary",
    )
    editorial_motion_sample_parser.add_argument("--plan", required=True)
    editorial_motion_sample_parser.add_argument("--asset-map", required=True)
    editorial_motion_sample_parser.add_argument("--end-s", type=float, required=True)
    editorial_motion_sample_parser.add_argument("--output", required=True)
    compile_editorial_motion_parser = subparsers.add_parser(
        "compile-editorial-motion"
    )
    compile_editorial_motion_parser.add_argument("--storyboard", required=True)
    compile_editorial_motion_parser.add_argument("--beat-plan", required=True)
    compile_editorial_motion_parser.add_argument("--narration", required=True)
    compile_editorial_motion_parser.add_argument("--audio", required=True)
    compile_editorial_motion_parser.add_argument("--words", required=True)
    compile_editorial_motion_parser.add_argument("--pacing-recipe", required=True)
    compile_editorial_motion_parser.add_argument("--shot-specs", required=True)
    compile_editorial_motion_parser.add_argument(
        "--scene-bundle", action="append", required=True
    )
    compile_editorial_motion_parser.add_argument("--scene-flow", required=True)
    compile_editorial_motion_parser.add_argument("--asset-map", required=True)
    compile_editorial_motion_parser.add_argument("--source-end", type=float)
    compile_editorial_motion_parser.add_argument("--output", required=True)
    compile_timestamped_editorial_motion_parser = subparsers.add_parser(
        "compile-timestamped-editorial-motion",
        help="Bind one approved original plate per timestamp slot to canonical narration timings",
    )
    compile_timestamped_editorial_motion_parser.add_argument("--plate-plan", required=True)
    compile_timestamped_editorial_motion_parser.add_argument("--asset-map", required=True)
    compile_timestamped_editorial_motion_parser.add_argument("--audio", required=True)
    compile_timestamped_editorial_motion_parser.add_argument("--words", required=True)
    compile_timestamped_editorial_motion_parser.add_argument("--pacing-recipe", required=True)
    compile_timestamped_editorial_motion_parser.add_argument("--output", required=True)
    timestamped_coverage_parser = subparsers.add_parser(
        "analyze-timestamped-semantic-coverage",
        help="Report canonical narration spans that need new semantic plate assignments",
    )
    timestamped_coverage_parser.add_argument("--plate-plan", required=True)
    timestamped_coverage_parser.add_argument("--words", required=True)
    timestamped_coverage_parser.add_argument("--output", required=True)
    canonical_coverage_parser = subparsers.add_parser(
        "compile-canonical-visual-coverage",
        help="Create a semantic two-to-six-second image schedule from final narration",
    )
    canonical_coverage_parser.add_argument("--audio", required=True)
    canonical_coverage_parser.add_argument("--words", required=True)
    canonical_coverage_parser.add_argument("--target-duration", type=float, default=4.0)
    canonical_coverage_parser.add_argument("--minimum-duration", type=float, default=1.8)
    canonical_coverage_parser.add_argument("--maximum-duration", type=float, default=6.0)
    canonical_coverage_parser.add_argument("--output", required=True)
    editorial_revision_parser = subparsers.add_parser(
        "render-editorial-motion-revision"
    )
    editorial_revision_parser.add_argument("--plan", required=True)
    editorial_revision_parser.add_argument("--asset-map", required=True)
    editorial_revision_parser.add_argument("--pacing-recipe", required=True)
    editorial_revision_parser.add_argument("--audio", required=True)
    editorial_revision_parser.add_argument("--asset-root", required=True)
    editorial_revision_parser.add_argument("--job-dir", required=True)
    editorial_revision_parser.add_argument("--output-dir", required=True)
    editorial_revision_parser.add_argument("--overlay-map")
    editorial_revision_parser.add_argument("--editor-root")
    editorial_revision_parser.add_argument("--browser-executable")
    editorial_revision_parser.add_argument("--width", type=int, default=854)
    editorial_revision_parser.add_argument("--height", type=int, default=480)
    editorial_revision_parser.add_argument("--fps", type=int, default=15)
    blocks_parser = subparsers.add_parser("compile-higgsfield-blocks")
    blocks_parser.add_argument("--coverage", required=True)
    blocks_parser.add_argument("--generated-batch", required=True)
    blocks_parser.add_argument("--job-dir", required=True)
    blocks_parser.add_argument("--output", required=True)
    blocks_parser.add_argument("--block-count", type=int, default=60)
    blocks_parser.add_argument("--character-pack")
    blocks_parser.add_argument("--art-bible-hash", default="")
    blocks_parser.add_argument("--storyboard-hash", default="")
    audio_blocks_parser = subparsers.add_parser("compile-higgsfield-audio-blocks")
    audio_blocks_parser.add_argument("--coverage", required=True)
    audio_blocks_parser.add_argument("--generated-batch", required=True)
    audio_blocks_parser.add_argument("--narration", required=True)
    audio_blocks_parser.add_argument("--audio", required=True)
    audio_blocks_parser.add_argument("--job-dir", required=True)
    audio_blocks_parser.add_argument("--output", required=True)
    audio_blocks_parser.add_argument("--character-pack")
    audio_blocks_parser.add_argument("--art-bible-hash", default="")
    audio_blocks_parser.add_argument("--storyboard-hash", default="")
    validate_blocks_parser = subparsers.add_parser("validate-higgsfield-blocks")
    validate_blocks_parser.add_argument("file")
    validate_blocks_parser.add_argument("--job-dir", required=True)
    validate_blocks_parser.add_argument("--coverage-hash", default="")
    validate_blocks_parser.add_argument("--plate-batch-hash", default="")
    validate_blocks_parser.add_argument("--block-count", type=int, default=60)
    narration_parser = subparsers.add_parser("compile-history-narration")
    narration_parser.add_argument("--storyboard", required=True)
    narration_parser.add_argument("--source")
    narration_parser.add_argument("--output", required=True)
    validate_narration_parser = subparsers.add_parser("validate-history-narration")
    validate_narration_parser.add_argument("file")
    validate_narration_parser.add_argument("--storyboard-hash", default="")
    validate_narration_parser.add_argument("--research-hash", default="")
    validate_narration_parser.add_argument("--min-words", type=int, default=1)
    canonical_audio_parser = subparsers.add_parser("resolve-canonical-audio")
    canonical_audio_parser.add_argument("--narration", required=True)
    canonical_audio_parser.add_argument("--job-dir", required=True)
    canonical_audio_parser.add_argument("--manifest")
    canonical_audio_parser.add_argument("--output", required=True)
    canonical_audio_parser.add_argument("--storyboard-hash", default="")
    canonical_audio_parser.add_argument("--voice-id", default="")
    canonical_audio_parser.add_argument("--allow-synthesis", action="store_true")
    validate_canonical_audio_parser = subparsers.add_parser("validate-canonical-audio")
    validate_canonical_audio_parser.add_argument("file")
    validate_canonical_audio_parser.add_argument("--job-dir", required=True)
    validate_canonical_audio_parser.add_argument("--narration-hash", default="")
    validate_canonical_audio_parser.add_argument("--storyboard-hash", default="")
    validate_canonical_audio_parser.add_argument("--voice-id", default="")
    audio_parser = subparsers.add_parser("resolve-elevenlabs-audio")
    audio_parser.add_argument("--blocks", required=True)
    audio_parser.add_argument("--job-dir", required=True)
    audio_parser.add_argument("--manifest")
    audio_parser.add_argument("--output", required=True)
    audio_parser.add_argument("--storyboard-hash", default="")
    audio_parser.add_argument("--voice-id", default="")
    audio_parser.add_argument(
        "--allow-synthesis",
        action="store_true",
        help="explicitly enable the ElevenLabs synthesis adapter; this CLI still requires an adapter",
    )
    validate_audio_parser = subparsers.add_parser("validate-elevenlabs-audio")
    validate_audio_parser.add_argument("file")
    validate_audio_parser.add_argument("--blocks", required=True)
    validate_audio_parser.add_argument("--job-dir", required=True)
    validate_audio_parser.add_argument("--voice-id", default="")
    validate_audio_parser.add_argument("--storyboard-hash", default="")
    preflight_parser = subparsers.add_parser("higgsfield-preflight")
    preflight_parser.add_argument("--model", default="seedance_2_0")
    preflight_parser.add_argument("--duration", type=float, default=10.0)
    preflight_parser.add_argument("--audio-references", type=int, default=1)
    job_parser = subparsers.add_parser("compile-higgsfield-job")
    job_parser.add_argument("--blocks", required=True)
    job_parser.add_argument("--audio", required=True)
    job_parser.add_argument("--job-dir", required=True)
    job_parser.add_argument("--output", required=True)
    job_parser.add_argument("--project-root")
    job_parser.add_argument("--character-pack")
    job_parser.add_argument("--model", default="seedance_2_0")
    job_parser.add_argument("--storyboard-hash", default="")
    job_parser.add_argument("--art-bible-hash", default="")
    validate_job_parser = subparsers.add_parser("validate-higgsfield-job")
    validate_job_parser.add_argument("file")
    validate_job_parser.add_argument("--job-dir", required=True)
    validate_job_parser.add_argument("--blocks-hash", default="")
    validate_job_parser.add_argument("--audio-hash", default="")
    validate_job_parser.add_argument("--model", default="")
    record_task_parser = subparsers.add_parser("record-higgsfield-task")
    record_task_parser.add_argument("--job", required=True)
    record_task_parser.add_argument("--job-dir", required=True)
    record_task_parser.add_argument("--block-id", required=True)
    record_task_parser.add_argument("--task-id", required=True)
    record_task_parser.add_argument("--status", default="submitted")
    record_task_parser.add_argument("--output", required=True)
    record_output_parser = subparsers.add_parser("record-higgsfield-output")
    record_output_parser.add_argument("--job", required=True)
    record_output_parser.add_argument("--job-dir", required=True)
    record_output_parser.add_argument("--block-id", required=True)
    record_output_parser.add_argument("--provider-output", required=True)
    record_output_parser.add_argument("--status", default="complete")
    record_output_parser.add_argument("--output", required=True)
    assembly_parser = subparsers.add_parser("compile-higgsfield-assembly")
    assembly_parser.add_argument("--job", required=True)
    assembly_parser.add_argument("--audio", required=True)
    assembly_parser.add_argument("--job-dir", required=True)
    assembly_parser.add_argument("--output", required=True)
    bind_audio_parser = subparsers.add_parser("bind-higgsfield-audio")
    bind_audio_parser.add_argument("--blocks", required=True)
    bind_audio_parser.add_argument("--audio", required=True)
    bind_audio_parser.add_argument("--job-dir", required=True)
    bind_audio_parser.add_argument("--output", required=True)
    bind_audio_parser.add_argument("--storyboard-hash", default="")
    media_parser = subparsers.add_parser("media-generate")
    media_parser.add_argument("--plan", required=True)
    media_parser.add_argument("--output-dir", required=True)
    media_parser.add_argument("--max-cost-usd", required=True, type=float)
    media_parser.add_argument("--max-calls", default=6, type=int)
    media_parser.add_argument(
        "--allow-paid",
        action="store_true",
        help="required acknowledgement for paid Magnific operations",
    )
    video_parser = subparsers.add_parser("magnific-video-generate")
    video_parser.add_argument("--plan", required=True)
    video_parser.add_argument("--output-dir", required=True)
    video_parser.add_argument("--max-cost-usd", required=True, type=float)
    video_parser.add_argument("--max-calls", default=1, type=int)
    video_parser.add_argument(
        "--allow-paid",
        action="store_true",
        help="required acknowledgement for a bounded Magnific video call",
    )
    image_parser = subparsers.add_parser("magnific-image-generate")
    image_parser.add_argument("--plan", required=True)
    image_parser.add_argument("--output-dir", required=True)
    image_parser.add_argument("--max-cost-usd", required=True, type=float)
    image_parser.add_argument("--max-calls", default=1, type=int)
    image_parser.add_argument(
        "--allow-paid",
        action="store_true",
        help="required acknowledgement for a bounded Magnific image call",
    )
    return parser


def _print_status_table(run: VideoRun, events: list[VideoStageEvent]) -> None:
    latest_by_stage: dict[str, VideoStageEvent] = {}
    for event in events:
        latest_by_stage[event.stage_name] = event

    rows: list[tuple[str, str, float, float]] = []
    for event in latest_by_stage.values():
        summary = event.output_summary
        rows.append(
            (
                event.stage_name,
                event.status,
                float(summary.get("cost_usd", 0.0) or 0.0),
                float(summary.get("wall_time_s", 0.0) or 0.0),
            )
        )
    stage_width = max([len("STAGE"), *(len(row[0]) for row in rows)])
    status_width = max([len("STATUS"), *(len(row[1]) for row in rows)])
    print(f"JOB     {run.id}")
    print(f"STATUS  {run.status}")
    print(
        f"{'STAGE':<{stage_width}}  {'STATUS':<{status_width}}  "
        f"{'COST_USD':>10}  {'WALL_TIME_S':>11}"
    )
    for stage, status, cost, wall_time in rows:
        print(
            f"{stage:<{stage_width}}  {status:<{status_width}}  "
            f"{cost:>10.4f}  {wall_time:>11.3f}"
        )
    print(
        f"{'TOTAL':<{stage_width}}  {'':<{status_width}}  "
        f"{sum(row[2] for row in rows):>10.4f}  "
        f"{sum(row[3] for row in rows):>11.3f}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    load_video_environment()
    args = build_parser().parse_args(argv)
    repository = _repository(args.artifact_root)
    pipeline = _pipeline(repository)

    if args.command == "run":
        targets = [target.strip() for target in args.targets.split(",") if target.strip()]
        run = pipeline.start(args.source, channel=args.channel, targets=targets)
        print(json.dumps(run.to_dict(), indent=2))
        return 0
    if args.command == "resume":
        print(json.dumps(pipeline.resume(args.job_id).to_dict(), indent=2))
        return 0
    if args.command == "approve":
        try:
            print(
                json.dumps(
                    pipeline.approve(
                        args.job_id,
                        args.gate,
                        rubric_path=args.rubric,
                    ).to_dict(),
                    indent=2,
                )
            )
        except VideoPipelineGateApprovalError as exc:
            print(json.dumps({"valid": False, "errors": exc.violations}, indent=2))
            return 1
        return 0
    if args.command == "status":
        if args.job_id:
            run = repository.load_run(args.job_id)
            if run is None:
                print(json.dumps({"error": "job not found", "job_id": args.job_id}))
                return 1
            payload = run.to_dict()
            payload["events"] = [
                event.to_dict() for event in repository.list_stage_events(run.id)
            ]
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                _print_status_table(
                    run,
                    repository.list_stage_events(run.id),
                )
        else:
            print(json.dumps([run.to_dict() for run in repository.list_runs()], indent=2))
        return 0

    if args.command == "compile-canonical-visual-coverage":
        from content.video_engine.src.services.editorial_motion import (
            EditorialMotionError,
            compile_canonical_visual_coverage,
        )

        try:
            compiled = compile_canonical_visual_coverage(
                audio_manifest=args.audio,
                word_timings=args.words,
                target_duration_s=args.target_duration,
                minimum_duration_s=args.minimum_duration,
                maximum_duration_s=args.maximum_duration,
            )
            output = Path(args.output)
            if output.exists():
                if _load_json(output) != compiled:
                    raise EditorialMotionError(
                        "canonical visual coverage is immutable and differs"
                    )
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(compiled, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        except (OSError, TypeError, ValueError, EditorialMotionError) as exc:
            print(
                json.dumps(
                    {"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))},
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "artifact_hash": compiled["artifact_hash"],
                    "slot_count": compiled["slot_count"],
                    "duration_s": compiled["duration_s"],
                    "render_ready": compiled["render_ready"],
                    "output": str(output),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "analyze-timestamped-semantic-coverage":
        from content.video_engine.src.services.editorial_motion import (
            EditorialMotionError,
            analyze_timestamped_semantic_coverage,
        )

        try:
            analyzed = analyze_timestamped_semantic_coverage(
                timestamped_plate_plan=args.plate_plan,
                word_timings=args.words,
            )
            output = Path(args.output)
            if output.exists():
                if _load_json(output) != analyzed:
                    raise EditorialMotionError(
                        "timestamped semantic coverage is immutable and differs"
                    )
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(analyzed, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        except (OSError, TypeError, ValueError, EditorialMotionError) as exc:
            print(
                json.dumps(
                    {"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))},
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "artifact_hash": analyzed["artifact_hash"],
                    "resolved_plate_count": analyzed["resolved_plate_count"],
                    "uncovered_slot_count": len(analyzed["uncovered_slots"]),
                    "render_ready": analyzed["render_ready"],
                    "output": str(output),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "compile-timestamped-editorial-motion":
        from content.video_engine.src.services.editorial_motion import (
            EditorialMotionError,
            compile_timestamped_editorial_motion_plan,
        )

        try:
            validated = compile_timestamped_editorial_motion_plan(
                timestamped_plate_plan=args.plate_plan,
                asset_map=_load_json(args.asset_map),
                audio_manifest=args.audio,
                word_timings=args.words,
                pacing_recipe=args.pacing_recipe,
            )
            output = Path(args.output)
            if output.exists():
                if _load_json(output) != validated:
                    raise EditorialMotionError(
                        "timestamped editorial motion plan is immutable and differs"
                    )
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(validated, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        except (OSError, TypeError, ValueError, EditorialMotionError) as exc:
            print(
                json.dumps(
                    {"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))},
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": validated["schema_version"],
                    "artifact_hash": validated["artifact_hash"],
                    "shot_count": len(validated["shots"]),
                    "duration_s": validated["duration_s"],
                    "asset_map_hash": validated["asset_map_hash"],
                    "output": str(output),
                },
                indent=2,
            )
        )
        return 0

    if args.command in {"compile-editorial-motion", "validate-editorial-motion"}:
        from content.video_engine.src.services.editorial_motion import (
            EditorialMotionError,
            compile_editorial_motion_plan,
            validate_editorial_motion_plan,
        )

        try:
            if args.command == "compile-editorial-motion":
                shot_payload = _load_json(args.shot_specs)
                raw_specs = shot_payload.get("shots")
                if not isinstance(raw_specs, list):
                    raise ValueError("shot specs file requires a shots array")
                validated = compile_editorial_motion_plan(
                    storyboard=args.storyboard,
                    beat_plan=args.beat_plan,
                    narration_plan=args.narration,
                    audio_manifest=args.audio,
                    word_timings=args.words,
                    pacing_recipe=args.pacing_recipe,
                    shot_specs=raw_specs,
                    scene_bundles=[_load_json(path) for path in args.scene_bundle],
                    scene_flow_graph=_load_json(args.scene_flow),
                    asset_map=_load_json(args.asset_map),
                    source_end_s=args.source_end,
                )
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(validated, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            else:
                known_assets = None
                if args.asset_map:
                    asset_payload = _load_json(args.asset_map)
                    raw_assets = asset_payload.get("assets")
                    if isinstance(raw_assets, dict):
                        known_assets = set(raw_assets)
                    elif isinstance(raw_assets, list):
                        known_assets = {
                            str(item.get("id") or item.get("asset_id") or "")
                            for item in raw_assets
                            if isinstance(item, dict)
                        }
                validated = validate_editorial_motion_plan(
                    args.file,
                    known_asset_ids=known_assets,
                )
        except (OSError, TypeError, ValueError, EditorialMotionError) as exc:
            print(
                json.dumps(
                    {"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))},
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": validated["schema_version"],
                    "artifact_hash": validated["artifact_hash"],
                    "shot_count": len(validated["shots"]),
                    "duration_s": validated["duration_s"],
                    "output": str(getattr(args, "output", "") or ""),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "sample-editorial-motion":
        from content.video_engine.src.services.editorial_motion import (
            EditorialMotionError,
            derive_editorial_motion_sample,
        )

        try:
            asset_payload = _load_json(args.asset_map)
            raw_assets = asset_payload.get("assets")
            if isinstance(raw_assets, dict):
                known_assets = set(raw_assets)
            elif isinstance(raw_assets, list):
                known_assets = {
                    str(item.get("id") or item.get("asset_id") or "")
                    for item in raw_assets
                    if isinstance(item, dict)
                }
            else:
                raise ValueError("editorial asset map requires assets")
            sample = derive_editorial_motion_sample(
                args.plan,
                end_s=args.end_s,
                known_asset_ids=known_assets,
            )
            output = Path(args.output)
            if output.exists():
                if _load_json(output) != sample:
                    raise EditorialMotionError("editorial motion sample is immutable and differs")
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(sample, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        except (OSError, TypeError, ValueError, EditorialMotionError) as exc:
            print(
                json.dumps(
                    {"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))},
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "artifact_hash": sample["artifact_hash"],
                    "shot_count": len(sample["shots"]),
                    "duration_s": sample["duration_s"],
                    "output": str(output),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "render-editorial-motion-revision":
        from content.video_engine.src.services.animatic import (
            AnimaticError,
            AnimaticService,
        )

        try:
            overlays = _load_json(args.overlay_map) if args.overlay_map else {}
            packet = AnimaticService().render_editorial_motion_revision(
                args.plan,
                asset_map=args.asset_map,
                pacing_recipe=args.pacing_recipe,
                audio_manifest=args.audio,
                asset_root=args.asset_root,
                job_dir=args.job_dir,
                output_dir=args.output_dir,
                editor_root=args.editor_root,
                overlay_map=overlays,
                browser_executable=args.browser_executable,
                width=args.width,
                height=args.height,
                fps=args.fps,
            )
        except (OSError, TypeError, ValueError, subprocess.SubprocessError, AnimaticError) as exc:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
            return 1
        print(json.dumps({"valid": True, **packet}, indent=2))
        return 0

    if args.command == "media-generate":
        from content.video_engine.src.services.media_enhancement import (
            MediaEnhancementError,
            MediaEnhancementService,
            MagnificSettings,
        )

        try:
            settings = MagnificSettings.from_environment(
                max_cost_usd=args.max_cost_usd,
                max_calls=args.max_calls,
                paid_calls_allowed=args.allow_paid,
            )
            manifest = MediaEnhancementService(settings).execute(
                args.plan,
                project_root=PROJECT_ROOT,
                output_dir=args.output_dir,
            )
        except (OSError, TypeError, ValueError, MediaEnhancementError) as exc:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
            return 1
        print(json.dumps(manifest, indent=2))
        return 0

    if args.command == "magnific-video-generate":
        from content.video_engine.src.services.magnific_video import (
            MagnificVideoError,
            MagnificVideoService,
            MagnificVideoSettings,
        )

        try:
            motion_plan: str | dict = args.plan
            raw_plan = _load_json(args.plan)
            if raw_plan.get("schema_version") == "plate_motion_plan.v1":
                from content.video_engine.src.services.plate_motion import (
                    to_magnific_video_plan,
                )

                motion_plan = to_magnific_video_plan(
                    raw_plan,
                    job_root=PROJECT_ROOT,
                )
            settings = MagnificVideoSettings.from_environment(
                max_cost_usd=args.max_cost_usd,
                max_calls=args.max_calls,
                paid_calls_allowed=args.allow_paid,
            )
            manifest = MagnificVideoService(settings).execute(
                motion_plan,
                project_root=PROJECT_ROOT,
                output_dir=args.output_dir,
            )
        except (OSError, TypeError, ValueError, MagnificVideoError) as exc:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
            return 1
        print(json.dumps(manifest, indent=2))
        return 0

    if args.command == "magnific-image-generate":
        from content.video_engine.src.services.magnific_image import (
            MagnificImageError,
            MagnificImageService,
            MagnificImageSettings,
        )

        try:
            settings = MagnificImageSettings.from_environment(
                max_cost_usd=args.max_cost_usd,
                max_calls=args.max_calls,
                paid_calls_allowed=args.allow_paid,
            )
            manifest = MagnificImageService(settings).execute(
                args.plan,
                project_root=PROJECT_ROOT,
                output_dir=args.output_dir,
            )
        except (OSError, TypeError, ValueError, MagnificImageError) as exc:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
            return 1
        print(json.dumps(manifest, indent=2))
        return 0

    if args.command in {"compile-history-narration", "validate-history-narration"}:
        from content.video_engine.src.services.history_narration import (
            HistoryNarrationError,
            compile_history_narration,
            validate_history_narration,
        )

        try:
            if args.command == "compile-history-narration":
                payload = compile_history_narration(
                    args.storyboard,
                    source=args.source,
                    output_path=args.output,
                )
            else:
                payload = validate_history_narration(
                    args.file,
                    expected_storyboard_hash=args.storyboard_hash or None,
                    expected_research_hash=args.research_hash or None,
                    min_words=args.min_words,
                )
        except (OSError, TypeError, ValueError, HistoryNarrationError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "narration_hash": payload.get("narration_hash"),
            "total_words": payload.get("total_words"),
            "total_chars": payload.get("total_chars"),
            "output": str(getattr(args, "output", "") or ""),
        }, indent=2))
        return 0

    if args.command in {"resolve-canonical-audio", "validate-canonical-audio"}:
        from content.video_engine.src.services.history_narration import (
            HistoryNarrationError,
            resolve_canonical_elevenlabs_audio,
            validate_canonical_audio,
        )

        try:
            if args.command == "resolve-canonical-audio":
                payload = resolve_canonical_elevenlabs_audio(
                    args.narration,
                    job_root=args.job_dir,
                    manifest_path=args.manifest,
                    storyboard_hash=args.storyboard_hash,
                    voice_id=args.voice_id,
                    allow_synthesis=args.allow_synthesis,
                    output_path=args.output,
                )
            else:
                payload = validate_canonical_audio(
                    args.file,
                    job_root=args.job_dir,
                    expected_narration_hash=args.narration_hash or None,
                    expected_storyboard_hash=args.storyboard_hash or None,
                    expected_voice_id=args.voice_id or None,
                )
        except (OSError, TypeError, ValueError, HistoryNarrationError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "status": payload.get("status"),
            "duration_s": payload.get("duration_s"),
            "block_count": len(payload.get("blocks", [])),
            "cost_usd": payload.get("cost_usd"),
            "output": str(getattr(args, "output", "") or ""),
        }, indent=2))
        return 0

    if args.command == "compile-higgsfield-audio-blocks":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            compile_audio_aligned_higgsfield_blocks,
        )

        try:
            payload = compile_audio_aligned_higgsfield_blocks(
                args.coverage,
                args.generated_batch,
                args.narration,
                args.audio,
                job_root=args.job_dir,
                character_pack=args.character_pack,
                art_bible_hash=args.art_bible_hash,
                storyboard_hash=args.storyboard_hash,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "block_count": payload.get("block_count"),
            "coverage_slot_count": payload.get("coverage_slot_count"),
            "timeline_duration_s": payload.get("timeline_duration_s"),
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.command == "bind-higgsfield-audio":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            bind_canonical_audio_to_higgsfield_blocks,
        )

        try:
            payload = bind_canonical_audio_to_higgsfield_blocks(
                args.blocks,
                args.audio,
                job_root=args.job_dir,
                storyboard_hash=args.storyboard_hash,
                output_path=args.output,
            )
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "status": payload.get("status"),
            "item_count": len(payload.get("items", [])),
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.command in {"compile-higgsfield-blocks", "validate-higgsfield-blocks"}:
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            compile_higgsfield_blocks,
            validate_higgsfield_blocks,
        )

        try:
            if args.command == "compile-higgsfield-blocks":
                payload = compile_higgsfield_blocks(
                    args.coverage,
                    args.generated_batch,
                    job_root=args.job_dir,
                    block_count=args.block_count,
                    character_pack=args.character_pack,
                    art_bible_hash=args.art_bible_hash,
                    storyboard_hash=args.storyboard_hash,
                )
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                payload = validate_higgsfield_blocks(
                    args.file,
                    job_root=args.job_dir,
                    expected_coverage_hash=args.coverage_hash or None,
                    expected_plate_batch_hash=args.plate_batch_hash or None,
                    expected_block_count=args.block_count,
                )
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "block_count": len(payload.get("blocks", [])),
            "coverage_slot_count": payload.get("coverage_slot_count"),
            "output": str(getattr(args, "output", "") or ""),
        }, indent=2))
        return 0

    if args.command in {"resolve-elevenlabs-audio", "validate-elevenlabs-audio"}:
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            resolve_elevenlabs_audio,
            validate_elevenlabs_block_audio_manifest,
        )

        try:
            if args.command == "resolve-elevenlabs-audio":
                payload = resolve_elevenlabs_audio(
                    args.blocks,
                    job_root=args.job_dir,
                    manifest_path=args.manifest,
                    storyboard_hash=args.storyboard_hash,
                    voice_id=args.voice_id,
                    allow_synthesis=args.allow_synthesis,
                    output_path=args.output,
                )
            else:
                payload = validate_elevenlabs_block_audio_manifest(
                    args.file,
                    job_root=args.job_dir,
                    block_plan=args.blocks,
                    expected_voice_id=args.voice_id or None,
                    expected_storyboard_hash=args.storyboard_hash or None,
                    check_files=True,
                )
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "status": payload.get("status"),
            "item_count": len(payload.get("items", [])),
            "output": str(getattr(args, "output", "") or ""),
        }, indent=2))
        return 0

    if args.command == "higgsfield-preflight":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            preflight_higgsfield_models,
        )

        try:
            payload = preflight_higgsfield_models(
                preferred_model=args.model,
                duration_s=args.duration,
                audio_reference_count=args.audio_references,
            )
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "compile-higgsfield-job":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            compile_higgsfield_job_manifest,
        )

        try:
            payload = compile_higgsfield_job_manifest(
                args.blocks,
                args.audio,
                job_root=args.job_dir,
                project_root=args.project_root,
                character_pack=args.character_pack,
                preferred_model=args.model,
                storyboard_hash=args.storyboard_hash,
                art_bible_hash=args.art_bible_hash,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "status": payload["status"],
            "model": payload["model"],
            "block_count": payload["block_count"],
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.command == "validate-higgsfield-job":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            validate_higgsfield_job_manifest,
        )

        try:
            payload = validate_higgsfield_job_manifest(
                args.file,
                job_root=args.job_dir,
                expected_block_plan_hash=args.blocks_hash or None,
                expected_audio_manifest_hash=args.audio_hash or None,
                expected_model=args.model or None,
            )
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "status": payload["status"],
            "model": payload["model"],
            "block_count": payload["block_count"],
        }, indent=2))
        return 0

    if args.command == "record-higgsfield-task":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            record_higgsfield_task,
        )

        try:
            payload = record_higgsfield_task(
                args.job,
                job_root=args.job_dir,
                block_id=args.block_id,
                task_id=args.task_id,
                status=args.status,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "block_id": args.block_id,
            "task_id": args.task_id,
            "status": args.status,
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.command == "record-higgsfield-output":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            record_higgsfield_output,
        )

        try:
            payload = record_higgsfield_output(
                args.job,
                job_root=args.job_dir,
                block_id=args.block_id,
                output_path=args.provider_output,
                status=args.status,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        item = next(item for item in payload["items"] if item.get("block_id") == args.block_id)
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "block_id": args.block_id,
            "status": item.get("status"),
            "provider_output_sha256": item.get("provider_output_sha256"),
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.command == "compile-higgsfield-assembly":
        from content.video_engine.src.services.higgsfield_explainer import (
            HiggsfieldExplainerError,
            compile_higgsfield_local_assembly,
        )

        try:
            payload = compile_higgsfield_local_assembly(
                args.job,
                args.audio,
                job_root=args.job_dir,
                output_path=args.output,
            )
        except (OSError, TypeError, ValueError, HiggsfieldExplainerError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "status": payload["status"],
            "clip_count": payload["clip_count"],
            "output": str(args.output),
        }, indent=2))
        return 0

    if args.command == "validate-generated-visuals":
        from content.video_engine.src.services.generated_visuals import (
            GeneratedVisualValidationError,
            validate_generated_visual_candidates,
        )

        try:
            validated = validate_generated_visual_candidates(
                args.file,
                job_root=args.job_dir,
                check_files=True,
            )
        except (OSError, TypeError, ValueError, GeneratedVisualValidationError) as exc:
            print(
                json.dumps(
                    {
                        "valid": False,
                        "errors": list(getattr(exc, "errors", [str(exc)])),
                    },
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": validated["schema_version"],
                    "artifact_hash": validated["artifact_hash"],
                    "candidate_count": len(validated["items"]),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "validate-generated-block-batch":
        from content.video_engine.src.services.generated_block_images import (
            GeneratedBlockImageError,
            validate_generated_block_batch,
        )

        try:
            validated = validate_generated_block_batch(
                args.file,
                job_root=args.job_dir,
                expected_plan=args.plan,
                check_files=True,
            )
        except (OSError, TypeError, ValueError, GeneratedBlockImageError) as exc:
            print(
                json.dumps(
                    {
                        "valid": False,
                        "errors": list(getattr(exc, "errors", [str(exc)])),
                    },
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": validated["schema_version"],
                    "artifact_hash": validated["artifact_hash"],
                    "block_count": len(validated["blocks"]),
                    "one_generated_plate_per_block": True,
                },
                indent=2,
            )
        )
        return 0

    if args.command == "compile-timestamped-plate-plan":
        from content.video_engine.src.services.generated_block_images import (
            GeneratedBlockImageError,
            compile_timestamped_plate_plan,
        )

        try:
            payload = compile_timestamped_plate_plan(
                args.coverage,
                prompt_spine=args.prompt_spine,
                art_bible_id=args.art_bible_id,
                art_bible_hash=args.art_bible_hash,
                style_atoms=list(args.style_atom) or None,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError, GeneratedBlockImageError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "plate_count": payload["plate_count"],
            "duration_s": payload["duration_s"],
            "output": str(output),
        }, indent=2))
        return 0

    if args.command == "validate-timestamped-plate-plan":
        from content.video_engine.src.services.generated_block_images import (
            GeneratedBlockImageError,
            validate_timestamped_plate_plan,
        )

        try:
            payload = validate_timestamped_plate_plan(
                args.file,
                expected_coverage=args.coverage,
                expected_prompt_spine=args.prompt_spine,
            )
        except (OSError, TypeError, ValueError, GeneratedBlockImageError) as exc:
            print(json.dumps({"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))}, indent=2))
            return 1
        print(json.dumps({
            "valid": True,
            "schema_version": payload["schema_version"],
            "artifact_hash": payload["artifact_hash"],
            "plate_count": payload["plate_count"],
            "one_primary_plate_per_timestamp_slot": True,
        }, indent=2))
        return 0

    if args.command == "promote-timestamped-plates":
        from content.video_engine.src.services.generated_block_images import (
            GeneratedBlockImageError,
            compile_timestamped_plate_asset_manifest,
        )

        try:
            payload = compile_timestamped_plate_asset_manifest(
                args.inventory,
                job_root=args.job_dir,
                project_root=PROJECT_ROOT,
                expected_plan=args.plan,
                manifest_id=args.manifest_id,
                project_id=args.project_id,
                episode_id=args.episode_id,
                approved_by=args.approved_by,
                approved_at=args.approved_at,
            )
            output = Path(args.output)
            if output.exists():
                existing = _load_json(output)
                if existing != payload:
                    raise GeneratedBlockImageError(
                        ["timestamped plate asset manifest is immutable and differs"]
                    )
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                temporary = output.with_name(f".{output.name}.tmp")
                temporary.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                temporary.replace(output)
        except (OSError, TypeError, ValueError, GeneratedBlockImageError) as exc:
            print(
                json.dumps(
                    {"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))},
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": payload["schema_version"],
                    "artifact_hash": payload["artifact_hash"],
                    "render_eligible_count": sum(
                        item.get("render_eligible") is True
                        for item in payload.get("assets", [])
                    ),
                    "quarantined_count": sum(
                        item.get("render_eligible") is not True
                        for item in payload.get("assets", [])
                    ),
                    "output": str(output),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "replace-timestamped-plate-candidate":
        from content.video_engine.src.services.generated_block_images import (
            GeneratedBlockImageError,
            replace_timestamped_plate_candidate,
        )

        try:
            payload = replace_timestamped_plate_candidate(
                args.inventory,
                job_root=args.job_dir,
                expected_plan=args.plan,
                order=args.order,
                replacement_path=args.replacement_path,
            )
            output = Path(args.output)
            if output.exists():
                existing = _load_json(output)
                if existing != payload:
                    raise GeneratedBlockImageError(
                        ["replacement candidate inventory is immutable and differs"]
                    )
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                temporary = output.with_name(f".{output.name}.tmp")
                temporary.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                temporary.replace(output)
        except (OSError, TypeError, ValueError, GeneratedBlockImageError) as exc:
            print(
                json.dumps(
                    {"valid": False, "errors": list(getattr(exc, "errors", [str(exc)]))},
                    indent=2,
                )
            )
            return 1
        replacement = next(
            item for item in payload["items"] if int(item["order"]) == args.order
        )
        print(
            json.dumps(
                {
                    "valid": True,
                    "artifact_hash": payload["artifact_hash"],
                    "order": args.order,
                    "coverage_slot_id": replacement["slot_id"],
                    "replacement_sha256": replacement["sha256"],
                    "candidate_count": payload["candidate_count"],
                    "review_only_archive_count": payload["review_only_archive_count"],
                    "output": str(output),
                },
                indent=2,
            )
        )
        return 0

    if args.command in {
        "validate-plate-motion-plan",
        "validate-plate-motion-manifest",
    }:
        from content.video_engine.src.services.plate_motion import (
            PlateMotionError,
            validate_plate_motion_manifest,
            validate_plate_motion_plan,
        )

        try:
            validated = (
                validate_plate_motion_plan(
                    args.file,
                    job_root=args.job_dir,
                    expected_batch_hash=args.batch_hash or None,
                )
                if args.command == "validate-plate-motion-plan"
                else validate_plate_motion_manifest(args.file, job_root=args.job_dir)
            )
        except (OSError, TypeError, ValueError, PlateMotionError) as exc:
            print(
                json.dumps(
                    {
                        "valid": False,
                        "errors": list(getattr(exc, "errors", [str(exc)])),
                    },
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": validated["schema_version"],
                    "artifact_hash": validated.get("artifact_hash", ""),
                    "item_count": len(validated["items"]),
                },
                indent=2,
            )
        )
        return 0

    if args.command in {"validate-study", "validate-art-bible"}:
        from content.video_engine.src.services.art_direction import ArtDirectionService

        errors = (
            ArtDirectionService().check_reference_study(args.file)
            if args.command == "validate-study"
            else validate_art_bible_contract(args.file)
        )
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print("OK")
        return 0

    if args.command == "validate-martial-lanes":
        from content.video_engine.src.services.martial_lane_profiles import (
            check_martial_lanes,
        )

        errors = check_martial_lanes(args.file, root=PROJECT_ROOT)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print("OK")
        return 0

    if args.command in {
        "validate-martial-style-profile",
        "validate-martial-style-registry",
    }:
        from content.video_engine.src.services.martial_style_profiles import (
            check_martial_style_profile,
            check_martial_style_registry,
        )

        errors = (
            check_martial_style_profile(args.file, root=PROJECT_ROOT)
            if args.command == "validate-martial-style-profile"
            else check_martial_style_registry(args.file, root=PROJECT_ROOT)
        )
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print("OK")
        return 0

    if args.command in {
        "validate-martial-channel-v2",
        "validate-martial-lane-v2",
        "validate-martial-style-selection",
    }:
        from content.video_engine.src.services.martial_matters_v2 import (
            check_martial_channel_v2,
            check_martial_lane_profile_v2,
            check_martial_style_selection,
        )

        checker = {
            "validate-martial-channel-v2": check_martial_channel_v2,
            "validate-martial-lane-v2": check_martial_lane_profile_v2,
            "validate-martial-style-selection": check_martial_style_selection,
        }[args.command]
        errors = checker(args.file, root=PROJECT_ROOT)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print("OK")
        return 0

    if args.command == "validate-content-node":
        from content.video_engine.src.services.content_node_contracts import (
            ContentNodeContractError,
            validate_content_node,
        )

        try:
            payload = validate_content_node(
                args.file, format_family=args.format_family, root=PROJECT_ROOT
            )
        except (OSError, TypeError, ValueError, ContentNodeContractError) as exc:
            errors = exc.errors if isinstance(exc, ContentNodeContractError) else [str(exc)]
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print(json.dumps({"valid": True, "id": payload["id"], "artifact_hash": payload["artifact_hash"]}, indent=2))
        return 0

    if args.command == "validate-martial-asset-catalog":
        from content.video_engine.src.services.martial_asset_catalog import (
            MartialAssetCatalogError,
            validate_martial_asset_catalog,
        )

        try:
            payload = validate_martial_asset_catalog(
                args.file, taxonomy=args.taxonomy, root=PROJECT_ROOT
            )
        except (OSError, TypeError, ValueError, MartialAssetCatalogError) as exc:
            errors = exc.errors if isinstance(exc, MartialAssetCatalogError) else [str(exc)]
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print(json.dumps({"valid": True, "id": payload["id"], "artifact_hash": payload["artifact_hash"]}, indent=2))
        return 0

    if args.command == "validate-martial-scene-blocks":
        from content.video_engine.src.services.martial_asset_catalog import (
            MartialAssetCatalogError,
            validate_martial_scene_block_catalog,
        )

        try:
            payload = validate_martial_scene_block_catalog(
                args.file,
                asset_catalog=args.catalog,
                taxonomy=args.taxonomy,
                root=PROJECT_ROOT,
            )
        except (OSError, TypeError, ValueError, MartialAssetCatalogError) as exc:
            errors = exc.errors if isinstance(exc, MartialAssetCatalogError) else [str(exc)]
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print(json.dumps({"valid": True, "id": payload["id"], "artifact_hash": payload["artifact_hash"]}, indent=2))
        return 0

    if args.command == "plan-content-node":
        from content.video_engine.src.services.content_node_contracts import (
            ContentNodeContractError,
            validate_content_node,
        )

        try:
            payload = validate_content_node(
                args.node, format_family=args.format_family, root=PROJECT_ROOT
            )
        except (OSError, TypeError, ValueError, ContentNodeContractError) as exc:
            errors = exc.errors if isinstance(exc, ContentNodeContractError) else [str(exc)]
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print(json.dumps({"valid": True, "plan": payload}, indent=2))
        return 0

    if args.command == "resolve-martial-asset-demand":
        from content.video_engine.src.services.martial_asset_reuse import resolve_asset_demand

        try:
            payload = resolve_asset_demand(
                _load_json(args.demand),
                asset_catalog=args.catalog,
                taxonomy=args.taxonomy,
                scene_blocks=args.scene_blocks,
                root=PROJECT_ROOT,
            )
        except (OSError, TypeError, ValueError) as exc:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
            return 1
        print(json.dumps({"valid": True, "resolution": payload}, indent=2))
        return 0

    if args.command == "schedule-martial-matters":
        from content.video_engine.src.services.work_order_dispatch import (
            plan_and_dispatch_dry_run,
        )

        if not args.dry_run:
            print(json.dumps({"valid": False, "errors": ["schedule-martial-matters requires --dry-run"]}, indent=2))
            return 1
        try:
            fixture = _load_json(args.fixture)
            payload = plan_and_dispatch_dry_run(
                fixture.get("opportunities") or [],
                scheduler_config=args.config,
                as_of=str(fixture.get("as_of") or ""),
                capacity=int(fixture.get("capacity") or 0),
                root=PROJECT_ROOT,
            )
        except (OSError, TypeError, ValueError) as exc:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
            return 1
        print(json.dumps({"valid": True, **payload}, indent=2))
        return 0

    if args.command in {"run-content-node", "resume-content-node", "content-node-status"}:
        from content.video_engine.src.repositories.content_node_file_repository import (
            FileBackedContentNodeRepository,
        )
        from content.video_engine.src.services.content_node_orchestration import (
            ContentNodeOrchestrator,
        )

        orchestrator = ContentNodeOrchestrator(
            FileBackedContentNodeRepository(args.content_node_root), repository
        )
        try:
            if args.command == "run-content-node":
                run = orchestrator.start(
                    args.node,
                    format_family=args.format_family,
                    style_selection=args.style_selection,
                    root=PROJECT_ROOT,
                )
                print(json.dumps(run.to_dict(), indent=2))
                return 0
            if args.command == "resume-content-node":
                run = orchestrator.resume(args.id)
                print(json.dumps(run.to_dict(), indent=2))
                return 0
            payload = orchestrator.status(args.id)
        except (OSError, TypeError, ValueError) as exc:
            print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
            return 1
        children = payload["children"]
        if args.require_children_gate_b and any(
            child.get("gate_b_status") != "approved" for child in children
        ):
            print(json.dumps({"valid": False, "errors": ["not every child has Gate B approval"], **payload}, indent=2))
            return 1
        if args.require_qc_pass and any(
            child.get("summary", {}).get("qc_passed") is not True for child in children
        ):
            print(json.dumps({"valid": False, "errors": ["not every child has passing QC"], **payload}, indent=2))
            return 1
        print(json.dumps({"valid": True, **payload}, indent=2))
        return 0

    if args.command in {
        "validate-history",
        "validate-research",
        "validate-assets",
    }:
        try:
            if args.command == "validate-assets":
                from content.video_engine.src.services.asset_resolver import (
                    validate_asset_manifest,
                )

                validated = validate_asset_manifest(
                    args.file,
                    project_root=PROJECT_ROOT,
                    check_files=True,
                )
            else:
                from content.video_engine.src.services.history_contracts import (
                    HistoryContractService,
                )

                service = HistoryContractService(root=PROJECT_ROOT)
                validated = (
                    service.validate_history_episode(args.file)
                    if args.command == "validate-history"
                    else service.validate_research_packet(args.file)
                )
        except (OSError, TypeError, ValueError) as exc:
            errors = list(getattr(exc, "errors", [str(exc)]))
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": validated.get("schema_version"),
                    "artifact_hash": validated.get("artifact_hash"),
                },
                indent=2,
            )
        )
        return 0

    if args.command in {
        "validate-stock-batch",
        "validate-asset-selection",
        "validate-flow-snapshot",
    }:
        from content.video_engine.src.services.stock_assets import (
            validate_asset_selection,
            validate_flow_snapshot,
            validate_stock_candidate_batch,
        )

        errors = (
            validate_stock_candidate_batch(args.file, job_dir=args.job_dir)
            if args.command == "validate-stock-batch"
            else validate_asset_selection(
                args.file,
                args.batch,
                expected_coverage_hash=args.coverage_hash,
            )
            if args.command == "validate-asset-selection"
            else validate_flow_snapshot(args.file)
        )
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print("OK")
        return 0

    if args.command == "validate-character-pack":
        from content.video_engine.src.services.flow_character_pack import (
            FlowCharacterPackError,
            validate_flow_character_pack,
        )

        try:
            validated = validate_flow_character_pack(args.file)
        except (OSError, TypeError, ValueError, FlowCharacterPackError) as exc:
            print(
                json.dumps(
                    {
                        "valid": False,
                        "errors": list(getattr(exc, "errors", [str(exc)])),
                    },
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": validated["schema_version"],
                    "artifact_hash": validated["artifact_hash"],
                    "character_count": len(validated["characters"]),
                    "render_eligible": validated["render_eligible"],
                },
                indent=2,
            )
        )
        return 0

    if args.command == "validate-producer-plan":
        from content.video_engine.src.services.producer_orchestration import (
            validate_producer_plan,
        )

        try:
            payload = _load_json(args.file)
            errors = validate_producer_plan(payload)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            errors = [str(exc)]
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": payload["schema_version"],
                    "artifact_hash": payload["artifact_hash"],
                    "block_count": len(payload["blocks"]),
                },
                indent=2,
            )
        )
        return 0

    if args.command in {
        "inventory-creative-assets",
        "validate-creative-inventory",
        "compile-communication-grammar",
        "validate-communication-grammar",
        "validate-style-packs",
        "validate-asset-map",
        "validate-foundation-review",
        "validate-world-packs",
        "validate-scene-bundle",
        "validate-scene-flow",
    }:
        from content.video_engine.src.services.living_scenes import (
            LivingSceneValidationError,
            build_creative_inventory,
            build_default_communication_grammar,
            validate_communication_grammar,
            validate_asset_foundation_review,
            validate_creative_asset_map,
            validate_creative_inventory,
            validate_scene_bundle,
            validate_scene_flow_graph,
            validate_style_pack_library,
            validate_world_pack_library,
        )

        try:
            if args.command == "inventory-creative-assets":
                roots: dict[str, str] = {}
                for value in args.root:
                    if "=" not in value:
                        raise ValueError("--root must use id=path")
                    root_id, root_path = value.split("=", 1)
                    root_id = root_id.strip()
                    root_path = root_path.strip()
                    if not root_id or not root_path:
                        raise ValueError("--root requires non-empty id and path")
                    if root_id in roots:
                        raise ValueError(f"duplicate root id {root_id!r}")
                    roots[root_id] = root_path
                payload = build_creative_inventory(
                    roots=roots,
                    project_root=args.project_root,
                    asset_manifests=args.asset_manifest,
                    default_classification=args.default_classification,
                    output_path=args.output,
                )
            elif args.command == "validate-creative-inventory":
                payload = validate_creative_inventory(
                    args.file,
                    check_files=not args.skip_files,
                )
            elif args.command == "compile-communication-grammar":
                payload = build_default_communication_grammar()
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
                )
            elif args.command == "validate-communication-grammar":
                payload = validate_communication_grammar(args.file)
            elif args.command == "validate-asset-map":
                payload = validate_creative_asset_map(
                    args.file,
                    expected_grammar_hash=args.grammar_hash,
                )
            elif args.command == "validate-foundation-review":
                payload = validate_asset_foundation_review(
                    args.file,
                    asset_map=args.asset_map,
                    world_packs=args.world_packs,
                    style_packs=args.style_packs,
                    calibration_inventory=args.calibration_inventory,
                    asset_manifest=args.asset_manifest,
                    project_root=args.project_root,
                    check_files=not args.skip_files,
                )
            elif args.command == "validate-style-packs":
                payload = validate_style_pack_library(
                    args.file,
                    calibration_inventory=args.calibration_inventory,
                    asset_map=args.asset_map,
                    check_files=not args.skip_files,
                )
            elif args.command == "validate-world-packs":
                payload = validate_world_pack_library(
                    args.file,
                    asset_map=args.asset_map,
                    style_pack_library=args.style_packs,
                    expected_grammar_hash=args.grammar_hash,
                )
            elif args.command == "validate-scene-bundle":
                payload = validate_scene_bundle(
                    args.file,
                    asset_map=args.asset_map,
                    style_pack_library=args.style_packs,
                )
            else:
                payload = validate_scene_flow_graph(
                    args.file,
                    asset_map=args.asset_map,
                    style_pack_library=args.style_packs,
                    expected_grammar_hash=args.grammar_hash,
                )
        except (OSError, TypeError, ValueError, LivingSceneValidationError) as exc:
            print(
                json.dumps(
                    {
                        "valid": False,
                        "errors": list(getattr(exc, "errors", [str(exc)])),
                    },
                    indent=2,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema_version": payload["schema_version"],
                    "artifact_hash": payload["artifact_hash"],
                    "item_count": len(payload.get("items") or []),
                    "surface_count": len(payload.get("surfaces") or []),
                    "asset_count": len(payload.get("assets") or []),
                    "candidate_count": len(payload.get("candidates") or []),
                    "world_pack_count": len(payload.get("packs") or [])
                    if payload.get("schema_version") == "world_pack_library.v1"
                    else 0,
                    "style_pack_count": len(payload.get("packs") or [])
                    if payload.get("schema_version") == "style_pack_library.v1"
                    else 0,
                    "scene_count": len(payload.get("scenes") or []),
                    "output": str(getattr(args, "output", "") or ""),
                },
                indent=2,
            )
        )
        return 0

    errors = validate_storyboard(args.storyboard)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
