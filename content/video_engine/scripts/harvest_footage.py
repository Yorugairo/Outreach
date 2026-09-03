"""
CLI Script: Harvest Footage
Command-line tool to discover, slice, strip audio, and normalize b-roll video clips.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.footage_harvester import FootageHarvesterService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("harvest_footage")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover, slice, normalize, and extract internet/b-roll footage clips."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", "-q", type=str, help="Search query to find candidate video automatically")
    group.add_argument("--url", "-u", type=str, help="Direct video URL or local file path")

    parser.add_argument("--start", "-s", type=float, default=0.0, help="Start time in seconds (for --url)")
    parser.add_argument("--duration", "-d", type=float, default=5.0, help="Target clip duration in seconds")
    parser.add_argument("--output", "-o", type=str, required=True, help="Destination output .mp4 file path")
    parser.add_argument("--max-duration", type=float, default=6.0, help="Fair-use duration cap (default: 6.0s)")
    parser.add_argument("--resolution", "-r", type=str, default="1920x1080", help="Output resolution (e.g. 1920x1080 or 1080x1920)")
    parser.add_argument("--fps", type=int, default=30, help="Output framerate (default: 30)")
    parser.add_argument("--keywords", "-k", type=str, help="Comma-separated keywords for subtitle timestamp matching")
    parser.add_argument("--public-domain", action="store_true", help="Mark as verified public domain (bypasses 6s cap)")
    parser.add_argument("--manifest", "-m", type=str, help="Optional path to write/append JSON provenance manifest")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    service = FootageHarvesterService(
        max_clip_duration=args.max_duration,
        default_resolution=args.resolution,
        default_fps=args.fps,
    )

    deps = service.check_dependencies()
    logger.info(f"System tools: ffmpeg={deps['ffmpeg']}, yt-dlp={deps['yt-dlp']}")

    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else None

    try:
        if args.query:
            logger.info(f"Harvesting footage for query: '{args.query}' (target {args.duration}s)...")
            provenance = service.harvest_for_scene(
                query=args.query,
                target_duration=args.duration,
                output_path=args.output,
                keywords=keywords,
                resolution=args.resolution,
                fps=args.fps,
                is_public_domain=args.public_domain,
            )
        else:
            logger.info(f"Extracting clip from: {args.url} (start={args.start}s, dur={args.duration}s)...")
            provenance = service.download_and_slice(
                url_or_file=args.url,
                start_time=args.start,
                duration=args.duration,
                output_path=args.output,
                resolution=args.resolution,
                fps=args.fps,
                strip_audio=True,
                is_public_domain=args.public_domain,
            )

        logger.info(f"Successfully harvested clip: {provenance.file_path}")
        logger.info(f"  Duration: {provenance.duration:.2f}s | Resolution: {provenance.resolution} | SHA256: {provenance.sha256[:16]}...")
        logger.info(f"  Attribution: {provenance.attribution_text}")

        if args.manifest:
            manifest_p = Path(args.manifest)
            manifest_p.parent.mkdir(parents=True, exist_ok=True)
            existing_data = []
            if manifest_p.exists():
                try:
                    existing_data = json.loads(manifest_p.read_text(encoding="utf-8"))
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except Exception:
                    existing_data = []
            existing_data.append(provenance.to_dict())
            manifest_p.write_text(json.dumps(existing_data, indent=2), encoding="utf-8")
            logger.info(f"Updated provenance manifest: {manifest_p}")

        return 0
    except Exception as e:
        logger.error(f"Harvest failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
