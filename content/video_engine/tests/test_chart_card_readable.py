"""P69 T10c - A CHART CARD IS DRAWN FOR ITS OWN SIZE: the whole card, bigger type, thicker lines.

The operator (2026-09-22), on row 7's thrown Bravos card: "Those charts still seem tough to read to me" and "Evidence
cards that are using charts need to use the whole card and use bigger fonts and thicker lines". `chart_card` rendered
the FULL ledger page and shrank it to the dock's width, so every label shrank with the card. Under the `card` profile
(`chart_card.render_card(card_w=...)`, ledger_page.apply_card) the page is laid out for the card's DISPLAYED box, and
this file measures it on the served player, at row 7's own card - the Bravos pairing, `ev-divergence-v1` with the
memory line dropped (build_episode_h._hook_object), read on the studio's left monitor at 0.34 of the stage:

  (1) THE FLOOR       every word the card writes, AS DISPLAYED at the card's size, is at or above E99 s90's phone floor
                      (12 phone px on a 16:9 frame played 390 px wide = 59.08 stage px); the full page shrunk to the card
                      (today's card) is measured far under it.
  (2) EDGE TO EDGE    the chart runs from the card's margin to its margin, the plot keeps at least PLOT_MIN of the card's
                      height, no sub, no y label, no badge rail, no key, at most one short source line.
  (3) THICKER LINES   every line, as displayed, at least twice the full page's own line, as displayed (the same object
                      drawn as a full-stage page, measured in the same browser).
  (4) SHORT BADGES    the end tags are the values alone, in their lines' ink; the x ticks are the two ends; the card
                      keeps its title and its numbers.
  (5) THE HAND-OVER   a card drawn for its size is thrown and PUSHED into the page (`camera=`, row 7) - the full page
                      stands in the card's box from the push's first frame and the card gives way over HANDOVER_U of
                      it, so at the match only the page is left; a SNAP grows the full page out of the card's rectangle
                      and hides the card on its first frame, as it always did. A card drawn the old way pushes exactly as
                      before (the page waits for the match).
  (6) OFF             without `card_w` chart_card writes no sidecar, the compiler's evidence entry carries no `card`,
                      and a row may not name the profile; the goldens hold the rest.
"""
from __future__ import annotations

import copy
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
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
DIVERGENCE = "ev-divergence-v1"
HOOK_ID = "fx-divergence-hook-card"
AID = "dock-fx-two-line-copy"
READ = {"centre_w": 0.34, "centre_x": 0.26, "centre_y": 0.25}   # build_episode_h.BRAVOS_READ: row 7's left monitor
CARD_W = READ["centre_w"] * 1920                                 # the card's first read size: 652.8 px, 0.34 of the stage
T_CARD, T_PAGE = 1.0, 4.0                                        # the card is thrown at 1.0; the page arrives at 4.0
SNAP_S = 0.45                                                    # the player's SNAP_S (build_scene_timeline_f.CAMERA_ARRIVAL_S)
PLATE = EP / "host/H-1-studio.png"
FLOOR = 12.0 * 1920 / 390                                          # E99 s90's floor, 59.08 displayed stage px (test_longform_profile.PHONE_FLOOR / PHONE_W)
TOL = 0.05


# ---- row 7's card, as a fixture ---------------------------------------------------------------------------------------

def hook_object() -> dict:
    """build_episode_h._hook_object, copied: the verified object, the memory line dropped, the card's own words."""
    div = json.loads((EP / f"evidence/objects/{DIVERGENCE}.series.json").read_text(encoding="utf-8"))
    obj = copy.deepcopy(div)
    mem = next(i for i, s in enumerate(div["series"]) if str(s.get("name", "")).startswith("MEMORY"))
    obj["series"] = [s for i, s in enumerate(div["series"]) if i != mem]
    obj["badges"] = [b for b in (div.get("badges") or []) if not str(b.get("label", "")).startswith("MEMORY")]
    obj["title"], obj["sub"] = "Two lines, one warning", "Mega-cap tech against the chip industry. 100 = Aug '25, log scale"
    obj.pop("names_note", None)
    return obj


def write_hook(tmp: Path) -> Path:
    out = tmp / "evidence/objects" / f"{HOOK_ID}.series.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(hook_object(), indent=1), encoding="utf-8")
    return out


