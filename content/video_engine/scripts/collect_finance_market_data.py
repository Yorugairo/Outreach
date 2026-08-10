"""Collect an auditable YFinance price-return packet; never writes narration or visuals."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from content.video_engine.src.services.finance_market_data import (  # noqa: E402
    collect_market_data_packet,
    default_current_bubble_instruments,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--price-basis", choices=("adjusted_close", "close"), default="adjusted_close")
    args = parser.parse_args()
    packet = collect_market_data_packet(
        episode_id=args.episode_id,
        instruments=default_current_bubble_instruments(),
        start=args.start,
        end=args.end,
        price_basis=args.price_basis,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output.as_posix(), "artifact_hash": packet["artifact_hash"]}, indent=2))


if __name__ == "__main__":
    main()
