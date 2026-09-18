"""R26-233 - THE REVEAL RESCALE DRAGGED LANDED INK; THE AXIS NOW YIELDS TO THE LINE THAT PUSHES IT.

Measured by the critic on the Steel and Paper H unit's copy e (2026-09-18,
`build-h-frozen-f/BUILD-NOTES-H.md` s8c): at 0:28 a `chart_to rescale` opens the y domain 80..277 -> 640 while
the memory line is still drawing, and the three LANDED lines slide 253 px down over 2.2 s with the low ticks
going with them. The words DO name the reveal, so the rescale belongs - what was wrong was its CLOCK: the domain
ran on its own easing beside the line instead of on the line's own climb. E99 s82: *"the movement on screen drags
down the values somehow at 0:05, that can't happen"* - INK NEVER MOVES UNLESS THE SENTENCE MOVES IT.

The door is `follow` on the species: `follow: <name|index>`, or `follow: true` (the series this row's own
`build_to` draws). Frame by frame the y domain's TOP is the followed series' drawn extremum with the page's own
air above it (x1.06 - the 6 % the line builder pads a page's data by), and the transition's `u` is the place on
the A -> B blend that puts the top exactly there. So the landed ink yields as the new line climbs past the old
top, never before it and never after it lands; a standing tick fades only once the LIVE domain has left it
behind, so the low ticks stay. It is the BREAKTHROUGH bars' shape (the bar shoots WHILE the axis rescales, E60 /
CAPABILITIES:88) on a line page.

Two measurements make the mechanism honest, both on the served player: the domain's top at three instants inside
the followed series' window IS its drawn extremum x 1.06 - read off the LIVE TICK PIXELS, not off the engine's
own number - and the landed lines are PIXEL-IDENTICAL (the same path string, the same tag y) until the climb
passes the old top, against the same row with `follow` taken off, which drags them exactly as the H unit did.
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
import render_baseline as RB  # noqa: E402
import build_golden_sources as GS  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"

OBJ = GS.FOLLOW_OBJECT            # the test bed's own object: three lines that land, one that climbs to 600
OBJ_ID = GS.FOLLOW_ID
BORN = GS.FOLLOW_BORN             # [80, 320] - the scale the three landed lines are read on
TARGET = GS.FOLLOW_TARGET         # [80, 630] - the scale the memory line pushes to (600 x 1.06 = 636 >= 630)
MEM = 3                           # the climbing series' index
MEM_TOP = max(v for _x, v in OBJ["series"][MEM]["pts"])
PLATE = "ledger:%s:line;domain=%g,%g" % (OBJ_ID, BORN[0], BORN[1])
BARS = {"title": "Where they stand", "sub": "index", "src": "the test bed", "unit": "",
        "bars": [{"label": "A", "value": 150.0, "color": "crimson"}, {"label": "B", "value": 600.0, "color": "teal"}]}


def _ep(bars: bool = False):
    td = tempfile.TemporaryDirectory()
    ep = Path(td.name)
    (ep / "evidence/objects").mkdir(parents=True)
    (ep / f"evidence/objects/{OBJ_ID}.series.json").write_text(json.dumps(OBJ), encoding="utf-8")
    if bars:
        (ep / "evidence/objects/ev-follow-bars-v1.series.json").write_text(json.dumps(BARS), encoding="utf-8")
    return td, ep


def _species(follow=MEM, at: float = GS.FOLLOW_AT, dur: float = GS.FOLLOW_S, ymax: float | None = TARGET[1],
             ymin: float | None = TARGET[0], window=None, hold: bool = True, draw: bool = True) -> list[dict]:
    """The row: the memory line held at nothing through the page's build, drawn on its word, and the rescale that
    follows it over the same window - the H unit's own shape."""
    out = []
    if hold:
        out.append(copy.deepcopy(GS.FOLLOW_HOLD))
    if draw:
        out.append(copy.deepcopy(GS.FOLLOW_DRAW))
    resc: dict = {"kind": "chart_to", "at": at, "dur": dur, "to": "rescale"}
    if ymin is not None:
        resc["ymin"] = ymin
    if ymax is not None:
        resc["ymax"] = ymax
    if window is not None:
        resc["window"] = window
    if follow is not None:
        resc["follow"] = follow
    out.append(resc)
    return out


