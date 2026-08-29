from __future__ import annotations

import argparse
import json

from content.video_engine.src.services.video_review_learning import write_aggregated_learning


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate durable video reviews into confidence-scored learning candidates."
    )
    parser.add_argument("reviews", nargs="+", help="watch-review.v1.json files")
    parser.add_argument("--output", required=True, help="Output learning ledger JSON path")
    parser.add_argument("--repo-root", default=".", help="Repository root that must contain output")
    args = parser.parse_args()
    outputs = write_aggregated_learning(args.reviews, args.output, repo_root=args.repo_root)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
