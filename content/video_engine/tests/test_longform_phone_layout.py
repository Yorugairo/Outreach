"""P72 T12 (R26-339; D1 - the long form KEEPS its `phone` preset): A ONE-BAR STACKED PAGE HOLDS ON `longform:phone`.

Found by P70 T5 before the brace, on the base (`$SP/p70-t5/frames/probe-lf-phone.png`): at `longform:phone` the page's
61.4 px type left the bars page's legacy 1000-unit viewBox a plot 795 px wide on the left 41 % of the stage, so the T64
key (the parts' names) had nowhere clear to stand and sat over the bar's total, "Q1 2026" - wider than its capped 196 px
bar - was set on two lines, and the capex figure shrank to its bar under the E99 s90 floor (57.5 px). Only this preset
holds the brace's 59.08 px floor, so it is kept and made to hold (D1):

  - a bars page at `phone` draws its chart across the stage, as a dense-line page does (`lpLongformBarsVW`, mirrored by
    `ledger_page.longform_bars_vw` for the estimated boxes): the bars stay capped and centred (E99 s96), the room is
    the key's and the names';
  - a category name keeps ONE line while it fits its own slot (the bar's pitch less the air): it wraps only where it
    would run into its neighbour's column;
  - no word on the page is set under the floor: a part's figure too wide for its bar at the floor takes its leader
    beside the bar, and the key never shrinks under it.

Every other preset is the page it was, byte for byte (the viewBox stays 1000, a name wraps at its bar's width).
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
for p in (REPO / "content/video_engine/scripts", REPO / "content/video_engine/tests/golden"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402

FLOOR = 12 * 1920 / 390   # E99 s90: 59.08 stage px (test_longform_profile.PHONE_FLOOR / PHONE_W)
SAFE_RIGHT = LPG.LAND_PHONE_SAFE_RIGHT * 1920


def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


def _one_bar(preset: str | None, brace: bool) -> tuple[dict, dict]:
    """The Q1 2026 stacked bar alone on a bars page (the brace golden's page), braced or not, in the long form at
    `preset` (None: the plain page)."""
    if brace:
        return G.brace_funding(longform=preset)
    import build_scene_timeline_f as BST
    series = G.brace_funding_series()
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "bars", None, "right"))
        if preset:
            LPG.apply_longform(page, preset)
        world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
        BST.check_segments(world, [])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    tl = G._timeline("one stacked bar", scenes, {}, "16:9")
    return tl, (dict(G._base_uris(), **BST.longform_assets(tl)) if preset else G._base_uris())


READ = """() => { const s = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp);
  const lp = w.__lp, R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  const op = (e) => { let n = e, o = 1; while (n && n !== document.body) { const cs = getComputedStyle(n);
    if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +(cs.opacity || 1);
    const a = n.getAttribute && n.getAttribute('opacity'); if (a != null && a !== '') o *= +a; n = n.parentElement; } return o; };
  const svgText = [...w.querySelectorAll('svg text')].filter((e) => e.textContent.trim() && op(e) > 0.05).map((e) => {
    const m = e.getScreenCTM(); return { t: e.textContent.trim(), px: parseFloat(getComputedStyle(e).fontSize) * (m ? Math.hypot(m.a, m.b) : 1), box: R(e) }; });
  const pageInk = [...w.querySelectorAll('.lp-title, .lp-sub, .lp-src')].filter((e) => op(e) > 0.05 && e.textContent.trim()).map((e) => ({
    t: e.className, px: parseFloat(getComputedStyle(e).fontSize) * (e.getBoundingClientRect().width / (e.offsetWidth || 1)) }));
  const seg = lp.segs;
  return { chart: R(lp.chart), vb: lp.chart.getAttribute('viewBox'), svgText, pageInk,
    key: seg && seg.key ? R(seg.key) : null, keyOp: seg && seg.key ? op(seg.key) : 0,
    totals: lp.bars.map((b) => ({ box: R(b.val), op: op(b.val) })), bars: lp.bars.map((b) => R(b.bar)),
    labs: lp.bars.map((b) => ({ t: b.lab.textContent, lines: b.lab.__wrapLines ? b.lab.__wrapLines.length : 1, box: R(b.lab) })),
    figs: (lp.segFigs || []).map((f) => ({ t: f.text, inside: f.inside, box: R(f.el) })) }; }"""


def _read(tl: dict, uris: dict, times: list[float], tmp: Path) -> dict:
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    html = tmp / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp)
    out = {}
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            pg = br.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1).new_page()
            pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=180000)
            RB.prepare_page(pg, 1920, 1080)
            for x in times:
                pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                            "s.dispatchEvent(new Event('input', {bubbles:true})); }", x)
                out[x] = pg.evaluate(READ)
            br.close()
    finally:
        srv.shutdown()
    return out


HELD, BRACED = 12.0, G.FRAME_T["brace-funding"]


@pytest.fixture(scope="module")
def pages(tmp_path_factory) -> dict:
    """{(preset, braced): {t: read}} - the one-bar page at the three long-form presets, braced and not."""
    if not _chromium():
        pytest.skip("playwright chromium not installed")
    out = {}
    for preset in ("phone", "middle", "bravos"):
        for brace in (False, True):
            tl, uris = _one_bar(preset, brace)
            out[(preset, brace)] = _read(tl, uris, [HELD, BRACED], tmp_path_factory.mktemp(f"lf-{preset}-{int(brace)}"))
    return out


def _area(a, b) -> float:
    return max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))


# ---- R26-339 on `longform:phone` ------------------------------------------------------------------------------------
@pytest.mark.parametrize("brace", [False, True], ids=["page", "braced"])
def test_on_phone_the_key_clears_the_bars_total(pages, brace) -> None:
    """Acceptance (5): the T64 key and the bar's total never share a pixel (box overlap 0), nor the key and the bar."""
    for t, r in pages[("phone", brace)].items():
        assert r["key"] is not None and r["totals"][0]["op"] > 0.5, (t, r["key"], r["totals"])
        assert _area(r["key"], r["totals"][0]["box"]) == 0, (t, r["key"], r["totals"][0]["box"])
        assert _area(r["key"], r["bars"][0]) == 0, (t, r["key"], r["bars"][0])


