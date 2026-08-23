#!/usr/bin/env python3
"""Build the deterministic inputs for the Autopilot / ElevenLabs recut.

The supplied ``.elevenlabs-audio.mp4`` is the visual source.  Its picture was
cut to the prior narration cadence, while the accompanying ElevenLabs MP3
contains a longer, revised narration.  This builder aligns each sentence in
the new narration to the matching source words, retimes the source picture,
and emits JSON props for the Remotion overlay composition.

The one inserted sentence has no source words.  It is represented as a
deliberate still plate so the Remotion Ken Burns bit can animate it rather
than leaving an unrelated source scene under the new line.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


# scripts/ -> video_engine/ -> content/ -> repository root
ROOT = Path(__file__).resolve().parents[3]
EDITOR = ROOT / "content" / "video_engine" / "editor"
PUBLIC_DIR = EDITOR / "public" / "autopilot-elevenlabs-recut-v1"
PROJECT_DIR = (
    ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "autopilot-illusion"
    / "elevenlabs-recut-v1"
)
RENDER_DIR = PROJECT_DIR / "render"
FPS = 24

DEFAULT_VISUAL_SOURCE = Path(
    r"C:\Users\Snipe\Downloads\The_Autopilot_Illusion__The_Truth_Behind_Index_Funds.elevenlabs-audio.mp4"
)
DEFAULT_NARRATION = Path(
    r"C:\Users\Snipe\Downloads\ElevenLabs__00_00_251_-_00_04_154_For_most_people,_.mp3"
)
DEFAULT_OLD_TRANSCRIPT = Path(
    r"C:\Users\Snipe\Downloads\The_Autopilot_Illusion__The_Truth_Behind_Index_Funds.transcribe.json"
)
DEFAULT_NEW_ALIGNMENT = Path(
    r"C:\Users\Snipe\Downloads\autopilot-elevenlabs-align\ElevenLabs__00_00_251_-_00_04_154_For_most_people,_.json"
)


def normalized_word(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ffprobe_duration(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return float(completed.stdout.strip())


def command(*args: str) -> None:
    subprocess.run(args, check=True)


def source_word_map(old_words: list[dict[str, Any]], new_words: list[dict[str, Any]]) -> dict[int, int]:
    old_text = [normalized_word(str(word["text"])) for word in old_words]
    new_text = [normalized_word(str(word["word"])) for word in new_words]
    mapping: dict[int, int] = {}
    matcher = difflib.SequenceMatcher(a=old_text, b=new_text, autojunk=False)
    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        # Preserve one-for-one editorial inflections ("hyperscalers" ->
        # "hyperscaler") so they do not become accidental visual holds.
        if tag == "replace" and old_end - old_start == new_end - new_start:
            for offset in range(new_end - new_start):
                mapping[new_start + offset] = old_start + offset
            continue
        if tag != "equal":
            continue
        for offset in range(new_end - new_start):
            mapping[new_start + offset] = old_start + offset
    return mapping


def caption_cues(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Emit one short, non-overlapping lower-third phrase at a time.

    The source word timings remain canonical, but the rendered treatment is a
    Remotion Bits word-by-word reveal. Four-word phrases fit one line on a
    phone and avoid the two-line accumulation that fought the charts.
    """
    cues: list[dict[str, Any]] = []
    for segment in segments:
        words = segment["words"]
        groups = [words[index : index + 4] for index in range(0, len(words), 4)]
        for group_index, group in enumerate(groups):
            if not group:
                continue
            start = float(group[0]["start"])
            # The following phrase replaces this one. Do not add a tail hold:
            # it was the source of overlapping caption pages.
            next_start = (
                float(groups[group_index + 1][0]["start"])
                if group_index + 1 < len(groups)
                else float(segment["end"])
            )
            end = max(float(group[-1]["end"]), next_start)
            cues.append(
                {
                    "id": f"caption-{len(cues) + 1:03d}",
                    "start": start,
                    "end": end,
                    "text": " ".join(str(word["word"]) for word in group),
                }
            )
    return cues


