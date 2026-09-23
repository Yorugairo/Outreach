"""Focused artifact checks for the standalone minimal-2D fight proof."""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VIDEO = ROOT / "minimal-2d-fight-proof.mp4"
CONTACT_SHEET = ROOT / "contact-sheet.png"
STYLE_PREVIEW = ROOT / "style-preview.png"
TIMING = ROOT / "timing.json"


class Minimal2DProofTests(unittest.TestCase):
    def test_contact_receipt_geometry(self) -> None:
        self.assertTrue(TIMING.is_file())
        timing = json.loads(TIMING.read_text(encoding="utf-8"))
        self.assertEqual(timing["canvas"], {"width": 540, "height": 960, "fps": 24, "duration_s": 4.0, "frame_count": 96})
        self.assertTrue(timing["contact_geometry"]["passes"])
        self.assertLessEqual(timing["contact_geometry"]["center_distance_px"], 20.0)
        self.assertTrue(timing["followup_geometry"]["passes"])
        self.assertEqual(timing["contact_geometry"]["attacker"], "right_fighter_right_glove")
        self.assertEqual(timing["followup_geometry"]["attacker"], "right_fighter_left_glove")
        self.assertTrue(timing["fall_geometry"]["near_horizontal"])
        self.assertTrue(timing["fall_geometry"]["floor_contact_passes"])
        self.assertLessEqual(timing["fall_geometry"]["head_to_mat_px"], timing["fall_geometry"]["head_radius_px"] * 1.1)
        self.assertGreater(timing["contact_geometry"]["sample_s"], 1.0)
        self.assertGreater(timing["brain_visibility"]["start_s"], timing["contact_geometry"]["sample_s"])

    def test_contact_sheet_if_generated(self) -> None:
        if not CONTACT_SHEET.is_file():
            self.skipTest("review-only contact sheet has not been generated in this checkout")
        self.assertGreater(CONTACT_SHEET.stat().st_size, 0)

    def test_style_preview_if_generated(self) -> None:
        if not STYLE_PREVIEW.is_file():
            self.skipTest("review-only style preview has not been generated in this checkout")
        self.assertGreater(STYLE_PREVIEW.stat().st_size, 0)

    def test_mp4_probe_and_decode(self) -> None:
        if not VIDEO.is_file():
            self.skipTest("review-only MP4 has not been generated in this checkout")
        ffprobe = shutil.which("ffprobe")
        ffmpeg = shutil.which("ffmpeg")
        self.assertIsNotNone(ffprobe)
        self.assertIsNotNone(ffmpeg)
        probe = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,r_frame_rate,nb_frames,duration",
                "-of",
                "json",
                str(VIDEO),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        stream = json.loads(probe.stdout)["streams"][0]
        self.assertEqual([stream["width"], stream["height"]], [540, 960])
        self.assertEqual(stream["r_frame_rate"], "24/1")
        self.assertEqual(int(stream["nb_frames"]), 96)
        self.assertAlmostEqual(float(stream["duration"]), 4.0, places=3)
        decoded = subprocess.run([ffmpeg, "-v", "error", "-i", str(VIDEO), "-f", "null", "-"], capture_output=True, text=True)
        self.assertEqual(decoded.returncode, 0, decoded.stderr)


if __name__ == "__main__":
    unittest.main()
