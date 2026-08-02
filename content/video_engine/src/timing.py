"""Strict measured-audio timing artifacts for post-Gate-A video stages.

The storyboard owns authoring estimates (``timing.target_s``), but the audio
stage owns the clock after Gate A.  This module is the single parser for the
run-local ``audio/scene_<id>.words.json`` artifacts consumed by rendering,
compositing, packaging, and QC.  A missing or invalid artifact is never
silently replaced by a storyboard estimate.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


_WORDS_FILENAME = re.compile(r"^scene_(\d+)\.words\.json$")


class TimingArtifactError(ValueError):
    """A measured timing artifact cannot safely be used as the render clock."""


@dataclass(frozen=True, slots=True)
class SceneTiming:
    """One scene's measured audio interval, including storyboard padding."""

    scene_id: int
    duration_s: float
    padding_s: float
    start_s: float
    end_s: float

    @property
    def audio_duration_s(self) -> float:
        """Alias that makes the measured nature explicit to consumers."""

        return self.duration_s

    @property
    def total_duration_s(self) -> float:
        """Measured narration plus the configured inter-scene padding."""

        return self.end_s - self.start_s

    def to_dict(self) -> dict[str, float | int]:
        return {
            "scene_id": self.scene_id,
            "duration_s": self.duration_s,
            "audio_duration_s": self.duration_s,
            "padding_s": self.padding_s,
            "start_s": self.start_s,
            "end_s": self.end_s,
        }


@dataclass(frozen=True, slots=True)
class MeasuredTimeline(Sequence[SceneTiming]):
    """Ordered scene timing values and the total measured run duration."""

    scenes: tuple[SceneTiming, ...]

    def __post_init__(self) -> None:
        if not self.scenes:
            raise TimingArtifactError("measured audio timeline contains no scenes")

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self.scenes)

    def __len__(self) -> int:
        return len(self.scenes)

    def __getitem__(self, index):  # type: ignore[no-untyped-def]
        return self.scenes[index]

    @property
    def total_s(self) -> float:
        return self.scenes[-1].end_s

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenes": [scene.to_dict() for scene in self.scenes],
            "total_s": self.total_s,
        }


def _scene_error(scene_id: int, message: str) -> TimingArtifactError:
    return TimingArtifactError(f"scene {scene_id}: {message}")


