"""P69 T28b / R26-300 - THE TEST CARD READS ON A PHONE: the checklist's `profile: "phone"`.

Row 20's frame read (P69 T28): the checklist species had no type option - 19 px cells on the chart dock's fixed
1056 x 480 canvas reach ~34 stage px even at full width, under the long-form phone floor (E99 s90: 12 px on a 390 px
phone = 59.08 stage px, `ledger_page.CARD_PHONE_FLOOR`), and the card's lower half stood empty. Under the profile
(species/checklist.mjs CHECKLIST_PROFILES.phone) the type, the header, the title, the row pitch and the highlighter
band scale TOGETHER, on the same canvas, and this file measures it on the served player at row 20's own slot (the
right 0.60 of the stage, the host visible at left):

  (1) THE FLOOR     every cell, head and title, AS DISPLAYED, at or above 59.08 stage px; every cell at >= 54 canvas px
  (2) THE FILL      three rows, the first at PT + 130, pitched 90, the last row's baseline in the canvas' lower third
  (3) THE SLOT      the card stands in the right 0.60 of the stage - the stage's left 0.38 is the host's
  (4) BY NAME       the compiler refuses an unknown profile, a phone card that is not a question and two answers,
                    more rows than the canvas holds at the floor, and a sub (the title carries it) - each by name
  (5) OFF           a checklist that names no profile is the one it always was: 19 px cells (the `test-card` golden
                    holds its pixels)
"""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

SPECIES = ROOT / "content/video_engine/scripts/species/checklist.mjs"
FLOOR = LPG.CARD_PHONE_FLOOR * 1920 / LPG.CARD_PHONE_W   # 59.08 displayed stage px on a 16:9 frame played 390 px wide
CELL_MIN = 54.0                                          # canvas px: the cell type the profile must reach (row 20's measure)
T_FULL = 12.5                                            # every row landed, typed and swept (delays 1 / 4 / 7 after the land)
SQUEEZE_MIN = 0.85                                       # the answers may give way this far (textLength) - a semi-condensed read


def phone_chart() -> dict:
    tl, _ = G.test_card_phone()
    return copy.deepcopy(next(iter(tl["evidence"].values()))["chart"])


# ---- the compiler (no browser) ----------------------------------------------------------------------------------------

def test_the_compiler_names_the_profiles_the_species_draws():
    assert B.CHECKLIST_PROFILES == ("phone",)
    src = SPECIES.read_text(encoding="utf-8")
    block = re.search(r"export const CHECKLIST_PROFILES = Object\.freeze\(\{(.*?)\n\}\);", src, re.S)
    assert block, "species/checklist.mjs states CHECKLIST_PROFILES"
    names = tuple(re.findall(r"^  ([a-z_]+): Object\.freeze\(", block.group(1), re.M))
    assert names == B.CHECKLIST_PROFILES, "the compiler and the species name the same profiles"


def test_the_phone_card_and_the_default_card_pass():
    assert B.checklist_problems(phone_chart()) == []
    tl, _ = G.test_card()
    assert B.checklist_problems(next(iter(tl["evidence"].values()))["chart"]) == [], "the default card is untouched"
    assert B.checklist_problems({"series": []}) == [], "a chart that is no checklist has nothing to say"


@pytest.mark.parametrize("mutate, says", [
    (lambda c: c["checklist"].update(profile="tablet"), r"profile 'tablet' is not one of \('phone',\)"),
    (lambda c: c["checklist"].update(profile=True), r"profile True is not one of"),
    (lambda c: c["checklist"].update(head=["Ask", "Where", "Steel", "Paper"]),
     r"a phone card is a question and its two answers: 3 columns, not 4"),
    (lambda c: c["checklist"]["rows"][1].update(cells=["2  Cash?", "earns cash"]),
     r"row 2 has 2 cells, the head 3"),
    (lambda c: c["checklist"]["rows"].append({"cells": ["4  More?", "yes", "no"]}),
     r"4 rows - the phone canvas holds 3 at the floor"),
    (lambda c: c.update(sub="Ask it of any holding"),
     r"a phone card draws no sub .*'Ask it of any holding'"),
])
def test_the_compiler_refuses_by_name(mutate, says):
    chart = phone_chart()
    mutate(chart)
    problems = B.checklist_problems(chart)
    assert problems and re.search(says, " | ".join(problems)), problems


def test_the_compiler_refuses_a_bad_checklist_at_the_dock(tmp_path):
    """The door row 20 walks: a dock whose .series.json carries the checklist - refused with the asset named."""
    chart = phone_chart()
    chart["checklist"]["profile"] = "tablet"
    with pytest.raises(ValueError, match=r"ev-x: checklist: profile 'tablet' is not one of"):
        B.check_checklist("ev-x", chart)
    B.check_checklist("ev-x", phone_chart())   # a good one passes silently