@pytest.mark.parametrize("brace", [False, True], ids=["page", "braced"])
def test_on_phone_the_category_name_sits_on_one_line(pages, brace) -> None:
    for t, r in pages[("phone", brace)].items():
        assert [(lab["t"], lab["lines"]) for lab in r["labs"]] == [("Q1 2026", 1)], (t, r["labs"])


@pytest.mark.parametrize("brace", [False, True], ids=["page", "braced"])
def test_on_phone_every_word_on_the_page_holds_the_floor(pages, brace) -> None:
    """E99 s90's 59.08 stage px for every word the page draws - the chart's (ticks, the total, the parts' figures, the
    key, the name, the brace's words) and the page ink (title, sub, source)."""
    for t, r in pages[("phone", brace)].items():
        small = [(x["t"], round(x["px"], 2)) for x in r["svgText"] + r["pageInk"] if x["px"] < FLOOR - 0.01]
        assert not small, (t, small)


def test_on_phone_the_bars_chart_runs_across_the_stage_to_its_safe_edge(pages) -> None:
    r = pages[("phone", False)][HELD]
    x, _y, w, _h = r["chart"]
    assert abs(x + w - SAFE_RIGHT) <= 1.0, (r["chart"], SAFE_RIGHT)
    assert float(r["vb"].split()[2]) > 1000, r["vb"]
    bar = r["bars"][0]
    assert bar[2] == pytest.approx(196, abs=2), ("the bar keeps E99 s96's cap", bar)
    assert abs((bar[0] + bar[2] / 2) - (x + w / 2)) < 0.2 * w, "... centred in its plot, never stretched"


