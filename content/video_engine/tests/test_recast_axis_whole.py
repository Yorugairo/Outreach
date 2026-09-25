"""P71 T3 (R26-310): a plain recast on the DEFAULT clock never stands a half-written tick on an empty plot.

E64's axis hand-over writes the arriving state's tick labels glyph by glyph over the back half of the recast's clock.
On the default clock (every page that is not `landscape-phone`) that write ran with no look at the plot, so a
half-written tick ("16", "320") stood on a plot with nothing on it:
  - the standing line was un-drawn to nothing before the recast (H row 4's `chart_to recast` at 93.34 s);
  - on a long-form page the plot READS empty from the clock's first frame: the arriving chart is raised with its opaque
    plot panel (`rect.lp-panel`) over the leaving one, whose data are still drawn beneath it (H row 22's flip, 663.02 s:
    the trim bars at full height under the monitor's panel).
The arriving labels are now written before the plot is empty, and over a plot that reads empty a label is placed whole
in its turn, never as a fragment.

Served through the real player, as test_chart_transitions / test_fed_axis_handoff are: the compiler builds the page
states, the player owns the clock. The landscape-phone path (PLAIN_AXIS_HANDOFF, `lineGone`) is guarded by
test_chart_transitions::test_plain_recast_holds_target_identity_until_outgoing_data_is_gone, and by the last test here.
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

FED_EP = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
LINE_OBJ, BARS_OBJ = "fed-on-rrp-history", "debt-wall-2025-2027"
LONG_LINE_TO_BARS = f"ledger:{LINE_OBJ}:line;then={BARS_OBJ}:bars;readability=longform"
LONG_BARS_TO_LINE = f"ledger:{BARS_OBJ}:bars;then={LINE_OBJ}:line;readability=longform"
PHONE_LINE_TO_BARS = f"ledger:{LINE_OBJ}:line;then={BARS_OBJ}:bars"   # the line object's own landscape-phone profile
PLAIN_LINE_TO_BARS = "ledger:line-v1:line;then=bars-v1:bars"          # the same data with no profile: the default page
XF_AT, XF_S = 11.0, 1.2
RUNTIME = 20.0
FPS = 60                     # finer than any render: a fragment between two frames is still a fragment
INK_GONE = 0.995             # the phone path's own `lineGone` test (dashoffset >= 0.995 len)

# the plot's standing line leaves to nothing on the word before the recast (H row 4, 92.44 + 0.8 s -> 93.34 s)
UNDRAW_THEN_RECAST = [
    {"kind": "undraw", "at": XF_AT - 1.0, "dur": 0.8, "target": {"kind": "datum", "index": 0}},
    {"kind": "chart_to", "at": XF_AT, "dur": XF_S, "to": "recast", "state": 1},
]
PLAIN_RECAST = [{"kind": "chart_to", "at": XF_AT, "dur": XF_S, "to": "recast", "state": 1}]
UNKEYED_RECAST = [{"kind": "chart_to", "at": XF_AT, "dur": XF_S, "to": "recast", "state": 1, "keyed": False}]

needs_objects = pytest.mark.skipif(
    not ((FED_EP / f"evidence/objects/{LINE_OBJ}.series.json").exists()
         and (FED_EP / f"evidence/objects/{BARS_OBJ}.series.json").exists()),
    reason="the Fed liquidity evidence objects are not on disk",
)


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = r"""() => {
  const el = [wA, wB].find(e => e && e.__lp && e.classList.contains('ledger'));
  const st = el.__lp, S = st.states || [st];
  const charts = [...document.querySelectorAll('svg.lp-chart')];
  const LAB = ['ylabel', 'rulelabel', 'xtick', 'axislabel'];
  const num = (v, d) => { const x = parseFloat(v); return Number.isFinite(x) ? x : d; };
  return { active: st.active | 0, xf: st.xfNow || null, readability: S.map(s => s.readability || ''), states: S.map(s => ({
    chart: num(s.chart && s.chart.style.opacity, 1),
    order: charts.indexOf(s.chart),
    panel: !!(s.chart && s.chart.querySelector('rect.lp-panel')),
    labels: (s.marks || []).filter(m => m.el && LAB.includes(m.role)).map(m => ({ role: m.role, key: String(m.key),
      text: m.el.textContent || '', full: m.el.__full == null ? null : m.el.__full, op: num(m.el.style.opacity, 1) })),
    paths: (s.paths || []).filter(pp => pp.p && !pp.muted).map(pp => ({ len: pp.len || 0,
      off: num(pp.p.getAttribute('stroke-dashoffset'), null) })),
    bars: (s.bars || []).map(bb => { const m = /scaleY\(([-\d.e]+)\)/.exec(bb.bar.style.transform || ''); return m ? +m[1] : 1; }),
  })) };
}"""


def _plain_ep(tmp: Path) -> Path:
    """A temp episode: the Fed line with its landscape-phone field dropped, and the bars - the DEFAULT page profile."""
    objs = tmp / "evidence/objects"
    objs.mkdir(parents=True)
    line = json.loads((FED_EP / f"evidence/objects/{LINE_OBJ}.series.json").read_text(encoding="utf-8"))
    line.pop("readability", None)
    (objs / "line-v1.series.json").write_text(json.dumps(line), encoding="utf-8")
    (objs / "bars-v1.series.json").write_text(
        (FED_EP / f"evidence/objects/{BARS_OBJ}.series.json").read_text(encoding="utf-8"), encoding="utf-8")
    return tmp


def _player(plate: str, species: list, ep: Path = FED_EP):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    with pytest.MonkeyPatch.context() as patch:   # the long form is the 16:9 page profile (a 9:16 row may not name it)
        patch.setattr(B, "ASPECT", "16:9")
        world = B.world_for_plate(plate, (0, 0, 0), ep)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, RUNTIME],
                 world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="16:9", runtime_s=RUNTIME, scenes=[scene], caption_pages=[], captions=[])
    uris = dict(uris, **B.longform_assets(timeline))   # the long form's face, as a build carries it
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "recast-axis-whole.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t;"
                      " s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


def _no_data_ink(s: dict) -> bool:
    """A state draws no data: its chart is hidden, or every line is un-drawn and every bar is flat."""
    if s["chart"] <= 0.01:
        return True
    lines_gone = all(p["off"] is None or p["off"] >= p["len"] * INK_GONE for p in s["paths"])
    bars_flat = all(b <= 1 - INK_GONE for b in s["bars"])
    return lines_gone and bars_flat


def _reads_empty(sample: dict, frm: int = 0, to: int = 1) -> bool:
    """Nothing of either state's data READS on the plot: none is drawn, or the arriving chart's opaque plot panel is
    raised above the leaving chart's data."""
    A, Bs = sample["states"][frm], sample["states"][to]
    covered = Bs["chart"] >= 0.99 and Bs["panel"] and Bs["order"] > A["order"]
    return (covered or _no_data_ink(A)) and _no_data_ink(Bs)


