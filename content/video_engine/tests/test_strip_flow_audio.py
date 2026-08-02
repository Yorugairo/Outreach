from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from content.video_engine.scripts.strip_flow_audio import (
    AudioStripError,
    strip_audio,
)


def test_strip_audio_copies_video_only_and_returns_hashes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "raw.mp4"
    destination = tmp_path / "review.mp4"
    source.write_bytes(b"raw-flow-output")

    def fake_run(command, **kwargs):
        del kwargs
        Path(command[-1]).write_bytes(b"video-only-output")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(
        "content.video_engine.scripts.strip_flow_audio.subprocess.run",
        fake_run,
    )

    result = strip_audio(source, destination)

    assert destination.read_bytes() == b"video-only-output"
    assert result["input_sha256"]
    assert result["output_sha256"]
    assert result["audio_policy"] == "strip_provider_audio_in_post"


def test_strip_audio_rejects_in_place_rewrite(tmp_path: Path) -> None:
    source = tmp_path / "raw.mp4"
    source.write_bytes(b"raw-flow-output")

    with pytest.raises(AudioStripError, match="different paths"):
        strip_audio(source, source)
