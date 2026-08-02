from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


def _target_duration(text: str, wpm: int) -> float:
    words = max(1, len(text.split()))
    return round(max(1.5, words / (wpm / 60.0)), 3)


def _bjj_phases(shot: dict[str, Any]) -> list[dict[str, Any]]:
    state_from = str(shot.get("state_from") or "")
    state_to = str(shot.get("state_to") or "")
    action = str(shot.get("action") or "")
    motion = dict(shot.get("motion") or {})
    path = str(motion.get("path") or "linear")
    contact_value = shot.get("contact")
    if isinstance(contact_value, str):
        contacts = [contact_value]
    elif isinstance(contact_value, list):
        contacts = [str(value) for value in contact_value]
    else:
        contacts = []
    overlays = [str(value) for value in shot.get("overlays") or []]
    cues = [str(value) for value in shot.get("sound_cues") or []]
    return [
        {
            "phase": "anticipation",
            "state_from": state_from,
            "action": f"anticipate_{action}",
            "state_to": state_from,
            "motion_path": "linear",
            "duration_s": 0.18,
            "contact_anchors": [],
            "overlays": [],
            "sound_cues": cues[:1],
        },
        {
            "phase": "action",
            "state_from": state_from,
            "action": action,
            "state_to": state_to,
            "motion_path": path,
            "duration_s": 0.42,
            "contact_anchors": contacts,
            "overlays": overlays,
            "sound_cues": cues[:1],
        },
        {
            "phase": "contact",
            "state_from": state_to,
            "action": f"confirm_{action}",
            "state_to": state_to,
            "motion_path": "compression",
            "duration_s": 0.20,
            "contact_anchors": contacts,
            "overlays": overlays,
            "sound_cues": cues[1:2],
        },
        {
            "phase": "recovery",
            "state_from": state_to,
            "action": f"hold_{action}",
            "state_to": state_to,
            "motion_path": "release",
            "duration_s": 0.20,
            "contact_anchors": contacts,
            "overlays": overlays,
            "sound_cues": cues[2:3],
        },
    ]


