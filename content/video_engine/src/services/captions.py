from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


@dataclass(slots=True, frozen=True)
class CaptionCue:
    start_s: float
    end_s: float
    text: str


def group_words(
    words: list[dict[str, Any]],
    *,
    max_words: int,
    split_gap_s: float = 0.08,
    offset_s: float = 0.0,
) -> list[CaptionCue]:
    cues: list[CaptionCue] = []
    current: list[dict[str, Any]] = []
    for word in words:
        if current:
            gap = float(word["start_s"]) - float(current[-1]["end_s"])
            if len(current) >= max_words or gap >= split_gap_s:
                cues.append(_cue(current, offset_s))
                current = []
        current.append(word)
    if current:
        cues.append(_cue(current, offset_s))
    return cues


def _cue(words: list[dict[str, Any]], offset_s: float) -> CaptionCue:
    return CaptionCue(
        start_s=offset_s + float(words[0]["start_s"]),
        end_s=offset_s + float(words[-1]["end_s"]),
        text=" ".join(str(word["w"]) for word in words),
    )


def _srt_timestamp(seconds: float) -> str:
    milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def write_srt(cues: list[CaptionCue], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    blocks = [
        (
            f"{index}\n"
            f"{_srt_timestamp(cue.start_s)} --> {_srt_timestamp(cue.end_s)}\n"
            f"{cue.text}"
        )
        for index, cue in enumerate(cues, start=1)
    ]
    output.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    return output


def ffmpeg_subtitle_filter(path: str | Path, *, margin_v: int = 220) -> str:
    normalized = Path(path).resolve().as_posix()
    escaped = normalized.replace(":", r"\:").replace("'", r"\'")
    return (
        f"subtitles=filename='{escaped}':"
        f"force_style='Alignment=2,MarginV={int(margin_v)}'"
    )


class CaptionService:
    def __init__(
        self,
        *,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ):
        self._runner = runner

    def build_cues(
        self,
        storyboard: dict[str, Any],
        words_dir: str | Path,
        *,
        target: str,
    ) -> list[CaptionCue]:
        max_words = 3 if target == "vertical" else 7
        offset_s = 0.0
        cues: list[CaptionCue] = []
        words_root = Path(words_dir)
        for scene in storyboard["scenes"]:
            scene_id = int(scene["scene_id"])
            payload = json.loads(
                words_root.joinpath(f"scene_{scene_id}.words.json").read_text(
                    encoding="utf-8"
                )
            )
            cues.extend(
                group_words(
                    list(payload["words"]),
                    max_words=max_words,
                    offset_s=offset_s,
                )
            )
            offset_s += float(payload["duration_s"])
            offset_s += float(scene.get("timing", {}).get("padding_s", 0.0))
        return cues

    def burn(
        self,
        input_path: str | Path,
        srt_path: str | Path,
        output_path: str | Path,
        *,
        margin_v: int = 220,
    ) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(Path(input_path)),
            "-vf",
            ffmpeg_subtitle_filter(srt_path, margin_v=margin_v),
            "-c:v",
            "libx264",
            "-c:a",
            "copy",
            str(output),
        ]
        self._runner(command, check=True, capture_output=True, text=True)
        return output

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        storyboard = json.loads(
            ctx.job_dir.joinpath("storyboard.json").read_text(encoding="utf-8")
        )
        captions_dir = ctx.job_dir / "captions"
        generated: list[str] = []
        for target in storyboard["global_settings"]["targets"]:
            cues = self.build_cues(storyboard, ctx.job_dir / "audio", target=target)
            srt_path = write_srt(cues, captions_dir / f"{target}.srt")
            generated.append(srt_path.relative_to(ctx.job_dir).as_posix())
            if target == "vertical":
                final_path = ctx.job_dir / "video" / "vertical_final" / "final.mp4"
                if final_path.exists():
                    burned_path = final_path.with_name("final_captioned.mp4")
                    self.burn(final_path, srt_path, burned_path)
                    burned_path.replace(final_path)
        return StageOutput(
            {
                "caption_paths": generated,
                "cost_usd": 0.0,
            }
        )
