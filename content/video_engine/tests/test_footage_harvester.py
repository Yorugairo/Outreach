"""
Unit and Integration Tests for Footage Harvester Service
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.footage_harvester import FootageHarvesterService, ClipProvenance


class TestFootageHarvesterService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = FootageHarvesterService(
            cache_dir=self.temp_dir,
            max_clip_duration=6.0,
            default_resolution="1920x1080",
            default_fps=30,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dependency_check_structure(self):
        deps = self.service.check_dependencies()
        self.assertIn("ffmpeg", deps)
        self.assertIn("yt-dlp", deps)
        self.assertIn("ffprobe", deps)

    def test_ffmpeg_filter_builder_16_9(self):
        filters = self.service.build_ffmpeg_filter("1920x1080", 30)
        self.assertEqual(filters[0], "-vf")
        self.assertIn("scale=1920:1080", filters[1])
        self.assertIn("crop=1920:1080", filters[1])
        self.assertIn("fps=30", filters[1])

    def test_ffmpeg_filter_builder_9_16(self):
        filters = self.service.build_ffmpeg_filter("1080x1920", 60)
        self.assertEqual(filters[0], "-vf")
        self.assertIn("scale=1080:1920", filters[1])
        self.assertIn("crop=1080:1920", filters[1])
        self.assertIn("fps=60", filters[1])

    def test_timecode_selection_and_duration_clamp(self):
        subtitles = [
            {"start": 0.0, "end": 4.0, "text": "Welcome to our introductory overview."},
            {"start": 4.2, "end": 9.5, "text": "Here is the stock market crash and economic recession impact."},
            {"start": 9.8, "end": 14.0, "text": "Finally we look at recovery statistics."},
        ]

        # Search for stock market keywords
        start, end = self.service.find_best_timecode(subtitles, ["stock", "crash"], target_duration=5.0)
        self.assertAlmostEqual(start, 4.2)
        self.assertAlmostEqual(end, 9.2)

        # Test duration clamping (> 6s clamped to 6s)
        start, end = self.service.find_best_timecode(subtitles, ["stock", "crash"], target_duration=12.0)
        self.assertAlmostEqual(start, 4.2)
        self.assertAlmostEqual(end, 10.2)
        self.assertLessEqual(end - start, 6.0)

    def test_provenance_to_dict(self):
        prov = ClipProvenance(
            clip_id="clip_123456",
            source_url="https://youtube.com/watch?v=sample",
            start_time=10.0,
            duration=5.0,
            sha256="abcdef1234567890",
            resolution="1920x1080",
            fps=30,
            audio_stripped=True,
            is_public_domain=False,
            attribution_text="Sample Video",
            created_at="2026-08-24T00:00:00Z",
            file_path="/path/to/clip.mp4",
        )
        d = prov.to_dict()
        self.assertEqual(d["clip_id"], "clip_123456")
        self.assertEqual(d["duration"], 5.0)
        self.assertTrue(d["audio_stripped"])
        self.assertFalse(d["is_public_domain"])

    def test_synthetic_video_slicing_and_audio_stripping(self):
        deps = self.service.check_dependencies()
        if not deps["ffmpeg"]:
            self.skipTest("ffmpeg not available on test host")

        # Create synthetic 10s test video with audio tone
        src_video = Path(self.temp_dir) / "source_synthetic.mp4"
        gen_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=10:size=640x360:rate=30",
            "-f", "lavfi", "-i", "sine=frequency=1000:duration=10",
            "-c:v", "libx264", "-c:a", "aac",
            str(src_video)
        ]
        subprocess.run(gen_cmd, capture_output=True, check=True)
        self.assertTrue(src_video.exists())

        # Extract 4-second normalized clip (1080p, audio stripped)
        out_clip = Path(self.temp_dir) / "harvested_clip.mp4"
        provenance = self.service.download_and_slice(
            url_or_file=str(src_video),
            start_time=2.0,
            duration=4.0,
            output_path=out_clip,
            resolution="1280x720",
            fps=30,
            strip_audio=True,
        )

        self.assertTrue(out_clip.exists())
        self.assertEqual(provenance.duration, 4.0)
        self.assertEqual(provenance.resolution, "1280x720")
        self.assertTrue(provenance.audio_stripped)
        self.assertEqual(len(provenance.sha256), 64)

        # Check that audio was stripped using ffprobe if available
        if deps["ffprobe"]:
            probe_cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "a",
                "-show_entries", "stream=codec_name",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(out_clip)
            ]
            probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
            self.assertEqual(probe_res.stdout.strip(), "", "Audio stream was not stripped!")


if __name__ == "__main__":
    unittest.main()
