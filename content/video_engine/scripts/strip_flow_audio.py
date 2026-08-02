"""Strip provider-generated audio from Flow clips for post-owned sound design.

The raw provider output remains evidence. This utility writes a separate, atomically
replaced MP4 containing the first video stream only; narration, captions, credits,
and the project's own audio inserts are added later by the local editor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence


class AudioStripError(RuntimeError):
    """Raised when a clip cannot be sanitized safely."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_audio(
    input_path: str | Path,
    output_path: str | Path,
    *,
    ffmpeg: str = "ffmpeg",
) -> dict[str, object]:
    """Copy the first video stream without any audio, then return audit metadata."""

    source = Path(input_path).resolve()
    destination = Path(output_path).resolve()
    if not source.is_file():
        raise AudioStripError(f"input clip does not exist: {source}")
    if source == destination:
        raise AudioStripError("input and output must be different paths")
    destination.parent.mkdir(parents=True, exist_ok=True)

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.stem}.",
        suffix=destination.suffix or ".mp4",
        dir=destination.parent,
    )
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        command: Sequence[str] = (
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-c:v",
            "copy",
            "-an",
            "-movflags",
            "+faststart",
            str(temporary),
        )
        try:
            completed = subprocess.run(
                list(command),
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            raise AudioStripError(f"could not execute ffmpeg: {exc}") from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            raise AudioStripError(
                f"ffmpeg failed with exit code {completed.returncode}: {detail}"
            )
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise AudioStripError("ffmpeg produced no output clip")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)

    return {
        "input_path": str(source),
        "output_path": str(destination),
        "input_sha256": sha256(source),
        "output_sha256": sha256(destination),
        "audio_policy": "strip_provider_audio_in_post",
        "video_stream_policy": "copy_first_video_stream",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    print(
        json.dumps(
            strip_audio(args.input, args.output, ffmpeg=args.ffmpeg),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