class StoryboardBuildService:
    def build(
        self,
        job: VideoRun,
        bundle: dict[str, Any],
        beat_sheet: dict[str, Any],
        channel_config: dict[str, Any],
        shot_plan: dict[str, Any] | None = None,
        visual_treatment: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        wpm = int(channel_config.get("pacing", {}).get("wpm_target", 140))
        scenes = []
        source_beats = list((shot_plan or {}).get("shots") or beat_sheet["beats"])
        treatments_by_id = {
            str(item.get("treatment_id") or item.get("id")): dict(item)
            for item in (visual_treatment or {}).get("shots", [])
            if isinstance(item, dict) and (item.get("treatment_id") or item.get("id"))
        }
        for scene_id, beat in enumerate(source_beats, start=1):
            narration = str(beat["narration_text"])
            is_shot = "shot_id" in beat
            parameters = dict(beat.get("parameters") or {})
            if is_shot:
                treatment_id = str(beat.get("treatment_id") or "")
                parameters.update(
                    {
                        "shot_id": beat["shot_id"],
                        "function": beat.get("function"),
                        "cast": dict(beat.get("cast") or {}),
                        "state_from": beat.get("state_from"),
                        "action": beat.get("action"),
                        "state_to": beat.get("state_to"),
                        "contact": beat.get("contact"),
                        "camera": dict(beat.get("camera") or {}),
                        "motion": dict(beat.get("motion") or {}),
                        "overlays": list(beat.get("overlays") or []),
                        "sound_cues": list(beat.get("sound_cues") or []),
                        "reference_refs": list(beat.get("reference_refs") or []),
                        "action_source": beat.get("action_source"),
                        "treatment_id": treatment_id or None,
                    }
                )
                treatment = treatments_by_id.get(treatment_id)
                if treatment is not None:
                    parameters["visual_treatment"] = treatment
                if beat.get("manim_class") in {
                    "BJJActionScene",
                    "CombatScienceScene",
                }:
                    parameters["phases"] = _bjj_phases(beat)
            scene: dict[str, Any] = {
                "scene_id": scene_id,
                "act": beat["act"],
                "narration_text": narration,
                "visual_type": beat["visual_type"],
                "manim_class": beat["manim_class"],
                "parameters": parameters,
                "timing": {
                    "target_s": _target_duration(narration, wpm),
                    "min_s": 1.5,
                    "max_s": 45,
                    "padding_s": 0.3,
                },
                "claim_refs": list(beat.get("claim_refs") or []),
                "transition": dict(
                    beat.get("transition")
                    or {"in": "continuous", "motif": None}
                ),
            }
            if is_shot:
                scene["visual_function"] = str(beat.get("function") or "")
                if beat.get("treatment_id"):
                    scene["visual_treatment_id"] = str(beat["treatment_id"])
                if beat.get("manim_class") in {
                    "BJJActionScene",
                    "CombatScienceScene",
                }:
                    word_count = max(1, len(narration.split()))
                    scene["beats"] = [
                        {
                            "at_word": min(word_count - 1, index),
                            "action": f"bjj_action:{beat.get('action')}",
                        }
                        for index in sorted({0, word_count // 3, (word_count * 2) // 3})
                    ]
                    scene["layout_hints"] = {
                        "landscape": {
                            "action_zone": "center",
                            "caption_zone": "lower_third",
                        },
                        "vertical": {
                            "action_zone": "upper_center",
                            "caption_zone": "lower_third",
                        },
                    }
            if beat["manim_class"] == "StickFigureScene":
                poses = list(scene["parameters"].get("poses") or [])
                if poses:
                    scene["beats"] = [
                        {"at_word": 0, "action": f"pose:{poses[0]}"}
                    ]
            elif beat["manim_class"] == "JointLeverageScene":
                scene["beats"] = [
                    {"at_word": 0, "action": "flash_label:fulcrum"}
                ]
            if beat["act"] == "cta":
                scene["on_screen_text"] = str(
                    beat.get("parameters", {}).get("headline") or "Learn more."
                )
            scenes.append(scene)

        source_slug = str(bundle["slug"])
        theme = dict(channel_config.get("theme") or {})
        voice = dict(channel_config.get("voice") or {})
        targets = list(job.input_payload.get("targets") or ["landscape", "vertical"])
        art_bible_id = str((shot_plan or {}).get("art_direction_id") or "")
        art_bible_hash = str((shot_plan or {}).get("art_bible_hash") or "")
        storyboard = {
            "schema_version": "2.1.0" if art_bible_id and art_bible_hash else "2.0.0",
            "job_id": job.id,
            "source": {
                "slug": source_slug,
                "kind": bundle["kind"],
                "ref": bundle["ref"],
                "content_hash": bundle["content_hash"],
            },
            "channel": {
                "id": str(channel_config["id"]),
                "series": str(
                    channel_config.get("series") or "physics-of-grappling"
                ),
            },
            "global_settings": {
                "voice": voice,
                "theme": theme,
                "music": dict(
                    channel_config.get("music")
                    or {"track_id": None, "gain_db_rel_voice": -18, "ducking": True}
                ),
                "pacing": {
                    "wpm_target": wpm,
                    "visual_change_max_s": 6,
                    "pattern_interrupt_max_s": 25,
                    "shorts_visual_change_max_s": 3,
                },
                "targets": targets,
                "style_preset": str(
                    (shot_plan or {}).get("style_preset") or "technical_bjj_flat"
                ),
            },
            "claims": list(beat_sheet.get("claims") or []),
            "scenes": scenes,
            "shorts": [
                {
                    "clip_id": f"{source_slug}-short",
                    "scene_ids": [
                        next(
                            scene["scene_id"]
                            for scene in scenes
                            if scene["act"] == "payoff"
                        ),
                        scenes[0]["scene_id"],
                    ],
                    "hook_line": scenes[
                        next(
                            index
                            for index, scene in enumerate(scenes)
                            if scene["act"] == "payoff"
                        )
                    ]["narration_text"],
                    "title": f"{str(bundle['payload'].get('name') or source_slug).title()} explained",
                    "max_duration_s": 58,
                }
            ],
            "packaging": {
                "titles": [
                    f"{str(bundle['payload'].get('name') or source_slug).title()} Explained",
                    f"How {str(bundle['payload'].get('name') or source_slug).title()} Creates Leverage",
                ],
                "thumbnail": {
                    "concept": "Color-coded flat-vector athletes and a leverage diagram",
                    "variant_texts": ["POSITION CREATES LEVERAGE"],
                    "badge_color": str(theme.get("accent_color") or "#3B82F6"),
                },
                "description_md": (
                    "Full written breakdown: {ARTICLE_URL}\n"
                    "Find verified academies near you: {REGISTRY_URL}"
                ),
                "tags": ["bjj", source_slug, "grappling"],
                "chapters_from_scenes": True,
                "cta": {
                    "line": (
                        "Find verified academies near you at "
                        "NationalBJJRegistry.com"
                    ),
                    "url": "https://nationalbjjregistry.com",
                    "utm_campaign": source_slug,
                },
                "synthetic_content_disclosure": {
                    "required": False,
                    "reason": (
                        "Fully animated and non-realistic with an own-voice clone."
                    ),
                },
            },
        }
        if art_bible_id and art_bible_hash:
            storyboard["art_direction"] = {
                "id": art_bible_id,
                "hash": art_bible_hash,
                "treatment_contract_version": str(
                    (visual_treatment or {}).get(
                        "schema_version", "visual_treatment.v1"
                    )
                ),
                "treatment_hash": str(
                    (visual_treatment or {}).get("artifact_hash") or ""
                ),
            }
        return storyboard

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        bundle = json.loads(
            ctx.job_dir.joinpath("source_bundle.json").read_text(encoding="utf-8")
        )
        beat_sheet = json.loads(
            ctx.job_dir.joinpath("beat_sheet.json").read_text(encoding="utf-8")
        )
        shot_plan_path = ctx.job_dir / "shot_plan.json"
        shot_plan = (
            json.loads(shot_plan_path.read_text(encoding="utf-8"))
            if shot_plan_path.is_file()
            else None
        )
        treatment_path = ctx.job_dir / "visual_treatment.json"
        visual_treatment = (
            json.loads(treatment_path.read_text(encoding="utf-8"))
            if treatment_path.is_file()
            else None
        )
        channel_id = str(job.input_payload.get("channel") or "combat-science")
        config_path = (
            Path(ctx.configs.get("video_engine_root", Path.cwd()))
            / "configs"
            / "channels"
            / f"{channel_id}.json"
        )
        channel = json.loads(config_path.read_text(encoding="utf-8"))
        storyboard = self.build(
            job,
            bundle,
            beat_sheet,
            channel,
            shot_plan,
            visual_treatment,
        )
        schema_path = (
            Path(ctx.configs.get("video_engine_root", Path.cwd()))
            / "configs"
            / "storyboard.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = sorted(
            Draft7Validator(schema).iter_errors(storyboard),
            key=lambda error: list(error.absolute_path),
        )
        if errors:
            detail = "; ".join(error.message for error in errors)
            raise ValueError(f"built storyboard violates schema: {detail}")
        ctx.job_dir.joinpath("storyboard.json").write_text(
            json.dumps(storyboard, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return StageOutput(
            {
                "artifact_path": "storyboard.json",
                "scene_count": len(storyboard["scenes"]),
                "cost_usd": 0.0,
            }
        )