def card_place(aspect: float) -> dict:
    w = round(CARD_W)
    h = round(w * aspect)
    return {"x": round(READ["centre_x"] * 1920 - w / 2), "y": round(READ["centre_y"] * 1080 - h / 2), "w": w, "h": h}


def push_timeline(tmp: Path, card_png: Path, how: str = "camera") -> tuple[dict, dict]:
    """Row 7's two scenes: the studio with the card thrown at T_CARD, then the page it becomes at T_PAGE by `how` -
    `camera` (the push, row 7's own) or `snap`. The dock's evidence entry is the compiler's (`dock_card_profile`)."""
    from PIL import Image
    im = Image.open(card_png)
    place = card_place(im.height / im.width)
    dock = B.dock_entry(AID, 0, T_CARD, T_PAGE, 0, B.DOCK_KIND_IMAGE, place, "throw", "paper", True)
    ev = {AID: {"title": "Two lines, one warning", "source": "fixture", "species": "chart",
                "document": {"path": card_png.name, "sha256": "0" * 64}, "badges": [], **B.dock_card_profile(card_png)}}
    write_hook(tmp)
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(f"ledger:{HOOK_ID}:line:0:right:{how}={AID}:cut;card=no", (0, 0, 0), tmp)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": {"asset_id": "fx-studio", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, T_PAGE], "docks": [dock], "species": []},
              {"scene_id": "s02", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [T_PAGE, G.RUNTIME], "docks": [], "species": []}]
    B.extend_camera_cards(scenes)
    tl = G._timeline("P69 T10c: the card becomes the page", scenes, ev, "16:9")
    uris = G._base_uris()
    uris["fx-studio"] = B.data_uri(PLATE, 1920)
    uris[AID] = B.data_uri(card_png)
    uris.update(B.longform_assets(tl))
    return tl, uris


# ---- the profile and the row (no browser) -----------------------------------------------------------------------------

