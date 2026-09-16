"""P61 T8 / E99 s16 + E93 / BACKLOG R26-80: THE AGENDA PAGE - the plate version of the list effect.

The operator, E99 s16: *"still need the beautified agenda page, which i think we discussed as basically just
being the plate version of our list effect."* The dock form parks its rows in the box it was given, which at
three rows left the upper two thirds of the plate empty (`species-proof@proof-agenda.png`). `form: "page"` is
the same declaration on a plate of its own, and the model is Steel and Paper's three-question TEST card.

What this file holds, and the whole of what the page form may do:
  - THE FILL: the page form's rows cover their board - no two thirds of anything empty - and the dock form,
    measured the same way on its own golden, does not (that contrast IS the acceptance);
  - E93's ORDER: a row's icon is not on the page until that row's sentence has been fully written, checked row
    by row at the instant before and the instant after;
  - E94's GATE: every icon a row names resolves in the operator's catalogue, is an `icon`, is
    `operator_approved` and is `render_eligible` - and the compiler refuses one that is not, by name;
  - THE DOCK FORM IS UNTOUCHED: its two committed frames are byte-identical;
  - A SEEK IS THE PLAY: the same t gives the same page, reached forwards or backwards.
"""
from __future__ import annotations

import contextlib
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

MODULE = ROOT / "content/video_engine/scripts/species/agenda.mjs"
SURFACE = "agenda-page"
DOCK_SURFACES = ("agenda-two", "species-proof@proof-agenda")   # the dock form's committed frames
BOARD = G.AGENDA_PAGE["target"]                                # the page's own board, in frame fractions
ROWS = G.AGENDA_PAGE_ROWS
AT = G.AGENDA_PAGE["at"]


def dial(name: str) -> float:
    """One AGENDA dial, read from the module so this file cannot drift from the painter it judges."""
    m = re.search(rf"^\s*{re.escape(name)}:\s*([0-9.]+)", MODULE.read_text(encoding="utf-8"), re.M)
    assert m, f"{name} is not a dial of AGENDA in {MODULE.name}"
    return float(m.group(1))


def row_at(i: int) -> float:
    return float(ROWS[i].get("at", AT))


def read_at(i: int) -> float:
    """E93's instant: the row's own word plus the number's lead plus the text's rise - its sentence, read."""
    return row_at(i) + dial("NUM_LEAD") + dial("ROW_S")


def landed_at(i: int) -> float:
    return read_at(i) + dial("PAGE_STAMP_LAG") + dial("PAGE_STAMP_S") + dial("PAGE_SETTLE_S")


# ---- the catalogue (E93 / E94), with no browser ------------------------------------------------------


def test_every_row_names_a_catalogued_icon_the_operator_approved():
    """E93: an agenda row carries an icon; E94: only the operator's own, approved and render-eligible."""
    assert len(ROWS) >= 2
    for i, row in enumerate(ROWS):
        entry = B.catalogue_icon(row["icon"])
        assert entry["kind"] == "icon", (i, entry["kind"])
        assert entry["review_state"] == "operator_approved", (i, entry["review_state"])
        assert entry["rights_state"] == "approved", (i, entry["rights_state"])
        assert entry["render_eligible"] is True, i
        assert entry["sha256_measured"] == entry["sha256"], f"row {i + 1}: the file and the record disagree"
    assert B.species_props(G.AGENDA_PAGE) == [r["icon"] for r in ROWS]


def test_an_icon_the_operator_did_not_approve_is_refused_by_name():
    """The gate is the catalogue's own fields, not a list in the compiler: each refusal names the id and why."""
    catalog = B.icon_catalog()
    ok = ROWS[0]["icon"]
    for field, value, needle in (("kind", "plate", "not an icon"),
                                 ("review_state", "review_only", "operator-approved"),
                                 ("render_eligible", False, "render_eligible")):
        keep = catalog[ok][field]
        catalog[ok][field] = value
        try:
            with pytest.raises(ValueError, match=re.escape(needle)):
                B.catalogue_icon(ok)
        finally:
            catalog[ok][field] = keep
    with pytest.raises(ValueError, match="never invent an image"):
        B.catalogue_icon("prop-icon-there-is-no-such-cutout-v9")


