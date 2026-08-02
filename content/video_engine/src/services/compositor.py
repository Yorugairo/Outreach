from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Sequence

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.timing import load_measured_timeline


_LOUDNORM_JSON = re.compile(r"\{\s*\"input_i\".*?\}", re.DOTALL)


def _run(
    runner: Callable[..., subprocess.CompletedProcess[str]],
    command: Sequence[str],
) -> subprocess.CompletedProcess[str]:
    return runner(
        list(command),
        check=True,
        capture_output=True,
        text=True,
    )


def probe_duration(
    path: str | Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> float:
    result = _run(
        runner,
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(Path(path)),
        ],
    )
    return float(result.stdout.strip())


def _transition_for_segment(
    storyboard: dict[str, Any],
    scene_ids: list[int],
) -> str:
    scenes = {int(scene["scene_id"]): scene for scene in storyboard["scenes"]}
    first_scene = scenes[int(scene_ids[0])]
    return str((first_scene.get("transition") or {}).get("in") or "continuous")


def build_video_filter(
    storyboard: dict[str, Any],
    segments: list[dict[str, Any]],
    *,
    crossfade_s: float = 0.3,
) -> tuple[str, str]:
    filters = [
        f"[{index}:v]setpts=PTS-STARTPTS[v{index}]"
        for index in range(len(segments))
    ]
    current = "v0"
    duration = float(segments[0]["duration_s"])
    for index, segment in enumerate(segments[1:], start=1):
        output = f"join{index}"
        transition = _transition_for_segment(storyboard, list(segment["scene_ids"]))
        if transition == "crossfade":
            overlap = min(crossfade_s, duration / 2, float(segment["duration_s"]) / 2)
            padded = f"{current}pad"
            next_input = f"v{index}tb"
            filters.append(
                f"[{current}]tpad=stop_mode=clone:stop_duration={overlap:.6f},"
                f"settb=AVTB[{padded}]"
            )
            filters.append(
                f"[v{index}]settb=AVTB[{next_input}]"
            )
            filters.append(
                f"[{padded}][{next_input}]xfade=transition=fade:"
                f"duration={overlap:.6f}:offset={duration:.6f}[{output}]"
            )
            duration += float(segment["duration_s"])
        else:
            filters.append(
                f"[{current}][v{index}]concat=n=2:v=1:a=0[{output}]"
            )
            duration += float(segment["duration_s"])
        current = output
    return ";".join(filters), current


