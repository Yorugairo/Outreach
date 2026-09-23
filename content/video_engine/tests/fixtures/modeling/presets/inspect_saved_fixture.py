"""Read-only Blender-side reopen inspector for persisted native preset files."""

import argparse
import importlib
import json
import sys
import types
from pathlib import Path


def arguments_after_separator() -> list[str]:
    if "--" not in sys.argv:
        raise RuntimeError("expected inspector arguments after Blender's -- separator")
    return sys.argv[sys.argv.index("--") + 1:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(arguments_after_separator())

    repository = Path(__file__).resolve().parents[6]
    package_path = repository / "content/video_engine/src/modeling/blender"
    package = types.ModuleType("_t4a_blender")
    package.__path__ = [str(package_path)]
    sys.modules[package.__name__] = package
    authoring = importlib.import_module("_t4a_blender.authoring")

    report = authoring.collect_scene_state()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