def test_the_card_is_stated_at_the_phone_floor_as_displayed():
    assert LPG.card_floor_px() == pytest.approx(59.0769, abs=1e-3)
    assert LPG.CARD_TYPE_PX >= LPG.card_floor_px() - 1e-9
    assert LPG.CARD_STROKE_X >= 2.0
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LP_CARD = Object\.freeze\(\{ TYPE_PX: 12 \* 1920 / 390, PAD_PX: ([\d.]+), GAP_PX: [\d.]+, STROKE_X: ([\d.]+),", src)
    assert m, "the engine's LP_CARD states the floor as ledger_page does"
    assert float(m.group(1)) == LPG.CARD_PAD_PX and float(m.group(2)) == LPG.CARD_STROKE_X


def test_apply_card_draws_the_page_as_a_card():
    page = LPG.build_spec(hook_object(), "line")
    assert page["axes"].get("ylabel") and len(page["axes"]["xticks"]) == 4 and page["sub"] and page["badges"]
    LPG.apply_card(page, CARD_W, CARD_W * 9 / 16)
    ax = page["axes"]
    assert ax["readability"] == "card" and ax["card_w"] == 652.8 and ax["card_h"] == 367.2
    assert ax["tag_form"] == "badge", "two lines end on +21%: the shortening stops at the badge (the value and a short name)"
    assert [x[1] for x in ax["xticks"]] == ["Oct '25", "Jul '26"], "the minor ticks are dropped: the two ends stay"
    assert "ylabel" not in ax and "key" not in ax and page["sub"] == "" and page["badges"] == []
    assert page["source"] == "Yahoo Finance", "the source's first clause, on one line"
    assert page["title"] == "Two lines, one warning", "the card keeps its title"


def test_a_long_source_is_dropped_rather_than_shrunk():
    assert LPG.card_source("A very long source name that no card of this size could ever hold on one line", CARD_W) == ""
    assert LPG.card_source("Yahoo Finance - pairing after Bravos Research", CARD_W) == "Yahoo Finance"


def test_a_card_is_drawn_by_two_builders_and_is_never_a_row_option(tmp_path):
    with pytest.raises(ValueError, match=r"'card' is drawn by the dense-line and story builders.*'race'"):
        LPG.apply_card({"builder": "race", "axes": {}}, CARD_W, CARD_W * 9 / 16)
    write_hook(tmp_path)
    with pytest.raises(ValueError, match=r"readability 'card' is not one of"):
        B.world_for_plate(f"ledger:{HOOK_ID}:line;readability=card", (0, 0, 0), tmp_path)


def test_the_compiler_reads_the_card_sidecar_and_nothing_else(tmp_path):
    png = tmp_path / "card.png"
    png.write_bytes(b"")
    assert B.dock_card_profile(png) == {}, "a card with no sidecar: the evidence entry is what it was"
    png.with_suffix(".card.json").write_text(json.dumps({"profile": "card", "card_w": 652.8, "card_h": 367.2}), encoding="utf-8")
    assert B.dock_card_profile(png) == {"card": {"card_h": 367.2, "card_w": 652.8, "profile": "card"}}
    png.with_suffix(".card.json").write_text(json.dumps({"profile": "page"}), encoding="utf-8")
    with pytest.raises(ValueError, match="not a card profile's"):
        B.dock_card_profile(png)


def test_the_dock_kit_redraws_a_card_whose_size_changed_and_drops_a_stale_sidecar(tmp_path, monkeypatch):
    import chart_card as CC
    from authoring import docks as D
    calls = []

    def fake(series, out, variant, aspect=None, card_w=None):
        calls.append(card_w)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"png")
        if card_w is not None:
            CC.card_sidecar(out).write_text(json.dumps({"profile": "card", "card_w": round(card_w, 2)}), encoding="utf-8")
        return out

    monkeypatch.setattr(CC, "render_card", fake)
    series = write_hook(tmp_path)
    D.chart_card("dock-x", series, tmp_path, "line", card_w=CARD_W)
    D.chart_card("dock-x", series, tmp_path, "line", card_w=CARD_W)          # unchanged: not redrawn
    D.chart_card("dock-x", series, tmp_path, "line", card_w=0.4 * 1920)      # a new size: redrawn
    D.chart_card("dock-x", series, tmp_path, "line")                         # no size: redrawn as the page, sidecar gone
    assert calls == [CARD_W, 0.4 * 1920, None]
    assert not CC.card_sidecar(tmp_path / "docks" / "dock-x.png").exists()


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

# every word the page writes, its size as RENDERED on the stage (CSS px x the element's own scale to the stage), and
# every drawn line's stroke as rendered
CARD_PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp;
  const stage = document.getElementById('stage').getBoundingClientRect();
  const vis = (e) => { const c = getComputedStyle(e), r = e.getBoundingClientRect();
    return c.display !== 'none' && c.visibility !== 'hidden' && +c.opacity > 0.05 && r.width > 0.5 && r.height > 0.5
      && !(e.closest && e.closest('[style*="display: none"]')); };
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  const cm = st.chart.getScreenCTM(), chartK = Math.hypot(cm.a, cm.b);
  const pageK = st.page.getBoundingClientRect().width / (st.page.offsetWidth || 1);
  const words = [];
  for (const e of st.page.querySelectorAll('.lp-title, .lp-sub, .lp-src')) if (vis(e) && (e.textContent || '').trim())
    words.push({ role: e.className, text: e.textContent.trim(), px: parseFloat(getComputedStyle(e).fontSize) * pageK, box: R(e) });
  for (const e of st.chart.querySelectorAll('text')) if (vis(e) && (e.textContent || '').trim() && +(e.getAttribute('opacity') || 1) > 0.05)
    words.push({ role: 'svg:' + e.getAttribute('class'), text: e.textContent.trim(), px: parseFloat(getComputedStyle(e).fontSize) * chartK, box: R(e) });
  const lines = [...st.chart.querySelectorAll('path.ser')].filter(p => !p.classList.contains('muted'))
    .map(p => parseFloat(getComputedStyle(p).strokeWidth) * chartK);
  const panel = st.chart.querySelector('rect.lp-panel');
  return { card: st.page.classList.contains('lp-readability-card'), words, lines, chart: R(st.chart), panel: panel ? R(panel) : null,
           xticks: (st.marks || []).filter(m => m.role === 'xtick' && m.el).map(m => m.el.textContent),
           xboxes: [...st.chart.querySelectorAll('text.lab')].filter(e => e.isConnected && vis(e) && +(e.getAttribute('opacity') || 1) > 0.05).map(R),
           tags: [...st.chart.querySelectorAll('text.sname')].filter(vis).map(e => ({ text: e.textContent, fill: getComputedStyle(e).fill,
             value: (e.firstChild && e.firstChild.nodeType === 3 ? e.firstChild.textContent : e.textContent).trim(),
             chips: [...e.querySelectorAll('tspan.tagchip')].map(c => ({ text: c.textContent, px: parseFloat(getComputedStyle(c).fontSize) * chartK })) })),
           series: (st.paths || []).filter(p => !p.muted).map(p => getComputedStyle(p.p).stroke),
           hidden: ['.lp-sub', '.lp-rail', '.lp-key'].map(q => { const e = st.page.querySelector(q); return !e || !vis(e); }),
           src: (() => { const e = st.page.querySelector('.lp-src'); return e && vis(e) ? e.textContent.trim() : ''; })(),
           field: R(st.page.querySelector('.lp-field')) };
}"""

PUSH_PROBE = """() => {
  const stage = document.getElementById('stage').getBoundingClientRect();
  const dock = [...document.querySelectorAll('.dock')].find(d => d.dataset.slide === '%s');
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  const lp = wB.querySelector('.lp'), im = dock && dock.querySelector('img');
  return { arr: window.__camArr ? window.__camArr() : null, wB: { op: +getComputedStyle(wB).opacity, tf: wB.style.transform },
           page: lp ? R(lp) : null, img: im ? R(im) : null, title: wB.querySelector('.lp-title') ? R(wB.querySelector('.lp-title')) : null,
           dock: dock ? { op: +(dock.style.opacity === '' ? 1 : dock.style.opacity), vis: dock.style.visibility,
                          shown: getComputedStyle(dock).visibility !== 'hidden' && getComputedStyle(dock).display !== 'none', box: R(dock) } : null };
}""" % AID


def _serve(browser, tl: dict, uris: dict, tmp: Path, name: str):
    html = tmp / f"{name}.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(html.parent)
    w, h = RB.STAGE[tl.get("aspect") or "16:9"]
    page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)
    page.wait_for_function("document.fonts.status === 'loaded'")
    return page, srv, errors, (w, h)


def _at(page, t: float, size, probe: str):
    RB.frame_png(page, t, size)
    page.wait_for_timeout(80)
    RB.frame_png(page, t, size)
    return page.evaluate(probe)


@pytest.fixture(scope="module")
def cards(tmp_path_factory):
    """Row 7's card drawn both ways, the page it is of drawn full stage, and the push and the snap served both ways."""
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    import chart_card as CC
    from playwright.sync_api import sync_playwright
    tmp = tmp_path_factory.mktemp("cards")
    series = write_hook(tmp / "ep")
    out = {"before_png": CC.render_card(series, tmp / "before" / "card.png", "line"),
           "after_png": CC.render_card(series, tmp / "after" / "card.png", "line", card_w=CARD_W)}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for key, card_w in (("old", None), ("page", None), ("card", CARD_W)):
                tl, uris, _aspect = CC.card_timeline(series, "line", card_w=card_w)
                if key == "page":   # the page the card is of, as the full-stage page it becomes (the stroke the card doubles)
                    tl["scenes"][0]["world"]["page"]["full_stage"] = True
                page, srv, errors, size = _serve(browser, tl, uris, tmp, key)
                try:
                    out[key] = dict(_at(page, CC.LAND_T, size, CARD_PROBE), errors=errors)
                finally:
                    page.context.close(); srv.shutdown()
            for how in ("camera", "snap"):
                for tag in ("before", "after"):
                    tl, uris = push_timeline(tmp / f"{how}-{tag}", out[f"{tag}_png"], how)
                    page, srv, errors, size = _serve(browser, tl, uris, tmp, f"{how}-{tag}")
                    try:
                        got = {}
                        for u in (0.3, 0.5, 0.7, 1.05):
                            got[u] = _at(page, round(T_PAGE + u * SNAP_S, 4), size, PUSH_PROBE)
                        got["read"] = _at(page, T_PAGE - 0.4, size, PUSH_PROBE)
                        got["errors"] = errors
                        out[f"{how}-{tag}"] = got
                    finally:
                        page.context.close(); srv.shutdown()
        finally:
            browser.close()
    return out