def _derive(species: list[dict], plate: str = PLATE, bars: bool = False) -> dict:
    td, ep = _ep(bars)
    try:
        world = B.world_for_plate(plate, (0, 0, 0), ep)
        B.derive_rescale_states(world, species, plate, ep, sid="s01")
        return world
    finally:
        td.cleanup()


def _errs(entry: dict) -> list[str]:
    return B.validate_species([entry], (0, 0, 0), PLATE)   # a chart_to is a PAGE species: the row's plate is the page


# ---- the token's grammar -------------------------------------------------------------------------------


def test_follow_belongs_to_the_rescale_and_to_no_other_verb():
    """A recast, an extend, a park, a morph and a remake all have their own clocks; the RESCALE is the one verb
    whose clock a drawing line can be, because it is the one that moves the page's own scale."""
    for verb, extra in (("recast", {"state": 1}), ("extend", {"to_index": 3}), ("park", {}),
                        ("morph", {"state": 1}), ("remake", {"state": 1})):
        errs = _errs({"kind": "chart_to", "at": 11.0, "dur": 2.2, "to": verb, "follow": MEM, **extra})
        assert any("'follow' belongs to the RESCALE" in e for e in errs), (verb, errs)


def test_follow_takes_true_a_name_or_a_non_negative_index():
    for value in (True, 3, "Memory"):
        assert _errs({"kind": "chart_to", "at": 11.0, "dur": 2.2, "to": "rescale", "ymax": 630, "follow": value}) == []


def test_follow_refuses_anything_that_is_not_a_line_to_follow():
    for bad in (-1, 1.5, "", "   ", [3], {"series": 3}):
        errs = _errs({"kind": "chart_to", "at": 11.0, "dur": 2.2, "to": "rescale", "ymax": 630, "follow": bad})
        assert any("follow must be true" in e for e in errs), (bad, errs)


def test_follow_absent_or_false_is_the_rescale_it_always_was():
    """`false` is the author's explicit "no follow", read exactly as a recast's `keyed: false` is."""
    for value in ({}, {"follow": False}):
        assert _errs({"kind": "chart_to", "at": 11.0, "dur": 2.2, "to": "rescale", "ymax": 630, **value}) == []


def test_follow_needs_the_domains_top():
    errs = _errs({"kind": "chart_to", "at": 11.0, "dur": 2.2, "to": "rescale", "ymin": 80, "follow": MEM})
    assert any("follow needs ymax" in e for e in errs), errs


def test_follow_and_a_window_on_one_verb_is_refused():
    """A followed rescale's clock is the line's own climb, so an x window would open on that clock for a reason
    nothing said - which is the very thing E99 s82 refuses."""
    errs = _errs({"kind": "chart_to", "at": 11.0, "dur": 2.2, "to": "rescale", "ymax": 630,
                  "window": [2020, 2023], "follow": MEM})
    assert any("follow and window on ONE verb" in e for e in errs), errs


# ---- which line, resolved against the page and the row ------------------------------------------------


def test_follow_true_resolves_the_series_the_rows_build_to_draws():
    species = _species(follow=True)
    world = _derive(species)
    assert species[-1]["follow"] == MEM, species[-1]
    assert world["page_states"][0]["axes"]["domain"] == TARGET


def test_a_name_and_an_index_resolve_to_the_same_series():
    by_name, by_index = _species(follow="Memory"), _species(follow=MEM)
    _derive(by_name)
    _derive(by_index)
    assert by_name[-1]["follow"] == by_index[-1]["follow"] == MEM


def test_follow_true_with_no_build_to_on_the_row_is_refused():
    """`true` means "the series this row's build_to draws" - with no build_to it names nothing, and the refusal
    says which two ways out there are."""
    with pytest.raises(ValueError, match=r"follow: true is .the series this row's build_to draws"):
        _derive(_species(follow=True, hold=False, draw=False))


