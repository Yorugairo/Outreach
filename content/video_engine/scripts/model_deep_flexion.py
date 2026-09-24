"""Run or independently verify the pinned T5a.5 deep-flexion comparison."""

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
WORKER = ROOT / "content/video_engine/src/modeling/blender/deep_flexion.py"
BENCHMARK = ROOT / "content/video_engine/tests/fixtures/modeling/baseline/benchmark-inputs.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.video_engine.src.modeling.blender import deep_flexion as diagnostic  # noqa: E402


def pinned_blender() -> Path:
    try:
        benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        item = benchmark["tools"]["blender"]
        path = Path(item["path"])
        if (
            item["version"] != diagnostic.SUPPORTED_BLENDER_VERSION
            or item["build_hash"] != diagnostic.SUPPORTED_BLENDER_BUILD_HASH
        ):
            raise diagnostic.DeepFlexionError("benchmark manifest does not pin the required Blender build")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise diagnostic.DeepFlexionError(f"cannot read the pinned Blender executable: {exc}") from exc
    if not path.is_file() or diagnostic._reparse_point(path):
        raise diagnostic.DeepFlexionError(f"pinned Blender executable unavailable or unsafe: {path}")
    return path.resolve(strict=True)


def _review_root(*, create: bool = False) -> Path:
    root = ROOT / diagnostic.REVIEW_RELATIVE
    if diagnostic._path_chain_has_reparse(root):
        raise diagnostic.DeepFlexionError("deep-flexion review quarantine contains a symlink or junction")
    if create:
        try:
            root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise diagnostic.DeepFlexionError(f"could not create the deep-flexion review quarantine: {exc}") from exc
    if not root.is_dir():
        raise diagnostic.DeepFlexionError("deep-flexion review quarantine is missing or not a directory")
    if diagnostic._path_chain_has_reparse(root):
        raise diagnostic.DeepFlexionError("deep-flexion review quarantine contains a symlink or junction")
    return root.resolve(strict=True)


def _create_run_directory(run_name: str) -> tuple[Path, Path]:
    if not diagnostic.RUN_NAME.fullmatch(run_name):
        raise diagnostic.DeepFlexionError("run name must be a lowercase slug without path separators")
    review_root = _review_root(create=True)
    output = review_root / run_name
    if output.exists():
        raise diagnostic.DeepFlexionError(f"review run already exists: {run_name}")
    try:
        output.mkdir()
    except OSError as exc:
        raise diagnostic.DeepFlexionError(f"could not create a unique review run: {exc}") from exc
    if output.resolve(strict=True).parent != review_root or diagnostic._path_chain_has_reparse(output):
        raise diagnostic.DeepFlexionError("new run directory escaped or redirected the quarantine")
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


