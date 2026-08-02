"""Deterministic sound-cue scheduling from reviewed storyboard action phases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.timing import load_measured_timeline


ENGINE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PALETTE_PATH = ENGINE_ROOT / "configs" / "sound_palette.json"
PHASE_POSITION = {
    "anticipation": 0.18,
    "action": 0.38,
    "contact": 0.58,
    "recovery": 0.80,
}


class SoundDesignError(ValueError):
    """A cue cannot be resolved without changing the narration contract."""


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SoundDesignError(f"{path.name} must contain a JSON object")
    return value


class SoundDesignService:
    def __init__(self, palette_path: str | Path | None = None) -> None:
        self.palette_path = (
            Path(palette_path) if palette_path is not None else DEFAULT_PALETTE_PATH
        )

    def build(
        self,
        storyboard: Mapping[str, Any],
        audio_dir: str | Path,
        output_path: str | Path,
    ) -> dict[str, Any]:
        if not self.palette_path.is_file():
            raise FileNotFoundError(f"sound palette does not exist: {self.palette_path}")
        palette = _load_object(self.palette_path)
        cues = palette.get("cues")
        if not isinstance(cues, Mapping):
            raise SoundDesignError("sound palette requires a cues object")
        timeline = load_measured_timeline(storyboard, audio_dir)
        scenes = {
            int(scene["scene_id"]): scene
            for scene in storyboard.get("scenes", [])
            if isinstance(scene, Mapping)
        }
        events: list[dict[str, Any]] = []
        for scene_timing in timeline:
            scene = scenes[scene_timing.scene_id]
            parameters = scene.get("parameters") or {}
            requested = parameters.get("sound_cues") or []
            if not isinstance(requested, list):
                raise SoundDesignError(
                    f"scene {scene_timing.scene_id}: sound_cues must be an array"
                )
            for request in requested:
                if isinstance(request, str):
                    cue_id = request
                    requested_phase = None
                elif isinstance(request, Mapping):
                    cue_id = str(request.get("cue") or "")
                    requested_phase = request.get("phase")
                else:
                    raise SoundDesignError(
                        f"scene {scene_timing.scene_id}: invalid sound cue {request!r}"
                    )
                definition = cues.get(cue_id)
                if not isinstance(definition, Mapping):
                    raise SoundDesignError(
                        f"scene {scene_timing.scene_id}: unknown sound cue {cue_id!r}"
                    )
                phase = str(requested_phase or definition.get("phase") or "action")
                if phase not in PHASE_POSITION:
                    raise SoundDesignError(
                        f"scene {scene_timing.scene_id}: unknown sound phase {phase!r}"
                    )
                raw_asset = definition.get("asset_path")
                asset_path: Path | None = None
                if raw_asset:
                    candidate = Path(str(raw_asset))
                    asset_path = (
                        candidate
                        if candidate.is_absolute()
                        else self.palette_path.parent / candidate
                    ).resolve()
                at_s = scene_timing.start_s + (
                    scene_timing.audio_duration_s * PHASE_POSITION[phase]
                )
                events.append(
                    {
                        "event_id": f"s{scene_timing.scene_id}-{cue_id}-{len(events) + 1}",
                        "scene_id": scene_timing.scene_id,
                        "cue": cue_id,
                        "phase": phase,
                        "at_s": round(at_s, 6),
                        "gain_db": float(definition.get("gain_db", -18.0)),
                        "asset_path": str(asset_path) if asset_path is not None else None,
                        "available": bool(asset_path and asset_path.is_file()),
                    }
                )
        result = {
            "schema_version": "sound_manifest.v1",
            "palette_version": str(
                palette.get("schema_version") or "sound_palette.v1"
            ),
            "narration_clock_s": round(timeline.total_s, 6),
            "events": events,
            "available_event_count": sum(
                1 for event in events if event["available"]
            ),
            "music": None,
        }
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return result

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        del job
        storyboard_path = ctx.job_dir / "storyboard.json"
        if not storyboard_path.is_file():
            raise FileNotFoundError("storyboard.json is required before sound design")
        storyboard = _load_object(storyboard_path)
        configured = ctx.configs.get("sound_palette_path")
        service = SoundDesignService(configured or self.palette_path)
        result = service.build(
            storyboard,
            ctx.job_dir / "audio",
            ctx.job_dir / "audio" / "sound_manifest.json",
        )
        return StageOutput(
            {
                "manifest_path": "audio/sound_manifest.json",
                "event_count": len(result["events"]),
                "available_event_count": result["available_event_count"],
                "narration_clock_s": result["narration_clock_s"],
                "cost_usd": 0.0,
            }
        )


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return SoundDesignService().run_stage(job, ctx)


__all__ = [
    "DEFAULT_PALETTE_PATH",
    "PHASE_POSITION",
    "SoundDesignError",
    "SoundDesignService",
    "run_stage",
]
