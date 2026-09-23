"""Run or re-verify the pinned generic-Rigify deformation stress diagnostic."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
WORKER = ROOT / "content/video_engine/src/modeling/blender/deformation_stress.py"
BENCHMARK = ROOT / "content/video_engine/tests/fixtures/modeling/baseline/benchmark-inputs.json"
_RUN_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.video_engine.src.modeling.blender.deformation_stress import (  # noqa: E402
    DeformationStressError,
    MAX_RECEIPT_BYTES,
    REVIEW_RELATIVE,
    SOURCE_RELATIVE,
    SOURCE_SHA256,
    SUPPORTED_BLENDER_BUILD_HASH,
    SUPPORTED_BLENDER_VERSION,
    _reparse_point,
    sha256_file,
    validate_receipt,
)


def pinned_blender() -> Path:
    try:
        benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        item = benchmark["tools"]["blender"]
        path = Path(item["path"])
        if item["version"] != SUPPORTED_BLENDER_VERSION or item["build_hash"] != SUPPORTED_BLENDER_BUILD_HASH:
            raise DeformationStressError("baseline manifest does not pin the expected Blender build")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise DeformationStressError(f"cannot read the pinned Blender executable: {exc}") from exc
    if not path.is_file() or _reparse_point(path):
        raise DeformationStressError(f"pinned Blender executable unavailable or unsafe: {path}")
    return path.resolve(strict=True)


def _path_chain_has_reparse(path: Path) -> bool:
    current = path
    while True:
        if current.exists() and _reparse_point(current):
            return True
        if current.parent == current:
            return False
        current = current.parent


def _review_root() -> Path:
    root = ROOT / REVIEW_RELATIVE
    root.mkdir(parents=True, exist_ok=True)
    if _path_chain_has_reparse(root):
        raise DeformationStressError("review quarantine contains a symlink or junction")
    return root.resolve(strict=True)


def _create_run_directory(run_name: str) -> tuple[Path, Path]:
    if not _RUN_NAME.fullmatch(run_name):
        raise DeformationStressError("run name must be a lowercase slug without path separators")
    review_root = _review_root()
    output = review_root / run_name
    if output.exists():
        raise DeformationStressError(f"run output already exists: {run_name}")
    try:
        output.mkdir()
    except OSError as exc:
        raise DeformationStressError(f"could not create a unique review run: {exc}") from exc
    if output.resolve(strict=True).parent != review_root or _path_chain_has_reparse(output):
        raise DeformationStressError("new run directory escaped or redirected the review quarantine")
    return review_root, output.resolve(strict=True)


def _blender_environment(output: Path) -> dict[str, str]:
    """Pass a small isolated Windows runtime environment to offline Blender."""
    system_root = Path(os.environ.get("SystemRoot") or os.environ.get("WINDIR") or "C:/Windows")
    resources = output / "blender-user-resources"
    temporary = output / "tmp"
    for path in (
        temporary,
        resources,
        resources / "config",
        resources / "scripts",
        resources / "datafiles",
        resources / "extensions",
        resources / "appdata",
        resources / "localappdata",
    ):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "SystemRoot": str(system_root),
        "WINDIR": str(system_root),
        "PATH": os.pathsep.join((str(system_root / "System32"), str(system_root))),
        "TEMP": str(temporary),
        "TMP": str(temporary),
        "USERPROFILE": str(resources),
        "APPDATA": str(resources / "appdata"),
        "LOCALAPPDATA": str(resources / "localappdata"),
        "PYTHONNOUSERSITE": "1",
        "BLENDER_USER_RESOURCES": str(resources),
        "BLENDER_USER_CONFIG": str(resources / "config"),
        "BLENDER_USER_SCRIPTS": str(resources / "scripts"),
        "BLENDER_USER_DATAFILES": str(resources / "datafiles"),
        "BLENDER_USER_EXTENSIONS": str(resources / "extensions"),
    }


def _load_receipt(path: Path) -> dict[str, Any]:
    if not path.is_file() or _reparse_point(path) or path.stat().st_size > MAX_RECEIPT_BYTES:
        raise DeformationStressError(f"missing, unsafe, or oversized receipt: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DeformationStressError(f"receipt is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise DeformationStressError("receipt root must be an object")
    return value


def execute_probe(run_name: str, *, blender_path: Path | None = None) -> dict[str, Any]:
    """Create one new quarantined run, then re-open and recompute its receipt."""
    source = ROOT / SOURCE_RELATIVE
    if not source.is_file() or _reparse_point(source) or sha256_file(source) != SOURCE_SHA256:
        raise DeformationStressError("source hash differs from the pinned read-only fighter-family v1.1 scene")
    blender = blender_path or pinned_blender()
    if not blender.is_file() or _reparse_point(blender):
        raise DeformationStressError(f"Blender executable unavailable or unsafe: {blender}")
    review_root, output = _create_run_directory(run_name)
    env = _blender_environment(output)
    command = [
        str(blender),
        "--background",
        "--factory-startup",
        "--offline-mode",
        "--disable-autoexec",
        "--python-exit-code",
        "17",
        "--python",
        str(WORKER),
        "--",
        "--source",
        str(source.resolve(strict=True)),
        "--output",
        str(output),
    ]
    try:
        process = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DeformationStressError(f"Blender deformation run could not complete: {exc}") from exc
    (output / "blender.stdout.log").write_text(process.stdout, encoding="utf-8")
    (output / "blender.stderr.log").write_text(process.stderr, encoding="utf-8")
    if sha256_file(source) != SOURCE_SHA256:
        raise DeformationStressError("pinned source hash changed during the Blender run")
    if process.returncode != 0:
        raise DeformationStressError(f"Blender exited {process.returncode}; see logs under {output}")
    receipt = _load_receipt(output / "receipt.json")
    validate_receipt(receipt, output, review_root=review_root)
    receipt["run_dir"] = str(output)
    return receipt


def verify_run(run_name: str) -> dict[str, Any]:
    if not _RUN_NAME.fullmatch(run_name):
        raise DeformationStressError("run name must be a lowercase slug without path separators")
    review_root = _review_root()
    output = review_root / run_name
    if not output.is_dir() or output.resolve(strict=True).parent != review_root:
        raise DeformationStressError("review run is missing or outside its quarantine")
    receipt = _load_receipt(output / "receipt.json")
    validate_receipt(receipt, output, review_root=review_root)
    receipt["run_dir"] = str(output.resolve(strict=True))
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--run", help="create a new immutable review-only run")
    action.add_argument("--verify", help="reopen and recompute an existing run")
    args = parser.parse_args(argv)
    try:
        receipt = execute_probe(args.run) if args.run else verify_run(args.verify)
    except DeformationStressError as exc:
        print(f"MODEL_DEFORMATION_STRESS_ERROR: {exc}", file=sys.stderr)
        return 1
    compact = {
        "verdict": receipt["verdict"],
        "run_dir": receipt["run_dir"],
        "source_sha256": receipt["source"]["sha256_after"],
        "regions": {
            name: {
                "selected_vertices": data["selection"]["retained_region_vertices"],
                "selected_triangles": data["selection"]["retained_region_triangles"],
                "frame_27_or_52_total_area_ratio": data["measurements"][
                    "27" if name == "shoulder_elbow" else "52"
                ]["triangle_area_total_ratio_to_frame_1"],
            }
            for name, data in receipt["regions"].items()
        },
    }
    print(json.dumps(compact, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