def build_visual_segments(
    old_words: list[dict[str, Any]],
    new_segments: list[dict[str, Any]],
    mapping: dict[int, int],
    visual_duration: float,
) -> list[dict[str, Any]]:
    """Project new sentence timings onto matching picture ranges from the source."""
    result: list[dict[str, Any]] = []
    global_new_index = 0
    for segment in new_segments:
        segment_words = segment["words"]
        mapped_flags = [global_new_index + word_index in mapping for word_index in range(len(segment_words))]
        run_start = 0
        while run_start < len(segment_words):
            mapped = mapped_flags[run_start]
            run_end = run_start + 1
            while run_end < len(segment_words) and mapped_flags[run_end] == mapped:
                run_end += 1
            target_start = float(segment["start"]) if run_start == 0 else float(segment_words[run_start]["start"])
            target_end = float(segment["end"]) if run_end == len(segment_words) else float(segment_words[run_end]["start"])
            run_words = segment_words[run_start:run_end]
            if mapped:
                source_indices = [mapping[global_new_index + offset] for offset in range(run_start, run_end)]
                source_start = max(0.0, float(old_words[source_indices[0]]["start"]) - 0.08)
                source_end = min(visual_duration - 0.02, float(old_words[source_indices[-1]]["end"]) + 0.24)
                if source_end <= source_start:
                    source_end = min(visual_duration - 0.01, source_start + 0.25)
                mode = "video"
            else:
                # The inserted line sits between the 8% AI-investment sentence
                # and the hyperscaler ROI sentence.  A related chart still
                # communicates the pause cleanly and is animated later by
                # Ken Burns in Remotion.
                source_start = min(visual_duration - 0.25, 192.0)
                source_end = min(visual_duration - 0.02, source_start + 0.4)
                mode = "ken_burns_still"
            result.append(
                {
                    "id": f"visual-{len(result) + 1:03d}",
                    "target_start": target_start,
                    "target_end": target_end,
                    "source_start": source_start,
                    "source_end": source_end,
                    "mode": mode,
                    "text": " ".join(str(word["word"]) for word in run_words),
                }
            )
            run_start = run_end
        global_new_index += len(segment_words)
    return result


def render_visual_track(visual_source: Path, visual_segments: list[dict[str, Any]], market_still: Path) -> Path:
    """Render one silent, cadence-correct visual track for efficient Remotion playback."""
    clips_dir = PUBLIC_DIR / "retimed-clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    concat_file = clips_dir / "concat.txt"
    output = PUBLIC_DIR / "retimed-visual-track.mp4"
    entries: list[str] = []
    for segment in visual_segments:
        clip_path = clips_dir / f"{segment['id']}.mp4"
        target_duration = max(0.08, float(segment["target_end"]) - float(segment["target_start"]))
        source_duration = max(0.04, float(segment["source_end"]) - float(segment["source_start"]))
        if segment["mode"] == "ken_burns_still":
            command(
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-loop", "1", "-i", str(market_still),
                "-t", f"{target_duration:.6f}", "-r", str(FPS),
                "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(clip_path),
            )
        else:
            speed = source_duration / target_duration
            command(
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", f"{float(segment['source_start']):.6f}", "-to", f"{float(segment['source_end']):.6f}",
                "-i", str(visual_source),
                "-vf", f"setpts={1 / speed:.9f}*PTS,fps={FPS},scale=1280:720:flags=lanczos,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(clip_path),
            )
        entries.append(f"file '{clip_path.as_posix()}'")
    concat_file.write_text("\n".join(entries) + "\n", encoding="utf-8")
    command(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), str(output),
    )
    return output


