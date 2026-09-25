"""P72 T12 (R26-315, R26-299): THE PANELS PAGE BUILDS IN VIEW, AND NO PANEL'S WORD IS EVER CUT.

R26-315 - a hidden panel built while it was invisible: `lpPanelStart` started its build on the focus word, but the focus
move keeps a panel that comes forward at opacity 0 until the move is half run (`LP_PANELS.INK_LEAD`), so the viewer saw
the bars FADE IN ~95 % built (P70 T4's measure) instead of growing - Bravos DOM 06:02-06:04 grows them in view over
~1.5 s. Now a revealed panel stands its frame and its axes while it fades in (its bars at zero, its lines undrawn) and
BUILDS once the reveal has landed (`at + dur` - the instant the motion gate already credits as the arrival,
`gate_motion_density._panel_reveal_landings`). A panel that builds on its own turn with the page is unchanged.

R26-299 - "a panel's y labels read '%' without digits while it builds": the text was whole; the panel IN FRONT (the one
shrinking into its slot, its opaque ground under everything it draws) covered the digits and left the '%'. A panel's
word is now drawn whole or not at all: one that a panel in front covers, even in part, is not drawn.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
for p in (REPO / "content/video_engine/scripts", REPO / "content/video_engine/tests/golden"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import build_golden_sources as G  # noqa: E402

ENGINE = REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
FPS = 24
BUILD_S = 3.0          # LP.BUILD: a panel's build seconds (no golden here declares build_s)
BARS_GROW = 0.55       # lpPaintChart's bars law: a bar grows over this share of its build
OCCLUDE_OP = 0.5       # LP_PANELS.OCCLUDE_OP: a panel in front covers the words behind it from this opacity


def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


READ = """() => { const s = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp && x.__lp.panels);
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  const op = (e) => { let n = e, o = 1; while (n && n !== document.body) { const cs = getComputedStyle(n);
    if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +(cs.opacity || 1);
    const a = n.getAttribute && n.getAttribute('opacity'); if (a != null && a !== '') o *= +a; n = n.parentElement; } return o; };
  return w.__lp.panels.map((S) => ({ kind: S.kind, chart: R(S.chart), op: op(S.box), svg: +getComputedStyle(S.chart).opacity,
    z: +(S.box.style.zIndex || 0),
    lines: (S.paths || []).filter((p) => !p.muted).map((p) => 1 - (+p.p.getAttribute('stroke-dashoffset') || 0) / (p.len || 1)),
    bars: (S.bars || []).map((b) => R(b.bar)[3]),
    ticks: (S.marks || []).filter((m) => (m.role === 'ylabel' || m.role === 'xtick') && m.el).map((m) => ({ t: m.el.textContent, box: R(m.el), op: op(m.el) })),
    words: [...S.chart.querySelectorAll('text')].filter((e) => e.textContent.trim()).map((e) => ({ t: e.textContent.trim().slice(0, 40), box: R(e), op: op(e) })) })); }"""
SEEK = "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }"


def _play(surface: str, times: list[float], tmp: Path, cold: float | None = None) -> dict:
    """The surface played forward through `times` (seek + DOM read, no screenshot): {t: every panel's read}; with `cold`,
    a fresh page seeks straight to that instant as well ({'cold': read})."""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(surface)
    html = tmp / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp)
    w, h = RB.STAGE[aspect]
    out: dict = {}
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            for name, seq in (("play", times), ("cold", [cold] if cold is not None else [])):
                if not seq:
                    continue
                pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=180000)
                RB.prepare_page(pg, w, h)
                for x in seq:
                    pg.evaluate(SEEK, x)
                    out[("cold", x) if name == "cold" else x] = pg.evaluate(READ)
                pg.close()
            br.close()
    finally:
        srv.shutdown()
    return out


def _frames(a: float, b: float) -> list[float]:
    return [round(a + k / FPS, 4) for k in range(int(round((b - a) * FPS)) + 1)]


REVEAL, DUR = G.COMPANION_REVEAL_AT, G.COMPANION_DUR
LAND = round(REVEAL + DUR, 4)
PLAYED = _frames(REVEAL - 0.5, LAND + BUILD_S)
COLD = PLAYED[int(round((LAND + 0.5 - (REVEAL - 0.5)) * FPS))]   # a played frame ~0.5 s into the build, also seeked cold


@pytest.fixture(scope="module")
def companion(tmp_path_factory) -> dict:
    if not _chromium():
        pytest.skip("playwright chromium not installed")
    return _play("companion-railway-yardstick", PLAYED + [14.5], tmp_path_factory.mktemp("companion-reveal"), cold=COLD)


@pytest.fixture(scope="module")
def resize(tmp_path_factory) -> dict:
    if not _chromium():
        pytest.skip("playwright chromium not installed")
    ts = sorted(set(_frames(G.PANELS_RESIZE_AT - 0.2, G.PANELS_RESIZE_AT + G.PANELS_RESIZE_DUR + BUILD_S + 0.2)
                    + _frames(G.PANELS_LEAVE_AT - 0.2, G.PANELS_LEAVE_AT + G.PANELS_RESIZE_DUR + 0.3)
                    + [round(0.5 * k, 2) for k in range(1, 40)]))
    return _play("panels-resize", ts, tmp_path_factory.mktemp("panels-resize"))


def _played(reads: dict) -> list[tuple[float, list]]:
    return sorted((t, r) for t, r in reads.items() if not isinstance(t, tuple))


# ---- R26-315: a hidden panel builds in view ---------------------------------------------------------------------------
def test_a_revealed_panels_bars_stand_at_zero_on_its_first_visible_frame_and_grow_in_view(companion) -> None:
    """Acceptance (1), on the companion golden (the bars panel hidden, shown beside the line on its word): on every
    frame it is seen before its reveal lands its bars stand at 0; after the landing they GROW, frame by frame, to their
    true heights - seen whole (opacity 1) all the while."""
    seen = [(t, r[1]) for t, r in _played(companion) if r[1]["op"] > 0.001]
    assert seen, "the bars panel is shown"
    first_t, first = seen[0]
    assert REVEAL < first_t < LAND, (first_t, "it is first seen during its reveal")
    assert max(first["bars"]) <= 0.5, ("its bars stand at 0 on its first visible frame", first_t, first["bars"])
    fading = [(t, p) for t, p in seen if t < LAND]
    assert all(max(p["bars"]) <= 0.5 for _t, p in fading), [(t, p["bars"]) for t, p in fading if max(p["bars"]) > 0.5]
    full = companion[14.5][1]["bars"]
    assert min(full) > 50, full
    grow = [(t, p) for t, p in seen if LAND <= t <= LAND + BARS_GROW * BUILD_S + 0.05]
    assert all(p["op"] == pytest.approx(1.0) for _t, p in grow), "the bars grow with the panel fully shown"
    tall = [p["bars"][0] for _t, p in grow]
    assert all(b >= a - 0.01 for a, b in zip(tall, tall[1:])), ("a bar only grows", tall)
    mid = [h for (t, p), h in zip(grow, tall) if t >= LAND + 1.0 / FPS][0]
    assert 0 < mid < full[0], ("the frame after the landing shows the bar building", mid, full[0])
    assert tall[-1] == pytest.approx(full[0], abs=0.6), "the bars have grown to their heights ~1.65 s after the landing"


def test_a_revealed_panel_stands_its_frame_and_axes_while_it_fades_in(companion) -> None:
    """The panel is never an empty box fading in: from its word its chart (the plot's panel, the ticks) is drawn, only
    its data wait - so the fade shows a chart, and the build that follows is the bars growing on it."""
    fading = [r for t, r in _played(companion) if REVEAL <= t < LAND and r[1]["op"] > 0.001]
    assert fading
    for r in fading:
        p, front = r[1], r[0]
        assert p["svg"] == 1.0, "the panel's chart is drawn while it fades in"
        for tk in p["ticks"]:   # a tick is drawn, or the shrinking line in front still covers it (R26-299, below)
            assert tk["op"] > 0 or _meets(tk["box"], front["chart"]), (tk, front["chart"])
    assert any(any(tk["op"] > 0 for tk in r[1]["ticks"]) for r in fading), "its axes stand before its bars build"


def test_the_reveal_is_a_pure_function_of_t(companion) -> None:
    assert 0 < companion[COLD][1]["bars"][0] < companion[14.5][1]["bars"][0], "read mid-build"
    assert companion[("cold", COLD)][1]["bars"] == pytest.approx(companion[COLD][1]["bars"], abs=0.05)


def test_a_revealed_line_panel_draws_its_line_only_after_its_reveal_has_landed(resize) -> None:
    """The panels-resize golden: panel 2 hidden, shown beside the shrinking line on its word (9.0, 1.2 s) - its line is
    undrawn until 10.2, then draws over its build."""
    land = G.PANELS_RESIZE_AT + G.PANELS_RESIZE_DUR
    for t, r in _played(resize):
        p = r[1]
        if G.PANELS_RESIZE_AT <= t < land:
            assert max(p["lines"]) <= 0.004, (t, p["lines"])
    after = [r[1]["lines"][0] for t, r in _played(resize) if land < t <= land + BUILD_S]
    assert 0 < after[0] < 0.5 and after[-1] > 0.99, (after[0], after[-1])


def test_the_line_that_stood_alone_is_unchanged_by_the_reveal(resize) -> None:
    """Panel 1 built on its own turn with the page (4.4 - 7.4): drawn whole through the reveal."""
    for t, r in _played(resize):
        if 7.5 <= t <= G.PANELS_LEAVE_AT:
            assert min(r[0]["lines"]) > 0.99, (t, r[0]["lines"])


def test_the_engine_says_why_the_build_waits() -> None:
    """The reveal clock's two halves in the engine: lpPanelStart still names the word that SHOWS a panel (the motion
    gate's pin, test_gate_motion_density), and the build waits for that reveal's own landing."""
    src = ENGINE.read_text(encoding="utf-8")
    assert "const lpPanelBuildAt = " in src and "lpPanelBuildAt(st, scene, i, t0)" in src


# ---- R26-299: a panel's word is whole or not drawn at all -----------------------------------------------------------
def _meets(a, b, pad: float = 0.0) -> bool:
    return a[0] < b[0] + b[2] - pad and b[0] < a[0] + a[2] - pad and a[1] < b[1] + b[3] - pad and b[1] < a[1] + a[3] - pad


def _inside(a, b) -> bool:
    return a[0] >= b[0] and a[1] >= b[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3]


def _cut_words(reads: list) -> list[tuple]:
    """(panel, word) pairs drawn while a panel IN FRONT of theirs (a higher z; the later one on a tie) with at least
    OCCLUDE_OP of its ink covers PART of the word's box - a word the viewer would read cut (one it covers whole is not
    seen at all)."""
    cut = []
    for i, p in enumerate(reads):
        if p["op"] <= 0.001:
            continue
        for j, q in enumerate(reads):
            if j == i or q["op"] < OCCLUDE_OP or not (q["z"] > p["z"] or (q["z"] == p["z"] and j > i)):
                continue
            for wd in p["words"]:
                if wd["op"] > 0.001 and _meets(wd["box"], q["chart"], 0.5) and not _inside(wd["box"], q["chart"]):
                    cut.append((i, wd["t"]))
    return cut


def test_no_percent_without_its_digits_on_any_frame_of_the_resize_golden(resize) -> None:
    """Acceptance (3): every frame of the reveal and the leave (24 fps) and the timeline every 0.5 s - no tick label a
    panel in front covers in part is drawn, so '%' never stands without its digits."""
    bad = []
    for t, r in _played(resize):
        for i, word in _cut_words(r):
            if any(ch.isdigit() for ch in word) or word.endswith("%"):
                bad.append((t, i, word))
    assert not bad, bad[:12]


def test_no_word_of_a_panel_is_cut_by_the_panel_in_front(resize) -> None:
    """... and the rule is every word a panel writes - its sub ('AI era - 2021-today' read 'oday' at 9.7), its tags, its
    rules' names."""
    bad = [(t, i, wd) for t, r in _played(resize) for i, wd in _cut_words(r)]
    assert not bad, bad[:12]


def test_a_word_clear_of_the_panel_in_front_is_drawn(resize) -> None:
    """The rule hides only what is covered: once the shrinking line has left its column, panel 2's ticks are drawn."""
    land = G.PANELS_RESIZE_AT + G.PANELS_RESIZE_DUR
    r = resize[min(t for t in resize if not isinstance(t, tuple) and t >= land + 0.5)]
    assert all(tk["op"] > 0.99 for tk in r[1]["ticks"]), r[1]["ticks"]


def test_a_panels_page_draining_down_its_vortex_paints_without_an_error(tmp_path) -> None:
    """The H door's row 24 drains a panels page (`spiral` exit). The reveal clock's first cut named its build `c` in the
    painter that reads the board centre `c` for the drain - "Cannot access 'c' before initialization" on every drained
    frame (the goldens never drain). The resize golden, given a spiral exit at 20 s, drains clean through its last frame."""
    if not _chromium():
        pytest.skip("playwright chromium not installed")
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface("panels-resize")
    sc = tl["scenes"][0]
    sc["span"] = [0.0, 20.0]
    sc["world"]["page"]["exit"] = "spiral"
    html = tmp_path / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp_path)
    errs, xf = [], []
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            pg = br.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1).new_page()
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=180000)
            RB.prepare_page(pg, 1920, 1080)
            for x in (18.6, 19.2, 19.7, 19.95):
                pg.evaluate(SEEK, x)
                xf.append(pg.evaluate("() => [...document.querySelectorAll('.lp-pbox')].map((b) => b.style.transform)"))
            br.close()
    finally:
        srv.shutdown()
    assert not errs, errs[:3]
    assert any("rotate" in t or "matrix" in t or t.count("translate") > 1 for row in xf for t in row), ("the panels drain", xf)