class CompositorService:
    def __init__(
        self,
        *,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ):
        self._runner = runner

    def assemble_profile(
        self,
        storyboard: dict[str, Any],
        manifest_path: str | Path,
        audio_dir: str | Path,
        output_path: str | Path,
        *,
        music_path: str | Path | None = None,
        ducking: bool = True,
        sound_manifest_path: str | Path | None = None,
    ) -> StageOutput:
        manifest_file = Path(manifest_path)
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        segments = list(manifest.get("segments") or [])
        if not segments:
            raise ValueError("render manifest contains no segments")
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        work_dir = output.parent / ".assembly"
        work_dir.mkdir(parents=True, exist_ok=True)
        video_only = work_dir / "video.mp4"
        narration = work_dir / "narration.wav"
        mixed = work_dir / "mixed.mp4"

        # Gate-A output is immutable and the persisted word timings are the
        # only post-Gate-A duration clock.  Load the complete timeline before
        # invoking ffmpeg so a missing or malformed scene artifact fails
        # closed without producing a misleading final.
        measured_timeline = load_measured_timeline(storyboard, audio_dir)

        segment_paths = []
        for segment in segments:
            path = Path(segment["path"])
            if not path.is_absolute():
                profile_relative = manifest_file.parent / path
                job_relative = manifest_file.parents[2] / path
                path = (
                    profile_relative
                    if profile_relative.exists()
                    else job_relative
                )
            segment_paths.append(path)
        video_filter, video_label = build_video_filter(storyboard, segments)
        command = ["ffmpeg", "-y"]
        for path in segment_paths:
            command.extend(["-i", str(path)])
        command.extend(
            [
                "-filter_complex",
                video_filter,
                "-map",
                f"[{video_label}]",
                "-an",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(video_only),
            ]
        )
        _run(self._runner, command)

        audio_inputs: list[Path] = []
        audio_filters: list[str] = []
        for index, (scene, scene_timing) in enumerate(
            zip(storyboard["scenes"], measured_timeline)
        ):
            scene_id = int(scene["scene_id"])
            path = Path(audio_dir) / f"scene_{scene_id}.mp3"
            if not path.exists():
                raise FileNotFoundError(f"missing narration audio for scene {scene_id}")
            audio_inputs.append(path)
            padding = scene_timing.padding_s
            duration = scene_timing.total_duration_s
            audio_filters.append(
                f"[{index}:a]apad=pad_dur={padding:.6f},"
                f"atrim=duration={duration:.6f},asetpts=PTS-STARTPTS[a{index}]"
            )
        audio_filters.append(
            "".join(f"[a{index}]" for index in range(len(audio_inputs)))
            + f"concat=n={len(audio_inputs)}:v=0:a=1[narration]"
        )
        command = ["ffmpeg", "-y"]
        for path in audio_inputs:
            command.extend(["-i", str(path)])
        command.extend(
            [
                "-filter_complex",
                ";".join(audio_filters),
                "-map",
                "[narration]",
                "-c:a",
                "pcm_s16le",
                str(narration),
            ]
        )
        _run(self._runner, command)

        sound_events: list[dict[str, Any]] = []
        if sound_manifest_path is not None:
            sound_path = Path(sound_manifest_path)
            if sound_path.is_file():
                sound_payload = json.loads(sound_path.read_text(encoding="utf-8"))
                sound_events = [
                    dict(event)
                    for event in sound_payload.get("events", [])
                    if isinstance(event, dict)
                    and bool(event.get("available"))
                    and event.get("asset_path")
                    and Path(str(event["asset_path"])).is_file()
                ]

        mix_command = ["ffmpeg", "-y", "-i", str(video_only), "-i", str(narration)]
        for event in sound_events:
            mix_command.extend(["-i", str(Path(str(event["asset_path"])))])
        music_input_index: int | None = None
        if music_path is not None:
            music_input_index = 2 + len(sound_events)
            mix_command.extend(["-stream_loop", "-1", "-i", str(Path(music_path))])

        if music_path is None and not sound_events:
            mix_command.extend(
                [
                    "-map",
                    "0:v",
                    "-map",
                    "1:a",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(mixed),
                ]
            )
        else:
            filter_parts: list[str] = []
            mix_labels = ["[1:a]"]
            for index, event in enumerate(sound_events):
                input_index = 2 + index
                delay_ms = max(0, int(round(float(event.get("at_s", 0.0)) * 1000)))
                gain_db = float(event.get("gain_db", -18.0))
                label = f"sfx{index}"
                filter_parts.append(
                    f"[{input_index}:a]volume={gain_db:.6f}dB,"
                    f"adelay=delays={delay_ms}:all=1[{label}]"
                )
                mix_labels.append(f"[{label}]")
            if music_input_index is not None:
                filter_parts.append(
                    f"[{music_input_index}:a]volume=-18dB[music]"
                )
                if ducking:
                    filter_parts.append(
                        "[music][1:a]sidechaincompress="
                        "threshold=0.03:ratio=8[ducked]"
                    )
                    mix_labels.append("[ducked]")
                else:
                    mix_labels.append("[music]")
            filter_parts.append(
                "".join(mix_labels)
                + f"amix=inputs={len(mix_labels)}:normalize=0[mix]"
            )
            mix_command.extend(
                [
                    "-filter_complex",
                    ";".join(filter_parts),
                    "-map",
                    "0:v",
                    "-map",
                    "[mix]",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(mixed),
                ]
            )
        _run(self._runner, mix_command)

        measured = self._measure_loudness(mixed)
        self._normalize_loudness(mixed, output, measured)
        # The second loudnorm pass reports its predicted output before the
        # final container/audio encoding.  Measure the persisted final so QC
        # evaluates the artifact that will actually be reviewed and published.
        normalized = self._measure_loudness(output)
        measured_lufs = float(normalized["input_i"])
        loudness_correction_db = 0.0
        if abs(measured_lufs - (-14.0)) > 1.0:
            # AAC/container conversion can move the integrated value just
            # outside the Gate-B band even when the loudnorm pass predicted a
            # compliant result. Apply one bounded, measured correction to the
            # persisted artifact, then re-measure it before returning.
            loudness_correction_db = -14.0 - measured_lufs
            corrected = work_dir / "loudness-corrected.mp4"
            _run(
                self._runner,
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(output),
                    "-af",
                    f"volume={loudness_correction_db:.6f}dB",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    str(corrected),
                ],
            )
            corrected.replace(output)
            normalized = self._measure_loudness(output)
            measured_lufs = float(normalized["input_i"])
        actual_duration = probe_duration(output, runner=self._runner)
        expected_duration = measured_timeline.total_s
        if expected_duration > 0:
            drift = abs(actual_duration - expected_duration) / expected_duration
            if drift > 0.02:
                raise ValueError(
                    f"final duration drift {drift:.2%} exceeds 2% "
                    f"({actual_duration:.3f}s vs measured audio timeline "
                    f"{expected_duration:.3f}s)"
                )
        return StageOutput(
            {
                "final_path": str(output),
                "duration_s": round(actual_duration, 3),
                "expected_duration_s": round(expected_duration, 3),
                "measured_lufs": float(normalized["input_i"]),
                "loudness_target_lufs": -14.0,
                "loudness_correction_db": round(loudness_correction_db, 6),
                "sound_event_count": len(sound_events),
                "cost_usd": 0.0,
            }
        )

    def _measure_loudness(self, path: Path) -> dict[str, str]:
        result = _run(
            self._runner,
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(path),
                "-af",
                "loudnorm=I=-14:LRA=11:TP=-1.5:print_format=json",
                "-f",
                "null",
                "-",
            ],
        )
        return self._parse_loudnorm(result.stderr)

    def _normalize_loudness(
        self,
        input_path: Path,
        output_path: Path,
        measured: dict[str, str],
    ) -> dict[str, str]:
        loudnorm = (
            "loudnorm=I=-14:LRA=11:TP=-1.5:"
            f"measured_I={measured['input_i']}:"
            f"measured_LRA={measured['input_lra']}:"
            f"measured_TP={measured['input_tp']}:"
            f"measured_thresh={measured['input_thresh']}:"
            f"offset={measured['target_offset']}:"
            "linear=true:print_format=json"
        )
        result = _run(
            self._runner,
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-af",
                loudnorm,
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                str(output_path),
            ],
        )
        return self._parse_loudnorm(result.stderr)

    @staticmethod
    def _parse_loudnorm(stderr: str) -> dict[str, str]:
        matches = list(_LOUDNORM_JSON.finditer(stderr))
        if not matches:
            raise ValueError("ffmpeg loudnorm did not emit JSON measurements")
        return json.loads(matches[-1].group(0))

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        storyboard = json.loads(
            ctx.job_dir.joinpath("storyboard.json").read_text(encoding="utf-8")
        )
        profiles = list(job.config_snapshot.get("selected_render_profiles") or [])
        if not profiles:
            profiles = [
                f"{target}_final"
                if target in {"landscape", "vertical"}
                else str(target)
                for target in (
                    job.input_payload.get("targets")
                    or storyboard["global_settings"]["targets"]
                )
            ]
        outputs: dict[str, Any] = {}
        for profile in profiles:
            profile_dir = ctx.job_dir / "video" / profile
            profile_configs = job.config_snapshot.get("render_profile_configs") or {}
            configured = (
                profile_configs.get(profile, {})
                if isinstance(profile_configs, dict)
                and isinstance(profile_configs.get(profile), dict)
                else {}
            )
            target = str(
                configured.get("target")
                or (profile.rsplit("_", 1)[0] if "_" in profile else profile)
            )
            editorial_dir = ctx.job_dir / "editorial" / target
            editorial_video = editorial_dir / "editorial.mp4"
            editorial_manifest = editorial_dir / "edit_manifest.json"
            render_manifest = profile_dir / "manifest.json"
            picture_source = "manim_segments"
            if editorial_video.is_file() and editorial_manifest.is_file():
                edit = json.loads(editorial_manifest.read_text(encoding="utf-8"))
                fps = float(edit.get("fps") or configured.get("fps") or 30)
                duration_s = float(edit["duration_in_frames"]) / fps
                render_manifest = editorial_dir / "compositor_manifest.json"
                render_manifest.write_text(
                    json.dumps(
                        {
                            "segments": [
                                {
                                    "path": str(editorial_video.resolve()),
                                    "scene_ids": [
                                        int(scene["scene_id"])
                                        for scene in storyboard["scenes"]
                                    ],
                                    "duration_s": duration_s,
                                }
                            ]
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                picture_source = "remotion_editorial"
            result = self.assemble_profile(
                storyboard,
                render_manifest,
                ctx.job_dir / "audio",
                profile_dir / "final.mp4",
                music_path=ctx.configs.get("music_path"),
                ducking=bool(ctx.configs.get("music_ducking", True)),
                sound_manifest_path=ctx.job_dir / "audio" / "sound_manifest.json",
            )
            outputs[profile] = result.summary
            outputs[profile]["picture_source"] = picture_source
        measured = [
            float(summary["measured_lufs"]) for summary in outputs.values()
        ]
        return StageOutput(
            {
                "profiles": outputs,
                "measured_lufs": sum(measured) / len(measured),
                "cost_usd": 0.0,
            }
        )