def test_follow_true_is_refused_when_the_rows_caps_name_more_than_one_series():
    species = _species(follow=True)
    species.insert(1, {"kind": "build_to", "at": 5.0, "dur": 0.5, "series": 1,
                       "target": {"kind": "datum", "index": 2, "series": 1}})
    with pytest.raises(ValueError, match="name 2 different series"):
        _derive(species)


def test_follow_true_is_refused_when_a_cap_names_no_series_at_all():
    species = _species(follow=True, hold=False)
    species[0].pop("series")
    species[0]["target"].pop("series")
    with pytest.raises(ValueError, match="applies to EVERY series"):
        _derive(species)


def test_an_unknown_name_and_an_index_past_the_page_are_refused_by_name():
    with pytest.raises(ValueError, match="the page has no series by that name"):
        _derive(_species(follow="Semiconductors"))
    with pytest.raises(ValueError, match=r"the page draws 4 series"):
        _derive(_species(follow=9))


def test_a_later_series_is_not_on_the_page_to_follow():
    """A `later: true` series is not on this state at all - `LPG.build_spec` leaves it out of the page's series
    list and it arrives by `chart_to extend` - so there is no `later` case to write in the resolver: the page has
    three series and both the cap that stages it and the follow that names it are refused for that."""
    obj = copy.deepcopy(OBJ)
    obj["series"][MEM]["later"] = True
    td, ep = _ep()
    try:
        (ep / f"evidence/objects/{OBJ_ID}.series.json").write_text(json.dumps(obj), encoding="utf-8")
        world = B.world_for_plate(PLATE, (0, 0, 0), ep)
        assert len(world["page"]["series"]) == 3, "the later series is not on the page"
        with pytest.raises(ValueError, match=r"series 3 is past the page's last series"):
            B.derive_rescale_states(world, _species(), PLATE, ep, sid="s01")
        with pytest.raises(ValueError, match="the page has no series by that name"):
            B.rescale_follow_series(world, {"at": GS.FOLLOW_AT, "dur": GS.FOLLOW_S, "ymax": TARGET[1],
                                            "follow": "Memory"}, [], "row")
    finally:
        td.cleanup()


def test_only_the_builder_whose_paths_are_its_series_may_be_followed():
    """The conservative bound R26-223 and R26-226 both state: a bars page's own version of this move is the
    BREAKTHROUGH (the bar shoots while the axis rescales), and the refusal says so rather than half-working."""
    plate = "ledger:ev-follow-bars-v1:bars;domain=0,700"
    with pytest.raises(ValueError, match="follow tracks a DRAWING LINE"):
        _derive(_species(), plate=plate, bars=True)
    assert B.FOLLOW_BUILDERS == ("dense-line",)


# ---- and that the domain is in fact FOLLOWING: the refusals that are measurements ---------------------


def test_a_series_that_is_not_drawing_over_the_rescales_window_is_refused_with_the_windows():
    """The rescale fires at 6.0, five seconds before the memory line is drawn: there is nothing to follow, and
    the refusal names the window the row DOES have."""
    with pytest.raises(ValueError, match=r"is not DRAWING over the rescale's own window \[6, 7\]"):
        _derive(_species(at=6.0, dur=1.0))


def test_the_first_build_to_is_the_level_the_build_lands_at_and_not_a_draw():
    """The finding this row turns on: a rescale paints the standing chart FULLY BUILT, so the page's build clock
    is 1 for the whole transition and what still moves under it is the cap SEQUENCE - whose first cap is a
    constant level, not a draw. A line staged with one cap has no window a domain could follow, and the refusal
    says which cap to add rather than silently freezing the domain."""
    species = _species(draw=False)
    species[0]["at"], species[0]["dur"] = GS.FOLLOW_AT, GS.FOLLOW_S      # the only cap, over the rescale's own window
    species[0]["target"]["index"] = 4
    with pytest.raises(ValueError, match="the cap sequence"):
        _derive(species)
    assert B.follow_draw_windows(species, MEM) == [], "one cap is no draw"
    assert B.follow_draw_windows(_species(), MEM) == [(GS.FOLLOW_AT, GS.FOLLOW_AT + GS.FOLLOW_S)]