def _finite_number(value: Any, *, scene_id: int, field_name: str) -> float:
    if isinstance(value, bool):
        raise _scene_error(scene_id, f"{field_name} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise _scene_error(scene_id, f"{field_name} must be a finite number") from exc
    if not math.isfinite(result):
        raise _scene_error(scene_id, f"{field_name} must be finite")
    return result


def _read_words_artifact(path: Path, scene_id: int) -> Mapping[str, Any]:
    if not path.is_file():
        raise _scene_error(scene_id, f"missing word-timing artifact: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _scene_error(scene_id, f"malformed word-timing artifact: {path.name}") from exc
    if not isinstance(payload, Mapping):
        raise _scene_error(scene_id, "word-timing artifact must contain a JSON object")
    return payload


def _validate_words(payload: Mapping[str, Any], scene_id: int, duration_s: float) -> None:
    words = payload.get("words")
    if not isinstance(words, list) or not words:
        raise _scene_error(scene_id, "word-timing artifact must contain a non-empty words array")

    previous_start = -math.inf
    previous_end = -math.inf
    for index, item in enumerate(words):
        if not isinstance(item, Mapping):
            raise _scene_error(scene_id, f"word {index} must be an object")
        token = item.get("w")
        if not isinstance(token, str) or not token.strip():
            raise _scene_error(scene_id, f"word {index} is missing a non-empty 'w' value")
        start_s = _finite_number(item.get("start_s"), scene_id=scene_id, field_name=f"word {index} start_s")
        end_s = _finite_number(item.get("end_s"), scene_id=scene_id, field_name=f"word {index} end_s")
        if start_s < 0:
            raise _scene_error(scene_id, f"word {index} start_s must be non-negative")
        if end_s < start_s:
            raise _scene_error(scene_id, f"word {index} end_s must not precede start_s")
        if start_s < previous_start or end_s < previous_end:
            raise _scene_error(scene_id, "word timings must be ordered")
        if end_s > duration_s + 1e-6:
            raise _scene_error(
                scene_id,
                f"word {index} end_s {end_s:g} exceeds duration_s {duration_s:g}",
            )
        previous_start = start_s
        previous_end = end_s


def _scene_ids(storyboard: Mapping[str, Any]) -> list[int]:
    scenes = storyboard.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise TimingArtifactError("storyboard.scenes must be a non-empty array")
    ids: list[int] = []
    seen: set[int] = set()
    for index, scene in enumerate(scenes):
        if not isinstance(scene, Mapping):
            raise TimingArtifactError(f"scene at index {index}: storyboard scene must be an object")
        raw_id = scene.get("scene_id")
        if isinstance(raw_id, bool):
            raise TimingArtifactError(f"scene at index {index}: scene_id must be an integer")
        if isinstance(raw_id, float) and not raw_id.is_integer():
            raise TimingArtifactError(f"scene at index {index}: scene_id must be an integer")
        try:
            scene_id = int(raw_id)
        except (TypeError, ValueError) as exc:
            raise TimingArtifactError(f"scene at index {index}: scene_id must be an integer") from exc
        if scene_id in seen:
            raise _scene_error(scene_id, "duplicate storyboard scene_id")
        seen.add(scene_id)
        ids.append(scene_id)
    return ids


def _reject_unexpected_artifacts(audio_dir: Path, expected_ids: set[int]) -> None:
    if not audio_dir.exists():
        return
    seen_ids: set[int] = set()
    for path in audio_dir.glob("*.words.json"):
        match = _WORDS_FILENAME.fullmatch(path.name)
        if match is None:
            raise TimingArtifactError(f"unexpected timing artifact: {path.name}")
        artifact_id = int(match.group(1))
        if artifact_id not in expected_ids:
            raise _scene_error(artifact_id, f"unexpected word-timing artifact: {path.name}")
        if artifact_id in seen_ids:
            raise _scene_error(artifact_id, f"duplicate word-timing artifacts for scene {artifact_id}")
        seen_ids.add(artifact_id)


def load_measured_timeline(
    storyboard: Mapping[str, Any],
    audio_dir: str | Path,
) -> MeasuredTimeline:
    """Load and validate the complete measured timeline for a storyboard.

    Scenes are returned in storyboard order.  Each scene's ``duration_s`` comes
    only from its words artifact; ``timing.padding_s`` is then appended to form
    the scene interval and the run's cumulative ``total_s``.  No storyboard
    estimate fallback exists in this function.
    """

    if not isinstance(storyboard, Mapping):
        raise TimingArtifactError("storyboard must be a JSON object")
    scene_ids = _scene_ids(storyboard)
    words_dir = Path(audio_dir)
    _reject_unexpected_artifacts(words_dir, set(scene_ids))

    values: list[SceneTiming] = []
    elapsed = 0.0
    for scene, scene_id in zip(storyboard["scenes"], scene_ids):
        artifact_path = words_dir / f"scene_{scene_id}.words.json"
        payload = _read_words_artifact(artifact_path, scene_id)
        payload_id = payload.get("scene_id")
        if payload_id is None:
            raise _scene_error(scene_id, "word-timing artifact is missing scene_id")
        if isinstance(payload_id, bool) or (
            isinstance(payload_id, float) and not payload_id.is_integer()
        ):
            raise _scene_error(scene_id, "word-timing artifact scene_id is invalid")
        try:
            parsed_payload_id = int(payload_id)
        except (TypeError, ValueError) as exc:
            raise _scene_error(scene_id, "word-timing artifact scene_id is invalid") from exc
        if parsed_payload_id != scene_id:
            raise _scene_error(
                scene_id,
                f"word-timing artifact scene_id {parsed_payload_id} does not match filename",
            )

        duration_s = _finite_number(payload.get("duration_s"), scene_id=scene_id, field_name="duration_s")
        if duration_s <= 0:
            raise _scene_error(scene_id, "duration_s must be positive")
        _validate_words(payload, scene_id, duration_s)

        timing = scene.get("timing") or {}
        if not isinstance(timing, Mapping):
            raise _scene_error(scene_id, "storyboard timing must be an object")
        raw_padding = timing.get("padding_s", 0.0)
        padding_s = _finite_number(raw_padding, scene_id=scene_id, field_name="padding_s")
        if padding_s < 0:
            raise _scene_error(scene_id, "padding_s must be non-negative")

        start_s = elapsed
        end_s = start_s + duration_s + padding_s
        if not math.isfinite(end_s) or end_s <= start_s:
            raise _scene_error(scene_id, "computed timeline interval is invalid")
        values.append(
            SceneTiming(
                scene_id=scene_id,
                duration_s=duration_s,
                padding_s=padding_s,
                start_s=start_s,
                end_s=end_s,
            )
        )
        elapsed = end_s

    return MeasuredTimeline(tuple(values))


__all__ = [
    "MeasuredTimeline",
    "SceneTiming",
    "TimingArtifactError",
    "load_measured_timeline",
]