# ---- the player --------------------------------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# every word the dock's chart canvas writes: its canvas size (CSS px in the viewBox's units), its size AS DISPLAYED
# (x the canvas' own scale to the stage), its baseline, whether it is squeezed, and the canvas and dock boxes
CANVAS_PROBE = """() => {
  const stage = document.getElementById('stage').getBoundingClientRect();
  const svg = [...document.querySelectorAll('.dock svg.chartbox')].find(s => s.getBoundingClientRect().width > 0);
  if (!svg) return null;
  const cm = svg.getScreenCTM(), k = Math.hypot(cm.a, cm.b), vb = svg.viewBox.baseVal;
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  const nat = (e) => { const tl = e.getAttribute('textLength'); if (!tl) return e.getComputedTextLength();
    e.removeAttribute('textLength'); const w = e.getComputedTextLength(); e.setAttribute('textLength', tl); return w; };
  const texts = [...svg.querySelectorAll('text')].filter(e => (e.textContent || '').trim()).map(e => {
    const tl = e.getAttribute('textLength'), n = nat(e);
    return { cls: e.getAttribute('class'), text: e.textContent.trim(), fs: parseFloat(getComputedStyle(e).fontSize),
             px: parseFloat(getComputedStyle(e).fontSize) * k, y: +e.getAttribute('y'), x: +e.getAttribute('x'),
             natural: n, drawn: tl ? +tl : n, squeeze: tl ? +tl / n : 1 }; });
  return { k, vb: [vb.width, vb.height], box: R(svg), dock: R(svg.closest('.dock')), texts };
}"""


def _probe(browser, tl: dict, uris: dict, tmp: Path, name: str, t: float) -> dict:
    html = tmp / f"{name}.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(html.parent)
    w, h = RB.STAGE[tl.get("aspect") or "16:9"]
    page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    try:
        page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(page, w, h)
        page.wait_for_function("document.fonts.status === 'loaded'")
        for _ in range(2):
            RB.frame_png(page, t, (w, h))
            page.wait_for_timeout(80)
        return dict(page.evaluate(CANVAS_PROBE) or {}, errors=errors)
    finally:
        page.context.close()
        srv.shutdown()


@pytest.fixture(scope="module")
def canvases(tmp_path_factory):
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright
    tmp = tmp_path_factory.mktemp("checklist")
    out = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for key, build in (("phone", G.test_card_phone), ("default", G.test_card)):
                tl, uris = build()
                out[key] = _probe(browser, tl, uris, tmp, key, T_FULL)
        finally:
            browser.close()
    return out


def _cells(probe: dict) -> list[dict]:
    return [x for x in probe["texts"] if x["cls"] == "cs" and x["y"] > 96]


@needs_browser
def test_the_phone_card_writes_every_row_word_at_the_floor(canvases):
    ph = canvases["phone"]
    assert not ph["errors"], ph["errors"]
    cells = _cells(ph)
    assert len(cells) == 9, [c["text"] for c in cells]
    small = [(c["text"], round(c["fs"], 1), round(c["px"], 1)) for c in cells if c["fs"] < CELL_MIN or c["px"] < FLOOR]
    assert not small, f"cells under {CELL_MIN} canvas px or the {FLOOR:.2f} stage px floor: {small}"
    title = next(x for x in ph["texts"] if x["cls"] == "ct")
    head = [x for x in ph["texts"] if x["cls"] == "csr" and x["text"] in ("Ask", "Steel", "Paper")]
    assert len(head) == 3 and all(x["px"] >= FLOOR for x in head), head
    assert title["px"] >= FLOOR, title
    assert not [x for x in ph["texts"] if x["text"] == "Ask it of any holding"], "no sub on a phone card"


@needs_browser
def test_no_cell_runs_into_its_neighbour_and_the_question_is_never_squeezed(canvases):
    """The fit under the profile: the question column TYPES, so it keeps its natural width (FIT_KEEP_Q) and only the
    answers give way - never below SQUEEZE_MIN on the golden's cells, and no cell's drawn end past the next column."""
    ph = canvases["phone"]
    rows: dict[float, list[dict]] = {}
    for c in _cells(ph):
        rows.setdefault(c["y"], []).append(c)
    for y, cells in rows.items():
        cells.sort(key=lambda c: c["x"])
        assert cells[0]["squeeze"] == 1, cells[0]
        for a, b in zip(cells, cells[1:]):
            assert a["x"] + a["drawn"] < b["x"], f"row at {y}: {a['text']!r} ends at {a['x'] + a['drawn']:.0f}, {b['text']!r} starts at {b['x']:.0f}"
        assert cells[-1]["x"] + cells[-1]["drawn"] <= ph["vb"][0], cells[-1]
    worst = min(c["squeeze"] for c in _cells(ph))
    assert worst >= SQUEEZE_MIN, [(c["text"], round(c["squeeze"], 3)) for c in _cells(ph)]


@needs_browser
def test_the_phone_rows_fill_the_canvas(canvases):
    ph = canvases["phone"]
    ys = sorted({c["y"] for c in _cells(ph)})
    assert len(ys) == 3, ys
    assert ys[0] == pytest.approx(96 + 130) and ys[1] - ys[0] == pytest.approx(90) and ys[2] - ys[1] == pytest.approx(90)
    assert ys[-1] >= ph["vb"][1] * 2 / 3, f"the last row's baseline {ys[-1]} is not in the lower third of {ph['vb'][1]}"
    assert ph["vb"] == [1056, 480], "the profile keeps the dock's canvas - the card's aspect is unchanged"


@needs_browser
def test_the_phone_card_stands_at_the_right_leaving_the_host(canvases):
    ph = canvases["phone"]
    x, y, w, h = ph["box"]
    assert x >= 0.38 * 1920 and x + w <= 1920, ph["box"]
    assert 0.55 * 1920 <= ph["dock"][2] <= 0.62 * 1920, ph["dock"]


@needs_browser
def test_a_checklist_with_no_profile_is_unchanged(canvases):
    df = canvases["default"]
    cells = _cells(df)
    assert cells and all(c["fs"] == 19 for c in cells), sorted({c["fs"] for c in cells})
    assert sorted({c["y"] for c in cells}) == [160, 218, 276]