def test_a_rescale_that_ends_before_the_line_does_is_refused_as_a_snap():
    with pytest.raises(ValueError, match=r"draws until 13.2 - the domain would be handed to the target state"):
        _derive(_species(dur=1.0))


def test_a_target_the_lines_own_numbers_never_reach_is_refused():
    """The other half of "never after it lands": with ymax above the series' own top plus the air, the last of the
    move would happen after the line had stopped - the drag this row exists to end."""
    with pytest.raises(ValueError, match=r"it pushes the domain to 636 and no further"):
        _derive(_species(ymax=900))
    assert B.FOLLOW_HEADROOM == 1.06
    assert MEM_TOP * B.FOLLOW_HEADROOM == pytest.approx(636.0)


def test_a_target_that_does_not_open_the_domain_upward_is_refused():
    with pytest.raises(ValueError, match="a followed rescale OPENS the domain upward"):
        _derive(_species(ymax=300.0))


def test_a_series_that_does_not_climb_in_positive_values_cannot_hold_air_by_a_factor():
    obj = copy.deepcopy(OBJ)
    obj["series"][MEM]["pts"] = [[x, -v] for x, v in obj["series"][MEM]["pts"]]
    td, ep = _ep()
    try:
        (ep / f"evidence/objects/{OBJ_ID}.series.json").write_text(json.dumps(obj), encoding="utf-8")
        world = B.world_for_plate(PLATE, (0, 0, 0), ep)
        with pytest.raises(ValueError, match="a factor holds no air above a number at or below zero"):
            B.derive_rescale_states(world, _species(), PLATE, ep, sid="s01")
    finally:
        td.cleanup()


def test_a_rescale_that_names_no_follow_derives_exactly_what_it_always_did():
    """The byte-identity claim on the compiler's side: the derived state and the species are the same objects a
    plain rescale has produced since P48 T2."""
    plain, followed = _species(follow=None), _species()
    a, b = _derive(plain), _derive(followed)
    assert "follow" not in plain[-1]
    assert a["page_states"] == b["page_states"], "the follow changes no derived state"
    assert {k: v for k, v in followed[-1].items() if k != "follow"} == plain[-1]


# ---- the engine's own wiring, pinned in its text ------------------------------------------------------


def test_the_species_carries_its_follow_onto_the_transition():
    src = ENGINE.read_text(encoding="utf-8")
    assert "u: segEase(clamp01((t - sp.at) / d)), follow: sp.follow }" in src
    assert "const followSi = (sp) => (sp && sp.follow != null && Number.isFinite(+sp.follow)" in src, \
        "series 0 is a legal follow: the test is against null, never falsiness"


def test_the_old_clock_still_stands_on_the_else_arm():
    """Every committed golden rescale was captured through these two expressions and they are untouched: with no
    follow the transition reads its own eased clock and fades a tick against the TARGET domain."""
    src = ENGINE.read_text(encoding="utf-8")
    assert "const fadeOut = (v) => { if (!dom) return xfFade(vIn(v), false, u);" in src
    assert ("if (FW != null) { const uf = lpFollowNeedY(A, FW); const u2 = uf == null ? null : "
            "lpFollowU(sa, sb, uf); u = u2 == null ? 0 : u2; }") in src


def test_the_painted_clock_is_the_one_the_perform_layer_lerps_on():
    src = ENGINE.read_text(encoding="utf-8")
    assert "const uP = lpPaintRescale(states, xf, t3, scene, t);" in src
    assert "if (st.xfNow && uP != null && Number.isFinite(uP)) st.xfNow.u = uP;" in src


