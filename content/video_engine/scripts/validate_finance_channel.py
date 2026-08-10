"""Validate a finance-channel project without mutating it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from content.video_engine.src.services.finance_channel import (  # noqa: E402
    FinanceChannelValidationError,
    validate_project,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--include-pilots", action="store_true")
    args = parser.parse_args()
    try:
        result = validate_project(args.project_root, include_pilots=args.include_pilots)
    except FinanceChannelValidationError as exc:
        print("INVALID")
        for error in exc.errors:
            print(f"- {error}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
