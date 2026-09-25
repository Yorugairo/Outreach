"""P71 T4 / R26-312 - THE SECOND MELT THROWS THE PAGE ON SCREEN, NOT A STALE SNAPSHOT.

Steel and Paper H, 242.38 s: the second melt-and-throw threw the railways bars page - the page the FIRST melt had
thrown at 195.82 - instead of the yields page on screen (`SP/p69-m47/melt/M-tiles.png` d-f). E99 s74: a transition
carries the world it leaves.

The cause, proved on the frame (`SP/p71-t4/logs/diagnosis.md`): the melt's ink is a clone of the outgoing
world, mounted ONCE and kept on `wA.__melt`. A melt exit is read for EVERY frame of the scene it arrives into, so the
mount outlives its own window; when the next scene ALSO arrives by a melt there is no melt-free frame between the two,
and the second melt reused the first one's clone - on a play-through as much as on a seek. Only a cold seek was right,
so the frame was not a pure function of t. The same fault threw the wrong page at H 104.31 and 303.54 (every melt
whose scene follows another melt's).

What this file pins, on a three-scene surface where page A melts into page B and page B melts into page C:
  1. THE PLAY-THROUGH   every frame from inside B to inside the second melt: the clone thrown is B's.
  2. THE SEEK           straight from the first melt's window into the second's: the clone is B's.
  3. PURE IN t          the second melt's stage is the same DOM on the played path and on a cold page. (These pages
                        hold still; a page with a LIVE idle is cloned as it stands on the mount's frame - the
                        boundary when played, t when seeked cold - which this slice leaves as it was for every melt.)
  4. THE FIRST MELT     still throws A, the same stage cold and played (its goldens are test_golden_frames').
  5. THE KEY            the mount names the boundary it melts; one mount per melt, never two clones in the stage.
"""
from __future__ import annotations

import contextlib
import hashlib
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

CUT1, CUT2 = 10.0, 20.0   # page A melts into page B at CUT1; page B melts into page C at CUT2
TITLE_A = "Page A - the four lines that melt first"
TITLE_B = "Page B - where the four lines end"
TITLE_C = "Page C - the page the second melt hands to"
SIZE = RB.STAGE["16:9"]
FPS = 24