def counter_callouts() -> list[dict[str, Any]]:
    return [
        {"id": "top-ten", "start": 17.1, "end": 23.4, "from": 0, "to": 41, "postfix": "%", "label": "TOP 10 INDEX WEIGHT", "side": "left"},
        {"id": "ai-theme", "start": 24.0, "end": 34.1, "from": 0, "to": 50, "postfix": "%", "label": "AI-THEME EXPOSURE", "side": "right"},
        {"id": "single-theme", "start": 34.9, "end": 40.6, "from": 0, "to": 1, "prefix": "$1 OF EVERY ", "postfix": " $2", "label": "RIDING ON AI", "side": "left"},
        {"id": "largest-stock", "start": 93.5, "end": 96.6, "from": 0, "to": 8, "prefix": "$", "label": "TO THE LARGEST STOCK", "side": "right"},
        {"id": "smallest-stocks", "start": 97.2, "end": 100.8, "from": 0, "to": 2, "prefix": "$", "label": "SPLIT BY THE SMALLEST 100", "side": "left"},
        {"id": "inelastic", "start": 121.6, "end": 128.0, "from": 0, "to": 5, "prefix": "$1 → $", "label": "MARKET-VALUE EFFECT", "side": "right"},
        {"id": "history-peak", "start": 184.4, "end": 191.5, "from": 0, "to": 7, "postfix": "%", "label": "HISTORICAL PEAK THRESHOLD", "side": "left"},
        {"id": "ai-investment", "start": 191.9, "end": 201.8, "from": 0, "to": 8, "postfix": "%", "label": "AI INVESTMENT / GDP", "side": "right"},
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--visual-source", type=Path, default=DEFAULT_VISUAL_SOURCE)
    parser.add_argument("--narration", type=Path, default=DEFAULT_NARRATION)
    parser.add_argument("--old-transcript", type=Path, default=DEFAULT_OLD_TRANSCRIPT)
    parser.add_argument("--new-alignment", type=Path, default=DEFAULT_NEW_ALIGNMENT)
    parser.add_argument("--build-visual-track", action="store_true")
    args = parser.parse_args()

    for path in (args.visual_source, args.narration, args.old_transcript, args.new_alignment):
        if not path.is_file():
            raise FileNotFoundError(path)

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    visual_public = PUBLIC_DIR / "autopilot-source-visuals.mp4"
    narration_public = PUBLIC_DIR / "elevenlabs-narration.mp3"
    market_still = PUBLIC_DIR / "market-context-still.png"
    shutil.copy2(args.visual_source, visual_public)
    shutil.copy2(args.narration, narration_public)

    old_words = read_json(args.old_transcript)["words"]
    new_alignment = read_json(args.new_alignment)
    new_segments = new_alignment["segments"]
    new_words = [word for segment in new_segments for word in segment["words"]]
    mapping = source_word_map(old_words, new_words)
    visual_duration = ffprobe_duration(args.visual_source)
    narration_duration = ffprobe_duration(args.narration)
    visual_segments = build_visual_segments(old_words, new_segments, mapping, visual_duration)
    # A visual must also cover every spoken pause. Extend each segment to the
    # next segment's first word; otherwise a sentence-only assembly silently
    # drops the gaps and shortens the finished picture track.
    for index, segment in enumerate(visual_segments):
        segment["target_start"] = 0.0 if index == 0 else float(segment["target_start"])
        segment["target_end"] = (
            float(visual_segments[index + 1]["target_start"])
            if index + 1 < len(visual_segments)
            else narration_duration
        )
    inserted = [segment for segment in visual_segments if segment["mode"] == "ken_burns_still"]
    if len(inserted) != 1:
        raise RuntimeError(f"Expected exactly one inserted narration segment, found {len(inserted)}")

    command(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{inserted[0]['source_start']:.6f}",
        "-i", str(args.visual_source), "-frames:v", "1", "-q:v", "2", str(market_still),
    )
    if args.build_visual_track:
        render_visual_track(args.visual_source, visual_segments, market_still)

    props = {
        "schema_version": "autopilot_elevenlabs_recut.v1",
        "fps": FPS,
        "width": 1920,
        "height": 1080,
        "durationInFrames": round(narration_duration * FPS),
        "visualTrack": "autopilot-elevenlabs-recut-v1/retimed-visual-track.mp4",
        "narrationAudio": "autopilot-elevenlabs-recut-v1/elevenlabs-narration.mp3",
        "marketContextStill": "autopilot-elevenlabs-recut-v1/market-context-still.png",
        "kenBurnsRanges": [segment for segment in visual_segments if segment["mode"] == "ken_burns_still"],
        "captionCues": caption_cues(new_segments),
        "callouts": counter_callouts(),
        "provenance": {
            "visual_source": str(args.visual_source),
            "narration_source": str(args.narration),
            "old_transcript": str(args.old_transcript),
            "new_alignment": str(args.new_alignment),
            "matched_words": len(mapping),
            "new_words": len(new_words),
            "inserted_sentence_count": len(inserted),
            "narration_duration_seconds": narration_duration,
        },
    }
    props_path = RENDER_DIR / "autopilot-elevenlabs-recut-v1.props.json"
    props_path.write_text(json.dumps(props, indent=2) + "\n", encoding="utf-8")
    manifest_path = RENDER_DIR / "autopilot-elevenlabs-recut-v1.manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "autopilot_elevenlabs_recut_manifest.v1",
                "visual_grammar": {
                    "source_visuals": "sentence-aligned retime of the supplied ElevenLabs video",
                    "plate_motion": "one continuous slow directional Ken Burns-style camera move across the full cut",
                    "inserted_sentence": "Remotion Bits Ken Burns still",
                    "captions": "four-word Remotion Bits word-by-word phrases in one lower-third lane",
                    "metrics": "Remotion Bits basic-counter with typewriter labels",
                },
                "counts": {
                    "visual_segments": len(visual_segments),
                    "caption_cues": len(props["captionCues"]),
                    "counter_callouts": len(props["callouts"]),
                },
                "provenance": props["provenance"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(props_path)
    print(manifest_path)
    if args.build_visual_track:
        print(PUBLIC_DIR / "retimed-visual-track.mp4")


if __name__ == "__main__":
    main()