def _displayed(px: float) -> float:
    return px * CARD_W / 1920


@needs_browser
def test_every_word_on_the_card_is_at_the_phone_floor_as_displayed(cards):
    got = cards["card"]
    assert not got["errors"], got["errors"]
    assert got["card"], "the page is drawn under the card profile"
    assert got["words"], "the card writes words"
    small = min(got["words"], key=lambda w: w["px"])
    assert _displayed(small["px"]) >= FLOOR - TOL, (round(_displayed(small["px"]), 2), small)


@needs_browser
def test_the_full_page_shrunk_to_the_card_was_far_under_the_floor(cards):
    """Today's card, measured (the RED this slice answers): chart_card crops the charcoal page (its field's box on the
    stage) and the dock shows that box CARD_W wide - so a word's displayed size is its rendered size x CARD_W / the box."""
    got = cards["old"]
    assert not got["card"]
    shrink = CARD_W / got["field"][2]
    small = min(got["words"], key=lambda w: w["px"])
    shown = small["px"] * shrink
    assert shown < FLOOR / 4, (round(shown, 2), small)
    lines = [v * shrink for v in got["lines"]]
    assert max(lines) < 0.5 * max(cards["page"]["lines"]), "and its lines thinner than the page's own"


@needs_browser
def test_the_chart_runs_edge_to_edge_and_the_plot_keeps_its_room(cards):
    got = cards["card"]
    pad = LPG.CARD_PAD_PX * 1920 / CARD_W
    x, y, w, h = got["chart"]
    assert x == pytest.approx(pad, abs=2), got["chart"]
    tags = [wd["box"] for wd in got["words"] if wd["role"] == "svg:sname"]
    right = max(b[0] + b[2] for b in tags)   # the end badges stand past the plot's right edge, inside the card's margin
    assert 1920 - pad - 3 * LPG.CARD_TYPE_PX * 1920 / CARD_W / 4 <= right <= 1920 - pad + 2, (right, tags)
    px, py, pw, ph = got["panel"]
    assert ph >= 0.4 * 1080 - 1, ("the plot keeps PLOT_MIN of the card", got["panel"])
    assert all(got["hidden"]), "no sub, no badge rail, no key"
    assert not any(w["role"].startswith("svg:") and "ylabel" in w["role"] for w in got["words"])
    assert got["src"] in ("", "Yahoo Finance"), "at most one short source line"