def _surface() -> tuple[dict, dict]:
    """A line page, then two bars pages, each arriving by `melt` (the throw): the H boundary pair in miniature."""
    import json
    series = LPG.load_series(G.SERIES)
    page_a = LPG.build_spec(series, "line", None, "right")
    page_a.update(title=TITLE_A, field="scribble", exit="cut")
    raw = json.loads(G.SERIES.read_text(encoding="utf-8"))

    def bars(title: str, k: int) -> dict:
        spec = {"title": title, "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
                "bars": [{"label": short, "value": round(float(sr["pts"][-k][1]), 1),
                          "color": sr.get("color", "crimson")}
                         for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
        page = LPG.build_spec(spec, "bars", None, "right")
        page.update(field="scribble", enter="axes", exit="cut")
        return page

    kb = {"scale": 0, "x": 0, "y": 0}
    scenes = [
        {"scene_id": "s01", "world": {"kind": "ledger", "page": page_a, "ken_burns": kb}, "exit": "cut",
         "span": [0.0, CUT1], "docks": [], "species": []},
        {"scene_id": "s02", "world": {"kind": "ledger", "page": bars(TITLE_B, 1), "ken_burns": kb}, "exit": "melt",
         "span": [CUT1, CUT2], "docks": [], "species": []},
        {"scene_id": "s03", "world": {"kind": "ledger", "page": bars(TITLE_C, 30), "ken_burns": kb}, "exit": "melt",
         "span": [CUT2, G.RUNTIME], "docks": [], "species": []},
    ]
    return G._timeline("P71 T4: two melts back to back", scenes, {}, None), G._base_uris()


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


browser_only = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = r"""() => {
  /* the title's glyphs are joined by no-break spaces */
  const titles = (root) => root
    ? [...root.querySelectorAll('.lp-title')].map((e) => e.textContent.replace(/\u00a0/g, ' ').trim()) : [];
  const wA = document.getElementById('wA'), m = wA.__melt;
  return { world: titles(wA), clone: m ? titles(m.ink) : null, words: m ? titles(m.txt) : null,
           key: m ? (m.key === undefined ? null : m.key) : null,
           clones: document.querySelectorAll('.meltink').length, texts: document.querySelectorAll('.melttext').length,
           shown: m ? m.ink.style.visibility !== 'hidden' : false };
}"""


@contextlib.contextmanager
def _browser():
    tl, uris = _surface()
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "two-melts.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)

                contexts = []

                def fresh():
                    ctx = browser.new_context(viewport={"width": SIZE[0], "height": SIZE[1]})
                    contexts.append(ctx)
                    page = ctx.new_page()
                    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(page, *SIZE)
                    return page
                try:
                    yield fresh
                finally:
                    for ctx in contexts:
                        ctx.close()
                    browser.close()
        finally:
            srv.shutdown()


def _at(page, t: float) -> dict:
    RB.frame_png(page, t, SIZE)
    return page.evaluate(PROBE)


STAGE_DOM = r"""() => {
  /* the stage as the engine wrote it, with each inline style's declarations in name order: the order a style was
     first written in is history (a mount on an earlier frame set `opacity` before `transform-origin`), not the frame */
  const copy = document.getElementById('stage').cloneNode(true);
  for (const el of [copy, ...copy.querySelectorAll('[style]')]) {
    if (!el.getAttribute || el.getAttribute('style') === null) continue;
    const names = [...el.style].sort();
    el.setAttribute('style', names.map((n) => n + ':' + el.style.getPropertyValue(n)
      + (el.style.getPropertyPriority(n) ? '!important' : '')).join(';'));
  }
  return copy.outerHTML;
}"""


def _stage(page, t: float) -> str:
    """The frame at t as the engine wrote it: the whole stage's DOM, hashed."""
    RB.frame_png(page, t, SIZE)
    return hashlib.sha256(page.evaluate(STAGE_DOM).encode("utf-8")).hexdigest()


SECOND = (CUT2 + 0.10, CUT2 + 0.30, CUT2 + 0.45)   # inside the second melt's window, the ink showing


@browser_only
def test_the_play_through_throws_page_b_not_page_a() -> None:
    """Every frame from inside B's scene (the first melt's mount still kept) into the second melt: B's ink is thrown."""
    with _browser() as fresh:
        page = fresh()
        seen = []
        for i in range(round((CUT2 - 0.5) * FPS), round((CUT2 + 0.5) * FPS) + 1):
            t = i / FPS
            p = _at(page, t)
            if t >= CUT2:
                assert TITLE_B in p["world"], (t, p["world"])
                seen.append((round(t, 4), p["clone"]))
                assert p["clone"] is not None and TITLE_B in p["clone"], (
                    f"at {t:.4f} s the second melt threw {p['clone']} - the page on screen is B ({TITLE_B!r})")
                assert TITLE_A not in (p["clone"] or []) and TITLE_A not in (p["words"] or []), (t, p)
        assert seen, "no frame of the second melt was read"


@browser_only
def test_a_seek_from_the_first_melt_straight_into_the_second_throws_page_b() -> None:
    with _browser() as fresh:
        page = fresh()
        first = _at(page, CUT1 + 0.25)
        assert first["clone"] is not None and TITLE_A in first["clone"], first
        for t in SECOND:
            p = _at(page, t)
            assert p["clone"] is not None and TITLE_B in p["clone"], (t, p["clone"])
            assert TITLE_A not in p["clone"], (t, p["clone"])


@browser_only
def test_the_second_melt_is_a_pure_function_of_t() -> None:
    """The played path and a cold page write the same stage at every instant of the second melt.

    Compared as the stage's DOM - every element, attribute and inline style the engine writes - not as screenshot
    bytes: Chromium rasters the melt's filtered ink differently after a different paint history even when the DOM is
    identical (measured at cd0b630 on the FIRST melt, whose clone was never stale: the same stage, 6886 pixels apart by
    more than 2 levels at 10.10 s - `SP/p71-t4/NOTES.md`). The engine's output is the DOM."""
    with _browser() as fresh:
        played = fresh()
        _at(played, CUT1 + 0.25)
        _at(played, CUT2 - 0.30)
        warm = {t: _stage(played, t) for t in SECOND}
        for t in SECOND:
            assert _stage(fresh(), t) == warm[t], f"{t:.2f} s: the played stage differs from the cold one"


@browser_only
def test_the_first_melt_still_throws_page_a_the_same_stage_cold_and_played() -> None:
    with _browser() as fresh:
        played = fresh()
        _at(played, CUT1 - 0.30)
        warm = {}
        for t in (CUT1 + 0.10, CUT1 + 0.30):
            p = _at(played, t)
            assert p["clone"] is not None and TITLE_A in p["clone"], (t, p)
            warm[t] = _stage(played, t)
        for t, dom in warm.items():
            assert _stage(fresh(), t) == dom, f"{t:.2f} s: the first melt's played stage differs from the cold one"


@browser_only
def test_one_mount_per_melt_keyed_to_the_boundary_it_melts() -> None:
    """The mount names the boundary (the arriving scene's span[0]); a new boundary replaces it, never stacks it."""
    with _browser() as fresh:
        page = fresh()
        a = _at(page, CUT1 + 0.10)
        assert a["key"] == CUT1 and a["clones"] == 1 and a["texts"] == 1, a
        b = _at(page, CUT2 + 0.10)
        assert b["key"] == CUT2 and b["clones"] == 1 and b["texts"] == 1, b
        back = _at(page, CUT1 + 0.10)   # a seek BACK re-mounts the first boundary from the page then on screen
        assert back["key"] == CUT1 and TITLE_A in back["clone"] and back["clones"] == 1, back
