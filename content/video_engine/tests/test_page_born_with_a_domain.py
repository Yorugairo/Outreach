"""R26-223 - A PAGE CANNOT BE BORN WITH A DOMAIN.

Measured on the Steel and Paper H unit (2026-09-18): the hook's page opens on the evidence object's own scale -
`ledger_world` -> `LPG.build_spec`, and `AXES_KEYS` (`domain` among them) live on the OBJECT - so the only way to
open on the two lines' own range was to let the page arrive wrong and `chart_to rescale` off it. A rescale may not
fire at 0.00 (M23: never over a build, never at a page's edge), so the row's first four seconds stood on a scale
the sentence was not about.

The door is `;domain=<ymin>,<ymax>` on the ledger token: the y scale the page is BORN on, written onto the page's
own `axes` at load. The OBJECT's domain stays the default - a row that names none writes nothing.

Why that token and not `;ymin=..;ymax=..`: it names the key it WRITES (`axes.domain` is what the page spec
carries, what a derived rescale state carries and what the player reads, so one word describes both ends of the
transition); a domain is an indivisible pair and the plate-option grammar already spells a compound value as a
comma list inside one token (`plane=quad:<8 numbers>`); and both ends are required because the bars builder reads
`dom[0]` and `dom[1]` straight into its scale, so a half-declared domain would be a silent NaN on a bars page.

THE PLAYER IS UNTOUCHED. `buildLedgerLine` (`scene-evidence-engine.mjs:8679`) and `buildLedgerBars` (`:8431`) have
read `axes.domain` since P48 T2 / the breakthrough; neither ever cared which state carried it. So this row moves no
engine line, no mirrored module and no golden pixel - the compiler was the only shut door.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

# A two-line object with NO axes of its own, so every scale in this file is either the data's or the row's.
# Series A runs 100 -> 300 and B runs 100 -> 118: the object's own scale is A's, and B is the flat pair of lines
# at the bottom that the H unit's hook is actually about.
LINES = {"title": "Two lines, one scale", "sub": "index, 100 = the first period", "src": "the test bed", "unit": "",
         "series": [{"name": "A", "color": "crimson",
                     "pts": [[2020, 100], [2021, 140], [2022, 180], [2023, 240], [2024, 300]]},
                    {"name": "B", "color": "teal",
                     "pts": [[2020, 100], [2021, 105], [2022, 108], [2023, 112], [2024, 118]]}]}
BARS = {"title": "Where the two stand", "sub": "index, 100 = the first period", "src": "the test bed", "unit": "",
        "bars": [{"label": "A", "value": 300.0, "color": "crimson"}, {"label": "B", "value": 118.0, "color": "teal"}]}

BORN = [95.0, 130.0]          # the two lines' own scale: B's range with air, A off the top (the plot clips it)
RESCALE_TO = [60.0, 340.0]    # ... and the scale a `chart_to rescale` moves to from there
# the OBJECT's own scale, the way `buildLedgerLine` derives it when nothing names one: the data's range plus 6 %
DATA_LO, DATA_HI = 100.0 - (300.0 - 100.0) * 0.06, 300.0 + (300.0 - 100.0) * 0.06


def _ep(then: bool = False):
    td = tempfile.TemporaryDirectory()
    ep = Path(td.name)
    (ep / "evidence/objects").mkdir(parents=True)
    (ep / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(LINES), encoding="utf-8")
    if then:
        (ep / "evidence/objects/ev-bars-v1.series.json").write_text(json.dumps(BARS), encoding="utf-8")
    return td, ep


# ---- the token's grammar -------------------------------------------------------------------------------


def test_domain_is_a_plate_option_and_check_opt_routes_it():
    assert "domain" in B.PLATE_OPTS
    assert B.split_plate_opts("ledger:ev-lines-v1:line;domain=95,130")[1] == {"domain": "95,130"}
    with pytest.raises(ValueError, match="not <ymin>,<ymax>"):
        B.split_plate_opts("ledger:ev-lines-v1:line;domain=95")


def test_the_pair_is_read_as_the_two_ends_of_the_scale():
    assert B.page_domain_spec("95,130", None, "row") == [95.0, 130.0]
    assert B.page_domain_spec(" -2.5 , 4 ", None, "row") == [-2.5, 4.0]


def test_a_half_declared_domain_is_refused_and_says_why():
    """The bars builder reads both ends straight into its scale, so a one-sided born domain is a silent NaN."""
    for bad in ("95,", ",130", "95", "95,130,200"):
        with pytest.raises(ValueError, match="not <ymin>,<ymax>"):
            B.page_domain_spec(bad, None, "row")
    with pytest.raises(ValueError, match="bars page's scale reads them both"):
        B.page_domain_spec("95,", None, "row")


def test_a_non_numeric_or_inverted_domain_is_refused():
    with pytest.raises(ValueError, match="not two numbers"):
        B.page_domain_spec("low,high", None, "row")
    for bad in ("130,95", "95,95"):
        with pytest.raises(ValueError, match="empty or inverted"):
            B.page_domain_spec(bad, None, "row")


def test_a_domain_whose_ends_are_not_FINITE_is_refused_by_the_parser():
    """The reviewer's round: `inf` satisfies `hi > lo` outright, so `;domain=95,inf` used to be written onto the
    page's own axes for the player to divide by, and `-inf,130` with it. A scale has two FINITE ends, and the
    refusal is the parser's - the one place both the grammar pass and the page pass go through."""
    for bad in ("95,inf", "nan,130", "-inf,inf", "95,NaN", "-inf,130"):
        with pytest.raises(ValueError, match="is not two numbers"):
            B.page_domain_spec(bad, None, "row")
        with pytest.raises(ValueError, match="is not two numbers"):
            B.split_plate_opts("ledger:ev-lines-v1:line;domain=" + bad)   # ... and the row is refused at the token


