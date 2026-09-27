"""P71 T15 - a dock over a chart chooses by INTENT: `under: "hover"` or `under: "blur"` (E99 s124 AS AMENDED).

The operator, 2026-09-24: "it depends on the intent of the dock; often times when we dock on a chart we don't want to
obscure what's underneath. we could elevate/grow and hover the dock, and maybe use that hyperframes reference i
provided before, without blurring beneath the dock. but we should be able to blur if we want to ..." - and, amended the
same day: "the ultimate outcome is it needs to be a choice depending on the goal of what we want to have happen".

So there is NO default flip. `under` is the author's per-dock word:
- `hover` keeps the chart READ: after the arrival settles the card lifts, its shadow grows with the lift (the
  HyperFrames drift-hold card's own drop shadow), it grows one step and holds on the drift-hold (`idle: hold`, P70 T13);
  the chart under it is untouched - no veil, no wash.
- `blur` FOCUSES a temporary evidence dock: a veil between the page and the docks (`#dockveil`) blurs the chart on the
  dock's own clock and clears on its leave.
A dock that names `under` keeps its authored read over a ledger page's plot (s124 (3) lifts E63's bar; s106: where it
sits is the author's), and M25 / M27 report it as a WARN with its numbers. A dock over a ledger page that names neither
compiles exactly as today, keeps today's FAIL, and the compiler asks for the choice with a WARN (s106).
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
from authoring import table as T  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
COMPILER = ROOT / "content/video_engine/scripts/build_scene_timeline_f.py"
GATE = ROOT / "content/video_engine/scripts/gate_motion_density.py"
CHART_EV = {"species": "chart", "title": "t", "source": "s", "badges": []}
DECK_EV = {"species": "deck", "title": "t", "source": "s", "badges": []}
TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
PANEL = "dock-c-blue-ties-panel"
ASPECT = "9:16"


# ------------------------------------------------------------------ the option
def test_under_is_a_dock_option_and_names_one_of_two_intents():
    assert "under" in B.DOCK_OPTS
    assert B.DOCK_UNDER == ("hover", "blur")
    for v in B.DOCK_UNDER:
        assert B.dock_opts({"under": v}) == {"under": v}
    assert B.dock_opts({"under": "hover", "idle": "hold:standard"}) == {"under": "hover", "idle": "hold:standard"}


@pytest.mark.parametrize("bad", ["", "HOVER", "dim", "wash", "sharp", "blur:18", 1, True, None, {"blur": 1}])
def test_an_under_that_is_neither_hover_nor_blur_is_refused_by_name(bad):
    with pytest.raises(ValueError) as e:
        B.dock_opts({"under": bad})
    msg = str(e.value)
    assert "dock: under" in msg and "hover|blur" in msg, msg


@pytest.mark.parametrize("other, word", [
    ({"prop": True}, "prop"),
    ({"arrive": "stamp"}, "stamp"),
    ({"cutout": True}, "cutout"),
    ({"press": {"source": "s", "phrase": "p"}}, "press"),
    ({"embed": "poster"}, "embed"),
])
def test_under_is_a_held_cards_choice_and_is_refused_by_name_elsewhere(other, word):
    with pytest.raises(ValueError) as e:
        B.dock_opts({"under": "blur", **other})
    msg = str(e.value)
    assert f"under=blur and {word}" in msg, msg


def test_a_hover_holds_on_the_drift_hold_graded_by_the_payload():
    assert B.dock_idle({"under": "hover"}, CHART_EV) == "hold:whisper", "a card carrying a chart hovers at a whisper"
    assert B.dock_idle({"under": "hover"}, DECK_EV) == "hold:standard"
    assert B.dock_idle({"under": "hover", "idle": "hold:standard"}, CHART_EV) == "hold:standard", "an authored grade is the author's"
    assert B.dock_idle({"under": "blur"}, CHART_EV) is None, "blur stands the card on the blurred chart - no hold is implied"
    assert B.dock_idle({"under": "blur", "idle": "hold"}, CHART_EV) == "hold:whisper"
    assert B.dock_idle({}, CHART_EV) is None


def test_a_dock_that_names_no_under_is_the_entry_it_always_was():
    args = ("ev-card", 0, 2.0, 12.0, 1)
    plain = B.dock_entry(*args)
    assert "under" not in plain
    assert B.dock_entry(*args, under=None) == plain
    for v in B.DOCK_UNDER:
        chosen = B.dock_entry(*args, under=v)
        assert chosen["under"] == v
        assert {k: x for k, x in chosen.items() if k != "under"} == plain, "the choice adds one key and moves nothing else"


def test_the_main_loop_hands_the_choice_to_the_read_and_to_the_entry():
    src = COMPILER.read_text(encoding="utf-8")
    assert re.search(r"e63 = read_over_build\([^;]*?under=dopt\.get\(\"under\"\)\)", src, re.S), \
        "the read decision knows the author chose to sit over the chart"
    assert re.search(r"docks\.append\(dock_entry\([^;]*?under=dopt\.get\(\"under\"\)", src, re.S), \
        "the entry carries the choice to the painter and the gate"
    assert re.search(r"docks\.append\(dock_entry\([^;]*?idle=dock_idle\(dopt, evidence\[aid\]\)", src, re.S), \
        "P70 T13's pin: the idle is still resolved against the evidence (the hover's hold rides it)"


# ------------------------------------------------------------------ E63 lifted for a dock that chose (s124 (3))
@pytest.fixture(scope="module")
def s02() -> dict:
    """The Tokyo row E63 was ruled on (test_dock_over_build's fixture): its panel card READS over the plot."""
    rows = T.load_rows(TOKYO / "SHOT-TABLE-SHORT.py")
    row = next(r for r in rows if any(str(d[0]) == PANEL for d in (r[4] or [])))
    world = B.world_for_plate(row[2], row[3], TOKYO, None)
    dock = next(d for d in row[4] if str(d[0]) == PANEL)
    plot = B.LPG.page_boxes(world["page"], ASPECT)["plot"]
    # the author's read: the plot's own middle half - wholly over the plot and clear of every word the page prints, so
    # the ONLY rule it meets is E63's (the player's solo box on this page also covers the y-axis labels: P71 T5's words)
    read = {"x": plot["x"] + plot["w"] // 4, "y": plot["y"] + plot["h"] // 4, "w": plot["w"] // 2, "h": plot["h"] // 2}
    assert not [n for n, r in B.page_text_boxes(world["page"], ASPECT) if B._overlap_area(read, r) > 0]
    assert B._overlap_share(read, plot) > B.READ_OVER_PLOT_SHARE
    return {"page": world["page"], "place": B.dock_place(world, ASPECT), "enter": float(dock[2]), "read": read,
            "windows": B.page_build_windows(world, row[6], row[0])}


def _read(s02: dict, **kw) -> dict | None:
    return B.read_over_build(s02["place"], s02["read"], s02["page"], ASPECT,
                             s02["enter"], s02["enter"] + B.DOCK_READ_S, s02["windows"], **kw)


def test_a_dock_that_names_no_under_is_moved_off_the_plot_as_today(s02):
    today = _read(s02)
    assert today and (today.get("read_place") or today.get("read_deferred")), today
    assert _read(s02, under=None) == today


@pytest.mark.parametrize("under", ["hover", "blur"])
def test_a_dock_that_names_under_keeps_its_authored_read_over_the_plot(s02, under):
    assert _read(s02, under=under) is None, "s124 (3): the author chose to sit over the chart - the read is not moved"


def test_the_choice_lifts_the_plot_only_never_the_stamp_reserve_or_the_page_words(s02):
    """P71 T5's approved deviation (legibility first) holds for a dock that chose: a read over a stamp's reserved box
    still moves by the same law - `under` lifts E63's PLOT bar and nothing else."""
    stamp = dict(s02["read"])
    moved = _read(s02, under="hover", stamps=[stamp])
    assert moved and (moved.get("read_place") or moved.get("read_deferred")), moved
    if moved.get("read_moved"):
        assert "stamp" in moved["read_moved"]["why"], moved


def test_a_chosen_read_over_the_pages_words_still_moves_off_them(s02):
    """Review round 2 (2): the page-words half of P71 T5's rule under `under=` - a read that covers one of the words the
    page prints (E28: the page reads at a glance) moves or defers, and the reason names the page's words, never E63."""
    words = B.page_text_boxes(s02["page"], ASPECT)
    assert words, "the Tokyo page prints words"
    _name, r = words[0]
    read = {"x": r["x"], "y": r["y"], "w": max(r["w"], 240), "h": max(r["h"], 160)}
    assert B._overlap_area(read, r) > 0
    moved = B.read_over_build(s02["place"], read, s02["page"], ASPECT, s02["enter"], s02["enter"] + B.DOCK_READ_S,
                              s02["windows"], under="hover")
    assert moved and (moved.get("read_place") or moved.get("read_deferred")), moved
    if moved.get("read_moved"):
        assert "the page's words" in moved["read_moved"]["why"] and "E63" not in moved["read_moved"]["why"], moved


# ------------------------------------------------------------------ the choice is asked for, never assumed
def test_a_card_over_a_ledger_plot_that_names_neither_is_asked_to_choose(s02):
    world = {"kind": B.SPECIES_LEDGER, "page": s02["page"]}
    over = [s02["read"]]   # the plot's middle half
    note = B.under_choice_note(world, {}, "shot row 4 (10.0-20.0s) dock ev-a", over, ASPECT)
    assert note and "shot row 4 (10.0-20.0s) dock ev-a" in note
    for word in ('under: "hover"', 'under: "blur"', "keep the chart read", "temporary evidence dock", "s124", "s106",
                 "over the chart's plot"):
        assert word in note, (word, note)
    for chosen in B.DOCK_UNDER:
        assert B.under_choice_note(world, {"under": chosen}, "x", over, ASPECT) is None
    for other in ({"prop": True}, {"arrive": "stamp"}, {"cutout": True}, {"press": {"source": "s"}}, {"embed": "poster"}):
        assert B.under_choice_note(world, other, "x", over, ASPECT) is None, other
    assert B.under_choice_note({"kind": "plate", "asset_id": "plate-x"}, {}, "x", over, ASPECT) is None, \
        "a dock over a picture plate is not over a chart"
    assert B.under_choice_note(None, {}, "x", over, ASPECT) is None


def test_a_card_parked_clear_of_the_plot_is_not_asked(s02):
    """Review round 2 (7): the question is for a card that actually sits over the chart - a card the placer parked clear
    of the plot (a band, the corner) is asked nothing."""
    world = {"kind": B.SPECIES_LEDGER, "page": s02["page"]}
    plot = B.LPG.page_boxes(s02["page"], ASPECT)["plot"]
    clear = {"x": plot["x"], "y": max(0, plot["y"] - 120), "w": 200, "h": 100}
    assert B._overlap_area(clear, plot) == 0
    assert B.under_choice_note(world, {}, "x", [clear, None], ASPECT) is None
    assert B.under_choice_note(world, {}, "x", [], ASPECT) is None
    assert B.under_choice_note(world, {}, "x", [clear, s02["read"]], ASPECT), "any drawn box over the plot asks"


def test_the_main_loop_asks_with_the_boxes_it_draws():
    src = COMPILER.read_text(encoding="utf-8")
    assert src.count("under_choice_note(") == 2, "defined once, called once - in the dock loop"
    assert re.search(r"_uc = under_choice_note\(world, dopt, f\"shot row \{i \+ 1\} \(\{a\}-\{b\}s\) dock \{aid\}\",\n"
                     r"\s+\[eplace, _drawn_read\], ASPECT, _park\)\n"   # P72 T53 (f): the park standing at the enter
                     r"\s+if _uc:\n\s+print\(f\"  \[WARN\] P71 T15: \{_uc\}\"\)", src)
    assert src.index("_uc = under_choice_note(") > src.index("_drawn_read = None if (stamp_fit or"), \
        "asked once the read it draws is known"


# ------------------------------------------------------------------ the gate: a WARN with its numbers (s106)
def _inst(card: str, state: str, hit: str = "page.data", share: int = 30, area: int = 40000) -> dict:
    return {"t": 5.0, "docks": [{"id": card, "state": state, "rest": True}],
            "overlaps": [{"a": card, "b": hit, "share_of_smaller": share, "area_px": area}]}


def _scenes(under: str | None) -> list[dict]:
    d = {"slide": "ev-a", "slot": 0, "enter": 2.0, "exit": 12.0}
    return [{"scene_id": "s01", "span": [0.0, 20.0], "docks": [dict(d, under=under) if under else d]}]


@pytest.mark.parametrize("under", ["hover", "blur"])
def test_m27_reports_a_dock_that_chose_to_read_over_the_ink_as_a_warn_with_its_numbers(under):
    doc = {"aspect": "16:9", "instants": [_inst("ev-a", "reading")]}
    fails, warns, _n = G._over_build_faults(doc, _scenes(under))
    assert fails == [], fails
    assert len(warns) == 1 and f"under: {under}" in warns[0] and "s124" in warns[0] and "40,000 px" in warns[0] \
        and "30 %" in warns[0], warns
    gate = G._over_build_gate(doc, _scenes(under))
    assert gate.level == "WARN" and "by intent" in gate.message, gate.message
    ink = {"aspect": "16:9", "instants": [_inst("ev-a", "reading", "chart.lab", 40, 900)]}
    assert G._over_build_faults(ink, _scenes(under))[0] == [], "a label under a chosen dock is the same WARN"


def test_m27_keeps_todays_fail_for_a_dock_that_names_no_under():
    doc = {"aspect": "16:9", "instants": [_inst("ev-a", "reading")]}
    fails, warns, _n = G._over_build_faults(doc, _scenes(None))
    assert len(fails) == 1 and "reads on the chart's data" in fails[0] and warns == [], (fails, warns)
    assert G._over_build_gate(doc, _scenes(None)).level == "FAIL"


@pytest.mark.parametrize("under", ["hover", "blur"])
def test_m25_reports_a_settled_dock_that_chose_the_chart_as_a_warn_with_its_numbers(under):
    doc = {"aspect": "16:9", "instants": [_inst("ev-a", "parked")]}
    fails, warns = G._layout_faults(doc, _scenes(under))
    assert fails == [], fails
    assert len(warns) == 1 and f"under: {under}" in warns[0] and "40,000 px" in warns[0] and "s124" in warns[0], warns
    gate = G._layout_gate(doc, _scenes(under))
    assert gate.level == "WARN" and "by intent" in gate.message, gate.message


@pytest.mark.parametrize("hit", ["page.source", "page.title", "page.sub", "page.note", "page.key", "pill"])
@pytest.mark.parametrize("under", ["hover", "blur"])
def test_a_chosen_dock_over_the_pages_own_words_still_fails_m25_and_m27(under, hit):
    """Review round 2 (1): s124 (3) lifts the bar for the PLOT only - E45 s1 (never over the title, the source line)
    and E52 (the page CITES) stand for a dock that chose, so its read or its rest on the page's words is a FAIL."""
    for state, faults in (("parked", lambda doc: G._layout_faults(doc, _scenes(under))[0]),
                          ("reading", lambda doc: G._over_build_faults(doc, _scenes(under))[0])):
        doc = {"aspect": "16:9", "instants": [_inst("ev-a", state, hit, 60, 5000)]}
        assert faults(doc), (state, hit, under)
    assert G._layout_gate({"aspect": "16:9", "instants": [_inst("ev-a", "parked", hit, 60, 5000)]}, _scenes(under)).level == "FAIL"
    assert G._over_build_gate({"aspect": "16:9", "instants": [_inst("ev-a", "reading", hit, 60, 5000)]}, _scenes(under)).level == "FAIL"


@pytest.mark.parametrize("under", ["hover", "blur"])
def test_a_chosen_dock_over_a_chart_label_is_a_warn_in_m25_too(under):
    doc = {"aspect": "16:9", "instants": [_inst("ev-a", "parked", "chart.lab", 40, 900)]}
    fails, warns = G._layout_faults(doc, _scenes(under))
    assert fails == [] and warns and "an axis label" in warns[0], (fails, warns)


def test_the_gate_trusts_only_the_two_intents():
    """Review round 2 (6e): a hand-edited `under` that is not hover or blur claims nothing - today's FAIL."""
    doc = {"aspect": "16:9", "instants": [_inst("ev-a", "reading")]}
    for bogus in ("sharp", "HOVER", True, 1):
        assert G._over_build_faults(doc, _scenes(bogus))[0], bogus
        assert G._layout_faults({"aspect": "16:9", "instants": [_inst("ev-a", "parked")]}, _scenes(bogus))[0], bogus


def test_a_chosen_docks_leave_across_the_scene_boundary_is_still_chosen():
    """Review round 2 (6d): the dock's own window decides, not the scene whose span holds t - a chosen dock whose retract
    runs into the next scene is still the author's choice there."""
    scenes = [{"scene_id": "s01", "span": [0.0, 12.0], "docks": [{"slide": "ev-a", "slot": 0, "enter": 2.0, "exit": 11.9, "under": "hover"}]},
              {"scene_id": "s02", "span": [12.0, 20.0], "docks": []}]
    doc = {"aspect": "16:9", "instants": [dict(_inst("ev-a", "reading"), t=12.3)]}
    fails, warns, _n = G._over_build_faults(doc, scenes)
    assert fails == [] and warns, (fails, warns)
    late = {"aspect": "16:9", "instants": [dict(_inst("ev-a", "reading"), t=13.5)]}
    assert G._over_build_faults(late, scenes)[0], "past its leave the dock is no longer the chosen one"


def test_m25_keeps_todays_fail_without_under_and_its_signature_for_every_old_caller():
    doc = {"aspect": "16:9", "instants": [_inst("ev-a", "parked")]}
    assert G._layout_faults(doc) == G._layout_faults(doc, _scenes(None))
    fails, _w = G._layout_faults(doc)
    assert len(fails) == 1 and "over the chart's data" in fails[0], fails
    assert G._layout_gate(doc).level == "FAIL"
    src = GATE.read_text(encoding="utf-8")
    assert 'g.append(_layout_gate(layout, tl.get("scenes", [])))' in src, "the gate's run hands M25 the scenes"


def test_the_m25_and_m27_sources_cite_the_ruling():
    assert "E99 s124" in G.SRC_M25 and "E99 s124" in G.SRC_M27


# ------------------------------------------------------------------ the painter: structure
def test_the_veil_sits_above_the_chart_and_below_the_docks():
    html = TEMPLATE.read_text(encoding="utf-8")
    body = html[html.index('<div id="shell">'):]
    a, v, d = body.index('<div id="wash">'), body.index('<div id="dockveil">'), body.index('id="dock-1"')
    assert a < v < d, "the veil is over the page (and its wash) and under the first dock"
    assert re.search(r"#dockveil \{ position: absolute; inset: 0; pointer-events: none; z-index: 0; \}", html)


def test_the_veil_has_its_own_explicit_layer_and_answers_the_layer_switch():
    html = TEMPLATE.read_text(encoding="utf-8")
    assert re.search(r"#dockveil \{ position: absolute; inset: 0; pointer-events: none; z-index: 0; \}", html)
    assert 'html[data-layers]:not([data-layers~="page"]) #dockveil,' in html, "the veil is the page's treatment (R26-13)"


def test_blur_and_behind_cannot_be_combined_but_hover_can():
    """Review round 2 (5): the plate's foreground cutout paints at z 7, above the veil - a `behind` card over a blur
    would keep its occluder sharp over a blurred plate, so the pair is refused by name; the hover has no veil."""
    with pytest.raises(ValueError) as e:
        B.dock_opts({"under": "blur", "behind": "fg"})
    assert "under=blur and behind" in str(e.value), str(e.value)
    assert B.dock_opts({"under": "hover", "behind": "fg"}) == {"under": "hover", "behind": "fg"}


def test_the_veil_keeps_the_pages_words_out_of_the_blur():
    text = ENGINE.read_text(encoding="utf-8")
    assert "const DOCK_VEIL_WORDS = " in text and ".lp-title" in text and ".lp-src" in text
    assert "dockVeilClip(" in text, "the veil is clipped round the page's words (E52: a page cites)"


def test_the_engine_paints_the_veil_once_after_the_light_direction_and_before_the_landings():
    text = ENGINE.read_text(encoding="utf-8")
    assert text.count("paintDockVeil(live, t, ") == 1
    call = text.index("paintDockVeil(live, t, ")
    assert text.rindex('spot.style.setProperty("--sy", "44%");', 0, call) < call < text.index("const worldAnswer = { x: 0, y: 0 };")
    for name in ("const DOCK_VEIL = Object.freeze(", "const DOCK_HOVER = Object.freeze(", "const dockHover = ",
                 "const dockVeilK = "):
        assert name in text, name
    assert "[DERIVED: drift-hold.html" in text, "the hover shadow is read off the reference card"


def test_the_hover_is_prepended_once_inside_the_camera_and_the_plane():
    text = ENGINE.read_text(encoding="utf-8")
    assert text.count("const hov = dockHover(d, t, ") == 1
    hov = text.index("const hov = dockHover(d, t, ")
    assert hov < text.index("if (camArr && camArr.slide === d.slide) {   /* P49 T5: the landed card rides the arrival - screen = at + s (p - look), composed BEFORE")
    assert text.index("paintHoldLight(el, d, t);") > hov
    assert re.search(r"\.filter\(\(d\) => d\.arrive !== \"morph\" && d\.under !== \"hover\"\)", text), \
        "a hovering card lights no wash: the chart under it is untouched"


# ------------------------------------------------------------------ the painter: frames
def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:  # noqa: BLE001 - no browser on this machine: the frame tests skip, never pass
        return False


needs_chromium = pytest.mark.skipif(not _chromium(), reason="chromium not available")


def _frames(tl: dict, uris: dict, ts: list[float], layers: str = "page,docks") -> list[tuple[bytes, dict]]:
    """(PNG, the dock's laid-out box) at each t, on ONE page, seeked in the order given. The caption is the viewer's
    layer, not the chart (a card on the stage demotes it to its anchor, E62), so the frames read the page and the docks
    only - the shell's own layer switch (R26-13), which hides and never removes."""
    import tempfile
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "under.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}?layers={layers}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                for t in ts:
                    png = RB.frame_png(page, t, (w, h))
                    box = page.evaluate("() => { const s = document.getElementById('stage').getBoundingClientRect();"
                                        " const b = document.getElementById('dock-1').getBoundingClientRect();"
                                        " return {x: b.x - s.x, y: b.y - s.y, w: b.width, h: b.height}; }")
                    out.append((png, box))
                browser.close()
        finally:
            srv.shutdown()
            srv.server_close()
    return out


def _word_boxes(tl: dict, uris: dict, t: float) -> list[dict]:
    """The stage boxes of the page's own words at t (the title, the sub, the citation, a note, the key rail)."""
    import tempfile
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "words.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                RB.frame_png(page, t, (w, h))
                boxes = page.evaluate("() => { const s = document.getElementById('stage').getBoundingClientRect();"
                                      " return [...document.querySelectorAll('#wB .lp-title, #wB .lp-sub, #wB .lp-src')]"
                                      ".map((e) => e.getBoundingClientRect()).filter((b) => b.width > 4 && b.height > 4)"
                                      ".map((b) => ({x: b.x - s.x, y: b.y - s.y, w: b.width, h: b.height})); }")
                browser.close()
        finally:
            srv.shutdown()
            srv.server_close()
    return boxes


def _img(png: bytes):
    from PIL import Image
    return Image.open(io.BytesIO(png)).convert("RGB")


def _diff_outside(a: bytes, b: bytes, box: dict, grow: float) -> int:
    """Pixels that differ between a and b OUTSIDE `box` grown by `grow` px on every side."""
    from PIL import ImageChops, ImageDraw
    d = ImageChops.difference(_img(a), _img(b)).convert("L").point(lambda v: 255 if v > 0 else 0)
    ImageDraw.Draw(d).rectangle([box["x"] - grow, box["y"] - grow, box["x"] + box["w"] + grow, box["y"] + box["h"] + grow], fill=0)
    return sum(1 for v in d.getdata() if v)


def _sharpness(png: bytes, region: tuple[int, int, int, int]) -> float:
    """The gradient ENERGY in a region (the mean squared horizontal step) - a blur spreads an edge over many pixels, which
    keeps its total rise (the mean absolute step barely moves) and divides its energy: a blurred chart loses its edges."""
    im = _img(png).convert("L").crop(region)
    px, (w, h) = im.load(), im.size
    return sum((px[x + 1, y] - px[x, y]) ** 2 for y in range(h) for x in range(w - 1)) / max(1, (w - 1) * h)


@pytest.fixture(scope="module")
def surfaces():
    import build_golden_sources as GS
    return GS


@needs_chromium
def test_a_hovering_card_lifts_and_steps_and_leaves_the_chart_untouched(surfaces):
    GS = surfaces
    t_hold = GS.FRAME_T["dock-hover-over-ledger"]
    ts = [t_hold, GS.UNDER_EXIT + 1.2]
    hover = _frames(*GS.dock_under_surface("hover", "ledger"), ts)
    plain = _frames(*GS.dock_under_surface(None, "ledger", life=True), ts)   # the same page life as the hover's
    bare = _frames(*GS.dock_under_surface(None, "ledger", dock=False, life=True), ts)
    (hp, hb), (_pp, pb) = hover[0], plain[0]
    assert hb["y"] < pb["y"] - 4, f"the card lifts: {hb} against {pb}"
    assert hb["w"] > pb["w"] * 1.01, f"the card grows one step: {hb['w']:.1f} against {pb['w']:.1f}"
    grow = GS_SHADOW_REACH * pb["h"] + 24
    assert _diff_outside(hp, bare[0][0], hb, grow) == 0, \
        "outside the card's own box and shadow the chart is the chart with no dock at all (no veil, no wash)"
    assert _diff_outside(plain[0][0], bare[0][0], pb, grow) > 0, "the control: a dock that names nothing still lights its wash"
    assert hover[1][0] == plain[1][0], "after the leave nothing of the hover is left"


GS_SHADOW_REACH = 0.08 + 0.227 * 1.5   # the drop shadow's offset + its blur's visible reach, x card h (drift-hold's card)


@needs_chromium
@pytest.mark.parametrize("world", ["plate", "ledger"])
def test_a_blurring_card_blurs_the_chart_under_it_and_clears_on_its_leave(surfaces, world):
    GS = surfaces
    t_hold = GS.FRAME_T["dock-blur-over-plate"]
    ts = [GS.UNDER_ENTER - 0.5, t_hold, GS.UNDER_EXIT + 1.2]
    blur = _frames(*GS.dock_under_surface("blur", world), ts)
    plain = _frames(*GS.dock_under_surface(None, world), ts)
    assert blur[0][0] == plain[0][0], "before the card enters there is no veil"
    region = GS.UNDER_SHARP_REGION
    s_blur, s_plain = _sharpness(blur[1][0], region), _sharpness(plain[1][0], region)
    assert s_blur < 0.6 * s_plain, f"the chart beside the card is blurred while it reads: {s_blur:.2f} against {s_plain:.2f}"
    box = plain[1][1]
    inner = (round(box["x"] + 0.2 * box["w"]), round(box["y"] + 0.25 * box["h"]),
             round(box["x"] + 0.8 * box["w"]), round(box["y"] + 0.75 * box["h"]))
    assert _img(blur[1][0]).crop(inner).tobytes() == _img(plain[1][0]).crop(inner).tobytes(), \
        "the veil is BELOW the dock: the card itself is as sharp as it always was"
    assert blur[2][0] == plain[2][0], "the blur clears on the dock's leave"
    if world == "ledger":   # review round 2 (4): E52 - the page's title, sub and citation stay sharp over the blurred plot
        words = _word_boxes(*GS.dock_under_surface("blur", world), t_hold)
        assert len(words) >= 3, words
        for wb in words:
            box = (round(wb["x"]) + 2, round(wb["y"]) + 2, round(wb["x"] + wb["w"]) - 2, round(wb["y"] + wb["h"]) - 2)
            assert _img(blur[1][0]).crop(box).tobytes() == _img(plain[1][0]).crop(box).tobytes(), \
                f"the page's words at {box} are as sharp as with no veil"


@needs_chromium
def test_the_hover_and_the_veil_are_pure_in_t(surfaces):
    GS = surfaces
    t1, t2 = GS.FRAME_T["dock-hover-over-ledger"], GS.UNDER_ENTER + 0.9
    leave = GS.UNDER_EXIT + 0.15   # review round 2 (3): the leave is sampled too - the lift setting down, the veil clearing
    for under, world in (("hover", "ledger"), ("blur", "plate"), ("blur", "ledger")):
        a, lv1, _b, lv2, c = _frames(*GS.dock_under_surface(under, world), [t1, leave, t2, leave, t1])
        # the card's laid-out box IS the hover's pose (the lift and the step): the same box on every path to the instant
        assert a[1] == c[1] and lv1[1] == lv2[1], f"{under} over the {world}: the pose after a seek back ({a[1]}, {lv1[1]})"
        # outside the card: the shadow and the veil are functions of t alone. (Inside the card, the live chart payload's own
        # first-draw differs by a 3x3 px patch at its top-left after a seek back - with NO `under` too, a pre-existing
        # artifact of the card's chart, not of this option; reported, not pinned here.)
        assert _diff_outside(a[0], c[0], a[1], 0) == 0, f"{under} over the {world}: a seek back lands on the same bits"
        assert _diff_outside(lv1[0], lv2[0], lv1[1], 0) == 0, f"{under} over the {world}: the leave lands on the same bits"