def _load_json(path: Path, *, max_bytes: int = diagnostic.MAX_RECEIPT_BYTES) -> dict[str, Any]:
    if not path.is_file() or diagnostic._reparse_point(path) or path.stat().st_size > max_bytes:
        raise diagnostic.DeepFlexionError(f"missing, unsafe, or oversized JSON artifact: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise diagnostic.DeepFlexionError(f"invalid JSON artifact: {path.name}") from exc
    if not isinstance(value, dict):
        raise diagnostic.DeepFlexionError(f"JSON artifact must be an object: {path.name}")
    return value


def _log_meta(path: Path, name: str) -> dict[str, Any]:
    if not path.is_file() or diagnostic._reparse_point(path) or path.stat().st_size > diagnostic.MAX_LOG_BYTES:
        raise diagnostic.DeepFlexionError(f"missing, unsafe, or oversized Blender log: {name}")
    return {"path": name, "sha256": diagnostic.sha256_file(path), "bytes": path.stat().st_size}


def _write_attempt(
    output: Path,
    *,
    return_code: int | None,
    stdout_meta: dict[str, Any],
    stderr_meta: dict[str, Any],
    error: str | None,
    worker_receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    path = output / "attempt.json"
    if path.is_file() and not diagnostic._reparse_point(path):
        try:
            attempt = _load_json(path)
        except diagnostic.DeepFlexionError:
            attempt = {}
    else:
        attempt = {}
    complete = return_code == 0 and worker_receipt is not None
    observed_angles = (
        worker_receipt.get("pose_states", {})
        if worker_receipt is not None
        else attempt.get("pose_searches", {})
    )
    preserved_error = error or attempt.get("error")
    if preserved_error is None and return_code not in (None, 0):
        preserved_error = f"Blender exited {return_code}; see blender.stderr.log for the exact failure"
    attempt.update(
        {
            "schema": diagnostic.ATTEMPT_SCHEMA,
            "status": "complete" if complete else "failed",
            "source_sha256": diagnostic.SOURCE_SHA256,
            "target_bend_degrees": diagnostic.TARGET_BEND_DEGREES,
            "observed_angles_deg": observed_angles,
            "return_code": return_code,
            "error": preserved_error,
            "execution": {
                "offline": True,
                "factory_startup": True,
                "embedded_scripts": "disabled",
                "isolated_user_resources": True,
                "logs": {"stdout": stdout_meta, "stderr": stderr_meta},
            },
        }
    )
    diagnostic._write_json(path, attempt)
    return {"path": path.name, "sha256": diagnostic.sha256_file(path), "bytes": path.stat().st_size}


def execute_probe(run_name: str, *, blender_path: Path | None = None) -> dict[str, Any]:
    """Create one immutable quarantined run and independently re-open its receipt."""
    source = ROOT / diagnostic.SOURCE_RELATIVE
    diagnostic._assert_pinned_source(source)
    blender = blender_path or pinned_blender()
    if not blender.is_file() or diagnostic._reparse_point(blender):
        raise diagnostic.DeepFlexionError(f"Blender executable unavailable or unsafe: {blender}")
    review_root, output = _create_run_directory(run_name)
    environment = _blender_environment(output)
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
    stdout_path = output / "blender.stdout.log"
    stderr_path = output / "blender.stderr.log"
    return_code: int | None = None
    process_error: str | None = None
    with stdout_path.open("xb") as stdout_stream, stderr_path.open("xb") as stderr_stream:
        try:
            process = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                stdout=stdout_stream,
                stderr=stderr_stream,
                timeout=900,
                check=False,
            )
            return_code = process.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            process_error = f"{type(exc).__name__}: {exc}"
    stdout_meta = _log_meta(stdout_path, "blender.stdout.log")
    stderr_meta = _log_meta(stderr_path, "blender.stderr.log")
    worker_receipt: dict[str, Any] | None = None
    receipt_path = output / "receipt.json"
    if receipt_path.is_file() and not diagnostic._reparse_point(receipt_path):
        try:
            worker_receipt = _load_json(receipt_path)
        except diagnostic.DeepFlexionError as exc:
            process_error = process_error or str(exc)
    if diagnostic.sha256_file(source) != diagnostic.SOURCE_SHA256:
        process_error = process_error or "pinned source SHA changed during Blender execution"
        return_code = return_code if return_code not in (None, 0) else 1
    attempt_meta = _write_attempt(
        output,
        return_code=return_code,
        stdout_meta=stdout_meta,
        stderr_meta=stderr_meta,
        error=process_error,
        worker_receipt=worker_receipt,
    )
    if return_code != 0 or worker_receipt is None or process_error is not None:
        reason = process_error or (f"Blender exited {return_code}" if return_code != 0 else "Blender exit 0 had no complete worker receipt")
        raise diagnostic.DeepFlexionError(f"deep-flexion run failed; evidence preserved at {output}: {reason}")

    worker_receipt["execution"] = {
        "return_code": return_code,
        "offline": True,
        "factory_startup": True,
        "embedded_scripts": "disabled",
        "isolated_user_resources": True,
        "logs": {"stdout": stdout_meta, "stderr": stderr_meta},
    }
    worker_receipt["attempt"] = attempt_meta
    diagnostic._write_json(receipt_path, worker_receipt)
    if receipt_path.stat().st_size > diagnostic.MAX_RECEIPT_BYTES:
        raise diagnostic.DeepFlexionError(f"verified receipt exceeds size limit; evidence preserved at {output}")
    diagnostic.validate_receipt(worker_receipt, output, review_root=review_root)
    worker_receipt["run_dir"] = str(output)
    return worker_receipt


def verify_run(run_name: str) -> dict[str, Any]:
    if not diagnostic.RUN_NAME.fullmatch(run_name):
        raise diagnostic.DeepFlexionError("run name must be a lowercase slug without path separators")
    review_root = _review_root()
    output = review_root / run_name
    if (
        not output.is_dir()
        or diagnostic._path_chain_has_reparse(output)
        or output.resolve(strict=True).parent != review_root
    ):
        raise diagnostic.DeepFlexionError("review run is missing or outside the safe quarantine")
    receipt = _load_json(output / "receipt.json")
    diagnostic.validate_receipt(receipt, output, review_root=review_root)
    receipt["run_dir"] = str(output.resolve(strict=True))
    return receipt


def _compact(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": receipt["verdict"],
        "run_dir": receipt.get("run_dir"),
        "source_sha256": receipt["source"]["sha256_after"],
        "bend_degrees": {
            pose: {
                joint: values["bend_degrees"]
                for joint, values in receipt["pose_states"][pose].items()
            }
            for pose in ("neutral", "right_elbow_deep", "left_knee_deep")
        },
        "deep_patch_extrema": {
            joint: {
                configuration: {
                    "area_ratio_min": receipt["regions"][joint]["measurements"][configuration]["deep_flexion"]["triangle_area_ratio"]["min"],
                    "area_ratio_max": receipt["regions"][joint]["measurements"][configuration]["deep_flexion"]["triangle_area_ratio"]["max"],
                    "edge_ratio_min": receipt["regions"][joint]["measurements"][configuration]["deep_flexion"]["edge_length_ratio"]["min"],
                    "edge_ratio_max": receipt["regions"][joint]["measurements"][configuration]["deep_flexion"]["edge_length_ratio"]["max"],
                }
                for configuration in diagnostic.CONFIGURATIONS
            }
            for joint in diagnostic.REGIONS
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--run", help="create a new, immutable review-only run")
    action.add_argument("--verify", help="reopen and recompute an existing receipt")
    args = parser.parse_args(argv)
    try:
        receipt = execute_probe(args.run) if args.run else verify_run(args.verify)
    except diagnostic.DeepFlexionError as exc:
        print(f"MODEL_DEEP_FLEXION_ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(_compact(receipt), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
