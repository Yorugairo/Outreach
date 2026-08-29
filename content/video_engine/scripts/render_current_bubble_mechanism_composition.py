"""Render and inspect the current-bubble Remotion composition.

The earlier review path painted frames in Pillow and applied a dark blend at
asset changes.  That output was not evidence of the authored Remotion motion
plan.  This driver refuses stale props, renders the ``EditorialMotion``
composition at its declared frame rate, captures every shot boundary, and
rejects un-authored blank/dark cue starts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import statistics
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


EPISODE_ID = "current-bubble-mechanism"
RELATIVE_PILOT = Path(
    "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
)


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(command: list[str], *, cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")


def _probe(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    stream = payload["streams"][0]
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "r_frame_rate": str(stream["r_frame_rate"]),
        "avg_frame_rate": str(stream["avg_frame_rate"]),
        "nb_frames": int(stream.get("nb_frames") or 0),
        "duration_s": float(payload["format"]["duration"]),
    }


def _rate(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator)


def _frame_metrics(path: Path) -> dict[str, float | bool]:
    image = Image.open(path).convert("RGB")
    gray = image.convert("L")
    stats = ImageStat.Stat(gray)
    mean = float(stats.mean[0])
    stddev = float(stats.stddev[0])
    histogram = gray.histogram()
    pixels = max(1, image.width * image.height)
    near_dark_ratio = sum(histogram[:13]) / pixels
    blank_or_dark = (mean < 14.0 and stddev < 10.0) or near_dark_ratio > 0.985
    return {
        "mean_luma": round(mean, 3),
        "luma_stddev": round(stddev, 3),
        "near_dark_ratio": round(near_dark_ratio, 6),
        "blank_or_dark": blank_or_dark,
    }


def _difference(first: Path, second: Path, *, crop_bottom_ratio: float = 0.0) -> float:
    left = Image.open(first).convert("RGB")
    right = Image.open(second).convert("RGB")
    if left.size != right.size:
        right = right.resize(left.size, Image.Resampling.LANCZOS)
    if crop_bottom_ratio > 0:
        height = max(1, round(left.height * (1.0 - crop_bottom_ratio)))
        left = left.crop((0, 0, left.width, height))
        right = right.crop((0, 0, right.width, height))
    stat = ImageStat.Stat(ImageChops.difference(left, right))
    return round(math.sqrt(sum(value * value for value in stat.rms) / len(stat.rms)), 3)


def _is_authored_pause(shot: dict[str, Any]) -> bool:
    purpose = str(shot.get("purpose") or "").casefold()
    reasons = " ".join(
        str((shot.get(key) or {}).get("reason") or "")
        for key in ("transition_in", "transition_out")
    ).casefold()
    return purpose in {"pause", "breath", "intentional_pause"} or "authored pause" in reasons


def _capture_boundaries(
    video: Path,
    shots: list[dict[str, Any]],
    *,
    source_start_s: float,
    source_end_s: float,
    fps: int,
    output_dir: Path,
) -> dict[str, Any]:
    boundary_root = (output_dir / "boundary-frames").resolve()
    resolved_output = output_dir.resolve()
    if boundary_root.parent != resolved_output:
        raise ValueError(f"refusing to reset boundary frames outside render output: {boundary_root}")
    if boundary_root.exists():
        shutil.rmtree(boundary_root)
    boundaries: list[dict[str, Any]] = []
    frame_requests: set[int] = set()
    max_render_frame = max(0, math.ceil((source_end_s - source_start_s) * fps) - 1)
    for shot in shots:
        start_s = float(shot["start_s"])
        if start_s < source_start_s - 1e-6 or start_s >= source_end_s - 1e-6:
            continue
        relative = max(0.0, start_s - source_start_s)
        start_frame = max(0, round(relative * fps))
        shot_frames = max(1, round(float(shot.get("duration_s") or 0.0) * fps))
        settled_offset = min(max(1, round(0.55 * fps)), max(1, shot_frames // 2))
        transition = dict(shot.get("transition_in") or {})
        request = {
            "shot_id": str(shot["shot_id"]),
            "source_start_s": round(start_s, 6),
            "relative_start_s": round(relative, 6),
            "transition_in": transition,
            "authored_pause": _is_authored_pause(shot),
            "frames": {
                "before": max(0, start_frame - 1),
                "start": start_frame,
                "after": min(max_render_frame, start_frame + 1),
                "settled": min(max_render_frame, start_frame + settled_offset),
            },
        }
        transition_frames = max(0, round(float(transition.get("duration_s") or 0.0) * fps))
        if transition_frames > 1:
            request["frames"]["transition_mid"] = min(
                max_render_frame, start_frame + transition_frames // 2
            )
            request["frames"]["transition_end"] = min(
                max_render_frame, start_frame + transition_frames - 1
            )
        boundaries.append(request)
        frame_requests.update(request["frames"].values())

    if not boundaries:
        raise ValueError("render range contains no shot boundary")
    ordered_frames = sorted(frame_requests)
    raw_dir = boundary_root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    frame_paths: dict[int, Path] = {}
    # Windows caps process command lines at roughly 32K characters.  Long
    # focused renders can request hundreds of cue-boundary frames, so keep each
    # FFmpeg select expression intentionally small and map every batch back to
    # its source-frame indices.
    batch_size = 40
    for batch_number, offset in enumerate(range(0, len(ordered_frames), batch_size)):
        batch_frames = ordered_frames[offset : offset + batch_size]
        batch_dir = raw_dir / f"batch-{batch_number:03d}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        expression = "+".join(f"eq(n\\,{index})" for index in batch_frames)
        pattern = batch_dir / "frame-%04d.png"
        _run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video),
                "-vf",
                f"select={expression}",
                "-fps_mode",
                "vfr",
                str(pattern),
            ]
        )
        extracted = sorted(batch_dir.glob("frame-*.png"))
        if len(extracted) != len(batch_frames):
            raise RuntimeError(
                f"expected {len(batch_frames)} boundary frames in batch "
                f"{batch_number}, extracted {len(extracted)}"
            )
        frame_paths.update(dict(zip(batch_frames, extracted, strict=True)))
    if len(frame_paths) != len(ordered_frames):
        raise RuntimeError(
            f"expected {len(ordered_frames)} total boundary frames, mapped {len(frame_paths)}"
        )
    failures: list[str] = []
    distinct_deltas: list[float] = []
    for boundary in boundaries:
        named: dict[str, str] = {}
        for label, frame_index in boundary["frames"].items():
            destination = (
                output_dir
                / "boundary-frames"
                / f"{boundary['shot_id']}-{label}-f{frame_index:06d}.png"
            )
            shutil.copy2(frame_paths[frame_index], destination)
            named[label] = destination.relative_to(output_dir).as_posix()
        boundary["frame_paths"] = named
        start_path = output_dir / named["start"]
        boundary["start_metrics"] = _frame_metrics(start_path)
        boundary["sample_metrics"] = {
            label: _frame_metrics(output_dir / path)
            for label, path in named.items()
        }
        boundary["before_to_start_rms"] = _difference(
            output_dir / named["before"], start_path
        )
        boundary["before_to_settled_content_rms"] = _difference(
            output_dir / named["before"],
            output_dir / named["settled"],
            crop_bottom_ratio=0.12,
        )
        material_check_eligible = (
            int(boundary["frames"]["before"]) < int(boundary["frames"]["start"])
            and int(boundary["frames"]["settled"]) > int(boundary["frames"]["start"])
        )
        boundary["material_check_eligible"] = material_check_eligible
        boundary["materially_different"] = (
            float(boundary["before_to_settled_content_rms"]) >= 0.75
            if material_check_eligible
            else None
        )
        distinct_deltas.append(float(boundary["before_to_start_rms"]))
        for label, metrics in boundary["sample_metrics"].items():
            if metrics["blank_or_dark"] and not boundary["authored_pause"]:
                failures.append(
                    f"{boundary['shot_id']} has an un-authored blank/dark {label} frame"
                )
        if material_check_eligible and not boundary["materially_different"]:
            failures.append(
                f"{boundary['shot_id']} does not materially change the visual state"
            )

    transition_counts: dict[str, int] = {}
    for boundary in boundaries:
        kind = str(boundary["transition_in"].get("kind") or "hard_cut")
        transition_counts[kind] = transition_counts.get(kind, 0) + 1
        if kind == "match_cut" and not boundary["transition_in"].get("motif_id"):
            failures.append(f"{boundary['shot_id']} match_cut is missing motif_id")
    return {
        "schema_version": "finance_boundary_review.v1",
        "source_start_s": source_start_s,
        "source_end_s": source_end_s,
        "fps": fps,
        "boundary_count": len(boundaries),
        "transition_counts": transition_counts,
        "transition_contracts": {
            "hard_cut": "zero-duration direct semantic cut; no opacity or wipe",
            "paper_wipe": "visible base world plus moving foreground paper edge",
            "match_cut": "zero-duration direct cut with required shared motif_id and focal alignment",
        },
        "median_boundary_delta_rms": round(statistics.median(distinct_deltas), 3),
        "boundaries": boundaries,
        "failures": failures,
        "status": "pass" if not failures else "fail",
    }


def _full_gate(pilot: Path) -> None:
    gate_path = pilot / "review" / "p20-focused-gate-summary.v1.json"
    if not gate_path.is_file():
        raise ValueError("full render blocked: focused review gate summary is missing")
    gate = read_json(gate_path)
    if gate.get("status") != "pass":
        raise ValueError("full render blocked: focused review gate has not passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--props", type=Path)
    parser.add_argument("--export-scale", type=int, choices=(1, 2, 3, 4))
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    pilot = repo_root / RELATIVE_PILOT
    revision = pilot / "animatic" / "revisions" / "full-review-v1"
    props_path = (args.props or revision / "remotion-props-review.json").resolve()
    canonical_plan_path = pilot / "edit" / "word-timed-v1" / "editorial-motion-plan.v1.json"
    props = read_json(props_path)
    canonical_plan = read_json(canonical_plan_path)
    if props.get("plan") != canonical_plan:
        raise ValueError("Remotion props are stale relative to the canonical motion plan")
    if props["plan"].get("artifact_hash") != canonical_plan.get("artifact_hash"):
        raise ValueError("Remotion props and canonical motion-plan hashes differ")
    profile = dict(props.get("render_profile") or {})
    width = int(profile.get("width") or 0)
    height = int(profile.get("height") or 0)
    fps = int(profile.get("fps") or 0)
    if min(width, height, fps) <= 0:
        raise ValueError("Remotion props require a positive declared render profile")

    full_duration = float(canonical_plan["duration_s"])
    source_start_s = 0.0 if args.full else max(0.0, float(args.start))
    if args.full:
        _full_gate(pilot)
        source_end_s = full_duration
        output_dir = (
            args.output_dir
            or pilot / "animatic" / "revisions" / "composition-v2"
        ).resolve()
    else:
        source_end_s = min(full_duration, source_start_s + max(0.1, float(args.duration)))
        label = f"p20-remotion-smoke-{source_start_s:07.3f}-{source_end_s:07.3f}".replace(
            ".", "p"
        )
        output_dir = (
            args.output_dir or pilot / "animatic" / "revisions" / label
        ).resolve()
    if source_end_s <= source_start_s:
        raise ValueError("render range must be positive")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / (
        "current-bubble-mechanism-remotion-full-review.mp4"
        if args.full
        else "current-bubble-mechanism-remotion-smoke.mp4"
    )

    public_dir = revision / "public"
    editor = repo_root / "content" / "video_engine" / "editor"
    entry = editor / "src" / "index.tsx"
    for asset_id, relative in dict(props.get("asset_map") or {}).items():
        if not (public_dir / str(relative)).is_file():
            raise FileNotFoundError(f"staged Remotion asset missing: {asset_id}")
    audio_relative = str((props.get("canonical_audio") or {}).get("path") or "")
    if not audio_relative or not (public_dir / audio_relative).is_file():
        raise FileNotFoundError("staged canonical Remotion audio is missing")

    start_frame = round(source_start_s * fps)
    total_frames = max(1, round(full_duration * fps))
    end_frame = min(
        total_frames - 1,
        max(start_frame, math.ceil(source_end_s * fps) - 1),
    )
    source_end_s = min(source_end_s, (end_frame + 1) / fps)
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for Remotion rendering")
    # Keep the logical composition at 1280x720 so layout measurements and the
    # fast focus-review path remain stable. The full YouTube review is rendered
    # at 2x scale to produce a 2560x1440 upload candidate and trigger YouTube's
    # higher-quality transcode path.
    export_scale = args.export_scale or (2 if args.full else 1)
    output_width = width * export_scale
    output_height = height * export_scale
    command = [
        npx,
        "remotion",
        "render",
        str(entry),
        "EditorialMotion",
        f"--props={props_path}",
        f"--public-dir={public_dir}",
        f"--frames={start_frame}-{end_frame}",
        f"--scale={export_scale}",
        str(target),
    ]
    _run(command, cwd=editor)
    if not target.is_file():
        raise RuntimeError("Remotion did not produce the requested review render")
    probe = _probe(target)
    if probe["width"] != output_width or probe["height"] != output_height:
        raise ValueError("review render dimensions do not match the export profile")
    if abs(_rate(probe["avg_frame_rate"]) - fps) > 0.001:
        raise ValueError("review render frame rate does not match the declared profile")

    boundary = _capture_boundaries(
        target,
        list(canonical_plan["shots"]),
        source_start_s=source_start_s,
        source_end_s=source_end_s,
        fps=fps,
        output_dir=output_dir,
    )
    write_json(output_dir / "boundary-review.v1.json", boundary)
    if boundary["status"] != "pass":
        raise ValueError("boundary review failed: " + "; ".join(boundary["failures"]))

    manifest = {
        "schema_version": "finance_remotion_composition_render.v2",
        "episode_id": EPISODE_ID,
        "renderer": "remotion:EditorialMotion",
        "render_path": target.as_posix(),
        "render_sha256": sha256(target),
        "source_start_s": source_start_s,
        "source_end_s": source_end_s,
        "duration_s": round(source_end_s - source_start_s, 6),
        "full_episode_duration_s": full_duration,
        "logical_profile": {"width": width, "height": height, "fps": fps},
        "export_profile": {
            "width": output_width,
            "height": output_height,
            "fps": fps,
            "scale": export_scale,
            "paper_motion_fps": 12,
        },
        "ffprobe": probe,
        "canonical_motion_plan_path": canonical_plan_path.as_posix(),
        "canonical_motion_plan_artifact_hash": canonical_plan["artifact_hash"],
        "canonical_motion_plan_file_sha256": sha256(canonical_plan_path),
        "remotion_props_path": props_path.as_posix(),
        "remotion_props_sha256": sha256(props_path),
        "props_motion_plan_artifact_hash": props["plan"]["artifact_hash"],
        "public_dir": public_dir.as_posix(),
        "boundary_review_path": (output_dir / "boundary-review.v1.json").as_posix(),
        "boundary_review_status": boundary["status"],
        "status": "review_render_complete",
    }
    write_json(output_dir / "composition-render-manifest.v2.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
