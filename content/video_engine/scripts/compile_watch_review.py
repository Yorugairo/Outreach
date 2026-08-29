from __future__ import annotations

import argparse
import json

from content.video_engine.src.services.video_review_learning import compile_review_packet


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile selected /watch evidence into a durable review packet."
    )
    parser.add_argument("--draft", required=True, help="Path to a watch-review draft JSON file")
    parser.add_argument("--output-dir", required=True, help="Episode review packet directory")
    parser.add_argument("--repo-root", default=".", help="Repository root that must contain output-dir")
    args = parser.parse_args()
    outputs = compile_review_packet(args.draft, args.output_dir, repo_root=args.repo_root)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