@needs_browser
def test_every_line_is_at_least_twice_the_pages_as_displayed(cards):
    page_line = max(cards["page"]["lines"])            # the full page, on the stage it fills
    card_lines = [_displayed(v) for v in cards["card"]["lines"]]
    assert card_lines and min(card_lines) >= 2 * page_line - 0.05, (card_lines, page_line)


@needs_browser
def test_the_end_tags_are_short_badges_in_their_lines_ink_and_the_card_keeps_its_title_and_number(cards):
    got = cards["card"]
    assert [t["value"] for t in got["tags"]] == [s["label"] for s in hook_object()["series"]]
    assert [t["fill"] for t in got["tags"]] == got["series"], "each value in its own line's ink"
    assert got["xticks"] in (["Oct '25", "Jul '26"], ["Oct '25 – Jul '26"]),         "the axis states its span (E28): both ends, or one range label when the ends would meet - never the start alone"
    boxes = got["xboxes"]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert not (a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]), ("no label over another", a, b)
    assert any(w["text"] == "Two lines, one warning" for w in got["words"])


@needs_browser
def test_the_push_hands_over_to_the_full_page(cards):
    """(3): the card drawn for its size is never what the push grows - the page stands in its box and takes over."""
    got = cards["camera-after"]
    assert not got["errors"], got["errors"]
    read = got["read"]
    assert read["dock"]["shown"] and read["dock"]["op"] == pytest.approx(1.0), "the card is read at its size first"
    early, mid, late = got[0.3], got[0.5], got[0.7]
    for s in (early, mid, late):
        assert s["arr"] and s["wB"]["op"] == pytest.approx(1.0), "the full page stands under the card through the push"
        assert s["wB"]["tf"].startswith("translate("), "... in the card's own box"
    # the stage's region of the page IS the card's picture as the eye carries it (drawn on to the stage by u^3)
    for s in (early, mid):
        u = s["arr"]["u"]
        px, py, pw, ph = s["page"]
        ix, iy, iw, ih = s["img"]
        assert abs(pw / iw - 1) < 0.02 + 2 * u ** 3 and abs(px - ix) < 2 + ix * u ** 3 and abs(py - iy) < 2 + iy * u ** 3, (s["page"], s["img"], u)
    assert early["dock"]["op"] > mid["dock"]["op"] > late["dock"]["op"], "the card gives way over the push"
    assert late["dock"]["op"] == pytest.approx(0.0, abs=1e-3), "gone by HANDOVER_U"
    match = got[1.05]
    assert match["arr"] is None and not match["dock"]["shown"], "at the match: only the page"
    assert not match["wB"]["tf"].startswith("translate("), match["wB"]["tf"]