def test_only_the_two_builders_that_read_a_domain_may_declare_one():
    assert B.DOMAIN_BUILDERS == ("dense-line", "story")
    for ok in B.DOMAIN_BUILDERS:
        assert B.page_domain_spec("95,130", ok, "row") == BORN
    for bad in ("race", "share", "treemap", "tiers", "object", "combo", "decline"):
        with pytest.raises(ValueError, match="LINE or BARS page's y scale"):
            B.page_domain_spec("95,130", bad, "row")


def test_the_builder_bound_is_the_conservative_one_and_says_so():
    """The reviewer's third point: the engine's builder dispatch falls back to the bars builder for a kind it has no
    painter mapped for, so a page whose builder is `object` WOULD read the domain through that fall-back. Refusing
    it is the choice - a scale honoured by accident is a number no author can predict and no gate can read - and the
    code says that rather than claiming the two are the only builders that could ever read the key."""
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    block = src[src.index("DOMAIN_BUILDERS = ("):]
    block = block[:block.index("def page_domain_spec")]
    assert "CONSERVATIVE bound, not an exhaustive one" in block
    assert "falls back to the bars" in block and "`object`" in block


def test_the_born_domain_and_the_rescale_answer_to_ONE_builder_tuple():
    """`rescale_state` refuses anything but a line or a bars page; the born domain is the same door, so it reads
    the same tuple rather than a second copy of the pair."""
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    body = src[src.index("def rescale_state("):]
    body = body[:body.index("\ndef ", 10)]
    assert "if builder not in DOMAIN_BUILDERS:" in body, body[:400]
    assert '("dense-line", "story")' not in body, "one tuple, not two copies of it"


# ---- the page is BORN with it ---------------------------------------------------------------------------


def test_the_row_writes_the_domain_onto_the_pages_own_axes():
    td, ep = _ep()
    try:
        world = B.world_for_plate("ledger:ev-lines-v1:line;domain=95,130", (0, 0, 0), ep)
        assert world["kind"] == B.SPECIES_LEDGER
        assert world["page"]["axes"]["domain"] == BORN
        assert world["page"]["builder"] == "dense-line"
        assert "domain" not in world, "the option is consumed, never left on the world as a raw token"
    finally:
        td.cleanup()


