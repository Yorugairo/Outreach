"""Run a hash-pinned, offline Blender mesh audit and write a JSON receipt.

Example (all paths are rooted at ``--root``)::

    python content/video_engine/scripts/model_mesh_audit.py --root . \
      --input content/video_engine/assets/modeling/native/fighter-family-v1.blend \
      --sha256 <64-hex-digest> --output content/video_engine/review/model-engines/benchmark-v1/art/mesh-audit/native.json \
      --blender "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe"

Blender starts in offline/factory mode with embedded auto-run disabled. The
input is opened or imported in memory and is never saved by this command.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from content.video_engine.src.modeling.blender.mesh_audit import (  # noqa: E402
    MeshAuditError,
    resolve_receipt_path,
    validate_source,
)


BLENDER_WORKER = REPO_ROOT / "content/video_engine/src/modeling/blender/mesh_audit.py"


def execute_audit(
    *,
    root: str | Path,
    input_path: str | Path,
    expected_sha256: str,
    output_path: str | Path,
    blender_path: str | Path,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    source = validate_source(root, input_path, expected_sha256)
    receipt_path = resolve_receipt_path(source["root"], output_path, source["path"])
    try:
        blender = Path(blender_path).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise MeshAuditError(f"Blender executable is unavailable: {blender_path}") from exc
    if not blender.is_file():
        raise MeshAuditError(f"Blender executable is not a file: {blender_path}")
    if not BLENDER_WORKER.is_file():
        raise MeshAuditError(f"Blender audit worker is unavailable: {BLENDER_WORKER}")

    profile = receipt_path.parent / ".blender-user-resources"
    resource_paths = {
        "BLENDER_USER_RESOURCES": profile,
        "BLENDER_USER_CONFIG": profile / "config",
        "BLENDER_USER_SCRIPTS": profile / "scripts",
        "BLENDER_USER_DATAFILES": profile / "datafiles",
        "BLENDER_USER_EXTENSIONS": profile / "extensions",
    }
    for path in resource_paths.values():
        path.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["PYTHONNOUSERSITE"] = "1"
    environment.update({key: str(value) for key, value in resource_paths.items()})

    command = [
        str(blender),
        "--background",
        "--factory-startup",
        "--offline-mode",
        "--disable-autoexec",
        "--python-exit-code",
        "17",
        "--python",
        str(BLENDER_WORKER),
        "--",
        "--root",
        str(source["root"]),
        "--input",
        source["relative_path"],
        "--sha256",
        source["sha256"],
        "--output",
        receipt_path.relative_to(source["root"]).as_posix(),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=source["root"],
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise MeshAuditError(f"Blender mesh audit exceeded {timeout_seconds} seconds") from exc
    except OSError as exc:
        raise MeshAuditError(f"Blender process could not be started: {exc}") from exc
    if completed.returncode != 0:
        details = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
        if len(details) > 6000:
            details = details[-6000:]
        raise MeshAuditError(
            f"Blender mesh audit failed with exit code {completed.returncode}"
            + (f":\n{details}" if details else "")
        )
    if not receipt_path.is_file():
        raise MeshAuditError("Blender completed without writing the requested receipt")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise MeshAuditError("Blender wrote an invalid JSON receipt") from exc
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema") != "model_mesh_audit.v1"
        or not isinstance(receipt.get("source"), dict)
        or receipt["source"].get("sha256") != source["sha256"]
    ):
        raise MeshAuditError("Blender receipt does not match the validated source")
    return receipt


def _arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a hash-pinned .blend or self-contained .glb offline.")
    parser.add_argument("--root", required=True, help="caller-owned root; input and receipt must stay inside it")
    parser.add_argument("--input", required=True, help="source model path, absolute or relative to --root")
    parser.add_argument("--sha256", required=True, help="expected SHA-256 of the exact source bytes")
    parser.add_argument("--output", required=True, help="JSON receipt path, absolute or relative to --root")
    parser.add_argument("--blender", required=True, help="Blender 5.2.2 executable")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _arguments(argv)
    try:
        receipt = execute_audit(
            root=args.root,
            input_path=args.input,
            expected_sha256=args.sha256,
            output_path=args.output,
            blender_path=args.blender,
            timeout_seconds=args.timeout_seconds,
        )
    except MeshAuditError as exc:
        print(f"model mesh audit failed: {exc}", file=sys.stderr)
        return 2
    summary = receipt["summary"]
    print(
        "\n".join(
            (
                f"receipt={Path(args.output)}",
                f"source_sha256={receipt['source']['sha256']}",
                f"blender={receipt['tool']['version']}",
                f"all_scene_mesh_objects={summary['all_scene']['mesh_object_count']}",
                f"all_scene_stored_vertices={summary['all_scene']['stored']['vertices']}",
                f"all_scene_evaluated_vertices={summary['all_scene']['evaluated']['vertices']}",
                f"render_eligible_mesh_objects={summary['render_eligible']['mesh_object_count']}",
                f"render_eligible_stored_vertices={summary['render_eligible']['stored']['vertices']}",
                f"render_eligible_evaluated_vertices={summary['render_eligible']['evaluated']['vertices']}",
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