@needs_browser
def test_a_card_drawn_the_old_way_pushes_exactly_as_before(cards):
    got = cards["camera-before"]
    assert not got["errors"], got["errors"]
    for u in (0.3, 0.5, 0.7):
        s = got[u]
        assert s["arr"] and s["wB"]["op"] == pytest.approx(0.0), "the page waits for the eye (P49 T5)"
        assert s["dock"]["shown"] and s["dock"]["op"] == pytest.approx(1.0)
        assert not s["wB"]["tf"].startswith("translate("), s["wB"]["tf"]


@needs_browser
def test_under_a_snap_the_full_page_grows_and_the_card_render_never_does(cards):
    """(3) under the throw-then-zoom: the page grows out of the card's rectangle as the FULL page and the card render
    hides on the snap's first frame - for a card drawn for its size exactly as for one drawn the old way."""
    for tag in ("after", "before"):
        got = cards[f"snap-{tag}"]
        assert not got["errors"], got["errors"]
        assert got["read"]["dock"]["shown"], tag
        for u in (0.3, 0.5, 0.7):
            assert not got[u]["dock"]["shown"], (tag, u, got[u]["dock"])
            assert got[u]["wB"]["op"] == pytest.approx(1.0) and got[u]["title"], (tag, u)


@needs_browser
def test_without_the_profile_chart_card_writes_what_it_wrote(cards):
    import chart_card as CC
    from PIL import Image
    before, after = cards["before_png"], cards["after_png"]
    assert not CC.card_sidecar(before).exists()
    assert Image.open(before).width == 720
    assert Image.open(after).size == (round(CC.CARD_RES * CARD_W), round(round(CC.CARD_RES * CARD_W) * 9 / 16))
    assert json.loads(CC.card_sidecar(after).read_text(encoding="utf-8")) == {"card_h": 367.2, "card_w": 652.8, "profile": "card"}
    assert cards["page"]["card"] is False


# ---- the names a value cannot carry (the parent's frame read of the first card) -------------------------------------

def test_card_names_stop_the_shortening_at_the_badge_for_values_two_lines_share():
    page = LPG.build_spec(hook_object(), "line")
    names = LPG.card_names(page)
    labels = {i: s["label"] for i, s in enumerate(page["series"])}
    assert set(names) == {i for i, v in labels.items() if list(labels.values()).count(v) > 1}, (names, labels)
    assert sorted(names.values()) == ["MEGA-CAP", "S&P"], "the lines' own badge labels, cut to a first word that still tells them apart"
    LPG.apply_card(page, CARD_W, CARD_W * 9 / 16)
    assert page["axes"]["tag_form"] == "badge"
    assert LPG.CARD_NAME_MIN * LPG.CARD_TYPE_PX <= page["axes"]["card_chip_px"] <= LPG.CARD_TYPE_PX
    one = LPG.build_spec(dict(hook_object(), series=hook_object()["series"][:1]), "line")
    assert LPG.card_names(one) == {}, "a value no other tag shows keeps the value alone"


@needs_browser
def test_no_two_visible_end_tags_on_a_card_read_the_same(cards):
    """The parent's frame read: two "+21%" tags told apart by colour alone. Every visible end tag's whole text differs."""
    texts = [t["text"].strip() for t in cards["card"]["tags"]]
    assert len(texts) == len(set(texts)), texts
    chips = [c for t in cards["card"]["tags"] for c in t["chips"]]
    assert chips, "the two lines that share a value carry their names"
    for c in chips:
        assert _displayed(c["px"]) >= LPG.CARD_NAME_MIN * FLOOR - TOL, (round(_displayed(c["px"]), 2), c)
