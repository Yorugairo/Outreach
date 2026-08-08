"""HyperFrames unit lane — compile and render short/caption units.

The service accepts an asset-ID-only unit contract bound to canonical
narration word timings.  It never decides what the unit should say, never
invents timing, and never receives raw renderer paths inside the contract.
The HyperFrames CLI executes the compiled composition; this module validates,
resolves approved assets, compiles deterministic HTML, and verifies output
duration against the narration clock.

v1 limitation (recorded in docs/content-video-engine/19-HYPERFRAMES-LANE.md):
units render as silent visual builds; narration audio muxing remains the
compositor's job per the renderer-ownership table.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.asset_resolver import file_sha256

HYPERFRAMES_UNIT_VERSION = "hyperframes_unit.v1"
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = _VIDEO_ENGINE_ROOT.parents[1]
_DEFAULT_SCHEMA_PATH = _VIDEO_ENGINE_ROOT / "configs" / "hyperframes_unit.schema.json"
_DEFAULT_PROJECT_DIR = _VIDEO_ENGINE_ROOT / "hyperframes"

_PLATE_MIN_HOLD_S = 2.0
_PLATE_MAX_HOLD_S = 6.0
_TIMELINE_TOLERANCE_S = 0.001
_DURATION_DRIFT_RATIO = 0.02
_CAPTION_GROUP_WORDS = 4
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_APPROVED_REVIEW_STATUSES = {"rights_reviewed"}

_PROFILES = {
    "landscape": {"width": 1920, "height": 1080, "fps": 30},
    "vertical": {"width": 1080, "height": 1920, "fps": 30},
}


class HyperframesUnitError(ValueError):
    """Unit failed validation, asset resolution, or output verification."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid hyperframes unit")


class HyperframesCliError(RuntimeError):
    """The HyperFrames CLI invocation failed."""


@dataclass(frozen=True)
class HyperframesConfig:
    project_dir: Path = _DEFAULT_PROJECT_DIR
    version_pin: str = "0.7.101"
    timeout_s: int = 900

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "HyperframesConfig":
        import os

        source = os.environ if env is None else env
        project = source.get("HYPERFRAMES_PROJECT")
        return cls(
            project_dir=Path(project) if project else _DEFAULT_PROJECT_DIR,
            version_pin=source.get("HYPERFRAMES_VERSION_PIN", "0.7.101"),
            timeout_s=int(source.get("HYPERFRAMES_TIMEOUT_S", "900")),
        )

    def cli_command(self, *args: str) -> list[str]:
        npx = shutil.which("npx")
        if npx is None:
            raise HyperframesCliError("npx not found on PATH; Node.js is required")
        return [npx, "--yes", f"hyperframes@{self.version_pin}", *args]


@dataclass(frozen=True)
class CompiledUnit:
    unit_id: str
    composition_rel: str
    html_text: str
    asset_copies: tuple[tuple[Path, str], ...]
    duration_s: float
    profile: Mapping[str, int] = field(default_factory=dict)


def _load_schema(schema_path: Path | None = None) -> dict[str, Any]:
    path = schema_path or _DEFAULT_SCHEMA_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def validate_unit(unit: Mapping[str, Any], *, schema_path: Path | None = None) -> list[str]:
    """Return every violation; an empty list means the unit is valid."""

    validator = Draft7Validator(_load_schema(schema_path))
    errors = [
        f"schema: {'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(dict(unit)), key=lambda e: list(e.absolute_path))
    ]
    if errors:
        return errors

    words = unit["narration"]["words"]
    for index, word in enumerate(words):
        if word["end_s"] <= word["start_s"]:
            errors.append(f"narration: word {index} ('{word['w']}') has non-positive duration")
        if index and word["start_s"] < words[index - 1]["start_s"]:
            errors.append(f"narration: word {index} starts before word {index - 1}")

    plates = unit["plates"]
    for index, plate in enumerate(plates):
        hold = plate["end_s"] - plate["start_s"]
        if hold < _PLATE_MIN_HOLD_S - _TIMELINE_TOLERANCE_S:
            errors.append(
                f"plates: {plate['asset_id']} holds {hold:.3f}s (< {_PLATE_MIN_HOLD_S}s minimum)"
            )
        if hold > _PLATE_MAX_HOLD_S + _TIMELINE_TOLERANCE_S:
            errors.append(
                f"plates: {plate['asset_id']} holds {hold:.3f}s (> {_PLATE_MAX_HOLD_S}s hard ceiling)"
            )
        if index:
            gap = plate["start_s"] - plates[index - 1]["end_s"]
            if abs(gap) > _TIMELINE_TOLERANCE_S:
                errors.append(
                    f"plates: gap/overlap of {gap:.3f}s between plate {index - 1} and {index}"
                )

    total = plates[-1]["end_s"] - plates[0]["start_s"]
    if total > unit["output"]["max_duration_s"] + _TIMELINE_TOLERANCE_S:
        errors.append(
            f"plates: total {total:.3f}s exceeds output.max_duration_s {unit['output']['max_duration_s']}"
        )
    return errors


