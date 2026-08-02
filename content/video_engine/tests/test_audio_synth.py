from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from content.video_engine.src.models import StageContext, VideoRun
from content.video_engine.src.services.audio_synth import (
    AlignmentError,
    AudioSynthService,
    AudioSynthesisError,
    ElevenLabsConfig,
    ELEVENLABS_RATE_PER_CHARACTER_USD,
    group_word_timings,
)


def _alignment(text: str, *, start: float = 0.0, step: float = 0.1) -> dict:
    characters = list(text)
    starts = [start + index * step for index in range(len(characters))]
    ends = [value + step for value in starts]
    return {
        "characters": characters,
        "character_start_times_seconds": starts,
        "character_end_times_seconds": ends,
    }


def _response(text: str, *, audio: bytes = b"ID3-mock") -> tuple[int, dict]:
    return 200, {
        "audio_base64": base64.b64encode(audio).decode("ascii"),
        "alignment": _alignment(text),
    }


def _storyboard(*texts: str) -> dict:
    return {
        "global_settings": {
            "voice": {
                "provider": "elevenlabs",
                "voice_id": "VOICE_TEST",
                "settings": {"stability": 0.5, "similarity_boost": 0.75},
            }
        },
        "scenes": [
            {"scene_id": index, "narration_text": text}
            for index, text in enumerate(texts, start=1)
        ],
    }


def _config() -> ElevenLabsConfig:
    return ElevenLabsConfig(api_key="test-key", retry_backoff_s=0.0)


