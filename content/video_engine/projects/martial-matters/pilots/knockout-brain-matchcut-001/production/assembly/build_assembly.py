"""Build and render the Knockout Brain Match-Cut through the scene-evidence engine.

The input is the parent-owned ``production/edit.json`` contract::

    {
      "duration": 24.6,
      "clips": [{"id": "hook", "path": "...", "start": 0, "duration": 3.5}],
      "captions": [{"at": 0, "until": 1.2, "text": "..."}]
    }

Each clip is authored as a real ``clip:<path>`` world.  The shared compiler
and player then pool and seek those videos; no frame extraction or still-slide
fallback is used.  Source audio is copied/re-encoded into the build's one
master track because the player contract has one ``__audio__`` URI.

Typical commands (from the repository root)::

    python content/video_engine/projects/martial-matters/pilots/\
      knockout-brain-matchcut-001/production/assembly/build_assembly.py \
      --compile

    python .../build_assembly.py --compile --render --force \
      "footage-driven portrait review cut; motion gate is not tuned for this lane"

The output stays inside this directory.  The source manifest and raw custody
files are never rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
# This checkout has a nested content/video_engine/AGENTS.md.  Anchor the
# import root to the engine script itself so the wrapper works from pytest,
# PowerShell, or any current working directory.
REPO = next(
    (p for p in HERE.parents if (p / "content" / "video_engine" / "scripts" / "build_scene_timeline_f.py").is_file()),
    None,
)
if REPO is None:
    REPO = next((p for p in HERE.parents if (p / "AGENTS.md").is_file()), None)
if REPO is None:  # pragma: no cover - a checkout invariant, kept explicit for useful errors
    raise RuntimeError(f"cannot find repository root above {HERE}")
SCRIPTS = REPO / "content" / "video_engine" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from authoring import docks as D  # noqa: E402
from authoring import table as T  # noqa: E402


DEFAULT_EDIT = PROJECT / "production" / "edit.json"
DEFAULT_AUDIO = PROJECT / "production" / "audio" / "master.wav"
DEFAULT_WORD_TIMINGS = PROJECT / "production" / "audio" / "intro.words.json"
BUILD = HERE / "build"
SHOT_TABLE = HERE / "SHOT-TABLE.py"
TIMELINE_NAME = "knockout-brain-matchcut-001.timeline.json"
EPISODE_ID = "knockout-brain-matchcut-001"
TITLE = "Sean Sharaf Goes One Punch Mode"
SUBTITLE = "Martial Matters · private review cut"
ASPECT = "9:16"
EPS = 1e-3
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class ContractError(ValueError):
    """The edit manifest is not safe to turn into hard-cut scene rows."""


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ContractError(f"{label} must be a finite number")
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise ContractError(f"{label} must be a finite number") from None
    if not math.isfinite(out):
        raise ContractError(f"{label} must be a finite number")
    return out


def _resolve_media_path(raw: str, edit_path: Path) -> Path:
    """Resolve manifest paths without changing the manifest's spelling.

    Parent-produced manifests currently carry absolute paths.  Relative paths
    are intentionally portable: first relative to ``production/`` (the
    manifest's parent), then to the repository root.
    """
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    candidates = ((edit_path.parent / path).resolve(), (REPO / path).resolve())
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def load_edit(path: Path) -> dict[str, Any]:
    """Read and strictly validate the hard-cut edit contract."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read edit manifest {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContractError("edit manifest must be a JSON object")

    runtime = _finite(payload.get("duration", payload.get("runtime_s")), "duration")
    if runtime <= 0:
        raise ContractError("duration must be greater than zero")
    clips = payload.get("clips", payload.get("edit"))
    if not isinstance(clips, list) or not clips:
        raise ContractError("clips must be a non-empty list")

    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    cursor = 0.0
    for index, item in enumerate(clips):
        if not isinstance(item, dict):
            raise ContractError(f"clips[{index}] must be an object")
        clip_id = item.get("id")
        if not isinstance(clip_id, str) or not ID_RE.fullmatch(clip_id):
            raise ContractError(f"clips[{index}].id must match {ID_RE.pattern!r}")
        if clip_id in ids:
            raise ContractError(f"duplicate clip id {clip_id!r}")
        ids.add(clip_id)
        raw_path = item.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ContractError(f"clips[{index}].path must be a non-empty string")
        source = _resolve_media_path(raw_path, path)
        if not source.is_file():
            raise ContractError(f"clips[{index}] {clip_id!r}: source missing: {source}")
        start = _finite(item.get("start", cursor), f"clips[{index}].start")
        duration = _finite(item.get("duration"), f"clips[{index}].duration")
        if start < -EPS:
            raise ContractError(f"clips[{index}] {clip_id!r}: start must be >= 0")
        if duration <= EPS:
            raise ContractError(f"clips[{index}] {clip_id!r}: duration must be > 0")
        if abs(start - cursor) > EPS:
            relation = "overlap" if start < cursor else "gap"
            raise ContractError(
                f"clips[{index}] {clip_id!r}: {relation} at {start:g}s; expected {cursor:g}s for a hard cut"
            )
        end = start + duration
        if end > runtime + EPS:
            raise ContractError(f"clips[{index}] {clip_id!r}: ends at {end:g}s beyond duration {runtime:g}s")
        normalized.append({"id": clip_id, "path": source, "start": start, "duration": duration, "end": end})
        cursor = end
    if abs(cursor - runtime) > EPS:
        raise ContractError(f"clips end at {cursor:g}s but duration is {runtime:g}s; hard-cut timeline would black-frame")

    captions = payload.get("captions", [])
    if not isinstance(captions, list):
        raise ContractError("captions must be a list")
    normalized_captions: list[dict[str, Any]] = []
    previous_until = -math.inf
    for index, item in enumerate(captions):
        if not isinstance(item, dict):
            raise ContractError(f"captions[{index}] must be an object")
        at = _finite(item.get("at", item.get("start")), f"captions[{index}].at")
        until = _finite(item.get("until", item.get("end")), f"captions[{index}].until")
        text = item.get("text")
        if at < -EPS or until > runtime + EPS or until <= at + EPS:
            raise ContractError(f"captions[{index}] must fit within 0..{runtime:g}s and have until > at")
        if at < previous_until - EPS:
            raise ContractError(f"captions[{index}] overlaps the preceding caption")
        if not isinstance(text, str) or not text.strip():
            raise ContractError(f"captions[{index}].text must be non-empty")
        normalized_captions.append({"at": at, "until": until, "text": " ".join(text.split())})
        previous_until = until

    return {"duration": runtime, "clips": normalized, "captions": normalized_captions}


def _word_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _load_word_timings(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read caption word timings {path}: {exc}") from exc
    raw_words = payload.get("words") if isinstance(payload, dict) else payload
    if not isinstance(raw_words, list) or not raw_words:
        raise ContractError(f"caption word timings {path} must contain a non-empty words list")
    words: list[dict[str, Any]] = []
    for index, item in enumerate(raw_words):
        if not isinstance(item, dict) or not isinstance(item.get("w"), str) or not item["w"].strip():
            raise ContractError(f"caption word timings {path}: words[{index}].w must be non-empty")
        start = _finite(item.get("start_s", item.get("start")), f"words[{index}].start_s")
        end = _finite(item.get("end_s", item.get("end")), f"words[{index}].end_s")
        if start < -EPS or end <= start + EPS:
            raise ContractError(f"caption word timings {path}: words[{index}] must have end_s > start_s")
        words.append({"w": item["w"].strip(), "start": start, "end": end})
    return words


def _caption_pages(
    captions: list[dict[str, Any]], word_timings: list[dict[str, Any]] | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Turn manifest captions into engine pages using canonical word times.

    A word sidecar is matched in order, allowing an intro sidecar to contain
    spoken lead-in words before the first visible caption. The page end remains
    the manifest's hold end; only each word's on/off timing comes from the
    sidecar. A non-empty caption list without a sidecar is invalid.
    """
    pages: list[dict[str, Any]] = []
    words: list[dict[str, Any]] = []
    sidecar_index = 0
    for caption in captions:
        tokens = caption["text"].split()
        matched: list[dict[str, Any]] = []
        if word_timings is not None:
            wanted = [_word_key(token) for token in tokens]
            for start_index in range(sidecar_index, len(word_timings) - len(wanted) + 1):
                candidate = word_timings[start_index:start_index + len(wanted)]
                if [_word_key(item["w"]) for item in candidate] == wanted:
                    matched = candidate
                    sidecar_index = start_index + len(wanted)
                    break
            if not matched:
                raise ContractError(
                    f"caption {caption['text']!r} has no ordered match in the word-timing sidecar"
                )
        elif tokens:
            raise ContractError("caption word timings are required when edit.json contains captions")
        page_words = []
        for index, (token, timing) in enumerate(zip(tokens, matched, strict=True)):
            item = {
                "w": token,
                "s": round(timing["start"], 3),
                "e": round(timing["end"], 3),
                "k": bool(re.search(r"\d", token)),
            }
            page_words.append(item)
            words.append({"w": token, "start": item["s"], "end": item["e"], "part": 1})
        pages.append({"s": caption["at"], "e": caption["until"], "t": page_words})
    return pages, words


def _write_timeline_inputs(edit: dict[str, Any], audio: Path, word_timings_path: Path | None) -> None:
    word_timings = _load_word_timings(word_timings_path) if word_timings_path else None
    if edit["captions"] and word_timings is None:
        raise ContractError("caption word timings are required when edit.json contains captions")
    pages, words = _caption_pages(edit["captions"], word_timings)
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "caption-pages.json").write_text(json.dumps(pages, indent=1), encoding="utf-8")
    timeline = {
        "episode": EPISODE_ID,
        "script": "production/edit.json",
        "take": "master",
        "runtime_s": edit["duration"],
        "words": words,
        "sentences": [],
        "edit_pauses_applied": False,
        "audio_source": str(audio),
    }
    (BUILD / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8")


def _prepare_audio(audio: Path) -> Path:
    """Make the build's one engine-compatible master audio file."""
    out = BUILD / "audio" / "episode.mp3"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(audio), "-vn", "-ac", "2", "-ar", "48000",
         "-c:a", "libmp3lame", "-b:a", "192k", "-map_metadata", "-1", str(out)],
        check=True,
    )
    return out


def _write_shot_table(edit: dict[str, Any]) -> list[dict[str, Any]]:
    """Re-encode source clips for deterministic seeks and write hard-cut rows."""
    rows: list[tuple] = []
    prepared: list[dict[str, Any]] = []
    for clip in edit["clips"]:
        encoded = D.seekable_clip(f"{clip['id']}.mp4", clip["path"], BUILD)
        plate = f"clip:{encoded.resolve().as_posix()}"
        rows.append((clip["start"], clip["end"], plate, (0, 0, 0), [], "cut", []))
        prepared.append({**clip, "prepared": encoded})
    header = (
        '"""Generated by build_assembly.py; source rows are hard cuts over real video clips."""\n'
        "# Do not edit by hand; regenerate from production/edit.json.\n"
    )
    T.write_shot_table(SHOT_TABLE, rows, header)
    return prepared


def _compile() -> int:
    """Compile through the shared player/compiler, never a second renderer."""
    return T.compile_timeline(
        PROJECT,
        BUILD,
        timeline_name=TIMELINE_NAME,
        shot_table_file="production/assembly/SHOT-TABLE.py",
        title=TITLE,
        subtitle=SUBTITLE,
        episode_id=EPISODE_ID,
        aspect=ASPECT,
        caption_style="phrase",
        kinetics={},
        render=False,
        form="short",
    )


def _ffprobe(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration:stream=codec_type,width,height,codec_name",
         "-of", "json", str(path)], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def _render(force_reason: str | None, workers: int, output_size: str) -> Path:
    """Render the served split player and optionally downscale to the review size."""
    import serve_player

    server, port, _watch = serve_player.start(BUILD, port=0, check=False, quiet=True)
    try:
        env = os.environ.copy()
        env.update({
            "RENDER_BUILD": str(BUILD),
            "RENDER_URL": f"http://127.0.0.1:{port}/player.html",
            "RENDER_NAME": EPISODE_ID,
            "RENDER_ASPECT": ASPECT,
        })
        cmd = [sys.executable, str(SCRIPTS / "render_episode.py"), "--workers", str(workers)]
        if force_reason is not None:
            cmd += ["--force", force_reason]
        result = subprocess.run(cmd, cwd=str(REPO), env=env)
        if result.returncode:
            raise RuntimeError(f"render_episode.py exited {result.returncode}")
    finally:
        server.shutdown()

    source = BUILD / "render" / f"{EPISODE_ID}-full-1440p.mp4"
    if not source.is_file():
        raise RuntimeError(f"renderer completed without {source}")
    match = re.fullmatch(r"(\d+)x(\d+)", output_size)
    if not match:
        raise ValueError("output size must be WIDTHxHEIGHT, e.g. 1080x1920")
    width, height = (int(match.group(1)), int(match.group(2)))
    final = BUILD / "render" / f"{EPISODE_ID}-{output_size}.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(source), "-vf", f"scale={width}:{height}:flags=lanczos",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)],
        check=True,
    )
    probe = _ffprobe(final)
    digest = hashlib.sha256(final.read_bytes()).hexdigest()
    receipt = {
        "artifact": str(final),
        "sha256": digest,
        "format": probe.get("format", {}),
        "streams": probe.get("streams", []),
        "timeline": str(BUILD / TIMELINE_NAME),
        "engine": "docs/content-video-engine/samples/scene-evidence-engine.mjs",
        "hard_cuts": True,
        "review_only": True,
    }
    (BUILD / "ASSEMBLY-RECEIPT.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    return final


def build(
    edit_path: Path,
    audio_path: Path,
    word_timings_path: Path | None,
) -> dict[str, Any]:
    edit = load_edit(edit_path)
    if not audio_path.is_file():
        raise ContractError(f"audio master missing: {audio_path}")
    BUILD.mkdir(parents=True, exist_ok=True)
    prepared_audio = _prepare_audio(audio_path)
    _write_timeline_inputs(edit, prepared_audio, word_timings_path)
    prepared_clips = _write_shot_table(edit)
    rc = _compile()
    if rc:
        raise RuntimeError(f"scene compiler exited {rc}")
    return {"edit": edit, "audio": prepared_audio, "clips": prepared_clips}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edit", type=Path, default=DEFAULT_EDIT, help="parent-owned edit.json")
    parser.add_argument("--audio", type=Path, default=None, help="master WAV/MP3; defaults to production/audio/master.wav")
    parser.add_argument(
        "--word-timings", type=Path, default=None,
        help="caption word sidecar; defaults to production/audio/intro.words.json",
    )
    parser.add_argument("--compile", action="store_true", help="compile the split scene-evidence player")
    parser.add_argument("--render", action="store_true", help="render the compiled player to MP4")
    parser.add_argument("--force", dest="force_reason", metavar="REASON", help="explicit reason to override a motion-gate refusal")
    parser.add_argument("--workers", type=int, default=1, help="headless Chromium render workers")
    parser.add_argument("--output-size", default="1080x1920", help="review MP4 size; renderer captures at 1440x2560 first")
    parser.add_argument("--validate-only", action="store_true", help="validate edit.json and source files without audio or writes")
    args = parser.parse_args(argv)

    edit_path = args.edit.resolve()
    edit = load_edit(edit_path)
    word_timings = (args.word_timings or DEFAULT_WORD_TIMINGS).resolve()
    if edit["captions"]:
        if not word_timings.is_file():
            raise ContractError(f"caption word timings missing: {word_timings}")
        # Validate the ordered sidecar match without touching the build when
        # this is a validate-only invocation.
        _caption_pages(edit["captions"], _load_word_timings(word_timings))
    print(f"edit: {edit_path}")
    print(f"  clips={len(edit['clips'])} duration={edit['duration']:.3f}s captions={len(edit['captions'])}")
    if args.validate_only:
        print("VALID: hard-cut clip spans and source paths")
        return 0
    audio = (args.audio or DEFAULT_AUDIO).resolve()
    if not args.compile and not args.render:
        parser.error("choose --compile, --render, or --validate-only")
    build(edit_path, audio, word_timings if word_timings.is_file() else None)
    print(f"compiled: {BUILD / 'player.html'}")
    if args.render:
        if args.force_reason is None:
            print("render: relying on the motion gate; use --force with a reason only if it refuses this footage lane")
        final = _render(args.force_reason, args.workers, args.output_size)
        print(f"rendered: {final}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