def _fragments(sample: dict, frm: int = 0, to: int = 1) -> list:
    """The arriving state's labels that stand PART-written (a strict prefix of their own string) on an empty plot."""
    Bs = sample["states"][to]
    if Bs["chart"] <= 0.01 or not _reads_empty(sample, frm, to):
        return []
    return [(lb["role"], lb["text"], lb["full"]) for lb in Bs["labels"]
            if lb["full"] and lb["text"] and lb["text"] != lb["full"] and lb["op"] > 0.01]


def _sweep(at) -> list:
    """Every sample from just before the clock to just after it, at FPS."""
    n = int(round((XF_S + 0.4) * FPS))
    return [dict(at(round(XF_AT - 0.1 + k / FPS, 4)), t=round(XF_AT - 0.1 + k / FPS, 4)) for k in range(n + 1)]


def _bad(samples: list) -> list:
    return [{"t": s["t"], "pu": round((s["t"] - XF_AT) / XF_S, 3), "labels": _fragments(s)[:4]}
            for s in samples if _fragments(s)]


@needs_objects
@needs_browser
def test_a_recast_over_an_undrawn_line_never_writes_a_fragment_on_the_empty_plot(tmp_path):
    """H row 4 at 93.34 (a default page): the line un-drew to nothing, then the page recast - the ticks stood half-written."""
    at, errs, close = _player(PLAIN_LINE_TO_BARS, UNDRAW_THEN_RECAST, _plain_ep(tmp_path))
    try:
        samples = _sweep(at)
        assert samples[0]["readability"][0] == "", "the default clock on the default page: no profile"
        mid = [s for s in samples if XF_AT < s["t"] < XF_AT + XF_S]
        assert mid and all(_no_data_ink(s["states"][0]) for s in mid), "the plot is empty through the whole clock"
        assert _bad(samples) == [], _bad(samples)
        after = at(XF_AT + XF_S + 0.2)
        assert all(lb["full"] is None or lb["text"] == lb["full"] for lb in after["states"][1]["labels"]), \
            "after the clock every arriving label is whole"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