def test_the_compiler_refuses_a_page_that_does_not_fill_its_plate_and_a_dock_that_wears_the_pages_words():
    """E99 s16 held at compile time: a page form parked in a corner is not a page, and the dock form has no
    icon and no title to give (so the dock form cannot drift into half a page form)."""
    ok = json.loads(json.dumps(G.AGENDA_PAGE))
    assert B.validate_species([ok], (0, 0, 0), "plate-plain") == []

    corner = json.loads(json.dumps(G.AGENDA_PAGE))
    corner["target"] = {"kind": "region", "x0": 0.30, "y0": 0.50, "x1": 0.95, "y1": 0.95}
    errs = B.validate_species([corner], (0, 0, 0), "plate-plain")
    assert any("fills its own plate" in e for e in errs), errs

    word = json.loads(json.dumps(G.AGENDA_PAGE))
    word["form"] = "plate"
    assert any("is not one the agenda has" in e for e in B.validate_species([word], (0, 0, 0), "plate-plain"))

    bare = json.loads(json.dumps(G.AGENDA_PAGE))
    del bare["rows"][1]["icon"]
    assert any("E93" in e for e in B.validate_species([bare], (0, 0, 0), "plate-plain"))

    dock = json.loads(json.dumps(G.AGENDA_PAGE))
    del dock["form"]
    errs = B.validate_species([dock], (0, 0, 0), "plate-plain")
    assert any("title" in e for e in errs) and any("page form's stamp" in e for e in errs), errs


def test_the_stamp_is_a_pure_function_of_the_rows_own_read_instant():
    """The painter's clock, restated where a reader can see it: every stamp hangs off its row's sentence."""
    for i in range(len(ROWS)):
        assert read_at(i) > row_at(i)
        assert landed_at(i) > read_at(i) + dial("PAGE_STAMP_LAG")
    assert landed_at(len(ROWS) - 1) < RB.PROOF_FRAMES[f"{SURFACE}@proof-full"][2], \
        "the @proof-full instant must sit AFTER the last stamp has settled"
    assert RB.PROOF_FRAMES[f"{SURFACE}@proof-first-row"][2] == pytest.approx(read_at(0), abs=0.01)


