"""
Gather News Clips & Diegetic TV Evidence Pipeline.

Discovers, downloads, extracts, normalizes, and packages news video clips
for the diegetic TV-embed evidence dock (Bravos style, Doc 29 §8, §9.26).

Capabilities:
1. Search YouTube for broadcast news clips using yt-dlp.
2. Slices target sub-clips (-ss to -t) and strips/normalizes audio.
3. Applies the Bravos Diegetic TV styling filter (subtle desaturation, contrast, and CRT scanlines).
4. Generates 3-tile contact sheets (start, middle, settle) for human review.
5. Emits SHA-256 asset manifests conforming to Outreach Program standards (original_review_only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("gather_news_clips")

ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = ROOT / "content/video_engine/projects/systems-and-blowups/myth-of-historical-normal"
ASSETS_DIR = PROJECT_DIR / "assets/evidence_clips"
CONTACT_SHEETS_DIR = ASSETS_DIR / "contact_sheets"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"

TARGET_CLIPS = [
    {
        "clip_id": "clip_cnbc_yield_495",
        "scene": "SC-01",
        "title": "CNBC Squawk Box — 10-Year Yield Hits 4.95%",
        "search_query": "CNBC Squawk Box 10-year Treasury yield 4.95 percent September 2026",
        "target_duration": 8.5,
        "description": "Cable broadcast coverage of the 10-year Treasury yield hitting 4.95% in September 2026.",
    },
    {
        "clip_id": "clip_bloomberg_bessent_buyback",
        "scene": "SC-03",
        "title": "Bloomberg Surveillance — Scott Bessent $6B Debt Buyback",
        "search_query": "Bloomberg Surveillance Scott Bessent Treasury debt buyback September 2026",
        "target_duration": 11.0,
        "description": "Market commentary on Treasury Secretary Scott Bessent's $6B buyback program.",
    },
    {
        "clip_id": "clip_cnbc_oil_spr_300m",
        "scene": "SC-04",
        "title": "CNBC Closing Bell — WTI Crude Surges Past $82 / SPR Drops Below 300M Barrels",
        "search_query": "CNBC Closing Bell crude oil $82 strategic petroleum reserve 300 million barrels",
        "target_duration": 9.0,
        "description": "Oil surge and Strategic Petroleum Reserve drawdown coverage.",
    },
    {
        "clip_id": "clip_foxbiz_warsh_fed_guidance",
        "scene": "SC-05",
        "title": "Fox Business — Kevin Warsh on Fed Guidance and Long-Term Yields",
        "search_query": "Fox Business Maria Bartiromo Kevin Warsh Federal Reserve interest rates",
        "target_duration": 10.5,
        "description": "Discussion of Kevin Warsh and the pricing of term premium on Treasury bonds.",
    },
    {
        "clip_id": "clip_bloomberg_erp_inversion",
        "scene": "SC-06",
        "title": "Bloomberg Markets — Equity Risk Premium Inversion",
        "search_query": "Bloomberg Markets equity risk premium inverted stocks bond yields 2026",
        "target_duration": 12.0,
        "description": "Visual segment analyzing negative equity risk premium and stock valuation multiples.",
    },
]


def check_binaries() -> dict[str, bool]:
    return {
        "yt-dlp": shutil.which("yt-dlp") is not None,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
    }


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def search_youtube(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--default-search", "ytsearch",
        "--flat-playlist",
        "--skip-download",
        f"ytsearch{max_results}:{query}",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        results = []
        for line in res.stdout.strip().splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                results.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "uploader": entry.get("uploader"),
                    "duration": entry.get("duration"),
                    "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "view_count": entry.get("view_count"),
                })
            except json.JSONDecodeError:
                continue
        return results
    except subprocess.CalledProcessError as e:
        logger.error(f"yt-dlp search failed for '{query}': {e.stderr}")
        return []


def process_bravos_tv_clip(
    source_url_or_path: str,
    output_path: Path,
    start_time: float,
    duration: float,
    apply_crt: bool = True,
    width: int = 1280,
    height: int = 720,
    fps: int = 30,
) -> Path:
    """
    Download/slice and apply Bravos diegetic TV styling:
    - Scale/crop to exact 16:9
    - Desaturate (-15%) and boost contrast (+15%) to match dark slate environment
    - Optional scanlines
    - Mute audio (-an) for background diegetic video
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_src = source_url_or_path
    if not os.path.exists(source_url_or_path) and (source_url_or_path.startswith("http://") or source_url_or_path.startswith("https://")):
        # Resolve direct video stream URL
        cmd_url = ["yt-dlp", "-g", "-f", "bestvideo[ext=mp4]/best[ext=mp4]/best", source_url_or_path]
        try:
            res_url = subprocess.run(cmd_url, capture_output=True, text=True, check=True)
            valid_urls = [l.strip() for l in res_url.stdout.strip().splitlines() if l.strip().startswith("http://") or l.strip().startswith("https://")]
            if not valid_urls:
                raise RuntimeError(f"No direct stream URL returned by yt-dlp: {res_url.stdout}")
            input_src = valid_urls[0]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to resolve video stream: {e.stderr}")

    filters = [
        f"scale={width}:{height}:force_original_aspect_ratio=increase",
        f"crop={width}:{height}",
        f"fps={fps}",
        "eq=saturation=0.85:contrast=1.15:brightness=-0.02",
    ]
    if apply_crt:
        # Subtle horizontal scanlines
        filters.append("drawgrid=width=1280:height=4:thickness=1:color=black@0.12")

    filter_str = ",".join(filters)

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", f"{start_time:.3f}",
        "-i", input_src,
        "-t", f"{duration:.3f}",
        "-vf", filter_str,
        "-an",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path


