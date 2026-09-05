"""P39 T2: the same source rendered twice in two separate browsers yields identical pixels.

Requires playwright + chromium; skipped where they are absent so the suite still runs.
What this proves is the harness's capture path (render_baseline.render_frame), which
neutralises the two wall-clock dependencies found on 2026-09-04: CSS transitions and the
fit-scaled stage. The shipped render_episode.py inherits neither fix until P39 T6.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


@pytest.mark.parametrize("surface", ["chart-callout", "dock-pair-9x16"])
def test_same_source_renders_identically_in_two_browsers(surface: str) -> None:
    first = RB.rgb_bytes(RB.render_surface(surface))
    second = RB.rgb_bytes(RB.render_surface(surface))
    assert first[0] == second[0] == RB.STAGE["9:16" if surface.endswith("9x16") else "16:9"]
    assert hashlib.sha256(first[1]).hexdigest() == hashlib.sha256(second[1]).hexdigest(), (
        f"{surface}: two renders of the same source differ - a wall-clock dependency is back")
