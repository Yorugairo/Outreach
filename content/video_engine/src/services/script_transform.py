from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


@dataclass(slots=True, frozen=True)
class Beat:
    act: str
    narration_text: str
    visual_type: str
    manim_class: str
    parameters: dict[str, Any] = field(default_factory=dict)
    transition: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class BeatSheet:
    source_slug: str
    claims: list[dict[str, Any]]
    beats: list[Beat]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


class ScriptTransformService:
    def build_corpus(
        self,
        bundle: dict[str, Any],
        technique_manifest: dict[str, Any] | None = None,
        *,
        require_visual_manifest: bool = False,
    ) -> BeatSheet:
        source = dict(bundle["payload"])
        name = str(source.get("name") or bundle["slug"].replace("-", " ").title())
        transcript = _sentences(str(source["transcript"]))
        if not transcript:
            raise ValueError("corpus transcript contains no usable steps")
        errors = list(source.get("metadata", {}).get("common_errors") or [])
        conflict = (
            f"A common mistake is {str(errors[0]).rstrip('.').casefold()}."
            if errors
            else "The movement fails when posture and wrist control are released."
        )
        actions = [
            dict(action)
            for action in (technique_manifest or {}).get("actions", [])
            if isinstance(action, dict) and action.get("id")
        ]
        if not actions:
            if require_visual_manifest:
                raise ValueError(
                    "a reviewed technique visual manifest is required for visual-v2 transformation"
                )
            # Corpus validation only checks whether the transcript can be
            # deterministically segmented. It intentionally does not grant
            # visual-reference approval, so return the legacy-safe plan here;
            # pipeline execution always sets require_visual_manifest=True.
            legacy_beats = [
                Beat(
                    act="hook",
                    narration_text=f"{name} works when position creates leverage before the finish.",
                    visual_type="stick_figure_action",
                    manim_class="StickFigureScene",
                    parameters={"poses": ["closed_guard", "posture_broken"]},
                    transition={"in": "continuous", "motif": "cast:uke"},
                ),
                *[
                    Beat(
                        act="develop",
                        narration_text=re.sub(
                            r"^(?:first|second|third|finally),?\s+",
                            "",
                            sentence,
                            flags=re.IGNORECASE,
                        ),
                        visual_type="stick_figure_action",
                        manim_class="StickFigureScene",
                        parameters={"poses": ["posture_broken", "armbar_extension"]},
                        transition={"in": "continuous", "motif": "cast:uke"},
                    )
                    for sentence in transcript
                ],
                Beat(
                    act="conflict",
                    narration_text=conflict,
                    visual_type="stick_figure_action",
                    manim_class="StickFigureScene",
                    parameters={"poses": ["arm_yank_fail"]},
                    transition={"in": "match_cut", "motif": "lever_arrow"},
                ),
                Beat(
                    act="payoff",
                    narration_text="Keep the wrist, align the hips, and finish through controlled position.",
                    visual_type="joint_leverage_diagram",
                    manim_class="JointLeverageScene",
                    parameters={
                        "lever": {
                            "fulcrum": "hips",
                            "load": "elbow",
                            "effort": "hip_drive",
                        }
                    },
                    transition={"in": "continuous", "motif": "lever_arrow"},
                ),
                Beat(
                    act="cta",
                    narration_text=(
                        "Read the full steps and find a verified academy near you "
                        "through the National BJJ Registry."
                    ),
                    visual_type="title_card",
                    manim_class="TitleConceptCard",
                    parameters={"headline": "Learn it properly."},
                    transition={"in": "crossfade", "motif": None},
                ),
            ]
            return BeatSheet(
                source_slug=str(bundle["slug"]),
                claims=[],
                beats=legacy_beats,
            )

        def recipe(index: int, function: str) -> dict[str, Any]:
            explicit = next(
                (
                    action
                    for action in actions
                    if index in list(action.get("beat_indices") or [])
                ),
                None,
            )
            selected = explicit or actions[
                min(len(actions) - 1, max(0, round(index * (len(actions) - 1) / 10)))
            ]
            return {
                "action_id": str(selected["id"]),
                "function": function,
                "instructional": True,
            }

        beats: list[Beat] = [
            Beat(
                act="hook",
                narration_text=f"{name} works when position creates leverage before the finish.",
                visual_type="bjj_action",
                manim_class="BJJActionScene",
                parameters=recipe(0, "result_preview"),
                transition={"in": "continuous", "motif": "cast:uke"},
            )
        ]
        transcript_count = len(transcript)
        for index, sentence in enumerate(transcript):
            sentence = re.sub(r"^(?:first|second|third|finally),?\s+", "", sentence, flags=re.IGNORECASE)
            if index == 0:
                function = "wide_setup"
            elif index in {1, transcript_count - 1}:
                function = "contact_closeup"
            else:
                function = "mechanic_transition"
            beats.append(
                Beat(
                    act="develop",
                    narration_text=sentence,
                    visual_type="bjj_action",
                    manim_class="BJJActionScene",
                    parameters=recipe(index + 1, function),
                    transition={"in": "continuous", "motif": "cast:uke"},
                )
            )
        beats.extend(
            [
                Beat(
                    act="conflict",
                    narration_text=conflict,
                    visual_type="bjj_action",
                    manim_class="BJJActionScene",
                    parameters=recipe(8, "wrong_right_compare"),
                    transition={"in": "match_cut", "motif": "lever_arrow"},
                ),
                Beat(
                    act="payoff",
                    narration_text="Keep the wrist, align the hips, and finish through controlled position.",
                    visual_type="bjj_action",
                    manim_class="BJJActionScene",
                    parameters=recipe(9, "force_diagram"),
                    transition={"in": "continuous", "motif": "lever_arrow"},
                ),
                Beat(
                    act="payoff",
                    narration_text="The finish is the result of retained control, angle, and a stable elbow line.",
                    visual_type="bjj_action",
                    manim_class="BJJActionScene",
                    parameters=recipe(10, "result_hold"),
                    transition={"in": "continuous", "motif": "cast:uke"},
                ),
                Beat(
                    act="cta",
                    narration_text=(
                        "Read the full steps and find a verified academy near you "
                        "through the National BJJ Registry."
                    ),
                    visual_type="title_card",
                    manim_class="TitleConceptCard",
                    parameters={"headline": "Learn it properly."},
                    transition={"in": "crossfade", "motif": None},
                ),
            ]
        )
        return BeatSheet(source_slug=str(bundle["slug"]), claims=[], beats=beats)

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        bundle_path = ctx.job_dir / "source_bundle.json"
        if not bundle_path.exists():
            raise FileNotFoundError("source_bundle.json is required before transformation")
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        if bundle["kind"] != "corpus_technique":
            raise ValueError(
                "essay transformation requires an explicitly configured guarded writer"
            )
        manifest_path = ctx.job_dir / "technique_manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(
                "technique_manifest.json is required before visual-v2 transformation"
            )
        technique_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        beat_sheet = self.build_corpus(
            bundle,
            technique_manifest,
            require_visual_manifest=True,
        )
        output_path = ctx.job_dir / "beat_sheet.json"
        output_path.write_text(
            json.dumps(beat_sheet.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return StageOutput(
            {
                "artifact_path": "beat_sheet.json",
                "beat_count": len(beat_sheet.beats),
                "mode": "deterministic_corpus",
                "cost_usd": 0.0,
            }
        )
