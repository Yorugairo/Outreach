"""History V4 evidence stages and deterministic documentary compilation."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.services.history_contracts import (
    HistoryContractService,
    canonical_sha256,
)


_FUNCTION_ALIASES = {
    "document_closeup": "document_quote_closeup",
    "migration_map": "migration_map_timeline",
    "timeline": "migration_map_timeline",
    "concept_mechanics": "concept_mechanics_cutaway",
    "chapter_card": "chapter_cta",
}
_FUNCTION_ASSETS = {
    "artifact_cold_open": ["original-artifact-1882"],
    "archival_portrait": ["archive-jigoro-kano"],
    "illustrated_reconstruction": ["original-maeda-voyage"],
    "document_quote_closeup": ["original-document-question"],
    "lineage_graph": ["original-lineage-question"],
}


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain an object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _contained_ref(ref: Mapping[str, Any], project_root: Path, label: str) -> Path:
    raw = str(ref.get("path") or "").strip()
    if not raw:
        raise ValueError(f"{label}.path is required for a runnable History V4 episode")
    path = Path(raw)
    if not path.is_absolute():
        path = project_root / path
    try:
        path = path.resolve(strict=True)
        path.relative_to(project_root)
    except (OSError, ValueError) as exc:
        raise ValueError(f"{label}.path must resolve inside the project root") from exc
    if not path.is_file():
        raise ValueError(f"{label}.path must resolve to a file")
    return path


class HistoryEvidenceService:
    """Resolve and validate research/asset references before any creative stage."""

    def validate_research_stage(
        self,
        job: VideoRun,
        ctx: StageContext,
    ) -> StageOutput:
        project_root = Path(ctx.configs.get("project_root", Path.cwd())).resolve()
        episode_path = ctx.job_dir / "history_episode.json"
        episode = HistoryContractService(root=project_root).validate_history_episode(
            _read_object(episode_path, "history episode")
        )

        research_ref = episode["research_packet"]
        research_source = _contained_ref(research_ref, project_root, "research_packet")
        research = HistoryContractService(root=project_root).validate_research_packet(
            research_source
        )
        research_hash = str(research["artifact_hash"])
        if research_ref.get("id") != research.get("id"):
            raise ValueError("history episode research_packet.id does not match the packet")
        if research_ref.get("hash") != research_hash:
            raise ValueError(
                "history episode research_packet.hash is stale; "
                f"expected {research_hash}"
            )

        asset_ref = episode["asset_manifest"]
        asset_source = _contained_ref(asset_ref, project_root, "asset_manifest")
        asset_manifest = _read_object(asset_source, "asset manifest")
        from content.video_engine.src.services.asset_resolver import (
            AssetResolverService,
        )

        normalized_assets = AssetResolverService(
            project_root=project_root,
            job_dir=ctx.job_dir,
        ).validate(asset_manifest, check_files=True)
        asset_hash = str(normalized_assets["artifact_hash"])
        manifest_id = str(
            normalized_assets.get("manifest_id")
            or normalized_assets.get("id")
            or ""
        )
        if asset_ref.get("id") != manifest_id:
            raise ValueError("history episode asset_manifest.id does not match the manifest")
        if asset_ref.get("hash") != asset_hash:
            raise ValueError(
                "history episode asset_manifest.hash is stale; "
                f"expected {asset_hash}"
            )

        _write_json(ctx.job_dir / "research_packet.json", research)
        _write_json(ctx.job_dir / "asset_manifest.json", asset_manifest)
        _write_json(ctx.job_dir / "history_episode.json", episode)
        return StageOutput(
            {
                "episode_hash": episode["artifact_hash"],
                "research_hash": research_hash,
                "asset_manifest_hash": asset_hash,
                "claim_count": len(research["claims"]),
                "source_count": len(research["sources"]),
                "contested_claim_count": sum(
                    1
                    for claim in research["claims"]
                    if claim.get("contested") is True
                    or claim.get("status") == "contested"
                ),
                "cost_usd": 0.0,
            }
        )

    def prepare_review_stage(
        self,
        job: VideoRun,
        ctx: StageContext,
    ) -> StageOutput:
        del job
        episode = _read_object(ctx.job_dir / "history_episode.json", "history episode")
        research = _read_object(ctx.job_dir / "research_packet.json", "research packet")
        selected_assets = (
            ctx.job_dir
            / "asset_selection"
            / "resolved"
            / "resolved_assets.json"
        )
        assets = _read_object(
            selected_assets
            if selected_assets.is_file()
            else ctx.job_dir / "resolved_assets.json",
            "resolved assets",
        )
        research_hash = str(research["artifact_hash"])
        packet = {
            "schema_version": "research_review_packet.v1",
            "episode_id": episode["id"],
            "title": episode["title"],
            "thesis": episode["thesis"],
            "target_duration_s": episode["target_duration_s"],
            "research_hash": research_hash,
            "asset_manifest_hash": assets["manifest_hash"],
            "source_count": len(research["sources"]),
            "claim_count": len(research["claims"]),
            "contested_claim_ids": [
                claim["id"]
                for claim in research["claims"]
                if claim.get("contested") is True
                or claim.get("status") == "contested"
            ],
            "render_eligible_asset_ids": list(assets.get("asset_ids") or []),
            "quarantined_assets": copy.deepcopy(
                assets.get("quarantined_assets") or []
            ),
            "research_packet_path": "research_packet.json",
            "rights_packet_path": "credits.json",
            "approval_granted": False,
        }
        rubric_template = {
            "schema_version": "research_gate_rubric.v1",
            "research_hash": research_hash,
            "scores": {
                "thesis_clarity": 0,
                "source_quality": 0,
                "contested_framing": 0,
                "claim_completeness": 0,
                "promotional_neutrality": 0,
                "rights_readiness": 0,
            },
            "notes": "Operator fills this file outside the immutable job evidence.",
        }
        packet["artifact_hash"] = canonical_sha256(packet)
        _write_json(ctx.job_dir / "research" / "review-packet.json", packet)
        _write_json(
            ctx.job_dir / "research" / "review-rubric.template.json",
            rubric_template,
        )
        return StageOutput(
            {
                "artifact_path": "research/review-packet.json",
                "rubric_template_path": "research/review-rubric.template.json",
                "research_hash": research_hash,
                "approval_granted": False,
                "cost_usd": 0.0,
            }
        )


class HistoryArtDirectionService:
    """Validate art_bible.v2 and persist the job-local immutable direction."""

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        engine_root = Path(
            ctx.configs.get(
                "video_engine_root",
                Path(__file__).resolve().parents[2],
            )
        ).resolve()
        bible_id = str(
            job.config_snapshot.get("art_bible_id")
            or "combat-history-longform-cutout-fork-v1"
        )
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", bible_id):
            raise ValueError("History V4 art_bible_id must be a kebab-case identifier")
        bible_path = engine_root / "configs" / "art_bibles" / f"{bible_id}.json"
        schema_path = engine_root / "configs" / "art_bible_v2.schema.json"
        bible = _read_object(bible_path, "History V4 art bible")
        schema = _read_object(schema_path, "art_bible.v2 schema")
        errors = sorted(
            Draft7Validator(schema).iter_errors(bible),
            key=lambda error: [str(value) for value in error.absolute_path],
        )
        if errors:
            raise ValueError(
                "History V4 art bible failed validation: "
                + "; ".join(error.message for error in errors)
            )
        profile_derivation = bible.get("profile_derivation")
        profile_binding: dict[str, Any] | None = None
        if isinstance(profile_derivation, Mapping):
            profile_id = str(profile_derivation.get("base_profile_id") or "")
            profile_path = (
                engine_root
                / "configs"
                / "production_profiles"
                / f"{profile_id}.json"
            )
            profile_schema_path = (
                engine_root / "configs" / "production_profile.schema.json"
            )
            profile = _read_object(profile_path, "production profile")
            profile_schema = _read_object(
                profile_schema_path,
                "production_profile.v1 schema",
            )
            profile_errors = sorted(
                Draft7Validator(profile_schema).iter_errors(profile),
                key=lambda error: [
                    str(value) for value in error.absolute_path
                ],
            )
            if profile_errors:
                raise ValueError(
                    "History V4 production profile failed validation: "
                    + "; ".join(error.message for error in profile_errors)
                )
            profile_hash = canonical_sha256(profile)
            if profile.get("artifact_hash") != profile_hash:
                raise ValueError(
                    "History V4 production profile artifact_hash is stale"
                )
            if profile_derivation.get("base_profile_hash") != profile_hash:
                raise ValueError(
                    "History V4 art bible base_profile_hash does not match "
                    "the production profile"
                )
            if (
                (profile.get("render_policy") or {}).get("render_eligible")
                is not False
            ):
                raise ValueError(
                    "History V4 production profiles must remain research-only"
                )
            profile_binding = {
                "id": profile_id,
                "hash": profile_hash,
                "contract": "production_profile_fork.v1",
                "carry_forward": copy.deepcopy(
                    profile_derivation.get("carry_forward") or []
                ),
            }
        serialized = json.dumps(bible, ensure_ascii=False).casefold()
        for prohibited in (
            "in the style of",
            "youtube reference pack",
            "consultant outline",
            "creator_name",
            "source_frame",
        ):
            if prohibited in serialized:
                raise ValueError(
                    f"History V4 art bible contains prohibited renderer input {prohibited!r}"
                )
        bible["artifact_hash"] = canonical_sha256(bible)
        direction = {
            "schema_version": "art_direction.v2",
            "art_bible_id": bible["id"],
            "art_bible_hash": bible["artifact_hash"],
            "art_bible": copy.deepcopy(bible),
            "style_atoms": copy.deepcopy(bible["style_atoms"]),
            "palette": copy.deepcopy(bible["palette"]),
            "typography": copy.deepcopy(bible["typography"]),
            "composition": copy.deepcopy(bible["composition"]),
            "motion": copy.deepcopy(bible["motion"]),
            "render_policy": copy.deepcopy(bible["render_policy"]),
        }
        if profile_binding is not None:
            direction["production_profile"] = profile_binding
        direction["artifact_hash"] = canonical_sha256(direction)
        _write_json(ctx.job_dir / "art_bible.json", bible)
        _write_json(ctx.job_dir / "art_direction.json", direction)
        return StageOutput(
            {
                "artifact_path": "art_direction.json",
                "art_bible_path": "art_bible.json",
                "schema_version": "art_direction.v2",
                "art_bible_id": bible["id"],
                "art_bible_hash": bible["artifact_hash"],
                "style_atom_count": len(bible["style_atoms"]),
                "base_profile_id": (
                    profile_binding["id"]
                    if profile_binding is not None
                    else None
                ),
                "base_profile_hash": (
                    profile_binding["hash"]
                    if profile_binding is not None
                    else None
                ),
                "cost_usd": 0.0,
            }
        )


class DocumentaryScriptService:
    """Compile approved claim wording into documentary beats without an LLM."""

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        episode = _read_object(ctx.job_dir / "history_episode.json", "history episode")
        research = _read_object(ctx.job_dir / "research_packet.json", "research packet")
        claims = {str(claim["id"]): claim for claim in research["claims"]}
        citations = {
            str(citation["id"]): citation for citation in research["citations"]
        }
        beats: list[dict[str, Any]] = []
        for chapter_index, chapter in enumerate(episode["chapters"]):
            modes = list(chapter.get("visual_modes") or ["chapter_card"])
            claim_ids = list(
                chapter.get("claim_ids") or chapter.get("research_claim_ids") or []
            )
            if not claim_ids:
                raise ValueError(f"chapter {chapter['id']!r} has no approved claim IDs")
            per_claim_duration = float(chapter["target_duration_s"]) / len(claim_ids)
            for claim_index, claim_id in enumerate(claim_ids):
                claim = claims.get(str(claim_id))
                if claim is None:
                    raise ValueError(
                        f"chapter {chapter['id']!r} references unknown claim {claim_id!r}"
                    )
                narration = str(
                    claim.get("qualified_narration")
                    or claim.get("narration")
                    or claim["text"]
                ).strip()
                if not narration:
                    raise ValueError(f"claim {claim_id!r} has no approved narration")
                mode = str(modes[claim_index % len(modes)])
                function = _FUNCTION_ALIASES.get(mode, mode)
                if function == "archival_portrait" and chapter_index > 0:
                    asset_ids = ["archive-mitsuyo-maeda"]
                else:
                    asset_ids = list(_FUNCTION_ASSETS.get(function, []))
                citation_ids = [str(value) for value in claim["citation_ids"]]
                if any(citation_id not in citations for citation_id in citation_ids):
                    raise ValueError(f"claim {claim_id!r} has an unresolved citation")
                beats.append(
                    {
                        "beat_id": f"{chapter['id']}-{claim_index + 1:02d}",
                        "chapter_id": chapter["id"],
                        "act": (
                            "hook"
                            if not beats
                            else "conflict"
                            if claim.get("contested") is True
                            else "develop"
                        ),
                        "narration_text": narration,
                        "claim_refs": [str(claim_id)],
                        "citations": citation_ids,
                        "visual_type": function,
                        "visual_function": function,
                        "manim_class": "DocumentaryScene",
                        "asset_ids": asset_ids,
                        "timing": {"target_s": round(per_claim_duration, 3)},
                        "parameters": {
                            "documentary_function": function,
                            "chapter_title": chapter["title"],
                        },
                    }
                )
        if not beats:
            raise ValueError("history episode produced no documentary beats")
        beats[-1]["act"] = "payoff"
        cta = episode["cta"]
        cta_text = str(cta.get("text") if isinstance(cta, Mapping) else cta)
        beats.append(
            {
                "beat_id": "series-cta",
                "chapter_id": episode["chapters"][-1]["id"],
                "act": "cta",
                "narration_text": cta_text,
                "claim_refs": [],
                "citations": [],
                "visual_type": "chapter_cta",
                "visual_function": "chapter_cta",
                "manim_class": "DocumentaryScene",
                "asset_ids": [],
                "timing": {"target_s": 8.0},
                "parameters": {
                    "documentary_function": "chapter_cta",
                    "chapter_title": "Continue the history",
                },
            }
        )
        payload = {
            "schema_version": "documentary_beat_sheet.v1",
            "source_slug": episode["id"],
            "episode_id": episode["id"],
            "research_hash": research["artifact_hash"],
            "claims": copy.deepcopy(research["claims"]),
            "beats": beats,
        }
        payload["artifact_hash"] = canonical_sha256(payload)
        _write_json(ctx.job_dir / "beat_sheet.json", payload)
        return StageOutput(
            {
                "artifact_path": "beat_sheet.json",
                "beat_count": len(beats),
                "mode": "deterministic_approved_research",
                "research_hash": research["artifact_hash"],
                "cost_usd": 0.0,
            }
        )


class DocumentaryShotPlanService:
    """Convert documentary beats into renderer-safe shot_plan.v3."""

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        del job
        episode = _read_object(ctx.job_dir / "history_episode.json", "history episode")
        research = _read_object(ctx.job_dir / "research_packet.json", "research packet")
        assets = _read_object(ctx.job_dir / "resolved_assets.json", "resolved assets")
        art_direction = _read_object(ctx.job_dir / "art_direction.json", "art direction")
        beat_sheet = _read_object(ctx.job_dir / "beat_sheet.json", "beat sheet")
        allowed_assets = set(str(value) for value in assets.get("asset_ids") or [])
        shots: list[dict[str, Any]] = []
        previous_signature = ""
        for index, beat in enumerate(beat_sheet["beats"], start=1):
            function = str(beat["visual_function"])
            asset_ids = [str(value) for value in beat.get("asset_ids") or []]
            unknown = sorted(set(asset_ids) - allowed_assets)
            if unknown:
                raise ValueError(
                    f"documentary beat {beat['beat_id']!r} references unknown assets: "
                    + ", ".join(unknown)
                )
            signature = f"{function}:{','.join(asset_ids) or 'generated'}:{index % 3}"
            if signature == previous_signature:
                raise ValueError("adjacent documentary treatments repeat a signature")
            previous_signature = signature
            shots.append(
                {
                    "shot_id": f"history-{index:03d}",
                    "treatment_id": f"treatment-history-{index:03d}",
                    "chapter_id": beat["chapter_id"],
                    "act": beat["act"],
                    "narration_text": beat["narration_text"],
                    "claim_refs": list(beat["claim_refs"]),
                    "citations": list(beat["citations"]),
                    "function": function,
                    "visual_function": function,
                    "visual_type": function,
                    "scene_class": "DocumentaryScene",
                    "manim_class": "DocumentaryScene",
                    "asset_ids": asset_ids,
                    "duration_s": float(beat["timing"]["target_s"]),
                    "timing": copy.deepcopy(beat["timing"]),
                    "parameters": copy.deepcopy(beat["parameters"]),
                    "camera": {
                        "move": ["push_in", "lateral_drift", "hold"][index % 3],
                        "depth": ["foreground", "midground", "background"],
                    },
                    "typography": {
                        "caption_role": "narration",
                        "citation_role": "source_marker",
                    },
                    "transition": {
                        "in": "continuous" if index > 1 else "hard_cut",
                        "motif": "mat-line-to-document-axis",
                    },
                    "uniqueness_signature": signature,
                }
            )
        plan = {
            "schema_version": "shot_plan.v3",
            "source_kind": "documentary",
            "episode_id": episode["id"],
            "research_hash": research["artifact_hash"],
            "asset_manifest_hash": assets["manifest_hash"],
            "art_bible_id": art_direction["art_bible_id"],
            "art_bible_hash": art_direction["art_bible_hash"],
            "shots": shots,
        }
        plan["artifact_hash"] = canonical_sha256(plan)
        _write_json(ctx.job_dir / "shot_plan.json", plan)
        return StageOutput(
            {
                "artifact_path": "shot_plan.json",
                "shot_count": len(shots),
                "research_hash": research["artifact_hash"],
                "asset_manifest_hash": assets["manifest_hash"],
                "shot_plan_hash": plan["artifact_hash"],
                "cost_usd": 0.0,
            }
        )


class DocumentaryStoryboardService:
    """Build immutable Storyboard 2.2 from approved documentary treatments."""

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        bundle = _read_object(ctx.job_dir / "source_bundle.json", "source bundle")
        episode = _read_object(ctx.job_dir / "history_episode.json", "history episode")
        research = _read_object(ctx.job_dir / "research_packet.json", "research packet")
        assets = _read_object(ctx.job_dir / "resolved_assets.json", "resolved assets")
        plan = _read_object(ctx.job_dir / "shot_plan.json", "shot plan")
        treatment = _read_object(
            ctx.job_dir / "visual_treatment.v2.json",
            "visual treatment",
        )
        plan_by_id = {
            str(shot["shot_id"]): shot for shot in plan.get("shots") or []
        }
        scenes: list[dict[str, Any]] = []
        for index, treated in enumerate(treatment["shots"], start=1):
            shot_id = str(treated["shot_id"])
            shot = plan_by_id.get(shot_id)
            if shot is None:
                raise ValueError(f"treatment references unknown shot {shot_id!r}")
            function = str(treated["function"])
            parameters = copy.deepcopy(treated.get("parameters") or {})
            parameters.update(
                {
                    "documentary_function": function,
                    "style_atom_ids": list(treated.get("style_atom_ids") or []),
                    "palette_roles": list(treated.get("palette_roles") or []),
                    "camera": copy.deepcopy(treated.get("camera") or shot.get("camera") or {}),
                    "credit_ids": list(treated.get("credit_ids") or []),
                }
            )
            scene: dict[str, Any] = {
                "scene_id": index,
                "act": shot["act"],
                "chapter_id": shot["chapter_id"],
                "narration_text": shot["narration_text"],
                "visual_type": function,
                "visual_function": function,
                "manim_class": "DocumentaryScene",
                "visual_treatment_id": treated["treatment_id"],
                "parameters": parameters,
                "timing": {
                    "target_s": float(shot["duration_s"]),
                    "padding_s": 0.3,
                },
                "claim_refs": list(shot.get("claim_refs") or []),
                "citation_refs": [
                    str(
                        citation.get("citation_id")
                        if isinstance(citation, Mapping)
                        else citation
                    )
                    for citation in treated.get("citations") or []
                ],
                "asset_ids": list(treated.get("asset_ids") or []),
                "transition": copy.deepcopy(
                    shot.get("transition")
                    or {"in": "continuous", "motif": "document-axis"}
                ),
            }
            if function == "illustrated_reconstruction":
                scene["illustration_label"] = str(
                    treated.get("illustration_label")
                    or "ILLUSTRATION / RECONSTRUCTION"
                )
            scenes.append(scene)

        scene_by_chapter: dict[str, list[dict[str, Any]]] = {}
        for scene in scenes:
            scene_by_chapter.setdefault(str(scene["chapter_id"]), []).append(scene)
        chapters = episode["chapters"]
        if len(chapters) < 2:
            raise ValueError("History V4 requires at least two chapters for native clips")
        first_cluster = scene_by_chapter[str(chapters[0]["id"])][:3]
        second_cluster = scene_by_chapter[str(chapters[1]["id"])][:3]

        def derivative(
            identifier: str,
            cluster: list[dict[str, Any]],
            title: str,
            layout: str,
        ) -> dict[str, Any]:
            if not cluster:
                raise ValueError(f"derivative {identifier!r} has no source scenes")
            return {
                "id": identifier,
                "scene_ids": [int(scene["scene_id"]) for scene in cluster],
                "claim_ids": sorted(
                    {
                        str(claim_id)
                        for scene in cluster
                        for claim_id in scene["claim_refs"]
                    }
                ),
                "title": title,
                "hook_line": str(cluster[0]["narration_text"]),
                "native_layout": layout,
            }

        claims = []
        for claim in research["claims"]:
            normalized = {
                "id": claim["id"],
                "text": claim["text"],
                "citation_ids": list(claim["citation_ids"]),
                "status": claim["status"],
                "verified": True,
            }
            if claim.get("contested") is True:
                normalized["contested"] = True
                normalized["qualified_narration"] = str(
                    claim.get("qualified_narration") or ""
                )
            claims.append(normalized)

        voice = copy.deepcopy(
            (
                (ctx.configs.get("channel_configs") or {})
                .get(str(job.input_payload.get("channel") or "combat-science"), {})
                .get("voice")
            )
            or {
                "provider": "human_recorded",
                "voice_id": "",
                "is_custom_voice": True,
            }
        )
        voice["is_custom_voice"] = True
        storyboard = {
            "schema_version": "2.2.0",
            "job_id": job.id,
            "source": {
                "slug": episode["id"],
                "kind": "history_episode",
                "ref": bundle["ref"],
                "content_hash": bundle["content_hash"],
            },
            "channel": {
                "id": str(job.input_payload.get("channel") or "combat-science"),
                "series": "history-of-bjj",
            },
            "research_hash": research["artifact_hash"],
            "asset_manifest_hash": assets["manifest_hash"],
            "art_direction": {
                "id": treatment["art_bible_id"],
                "hash": treatment["art_bible_hash"],
                "treatment_contract_version": "visual_treatment.v2",
                "treatment_hash": treatment["artifact_hash"],
            },
            "global_settings": {
                "voice": voice,
                "targets": ["landscape", "vertical", "chapter_subvideo"],
                "target_duration_s": episode["target_duration_s"],
                "concept_mechanics_runtime_cap": 0.15,
            },
            "claims": claims,
            "scenes": scenes,
            "derivatives": {
                "vertical_clips": [
                    derivative(
                        "short-kano-built-a-system",
                        first_cluster,
                        "Judo Was Already a Reinvention",
                        "9:16",
                    ),
                    derivative(
                        "short-the-origin-story-is-a-network",
                        second_cluster,
                        "BJJ Did Not Begin With One Clean Handoff",
                        "9:16",
                    ),
                ],
                "chapter_subvideos": [
                    derivative(
                        f"subvideo-{chapter['id']}",
                        scene_by_chapter[str(chapter["id"])],
                        chapter["title"],
                        "16:9",
                    )
                    for chapter in chapters
                ],
            },
            "packaging": {
                "titles": [
                    "How Judo Became Brazilian Jiu-Jitsu",
                    "The BJJ Origin Story Is More Complicated Than You Think",
                    "From Kodokan to Brazil: What the Evidence Actually Says",
                ],
                "description_md": (
                    "A source-led account of how Kodokan judo, international "
                    "teaching networks, and Brazilian institutions shaped BJJ. "
                    "Full citations and asset credits ship with the episode."
                ),
                "cta": {
                    "line": episode["cta"]["text"],
                    "url": episode["cta"].get(
                        "destination",
                        "https://nationalbjjregistry.com",
                    ),
                },
                "credits_path": "credits.json",
                "synthetic_content_disclosure": {
                    "required": False,
                    "reason": (
                        "Archival photographs and visibly non-photorealistic "
                        "labeled illustration; no realistic synthetic recreation."
                    ),
                },
            },
        }
        schema_path = (
            Path(ctx.configs.get("video_engine_root", Path.cwd()))
            / "configs"
            / "storyboard_v2_2.schema.json"
        )
        schema = _read_object(schema_path, "Storyboard 2.2 schema")
        errors = sorted(
            Draft7Validator(schema).iter_errors(storyboard),
            key=lambda error: [str(value) for value in error.absolute_path],
        )
        if errors:
            raise ValueError(
                "built Storyboard 2.2 failed schema validation: "
                + "; ".join(error.message for error in errors)
            )
        _write_json(ctx.job_dir / "storyboard.json", storyboard)
        storyboard_hash = canonical_sha256(storyboard)
        return StageOutput(
            {
                "artifact_path": "storyboard.json",
                "schema_version": "2.2.0",
                "storyboard_hash": storyboard_hash,
                "scene_count": len(scenes),
                "vertical_clip_count": 2,
                "chapter_subvideo_count": len(chapters),
                "research_hash": research["artifact_hash"],
                "asset_manifest_hash": assets["manifest_hash"],
                "cost_usd": 0.0,
            }
        )


__all__ = [
    "HistoryEvidenceService",
    "HistoryArtDirectionService",
    "DocumentaryScriptService",
    "DocumentaryShotPlanService",
    "DocumentaryStoryboardService",
]
