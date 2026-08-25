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
    compile_pause_marks,
    group_word_timings,
    strip_pause_markup,
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


# --- TTS delivery standards (doc 37): pause marks, stitching, payload params ---


def test_compile_pause_marks_translates_and_strip_recovers_clean_text() -> None:
    text = "The peak. [post-key] And here is why. [pre-key] The number."
    compiled = compile_pause_marks(text)

    assert '<break time="1.2s" />' in compiled
    assert '<break time="0.6s" />' in compiled
    assert "[post-key]" not in compiled and "[pre-key]" not in compiled
    assert strip_pause_markup(compiled) == "The peak. And here is why. The number."
    assert strip_pause_markup(text) == "The peak. And here is why. The number."


def test_compile_pause_marks_warns_when_ration_exceeded(
    caplog: pytest.LogCaptureFixture,
) -> None:
    import logging

    text = "A. [pre-key] B. [pre-key] C. [pre-key] D. [pre-key] E."
    with caplog.at_level(logging.WARNING):
        compiled = compile_pause_marks(text)
    assert compiled.count("<break") == 4
    assert any("break" in record.message.lower() for record in caplog.records)


def test_pause_marks_reach_provider_but_never_the_word_timings(tmp_path: Path) -> None:
    sent: dict = {}

    def post(url: str, *, headers: dict, payload: dict, timeout: float):
        sent["payload"] = payload
        return _response(payload["text"])

    service = AudioSynthService(_config(), request_fn=post)
    service.synthesize_storyboard(
        _storyboard("Watch the gap. [post-key] It closes."), tmp_path
    )

    assert '<break time="1.2s" />' in sent["payload"]["text"]
    words = json.loads((tmp_path / "audio/scene_1.words.json").read_text())
    tokens = [word["w"] for word in words["words"]]
    assert tokens == ["Watch", "the", "gap.", "It", "closes."]


def test_editorial_flags_never_reach_the_provider_or_captions(tmp_path: Path) -> None:
    sent: dict = {}

    def post(url: str, *, headers: dict, payload: dict, timeout: float):
        sent["payload"] = payload
        return _response(payload["text"])

    service = AudioSynthService(_config(), request_fn=post)
    service.synthesize_storyboard(
        _storyboard("Order books are sold out [verify]. Prices climbed [check-me] all year."),
        tmp_path,
    )

    assert "[verify]" not in sent["payload"]["text"]
    assert "[check-me]" not in sent["payload"]["text"]
    words = json.loads((tmp_path / "audio/scene_1.words.json").read_text())
    assert all("verify" not in word["w"] for word in words["words"])


def test_alignment_fallback_when_provider_strips_break_tags(tmp_path: Path) -> None:
    def post(url: str, *, headers: dict, payload: dict, timeout: float):
        return _response(strip_pause_markup(payload["text"]))

    service = AudioSynthService(_config(), request_fn=post)
    service.synthesize_storyboard(_storyboard("Hold it. [pre-key] Now look."), tmp_path)

    words = json.loads((tmp_path / "audio/scene_1.words.json").read_text())
    assert [word["w"] for word in words["words"]] == ["Hold", "it.", "Now", "look."]


def test_request_stitching_chains_at_most_three_request_ids(tmp_path: Path) -> None:
    calls: list[dict] = []

    def post(url: str, *, headers: dict, payload: dict, timeout: float):
        calls.append(payload)
        status, body = _response(payload["text"])
        return status, body, {"request-id": f"req-{len(calls)}"}

    service = AudioSynthService(_config(), request_fn=post)
    summary = service.synthesize_storyboard(
        _storyboard("One.", "Two.", "Three.", "Four.", "Five."), tmp_path
    )

    assert "previous_request_ids" not in calls[0]
    assert calls[1]["previous_request_ids"] == ["req-1"]
    assert calls[4]["previous_request_ids"] == ["req-2", "req-3", "req-4"]
    assert summary["scenes"][0]["request_id"] == "req-1"
    words = json.loads((tmp_path / "audio/scene_1.words.json").read_text())
    assert words["request_id"] == "req-1"


def test_payload_carries_normalization_seed_and_dictionaries(tmp_path: Path) -> None:
    seen: dict = {}

    def post(url: str, *, headers: dict, payload: dict, timeout: float):
        seen["payload"] = payload
        return _response(payload["text"])

    config = ElevenLabsConfig(
        api_key="test-key",
        retry_backoff_s=0.0,
        seed=42,
        pronunciation_dictionary_locators=(
            {"pronunciation_dictionary_id": "dict-1", "version_id": "v1"},
        ),
    )
    service = AudioSynthService(config, request_fn=post)
    service.synthesize_storyboard(_storyboard("Numbers ahead."), tmp_path)

    payload = seen["payload"]
    assert payload["apply_text_normalization"] == "on"
    assert payload["seed"] == 42
    assert payload["pronunciation_dictionary_locators"] == [
        {"pronunciation_dictionary_id": "dict-1", "version_id": "v1"}
    ]


def test_more_than_three_pronunciation_dictionaries_rejected(tmp_path: Path) -> None:
    config = ElevenLabsConfig(
        api_key="test-key",
        pronunciation_dictionary_locators=tuple(
            {"pronunciation_dictionary_id": f"dict-{index}", "version_id": "v"}
            for index in range(4)
        ),
    )
    service = AudioSynthService(config, request_fn=lambda *a, **k: _response("x"))
    with pytest.raises(RuntimeError, match="at most 3"):
        service.synthesize_storyboard(_storyboard("Hi there."), tmp_path)


def test_cache_hit_with_pause_marks_compares_stripped_narration(tmp_path: Path) -> None:
    def post(url: str, *, headers: dict, payload: dict, timeout: float):
        return _response(payload["text"])

    service = AudioSynthService(_config(), request_fn=post)
    board = _storyboard("Steady now. [post-key] Breathe.")
    service.synthesize_storyboard(board, tmp_path)

    def fail_post(*args, **kwargs):
        raise AssertionError("provider must not be called on a cache hit")

    cached_service = AudioSynthService(_config(), request_fn=fail_post)
    summary = cached_service.synthesize_storyboard(board, tmp_path)
    assert summary["cache_hits"] == 1
