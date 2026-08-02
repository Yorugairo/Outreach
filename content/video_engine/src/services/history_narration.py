"""Canonical narration and timestamped audio contracts for History V4.

The documentary script is the editorial source of truth.  Visual coverage
excerpts are cues only and must never be sent to ElevenLabs.  This module
keeps that boundary explicit, produces one continuous canonical narration,
and cuts the resulting audio into provider-sized windows without changing the
spoken take.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from content.video_engine.src.services.history_contracts import canonical_sha256


HISTORY_NARRATION_VERSION = "history_narration.v1"
CANONICAL_AUDIO_VERSION = "elevenlabs_canonical_audio.v1"
_HEX64 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class HistoryNarrationError(ValueError):
    """Raised when a narration or canonical audio artifact is unsafe."""

    def __init__(self, errors: Iterable[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors) or "invalid history narration artifact")


def _load(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HistoryNarrationError([f"{label} is not valid JSON: {exc}"]) from exc
    if not isinstance(payload, dict):
        raise HistoryNarrationError([f"{label} must contain an object"])
    return payload


def _normalise_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", value, flags=re.UNICODE))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _narration_hash(text: str) -> str:
    return hashlib.sha256(_normalise_text(text).encode("utf-8")).hexdigest()


def _word_timing(raw: Mapping[str, Any]) -> tuple[str, float, float]:
    word = str(raw.get("w") or raw.get("word") or "")
    start = raw.get("start_s", raw.get("start", 0.0))
    end = raw.get("end_s", raw.get("end", 0.0))
    try:
        start_s = float(start)
        end_s = float(end)
    except (TypeError, ValueError) as exc:
        raise HistoryNarrationError([f"invalid word timing for {word!r}"]) from exc
    if not word or start_s < 0 or end_s < start_s:
        raise HistoryNarrationError([f"invalid word timing for {word!r}"])
    return word, start_s, end_s


def _chunk_text(text: str, *, max_chars: int = 4200) -> list[str]:
    """Split long narration at whitespace without changing spoken text."""

    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    current_chars = 0
    for word in words:
        projected = current_chars + len(word) + (1 if current else 0)
        if current and projected > max_chars:
            chunks.append(" ".join(current))
            current = []
            current_chars = 0
        current.append(word)
        current_chars += len(word) + (1 if len(current) > 1 else 0)
    if current:
        chunks.append(" ".join(current))
    return chunks


def _concat_audio(paths: list[Path], target: Path) -> None:
    try:
        from pydub import AudioSegment
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise HistoryNarrationError(["pydub is required to concatenate canonical audio takes"]) from exc
    try:
        combined = AudioSegment.empty()
        for path in paths:
            combined += AudioSegment.from_file(path)
        combined.export(target, format="mp3")
    except Exception as exc:  # noqa: BLE001 - media decoder boundary
        raise HistoryNarrationError([f"unable to concatenate canonical audio takes: {exc}"]) from exc


def compile_history_narration(
    storyboard: Mapping[str, Any] | str | Path,
    *,
    source: Mapping[str, Any] | str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Compile canonical scene narration, optionally from an approved expansion.

    When ``source`` is omitted, one segment is emitted per storyboard scene.
    A supplied source may split a scene into editorial paragraphs, but every
    segment must retain a valid scene, chapter, claim, and citation boundary.
    The source's visual-beat excerpts are intentionally ignored.
    """

    storyboard_payload = _load(storyboard, "storyboard")
    scenes = storyboard_payload.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise HistoryNarrationError(["storyboard scenes must be a non-empty array"])
    scene_map: dict[int, Mapping[str, Any]] = {}
    for index, scene in enumerate(scenes):
        if not isinstance(scene, Mapping):
            raise HistoryNarrationError([f"storyboard scenes[{index}] must be an object"])
        try:
            scene_id = int(scene.get("scene_id"))
        except (TypeError, ValueError) as exc:
            raise HistoryNarrationError([f"storyboard scenes[{index}] has an invalid scene_id"]) from exc
        scene_map[scene_id] = scene

    if source is None:
        raw_segments: list[Mapping[str, Any]] = []
        for scene in scenes:
            raw_segments.append(
                {
                    "segment_id": f"scene-{int(scene['scene_id']):03d}",
                    "scene_id": int(scene["scene_id"]),
                    "chapter_id": str(scene.get("chapter_id") or ""),
                    "claim_refs": list(scene.get("claim_refs") or []),
                    "citation_refs": list(scene.get("citation_refs") or []),
                    "text": str(scene.get("narration_text") or ""),
                }
            )
        source_status = "storyboard_scene_narration"
        target_duration_s = None
        source_episode_id = ""
    else:
        source_payload = _load(source, "history narration source")
        raw_segments_value = source_payload.get("segments")
        if not isinstance(raw_segments_value, list) or not raw_segments_value:
            raise HistoryNarrationError(["history narration source segments must be a non-empty array"])
        raw_segments = [item for item in raw_segments_value if isinstance(item, Mapping)]
        if len(raw_segments) != len(raw_segments_value):
            raise HistoryNarrationError(["history narration source segments must contain objects"])
        source_status = str(source_payload.get("status") or "source_expansion")
        target_duration_s = source_payload.get("target_duration_s")
        source_episode_id = str(source_payload.get("episode_id") or "")

    segments: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    previous_scene_id = 0
    for index, raw in enumerate(raw_segments):
        segment_id = str(raw.get("segment_id") or "")
        if not _SAFE_ID.fullmatch(segment_id) or segment_id in seen_ids:
            raise HistoryNarrationError([f"segments[{index}].segment_id must be unique and safe"])
        try:
            scene_id = int(raw.get("scene_id"))
        except (TypeError, ValueError) as exc:
            raise HistoryNarrationError([f"segments[{index}].scene_id must be an integer"]) from exc
        scene = scene_map.get(scene_id)
        if scene is None:
            raise HistoryNarrationError([f"segments[{index}] references unknown scene {scene_id}"])
        if scene_id < previous_scene_id:
            raise HistoryNarrationError(["narration segments must remain in storyboard scene order"])
        previous_scene_id = scene_id
        text = _normalise_text(raw.get("text"))
        if not text:
            raise HistoryNarrationError([f"segments[{index}].text must be non-empty"])
        chapter_id = str(raw.get("chapter_id") or scene.get("chapter_id") or "")
        if chapter_id != str(scene.get("chapter_id") or ""):
            raise HistoryNarrationError([f"segments[{index}].chapter_id does not match scene {scene_id}"])
        claim_refs = [str(value) for value in (raw.get("claim_refs") or [])]
        citation_refs = [str(value) for value in (raw.get("citation_refs") or [])]
        seen_ids.add(segment_id)
        segments.append(
            {
                "segment_id": segment_id,
                "scene_id": scene_id,
                "chapter_id": chapter_id,
                "claim_refs": claim_refs,
                "citation_refs": citation_refs,
                "text": text,
                "word_count": _word_count(text),
                "char_count": len(text),
            }
        )

    full_text = " ".join(segment["text"] for segment in segments)
    core = {
        "schema_version": HISTORY_NARRATION_VERSION,
        "episode_id": source_episode_id
        or (
            str(storyboard_payload.get("channel", {}).get("series") or "history-of-bjj")
            + ":"
            + str(storyboard_payload.get("job_id") or "history-episode-1")
        ),
        "source_storyboard_hash": canonical_sha256(storyboard_payload),
        "base_narration_hash": _narration_hash(
            " ".join(str(scene.get("narration_text") or "") for scene in scenes)
        ),
        "research_hash": str(storyboard_payload.get("research_hash") or ""),
        "source_kind": source_status,
        "target_duration_s": float(target_duration_s) if target_duration_s not in (None, "") else None,
        "segments": segments,
        "full_text": full_text,
        "total_words": _word_count(full_text),
        "total_chars": len(full_text),
        "policy": {
            "canonical_text_owner": "storyboard_scene_narration",
            "visual_beat_excerpts_are_not_tts_input": True,
            "provider_audio_is_single_continuous_take": True,
            "research_claims_must_remain_cited": True,
        },
    }
    payload = {**core, "narration_hash": _narration_hash(full_text)}
    payload["artifact_hash"] = canonical_sha256(payload)
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def validate_history_narration(
    value: Mapping[str, Any] | str | Path,
    *,
    expected_storyboard_hash: str | None = None,
    expected_research_hash: str | None = None,
    min_words: int = 1,
) -> dict[str, Any]:
    payload = _load(value, "history narration")
    errors: list[str] = []
    if payload.get("schema_version") != HISTORY_NARRATION_VERSION:
        errors.append(f"schema_version must be {HISTORY_NARRATION_VERSION}")
    if expected_storyboard_hash and payload.get("source_storyboard_hash") != expected_storyboard_hash:
        errors.append("source_storyboard_hash is stale")
    if expected_research_hash and payload.get("research_hash") != expected_research_hash:
        errors.append("research_hash is stale")
    segments = payload.get("segments")
    if not isinstance(segments, list) or not segments:
        errors.append("segments must be a non-empty array")
        segments = []
    seen: set[str] = set()
    last_scene = 0
    texts: list[str] = []
    for index, raw in enumerate(segments):
        label = f"segments[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        segment_id = str(raw.get("segment_id") or "")
        if not _SAFE_ID.fullmatch(segment_id) or segment_id in seen:
            errors.append(f"{label}.segment_id must be unique and safe")
        seen.add(segment_id)
        try:
            scene_id = int(raw.get("scene_id"))
        except (TypeError, ValueError):
            errors.append(f"{label}.scene_id must be an integer")
            scene_id = last_scene
        if scene_id < last_scene:
            errors.append(f"{label} is out of scene order")
        last_scene = scene_id
        text = _normalise_text(raw.get("text"))
        if not text:
            errors.append(f"{label}.text must be non-empty")
        texts.append(text)
        for field in ("claim_refs", "citation_refs"):
            if not isinstance(raw.get(field), list) or not all(isinstance(item, str) for item in raw.get(field, [])):
                errors.append(f"{label}.{field} must be a string array")
    full_text = " ".join(texts)
    if _word_count(full_text) < min_words:
        errors.append(f"narration must contain at least {min_words} words")
    if payload.get("full_text") != full_text:
        errors.append("full_text does not match ordered segments")
    if int(payload.get("total_words") or 0) != _word_count(full_text):
        errors.append("total_words does not match narration")
    if int(payload.get("total_chars") or 0) != len(full_text):
        errors.append("total_chars does not match narration")
    if payload.get("narration_hash") != _narration_hash(full_text):
        errors.append("narration_hash is stale")
    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    actual_hash = canonical_sha256({key: value for key, value in payload.items() if key != "artifact_hash"})
    if declared_hash != actual_hash:
        errors.append("artifact_hash is stale")
    if errors:
        raise HistoryNarrationError(errors)
    return {**payload, "artifact_hash": actual_hash}


