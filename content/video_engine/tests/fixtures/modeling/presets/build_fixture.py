"""Blender-side build driver for the real, offline MPFB/Rigify acceptance test."""

import argparse
import importlib
import json
import sys
import types
from pathlib import Path


def arguments_after_separator() -> list[str]:
    if "--" not in sys.argv:
        raise RuntimeError("expected driver arguments after Blender's -- separator")
    return sys.argv[sys.argv.index("--") + 1:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controls", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--renders", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args(arguments_after_separator())

    repository = Path(__file__).resolve().parents[6]
    package_path = repository / "content/video_engine/src/modeling/blender"
    package = types.ModuleType("_t4a_blender")
    package.__path__ = [str(package_path)]
    sys.modules[package.__name__] = package
    authoring = importlib.import_module("_t4a_blender.authoring")

    document = json.loads(args.controls.read_text(encoding="utf-8"))
    result = authoring.build_native_preset(args.output, controls=document["controls"], render_dir=args.renders)
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