# ---- the page, in the player --------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const q = (sel) => [...document.querySelectorAll('#species ' + sel + ', #species-under ' + sel)];
  const sb = document.getElementById('stage').getBoundingClientRect();
  const bb = (e) => { const r = e.getBoundingClientRect();
    return { x: (r.left - sb.left) / sb.width, y: (r.top - sb.top) / sb.height,
             w: r.width / sb.width, h: r.height / sb.height }; };
  const of = (sel) => q(sel).map((e) => Object.assign({ text: e.textContent }, bb(e)));
  return { rows: of('text.agrow'), nums: of('text.agnum'), plates: q('rect.agplate').map(bb),
           title: of('text.agtitle'), figs: of('text.agfig'),
           icons: q('image.agicon').map((e) => Object.assign({ href: (e.getAttribute('href') || '').slice(0, 24) }, bb(e))) };
}"""


def _union(boxes: list[dict]) -> dict | None:
    if not boxes:
        return None
    x0 = min(b["x"] for b in boxes); y0 = min(b["y"] for b in boxes)
    x1 = max(b["x"] + b["w"] for b in boxes); y1 = max(b["y"] + b["h"] for b in boxes)
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


@contextlib.contextmanager
def _browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        yield br
    finally:
        br.close(); pw.stop()


class _Player:
    """One surface, served and mounted from the GOLDEN's own source, so the test and the committed frames
    read the same page."""

    def __init__(self, browser, surface: str):
        tl, uris, _t, aspect = RB.load_surface(surface)
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": w, "height": h}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, w, h)

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


@needs_browser
def test_the_page_form_fills_its_board_and_the_dock_form_does_not():
    """E99 s16's whole complaint, measured: the page form's rows cover their board; the dock form's rows,
    measured the same way on their own golden, sit in a corner with the plate empty around them."""
    with _browser() as br:
        page = _Player(br, SURFACE)
        try:
            read = page.at(G.FRAME_T[SURFACE])
            assert not page.errors, page.errors
            assert len(read["rows"]) == len(ROWS) and len(read["plates"]) == len(ROWS)
            board_w = BOARD["x1"] - BOARD["x0"]
            board_h = BOARD["y1"] - BOARD["y0"]
            mounts = _union(read["plates"])
            written = _union(read["plates"] + read["title"])
            # the bar is the board itself, less the block's own daylight (PAGE_PAD, read from the module):
            # anything short of that is board the page did not use
            pad_x, pad_y = dial("PAGE_PAD") / 1920, dial("PAGE_PAD") / 1080
            assert mounts["w"] >= board_w - 2 * pad_x - 0.005, mounts    # the rows span the board's width ...
            assert mounts["h"] >= 0.65 * board_h, mounts                 # ... and the height the title's room leaves them
            assert written["h"] >= board_h - 2 * pad_y - 0.02, written   # title + rows: the board, top to bottom
            assert written["y"] <= BOARD["y0"] + 0.05, written
            # no two thirds empty, stated as the frame sees it
            assert mounts["h"] >= 0.60 and mounts["w"] >= 0.80, mounts
            # every row is the same height: the rows divide the board, they do not pile up at one end
            hs = sorted(p["h"] for p in read["plates"])
            assert hs[-1] - hs[0] < 0.005, read["plates"]
            assert read["title"] and read["title"][0]["text"] == G.AGENDA_PAGE["title"]
            assert [r["text"] for r in read["rows"]] == [r["text"] for r in ROWS]
            assert [f["text"] for f in read["figs"]] == [r["sub"] for r in ROWS if r.get("sub")]
        finally:
            page.close()

        dock = _Player(br, "agenda-two")
        try:
            read = dock.at(G.FRAME_T["agenda-two"])
            block = _union(read["rows"] + read["nums"])
            assert block["h"] < 0.40 and block["w"] < 0.45, \
                f"the dock form is the corner block E99 s16 asked to be beautified, not a page: {block}"
        finally:
            dock.close()


@needs_browser
def test_a_rows_icon_is_not_on_the_page_until_its_sentence_has_been_read():
    """E93, row by row: at the instant the sentence finishes there is no icon; after the stamp's own clock
    there is exactly one more, and it is the catalogued cutout that row named."""
    with _browser() as br:
        page = _Player(br, SURFACE)
        try:
            assert page.at(row_at(0) - 0.01)["icons"] == [], "nothing is stamped before the first row exists"
            for i in range(len(ROWS)):
                before = page.at(read_at(i))          # the sentence is exactly written - the stamp has not opened
                after = page.at(landed_at(i) + 0.01)  # ... and now it has landed and settled
                assert len(before["icons"]) == i, f"row {i + 1}: an icon before its sentence was read: {before['icons']}"
                assert len(after["icons"]) == i + 1, f"row {i + 1}: no icon after its sentence was read"
                assert all(ic["href"].startswith("data:image/png;base64,") for ic in after["icons"])
            landed = page.at(G.FRAME_T[SURFACE])
            assert len(landed["icons"]) == len(ROWS)
            for ic, plate in zip(landed["icons"], landed["plates"]):   # each stamp sits inside its own row
                assert plate["x"] <= ic["x"] and ic["x"] + ic["w"] <= plate["x"] + plate["w"] + 1e-3, (ic, plate)
                assert plate["y"] <= ic["y"] + 1e-3 and ic["y"] + ic["h"] <= plate["y"] + plate["h"] + 1e-3, (ic, plate)
            mid = page.at(RB.PROOF_FRAMES[f"{SURFACE}@proof-stamp"][2])   # mid-fall: bigger than a landed stamp
            assert mid["icons"][-1]["w"] > landed["icons"][-1]["w"] * 1.1, (mid["icons"][-1], landed["icons"][-1])
            assert not page.errors, page.errors
        finally:
            page.close()


@needs_browser
def test_a_seek_is_the_play_on_the_agenda_page():
    """Nothing is stored: the same t gives the same page reached forwards, backwards or cold."""
    with _browser() as br:
        page = _Player(br, SURFACE)
        try:
            t = RB.PROOF_FRAMES[f"{SURFACE}@proof-stamp"][2]
            for x in range(0, int(t * 4) + 1):    # walked UP to it ...
                page.at(x / 4)
            forward = page.at(t)
            for x in range(0, int((20 - t) * 4) + 1):   # ... and walked back DOWN to it
                page.at(20 - x / 4)
            backward = page.at(t)
            assert json.dumps(forward, sort_keys=True) == json.dumps(backward, sort_keys=True)
        finally:
            page.close()
    assert RB.render_surface(SURFACE) == RB.render_surface(SURFACE), "two cold renders of one instant differ"


@needs_browser
def test_the_dock_form_is_byte_identical():
    """The page form is opt-in: `form` absent takes the code the dock form always took, so its committed
    frames - the two the operator has already read - do not move by a pixel."""
    assert RB.check(list(DOCK_SURFACES)) == []


@needs_browser
def test_the_pages_own_frames_are_the_committed_ones():
    assert RB.check([SURFACE] + [n for n in RB.PROOF_FRAMES if n.startswith(SURFACE + "@")]) == []