def test_the_air_above_the_tip_is_the_builders_own_six_per_cent():
    """ONE number in two places that must not drift: the compiler checks the target is reachable with it and the
    player applies it - and it is the line builder's own `pad = (y1 - y0) * 0.06`."""
    src = ENGINE.read_text(encoding="utf-8")
    head = re.search(r"XF_FOLLOW = Object\.freeze\(\{\s*\n\s*HEAD: ([0-9.]+),", src)
    assert head and float(head.group(1)) == B.FOLLOW_HEADROOM, (head, B.FOLLOW_HEADROOM)
    assert "pad = (y1 - y0) * 0.06" in src


# ---- the frames: the domain's top IS the line's drawn extremum ----------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# Everything the claim needs off the LIVE marks rather than off the engine's own arithmetic: each y tick's value
# and the pixel it is drawn at this frame (the blend writes `y1` on it), the followed series' drawn fraction with
# its points and data, every end tag's y, and each standing series' path exactly as written.
FOLLOW_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, S = (st.states && st.states[0]) || st, Bs = (st.states || [])[1] || null;
  const op = (e) => (e.style.opacity === "" ? 1 : +e.style.opacity);
  const ticksOf = (X) => (((X || {}).marks) || []).filter((m) => m.role === "tick" && m.el)
      .map((m) => ({ v: m.geom.v, y: +m.el.getAttribute("y1"), op: op(m.el) }));
  return {
    active: st.active | 0, states: (st.states || []).length, u: st.xfNow ? st.xfNow.u : null,
    follow: S.followNow ? { si: S.followNow.si, u: S.followNow.u, y0: S.followNow.y0, y1: S.followNow.y1 } : null,
    plot: S.plot ? { T: S.plot.T, B: S.plot.B, y0: S.plot.y0, y1: S.plot.y1, log: !!S.plot.log } : null,
    ticks: ticksOf(S), ticksB: ticksOf(Bs),
    tags: (S.marks || []).filter((m) => m.role === "name" && m.el).map((m) => ({ key: m.key, y: +m.el.getAttribute("y"), op: op(m.el) })),
    paths: (S.paths || []).map((pp) => ({ si: pp.si | 0, d: pp.p.getAttribute("d"), d0: pp.d0,
      f: 1 - parseFloat(pp.p.getAttribute("stroke-dashoffset") || "0") / (pp.len || 1), pts: pp.pts, data: pp.data })),
  };
}"""


def _player(species, runtime: float = GS.RUNTIME):
    """The golden's own page and row on the served player at 16:9 - the aspect the H unit is cut at."""
    from playwright.sync_api import sync_playwright
    td, ep = _ep()
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(PLATE, (0, 0, 0), ep)
    species = copy.deepcopy(species)
    B.derive_rescale_states(world, species, PLATE, ep, sid="s01")
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime],
                 world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="16:9", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[],
                    kinetics={"idle": True, "min_jerk": True})
    html = ep / "follow.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(FOLLOW_PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


def _drawn_max(p: dict, si: int = MEM) -> float | None:
    """The followed series' drawn extremum, computed HERE from the frame's own numbers - the polyline's length
    metric (`capFrac`'s own), the value interpolated in the segment the nib is in."""
    best = None
    for pp in p["paths"]:
        if pp["si"] != si or not (pp["f"] > 0):
            continue
        pts, data = pp["pts"], pp["data"]
        segs = [((pts[k][0] - pts[k - 1][0]) ** 2 + (pts[k][1] - pts[k - 1][1]) ** 2) ** 0.5
                for k in range(1, len(pts))]
        want, acc, cur = sum(segs) * min(1.0, pp["f"]), 0.0, float(data[0][1])
        for k, seg in enumerate(segs, start=1):
            if acc + seg <= want:
                cur, acc = max(cur, float(data[k][1])), acc + seg
                continue
            a, b = float(data[k - 1][1]), float(data[k][1])
            cur = max(cur, a + (b - a) * (max(0.0, min(1.0, (want - acc) / seg)) if seg else 0.0))
            break
        best = cur if best is None else max(best, cur)
    return best