def test_a_row_that_names_no_domain_writes_nothing_at_all():
    """The object's own domain stays the default: byte-identity for every page that came before this row."""
    td, ep = _ep()
    try:
        plain = B.world_for_plate("ledger:ev-lines-v1:line", (0, 0, 0), ep)
        assert "domain" not in plain["page"]["axes"]
        born = B.world_for_plate("ledger:ev-lines-v1:line;domain=95,130", (0, 0, 0), ep)
        del born["page"]["axes"]["domain"]
        assert born == plain, "the domain is the ONLY difference the token makes"
    finally:
        td.cleanup()


def test_an_object_that_declares_its_own_domain_is_overridden_by_the_row_and_nothing_else_moves():
    td, ep = _ep()
    try:
        own = dict(LINES, domain=[80.0, 400.0], ylabel="index")
        (ep / "evidence/objects/ev-own-v1.series.json").write_text(json.dumps(own), encoding="utf-8")
        world = B.world_for_plate("ledger:ev-own-v1:line;domain=95,130", (0, 0, 0), ep)
        assert world["page"]["axes"]["domain"] == BORN, "the ROW's word, on the row it is written on"
        assert world["page"]["axes"]["ylabel"] == "index", "and the object's other axes keys are untouched"
    finally:
        td.cleanup()


def test_the_bars_page_takes_a_born_domain_too():
    td, ep = _ep(then=True)
    try:
        world = B.world_for_plate("ledger:ev-bars-v1:bars;domain=0,400", (0, 0, 0), ep)
        assert world["page"]["builder"] == "story" and world["page"]["axes"]["domain"] == [0.0, 400.0]
    finally:
        td.cleanup()


def test_domain_on_a_race_page_is_refused_by_name():
    td, ep = _ep()
    try:
        race = {"title": "A race", "sub": "", "src": "the test bed", "unit": "",
                "periods": ["2020", "2021"],
                "series": [{"name": "A", "color": "crimson", "values": [1, 2]},
                           {"name": "B", "color": "teal", "values": [2, 1]}]}
        (ep / "evidence/objects/ev-race-v1.series.json").write_text(json.dumps(race), encoding="utf-8")
        with pytest.raises(ValueError, match="LINE or BARS page's y scale"):
            B.world_for_plate("ledger:ev-race-v1:race;domain=0,4", (0, 0, 0), ep)
    finally:
        td.cleanup()


def test_domain_is_refused_on_a_world_that_is_not_a_page():
    """A plate is a picture and carries no scale, so the row is refused by name rather than writing a number
    nothing will read - the same call `;drift=` makes on a page and `;field=` makes on a plate."""
    with pytest.raises(ValueError, match="domain= is a LEDGER PAGE option"):
        B.world_for_plate("vecmap;domain=0,1", (0, 0, 0), Path("."))


# ---- and the rescale off the born scale still works -----------------------------------------------------


def _rescale(at: float = 8.0, dur: float = 1.0) -> dict:
    return {"kind": "chart_to", "at": at, "dur": dur, "to": "rescale",
            "ymin": RESCALE_TO[0], "ymax": RESCALE_TO[1]}


def test_a_rescale_from_the_born_domain_derives_its_own_state_and_leaves_the_born_one_standing():
    td, ep = _ep()
    try:
        plate = "ledger:ev-lines-v1:line;domain=95,130"
        world = B.world_for_plate(plate, (0, 0, 0), ep)
        species = [_rescale()]
        B.derive_rescale_states(world, species, plate, ep)
        assert world["page"]["axes"]["domain"] == BORN, "the page it was born on"
        assert species[0]["state"] == 1
        assert world["page_states"][0]["axes"]["domain"] == RESCALE_TO, "and the state it moves to"
        assert world["page_states"][0]["derived"] == "rescale"
    finally:
        td.cleanup()