def test_the_estimated_boxes_follow_the_engine_at_phone(pages) -> None:
    """N3's contract: `ledger_page._longform_full_boxes` estimates the chart the engine draws - at phone its width is
    the stage's run to the safe edge (`longform_bars_vw`), within a pixel."""
    tl, _u = _one_bar("phone", False)
    est = LPG._longform_full_boxes(tl["scenes"][0]["world"]["page"], 1920, 1080)["chart"]
    got = pages[("phone", False)][HELD]["chart"]
    assert est["x"] + est["w"] == pytest.approx(got[0] + got[2], abs=1.0), (est, got)


# ---- every other preset is the page it was ----------------------------------------------------------------------------
@pytest.mark.parametrize("preset", ["middle", "bravos"])
def test_every_other_preset_keeps_the_legacy_viewbox(pages, preset) -> None:
    for brace in (False, True):
        for t, r in pages[(preset, brace)].items():
            assert r["vb"].split()[2] == "1000", (preset, brace, t, r["vb"])


def test_longform_bars_vw_widens_only_the_phone_preset() -> None:
    tl, _u = _one_bar("phone", False)
    page = tl["scenes"][0]["world"]["page"]
    scale = 0.795
    assert LPG.longform_bars_vw(page, scale) == pytest.approx((LPG.LAND_PHONE_SAFE_RIGHT - LPG.LAND_FULL["X"]) * 1920 / scale, abs=0.001)
    for preset in ("middle", "bravos"):
        tl2, _ = _one_bar(preset, False)
        assert LPG.longform_bars_vw(tl2["scenes"][0]["world"]["page"], scale) == 1000.0
    assert LPG.longform_bars_vw(dict(page, builder="dense-line"), scale) == 1000.0, "a line page has its own (longform_page_vw)"


def _line_state() -> dict:
    series = {"title": "A line state", "sub": "Synthetic, for the test", "src": "Synthetic", "yunit": "%",
              "series": [{"name": "CAPEX SHARE OF CASH", "label": "+613%", "color": "teal",
                          "pts": [[2020 + i / 40, 10 + 0.3 * i] for i in range(40)]}]}   # dense: the line builder's
    spec = LPG.build_spec(series, "line")
    assert spec["builder"] == "dense-line", spec["builder"]
    return spec


def test_a_line_state_keeps_its_end_tags_room_in_the_phone_bars_viewbox() -> None:
    """A `then=` LINE state is drawn in the bars page's viewBox (the suite's `bars-to-line-phone` caught the first cut
    running its tags off the stage): at `phone` the compiler writes the state's widest tag as the bars page's
    `tag_room`, and the widened viewBox keeps exactly that room at the right; at every other preset nothing is written."""
    for preset, wants in (("phone", True), ("middle", False), ("bravos", False)):
        tl, _u = _one_bar(preset, False)
        page = copy.deepcopy(tl["scenes"][0]["world"]["page"])
        assert LPG.apply_longform_states(page, [_line_state()]) is None
        assert ("tag_room" in page["axes"]) is wants, (preset, page["axes"].get("tag_room"))
        if not wants:
            assert LPG.longform_bars_vw(page, 0.795) == 1000.0
            continue
        s, room = 0.795, page["axes"]["tag_room"]
        vw = LPG.longform_bars_vw(page, s)
        tag_right = LPG.LAND_FULL["X"] * 1920 + (vw - LPG.LAND_PLOT["R"] * 1000 + LPG.LAND_TAG_GAP) * s + room
        assert tag_right == pytest.approx(SAFE_RIGHT, abs=0.01), (vw, room, tag_right)
        assert 1000 < vw < LPG.longform_bars_vw(dict(page, axes={k: v for k, v in page["axes"].items() if k != "tag_room"}), s)


# ---- round 2: R26-316 - a panels page at `longform:phone` is WARNED by name, never refused (D1; E99 s106) ------------
# The panels page's build at phone is its own slice; until then the compiler says, per row, the region the panels get
# against the height one panel needs and which of the five measured faults apply (P72 T12's frames: the subs, the y
# ticks, the x labels, the rule names, the bars), with their numbers. The page renders as it does.
FIT_WARN = "WARN fit:"


def _panels_page(series: dict, preset: str | None) -> dict:
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))
    finally:
        BST.ASPECT = saved
    if preset:
        LPG.apply_longform(page, preset)
    return page