def _live_top(p: dict) -> float:
    """The domain's TOP this frame, read off the live tick pixels: two ticks give the affine map the blend is
    drawing on, and the top is the value at the plot's own y = T."""
    ticks = sorted(p["ticks"], key=lambda t: t["y"])
    lo, hi = ticks[-1], ticks[0]
    assert hi["y"] != lo["y"], ticks
    slope = (hi["v"] - lo["v"]) / (hi["y"] - lo["y"])
    return lo["v"] + (p["plot"]["T"] - lo["y"]) * slope


def _tag_y(p: dict, key: str = "name:s0") -> float:
    return next(t["y"] for t in p["tags"] if t["key"] == key)


# The instants, MEASURED (tests/R26-233-NOTE.md's table) rather than chosen. The cap's clock is min-jerk - slow at
# each end, quickest in the middle - and the memory line's extremum passes the standing top (320, reached with the
# air at a drawn 302) between 12.10 and 12.30, so these three are the yield itself: u 0.479, 0.865 and 0.989.
INSTANTS = (12.30, 12.60, 12.90)
# ... and these are the frames the domain has NOT moved on, every one inside the rescale's own window.
HELD = (11.00, 11.20, 11.55, 11.95, 12.10)


@needs_browser
def test_the_domains_top_is_the_followed_lines_drawn_extremum_at_every_instant():
    """R26-233's acceptance, measured three times inside the window: the top of the scale the page is DRAWING on
    is the followed line's drawn extremum x the page's own air - so the axis is on the line's clock and on
    nothing else."""
    at, errs, close = _player(_species())
    try:
        rows = []
        for t in INSTANTS:
            p = at(t)
            drawn, top = _drawn_max(p), _live_top(p)
            assert drawn is not None, (t, p["paths"])
            want = min(TARGET[1], max(BORN[1], drawn * B.FOLLOW_HEADROOM))
            rows.append((t, round(drawn, 1), round(top, 1), round(want, 1)))
            assert abs(top - want) < 1.5, ("the domain's top is the line's own", rows[-1])
            assert 0.0 < p["follow"]["u"] <= 1.0, (t, p["follow"])
            assert len([k for k in p["ticks"] if k["op"] > 0.01]) >= 2, ("a scale is never one tick", t, p["ticks"])
        assert rows[0][2] < rows[1][2] < rows[2][2], ("the top opens with the climb", rows)
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_the_landed_ink_does_not_move_until_the_climb_passes_the_old_top():
    """The operator's own sentence as a measurement: while the memory line is still under the standing top the
    three landed lines are PIXEL-IDENTICAL to the page before the word - the same path string, the same tag y -
    and the yield begins only when the climb with its air reaches the old ceiling."""
    at, errs, close = _player(_species())
    try:
        before = at(GS.FOLLOW_AT - 0.1)          # the frame before the rescale opens
        base_tag = _tag_y(before)
        base_d = {pp["si"]: pp["d"] for pp in before["paths"]}
        for t in HELD:
            p = at(t)
            drawn = _drawn_max(p) or 0.0
            assert drawn * B.FOLLOW_HEADROOM < BORN[1], ("still under the old top", t, drawn)
            assert p["follow"]["u"] == 0, (t, p["follow"])
            assert _tag_y(p) == base_tag, ("the landed tag moved before the climb reached the top", t, drawn)
            for pp in p["paths"]:
                if pp["si"] != MEM:
                    assert pp["d"] == base_d[pp["si"]], ("a landed line moved", t, pp["si"])
                    assert pp["d"] == pp["d0"], ("... and it is the page's own geometry", t, pp["si"])
        after = at(INSTANTS[-1])
        assert _tag_y(after) > base_tag + 20, ("and then it yields", base_tag, _tag_y(after))
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_the_low_ticks_stay_while_the_live_domain_still_holds_them():
    """The other half of what the critic read at 0:28: the 80 / 100 ticks vanished. A standing tick now fades only
    once the LIVE domain has left it behind - and a domain that is only OPENING never leaves one."""
    at, errs, close = _player(_species())
    try:
        low = sorted(k["v"] for k in at(GS.FOLLOW_AT)["ticks"])[:2]
        for t in HELD + INSTANTS + (13.19,):
            p = at(t)
            lit = {k["v"]: k["op"] for k in p["ticks"]}
            for v in low:
                assert lit.get(v, 0) > 0.99, ("a tick the live domain still holds stays lit", t, v, lit)
            assert len([k for k in p["ticks"] if k["op"] > 0.01]) >= 2, (t, p["ticks"])
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_a_seek_back_is_the_play_and_the_target_stands_at_the_end():
    at, errs, close = _player(_species())
    try:
        first = at(INSTANTS[1])
        end = at(GS.FOLLOW_AT + GS.FOLLOW_S + 0.2)     # past the window: the derived state is the page
        assert end["active"] == 1 and end["states"] == 2, end
        again = at(INSTANTS[1])
        assert again["follow"]["u"] == first["follow"]["u"], "the domain is a pure function of the frame"
        assert _tag_y(again) == _tag_y(first)
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_the_same_row_without_follow_drags_the_landed_ink_the_way_the_h_unit_did():
    """The before/after on one page and one set of instants: with `follow` taken off the domain runs on its own
    easing, so the landed tag is already 26 px down while the memory line has drawn a third of itself - and both
    land on the same last frame. The followed one is never ahead of the line."""
    drops = {}
    for name, species in (("follow", _species()), ("plain", _species(follow=None))):
        at, errs, close = _player(species)
        try:
            base = _tag_y(at(GS.FOLLOW_AT - 0.1))
            drops[name] = {t: round(_tag_y(at(t)) - base, 1) for t in HELD + INSTANTS + (13.19,)}
            assert not errs, errs
        finally:
            close()
    for t in HELD:
        assert drops["follow"][t] == 0.0, ("the followed domain moves nothing while the line is under the top", t, drops)
    assert drops["plain"][11.20] > 0.0, ("the plain rescale is already dragging it", drops)
    assert drops["plain"][11.95] > 25.0, ("... 26 px down a third of the way through the line", drops)
    assert drops["follow"][12.30] < drops["plain"][12.30] - 10.0, ("the followed domain is behind the line", drops)
    # ... and the two CONVERGE as the line lands, which is the point: the followed domain is not a slower rescale,
    # it is the SAME move re-timed onto the climb. By 12.60 the climb has asked for 548 of the target's 630 and the
    # two readings are 0.5 px apart; on the last frame of the window they are the same number.
    for t in (12.60, 12.90):
        assert abs(drops["follow"][t] - drops["plain"][t]) < 1.5, (t, drops)
    assert drops["follow"][13.19] == drops["plain"][13.19], ("and both land on the same frame", drops)