def generate_3tile_contact_sheet(
    video_path: Path,
    output_sheet_path: Path,
    total_duration: float,
) -> Path:
    """
    Extracts 3 representative frames (start, middle, settle)
    and stitches them horizontally with timestamps.
    """
    output_sheet_path.parent.mkdir(parents=True, exist_ok=True)
    # Get actual duration from ffprobe if possible
    dur = total_duration
    try:
        probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
        dur_str = subprocess.check_output(probe_cmd, text=True).strip()
        dur = float(dur_str)
    except Exception:
        dur = total_duration

    t1 = max(0.2, min(1.0, dur * 0.20))
    t2 = max(t1 + 0.2, dur * 0.50)
    t3 = min(dur - 0.3, max(t2 + 0.2, dur * 0.85))

    temp_dir = output_sheet_path.parent / f"_tmp_{video_path.stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    f1 = temp_dir / "frame_01.jpg"
    f2 = temp_dir / "frame_02.jpg"
    f3 = temp_dir / "frame_03.jpg"

    for t, out_f, label in [(t1, f1, "START"), (t2, f2, "MID"), (t3, f3, "SETTLE")]:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{t:.3f}",
            "-i", str(video_path),
            "-frames:v", "1",
            "-update", "1",
            "-vf", "scale=640:360",
            "-q:v", "2",
            str(out_f),
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Stitch 3 frames horizontally into 1 contact sheet
    cmd_stitch = [
        "ffmpeg",
        "-y",
        "-i", str(f1),
        "-i", str(f2),
        "-i", str(f3),
        "-filter_complex", "hstack=inputs=3",
        "-q:v", "2",
        str(output_sheet_path),
    ]
    subprocess.run(cmd_stitch, capture_output=True, text=True, check=True)

    # Cleanup temp frames
    shutil.rmtree(temp_dir, ignore_errors=True)
    return output_sheet_path


