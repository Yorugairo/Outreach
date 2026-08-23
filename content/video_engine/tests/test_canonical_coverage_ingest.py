from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.canonical_coverage_ingest import (
    CanonicalIngestError,
    compile_canonical_coverage,
    flatten_word_timings,
    ingest_canonical_audio,
    reconcile_read_against_script,
    validate_canonical_audio,
)
from content.video_engine.src.services.director import validate_director_proposal
from content.video_engine.src.services.provisional_coverage import (
    ProvisionalCoverageError,
    assert_render_ready,
    compile_provisional_coverage,
)
from content.video_engine.tests.conftest import build_proposal

SCRIPT_WORDS = None


def _words_for(text: str, *, step: float = 0.4) -> list[dict]:
    return [
        {"w": word, "start_s": round(i * step, 3), "end_s": round(i * step + step * 0.8, 3)}
        for i, word in enumerate(text.split())
    ]


def _audio(text: str, *, status: str = "ready", block_size: int = 8, step: float = 0.4) -> dict:
    words = _words_for(text, step=step)
    blocks = []
    for order, start in enumerate(range(0, len(words), block_size), start=1):
        chunk = words[start : start + block_size]
        blocks.append(
            {
                "order": order,
                "start_s": chunk[0]["start_s"],
                "end_s": chunk[-1]["end_s"],
                "audio_path": f"audio/blocks/{order:03d}.mp3",
                "sha256": "c" * 64,
                "duration_s": round(chunk[-1]["end_s"] - chunk[0]["start_s"], 3),
                "word_timings": chunk,
            }
        )
    return {
        "schema_version": "elevenlabs_canonical_audio.v1",
        "status": status,
        "provider": "elevenlabs",
        "episode_id": "test:ep1",
        "narration_hash": "d" * 64,
        "voice_id": "LMNWDJCqXz0WdUKd2FE1",
        "audio_path": "audio/canonical/master.mp3",
        "words_path": "audio/canonical/master.words.json",
        "duration_s": round(words[-1]["end_s"], 3),
        "blocks": blocks,
    }


@pytest.fixture()
def estimated(paste_brief):
    proposal = validate_director_proposal(build_proposal(paste_brief), brief=paste_brief)
    return compile_provisional_coverage(proposal, brief=paste_brief)


@pytest.fixture()
def audio(paste_brief):
    return _audio(paste_brief["script"]["text"])


def test_estimated_coverage_is_refused_for_render(estimated):
    with pytest.raises(ProvisionalCoverageError):
        assert_render_ready(estimated)


def test_ingest_flips_timing_basis_to_canonical(estimated, audio, paste_brief):
    canonical = compile_canonical_coverage(estimated, audio=audio, brief=paste_brief)

    assert canonical["timing_basis"] == "canonical"
    assert_render_ready(canonical)


def test_duration_comes_from_the_audio_not_word_count(estimated, audio, paste_brief):
    canonical = compile_canonical_coverage(estimated, audio=audio, brief=paste_brief)

    assert canonical["duration_s"] == audio["duration_s"]
    assert canonical["duration_s"] != estimated["duration_s"]


def test_slot_boundaries_are_measured_not_estimated(estimated, audio, paste_brief):
    canonical = compile_canonical_coverage(estimated, audio=audio, brief=paste_brief)

    for slot in canonical["slots"]:
        assert "measured_start_s" in slot
        assert "measured_end_s" in slot
        assert slot["measured_end_s"] >= slot["measured_start_s"]
    starts = [slot["measured_start_s"] for slot in canonical["slots"]]
    assert starts == sorted(starts), "slots must advance monotonically through the audio"


def test_the_estimated_artifact_is_not_mutated(estimated, audio, paste_brief):
    before = json.dumps(estimated, sort_keys=True)
    compile_canonical_coverage(estimated, audio=audio, brief=paste_brief)

    assert json.dumps(estimated, sort_keys=True) == before