def _default_segmenter(
    source_audio: Path,
    windows: list[tuple[float, float]],
    output_dir: Path,
) -> list[Path]:
    try:
        from pydub import AudioSegment
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise HistoryNarrationError(["pydub is required to cut canonical audio blocks"]) from exc
    try:
        audio = AudioSegment.from_file(source_audio)
    except Exception as exc:  # noqa: BLE001 - media decoder boundary
        raise HistoryNarrationError([f"unable to decode canonical audio: {exc}"]) from exc
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, (start_s, end_s) in enumerate(windows, start=1):
        target = output_dir / f"audio_block_{index:03d}.mp3"
        clip = audio[int(round(start_s * 1000)) : int(round(end_s * 1000))]
        if len(clip) <= 0:
            raise HistoryNarrationError([f"audio block {index} is empty"])
        try:
            clip.export(target, format="mp3")
        except Exception as exc:  # noqa: BLE001 - media encoder boundary
            raise HistoryNarrationError([f"unable to write canonical audio block {index}: {exc}"]) from exc
        paths.append(target)
    return paths


def resolve_canonical_elevenlabs_audio(
    narration: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    manifest_path: str | Path | None = None,
    storyboard_hash: str = "",
    voice_id: str = "",
    allow_synthesis: bool = False,
    synthesizer: Any | None = None,
    synthesis_config: Any | None = None,
    segmenter: Callable[[Path, list[tuple[float, float]], Path], list[Path]] | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve one continuous episode take and deterministic ten-second slices."""

    narration_payload = validate_history_narration(narration)
    root = Path(job_root).resolve()
    voice_id = voice_id or (os.environ.get("ELEVENLABS_VOICE_ID") or "").strip()
    if manifest_path is not None and Path(manifest_path).is_file():
        existing = _load(manifest_path, "canonical ElevenLabs audio manifest")
        if (
            existing.get("status") == "ready"
            and existing.get("narration_hash") == narration_payload["narration_hash"]
            and (not storyboard_hash or existing.get("storyboard_hash") == storyboard_hash)
            and (not voice_id or existing.get("voice_id") == voice_id)
        ):
            return validate_canonical_audio(existing, job_root=root)
        if not allow_synthesis:
            raise HistoryNarrationError(["existing canonical audio does not match this narration/voice"])
    if not allow_synthesis:
        core = {
            "schema_version": CANONICAL_AUDIO_VERSION,
            "status": "awaiting_audio",
            "provider": "elevenlabs",
            "episode_id": narration_payload["episode_id"],
            "narration_hash": narration_payload["narration_hash"],
            "storyboard_hash": storyboard_hash,
            "voice_id": voice_id,
            "audio_path": "",
            "words_path": "",
            "duration_s": 0.0,
            "blocks": [],
            "policy": {"single_continuous_take": True, "provider_audio_is_canonical": True},
        }
        payload = {**core, "artifact_hash": canonical_sha256(core)}
        if output_path is not None:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    from content.video_engine.src.services.audio_synth import AudioSynthService, ElevenLabsConfig

    service = synthesizer or AudioSynthService()
    config = synthesis_config or getattr(service, "config", None) or ElevenLabsConfig.from_env()
    resolved_voice_id = voice_id or str(getattr(config, "voice_id", "") or "")
    if not resolved_voice_id:
        raise HistoryNarrationError(["an ElevenLabs voice ID is required before synthesis"])
    audio_dir = root / "audio" / "canonical"
    cache_dir = root / "audio" / ".cache"
    audio_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    (audio_dir / "takes").mkdir(parents=True, exist_ok=True)
    full_text = str(narration_payload["full_text"])
    take_texts = _chunk_text(full_text)
    take_results: list[Any] = []
    try:
        for take_index, take_text in enumerate(take_texts, start=1):
            take_results.append(
                service.synthesize_scene(
                    9000 + take_index,
                    take_text,
                    voice_id=resolved_voice_id,
                    settings={},
                    audio_dir=audio_dir / "takes",
                    cache_dir=cache_dir,
                    config=config,
                )
            )
    except Exception as exc:  # noqa: BLE001 - provider boundary
        raise HistoryNarrationError([f"ElevenLabs canonical synthesis failed: {exc}"]) from exc
    source_paths = [Path(result.audio_path) for result in take_results]
    word_paths = [Path(result.words_path) for result in take_results]
    if any(not path.is_file() for path in source_paths + word_paths):
        raise HistoryNarrationError(["ElevenLabs canonical synthesis did not produce audio and timings"])
    canonical_audio = audio_dir / "history_episode_1_master.mp3"
    canonical_words = audio_dir / "history_episode_1_master.words.json"
    words: list[dict[str, Any]] = []
    offsets = 0.0
    for result, words_path in zip(take_results, word_paths):
        words_payload = json.loads(words_path.read_text(encoding="utf-8"))
        raw_words = words_payload.get("words") if isinstance(words_payload, Mapping) else None
        if not isinstance(raw_words, list) or not raw_words:
            raise HistoryNarrationError(["canonical ElevenLabs timing artifact has no words"])
        for raw in raw_words:
            if not isinstance(raw, Mapping):
                raise HistoryNarrationError(["canonical word timings must contain objects"])
            word, start_s, end_s = _word_timing(raw)
            words.append(
                {
                    "w": word,
                    "start_s": round(offsets + start_s, 6),
                    "end_s": round(offsets + end_s, 6),
                }
            )
        offsets += float(result.duration_s)
    if len(source_paths) == 1:
        canonical_audio.write_bytes(source_paths[0].read_bytes())
    else:
        _concat_audio(source_paths, canonical_audio)
    duration_s = max(offsets, max(word["end_s"] for word in words))
    canonical_words.write_text(
        json.dumps({"duration_s": duration_s, "words": words}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    block_count = max(1, math.ceil(duration_s / 10.0))
    windows = [(index * 10.0, min((index + 1) * 10.0, duration_s)) for index in range(block_count)]
    block_paths = (segmenter or _default_segmenter)(canonical_audio, windows, audio_dir / "blocks")
    if len(block_paths) != block_count:
        raise HistoryNarrationError(["audio segmenter returned the wrong block count"])
    block_records: list[dict[str, Any]] = []
    for index, ((start_s, end_s), block_path) in enumerate(zip(windows, block_paths), start=1):
        resolved = Path(block_path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise HistoryNarrationError([f"audio block {index} escaped the job root"]) from exc
        selected_words: list[dict[str, Any]] = []
        for word in words:
            midpoint = (float(word["start_s"]) + float(word["end_s"])) / 2.0
            if start_s <= midpoint < end_s or (index == block_count and midpoint <= end_s):
                selected_words.append(
                    {
                        "w": word["w"],
                        "start_s": round(max(0.0, word["start_s"] - start_s), 6),
                        "end_s": round(max(0.0, min(end_s, word["end_s"]) - start_s), 6),
                    }
                )
        block_records.append(
            {
                "audio_block_id": f"audio-block-{index:03d}",
                "order": index,
                "start_s": round(start_s, 6),
                "end_s": round(end_s, 6),
                "audio_path": resolved.relative_to(root).as_posix(),
                "sha256": _sha256(resolved),
                "duration_s": round(end_s - start_s, 6),
                "word_timings": selected_words,
            }
        )
    core = {
        "schema_version": CANONICAL_AUDIO_VERSION,
        "status": "ready",
        "provider": "elevenlabs",
        "episode_id": narration_payload["episode_id"],
        "narration_hash": narration_payload["narration_hash"],
        "storyboard_hash": storyboard_hash,
        "voice_id": resolved_voice_id,
        "audio_path": canonical_audio.relative_to(root).as_posix(),
        "audio_sha256": _sha256(canonical_audio),
        "words_path": canonical_words.relative_to(root).as_posix(),
        "duration_s": round(duration_s, 6),
        "blocks": block_records,
        "cache_hit": all(bool(result.cache_hit) for result in take_results),
        "take_count": len(take_results),
        "cost_usd": round(sum(float(result.cost_usd) for result in take_results), 8),
        "policy": {
            "single_continuous_take": True,
            "provider_audio_is_canonical": True,
            "visual_coverage_excerpts_are_never_spoken": True,
            "provider_audio_is_disabled_for_video_generation": True,
        },
    }
    payload = {**core, "artifact_hash": canonical_sha256(core)}
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def validate_canonical_audio(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_narration_hash: str | None = None,
    expected_storyboard_hash: str | None = None,
    expected_voice_id: str | None = None,
) -> dict[str, Any]:
    payload = _load(value, "canonical ElevenLabs audio")
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != CANONICAL_AUDIO_VERSION:
        errors.append(f"schema_version must be {CANONICAL_AUDIO_VERSION}")
    if payload.get("provider") != "elevenlabs":
        errors.append("provider must be elevenlabs")
    if payload.get("status") not in {"awaiting_audio", "ready"}:
        errors.append("status must be awaiting_audio or ready")
    if expected_narration_hash and payload.get("narration_hash") != expected_narration_hash:
        errors.append("narration_hash is stale")
    if expected_storyboard_hash and payload.get("storyboard_hash") != expected_storyboard_hash:
        errors.append("storyboard_hash is stale")
    if expected_voice_id and payload.get("voice_id") != expected_voice_id:
        errors.append("voice_id is stale")
    if payload.get("status") == "ready":
        for field in ("audio_path", "words_path"):
            path_text = str(payload.get(field) or "")
            try:
                resolved = (root / path_text).resolve(strict=True)
                resolved.relative_to(root)
            except (OSError, RuntimeError, ValueError):
                errors.append(f"{field} must resolve inside the job")
                continue
            if field == "audio_path":
                digest = str(payload.get("audio_sha256") or "").casefold()
                if not _HEX64.fullmatch(digest) or _sha256(resolved) != digest:
                    errors.append("audio_sha256 is missing or stale")
        blocks = payload.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            errors.append("ready canonical audio requires blocks")
            blocks = []
        previous_end = 0.0
        for index, raw in enumerate(blocks, start=1):
            label = f"blocks[{index - 1}]"
            if not isinstance(raw, Mapping):
                errors.append(f"{label} must be an object")
                continue
            if int(raw.get("order") or 0) != index:
                errors.append(f"{label}.order must be {index}")
            start_s = float(raw.get("start_s") or 0)
            end_s = float(raw.get("end_s") or 0)
            if start_s < previous_end - 0.001 or end_s <= start_s:
                errors.append(f"{label} window is not contiguous")
            previous_end = end_s
            path_text = str(raw.get("audio_path") or "")
            try:
                resolved = (root / path_text).resolve(strict=True)
                resolved.relative_to(root)
            except (OSError, RuntimeError, ValueError):
                errors.append(f"{label}.audio_path must resolve inside the job")
                continue
            digest = str(raw.get("sha256") or "").casefold()
            if not _HEX64.fullmatch(digest) or _sha256(resolved) != digest:
                errors.append(f"{label}.sha256 is missing or stale")
    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    actual_hash = canonical_sha256({key: value for key, value in payload.items() if key != "artifact_hash"})
    if declared_hash != actual_hash:
        errors.append("artifact_hash is stale")
    if errors:
        raise HistoryNarrationError(errors)
    return {**payload, "artifact_hash": actual_hash}


__all__ = [
    "CANONICAL_AUDIO_VERSION",
    "HISTORY_NARRATION_VERSION",
    "HistoryNarrationError",
    "compile_history_narration",
    "resolve_canonical_elevenlabs_audio",
    "validate_canonical_audio",
    "validate_history_narration",
]