def _fit(page: dict) -> list[str]:
    return [w for w in page.get("warnings") or [] if str(w).startswith(FIT_WARN)]


def test_the_companion_page_at_phone_is_warned_with_its_region_its_need_and_its_faults() -> None:
    """The pinned text: 210 px against ~327, the subs at 15.3 px, panel 0's plot under two ticks, its x labels
    overprinting, the bars 5.7 px - the numbers P72 T12's probe measured on the engine (logs/r26-316-phone-measure.txt)."""
    warns = _fit(_panels_page(G.companion_series(), "phone"))
    assert warns == [
        "WARN fit: a panels page at readability=longform:phone gets a 210 px region and a panel needs ~327 px (its sub at "
        "the floor, two y ticks, its x labels): the panel subs at 15.3 px (floor 59.08); panel 0's plot 81 px - under two "
        "y ticks' 154; panel 0's x labels overprint (906 px of labels on a 663 px plot); panel 1's bars at most 5.7 px "
        "tall - it renders as drawn (E99 s106: advice; R26-316's build is its own slice)"], warns


def test_a_roomy_panels_page_at_phone_names_only_the_faults_it_has() -> None:
    """The two-era page gets 475 px - more than a panel needs - and still sets its subs and its labels too small or too
    close: the WARN names those, and no bars (it has none) and no tick room (its plots hold two)."""
    (w,) = _fit(_panels_page(LPG.load_series(G.PANELS_V3), "phone"))
    assert "gets a 475 px region" in w and "the panel subs at 34.5 px" in w and "the rule names overprint on panels 0, 1" in w
    assert "bars" not in w and "under two y ticks" not in w, w


@pytest.mark.parametrize("preset", [None, "middle", "bravos"])
def test_every_other_preset_prints_nothing(preset) -> None:
    for series in (G.companion_series(), LPG.load_series(G.PANELS_V3), G._panels_mixed()):
        assert _fit(_panels_page(series, preset)) == [], preset


def test_the_warn_is_advice_the_page_builds_as_it_did() -> None:
    """Nothing else moves: the phone page is the page it was but for its `warnings` (s106: a finding, never a refusal),
    and fitting it again keeps one WARN, not two."""
    page = _panels_page(G.companion_series(), "phone")
    bare = copy.deepcopy(page)
    bare.pop("warnings")
    assert LPG.longform_panels_fit_warning(bare) == _fit(page)[0]
    LPG.apply_longform(page, "phone")
    assert len(_fit(page)) == 1
    assert LPG.page_ink_key(page) == LPG.page_ink_key(bare), "the boxes the page is placed by are unchanged"


def test_the_compiler_prints_the_fit_warning_with_the_rows_id() -> None:
    src = (REPO / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    lines = [ln.strip() for ln in src.splitlines() if "startswith(LPG.FIT_WARN)" in ln]
    assert len(lines) == 1, lines
    i = next(k for k, ln in enumerate(src.splitlines()) if "startswith(LPG.FIT_WARN)" in ln)
    assert 'print(f"  [WARN] P72 T12: shot row {i + 1} ({a}-{b}s): {_w}")' in src.splitlines()[i + 1]
    assert LPG.FIT_WARN == FIT_WARN


def test_a_row_at_longform_phone_carries_the_warning_to_the_build(tmp_path) -> None:
    """The row path (`world_for_plate` with `;readability=longform:phone`) - the world main's loop prints from."""
    import json
    import build_scene_timeline_f as BST
    (tmp_path / "evidence/objects").mkdir(parents=True)
    (tmp_path / "evidence/objects/fx-panels.series.json").write_text(json.dumps(G.companion_series()), encoding="utf-8")
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        phone = BST.world_for_plate("ledger:fx-panels:line;readability=longform:phone", (0, 0, 0), tmp_path)
        middle = BST.world_for_plate("ledger:fx-panels:line;readability=longform", (0, 0, 0), tmp_path)
    finally:
        BST.ASPECT = saved
    assert len(_fit(phone["page"])) == 1 and "gets a 210 px region" in _fit(phone["page"])[0]
    assert _fit(middle["page"]) == []
