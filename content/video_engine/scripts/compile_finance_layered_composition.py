"""Compile the P21 sentence-native layered finance composition plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from content.video_engine.src.services.finance_channel import (  # noqa: E402
    file_sha256,
    validate_artifact,
    validate_finance_layered_composition_package,
)
from content.video_engine.src.services.finance_layered_composition import (  # noqa: E402
    compile_finance_layered_composition,
)


DEFAULT_PILOT = (
    REPO_ROOT
    / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def compile_plan(pilot_root: Path = DEFAULT_PILOT) -> dict:
    pilot_root = pilot_root.resolve()
    output = pilot_root / "edit/sentence-native-v1"
    ledger_path = output / "semantic-beat-ledger.v1.json"
    demand_path = output / "asset-demand.v1.json"
    words_path = pilot_root / "audio/canonical/history_episode_1_master.words.json"
    ledger, demand, words = _load(ledger_path), _load(demand_path), _load(words_path)
    return compile_finance_layered_composition(
        semantic_ledger=ledger,
        asset_demand=demand,
        word_timings=words,
        source_bindings={
            "semantic_beat_ledger": {
                "path": _repo_path(ledger_path),
                "sha256": file_sha256(ledger_path),
                "artifact_hash": ledger["artifact_hash"],
            },
            "asset_demand": {
                "path": _repo_path(demand_path),
                "sha256": file_sha256(demand_path),
                "artifact_hash": demand["artifact_hash"],
            },
            "word_timing": {"path": _repo_path(words_path), "sha256": file_sha256(words_path)},
        },
    )


def write_plan(pilot_root: Path = DEFAULT_PILOT) -> Path:
    plan = compile_plan(pilot_root)
    validate_artifact(plan)
    target = pilot_root.resolve() / "edit/sentence-native-v1/layered-composition-plan.v1.json"
    target.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    validate_finance_layered_composition_package(plan, REPO_ROOT)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    args = parser.parse_args()
    print(write_plan(args.pilot_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