# ---- round 2: a figure authored on a revealed panel lands with its bars (H row 21's "3x") ------------------------------
# Row 21 writes "3x" on the wafer bars panel on the reveal's own word (556.21, 1.2 s); with the build waiting for the
# reveal's landing the figure stood over an empty plot for ~0.3 s and the bar grew up to it. A figure's clock on a panel
# now starts no earlier than the panel's build (lpPanelBuildAt): its write runs as the bars grow.
FIG_DUR = 1.2


def _companion_with_figure() -> tuple[dict, dict]:
    """The companion golden's page with row 21's shape of figure: on the bars panel, on the reveal's word."""
    import build_scene_timeline_f as BST
    import ledger_page as LPG
    series = G.companion_series()
    species = [dict(e) for e in G.COMPANION_FOCUS] + [
        {"kind": "figure", "at": REVEAL, "dur": FIG_DUR, "panel": 1, "text": "50%", "target": {"kind": "datum", "index": 0}}]
    plate = "ledger:golden-panels:line"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))
        world = {"kind": "ledger", "page": page, "idle": "live", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
        BST.derive_rescale_states(world, species, plate, REPO)
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    return G._timeline("figure on a revealed panel", scenes, {}, "16:9"), G._base_uris()


FIG_READ = """() => { const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp && x.__lp.panels);
  const S = w.__lp.panels[1], F = (S.perform && S.perform.figures) || [];
  return { glyphs: F.map((f) => f.lg.map((g) => +g.getAttribute('opacity'))), shown: F.map((f) => +f.g.getAttribute('opacity')),
           bar: Math.max(...(S.bars || []).map((b) => b.bar.getBoundingClientRect().height)) }; }"""


@pytest.fixture(scope="module")
def figure_play(tmp_path_factory) -> dict:
    if not _chromium():
        pytest.skip("playwright chromium not installed")
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris = _companion_with_figure()
    tmp = tmp_path_factory.mktemp("figure-reveal")
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
            for x in _frames(REVEAL, LAND + FIG_DUR + 0.5):
                pg.evaluate(SEEK, x)
                out[x] = pg.evaluate(FIG_READ)
            br.close()
    finally:
        srv.shutdown()
    return out


def test_a_figure_on_a_revealed_panel_writes_nothing_before_its_panel_builds(figure_play) -> None:
    early = {t: r for t, r in figure_play.items() if t < LAND}
    assert early
    inked = [(t, max(r["glyphs"][0])) for t, r in early.items() if max(r["glyphs"][0]) > 0.001]
    assert not inked, ("no glyph of the figure is inked while its panel's bars stand at zero", inked[:6])


def test_the_figure_writes_as_its_bars_grow_and_lands_by_its_own_duration_after_the_build(figure_play) -> None:
    rows = sorted(figure_play.items())
    during = [(t, r) for t, r in rows if LAND < t < LAND + FIG_DUR]
    assert any(0 < max(r["glyphs"][0]) for _t, r in during), "the figure writes while the bars grow"
    first = next(t for t, r in rows if max(r["glyphs"][0]) > 0.001)
    assert first > LAND and first - LAND <= 2.0 / FPS + 1e-6, (first, LAND)
    bar_then = next(r["bar"] for t, r in rows if t == first)
    assert 0 < bar_then < 0.5 * rows[-1][1]["bar"], ("the bar is growing as the figure starts", bar_then)
    done = [r for t, r in rows if t >= LAND + FIG_DUR + 0.3]
    assert done and min(done[-1]["glyphs"][0]) > 0.99, done[-1]


def test_a_figure_on_a_page_with_no_reveal_keeps_its_own_clock() -> None:
    """The floor is a revealed panel's alone: the engine reads it off the panel (`panelBuildAt`), which only lpPaintPanels
    writes, and only for a panel a focus state shows - every other page's figure runs on its `at` exactly as before."""
    src = ENGINE.read_text(encoding="utf-8")
    assert "S.panelBuildAt = pb.build > pb.shown ? pb.build : null;" in src
    assert src.count("panelBuildAt") == 4, src.count("panelBuildAt")