@pytest.mark.parametrize("plate", [pytest.param(LONG_BARS_TO_LINE, id="bars_to_line_the_flip"),
                                   pytest.param(LONG_LINE_TO_BARS, id="line_to_bars")])
def test_a_long_form_recast_never_writes_a_fragment_under_the_arriving_panel(plate):
    """H row 22's flip: the arriving chart's panel covers the leaving data from the first frame - the plot reads empty,
    so no arriving tick may stand part-written on it."""
    at, errs, close = _player(plate, UNKEYED_RECAST)
    try:
        samples = _sweep(at)
        assert samples[0]["readability"][0] == "longform"
        early = [s for s in samples if XF_AT < s["t"] < XF_AT + 0.25 * XF_S]
        assert early and all(_reads_empty(s) for s in early), "the long form's arriving panel covers the leaving data"
        assert not all(_no_data_ink(s["states"][0]) for s in early), "... while they are still drawn beneath it"
        assert _bad(samples) == [], _bad(samples)
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_recast_whose_line_leaves_on_the_clock_writes_its_ticks_whole_while_the_line_still_stands(tmp_path):
    """On a default page the write is still a WRITE, glyph by glyph, while the leaving line shows - and it ends first."""
    at, errs, close = _player(PLAIN_LINE_TO_BARS, PLAIN_RECAST, _plain_ep(tmp_path))
    try:
        samples = _sweep(at)
        assert _bad(samples) == [], _bad(samples)
        inked = [s for s in samples if XF_AT < s["t"] < XF_AT + XF_S and not _reads_empty(s)]
        writing = [s for s in inked if any(lb["full"] and lb["text"] and lb["text"] != lb["full"]
                                          for lb in s["states"][1]["labels"])]
        assert writing, "over a standing line the arriving ticks are written glyph by glyph, not dropped in"
        whole_at = min(s["t"] for s in samples if s["t"] > XF_AT and s["states"][1]["labels"]
                       and all(lb["text"] == lb["full"] for lb in s["states"][1]["labels"] if lb["full"]))
        gone_at = min(s["t"] for s in samples if s["t"] > XF_AT and _no_data_ink(s["states"][0]))
        assert whole_at < gone_at, f"the ticks are whole at {whole_at} s, the line is gone at {gone_at} s"
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
@pytest.mark.parametrize("plate", [pytest.param(LONG_BARS_TO_LINE, id="long_form"),
                                   pytest.param(PLAIN_LINE_TO_BARS, id="default_page")])
def test_the_recast_hand_over_seeks_exactly(plate, tmp_path):
    """A pure function of t: a cold seek inside the hand-over lands the frame a warm one does."""
    ep = FED_EP if plate != PLAIN_LINE_TO_BARS else _plain_ep(tmp_path)
    at, _errs, close = _player(plate, UNDRAW_THEN_RECAST if plate == PLAIN_LINE_TO_BARS else UNKEYED_RECAST, ep)
    try:
        for t in (XF_AT + XF_S * 0.4, XF_AT + XF_S * 0.62, XF_AT + XF_S * 0.9, XF_AT + XF_S + 0.5):
            a = at(t)
            at(2.0)
            b = at(t)
            assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), t
    finally:
        close()


@needs_objects
@needs_browser
def test_the_landscape_phone_recast_keeps_its_own_late_hand_over():
    """The opt-in phone profile is not this path: its target axes stay hidden until the old line is gone (unchanged)."""
    at, errs, close = _player(PHONE_LINE_TO_BARS, PLAIN_RECAST)
    try:
        mid = at(XF_AT + XF_S * 0.65)
        assert mid["readability"][0] == "landscape-phone"
        assert mid["states"][1]["chart"] == 0, "the phone path holds the target's axes back while the line remains"
        assert not errs, errs
    finally:
        close()