def test_a_rewritten_read_is_rejected_not_retimed(estimated, paste_brief):
    drifted = _audio(
        paste_brief["script"]["text"].replace("exhaustion", "fatigue", 1)
    )

    with pytest.raises(CanonicalIngestError) as excinfo:
        compile_canonical_coverage(estimated, audio=drifted, brief=paste_brief)

    joined = " ".join(excinfo.value.errors)
    assert "diverges from the attested script" in joined
    assert "re-attested" in joined


def test_a_truncated_read_is_rejected(estimated, paste_brief):
    text = " ".join(paste_brief["script"]["text"].split()[:-6])

    with pytest.raises(CanonicalIngestError) as excinfo:
        compile_canonical_coverage(estimated, audio=_audio(text), brief=paste_brief)

    assert any("stops" in error and "short" in error for error in excinfo.value.errors)


def test_an_extended_read_is_rejected(estimated, paste_brief):
    text = paste_brief["script"]["text"] + " And that is the whole story."

    with pytest.raises(CanonicalIngestError) as excinfo:
        compile_canonical_coverage(estimated, audio=_audio(text), brief=paste_brief)

    assert any("beyond the attested script" in error for error in excinfo.value.errors)


def test_audio_not_ready_is_refused(estimated, paste_brief):
    pending = _audio(paste_brief["script"]["text"], status="awaiting_audio")

    with pytest.raises(CanonicalIngestError) as excinfo:
        validate_canonical_audio(pending)

    assert any("requires 'ready'" in error for error in excinfo.value.errors)


def test_slot_overruns_are_reported_not_clamped(estimated, paste_brief, tmp_path):
    # A slow read pushes slots past the 8s coverage cap.
    slow = _audio(paste_brief["script"]["text"], step=1.6)
    summary = ingest_canonical_audio(
        estimated, audio=slow, brief=paste_brief, output_dir=tmp_path / "job"
    )
    canonical = json.loads(Path(summary["coverage_path"]).read_text(encoding="utf-8"))

    assert summary["overrun_count"] > 0
    assert any("over the 8.0s coverage cap" in item for item in summary["overruns"])
    assert any(slot["duration_s"] > 8.0 for slot in canonical["slots"]), (
        "measured duration must survive; clamping would desync the plate from the voice"
    )


def test_block_relative_timings_are_offset_to_absolute():
    audio = {
        "blocks": [
            {"order": 1, "start_s": 0.0, "word_timings": [{"w": "a", "start_s": 0.0, "end_s": 0.5}]},
            {"order": 2, "start_s": 10.0, "word_timings": [{"w": "b", "start_s": 0.0, "end_s": 0.5}]},
        ]
    }

    words = flatten_word_timings(audio)

    assert [w["start_s"] for w in words] == [0.0, 10.0]


def test_absolute_timings_are_left_alone():
    audio = {
        "blocks": [
            {"order": 1, "start_s": 0.0, "word_timings": [{"w": "a", "start_s": 0.0, "end_s": 0.5}]},
            {"order": 2, "start_s": 10.0, "word_timings": [{"w": "b", "start_s": 10.0, "end_s": 10.5}]},
        ]
    }

    assert [w["start_s"] for w in flatten_word_timings(audio)] == [0.0, 10.0]


def test_reconciliation_ignores_punctuation_and_case():
    words = [{"w": "The"}, {"w": "market,"}, {"w": "again."}]

    assert reconcile_read_against_script(words, "the market again") == []


def test_ingest_writes_canonical_beside_the_estimate(estimated, audio, paste_brief, tmp_path):
    job = tmp_path / "job"
    summary = ingest_canonical_audio(
        estimated, audio=audio, brief=paste_brief, output_dir=job
    )

    assert Path(summary["coverage_path"]).name == "canonical_coverage.json"
    assert summary["timing_basis"] == "canonical"
    assert summary["slot_count"] == estimated["slot_count"]