def resolve_assets(
    unit: Mapping[str, Any], *, repo_root: Path | None = None
) -> dict[str, dict[str, Any]]:
    """Bind plate asset ids to approved manifest entries; fail closed on any drift."""

    root = repo_root or _REPO_ROOT
    manifest_path = root / unit["manifest_path"]
    errors: list[str] = []
    if not manifest_path.is_file():
        raise HyperframesUnitError([f"manifest: {unit['manifest_path']} not found"])

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    review_status = str(manifest.get("review", {}).get("status", ""))
    if review_status not in _APPROVED_REVIEW_STATUSES:
        errors.append(
            f"manifest: review.status '{review_status}' is not an approved status"
        )

    by_id = {entry["id"]: entry for entry in manifest.get("assets", [])}
    resolved: dict[str, dict[str, Any]] = {}
    for plate in unit["plates"]:
        asset_id = plate["asset_id"]
        entry = by_id.get(asset_id)
        if entry is None:
            errors.append(f"assets: '{asset_id}' is not in the approved manifest")
            continue
        asset_path = root / entry["path"]
        suffix = asset_path.suffix.lower()
        if suffix not in _IMAGE_EXTENSIONS:
            errors.append(f"assets: '{asset_id}' has unsupported extension '{suffix}'")
            continue
        if not asset_path.is_file():
            errors.append(f"assets: '{asset_id}' file missing at {entry['path']}")
            continue
        actual = file_sha256(asset_path)
        if actual != entry.get("sha256"):
            errors.append(f"assets: '{asset_id}' sha256 mismatch vs manifest")
            continue
        resolved[asset_id] = {"path": asset_path, "sha256": actual, "suffix": suffix}

    if errors:
        raise HyperframesUnitError(errors)
    return resolved


def _caption_groups(words: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for start in range(0, len(words), _CAPTION_GROUP_WORDS):
        chunk = words[start : start + _CAPTION_GROUP_WORDS]
        groups.append(
            {
                "text": " ".join(word["w"] for word in chunk),
                "start_s": chunk[0]["start_s"],
                "end_s": chunk[-1]["end_s"],
            }
        )
    return groups


def compile_unit(
    unit: Mapping[str, Any],
    assets: Mapping[str, Mapping[str, Any]],
    *,
    config: HyperframesConfig | None = None,
) -> CompiledUnit:
    """Produce deterministic composition HTML + the asset copy plan."""

    cfg = config or HyperframesConfig()
    profile = _PROFILES[unit["layout"]["aspect"]]
    background = unit["layout"].get("background", "#0F0F12")
    unit_id = unit["unit_id"]
    plates = unit["plates"]
    t0 = plates[0]["start_s"]
    duration = round(plates[-1]["end_s"] - t0, 3)

    copies: list[tuple[Path, str]] = []
    plate_clips: list[str] = []
    for plate in plates:
        asset = assets[plate["asset_id"]]
        rel = f"assets/units/{unit_id}/{plate['asset_id']}{asset['suffix']}"
        copies.append((Path(asset["path"]), rel))
        start = round(plate["start_s"] - t0, 3)
        plate_duration = round(plate["end_s"] - plate["start_s"], 3)
        plate_clips.append(
            f'      <div class="clip plate" data-start="{start}" '
            f'data-duration="{plate_duration}" data-track-index="1">\n'
            f'        <img src="{rel}" alt="{html.escape(plate["asset_id"])}" />\n'
            f"      </div>"
        )

    caption_clips: list[str] = []
    if unit.get("captions", True):
        for group in _caption_groups(unit["narration"]["words"]):
            start = round(max(0.0, group["start_s"] - t0), 3)
            caption_duration = round(group["end_s"] - group["start_s"], 3)
            if caption_duration <= 0:
                continue
            caption_clips.append(
                f'      <div class="clip caption" data-start="{start}" '
                f'data-duration="{caption_duration}" data-track-index="2">'
                f"{html.escape(group['text'])}</div>"
            )

    html_text = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={profile['width']}, height={profile['height']}" />
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{
        width: {profile['width']}px;
        height: {profile['height']}px;
        overflow: hidden;
        background: {background};
      }}
      body {{ font-family: "Inter", sans-serif; }}
      .plate, .plate img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
      }}
      .caption {{
        position: absolute;
        left: 8%;
        right: 8%;
        bottom: 14%;
        text-align: center;
        color: #ffffff;
        font-size: {56 if unit['layout']['aspect'] == 'vertical' else 44}px;
        font-weight: 700;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.85);
      }}
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="unit-{unit_id}"
      data-start="0"
      data-duration="{duration}"
      data-width="{profile['width']}"
      data-height="{profile['height']}"
      data-fps="{profile['fps']}"
    >
{chr(10).join(plate_clips)}
{chr(10).join(caption_clips)}
    </div>
  </body>
