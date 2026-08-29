"""Write the non-mutating P32 Gate-A evidence/cadence baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.video_engine.src.services.full_episode_evidence_coverage import (
    CoverageCompilationError,
    validate_full_episode_evidence_coverage,
    write_full_episode_evidence_coverage,
)


DEFAULT_PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    try:
        paths = write_full_episode_evidence_coverage(args.project, args.output)
        payload = json.loads(paths["coverage"].read_text(encoding="utf-8"))
        errors = validate_full_episode_evidence_coverage(payload)
    except CoverageCompilationError as exc:
        raise SystemExit(f"P32 coverage compilation failed: {exc}") from exc
    if errors:
        raise SystemExit("P32 coverage validation failed: " + "; ".join(errors))
    print(json.dumps({key: str(value) for key, value in paths.items()} | {"artifact_hash": payload["artifact_hash"]}, indent=2))


if __name__ == "__main__":
    main()