# ---- the frames: the ticks at 0.5 s are the ROW's domain's, not the object's -----------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# The live page's own scale and the y tick VALUES it wrote (`lpYTicks` records each label's value on its mark),
# read off the ACTIVE state - so a failure says which scale the page is standing on, not merely that it is wrong.
SCALE_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, S = (st.states && st.states[st.active | 0]) || st;
  return { active: st.active | 0, states: (st.states || []).length,
           y0: S.plot ? S.plot.y0 : null, y1: S.plot ? S.plot.y1 : null,
           ticks: (S.marks || []).filter((m) => m.role === "ylabel").map((m) => m.geom.v),
           labels: (S.marks || []).filter((m) => m.role === "ylabel").map((m) => m.el.textContent) };
}"""


def _born_player(domain, species=None, runtime: float = 20.0):
    from playwright.sync_api import sync_playwright
    td, ep = _ep()
    plate = "ledger:ev-lines-v1:line" + (";domain=%s" % domain if domain else "")
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    species = list(species or [])
    B.derive_rescale_states(world, species, plate, ep)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime],
                 world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[])
    html = ep / "born.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE["9:16"]
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
        return page.evaluate(SCALE_PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


@needs_browser
def test_the_page_opens_on_the_rows_domain_and_its_ticks_are_that_domains():
    """The row's own acceptance, on the frames: at 0.5 s - before any transition could legally fire - the page's
    scale IS [95, 130] and every y tick it wrote lies in it. The object's own scale (88 -> 312) is nowhere."""
    at, errs, close = _born_player("95,130")
    try:
        p = at(0.5)
        assert p["states"] == 0 or p["active"] == 0, p
        assert abs(p["y0"] - BORN[0]) < 1e-6 and abs(p["y1"] - BORN[1]) < 1e-6, ("the row's domain", p)
        assert p["ticks"], "the page wrote y ticks"
        assert min(p["ticks"]) >= BORN[0] - 1e-6 and max(p["ticks"]) <= BORN[1] + 1e-6, p["ticks"]
        # ... and they are NOT the object's own. Its scale (88 -> 312) writes ticks 50 apart - exactly ONE of them,
        # 100, lands in the row's range - so three or more ticks inside [95, 130] is a scale the object never had.
        assert len([v for v in p["ticks"] if v <= BORN[1]]) >= 3,             ("the object's own scale puts one tick in this range and the rest above it", p["ticks"])
        assert p["y1"] < DATA_HI - 100.0, ("the object's scale reaches 312 - the page is not on it", p)
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_the_same_page_with_no_domain_opens_on_the_objects_scale_which_is_the_default():
    """The control, and the byte-identity claim read on the frames: without the token nothing moved."""
    at, errs, close = _born_player(None)
    try:
        p = at(0.5)
        assert abs(p["y0"] - DATA_LO) < 0.5 and abs(p["y1"] - DATA_HI) < 0.5, ("the data's own range plus 6 %", p)
        assert max(p["ticks"]) > BORN[1], ("the object's scale reaches past the row's", p["ticks"])
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_a_rescale_off_the_born_domain_lands_on_the_scale_it_names():
    """R26-223's second half: the page is born on [95, 130] and the transition still works from there - the live
    scale is the born one before the word and the target's after it."""
    at, errs, close = _born_player("95,130", species=[_rescale(at=8.0, dur=1.0)])
    try:
        before = at(0.5)
        assert abs(before["y0"] - BORN[0]) < 1e-6 and abs(before["y1"] - BORN[1]) < 1e-6, before
        after = at(10.0)
        assert after["active"] == 1 and after["states"] == 2, after
        assert abs(after["y0"] - RESCALE_TO[0]) < 1e-6 and abs(after["y1"] - RESCALE_TO[1]) < 1e-6, \
            ("the scale the rescale names", after)
        assert min(after["ticks"]) >= RESCALE_TO[0] - 1e-6 and max(after["ticks"]) <= RESCALE_TO[1] + 1e-6, after
        back = at(0.5)
        assert back["ticks"] == before["ticks"], "a seek back is the play"
        assert not errs, errs
    finally:
        close()