</html>
"""
    return CompiledUnit(
        unit_id=unit_id,
        composition_rel=f"compositions/unit-{unit_id}.html",
        html_text=html_text,
        asset_copies=tuple(copies),
        duration_s=duration,
        profile=profile,
    )


def write_compiled(compiled: CompiledUnit, *, config: HyperframesConfig | None = None) -> Path:
    cfg = config or HyperframesConfig()
    project = cfg.project_dir
    for source, rel in compiled.asset_copies:
        destination = project / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    composition_path = project / compiled.composition_rel
    composition_path.parent.mkdir(parents=True, exist_ok=True)
    composition_path.write_text(compiled.html_text, encoding="utf-8", newline="\n")
    return composition_path


def _run_cli(args: Sequence[str], *, config: HyperframesConfig) -> subprocess.CompletedProcess:
    import os

    env = dict(os.environ)
    env.setdefault("HYPERFRAMES_SKIP_SKILLS", "1")
    result = subprocess.run(
        config.cli_command(*args),
        cwd=config.project_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=config.timeout_s,
    )
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip().splitlines()[-8:]
        raise HyperframesCliError(
            f"hyperframes {' '.join(args[:1])} failed (exit {result.returncode}): "
            + " | ".join(tail)
        )
    return result


def _probe_duration_s(path: Path) -> float:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise HyperframesCliError("ffprobe not found on PATH")
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise HyperframesCliError(f"ffprobe failed: {result.stderr.strip()[:200]}")
    return float(result.stdout.strip())


def render_unit(
    unit_path: str | Path,
    *,
    config: HyperframesConfig | None = None,
    repo_root: Path | None = None,
    dry_run: bool = False,
    skip_check: bool = False,
) -> dict[str, Any]:
    """Validate → resolve → compile → write → check → render → verify."""

    cfg = config or HyperframesConfig.from_env()
    unit = json.loads(Path(unit_path).read_text(encoding="utf-8"))

    violations = validate_unit(unit)
    if violations:
        raise HyperframesUnitError(violations)
    assets = resolve_assets(unit, repo_root=repo_root)
    compiled = compile_unit(unit, assets, config=cfg)

    summary: dict[str, Any] = {
        "unit_id": compiled.unit_id,
        "composition": compiled.composition_rel,
        "expected_duration_s": compiled.duration_s,
        "plates": len(unit["plates"]),
        "captions": bool(unit.get("captions", True)),
        "profile": dict(compiled.profile),
        "dry_run": dry_run,
    }
    if dry_run:
        return summary

    composition_path = write_compiled(compiled, config=cfg)
    summary["composition_path"] = str(composition_path)

    if not skip_check:
        _run_cli(["check"], config=cfg)
        summary["check"] = "pass"

    output_rel = f"renders/unit-{compiled.unit_id}.mp4"
    _run_cli(
        [
            "render",
            "-c",
            compiled.composition_rel,
            "-o",
            output_rel,
            "--quality",
            unit["output"]["quality"],
            "--quiet",
        ],
        config=cfg,
    )
    output_path = cfg.project_dir / output_rel
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise HyperframesCliError(f"render produced no output at {output_rel}")

    actual = _probe_duration_s(output_path)
    drift = abs(actual - compiled.duration_s) / max(compiled.duration_s, 0.001)
    summary.update(
        {
            "output_path": str(output_path),
            "actual_duration_s": round(actual, 3),
            "duration_drift_ratio": round(drift, 4),
        }
    )
    if drift > _DURATION_DRIFT_RATIO:
        raise HyperframesUnitError(
            [
                f"output: duration {actual:.3f}s drifts {drift:.1%} from expected "
                f"{compiled.duration_s:.3f}s (limit {_DURATION_DRIFT_RATIO:.0%})"
            ]
        )
    summary["qc"] = "pass"
    return summary