def test_config_requires_api_key_only_when_loaded_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
        ElevenLabsConfig.from_env()

    monkeypatch.setenv("ELEVENLABS_API_KEY", "env-key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "env-voice")
    config = ElevenLabsConfig.from_env()
    assert config.api_key == "env-key"
    assert config.voice_id == "env-voice"


def test_group_word_timings_handles_multi_space_punctuation_and_unicode() -> None:
    narration = "  Keep  hips—forward, then tap!  "
    words, duration = group_word_timings(narration, _alignment(narration, step=0.05))

    assert [word["w"] for word in words] == ["Keep", "hips—forward,", "then", "tap!"]
    assert words[0]["start_s"] == 0.1
    assert words[-1]["end_s"] < duration  # trailing provider whitespace may carry silence
    assert duration == pytest.approx(len(narration) * 0.05)


def test_group_word_timings_rejects_alignment_text_drift() -> None:
    with pytest.raises(AlignmentError, match="does not match narration"):
        group_word_timings("Correct text", _alignment("Different text"))


def test_synthesizes_each_scene_writes_mp3_and_words_and_reports_cost(tmp_path: Path) -> None:
    calls: list[dict] = []

    def post(url: str, *, headers: dict, payload: dict, timeout: float):
        calls.append({"url": url, "headers": headers, "payload": payload, "timeout": timeout})
        return _response(payload["text"], audio=b"ID3-scene")

    service = AudioSynthService(_config(), request_fn=post)
    summary = service.synthesize_storyboard(
        _storyboard("Break posture.", "Keep the wrist."), tmp_path
    )

    assert len(calls) == 2
    assert "/text-to-speech/VOICE_TEST/with-timestamps?" in calls[0]["url"]
    assert "output_format=mp3_44100_128" in calls[0]["url"]
    assert "output_format" not in calls[0]["payload"]
    assert calls[0]["headers"]["xi-api-key"] == "test-key"
    assert summary["scene_count"] == 2
    assert summary["cache_hits"] == 0
    assert summary["total_chars"] == len("Break posture.") + len("Keep the wrist.")
    assert summary["cost_usd"] == pytest.approx(
        summary["total_chars"] * ELEVENLABS_RATE_PER_CHARACTER_USD
    )
    assert (tmp_path / "audio/scene_1.mp3").read_bytes() == b"ID3-scene"
    words = json.loads((tmp_path / "audio/scene_1.words.json").read_text())
    assert words["scene_id"] == 1
    assert [item["w"] for item in words["words"]] == ["Break", "posture."]


def test_cache_hit_skips_provider_and_preserves_artifacts(tmp_path: Path) -> None:
    calls = 0

    def post(*args, **kwargs):
        nonlocal calls
        calls += 1
        return _response(kwargs["payload"]["text"])

    service = AudioSynthService(_config(), request_fn=post)
    storyboard = _storyboard("Cache this scene.")
    first = service.synthesize_storyboard(storyboard, tmp_path)
    second = service.synthesize_storyboard(storyboard, tmp_path)

    assert calls == 1
    assert first["cache_hits"] == 0
    assert second["cache_hits"] == 1
    assert second["cost_usd"] == 0.0
    assert (tmp_path / "audio/scene_1.mp3").exists()
    assert json.loads((tmp_path / "audio/scene_1.words.json").read_text())["words"]


def test_incomplete_cache_fails_closed_instead_of_fabricating_timings(
    tmp_path: Path,
) -> None:
    service = AudioSynthService(_config(), request_fn=lambda *args, **kwargs: _response("unused"))
    storyboard = _storyboard("Cache without timings.")
    voice = storyboard["global_settings"]["voice"]
    from content.video_engine.src.services.audio_synth import _cache_key

    cache_dir = tmp_path / "audio" / ".cache"
    cache_dir.mkdir(parents=True)
    cache_hash = _cache_key(voice["voice_id"], "Cache without timings.", voice["settings"])
    cache_dir.joinpath(f"{cache_hash}.mp3").write_bytes(b"ID3-incomplete")

    with pytest.raises(AudioSynthesisError, match="word-timing sidecar"):
        service.synthesize_storyboard(storyboard, tmp_path)


def test_cache_hit_rejects_word_timings_for_different_narration(
    tmp_path: Path,
) -> None:
    narration = "Cache this exact narration."
    service = AudioSynthService(
        _config(),
        request_fn=lambda *args, **kwargs: _response(kwargs["payload"]["text"]),
    )
    storyboard = _storyboard(narration)
    service.synthesize_storyboard(storyboard, tmp_path)

    from content.video_engine.src.services.audio_synth import _cache_key

    voice = storyboard["global_settings"]["voice"]
    cache_hash = _cache_key(voice["voice_id"], narration, voice["settings"])
    stale = {
        "scene_id": 1,
        "duration_s": 1.0,
        "words": [{"w": "Different"}, {"w": "narration."}],
    }
    (tmp_path / "audio" / "scene_1.words.json").write_text(
        json.dumps(stale),
        encoding="utf-8",
    )
    (tmp_path / "audio" / ".cache" / f"{cache_hash}.words.json").write_text(
        json.dumps(stale),
        encoding="utf-8",
    )

    with pytest.raises(AudioSynthesisError, match="word-timing sidecar"):
        service.synthesize_storyboard(storyboard, tmp_path)


def test_retries_transient_5xx_and_timeout_with_exponential_backoff(tmp_path: Path) -> None:
    responses: list[object] = [
        (503, {"error": "busy"}),
        TimeoutError("slow"),
        _response("Try again.", audio=b"final"),
    ]
    sleeps: list[float] = []

    def post(*args, **kwargs):
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    service = AudioSynthService(
        _config(),
        request_fn=post,
        sleep_fn=sleeps.append,
    )
    summary = service.synthesize_storyboard(_storyboard("Try again."), tmp_path)

    assert summary["cache_hits"] == 0
    assert sleeps == [0.0, 0.0]


def test_four_hundred_failure_is_not_retried(tmp_path: Path) -> None:
    calls = 0

    def post(*args, **kwargs):
        nonlocal calls
        calls += 1
        return 401, {"detail": "bad key"}

    service = AudioSynthService(_config(), request_fn=post)
    with pytest.raises(AudioSynthesisError, match="HTTP 401"):
        service.synthesize_storyboard(_storyboard("Do not call again."), tmp_path)
    assert calls == 1


def test_run_stage_loads_job_storyboard_and_returns_stage_output(tmp_path: Path) -> None:
    storyboard = _storyboard("Run the stage.")
    (tmp_path / "storyboard.json").write_text(json.dumps(storyboard), encoding="utf-8")

    service = AudioSynthService(
        _config(),
        request_fn=lambda *args, **kwargs: _response(kwargs["payload"]["text"]),
    )
    job = VideoRun(source_ref="unused.json")
    context = StageContext(repository=object(), configs={}, job_dir=tmp_path)
    output = service.run_stage(job, context)

    assert output.summary["scene_count"] == 1
