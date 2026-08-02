"""Deterministic Remotion editorial boundary.

The Manim renderer owns scene clips and measured audio timing.  This service
owns the small, immutable manifest consumed by the local Remotion project.  A
manifest contains no generated media and never changes after it has been
written; a retry is allowed only when it produces byte-for-byte equivalent
canonical JSON.

The service deliberately does not import Node, Chromium, or Remotion.  The
render command is built as an argument vector and passed to an injected
``runner`` so contract tests can exercise the editorial boundary without a
browser or a render dependency.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


MANIFEST_VERSION = "edit_manifest.v1"
SUPPORTED_ASPECTS = frozenset({"landscape", "vertical"})
SUPPORTED_TRANSITIONS = frozenset(
    {"continuous", "crossfade", "match_cut", "hard_cut"}
)

DEFAULT_PROFILES: dict[str, dict[str, int]] = {
    "landscape": {"width": 1920, "height": 1080, "fps": 60},
    "vertical": {"width": 1080, "height": 1920, "fps": 30},
}


class EditorialManifestError(ValueError):
    """A manifest is malformed or cannot be safely rendered."""


class ManifestImmutableError(EditorialManifestError):
    """An existing manifest differs from a new attempted write."""


class EditorialRenderError(RuntimeError):
    """Remotion did not complete a requested render."""


@dataclass(frozen=True, slots=True)
class EditorialRenderResult:
    """Evidence returned after invoking Remotion."""

    manifest_path: Path
    output_path: Path
    command: tuple[str, ...]

    @property
    def summary(self) -> dict[str, Any]:
        return {
            "manifest_path": str(self.manifest_path),
            "output_path": str(self.output_path),
            "command": list(self.command),
            "cost_usd": 0.0,
        }


Runner = Callable[..., subprocess.CompletedProcess[str]]


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EditorialManifestError(f"{label} must be an object")
    return value


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise EditorialManifestError(f"{label} must be a positive integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise EditorialManifestError(f"{label} must be a positive integer") from exc
    if number <= 0 or float(value) != number:
        raise EditorialManifestError(f"{label} must be a positive integer")
    return number


def _non_negative_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise EditorialManifestError(f"{label} must be a non-negative integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise EditorialManifestError(f"{label} must be a non-negative integer") from exc
    if number < 0 or float(value) != number:
        raise EditorialManifestError(f"{label} must be a non-negative integer")
    return number


def _positive_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise EditorialManifestError(f"{label} must be a positive number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise EditorialManifestError(f"{label} must be a positive number") from exc
    if not math.isfinite(number) or number <= 0:
        raise EditorialManifestError(f"{label} must be a positive number")
    return number


def _non_negative_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise EditorialManifestError(f"{label} must be a non-negative number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise EditorialManifestError(f"{label} must be a non-negative number") from exc
    if not math.isfinite(number) or number < 0:
        raise EditorialManifestError(f"{label} must be a non-negative number")
    return number


def _clip_path(clip: Mapping[str, Any], index: int) -> str:
    for key in ("src", "path", "local_path", "video_path", "file", "asset"):
        value = clip.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise EditorialManifestError(f"clips[{index}] is missing a local src/path")


def _clip_id(clip: Mapping[str, Any], index: int) -> str:
    value = clip.get("id", clip.get("clip_id", clip.get("scene_id", index + 1)))
    if value is None or not str(value).strip():
        raise EditorialManifestError(f"clips[{index}] has an empty id")
    return str(value)


def _transition_value(clip: Mapping[str, Any], index: int) -> str:
    value: Any = clip.get("transition", clip.get("transition_in", "continuous"))
    if isinstance(value, Mapping):
        value = value.get("in", value.get("type", value.get("kind", "continuous")))
    transition = str(value or "continuous").casefold()
    if transition not in SUPPORTED_TRANSITIONS:
        supported = ", ".join(sorted(SUPPORTED_TRANSITIONS))
        raise EditorialManifestError(
            f"clips[{index}] transition {transition!r} is unsupported; use {supported}"
        )
    return transition


def _duration_frames(clip: Mapping[str, Any], index: int, fps: int) -> int:
    for key in ("duration_in_frames", "duration_frames", "frames"):
        if clip.get(key) is not None:
            return _positive_int(clip[key], f"clips[{index}].{key}")
    for key in ("duration_s", "duration", "seconds"):
        if clip.get(key) is not None:
            seconds = _positive_number(clip[key], f"clips[{index}].{key}")
            return max(1, round(seconds * fps))
    raise EditorialManifestError(
        f"clips[{index}] needs duration_in_frames or duration_s"
    )


def _transition_frames(clip: Mapping[str, Any], index: int, fps: int, transition: str) -> int:
    value: Any = clip.get("transition_frames")
    if value is None:
        value = clip.get("transition_duration_frames")
    if value is None:
        transition_data = clip.get("transition")
        if isinstance(transition_data, Mapping):
            value = transition_data.get(
                "duration_in_frames",
                transition_data.get(
                    "duration_frames",
                    transition_data.get("duration_s"),
                ),
            )
            if value is not None and transition_data.get("duration_s") is not None and not transition_data.get("duration_in_frames") and not transition_data.get("duration_frames"):
                value = round(_non_negative_number(value, f"clips[{index}].transition.duration_s") * fps)
    if value is None:
        for key in ("transition_duration_s", "transition_s"):
            if clip.get(key) is not None:
                value = round(_non_negative_number(clip[key], f"clips[{index}].{key}") * fps)
                break
    if value is None:
        value = round(0.3 * fps) if transition in {"crossfade", "match_cut"} else 0
    frames = _non_negative_int(value, f"clips[{index}].transition_frames")
    if transition in {"continuous", "hard_cut"} and frames:
        raise EditorialManifestError(
            f"clips[{index}] transition_frames must be zero for {transition}"
        )
    return frames


def _timing_frames(
    item: Mapping[str, Any], index: int, fps: int, label: str
) -> tuple[int, int]:
    if item.get("start_s") is not None or item.get("from_s") is not None:
        start_seconds = item.get("start_s", item.get("from_s"))
        start_frames = max(
            0,
            round(_non_negative_number(start_seconds, f"{label}[{index}].start_s") * fps),
        )
    else:
        start: Any = item.get(
            "from",
            item.get("start_frame", item.get("start_in_frames", item.get("start", 0))),
        )
        start_frames = _non_negative_int(start, f"{label}[{index}].from")
    for key in ("duration_in_frames", "duration_frames", "frames"):
        if item.get(key) is not None:
            return start_frames, _positive_int(item[key], f"{label}[{index}].{key}")
    if item.get("duration_s") is not None or item.get("duration") is not None or item.get("seconds") is not None:
        duration_value = item.get("duration_s", item.get("duration", item.get("seconds")))
        return start_frames, max(
            1,
            round(_positive_number(duration_value, f"{label}[{index}].duration_s") * fps),
        )
    end_s = item.get("end_s", item.get("to_s"))
    if end_s is not None:
        end_frames = round(_non_negative_number(end_s, f"{label}[{index}].end_s") * fps)
        if end_frames <= start_frames:
            raise EditorialManifestError(f"{label}[{index}] end must be after from")
        return start_frames, end_frames - start_frames
    end = item.get("to", item.get("end_frame", item.get("end")))
    if end is not None:
        end_frames = _positive_int(end, f"{label}[{index}].to")
        if end_frames <= start_frames:
            raise EditorialManifestError(f"{label}[{index}] end must be after from")
        return start_frames, end_frames - start_frames
    raise EditorialManifestError(
        f"{label}[{index}] needs duration_in_frames or duration_s"
    )


def _asset_is_remote(value: str) -> bool:
    lowered = value.casefold()
    return lowered.startswith(("http://", "https://", "data:", "blob:"))


def _validate_local_asset(
    value: str,
    *,
    manifest_path: Path | None,
    label: str,
    check_assets: bool,
) -> None:
    if _asset_is_remote(value):
        raise EditorialManifestError(f"{label} must reference a local asset")
    if not check_assets:
        return
    candidate = Path(value)
    if not candidate.is_absolute() and manifest_path is not None:
        candidate = manifest_path.parent / candidate
    if not candidate.is_file():
        raise EditorialManifestError(f"{label} does not exist: {value}")


def _raw_clips(manifest: Mapping[str, Any]) -> list[Any]:
    for key in ("clips", "segments", "scenes"):
        value = manifest.get(key)
        if value is not None:
            if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
                raise EditorialManifestError(f"{key} must be an array")
            return list(value)
    raise EditorialManifestError("manifest must contain clips, segments, or scenes")


def _profile_defaults(aspect: str) -> dict[str, int]:
    return dict(DEFAULT_PROFILES[aspect])


def _canonicalize(
    manifest: Mapping[str, Any],
    *,
    manifest_path: Path | None = None,
    check_assets: bool = False,
) -> dict[str, Any]:
    data = _as_mapping(manifest, "manifest")
    version = data.get("schema_version", data.get("version", MANIFEST_VERSION))
    if str(version) != MANIFEST_VERSION:
        raise EditorialManifestError(
            f"manifest schema_version must be {MANIFEST_VERSION!r}"
        )

    aspect_value = data.get("aspect", data.get("target", data.get("profile", "landscape")))
    if isinstance(aspect_value, Mapping):
        aspect_value = aspect_value.get("target", aspect_value.get("aspect", "landscape"))
    aspect = str(aspect_value).casefold()
    if aspect.endswith("_draft") or aspect.endswith("_final"):
        aspect = aspect.rsplit("_", 1)[0]
    if aspect not in SUPPORTED_ASPECTS:
        raise EditorialManifestError("manifest aspect must be landscape or vertical")
    defaults = _profile_defaults(aspect)
    fps = _positive_int(data.get("fps", defaults["fps"]), "manifest.fps")
    width = _positive_int(data.get("width", defaults["width"]), "manifest.width")
    height = _positive_int(data.get("height", defaults["height"]), "manifest.height")

    raw_clips = _raw_clips(data)
    if not raw_clips:
        raise EditorialManifestError("manifest clips must not be empty")
    clips: list[dict[str, Any]] = []
    ids: set[str] = set()
    for index, raw_clip in enumerate(raw_clips):
        clip = _as_mapping(raw_clip, f"clips[{index}]")
        path = _clip_path(clip, index)
        _validate_local_asset(
            path,
            manifest_path=manifest_path,
            label=f"clips[{index}].src",
            check_assets=check_assets,
        )
        clip_id = _clip_id(clip, index)
        if clip_id in ids:
            raise EditorialManifestError(f"duplicate clip id: {clip_id}")
        ids.add(clip_id)
        transition = _transition_value(clip, index)
        duration = _duration_frames(clip, index, fps)
        transition_frames = _transition_frames(clip, index, fps, transition)
        canonical_clip: dict[str, Any] = {
            "id": clip_id,
            "src": path,
            "duration_in_frames": duration,
            "transition": transition,
            "transition_frames": transition_frames,
        }
        # Preserve scene identity and the reviewed transition motif without
        # copying arbitrary mutable storyboard objects into the contract.
        for key in ("scene_id", "scene_ids", "motif", "transition_motif", "function"):
            if clip.get(key) is not None:
                canonical_clip[key] = deepcopy(clip[key])
        clips.append(canonical_clip)

    captions: list[dict[str, Any]] = []
    raw_captions = data.get("captions", [])
    if not isinstance(raw_captions, Sequence) or isinstance(raw_captions, (str, bytes, bytearray)):
        raise EditorialManifestError("manifest.captions must be an array")
    for index, raw_caption in enumerate(raw_captions):
        caption = _as_mapping(raw_caption, f"captions[{index}]")
        text = str(caption.get("text", caption.get("caption", ""))).strip()
        if not text:
            raise EditorialManifestError(f"captions[{index}] text must not be empty")
        start, duration = _timing_frames(caption, index, fps, "captions")
        item: dict[str, Any] = {
            "id": str(caption.get("id", f"caption-{index + 1}")),
            "text": text,
            "from": start,
            "duration_in_frames": duration,
        }
        if caption.get("style") is not None:
            item["style"] = deepcopy(
                dict(_as_mapping(caption["style"], f"captions[{index}].style"))
            )
        captions.append(item)

    overlays: list[dict[str, Any]] = []
    raw_overlays = data.get("overlays", [])
    if not isinstance(raw_overlays, Sequence) or isinstance(raw_overlays, (str, bytes, bytearray)):
        raise EditorialManifestError("manifest.overlays must be an array")
    for index, raw_overlay in enumerate(raw_overlays):
        overlay = _as_mapping(raw_overlay, f"overlays[{index}]")
        start, duration = _timing_frames(overlay, index, fps, "overlays")
        kind = str(overlay.get("kind", overlay.get("type", "text"))).casefold()
        if kind not in {"text", "image", "box", "line", "arrow"}:
            raise EditorialManifestError(f"overlays[{index}] has unsupported kind {kind!r}")
        item = {
            "id": str(overlay.get("id", f"overlay-{index + 1}")),
            "kind": kind,
            "from": start,
            "duration_in_frames": duration,
        }
        if overlay.get("text") is not None:
            item["text"] = str(overlay["text"])
        source = overlay.get(
            "src",
            overlay.get("path", overlay.get("local_path", overlay.get("asset"))),
        )
        if source is not None:
            source_text = str(source).strip()
            if not source_text:
                raise EditorialManifestError(f"overlays[{index}].src must not be empty")
            _validate_local_asset(
                source_text,
                manifest_path=manifest_path,
                label=f"overlays[{index}].src",
                check_assets=check_assets,
            )
            item["src"] = source_text
        if kind == "text" and "text" not in item and "src" not in item:
            raise EditorialManifestError(f"overlays[{index}] needs text or src")
        if overlay.get("style") is not None:
            item["style"] = deepcopy(
                dict(_as_mapping(overlay["style"], f"overlays[{index}].style"))
            )
        overlays.append(item)

    computed_duration = 0
    for index, clip in enumerate(clips):
        duration = int(clip["duration_in_frames"])
        overlap = 0
        if index > 0 and clip["transition"] in {"crossfade", "match_cut"}:
            overlap = min(
                int(clip["transition_frames"]),
                int(clips[index - 1]["duration_in_frames"]) // 2,
                duration // 2,
            )
        computed_duration = max(computed_duration, computed_duration + duration - overlap)
    explicit_duration = data.get("duration_in_frames", data.get("duration_frames"))
    duration_in_frames = computed_duration if explicit_duration is None else _positive_int(
        explicit_duration, "manifest.duration_in_frames"
    )
    if duration_in_frames < computed_duration:
        raise EditorialManifestError(
            "manifest.duration_in_frames is shorter than the clip timeline"
        )
    for label, items in (("captions", captions), ("overlays", overlays)):
        for index, item in enumerate(items):
            end_frame = int(item["from"]) + int(item["duration_in_frames"])
            if end_frame > duration_in_frames:
                raise EditorialManifestError(
                    f"{label}[{index}] extends beyond manifest.duration_in_frames"
                )

    canonical: dict[str, Any] = {
        "schema_version": MANIFEST_VERSION,
        "aspect": aspect,
        "fps": fps,
        "width": width,
        "height": height,
        "duration_in_frames": duration_in_frames,
        "clips": clips,
        "captions": captions,
        "overlays": overlays,
    }
    # ``segments`` is a read-only coverage index for the existing visual-QC
    # contract.  Remotion renders ``clips``; operators can still trace every
    # storyboard scene to the clip that carries it without parsing a path.
    segments: list[dict[str, Any]] = []
    for clip in clips:
        scene_ids = clip.get("scene_ids")
        if isinstance(scene_ids, Sequence) and not isinstance(scene_ids, (str, bytes, bytearray)):
            ids = list(scene_ids)
        elif clip.get("scene_id") is not None:
            ids = [clip["scene_id"]]
        else:
            ids = []
        for scene_id in ids:
            segments.append(
                {
                    "scene_id": scene_id,
                    "clip_id": clip["id"],
                    "path": clip["src"],
                    "duration_in_frames": clip["duration_in_frames"],
                }
            )
    canonical["segments"] = segments
    metadata = data.get("metadata")
    if metadata is not None:
        canonical["metadata"] = deepcopy(dict(_as_mapping(metadata, "manifest.metadata")))
    return canonical


def validate_edit_manifest(
    manifest: Mapping[str, Any],
    *,
    manifest_path: str | Path | None = None,
    check_assets: bool = False,
) -> dict[str, Any]:
    """Validate and return canonical JSON-safe editorial data."""

    return _canonicalize(
        manifest,
        manifest_path=Path(manifest_path) if manifest_path is not None else None,
        check_assets=check_assets,
    )


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def manifest_sha256(manifest: Mapping[str, Any]) -> str:
    """Return the stable hash used in operator evidence and cache keys."""

    canonical = _canonical_json(validate_edit_manifest(manifest)).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def write_edit_manifest(
    manifest: Mapping[str, Any] | str | Path,
    path: str | Path | Mapping[str, Any],
    *,
    check_assets: bool = False,
) -> Path:
    """Functional convenience wrapper for callers without a render service."""

    return EditorialService().write_manifest(
        manifest,
        path,
        check_assets=check_assets,
    )


class EditorialService:
    """Write immutable edit manifests and invoke the local Remotion project."""

    def __init__(
        self,
        editor_root: str | Path | None = None,
        *,
        runner: Runner = subprocess.run,
        remotion_executable: str = "npx",
        remotion_package: str = "remotion",
        remotion_version: str = "4.0.502",
    ) -> None:
        self.editor_root = Path(editor_root) if editor_root is not None else Path(__file__).resolve().parents[2] / "editor"
        self._runner = runner
        self.remotion_executable = shutil.which(remotion_executable) or remotion_executable
        self.remotion_package = remotion_package
        self.remotion_version = remotion_version

    def build_manifest(
        self,
        clips: Iterable[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        *source_args: Mapping[str, Any],
        segments: Iterable[Mapping[str, Any]] | None = None,
        scenes: Iterable[Mapping[str, Any]] | None = None,
        storyboard: Mapping[str, Any] | None = None,
        segment_manifest: Mapping[str, Any] | None = None,
        captions: Iterable[Mapping[str, Any]] = (),
        overlays: Iterable[Mapping[str, Any]] = (),
        aspect: str = "landscape",
        target: str | None = None,
        fps: int | None = None,
        width: int | None = None,
        height: int | None = None,
        duration_in_frames: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a canonical manifest from scene/segment-like dictionaries."""

        if len(source_args) > 1:
            raise EditorialManifestError("build_manifest accepts at most storyboard and segment manifest")
        if source_args:
            if isinstance(clips, Mapping) and storyboard is None:
                storyboard = clips
                clips = None
            if segment_manifest is None:
                segment_manifest = source_args[0]
        if storyboard is None and isinstance(clips, Mapping) and "scenes" in clips:
            storyboard = clips
            clips = None
        if segment_manifest is None and isinstance(segments, Mapping):
            segment_manifest = segments
            segments = None
        if target is not None:
            aspect = target
        if storyboard is not None and segment_manifest is not None:
            scenes_by_id = {
                int(scene["scene_id"]): scene
                for scene in list(storyboard.get("scenes") or [])
                if isinstance(scene, Mapping) and scene.get("scene_id") is not None
            }
            converted: list[dict[str, Any]] = []
            for index, raw_segment in enumerate(list(segment_manifest.get("segments") or [])):
                segment = _as_mapping(raw_segment, f"segments[{index}]")
                scene_ids = list(segment.get("scene_ids") or [])
                if not scene_ids and segment.get("scene_id") is not None:
                    scene_ids = [segment["scene_id"]]
                first_scene = scenes_by_id.get(int(scene_ids[0])) if scene_ids else None
                converted.append(
                    {
                        "id": f"segment-{index + 1}",
                        "path": segment.get("path"),
                        "duration_s": segment.get("duration_s"),
                        "duration_in_frames": segment.get("duration_in_frames"),
                        "scene_ids": scene_ids,
                        "transition": (first_scene or {}).get("transition", "continuous"),
                    }
                )
            clips = converted
        selected = clips if clips is not None else segments if segments is not None else scenes
        if selected is None:
            raise EditorialManifestError("build_manifest requires clips, segments, or scenes")
        normalized_aspect = str(aspect).casefold().removesuffix("_draft").removesuffix("_final")
        if normalized_aspect not in SUPPORTED_ASPECTS:
            raise EditorialManifestError("manifest aspect must be landscape or vertical")
        profile = _profile_defaults(normalized_aspect)
        payload: dict[str, Any] = {
            "schema_version": MANIFEST_VERSION,
            "aspect": aspect,
            "fps": fps if fps is not None else profile["fps"],
            "width": width if width is not None else profile["width"],
            "height": height if height is not None else profile["height"],
            "clips": [dict(clip) for clip in selected],
            "captions": [dict(caption) for caption in (captions or ())],
            "overlays": [dict(overlay) for overlay in (overlays or ())],
        }
        if duration_in_frames is not None:
            payload["duration_in_frames"] = duration_in_frames
        if metadata is not None:
            payload["metadata"] = dict(metadata)
        return validate_edit_manifest(payload)

    # Explicit names make the boundary discoverable to callers migrating from
    # the existing ``manifest.json`` render artifact.
    create_manifest = build_manifest
    build_edit_manifest = build_manifest
    compile_manifest = build_manifest

    def write_manifest(
        self,
        manifest: Mapping[str, Any] | str | Path,
        path: str | Path | Mapping[str, Any],
        *,
        check_assets: bool = False,
    ) -> Path:
        # Accept both ``write_manifest(manifest, path)`` and the natural file
        # first spelling used by a few repository callers.
        if isinstance(manifest, (str, Path)) and isinstance(path, Mapping):
            manifest, path = path, manifest
        if not isinstance(manifest, Mapping):
            raise EditorialManifestError("write_manifest requires a manifest object")
        output = Path(path)
        canonical = validate_edit_manifest(
            manifest,
            manifest_path=output,
            check_assets=check_assets,
        )
        text = _canonical_json(canonical)
        if output.exists():
            try:
                existing = json.loads(output.read_text(encoding="utf-8"))
                existing_canonical = validate_edit_manifest(
                    existing,
                    manifest_path=output,
                    check_assets=False,
                )
            except (OSError, json.JSONDecodeError, EditorialManifestError) as exc:
                raise ManifestImmutableError(
                    f"existing edit manifest is invalid and cannot be replaced: {output}"
                ) from exc
            if _canonical_json(existing_canonical) != text:
                raise ManifestImmutableError(
                    f"edit manifest is immutable and differs from attempted write: {output}"
                )
            return output
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(output)
        return output

    write_edit_manifest = write_manifest
    persist_manifest = write_manifest

    def read_manifest(self, path: str | Path, *, check_assets: bool = False) -> dict[str, Any]:
        manifest_path = Path(path)
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EditorialManifestError(f"unable to read edit manifest: {manifest_path}") from exc
        return validate_edit_manifest(
            payload,
            manifest_path=manifest_path,
            check_assets=check_assets,
        )

    load_manifest = read_manifest

    def validate_manifest(
        self,
        value: Mapping[str, Any] | str | Path,
        *,
        check_assets: bool = False,
    ) -> dict[str, Any]:
        if isinstance(value, (str, Path)):
            return self.read_manifest(value, check_assets=check_assets)
        return validate_edit_manifest(value, check_assets=check_assets)

    def build_render_command(
        self,
        manifest_path: str | Path,
        output_path: str | Path,
        *,
        composition_id: str = "Editorial",
        public_dir: str | Path | None = None,
    ) -> list[str]:
        manifest_file = Path(manifest_path).resolve()
        manifest = self.read_manifest(manifest_file)
        del manifest  # Validation above is intentional before any process spawn.
        output = Path(output_path).resolve()
        command = [
            self.remotion_executable,
            self.remotion_package,
            "render",
            "src/index.tsx",
            composition_id,
            str(output),
            "--props",
            str(manifest_file),
        ]
        if public_dir is not None:
            resolved_public_dir = Path(public_dir).resolve()
            if not resolved_public_dir.is_dir():
                raise EditorialManifestError(
                    f"Remotion public directory does not exist: {resolved_public_dir}"
                )
            command.extend(["--public-dir", str(resolved_public_dir)])
        return command

    def render_manifest(
        self,
        manifest_path: str | Path,
        output_path: str | Path,
        *,
        composition_id: str = "Editorial",
        target: str | None = None,
        profile: str | None = None,
        public_dir: str | Path | None = None,
        verify_output: bool = True,
    ) -> EditorialRenderResult:
        manifest_file = Path(manifest_path)
        output = Path(output_path)
        loaded = self.read_manifest(manifest_file)
        if target is not None and str(target).casefold() != str(loaded["aspect"]).casefold():
            raise EditorialManifestError(
                f"render target {target!r} does not match manifest aspect {loaded['aspect']!r}"
            )
        if profile is not None:
            composition_id = str(profile)
        command = self.build_render_command(
            manifest_file,
            output,
            composition_id=composition_id,
            public_dir=public_dir,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            completed = self._runner(
                command,
                cwd=str(self.editor_root),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            detail = getattr(exc, "stderr", None) or str(exc)
            raise EditorialRenderError(f"Remotion render failed: {detail}") from exc
        if getattr(completed, "returncode", 0) not in (0, None):
            detail = getattr(completed, "stderr", None) or getattr(completed, "stdout", None) or ""
            raise EditorialRenderError(
                f"Remotion render failed with exit code {completed.returncode}: {detail}"
            )
        if verify_output and not output.is_file():
            stderr = getattr(completed, "stderr", "") or ""
            raise EditorialRenderError(
                f"Remotion completed without output artifact {output}: {stderr}"
            )
        return EditorialRenderResult(
            manifest_path=manifest_file,
            output_path=output,
            command=tuple(command),
        )

    render = render_manifest
    invoke = render_manifest

    def render_storyboard_profile(
        self,
        storyboard: Mapping[str, Any],
        segment_manifest: Mapping[str, Any],
        output_dir: str | Path,
        *,
        target: str = "landscape",
        captions: Iterable[Mapping[str, Any]] = (),
        overlays: Iterable[Mapping[str, Any]] = (),
        verify_output: bool = True,
    ) -> EditorialRenderResult:
        """Compile an existing Manim segment manifest and render one profile."""

        scenes_by_id = {
            int(scene["scene_id"]): scene
            for scene in list(storyboard.get("scenes") or [])
            if isinstance(scene, Mapping) and scene.get("scene_id") is not None
        }
        clips: list[dict[str, Any]] = []
        for index, raw_segment in enumerate(list(segment_manifest.get("segments") or [])):
            segment = _as_mapping(raw_segment, f"segments[{index}]")
            scene_ids = list(segment.get("scene_ids") or [])
            first = scenes_by_id.get(int(scene_ids[0])) if scene_ids else None
            transition: Any = (first or {}).get("transition", "continuous")
            motif = (first or {}).get("transition", {})
            duration_s = segment.get("duration_s")
            if duration_s is None and segment.get("duration_in_frames") is not None:
                duration_s = float(segment["duration_in_frames"]) / DEFAULT_PROFILES[
                    str(target).casefold().removesuffix("_draft").removesuffix("_final")
                ]["fps"]
            clip: dict[str, Any] = {
                "id": f"segment-{index + 1}",
                "path": segment.get("path"),
                "duration_s": duration_s,
                "transition": transition,
                "scene_ids": scene_ids,
            }
            if isinstance(motif, Mapping) and motif.get("motif") is not None:
                clip["motif"] = motif["motif"]
            clips.append(clip)
        output_root = Path(output_dir)
        manifest_path = output_root / "edit_manifest.json"
        manifest = self.build_manifest(
            clips,
            captions=captions,
            overlays=overlays,
            aspect=target,
            metadata={"source": "storyboard", "scene_count": len(storyboard.get("scenes") or [])},
        )
        self.write_manifest(manifest, manifest_path, check_assets=False)
        return self.render_manifest(
            manifest_path,
            output_root / "editorial.mp4",
            verify_output=verify_output,
        )

    def run_stage(self, job: Any, ctx: Any) -> Any:
        """Pipeline adapter for the optional ``editing_picture`` stage.

        Manim writes one ``video/<profile>/manifest.json`` per selected
        profile.  This adapter converts those measured segment manifests into
        immutable editorial manifests and invokes the local renderer through
        this service's injected runner.  No storyboard is edited.
        """

        from content.video_engine.src.models import StageOutput

        job_dir = Path(ctx.job_dir).resolve()
        storyboard_path = job_dir / "storyboard.json"
        if not storyboard_path.is_file():
            raise FileNotFoundError(f"storyboard not found: {storyboard_path}")
        storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
        if not isinstance(storyboard, Mapping):
            raise EditorialManifestError("storyboard must contain an object")
        profiles = list(job.config_snapshot.get("selected_render_profiles") or [])
        if not profiles:
            targets = list(job.input_payload.get("targets") or ["landscape"])
            profiles = [
                {"landscape": "landscape_final", "vertical": "vertical_final"}.get(
                    str(target), str(target)
                )
                for target in targets
            ]
        outputs: dict[str, Any] = {}
        captions: list[dict[str, Any]] = []
        cursor_s = 0.0
        for scene in list(storyboard.get("scenes") or []):
            words_path = (
                job_dir
                / "audio"
                / f"scene_{int(scene['scene_id'])}.words.json"
            )
            if not words_path.is_file():
                continue
            timing = json.loads(words_path.read_text(encoding="utf-8"))
            duration_s = float(timing.get("duration_s") or 0.0)
            narration = str(scene.get("narration_text") or "").strip()
            words = [
                dict(word)
                for word in timing.get("words", [])
                if isinstance(word, Mapping) and word.get("w")
            ]
            if words:
                for chunk_index in range(0, len(words), 6):
                    chunk = words[chunk_index : chunk_index + 6]
                    start_s = float(chunk[0].get("start_s") or 0.0)
                    end_s = float(chunk[-1].get("end_s") or duration_s)
                    captions.append(
                        {
                            "id": (
                                f"scene-{int(scene['scene_id'])}-caption-"
                                f"{chunk_index // 6 + 1}"
                            ),
                            "text": " ".join(str(word["w"]) for word in chunk),
                            "start_s": cursor_s + start_s,
                            "duration_s": max(0.05, end_s - start_s),
                        }
                    )
            elif narration and duration_s > 0:
                captions.append(
                    {
                        "id": f"scene-{int(scene['scene_id'])}-caption",
                        "text": narration,
                        "start_s": cursor_s,
                        "duration_s": duration_s,
                    }
                )
            cursor_s += duration_s + float(
                (scene.get("timing") or {}).get("padding_s") or 0.0
            )
        for profile_name in profiles:
            profile_name = str(profile_name)
            profile_configs = job.config_snapshot.get("render_profile_configs") or {}
            configured_target = (
                profile_configs.get(profile_name, {}).get("target")
                if isinstance(profile_configs, Mapping)
                and isinstance(profile_configs.get(profile_name), Mapping)
                else None
            )
            target = str(
                configured_target
                or (profile_name.rsplit("_", 1)[0] if "_" in profile_name else profile_name)
            )
            if target not in SUPPORTED_ASPECTS:
                raise EditorialManifestError(
                    f"editorial profile {profile_name!r} must resolve to landscape or vertical"
                )
            segment_path = job_dir / "video" / profile_name / "manifest.json"
            if not segment_path.is_file():
                raise FileNotFoundError(f"scene segment manifest not found: {segment_path}")
            segment_manifest = json.loads(segment_path.read_text(encoding="utf-8"))
            if not isinstance(segment_manifest, Mapping):
                raise EditorialManifestError(f"segment manifest must contain an object: {segment_path}")
            scenes_by_id = {
                int(scene["scene_id"]): scene
                for scene in list(storyboard.get("scenes") or [])
                if isinstance(scene, Mapping) and scene.get("scene_id") is not None
            }
            clips: list[dict[str, Any]] = []
            for index, raw_segment in enumerate(list(segment_manifest.get("segments") or [])):
                segment = _as_mapping(raw_segment, f"segments[{index}]")
                raw_path = segment.get("path")
                if not isinstance(raw_path, str) or not raw_path:
                    raise EditorialManifestError(f"segments[{index}] is missing path")
                clip_path = Path(raw_path)
                if not clip_path.is_absolute():
                    candidates = [segment_path.parent / clip_path, job_dir / clip_path]
                    clip_path = next((candidate for candidate in candidates if candidate.is_file()), candidates[0])
                clip_path = clip_path.resolve()
                try:
                    public_path = clip_path.relative_to(job_dir).as_posix()
                except ValueError as exc:
                    raise EditorialManifestError(
                        f"segments[{index}] path escapes the video job: {clip_path}"
                    ) from exc
                scene_ids = list(segment.get("scene_ids") or [])
                if not scene_ids and segment.get("scene_id") is not None:
                    scene_ids = [segment["scene_id"]]
                first_scene = scenes_by_id.get(int(scene_ids[0])) if scene_ids else None
                duration_s = segment.get("duration_s")
                if duration_s is None and segment.get("duration_in_frames") is not None:
                    profile_config_for_duration = (
                        profile_configs.get(profile_name)
                        if isinstance(profile_configs, Mapping)
                        and isinstance(profile_configs.get(profile_name), Mapping)
                        else {}
                    )
                    profile_fps = int(
                        profile_config_for_duration.get("fps", DEFAULT_PROFILES[target]["fps"])
                    )
                    duration_s = float(segment["duration_in_frames"]) / profile_fps
                clips.append(
                    {
                        "id": f"segment-{index + 1}",
                        "path": public_path,
                        "duration_s": duration_s,
                        "scene_ids": scene_ids,
                        "transition": (first_scene or {}).get("transition", "continuous"),
                        "transition_frames": 0,
                    }
                )
            output_root = job_dir / "editorial" / target
            manifest_path = output_root / "edit_manifest.json"
            profile_config = (
                profile_configs.get(profile_name)
                if isinstance(profile_configs, Mapping)
                and isinstance(profile_configs.get(profile_name), Mapping)
                else {}
            )
            manifest = self.build_manifest(
                clips,
                aspect=target,
                fps=profile_config.get("fps"),
                width=profile_config.get("width"),
                height=profile_config.get("height"),
                captions=captions,
                metadata={"profile": profile_name, "source": "manim"},
            )
            self.write_manifest(manifest, manifest_path)
            # Keep a root-level index for visual QC and operator discovery.
            root_manifest = job_dir / "edit_manifest.json"
            if not root_manifest.exists():
                self.write_manifest(manifest, root_manifest)
            editorial_index = job_dir / "editorial" / "edit_manifest.json"
            if not editorial_index.exists():
                self.write_manifest(manifest, editorial_index)
            result = self.render_manifest(
                manifest_path,
                output_root / "editorial.mp4",
                public_dir=job_dir,
            )
            outputs[profile_name] = result.summary
            outputs[profile_name]["manifest_path"] = str(
                manifest_path.relative_to(job_dir).as_posix()
            )
        return StageOutput(
            {
                "profiles": outputs,
                "manifest_count": len(outputs),
                "manifest_paths": [
                    str(value["manifest_path"])
                    for value in outputs.values()
                    if isinstance(value, Mapping) and value.get("manifest_path")
                ],
                "cost_usd": 0.0,
            }
        )


def run_stage(job: Any, ctx: Any) -> Any:
    """Module-level pipeline adapter matching the other video services."""

    return EditorialService().run_stage(job, ctx)


__all__ = [
    "DEFAULT_PROFILES",
    "EditorialManifestError",
    "EditorialRenderError",
    "EditorialRenderResult",
    "EditorialService",
    "MANIFEST_VERSION",
    "ManifestImmutableError",
    "SUPPORTED_ASPECTS",
    "SUPPORTED_TRANSITIONS",
    "manifest_sha256",
    "run_stage",
    "validate_edit_manifest",
    "write_edit_manifest",
]
