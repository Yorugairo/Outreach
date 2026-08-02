"""Deterministic pre-Gate-B quality checks and report writer."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import parse_qs, urlparse

from content.video_engine.src.guards.visual_qc import run_visual_qc
from content.video_engine.src.services.compositor import probe_duration
from content.video_engine.src.timing import TimingArtifactError, load_measured_timeline


QCResult = dict[str, Any]

_PROFILE_ALIASES = {
    "landscape": ("landscape_final", "landscape"),
    "vertical": ("vertical_final", "vertical"),
}
_WORDS_FILE = re.compile(r"scene_(?P<scene_id>\d+)\.words\.json$")


def _load_json(value: Mapping[str, Any] | str | Path | None) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value
    return json.loads(Path(value).read_text(encoding="utf-8"))


def _check(check_id: str, status: str, detail: str) -> dict[str, str]:
    return {"check_id": check_id, "status": status, "detail": detail}


def _duration_check(
    storyboard: Mapping[str, Any],
    job_dir: Path,
    manifest: Mapping[str, Any] | str | Path | None,
    *,
    compositor_summary: Mapping[str, Any] | None = None,
    duration_probe: Callable[[Path], float] | None = None,
) -> dict[str, str]:
    del manifest  # Final artifacts, not stale render manifests, are the QC clock.
    try:
        timeline = load_measured_timeline(storyboard, job_dir / "audio")
    except TimingArtifactError as exc:
        return _check("duration_drift", "fail", f"measured timeline invalid: {exc}")

    expected = timeline.total_s
    if not math.isfinite(expected) or expected <= 0:
        return _check("duration_drift", "fail", "measured audio timeline duration is invalid")

    profiles = _selected_profiles(storyboard, job_dir, compositor_summary)
    if not profiles:
        return _check("duration_drift", "fail", "no selected render profiles found")

    details: list[str] = []
    failures: list[str] = []
    probe = duration_probe or probe_duration
    for profile in profiles:
        final_path = job_dir / "video" / profile / "final.mp4"
        if not final_path.is_file():
            failures.append(f"{profile}: final.mp4 is missing ({final_path.as_posix()})")
            continue
        try:
            actual = float(probe(final_path))
            if not math.isfinite(actual) or actual <= 0:
                raise ValueError("probe returned a non-positive or non-finite duration")
        except Exception as exc:  # ffprobe failures are deterministic QC failures.
            failures.append(f"{profile}: final.mp4 is unprobeable: {exc}")
            continue
        drift = abs(actual - expected) / expected
        details.append(
            f"{profile}: expected={expected:g}s actual={actual:g}s "
            f"drift={drift * 100:.2f}%"
        )
        if drift > 0.02:
            failures.append(f"{profile}: drift={drift * 100:.2f}% exceeds 2%")
    if failures:
        return _check("duration_drift", "fail", "; ".join(failures + details))
    return _check("duration_drift", "pass", f"measured_audio={expected:g}s; " + "; ".join(details))


def _selected_profiles(
    storyboard: Mapping[str, Any],
    job_dir: Path,
    compositor_summary: Mapping[str, Any] | None,
) -> list[str]:
    """Resolve the exact final profiles that Gate-B QC must verify.

    A compositor stage summary is authoritative because it records explicit
    profile selection (including custom profiles).  Direct QC callers may not
    have that summary, so storyboard targets are mapped through the existing
    landscape/vertical aliases.  When both aliases are possible, prefer the
    artifact that exists while retaining a canonical alias for a missing-file
    diagnostic when neither exists.
    """

    if compositor_summary is not None:
        selected = compositor_summary.get("profiles")
        if isinstance(selected, Mapping) and selected:
            return list(dict.fromkeys(str(profile) for profile in selected))

    settings = storyboard.get("global_settings", {})
    targets = settings.get("targets", []) if isinstance(settings, Mapping) else []
    if not isinstance(targets, list):
        return []

    profiles: list[str] = []
    for target in targets:
        target_name = str(target)
        aliases = _PROFILE_ALIASES.get(target_name, (target_name,))
        existing = next(
            (
                alias
                for alias in aliases
                if (job_dir / "video" / alias / "final.mp4").is_file()
                or (job_dir / "video" / alias).is_dir()
            ),
            aliases[0],
        )
        if existing not in profiles:
            profiles.append(existing)
    return profiles


def _word_files(job_dir: Path) -> dict[int, tuple[Path, Mapping[str, Any] | None]]:
    audio_dir = job_dir / "audio"
    files: dict[int, tuple[Path, Mapping[str, Any] | None]] = {}
    if not audio_dir.is_dir():
        return files
    for path in sorted(audio_dir.glob("scene_*.words.json")):
        match = _WORDS_FILE.search(path.name)
        if match is None:
            continue
        scene_id = int(match.group("scene_id"))
        try:
            loaded = _load_json(path)
        except (OSError, json.JSONDecodeError):
            loaded = None
        files[scene_id] = (path, loaded)
    return files


def _words_coverage(
    storyboard: Mapping[str, Any], job_dir: Path
) -> tuple[dict[str, str], dict[int, Mapping[str, Any]]]:
    files = _word_files(job_dir)
    expected_ids = [
        int(scene["scene_id"])
        for scene in storyboard.get("scenes", [])
        if isinstance(scene, Mapping) and scene.get("scene_id") is not None
    ]
    missing = [str(scene_id) for scene_id in expected_ids if scene_id not in files]
    malformed: list[str] = []
    loaded: dict[int, Mapping[str, Any]] = {}
    for scene_id in expected_ids:
        if scene_id not in files:
            continue
        path, data = files[scene_id]
        if data is None or not isinstance(data.get("words"), list):
            malformed.append(path.name)
            continue
        words = data.get("words", [])
        if not words:
            malformed.append(f"{path.name}: empty words")
            continue
        try:
            duration = float(data.get("duration_s"))
        except (TypeError, ValueError):
            malformed.append(f"{path.name}: invalid duration_s")
            continue
        last_end = 0.0
        for word in words:
            if not isinstance(word, Mapping):
                malformed.append(f"{path.name}: malformed word")
                break
            try:
                start = float(word["start_s"])
                end = float(word["end_s"])
            except (KeyError, TypeError, ValueError):
                malformed.append(f"{path.name}: malformed timing")
                break
            if start < 0 or end < start:
                malformed.append(f"{path.name}: invalid timing range")
                break
            last_end = max(last_end, end)
        else:
            if duration + 1e-9 < last_end:
                malformed.append(f"{path.name}: words extend past duration_s")
            else:
                loaded[scene_id] = data
    if missing or malformed:
        details: list[str] = []
        if missing:
            details.append("missing scenes=" + ",".join(missing))
        if malformed:
            details.append("invalid=" + ",".join(malformed))
        return _check("words_coverage", "fail", "; ".join(details)), loaded
    return _check("words_coverage", "pass", f"{len(expected_ids)} scene word files covered"), loaded


def _numeric_lufs(summary: Mapping[str, Any] | None) -> list[float]:
    values: list[float] = []
    if summary is None:
        return values
    keys = {"integrated_lufs", "measured_lufs", "loudness_lufs", "lufs", "loudness"}

    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, Mapping):
            for child_key, child_value in value.items():
                visit(child_value, str(child_key).lower())
        elif (key in keys or "lufs" in key) and not any(
            marker in key for marker in ("target", "goal", "tolerance")
        ):
            try:
                values.append(float(value))
            except (TypeError, ValueError):
                pass

    visit(summary)
    return values


def _load_compositor_summary(job_dir: Path) -> Mapping[str, Any] | None:
    for path in (
        job_dir / "compositor_summary.json",
        job_dir / "video" / "compositor_summary.json",
    ):
        if path.exists():
            try:
                return _load_json(path)
            except (OSError, json.JSONDecodeError):
                return None
    return None


def _loudness_check(
    job_dir: Path, compositor_summary: Mapping[str, Any] | None
) -> dict[str, str]:
    summary = compositor_summary if compositor_summary is not None else _load_compositor_summary(job_dir)
    values = _numeric_lufs(summary)
    if not values:
        return _check("loudness", "fail", "compositor summary has no measured LUFS field")
    outside = [value for value in values if abs(value - (-14.0)) > 1.0]
    detail = ", ".join(f"{value:g} LUFS" for value in values)
    if outside:
        return _check("loudness", "fail", f"measured {detail}; target is -14 ±1 LUFS")
    return _check("loudness", "pass", f"measured {detail}")


def _caption_check(storyboard: Mapping[str, Any], job_dir: Path) -> dict[str, str]:
    targets = (
        storyboard.get("global_settings", {}).get("targets", [])
        if isinstance(storyboard.get("global_settings"), Mapping)
        else []
    )
    if not targets:
        return _check("captions", "skip", "storyboard declares no output targets")
    captions_dir = job_dir / "captions"
    missing: list[str] = []
    found: list[str] = []
    for target in targets:
        aliases = _PROFILE_ALIASES.get(str(target), (str(target),))
        candidates = [captions_dir / f"{alias}.srt" for alias in aliases]
        candidates += [captions_dir / f"{alias}.vtt" for alias in aliases]
        existing = next((path for path in candidates if path.is_file()), None)
        if existing is None:
            missing.append(str(target))
        else:
            found.append(existing.name)
    if missing:
        return _check("captions", "fail", "missing caption files for " + ", ".join(missing))
    return _check("captions", "pass", "found " + ", ".join(found))


def _metadata_check(
    storyboard: Mapping[str, Any], job_dir: Path, metadata: Mapping[str, Any] | str | Path | None
) -> dict[str, str]:
    if metadata is None:
        path = job_dir / "package" / "metadata.json"
        if not path.is_file():
            return _check("metadata", "fail", "package/metadata.json is missing")
        try:
            metadata = _load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            return _check("metadata", "fail", f"metadata is not valid JSON: {exc}")
    else:
        try:
            metadata = _load_json(metadata)
        except (OSError, json.JSONDecodeError) as exc:
            return _check("metadata", "fail", f"metadata is not valid JSON: {exc}")
    if metadata is None:
        return _check("metadata", "fail", "metadata is empty")

    required = ("titles", "description", "tags", "chapters", "disclosure", "upload_checklist")
    missing = [key for key in required if key not in metadata]
    malformed: list[str] = []
    if "titles" in metadata:
        if not isinstance(metadata["titles"], list):
            malformed.append("titles must be a list")
        elif not metadata["titles"] or not all(isinstance(title, str) and title.strip() for title in metadata["titles"]):
            malformed.append("titles must contain non-empty strings")
    if "description" in metadata and not isinstance(metadata["description"], str):
        malformed.append("description must be a string")
    elif isinstance(metadata.get("description"), str) and not metadata["description"].strip():
        malformed.append("description must not be empty")
    if "tags" in metadata and not isinstance(metadata["tags"], list):
        malformed.append("tags must be a list")
    chapters = metadata.get("chapters")
    if "chapters" in metadata:
        if not isinstance(chapters, list):
            malformed.append("chapters must be a list")
        else:
            for index, chapter in enumerate(chapters):
                if not isinstance(chapter, Mapping) or not isinstance(chapter.get("start_s"), (int, float)) or not isinstance(chapter.get("title"), str):
                    malformed.append(f"chapters[{index}] must include start_s and title")
    disclosure = metadata.get("disclosure")
    if "disclosure" in metadata:
        if not isinstance(disclosure, Mapping) or not isinstance(disclosure.get("required"), bool):
            malformed.append("disclosure must include boolean required")
        elif "reason" not in disclosure:
            malformed.append("disclosure must include reason")
    if "upload_checklist" in metadata and not isinstance(metadata["upload_checklist"], list):
        malformed.append("upload_checklist must be a list")

    if not missing and isinstance(metadata.get("description"), str):
        description = metadata["description"]
        if "{" in description or "}" in description:
            malformed.append("description contains unresolved URL placeholders")
        urls = re.findall(r"https?://[^\s)]+", description)
        for url in urls:
            query = parse_qs(urlparse(url.rstrip(".," )).query)
            missing_utm = [key for key in ("utm_source", "utm_medium", "utm_campaign") if key not in query]
            if missing_utm:
                malformed.append(f"description URL lacks {','.join(missing_utm)}: {url}")

    realistic = any(
        isinstance(scene, Mapping) and bool(scene.get("realistic_recreation"))
        for scene in storyboard.get("scenes", [])
    )
    if realistic and isinstance(disclosure, Mapping) and disclosure.get("required") is not True:
        malformed.append("disclosure.required must be true for realistic_recreation")

    if missing or malformed:
        parts: list[str] = []
        if missing:
            parts.append("missing=" + ",".join(missing))
        if malformed:
            parts.append("invalid=" + "; ".join(malformed))
        return _check("metadata", "fail", "; ".join(parts))
    return _check("metadata", "pass", "metadata contract complete")


def _silent_gap_check(
    storyboard: Mapping[str, Any], words_by_scene: Mapping[int, Mapping[str, Any]]
) -> dict[str, str]:
    if not words_by_scene:
        return _check("silent_gaps", "skip", "no valid words artifacts to inspect")
    scenes = [
        scene for scene in storyboard.get("scenes", []) if isinstance(scene, Mapping)
    ]
    scenes.sort(key=lambda scene: int(scene.get("scene_id", 0)))
    gaps: list[str] = []
    previous_end: float | None = None
    previous_scene_id: int | None = None
    for scene in scenes:
        try:
            scene_id = int(scene.get("scene_id"))
        except (TypeError, ValueError):
            continue
        data = words_by_scene.get(scene_id)
        if data is None:
            continue
        words = data.get("words", [])
        if not words:
            continue
        try:
            duration = float(data.get("duration_s", 0))
            last_end = float(words[-1]["end_s"])
        except (KeyError, TypeError, ValueError):
            continue
        if previous_end is not None and previous_scene_id is not None:
            trailing = previous_end
            # A words artifact uses a scene-local clock.  Any unfilled tail in
            # the previous scene is therefore the measurable boundary gap.
            if trailing > 0.5:
                gaps.append(f"scene {previous_scene_id} trailing gap {trailing:g}s before scene {scene_id}")
        for left, right in zip(words, words[1:]):
            try:
                gap = float(right["start_s"]) - float(left["end_s"])
            except (KeyError, TypeError, ValueError):
                continue
            if gap > 0.5:
                gaps.append(f"scene {scene_id} word gap {gap:g}s")
        try:
            previous_end = max(0.0, duration - last_end)
        except (TypeError, ValueError):
            previous_end = None
        previous_scene_id = scene_id
    if gaps:
        return _check("silent_gaps", "fail", "; ".join(gaps))
    return _check("silent_gaps", "pass", "no gaps over 500ms")


def run_qc_checks(
    storyboard: Mapping[str, Any] | str | Path,
    job_dir: str | Path,
    compositor_summary: Mapping[str, Any] | str | Path | None = None,
    *,
    manifest: Mapping[str, Any] | str | Path | None = None,
    metadata: Mapping[str, Any] | str | Path | None = None,
    duration_probe: Callable[[Path], float] | None = None,
    write_report: bool = True,
) -> QCResult:
    """Run deterministic QC and optionally persist ``qc/report.json``.

    ``compositor_summary`` is the measured summary emitted by the compositor;
    it is deliberately an input rather than a value inferred from a filename.
    """

    loaded_storyboard = _load_json(storyboard)
    if loaded_storyboard is None:
        raise ValueError("storyboard is empty")
    root = Path(job_dir)
    summary = _load_json(compositor_summary)
    duration = _duration_check(
        loaded_storyboard,
        root,
        manifest,
        compositor_summary=summary,
        duration_probe=duration_probe,
    )
    words_check, words_by_scene = _words_coverage(loaded_storyboard, root)
    checks = [
        duration,
        words_check,
        _loudness_check(root, summary),
        _caption_check(loaded_storyboard, root),
        _metadata_check(loaded_storyboard, root, metadata),
        _silent_gap_check(loaded_storyboard, words_by_scene),
    ]
    checks.extend(run_visual_qc(loaded_storyboard, root)["checks"])
    result: QCResult = {
        "overall": "pass" if all(check["status"] != "fail" for check in checks) else "fail",
        "checks": checks,
    }
    if write_report:
        write_qc_report(root, result)
    return result


def write_qc_report(job_dir: str | Path, report: QCResult) -> Path:
    """Persist a QC report under the job artifact tree and return its path."""

    path = Path(job_dir) / "qc" / "report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


run_qc = run_qc_checks
qc = run_qc_checks
run_checks = run_qc_checks
check_qc = run_qc_checks


__all__ = [
    "QCResult",
    "check_qc",
    "qc",
    "run_checks",
    "run_qc",
    "run_qc_checks",
    "write_qc_report",
]