# ---- the goldens ---------------------------------------------------------------------------------------


def test_the_golden_pair_is_the_same_page_at_two_instants():
    a, _ua = GS.SURFACES["page-rescale-follow"]()
    b, _ub = GS.SURFACES["page-rescale-follow-yield"]()
    assert a["scenes"] == b["scenes"], "two surfaces, one timeline - the instants differ and nothing else"
    assert GS.FRAME_T["page-rescale-follow"] != GS.FRAME_T["page-rescale-follow-yield"]
    assert GS.FOLLOW_AT < GS.FRAME_T["page-rescale-follow"] < GS.FRAME_T["page-rescale-follow-yield"] \
        < GS.FOLLOW_AT + GS.FOLLOW_S, "both instants are inside the followed line's own window"


def test_the_golden_source_carries_exactly_what_the_compiler_resolves():
    tl, _uris = GS.SURFACES["page-rescale-follow"]()
    scene = tl["scenes"][0]
    resc = [e for e in scene["species"] if e.get("kind") == "chart_to"][0]
    assert resc["follow"] == MEM, "the NAME the source authors is resolved to the series index by the compiler"
    assert scene["world"]["page"]["axes"]["domain"] == BORN
    assert scene["world"]["page_states"][0]["axes"]["domain"] == TARGET
    assert [e["at"] for e in scene["species"] if e.get("kind") == "build_to"] == [GS.FOLLOW_HOLD["at"], GS.FOLLOW_AT]
