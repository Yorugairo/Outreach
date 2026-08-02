"""Manim scene rendering with deterministic grouping and manifest output.

The module deliberately contains no shell command strings.  Manim is imported
only at the render boundary, allowing the fast contract suite to run on
machines that have not installed the optional renderer dependencies.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from content.video_engine.src.models import (
    ALL_SCENE_CLASS_REGISTRY,
    StageContext,
    StageOutput,
    VideoRun,
)
from content.video_engine.src.scenes import SCENE_CLASSES
from content.video_engine.src.scenes.base import MANIM_AVAILABLE, ThemedScene, tempconfig


ENGINE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILES_PATH = ENGINE_ROOT / "configs" / "render_profiles.json"


class RenderError(RuntimeError):
    """Base error for a render unit that cannot produce a valid clip."""


class RenderDependencyUnavailable(RenderError):
    """Manim/ffmpeg is not installed on this local worker."""


class DurationMismatchError(RenderError):
    """A rendered unit drifted beyond the one-percent audio contract."""


@dataclass(frozen=True, slots=True)
class RenderUnit:
    """A contiguous set of scenes rendered into one movie segment."""

    scenes: tuple[dict[str, Any], ...]
    class_name: str

    @property
    def scene_ids(self) -> tuple[int, ...]:
        return tuple(int(scene["scene_id"]) for scene in self.scenes)

    @property
    def first_scene_id(self) -> int:
        return self.scene_ids[0]

    @property
    def last_scene_id(self) -> int:
        return self.scene_ids[-1]

    @property
    def is_sequence(self) -> bool:
        return len(self.scenes) > 1

    def output_stem(self) -> str:
        if self.is_sequence:
            return f"seq_{self.first_scene_id}-{self.last_scene_id}"
        return f"scene_{self.first_scene_id}"


def _registry_entry(class_name: str) -> Mapping[str, Any]:
    value = ALL_SCENE_CLASS_REGISTRY.get(class_name, {})
    return value if isinstance(value, Mapping) else {}


def classes_compatible(left: str, right: str) -> bool:
    """Return whether two scene classes may share one continuous render."""

    if left == right:
        return True
    left_entry = _registry_entry(left)
    right_entry = _registry_entry(right)
    left_allowed = left_entry.get("continuous_with", ())
    right_allowed = right_entry.get("continuous_with", ())
    return right in left_allowed or left in right_allowed


def _transition_in(scene: Mapping[str, Any]) -> str:
    transition = scene.get("transition") or {}
    if not isinstance(transition, Mapping):
        return "continuous"
    return str(transition.get("in", "continuous")).casefold()


def group_render_units(scenes: Iterable[Mapping[str, Any]]) -> list[RenderUnit]:
    """Group consecutive continuous scenes with compatible classes.

    The transition belongs to the entering scene.  A missing transition uses
    the schema default (``continuous``); any explicit cut starts a new unit.
    """

    units: list[RenderUnit] = []
    current: list[dict[str, Any]] = []
    current_class: str | None = None
    for raw_scene in scenes:
        scene = dict(raw_scene)
        class_name = str(scene.get("manim_class", ""))
        can_join = bool(
            current
            and _transition_in(scene) == "continuous"
            and current_class is not None
            and classes_compatible(current_class, class_name)
        )
        if not can_join:
            if current:
                units.append(RenderUnit(tuple(current), current_class or ""))
            current = [scene]
            current_class = class_name
        else:
            current.append(scene)
    if current:
        units.append(RenderUnit(tuple(current), current_class or ""))
    return units


# A short alias is useful to callers that describe the operation as scene
# grouping rather than render-unit construction.
group_scenes = group_render_units


def load_render_profiles(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    profile_path = Path(path) if path is not None else DEFAULT_PROFILES_PATH
    payload = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("render_profiles.json must contain an object")
    return {str(name): dict(profile) for name, profile in payload.items()}


def _profile_config(profile: Mapping[str, Any]) -> dict[str, Any]:
    required = ("target", "width", "height", "fps")
    missing = [key for key in required if key not in profile]
    if missing:
        raise ValueError(f"render profile is missing keys: {', '.join(missing)}")
    return {
        "target": str(profile["target"]),
        "width": int(profile["width"]),
        "height": int(profile["height"]),
        "fps": int(profile["fps"]),
        "quality": str(profile.get("quality", "low_quality")),
    }


def render_dependency_status() -> tuple[str, ...]:
    """Return explicit local dependency reasons, preserving their order."""

    missing: list[str] = []
    if not MANIM_AVAILABLE:
        missing.append("missing local dependency: manim")
    if shutil.which("ffmpeg") is None:
        missing.append("missing local dependency: ffmpeg")
    if shutil.which("ffprobe") is None:
        missing.append("missing local dependency: ffprobe")
    return tuple(missing)


def render_smoke_skip_reason() -> str | None:
    """Return the pytest skip reason, or ``None`` when smoke can run."""

    missing = render_dependency_status()
    return "; ".join(missing) if missing else None


def _duration_from_words(
    scene: Mapping[str, Any],
    audio_dir: Path | None,
) -> float:
    scene_id = int(scene["scene_id"])
    candidates: list[Path] = []
    if audio_dir is not None:
        candidates.append(audio_dir / f"scene_{scene_id}.words.json")
    explicit = scene.get("audio_words_path")
    if explicit:
        candidates.insert(0, Path(str(explicit)))
    for path in candidates:
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            duration = payload.get("duration_s") if isinstance(payload, Mapping) else None
            if duration is not None:
                return max(0.01, float(duration)) + float(
                    (scene.get("timing") or {}).get("padding_s", 0.0) or 0.0
                )
    # Contract tests and local previews may carry measured duration directly;
    # production stages are expected to provide words.json from audio_synth.
    for key in ("audio_duration", "duration_s"):
        if scene.get(key) is not None:
            return max(0.01, float(scene[key]))
    timing = scene.get("timing") or {}
    return max(0.01, float(timing.get("target_s", 0.01)))


def _with_word_timings(
    scene: Mapping[str, Any],
    audio_dir: Path,
) -> dict[str, Any]:
    enriched = dict(scene)
    candidates: list[Path] = []
    explicit = scene.get("audio_words_path")
    if explicit:
        candidates.append(Path(str(explicit)))
    candidates.append(audio_dir / f"scene_{int(scene['scene_id'])}.words.json")
    source = next((path for path in candidates if path.is_file()), None)
    if source is None:
        return enriched
    payload = json.loads(source.read_text(encoding="utf-8"))
    words = payload.get("words") if isinstance(payload, Mapping) else None
    if isinstance(words, list):
        enriched["word_timings"] = words
        enriched["audio_words_path"] = str(source)
    return enriched


def _read_storyboard(value: Mapping[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    path = Path(value)
    return json.loads(path.read_text(encoding="utf-8"))


class ManimRenderService:
    """Render storyboard scene units for one or more aspect profiles."""

    def __init__(
        self,
        job_dir: str | Path,
        *,
        profiles: Mapping[str, Mapping[str, Any]] | None = None,
        scene_classes: Mapping[str, type] | None = None,
        duration_probe: Callable[[Path], float] | None = None,
        render_unit_fn: Callable[[RenderUnit, Mapping[str, Any], Path, str], Path] | None = None,
    ) -> None:
        self.job_dir = Path(job_dir)
        self.profiles = (
            {str(name): dict(profile) for name, profile in profiles.items()}
            if profiles is not None
            else load_render_profiles()
        )
        self.scene_classes = dict(scene_classes or SCENE_CLASSES)
        self.duration_probe = duration_probe or probe_duration
        self.render_unit_fn = render_unit_fn

    def render_storyboard(
        self,
        storyboard: Mapping[str, Any] | str | Path,
        profile_name: str,
        *,
        audio_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        data = _read_storyboard(storyboard)
        if profile_name not in self.profiles:
            raise ValueError(f"unknown render profile: {profile_name}")
        profile = _profile_config(self.profiles[profile_name])
        source_scenes = data.get("scenes") or []
        if not isinstance(source_scenes, Sequence):
            raise ValueError("storyboard.scenes must be an array")
        words_dir = Path(audio_dir) if audio_dir is not None else self.job_dir / "audio"
        scenes = [
            _with_word_timings(scene, words_dir)
            for scene in source_scenes
        ]
        units = group_render_units(scenes)
        profile_dir = self.job_dir / "video" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        segments: list[dict[str, Any]] = []
        for unit in units:
            durations = [_duration_from_words(scene, words_dir) for scene in unit.scenes]
            expected_duration = sum(durations)
            output_path = profile_dir / f"{unit.output_stem()}.mp4"
            if self.render_unit_fn is not None:
                produced = Path(
                    self.render_unit_fn(unit, profile, output_path, str(profile_name))
                )
                if produced != output_path:
                    if not produced.is_file():
                        raise RenderError(f"render callback did not create {produced}")
                    shutil.copyfile(produced, output_path)
            else:
                self._render_unit(
                    unit,
                    profile,
                    profile_name,
                    output_path,
                    audio_dir=words_dir,
                )
            if not output_path.is_file():
                raise RenderError(f"render did not produce {output_path}")
            measured = self.duration_probe(output_path)
            tolerance = max(0.01, expected_duration * 0.01)
            difference = abs(measured - expected_duration)
            # Low-frame-rate Manim previews quantize each play() call to a
            # frame. A multi-scene articulated sequence can therefore drift
            # slightly even though its logical timeline is exact. Conform
            # bounded renderer-only drift back to the narration clock; large
            # mismatches and injected test renderers still fail closed.
            quantization_budget = max(
                expected_duration * 0.05,
                len(unit.scenes) * 5 / max(1, int(profile["fps"])),
            )
            if (
                difference > tolerance
                and self.render_unit_fn is None
                and difference <= quantization_budget
            ):
                conformed = output_path.with_name(f".{output_path.stem}.conformed.mp4")
                ratio = expected_duration / measured
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(output_path),
                        "-vf",
                        f"setpts={ratio:.12f}*PTS",
                        "-an",
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        str(conformed),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                conformed.replace(output_path)
                measured = self.duration_probe(output_path)
                difference = abs(measured - expected_duration)
            if difference > tolerance:
                ids = ", ".join(str(scene_id) for scene_id in unit.scene_ids)
                raise DurationMismatchError(
                    f"scene ids [{ids}] duration {measured:.3f}s differs from "
                    f"audio clock {expected_duration:.3f}s by more than 1%"
                )
            segments.append(
                {
                    "path": output_path.relative_to(self.job_dir).as_posix(),
                    "scene_ids": list(unit.scene_ids),
                    "duration_s": round(float(measured), 6),
                }
            )

        manifest = {"segments": segments}
        manifest_path = profile_dir / "manifest.json"
        _write_json(manifest_path, manifest)
        return manifest

    # Common service spelling used by pipeline wiring and tests.
    render = render_storyboard

    def _render_unit(
        self,
        unit: RenderUnit,
        profile: Mapping[str, Any],
        profile_name: str,
        output_path: Path,
        *,
        audio_dir: Path,
    ) -> Path:
        missing = render_dependency_status()
        if missing:
            raise RenderDependencyUnavailable("; ".join(missing))
        scene_class = self.scene_classes.get(unit.class_name)
        if scene_class is None:
            raise RenderError(f"unknown scene class: {unit.class_name}")

        durations = [
            _duration_from_words(scene, audio_dir) for scene in unit.scenes
        ]
        theme = {}
        if unit.scenes:
            theme = dict(unit.scenes[0].get("theme") or {})
        storyboard_theme = getattr(self, "storyboard_theme", None)
        if isinstance(storyboard_theme, Mapping):
            theme = {**storyboard_theme, **theme}

        service = self
        scene_specs = unit.scenes

        class SequenceScene(scene_class):  # type: ignore[misc, valid-type]
            def construct(self) -> None:  # pragma: no cover - optional smoke path
                for index, (spec, duration) in enumerate(zip(scene_specs, durations)):
                    self._activate_scene(spec, profile["target"], duration, theme)
                    if index:
                        self.next_section(name=f"scene_{spec['scene_id']}")
                    scene_class.entrance(self)
                    if self._first_animation_start is None:
                        raise AssertionError(
                            f"scene {spec['scene_id']} entrance contract violated: no animation"
                        )
                    if self._first_animation_start > 0.5:
                        raise AssertionError(
                            f"scene {spec['scene_id']} first animation starts "
                            f"at {self._first_animation_start:.3f}s"
                        )
                    scene_class.body(self, duration)

        media_dir = self.job_dir / ".manim_media" / profile_name
        media_dir.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "media_dir": str(media_dir),
            "pixel_width": int(profile["width"]),
            "pixel_height": int(profile["height"]),
            "frame_rate": int(profile["fps"]),
            "output_file": output_path.stem,
            "disable_caching": True,
        }
        # Keep the profile's output path isolated per job.  Manim's file
        # writer may place the movie in a quality subdirectory, so resolve it
        # from the writer after render and copy it into the artifact contract.
        with tempconfig(config):
            rendered_scene = SequenceScene(
                scene_specs[0], profile["target"], durations[0], theme
            )
            rendered_scene.render()
            movie_path = getattr(
                getattr(getattr(rendered_scene, "renderer", None), "file_writer", None),
                "movie_file_path",
                None,
            )
        candidates: list[Path] = []
        if movie_path:
            candidates.append(Path(str(movie_path)))
        candidates.extend(media_dir.rglob(f"{output_path.stem}*.mp4"))
        source = next((candidate for candidate in candidates if candidate.is_file()), None)
        if source is None:
            raise RenderError(f"Manim did not write an mp4 for {unit.output_stem()}")
        if source.resolve() != output_path.resolve():
            shutil.copyfile(source, output_path)
        return output_path


def probe_duration(path: str | Path) -> float:
    """Read an mp4 duration through ffprobe without invoking a shell."""

    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise RenderDependencyUnavailable("missing local dependency: ffprobe")
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        return float(completed.stdout.strip())
    except (TypeError, ValueError) as exc:
        raise RenderError(f"ffprobe returned no duration for {path}") from exc


def run_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    """Pipeline stage adapter for ``rendering_scenes``."""

    storyboard_path = ctx.job_dir / "storyboard.json"
    if not storyboard_path.is_file():
        candidate = job.input_payload.get("storyboard_path") or job.source_ref
        candidate_path = Path(str(candidate))
        if not candidate_path.is_file():
            raise FileNotFoundError(f"storyboard not found: {candidate_path}")
        storyboard_path = candidate_path
    data = _read_storyboard(storyboard_path)
    settings = data.get("global_settings") or {}
    theme = settings.get("theme") if isinstance(settings, Mapping) else {}
    snapshotted_profiles = job.config_snapshot.get("render_profile_configs")
    service = ManimRenderService(
        ctx.job_dir,
        profiles=snapshotted_profiles or ctx.configs.get("render_profiles"),
    )
    service.storyboard_theme = dict(theme or {})  # type: ignore[attr-defined]
    targets = job.input_payload.get("targets") or settings.get("targets") or ["landscape"]
    selected_profiles = list(job.config_snapshot.get("selected_render_profiles") or [])
    if not selected_profiles:
        profile_aliases = {
            "landscape": "landscape_final",
            "vertical": "vertical_final",
        }
        selected_profiles = [
            profile_aliases.get(str(target), str(target))
            for target in targets
        ]
    manifests: dict[str, dict[str, Any]] = {}
    for profile_name in selected_profiles:
        manifests[profile_name] = service.render_storyboard(data, profile_name)
    return StageOutput(
        {
            "profiles": sorted(manifests),
            "manifests": manifests,
            "segment_count": sum(
                len(manifest.get("segments", [])) for manifest in manifests.values()
            ),
        }
    )


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    temporary.replace(path)


# Backwards-compatible class alias for callers that name the implementation
# ``ManimRenderer`` rather than ``ManimRenderService``.
ManimRenderer = ManimRenderService


__all__ = [
    "DurationMismatchError",
    "ManimRenderService",
    "ManimRenderer",
    "RenderError",
    "RenderDependencyUnavailable",
    "RenderUnit",
    "classes_compatible",
    "group_render_units",
    "group_scenes",
    "load_render_profiles",
    "probe_duration",
    "render_dependency_status",
    "render_smoke_skip_reason",
    "run_stage",
]
