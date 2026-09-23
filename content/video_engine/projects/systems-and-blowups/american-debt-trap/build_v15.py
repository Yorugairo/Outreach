"""Build the frozen V15 first act against the editor-paused measured clock.

This is a thin episode adapter over the tested V13 builder.  It preserves the
original builder while binding the stabilized V15 narration, paused scratch
audio, 180.225-second sentence boundary and V15 shot table.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def _load_base():
    path = HERE / "build_v13.py"
    spec = importlib.util.spec_from_file_location("american_debt_trap_build_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load shared episode builder: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = _load_base()
BASE.BUILD_VERSION = "V15"
BASE.VIDEO_FORM = "long"
BASE.EPISODE_ID = "american-debt-trap-v15"
BASE.SCRIPT_PATH = REPO / "docs/research/runs/american-debt-trap-20260920/script-review/REVISED-V15-VO.txt"
BASE.SCRIPT_NAME = BASE.SCRIPT_PATH.name
BASE.SHOT_TABLE_NAME = "SHOT-TABLE-V15.py"
BASE.DEFAULT_BUILD_ROOT = HERE / "build-private/v15"
BASE.SEGMENT_TARGETS = {"pilot": 180.975}
BASE.TIMELINE_NAMES = {"pilot": "american-debt-trap-v15-pilot.timeline.json"}

PAUSED_CLOCK = HERE / "review-clock-v15-fast/timeline.json"
PAUSED_AUDIO = HERE / "review-clock-v15-fast/audio/episode-paused.mp3"
PREPARED_TAKE = HERE / "build-private/v15/_prepared-take"


def prepare_take() -> Path:
    """Materialize the editor-paused take in the builder's immutable input shape."""
    if not PAUSED_CLOCK.is_file() or not PAUSED_AUDIO.is_file():
        raise BASE.BuildInputError("V15 paused clock or paused audio is missing")
    payload = json.loads(PAUSED_CLOCK.read_text(encoding="utf-8"))
    words = payload.get("words")
    if not isinstance(words, list) or not words:
        raise BASE.BuildInputError("V15 paused clock has no words")
    converted = []
    for index, word in enumerate(words):
        try:
            converted.append({
                **word,
                "start_s": float(word["start"]),
                "end_s": float(word["end"]),
            })
        except (KeyError, TypeError, ValueError) as exc:
            raise BASE.BuildInputError(f"V15 paused word {index} is malformed") from exc
    PREPARED_TAKE.mkdir(parents=True, exist_ok=True)
    words_path = PREPARED_TAKE / "scratch-kokoro.words.json"
    words_path.write_text(
        json.dumps({"words": converted}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    shutil.copy2(PAUSED_AUDIO, PREPARED_TAKE / "scratch-kokoro.mp3")
    return PREPARED_TAKE


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build the quarantined V15 American Debt Trap first act")
    parser.add_argument("--build-dir", type=Path)
    parser.add_argument("--asset-manifest", type=Path, default=HERE / "ASSET-CANDIDATES.json")
    parser.add_argument("--check-inputs", action="store_true")
    args = parser.parse_args(argv)
    try:
        take = prepare_take()
        if args.check_inputs:
            blockers = BASE.check_inputs(
                take_dir=take,
                script_path=BASE.SCRIPT_PATH,
                asset_manifest=args.asset_manifest,
            )
            for blocker in blockers:
                print(f"[FAIL] {blocker}")
            if not blockers:
                print("[PASS] frozen V15 narration, paused clock, audio and 18 approved candidates are aligned")
            return 1 if blockers else 0
        return BASE.build(
            segment="pilot",
            take_dir=take,
            build_dir=args.build_dir,
            asset_manifest=args.asset_manifest,
        )
    except (BASE.BuildInputError, OSError) as exc:
        print(f"[FAIL] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
