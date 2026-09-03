"""
Footage Harvester Service
Extracts, normalizes, and packages internet/public domain video clips for Remotion timelines.
Enforces fair-use duration limits (~6s max) and strips audio automatically.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclasses.dataclass(slots=True)
class ClipProvenance:
    clip_id: str
    source_url: str
    start_time: float
    duration: float
    sha256: str
    resolution: str
    fps: int
    audio_stripped: bool
    is_public_domain: bool
    attribution_text: str
    created_at: str
    file_path: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class FootageHarvesterService:
    """Service to discover, download, trim, and normalize video footage from web sources."""

    def __init__(
        self,
        cache_dir: Optional[str | Path] = None,
        max_clip_duration: float = 6.0,
        default_resolution: str = "1920x1080",
        default_fps: int = 30,
    ) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else Path(".cache/footage_harvests")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_clip_duration = max_clip_duration
        self.default_resolution = default_resolution
        self.default_fps = default_fps

    def check_dependencies(self) -> dict[str, bool]:
        """Verify presence of external CLI tools."""
        return {
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "yt-dlp": shutil.which("yt-dlp") is not None,
            "ffprobe": shutil.which("ffprobe") is not None,
        }

    def search_candidates(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        """Search YouTube/Web for video candidates via yt-dlp metadata query."""
        deps = self.check_dependencies()
        if not deps["yt-dlp"]:
            logger.warning("yt-dlp is not installed. Returning empty candidates.")
            return []

        search_expr = f"ytsearch{max_results}:{query}"
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--default-search",
            "ytsearch",
            "--flat-playlist",
            "--skip-download",
            search_expr,
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            candidates = []
            for line in res.stdout.strip().splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    candidates.append({
                        "id": entry.get("id"),
                        "title": entry.get("title"),
                        "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "duration": entry.get("duration"),
                        "uploader": entry.get("uploader"),
                        "view_count": entry.get("view_count"),
                    })
                except json.JSONDecodeError:
                    continue
            return candidates
        except subprocess.CalledProcessError as e:
            logger.error(f"Search query failed: {e.stderr}")
            return []

    def fetch_subtitles(self, url: str) -> list[dict[str, Any]]:
        """Fetch automatic or uploaded captions/subtitles for a video."""
        deps = self.check_dependencies()
        if not deps["yt-dlp"]:
            return []

        temp_vtt_prefix = self.cache_dir / f"sub_{abs(hash(url))}"
        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--write-subs",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--skip-download",
            "--output", str(temp_vtt_prefix),
            url,
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            vtt_files = list(self.cache_dir.glob(f"{temp_vtt_prefix.name}*.vtt"))
            if not vtt_files:
                return []
            
            segments = self._parse_vtt(vtt_files[0])
            for vf in vtt_files:
                try:
                    vf.unlink()
                except OSError:
                    pass
            return segments
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to fetch subtitles for {url}: {e.stderr}")
            return []

    def _parse_vtt(self, vtt_path: Path) -> list[dict[str, Any]]:
        """Parse basic VTT caption timings and text."""
        segments = []
        pattern = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})")
        
        def parse_ts(ts_str: str) -> float:
            parts = ts_str.strip().split(":")
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            return 0.0

        content = vtt_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            match = pattern.search(line)
            if match:
                start = parse_ts(match.group(1))
                end = parse_ts(match.group(2))
                text_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() and not pattern.search(lines[i]):
                    clean_line = re.sub(r"<[^>]+>", "", lines[i].strip())
                    if clean_line:
                        text_lines.append(clean_line)
                    i += 1
                segments.append({
                    "start": start,
                    "end": end,
                    "text": " ".join(text_lines),
                })
            else:
                i += 1
        return segments

    def find_best_timecode(
        self,
        subtitles: list[dict[str, Any]],
        keywords: list[str],
        target_duration: float = 5.0,
    ) -> Tuple[float, float]:
        """Find the optimal start/end timestamps from subtitles matching keywords."""
        if not subtitles or not keywords:
            return 0.0, min(target_duration, self.max_clip_duration)

        kw_lower = [k.lower() for k in keywords if k]
        best_score = -1
        best_start = 0.0

        for seg in subtitles:
            text = seg.get("text", "").lower()
            score = sum(1 for kw in kw_lower if kw in text)
            if score > best_score:
                best_score = score
                best_start = seg.get("start", 0.0)

        effective_duration = min(target_duration, self.max_clip_duration)
        return best_start, best_start + effective_duration

    def compute_sha256(self, file_path: str | Path) -> str:
        """Compute SHA256 hex digest of file bytes."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest().lower()

    def build_ffmpeg_filter(self, resolution: str, fps: int) -> list[str]:
        """Build standard FFmpeg scale/crop filters for target resolution and fps."""
        try:
            width_s, height_s = resolution.lower().split("x")
            width, height = int(width_s), int(height_s)
        except Exception:
            width, height = 1920, 1080

        # Smart center crop to fill exact resolution without distortion
        filter_str = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"fps={fps}"
        )
        return ["-vf", filter_str]

    def download_and_slice(
        self,
        url_or_file: str,
        start_time: float,
        duration: float,
        output_path: str | Path,
        resolution: Optional[str] = None,
        fps: Optional[int] = None,
        strip_audio: bool = True,
        is_public_domain: bool = False,
        attribution_name: Optional[str] = None,
    ) -> ClipProvenance:
        """Download, slice, strip audio, and normalize clip to exact target parameters."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        res = resolution or self.default_resolution
        rate = fps or self.default_fps

        # Enforce fair-use cap unless verified public domain
        if not is_public_domain and duration > self.max_clip_duration:
            logger.info(f"Clamping requested duration {duration}s to fair-use maximum {self.max_clip_duration}s")
            effective_duration = self.max_clip_duration
        else:
            effective_duration = duration

        # If url is a local file, slice directly; otherwise resolve direct media URL with yt-dlp
        input_source = url_or_file
        if not os.path.exists(url_or_file) and (url_or_file.startswith("http://") or url_or_file.startswith("https://")):
            deps = self.check_dependencies()
            if not deps["yt-dlp"]:
                raise RuntimeError("yt-dlp is required to download web clips.")
            # Get direct video stream URL
            cmd_url = ["yt-dlp", "-g", "-f", "bestvideo[ext=mp4]/best[ext=mp4]/best", url_or_file]
            try:
                res_url = subprocess.run(cmd_url, capture_output=True, text=True, check=True)
                stream_url = res_url.stdout.strip().splitlines()[0]
                input_source = stream_url
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to resolve video stream: {e.stderr}")

        # Construct FFmpeg slice & normalization command
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", input_source,
            "-t", str(effective_duration),
        ]

        if strip_audio:
            ffmpeg_cmd.append("-an")

        ffmpeg_cmd.extend(self.build_ffmpeg_filter(res, rate))
        ffmpeg_cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            str(out_p),
        ])

        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg processing failed: {e.stderr}")

        file_sha256 = self.compute_sha256(out_p)
        clip_id = f"clip_{file_sha256[:12]}"
        attr_text = attribution_name or (f"Source: {url_or_file} (Time: {start_time:.1f}s-{start_time+effective_duration:.1f}s)")

        return ClipProvenance(
            clip_id=clip_id,
            source_url=url_or_file,
            start_time=start_time,
            duration=effective_duration,
            sha256=file_sha256,
            resolution=res,
            fps=rate,
            audio_stripped=strip_audio,
            is_public_domain=is_public_domain,
            attribution_text=attr_text,
            created_at=datetime.now(timezone.utc).isoformat(),
            file_path=str(out_p.resolve()),
        )

    def harvest_for_scene(
        self,
        query: str,
        target_duration: float,
        output_path: str | Path,
        keywords: Optional[list[str]] = None,
        resolution: Optional[str] = None,
        fps: Optional[int] = None,
        is_public_domain: bool = False,
    ) -> ClipProvenance:
        """Search, select best timecode, download, and normalize clip in a single call."""
        candidates = self.search_candidates(query, max_results=3)
        if not candidates:
            raise RuntimeError(f"No video candidates found for query: {query}")

        chosen_candidate = candidates[0]
        url = chosen_candidate["url"]
        logger.info(f"Selected candidate: '{chosen_candidate.get('title')}' ({url})")

        subtitles = self.fetch_subtitles(url)
        search_kws = keywords or query.split()
        start_t, _ = self.find_best_timecode(subtitles, search_kws, target_duration)

        return self.download_and_slice(
            url_or_file=url,
            start_time=start_t,
            duration=target_duration,
            output_path=output_path,
            resolution=resolution,
            fps=fps,
            strip_audio=True,
            is_public_domain=is_public_domain,
            attribution_name=f"{chosen_candidate.get('title', 'Web Video')} (via {chosen_candidate.get('uploader', 'Online')})",
        )
