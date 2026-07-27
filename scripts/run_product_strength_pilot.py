from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.product_strength_pilot_service import (
    ProductStrengthPilotService,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the offline P10 product-strength evaluation harness."
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("tests/fixtures/product_strength_pilot_v1.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "artifacts/product-strength-pilot/p10-fixture-dry-run.json"
        ),
    )
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    summary = ProductStrengthPilotService().evaluate(fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    print(
        "promotion_ready="
        f"{summary['evaluation']['promotion_ready']} "
        f"sample_authenticity="
        f"{summary['evaluation']['gates']['sample_authenticity']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