def update_manifest(records: list[dict[str, Any]]) -> Path:
    existing: dict[str, Any] = {"version": "1.0", "updated_at": datetime.now(timezone.utc).isoformat(), "assets": {}}
    if MANIFEST_PATH.exists():
        try:
            existing = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    for rec in records:
        existing["assets"][rec["asset_id"]] = rec

    existing["updated_at"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return MANIFEST_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Gather News Clips & Build Diegetic TV Evidence Layer.")
    parser.add_argument("--search-all", action="store_true", help="Search YouTube for all 5 target news clips.")
    parser.add_argument("--query", type=str, help="Search YouTube for custom query.")
    parser.add_argument("--harvest", type=str, help="Harvest clip by clip_id (e.g. clip_cnbc_yield_495).")
    parser.add_argument("--url", type=str, help="Source video URL or local path for harvesting.")
    parser.add_argument("--start", type=float, default=0.0, help="Start time in seconds.")
    parser.add_argument("--duration", type=float, default=None, help="Clip duration in seconds.")
    parser.add_argument("--contact-sheet-only", type=Path, help="Generate 3-tile contact sheet for an existing clip.")

    args = parser.parse_args()

    deps = check_binaries()
    if not deps["yt-dlp"] or not deps["ffmpeg"]:
        logger.error(f"Missing required dependencies: {deps}")
        return 1

    if args.search_all:
        print("=== Searching Broadcast News Candidates for Myth of Historical Normal ===")
        all_results = {}
        for clip in TARGET_CLIPS:
            print(f"\n--- Target: {clip['title']} (Scene: {clip['scene']}, Target: {clip['target_duration']}s) ---")
            print(f"Query: {clip['search_query']}")
            candidates = search_youtube(clip["search_query"], max_results=3)
            all_results[clip["clip_id"]] = candidates
            for idx, c in enumerate(candidates, 1):
                dur_str = f"{c['duration']}s" if c.get("duration") else "unknown"
                print(f"  [{idx}] {c['title']}")
                print(f"      Channel: {c['uploader']} | Duration: {dur_str} | URL: {c['url']}")

        out_search = ASSETS_DIR / "candidates.json"
        out_search.parent.mkdir(parents=True, exist_ok=True)
        out_search.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
        print(f"\nCandidates catalog written to: {out_search}")
        return 0

    if args.query:
        print(f"Searching: {args.query}")
        candidates = search_youtube(args.query, max_results=5)
        for idx, c in enumerate(candidates, 1):
            print(f"[{idx}] {c['title']} ({c['url']})")
        return 0

    if args.contact_sheet_only:
        p = args.contact_sheet_only
        if not p.exists():
            print(f"Error: {p} does not exist.")
            return 1
        sheet_out = CONTACT_SHEETS_DIR / f"{p.stem}_contact_sheet.jpg"
        generate_3tile_contact_sheet(p, sheet_out, 10.0)
        print(f"Contact sheet generated: {sheet_out}")
        return 0

    if args.harvest:
        target = next((c for c in TARGET_CLIPS if c["clip_id"] == args.harvest), None)
        if not target and not args.url:
            print(f"Clip ID '{args.harvest}' not recognized and no --url provided.")
            return 1

        url = args.url
        duration = args.duration or (target["target_duration"] if target else 8.0)
        out_clip_path = ASSETS_DIR / f"{args.harvest}.mp4"
        sheet_path = CONTACT_SHEETS_DIR / f"{args.harvest}_contact_sheet.jpg"

        if not url:
            print(f"Searching candidate for {args.harvest}...")
            candidates = search_youtube(target["search_query"], max_results=1)
            if not candidates:
                print("No candidate found via YouTube search.")
                return 1
            url = candidates[0]["url"]
            print(f"Found: {candidates[0]['title']} ({url})")

        print(f"Processing clip to: {out_clip_path} (Start: {args.start}s, Duration: {duration}s)")
        process_bravos_tv_clip(url, out_clip_path, args.start, duration)
        print("Generating 3-tile contact sheet...")
        generate_3tile_contact_sheet(out_clip_path, sheet_path, duration)

        digest = compute_sha256(out_clip_path)
        record = {
            "asset_id": args.harvest,
            "scene": target["scene"] if target else "UNKNOWN",
            "source_url": url,
            "start_s": args.start,
            "duration_s": duration,
            "sha256": digest,
            "resolution": "1280x720",
            "fps": 30,
            "rights_state": "original_review_only",
            "review_state": "original_review_only",
            "render_eligible": False,
            "clip_path": str(out_clip_path.relative_to(ROOT)).replace("\\", "/"),
            "contact_sheet_path": str(sheet_path.relative_to(ROOT)).replace("\\", "/"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        update_manifest([record])
        print(f"\nClip harvested successfully!")
        print(f"  File: {out_clip_path}")
        print(f"  SHA-256: {digest}")
        print(f"  Contact Sheet: {sheet_path}")
        print(f"  Manifest updated at: {MANIFEST_PATH}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
