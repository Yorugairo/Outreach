"""P73 T2: THE DATED EVENT TIMELINE PAGE - `ledger:<id>:timeline`.

Dated EVENTS on one real date axis with no series (the AMD RFSoC episode's gap #2): each event a date, a short label and
an optional research tier, landing on its word (`build_to` names an event by index); the axis STATES ITS RULE (E28 (2)):
a gap that dwarfs the rest is cut and the cut is drawn `//` with its length written, and each stretch writes its own
tick ("1 tick = 1 month"); today is marked; the newest named event is lit (the one glow system); an event whose date
MOVED strikes it and writes the new one. 16:9 is a horizontal axis with the labels in lanes above it; 9:16 is a
vertical axis with the labels in a column - a portrait layout, not a squeezed one.

Proved on the story's own dates (the research pack's section 2): 2017-08-15 the control (3A001.a.14 created),
2019-02-20 the chip announced, 2026-06 the campaign (PLAUSIBLE), 2026-08-27 the campaign ends, 2026-09-19 Patel's
post, 2026-09-24 the article, the ship date 2026-11-06 (PLAUSIBLE, Tom's) moved to 2027-05-06 (CONFIRMED, the
Crowd Supply page). The 10-event decade fixture below is SYNTHETIC (labels "Event 1".."Event 10") - it proves the
layout on the operator's uneven-density shape, and states nothing about the world.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as L  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

SURFACE, SURFACE_P = "event-timeline", "event-timeline-9x16"
ASPECTS = ("16:9", "9:16")


def _story() -> dict:
    import build_golden_sources as G
    return copy.deepcopy(G.TIMELINE_STORY)


def _decade() -> dict:
    """SYNTHETIC: ten events over a decade, clustered in 2019-2020 and 2025-2026 (the operator's geopolitical shape)."""
    dates = ["2016-03", "2019-05-15", "2019-08", "2020-06-30", "2020-11", "2022-02-14", "2022-10-07", "2025-04",
             "2025-08-12", "2026-09-19"]
    return {"title": "Synthetic decade", "sub": "ten dates, clustered", "src": "Synthetic fixture; not a claim",
            "today": "2026-09-26",
            "events": [{"date": d, "label": f"Event {i + 1} on the record"} for i, d in enumerate(dates)]}


def _errs(s: dict) -> str:
    return " | ".join(L.validate(s, "timeline"))


# ---- the object ---------------------------------------------------------------------------------------------------

def test_timeline_is_a_variant_with_its_own_builder():
    s = _story()
    assert "timeline" in L.VARIANTS and "timeline" not in L.CHART_VARIANTS
    assert L.pick_builder(s, "timeline") == "timeline"
    assert L.infer_variant(s) == "timeline"


def test_the_story_validates():
    assert L.validate(_story(), "timeline") == []
    assert L.validate(_decade(), "timeline") == []


@pytest.mark.parametrize("n", [2, 11])
def test_three_to_ten_events(n):
    s = _decade()
    s["events"] = s["events"][:n] if n < 10 else s["events"] + [{"date": "2026-09-20", "label": "one more"}]
    assert "3-10 events" in _errs(s)


@pytest.mark.parametrize("date", ["2017-13", "2017-02-30", "17-08-15", "Aug 2017", 2017, "2017-8-1"])
def test_a_date_that_is_not_a_real_date_is_refused(date):
    s = _story()
    s["events"][0]["date"] = date
    assert "is not YYYY, YYYY-MM or YYYY-MM-DD" in _errs(s)


def test_the_file_lists_events_in_time_order():
    s = _story()
    s["events"][1]["date"] = "2016-01-01"
    assert "in time order" in _errs(s)


def test_a_rejected_tier_never_goes_on_the_page():
    s = _story()
    s["events"][2]["tier"] = "REJECTED"
    assert "a REJECTED claim never goes on the page" in _errs(s)
    s["events"][2]["tier"] = "MAYBE"
    assert "is not one of CONFIRMED|PLAUSIBLE|UNSOURCED" in _errs(s)


def test_unknown_keys_and_data_keys_are_refused_by_name():
    s = _story()
    s["events"][0]["value"] = 3
    assert "key 'value' is not an event's" in _errs(s)
    s = _story()
    s["series"] = [{"name": "x", "pts": [[2017, 1], [2018, 2]]}]
    assert "a timeline page draws DATES, not values" in _errs(s)


def test_today_is_stated_as_a_day():
    s = _story()
    s["today"] = "2026-09"
    assert "today" in _errs(s)
    del s["today"]
    assert "today" in _errs(s)


def test_a_label_is_short():
    s = _story()
    s["events"][0]["label"] = "x" * 45
    assert "at most 44" in _errs(s)


def test_a_moved_date_must_move_and_carries_its_own_tier():
    s = _story()
    ev = next(e for e in s["events"] if "moved_to" in e)
    ev["moved_to"]["date"] = ev["date"]
    assert "the date did not move" in _errs(s)
    s = _story()
    next(e for e in s["events"] if "moved_to" in e)["moved_to"]["tier"] = "REJECTED"
    assert "REJECTED" in _errs(s)


def test_a_cut_that_hides_an_event_is_refused():
    s = _story()
    s["cuts"] = [["2017-01", "2018-01"]]
    assert "would hide 1 dated thing" in _errs(s)
    s["cuts"] = [["2019-06", "2026-03"]]
    assert _errs(s) == ""
    s["cuts"] = [["2019-06", "2026-03"], ["2020-01", "2021-01"]]
    assert "two cuts overlap" in _errs(s)


# ---- the axis states its rule (E28 (2)) -----------------------------------------------------------------------------

def test_the_story_is_cut_where_nothing_happened():
    s = _story()
    cuts = L.timeline_cuts(s)
    assert len(cuts) == 1
    a, b = cuts[0]
    assert a == pytest.approx(L.timeline_decimal("2019-02-20")) and b == pytest.approx(L.timeline_decimal("2026-06"))


def test_an_even_decade_is_not_cut():
    assert L.timeline_cuts(_decade()) == []


def test_an_authored_empty_cut_list_draws_one_linear_axis():
    s = _story()
    s["cuts"] = []
    assert L.timeline_cuts(s) == []
    assert len(L.timeline_stretches(s)) == 1


def test_each_stretch_writes_its_tick_and_the_cut_its_length():
    spec = L.build_spec(_story(), "timeline")
    for aspect in ASPECTS:
        lay = spec["layout"][aspect]
        assert [s["rule"] for s in lay["stretches"]] == ["1 tick = 1 year", "1 tick = 1 month"], aspect
        assert [r["text"] for r in lay["rules"]] == ["1 tick = 1 year", "1 tick = 1 month"]
        assert [c["text"] for c in lay["cuts"]] == ["7 yrs"]
    assert any("E28 (2)" in n and "cut 7 yrs" in n for n in spec["judge"])


def test_dates_run_in_order_along_the_axis_at_both_aspects():
    spec = L.build_spec(_story(), "timeline")
    for aspect in ASPECTS:
        lay = spec["layout"][aspect]
        axis_i = 1 if lay["vertical"] else 0
        pins = [(it["x"], it["pin"][axis_i]) for it in lay["items"]]
        pins.sort()
        assert all(p1 < p2 for (_, p1), (_, p2) in zip(pins, pins[1:])), aspect
        other = [it["pin"][1 - axis_i] for it in lay["items"]]
        assert len(set(other)) == 1, "every pin stands ON the axis"


def test_the_portrait_axis_is_vertical_and_the_landscape_horizontal():
    spec = L.build_spec(_story(), "timeline")
    assert spec["layout"]["9:16"]["vertical"] is True and spec["layout"]["16:9"]["vertical"] is False


def _boxes_apart(boxes: list, gap: float = 0.0) -> bool:
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap:
                return False
    return True


@pytest.mark.parametrize("fixture", ["story", "decade"])
@pytest.mark.parametrize("aspect", ASPECTS)
def test_no_label_overlaps_another_and_every_label_is_inside_the_plot(fixture, aspect):
    s = _story() if fixture == "story" else _decade()
    lay = L.build_spec(s, "timeline")["layout"][aspect]
    boxes = [it["box"] for it in lay["items"]]
    assert _boxes_apart(boxes), [(it["date_text"], it["box"]) for it in lay["items"]]
    W, H = lay["plot"]["w"], lay["plot"]["h"]
    for b in boxes:
        assert -0.5 <= b[0] and b[2] <= W + 0.5 and -0.5 <= b[1] and b[3] <= H + 0.5, (b, W, H)
    assert lay["warnings"] == []


@pytest.mark.parametrize("fixture", ["story", "decade"])
@pytest.mark.parametrize("aspect", ASPECTS)
def test_no_leader_crosses_another_label(fixture, aspect):
    s = _story() if fixture == "story" else _decade()
    lay = L.build_spec(s, "timeline")["layout"][aspect]
    for it in lay["items"]:
        x1, y1, x2, y2 = it["leader"]
        for other in lay["items"]:
            if other is it:
                continue
            b = other["box"]
            if lay["vertical"]:   # a short horizontal run from the axis to the column
                assert not (min(y1, y2) < b[3] and max(y1, y2) > b[1] and b[0] < max(x1, x2) - 1), (it["date_text"], other["date_text"])
            else:                 # a vertical run from the pin up to the block
                assert not (b[0] < x1 < b[2] and min(y1, y2) < b[3] and max(y1, y2) > b[1]), (it["date_text"], other["date_text"])


@pytest.mark.parametrize("aspect", ASPECTS)
def test_no_standing_tick_label_collides_with_today_a_cut_or_another_tick(aspect):
    lay = L.build_spec(_story(), "timeline")["layout"][aspect]
    shown = [t["box"] for t in lay["ticks"] if not t.get("hidden")]
    assert len(shown) >= 4 and _boxes_apart(shown)
    for b in shown:
        assert _boxes_apart([b, lay["today"]["box"]]) and all(_boxes_apart([b, c["box"]]) for c in lay["cuts"])


def test_the_tier_is_written_and_the_moved_date_is_its_own_item():
    lay = L.build_spec(_story(), "timeline")["layout"]["16:9"]
    by = {(it["event"], it["kind"]): it for it in lay["items"]}
    assert by[(2, "event")]["tier"] == "PLAUSIBLE" and by[(2, "event")]["date_line"] == "Jun 2026 · reported"
    assert by[(0, "event")]["date_line"] == "15 Aug 2017"
    ship, moved = by[(6, "event")], by[(6, "moved_to")]
    assert ship["moved"] is True and ship["date_text"] == "6 Nov 2026" and moved["date_text"] == "6 May 2027"
    assert moved["pin"][0] > ship["pin"][0]


def test_today_stands_between_the_article_and_the_ship_date():
    lay = L.build_spec(_story(), "timeline")["layout"]["16:9"]
    by = {(it["event"], it["kind"]): it for it in lay["items"]}
    assert by[(5, "event")]["pin"][0] < lay["today"]["p"] < by[(6, "event")]["pin"][0]


def test_the_layout_is_pure():
    s = _story()
    frozen = json.dumps(s, sort_keys=True)
    a = L.build_spec(s, "timeline")
    b = L.build_spec(s, "timeline")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert json.dumps(s, sort_keys=True) == frozen


def test_page_boxes_reports_the_timelines_own_plot():
    spec = L.build_spec(_story(), "timeline")
    for aspect in ASPECTS:
        bx = L.page_boxes(spec, aspect)
        c, p = bx["chart"], bx["plot"]
        assert c["x"] <= p["x"] and p["x"] + p["w"] <= c["x"] + c["w"] + 1 and p["w"] >= 0.9 * c["w"] - 60


# ---- the compiler -----------------------------------------------------------------------------------------------------

def test_the_compiler_knows_the_pages_own_clock():
    assert B.PAGE_INTRINSIC_BUILDERS["timeline"] == pytest.approx(3.6)
    spec = L.build_spec(_story(), "timeline")
    assert B.page_build_duration_s(spec) == pytest.approx(3.6)


def test_build_to_names_an_event_on_a_timeline_row():
    import build_golden_sources as G
    species = copy.deepcopy(G.TIMELINE_WORDS)
    assert not B.validate_species(species, (0, 0, 0), "ledger:amd-rfsoc-timeline:timeline")
    world = {"kind": "ledger", "page": L.build_spec(_story(), "timeline"), "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    B.derive_rescale_states(world, species, "ledger:amd-rfsoc-timeline:timeline", ROOT)
    assert not world.get("page_states")


def test_the_plate_id_parses_and_each_word_is_a_drawing_window_the_gate_credits():
    import build_golden_sources as G
    assert B.parse_ledger_id(G.TIMELINE_PLATE)[:2] == ("amd-rfsoc-timeline", "timeline")
    species = copy.deepcopy(G.TIMELINE_WORDS)
    world = {"kind": "ledger", "page": L.build_spec(_story(), "timeline"), "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    windows = B.page_build_windows(world, species, 0.0)
    for sp in species:   # E63: every word the page performs on is a window the motion gate reads as the chart drawing
        assert (sp["at"], round(sp["at"] + sp["dur"], 3)) in [(a, round(b, 3)) for a, b in windows]


# ---- the painter (the served player) --------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """t => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp;
  const S = (st.states && st.states[st.active | 0]) || st, T = S.timeline;
  const bb = (e) => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.x + r.width, r.y + r.height]; };
  const op = (e) => { let o = 1; for (let n = e; n && n.getAttribute; n = n.parentNode) { const a = n.getAttribute('opacity');
    if (a != null) o *= +a; if (n.style && n.style.opacity !== '') o *= +n.style.opacity; } return o; };
  if (!T) return { has: false };
  return { has: true, vertical: T.vertical,
    axis: T.axis.map(e => ({ op: op(e), x1: +e.getAttribute('x1'), y1: +e.getAttribute('y1'), x2: +e.getAttribute('x2'), y2: +e.getAttribute('y2'), dash: e.getAttribute('stroke-dashoffset') })),
    slashes: T.slashes.map(e => ({ op: op(e), box: bb(e) })),
    cuts: T.cutEls.map(e => ({ text: e.textContent, op: op(e), box: bb(e) })),
    rules: T.ruleEls.map(e => ({ text: e.textContent, op: op(e), box: bb(e) })),
    ticks: T.tickEls.map(e => ({ text: e.textContent, op: op(e), box: bb(e) })),
    today: { op: op(T.today.g), text: T.today.text.textContent, box: bb(T.today.text) },
    items: T.items.map(it => ({ event: it.event, kind: it.kind, land: op(it.g), lit: it.lit,
      glow: it.pin.style.filter || '', dateFill: getComputedStyle(it.date).fill,
      strike: it.strike ? { op: op(it.strike), len: +it.strike.getAttribute('x2') - +it.strike.getAttribute('x1') } : null,
      box: bb(it.words), pin: bb(it.pin) })) };
}"""


def _player(surface: str = SURFACE, mutate=None):
    tl, uris, _t, asp = RB.load_surface(surface)
    if mutate:
        tl = mutate(copy.deepcopy(tl))
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "tl.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[asp]
    page, _errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded
    return page, close


def _at(page, t: float) -> dict:
    page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    return page.evaluate(PROBE, t)


def _landed(d: dict) -> list:
    return [(it["event"], it["kind"]) for it in d["items"] if it["land"] >= 0.99]


def _lit(d: dict) -> list:
    return [(it["event"], it["kind"]) for it in d["items"] if it["lit"] >= 0.99]


def _words():
    import build_golden_sources as G
    return G.TIMELINE_WORDS, G.FRAME_T


@needs_browser
def test_the_page_draws_its_axis_states_its_rule_and_marks_today():
    words, FT = _words()
    page, close = _player()
    try:
        d = _at(page, FT[SURFACE])
        assert d["has"] and d["vertical"] is False
        assert len(d["axis"]) == 2 and min(a["op"] for a in d["axis"]) >= 0.99, "two stretches, both drawn"
        assert [c["text"] for c in d["cuts"]] == ["7 yrs"] and d["cuts"][0]["op"] >= 0.99
        assert len(d["slashes"]) == 2 and min(s["op"] for s in d["slashes"]) >= 0.99, "the cut is DRAWN (E28 (2))"
        assert sorted(r["text"] for r in d["rules"]) == ["1 tick = 1 month", "1 tick = 1 year"]
        assert min(r["op"] for r in d["rules"]) >= 0.99
        assert d["today"]["text"] == "today" and d["today"]["op"] >= 0.99
        shown = [t for t in d["ticks"] if t["op"] >= 0.99]
        assert any(t["text"] == "2018" for t in shown) and any(t["text"] == "Aug" for t in shown)
    finally:
        close()


@needs_browser
def test_each_event_lands_on_its_word_and_the_named_one_is_lit():
    words, FT = _words()
    page, close = _player()
    try:
        first, post = words[0]["at"], words[4]["at"]
        d0 = _at(page, first - 0.05)
        assert _landed(d0) == [] and _lit(d0) == []
        d1 = _at(page, first + 0.6)
        assert _landed(d1) == [(0, "event")] and _lit(d1) == [(0, "event")]
        lit0 = next(it for it in d1["items"] if it["event"] == 0)
        assert "#lpfill-" in lit0["glow"], "the lit pin glows by the one glow system (lpFillGlow)"
        d4 = _at(page, post + 0.6)
        assert _landed(d4) == [(i, "event") for i in range(5)]
        assert _lit(d4) == [(4, "event")], "the newest named event is the lit one; the one before hands its light over"
        prev = next(it for it in d4["items"] if it["event"] == 3)
        assert prev["glow"] in ("", "none")
    finally:
        close()


@needs_browser
def test_the_moved_date_is_struck_and_the_new_one_written_on_its_second_word():
    words, FT = _words()
    page, close = _player()
    try:
        second = [w for w in words if w["target"]["index"] == 6][1]["at"]
        before = _at(page, second - 0.05)
        ship = next(it for it in before["items"] if (it["event"], it["kind"]) == (6, "event"))
        assert ship["land"] >= 0.99 and ship["strike"]["op"] < 0.01
        assert (6, "moved_to") not in _landed(before)
        after = _at(page, second + 1.4)
        ship = next(it for it in after["items"] if (it["event"], it["kind"]) == (6, "event"))
        assert ship["strike"]["op"] >= 0.99 and ship["strike"]["len"] > 20
        assert (6, "moved_to") in _landed(after) and _lit(after) == [(6, "moved_to")]
    finally:
        close()


def _apart(boxes: list) -> bool:
    return _boxes_apart([b for b in boxes], 0.0)


@needs_browser
@pytest.mark.parametrize("surface", [SURFACE, SURFACE_P])
def test_as_drawn_no_label_overlaps_another_and_all_are_on_the_stage(surface):
    _words_, FT = _words()
    page, close = _player(surface)
    try:
        d = _at(page, FT[surface])
        boxes = [it["box"] for it in d["items"] if it["land"] >= 0.99]
        assert len(boxes) == 8
        assert _apart(boxes), boxes
        W, H = RB.STAGE[RB.load_surface(surface)[3]]
        assert all(0 <= b[0] and b[2] <= W and 0 <= b[1] and b[3] <= H for b in boxes)
        ticks = [t["box"] for t in d["ticks"] if t["op"] >= 0.99]
        assert _apart(ticks + [d["today"]["box"]] + [c["box"] for c in d["cuts"]])
    finally:
        close()


@needs_browser
def test_the_portrait_page_stands_its_axis_upright():
    _w, FT = _words()
    page, close = _player(SURFACE_P)
    try:
        d = _at(page, FT[SURFACE_P])
        assert d["vertical"] is True
        assert all(abs(a["x1"] - a["x2"]) < 0.01 and a["y2"] > a["y1"] for a in d["axis"])
        pins = [(it["event"], it["kind"], it["pin"][1]) for it in d["items"]]
        ys = [p[2] for p in sorted(pins, key=lambda p: (p[0], p[1] != "event"))]
        assert ys == sorted(ys), "dates run DOWN the page"
    finally:
        close()


@needs_browser
def test_the_page_is_a_function_of_t():
    words, FT = _words()
    page, close = _player()
    try:
        t = words[4]["at"] + 0.2
        cold = _at(page, t)
        _at(page, FT[SURFACE])
        _at(page, 0.5)
        warm = _at(page, t)
        for d in (cold, warm):   # a glow's filter id counts filters in the order they were first built - its PRESENCE is the state
            for it in d["items"]:
                it["glow"] = bool(it["glow"] and it["glow"] != "none")
        assert cold == warm
    finally:
        close()
