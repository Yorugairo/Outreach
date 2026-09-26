"""P72 T46b - the wave-3 follow-ups: the seal, the prop's owned exit, the verdict tile's credit, the stroke's width.

One section per backlog row (BACKLOG-HISTORY R26-361, R26-362, R26-391, R26-106 / R26-365 (a)):

  R26-361 THE SEAL'S GOLD FOLLOW-UPS
    (a) the stamped chip's NAME keyline reads the same latched ground as its gold (a bronze name in a charcoal keyline on
        a mid-tone photo read muddy - 1.57:1 between the two at the base);
    (b) the compiler's `seal_gold` twin reads a MEASURED ground as chip.mjs `sealGoldReport` does, and its contrast note
        reads the picture under the seal instead of the authored ink (a WARN, s106 - never a refusal);
    (c) `paint`'s world transform and `worldXfAt` are ONE function (`worldPoseAt`).
  R26-362 A PROP'S OWNED EXIT
    (a) `emit_choreography.py`'s mirror rule 2 no longer snaps a prop or a stamp onto the boundary (the engine's
        `dockOwnsExit`), and `authoring/shapes.py dock_leave` says so;
    (b) an owned exit whose curve runs past its page's end is ADVISED - a WARN naming the exit, the page's end and the
        curve (E99 s106: honoured, never refused).
  R26-391 THE VERDICT TILE'S TWO LEFT-OVERS
    (a) the motion gate credits a verdict tile landing on its word (T7's painter-credit pattern);
    (b) the seal refusal's message names the verdict tile P71 T19 built (the pin in test_stamp_is_a_seal moves with it).
  R26-106 / R26-365 (a) THE STROKE'S WIDTH PROFILE
    `strokeAt` has a caller: under the new `stroke_width` flag a hand-drawn species (callout, squiggle, underline) is a
    filled OUTLINE regrown from the drawn prefix each frame, its width kinetics/stroke.mjs's `prof.w`; flag off, the
    dash-offset branch is byte-identical (the goldens).
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import emit_choreography as EC  # noqa: E402
import gate_motion_density as G  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener
from authoring import shapes as SH  # noqa: E402

CHIP = ROOT / "content/video_engine/scripts/species/chip.mjs"
STROKE = ROOT / "content/video_engine/scripts/kinetics/stroke.mjs"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
GPU = "prop-icon-gpu-ai-accelerator-v1"
CREAM, CHARCOAL = "#F4E6C7", "#25313C"


def _node(src: str):
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def _lum(hex_: str) -> float:
    c = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _ratio(a: str, b: str) -> float:
    x, y = _lum(a), _lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


# ================================================================== R26-361 (a) the name's keyline
PAINT_NAME = """
const C = await import(%(chip)s);
const lum = (hex) => [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(c=>c<=0.04045?c/12.92:Math.pow((c+0.055)/1.055,2.4)).reduce((a,c,i)=>a+c*[0.2126,0.7152,0.0722][i],0);
const out = [];
for (const [ground, ink, arrive] of %(cases)s) {
  const sp = { kind: "chip", form: "stamp", arrive, at: 4, dur: 6, size: 260, ink, icon: %(gpu)s, label: "NVIDIA",
               target: { kind: "point", x: 0.5, y: 0.5 } };
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [] }; made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  const ctx = { sp, t: 5.5, sc: { world: { asset_id: "plate-x" } }, svg: { kids: [] }, el, A: { ["prop:" + sp.icon]: "data:," },
    resolveTarget: () => ({ x: 960, y: 540, w: 0, h: 0 }), hash: () => .5, idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 };
  if (ground) ctx.groundLumThen = (pts) => pts.map(() => lum(ground));
  C.paintChip(ctx);
  const st = made.find((e) => e.cls === "chipstamplab").at.style;
  out.push({ fill: /fill:(#[0-9A-Fa-f]{6})/.exec(st)[1], key: /stroke:(#[0-9A-Fa-f]{6})/.exec(st)[1] });
}
console.log(JSON.stringify(out));
"""


def _names(cases: list[tuple]) -> list[dict]:
    return _node(PAINT_NAME % {"chip": json.dumps(CHIP.as_uri()), "cases": json.dumps(cases), "gpu": json.dumps(GPU)})


# (the ground measured under the seal - None when nothing was -, the row's authored `ink`, the keyline owed)
KEYLINE_CASES = [
    ("#9A9A9A", "cream", CREAM),       # a mid-tone photo: the gold goes bronze, so the name's keyline is the LIGHT one
    ("#C8C0B0", "cream", CREAM),       # a light photo: the same
    ("#3A3530", "cream", CHARCOAL),    # a dark photo: the gold holds as it is, on the dark keyline (as the base)
    ("#25313C", "cream", CHARCOAL),    # the charcoal ground (as the base)
    ("#F4E6C7", "charcoal", CREAM),    # the cream page, authored charcoal (as the base)
    ("#3A3530", "charcoal", CHARCOAL),  # authored charcoal on a DARK photo: the latched ground, not the authored ink, decides
    (None, "cream", CHARCOAL),         # nothing measured (node): the authored ink's keyline, byte for byte
    (None, "charcoal", CREAM),
]


def test_r26_361a_the_seals_name_keyline_reads_the_latched_ground():
    got = _names([(g, ink, "stamp") for g, ink, _k in KEYLINE_CASES])
    wrong = [f"ground {g} ink {ink}: name {n['fill']} on keyline {n['key']}, owed keyline {k}"
             for (g, ink, k), n in zip(KEYLINE_CASES, got) if n["key"] != k]
    assert not wrong, "the name's keyline does not read the ground the gold latched: " + "; ".join(wrong)


def test_r26_361a_on_every_measured_ground_the_keyline_holds_the_name_off_it():
    measured = [c for c in KEYLINE_CASES if c[0]]
    got = _names([(g, ink, "stamp") for g, ink, _k in measured])
    weak = [f"ground {g}: name {n['fill']} vs keyline {n['key']} {_ratio(n['fill'], n['key']):.2f}:1"
            for (g, _i, _k), n in zip(measured, got) if _ratio(n["fill"], n["key"]) < 3.0]
    assert not weak, "a keyline that does not separate the name from it is mud: " + "; ".join(weak)


def test_r26_361a_an_unstamped_stamp_form_keeps_its_keyline():
    got = _names([("#9A9A9A", "cream", None), ("#9A9A9A", "charcoal", None)])
    assert [n["key"] for n in got] == [CHARCOAL, CREAM], got


# ================================================================== R26-361 (b) the compiler's twin and its note
GROUNDS = [[0.3231], [0.28, 0.30, 0.33, 0.373], [0.035], [0.79], [0.02, 0.9], [0.2, None, 0.25], []]


def test_r26_361b_the_compilers_seal_gold_report_is_chip_mjs_on_a_measured_ground():
    js = _node(f"""const C = await import({json.dumps(CHIP.as_uri())});
      console.log(JSON.stringify({json.dumps(GROUNDS)}.map((g) => C.sealGoldReport(g))));""")
    for g, want in zip(GROUNDS, js):
        got = B.seal_gold_report(g)
        assert got["ink"] == want["ink"] and got["n"] == want["n"] and got["holds"] == want["holds"], (g, got, want)
        if want["worst"] is not None:
            assert abs(got["worst"] - want["worst"]) < 1e-9 and abs(got["min"] - want["min"]) < 1e-12, (g, got, want)


def test_r26_361b_seal_gold_with_no_ground_is_the_authored_ink_as_it_was():
    assert B.seal_gold({"ink": "cream"}) == ("#E8B86D", CHARCOAL)
    assert B.seal_gold({"ink": "charcoal"}) == ("#A07F4B", CREAM)


def _stamp(**extra) -> dict:
    return {"kind": "chip", "form": "stamp", "arrive": "stamp", "at": 10.0, "dur": 6.0, "icon": GPU, "label": "NVIDIA",
            "target": {"kind": "point", "x": 0.5, "y": 0.5}, **extra}


def _plate(tmp: Path, name: str, split: bool, grey: int = 150) -> Path:
    """`split`: black, a mid-grey band and white under one seal - no ink holds 3:1 on all three (a mid ink holds on
    black and white alone: it is the band between them that no ink can clear)."""
    from PIL import Image
    im = Image.new("RGB", (1920, 1080), (grey, grey, grey))
    if split:
        im.paste((5, 5, 5), (0, 0, 920, 1080))
        im.paste((118, 118, 118), (920, 0, 1000, 1080))
        im.paste((250, 250, 250), (1000, 0, 1920, 1080))
    p = tmp / f"{name}.png"
    im.save(p)
    return p


def _fit_on(monkeypatch, tmp: Path, split: bool):
    plate = _plate(tmp, "plate-t46b", split)
    monkeypatch.setattr(B.R, "find_asset", lambda name: plate if name == "plate-t46b" else None)
    paint = B.painted_box(B.catalogue_stamp_asset(GPU)["file"])
    return B.chip_stamp_ring_fit(_stamp(), {"asset_id": "plate-t46b", "ken_burns": {"scale": 0, "x": 0, "y": 0}},
                                 "16:9", paint, where="row 9 chip")


def test_r26_361b_the_seal_note_reads_the_picture_under_the_seal(monkeypatch, tmp_path):
    _out, notes = _fit_on(monkeypatch, tmp_path, split=True)
    seal = [n for n in notes if "seal's gold" in n]
    assert len(seal) == 1, notes
    assert "the picture under it" in seal[0] and "3:1" in seal[0] and "read the frame" in seal[0], seal[0]


def test_r26_361b_a_picture_the_gold_holds_on_says_nothing(monkeypatch, tmp_path):
    _out, notes = _fit_on(monkeypatch, tmp_path, split=False)
    assert not [n for n in notes if "seal's gold" in n], notes


def test_r26_361b_the_note_is_advice_the_fit_is_returned(monkeypatch, tmp_path):
    out, _notes = _fit_on(monkeypatch, tmp_path, split=True)
    assert out["seal_r"] > 0 and "ring_to" in out   # s106: a WARN, never a refusal


# ================================================================== R26-361 (c) paint through worldXfAt
def test_r26_361c_paint_and_worldXfAt_build_the_world_transform_in_one_function():
    src = ENGINE.read_text(encoding="utf-8")
    assert src.count("const worldPoseAt = (scene, t, dx = 0) => {") == 1, "the one function"
    assert src.count("`translateX(${dx.toFixed(1)}px) scale(${z.toFixed(4)}) `") == 1, "the world's rest string, ONCE"
    assert "`translateX(${(0).toFixed(1)}px) scale(" not in src, "worldXfAt's mirrored copy is gone"
    paint = src[src.index("const paint = (el, scene, dx = 0) => {"):src.index("paintPlanes(el, plies, camXfNow")]
    assert "= worldPoseAt(scene, t, dx);" in paint and "kenProgress(" not in paint, "paint reads the pose, not a copy of it"
    xf = src[src.index("const worldXfAt = "):src.index("const cssMatrix = ")]
    assert "const P = worldPoseAt(scene, t0);" in xf and "kenProgress(" not in xf, "worldXfAt reads the same function"


# ================================================================== R26-362 (a) the choreography mirror
SHOT_TABLE = """W = [
    (0.0, 20.0, "plate-a", (0, 0, 0), [("dock-card", 1, 5.0, 19.0), ("dock-prop", 2, 6.0, 19.7, {"prop": True}),
                                       ("dock-stamp", 1, 12.0, 19.3, {"arrive": "stamp"})]),
    (20.0, 40.0, "plate-b", (0, 0, 0), []),
]
"""


def test_r26_362a_the_choreography_mirror_honours_an_owned_exit(monkeypatch, tmp_path):
    (tmp_path / "SHOT-TABLE-F.py").write_text(SHOT_TABLE, encoding="utf-8")
    (tmp_path / "timeline.json").write_text(json.dumps({"runtime_s": 40.0}), encoding="utf-8")
    monkeypatch.setattr(EC, "EP", tmp_path)
    monkeypatch.setattr(EC, "BUILD", tmp_path)
    _scenes, docks, _w, _rt = EC.load_model()
    exits = {d["slide"]: d["exit"] for d in docks}
    assert exits["dock-card"] == 20.0, "a CARD still rides the turn (the player's snap)"
    assert exits["dock-prop"] == 19.7 and exits["dock-stamp"] == 19.3, f"a prop / a stamp owns its exit: {exits}"


def test_r26_362a_dock_leave_says_a_prop_owns_its_exit():
    doc = SH.dock_leave.__doc__
    assert "owns its exit" in doc and "P71 T6" in doc, doc


# ================================================================== R26-362 (b) the curve past the page
def _dock(slide, exitt, arrive=None, prop=False, handed=False) -> tuple[dict, dict]:
    d = {"slide": slide, "slot": 1, "enter": 5.0, "exit": exitt, **({"arrive": arrive} if arrive else {}),
         **({"kind": "prop"} if prop else {}), **({"handed": True} if handed else {})}
    return d, ({"kind": "prop"} if prop else {})


@pytest.mark.parametrize("exitt, arrive, prop, owed", [
    (19.7, "stamp", True, True),     # the row's case: 0.3 s lead, a 0.533 s curve -> 0.233 s over the next page
    (19.5, "stamp", False, True),    # a DOCK stamp (no prop): a 0.5 s lead is inside its 0.533 s curve (ends 20.033)
    (19.8, None, True, True),        # a spring prop's 0.35 s retract from 19.8 ends 20.15
    (19.6, None, True, False),       # ... from 19.6 it ends 19.95, before the page's end
    (19.0, None, False, False),      # a CARD is snapped to the turn and carried off: not an owned exit
    (20.0, "stamp", True, False),    # an exit ON the page's end is the turn's (swept / dipped), no curve past it
    (18.0, "stamp", True, False),    # the whole curve fits
])
def test_r26_362b_an_owned_exit_whose_curve_runs_past_its_page_is_advised(exitt, arrive, prop, owed):
    d, ev = _dock("dock-x", exitt, arrive, prop)
    notes = B.owned_exit_notes([d], {"dock-x": ev}, 20.0, "shot row 7 (0.0-20.0s)")
    assert bool(notes) == owed, (exitt, arrive, prop, notes)
    if owed:
        n = notes[0]
        assert "dock-x" in n and f"{exitt:.2f}" in n and "20.00" in n and "E99 s106" in n, n
        curve = B.STAMP_EXIT_S if arrive == "stamp" else B.PROP_RETRACT_S
        assert f"{curve:.2f}" in n and f"{exitt + curve - 20.0:.2f}" in n and "20.10" in n, n


def test_r26_362b_a_handed_prop_leaves_on_its_morph_not_its_curve():
    d, ev = _dock("dock-x", 19.7, "stamp", True, handed=True)
    assert B.owned_exit_notes([d], {"dock-x": ev}, 20.0, "row") == []


def test_r26_362b_the_build_prints_the_advice_and_never_refuses():
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert "owned_exit_notes(docks, evidence, b," in src
    assert 'print(f"  [WARN] P72 T46b: {_w}")' in src


def test_r26_362b_the_compilers_curves_are_the_engines():
    src = ENGINE.read_text(encoding="utf-8")
    assert "DOCK_RETRACT_S = %s;" % f"{B.PROP_RETRACT_S:g}" in src, "the spring prop's retract is the engine's"


# ================================================================== R26-391 (a) the verdict tile's credit
def _tile_tl(verdict, enter=5.0, exitt=20.0) -> dict:
    return {"aspect": "16:9", "scenes": [{"scene_id": "s01", "span": [0.0, 30.0], "world": {"asset_id": "p"},
            "docks": [{"slide": "dock-tile", "slot": 1, "enter": enter, "exit": exitt, "verdict": verdict}], "species": []}],
            "evidence": {"dock-tile": {"chart": {"series": [[1, 2]], "src": "x"}}}}


@pytest.mark.parametrize("state", ["tick", "cross", "buy", "sell"])
def test_r26_391a_a_verdict_landing_on_its_word_is_credited(state):
    events, line = G._credited_beats(_tile_tl({"state": state, "at": 12.4}))
    assert 12.4 in events, events
    assert "verdict tile 1 landing(s) (dock-tile)" in line, line


def test_r26_391a_a_verdict_off_the_stage_is_not_credited():
    events, _line = G._credited_beats(_tile_tl({"state": "tick", "at": 25.0}))
    assert 25.0 not in events, events


@pytest.mark.parametrize("bad", [{"state": "win", "at": 12.4}, {"state": "tick"}, "tick"])
def test_r26_391a_a_malformed_verdict_is_refused_by_name_and_credits_nothing(bad):
    events, line = G._credited_beats(_tile_tl(bad))
    assert events == [] and "dock-tile: verdict refused" in line, (events, line)


def test_r26_391a_a_build_with_no_verdict_is_the_report_it_was():
    tl = _tile_tl(None)
    del tl["scenes"][0]["docks"][0]["verdict"]
    assert G._credited_beats(tl) == ([], None)


# ================================================================== R26-391 (b) the seal refusal's message
def test_r26_391b_the_seal_refusal_names_the_verdict_tile_it_is_not():
    with pytest.raises(ValueError) as exc:
        B.dock_opts({"arrive": "stamp", "ring_text": "AUDITED"})
    msg = str(exc.value)
    assert "no dock payload is a badge or a verdict today" not in msg, msg
    assert "a chart card's `verdict` tile (P71 T19)" in msg and "never a seal" in msg, msg


# ================================================================== R26-106 / R26-365 (a) the stroke's width
def test_r26_365a_strokeAt_has_a_caller():
    src = ENGINE.read_text(encoding="utf-8")
    assert src.count("strokeAt(") >= 1, "strokeAt is defined (`strokeAt = (`) and never called: nothing draws prof.w"


def test_r26_365a_the_outline_is_the_width_profile_in_node():
    got = _node(f"""const S = await import({json.dumps(STROKE.as_uri())});
      const line = []; for (let i = 0; i <= 40; i++) line.push({{ x: i * 10, y: 0 }});
      const hook = []; for (let i = 0; i <= 30; i++) hook.push({{ x: i * 8, y: 0 }});   /* a straight, then a half turn */
      for (let i = 1; i <= 30; i++) {{ const a = Math.PI * i / 30; hook.push({{ x: 240 + 30 * Math.sin(a), y: 30 - 30 * Math.cos(a) }}); }}
      const out = {{}};
      for (const [k, pts] of [["line", line], ["hook", hook]]) {{
        const prof = S.strokeProfile(pts), L = prof.L, part = S.strokeWidths(prof, pts, L * 0.6, 4), all = S.strokeWidths(prof, pts, L, 4);
        let area = 0; for (let i = 1; i < all.pts.length; i++) area += (prof.s[i] - prof.s[i - 1]) * (all.hw[i - 1] + all.hw[i]);
        out[k] = {{ L, n: part.pts.length, s: part.s, last: part.pts[part.pts.length - 1], hw: all.hw, mean: area / L,
                   poly: S.strokeOutline(part.pts, part.hw).length }};
      }}
      console.log(JSON.stringify(out));""")
    line, hook = got["line"], got["hook"]
    assert abs(line["s"] - 0.6 * line["L"]) < 1e-9 and abs(line["last"]["x"] - 0.6 * line["L"]) < 1e-6, line
    assert max(line["hw"]) - min(line["hw"]) < 1e-9 and abs(line["hw"][0] - 2.0) < 1e-9, "a straight stroke is its authored width"
    assert abs(hook["mean"] - 4.0) < 1e-9, "the whole stroke carries the authored weight (its mean width)"
    assert min(hook["hw"][35:55]) > max(hook["hw"][2:25]) * 1.05, "the ink pools in the curve, out of the straight"
    assert line["poly"] == 2 * line["n"], "the outline walks one side out and the other back"


@pytest.fixture(scope="module")
def browser():
    with SP.browser() as br:
        yield br


BRUSH_PROBE = """() => {
  const b = [...document.querySelectorAll('path.hand-brush')], co = document.querySelector('path.co');
  return { n: b.length, cls: b.map((x) => x.getAttribute('class')), fill: b.map((x) => x.style.fill), stroke: b.map((x) => x.style.stroke),
           wmin: b.map((x) => +x.dataset.wMin), wmax: b.map((x) => +x.dataset.wMax), drawn: b.map((x) => +x.dataset.drawn),
           len: co ? co.getTotalLength() : null, vis: co ? getComputedStyle(co).visibility : null,
           sw: co ? parseFloat(getComputedStyle(co).strokeWidth) : null };
}"""


def _callout_at(browser, t: float, kinetics: dict) -> dict:
    tl, uris, _t, aspect = RB.load_surface("chart-callout")
    tl = dict(tl, kinetics=kinetics)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        srv, port = RB.serve(html.parent)
        page = browser.new_context(viewport={"width": w, "height": h}).new_page()
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        try:
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                          "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
            got = page.evaluate(BRUSH_PROBE)
        finally:
            page.context.close(); srv.shutdown()
    assert not errs, errs
    return got


@pytest.mark.parametrize("flags", [{"stroke_width": True}, {"stroke_width": True, "curvature_stroke": True}])
def test_r26_365a_under_the_flag_the_callout_is_a_filled_outline_of_its_width_profile(browser, flags):
    got = _callout_at(browser, 10.3, flags)
    assert got["n"] == 1, got
    assert got["stroke"] == ["none"] and got["fill"][0], got
    assert got["vis"] == "hidden", "the centreline is the outline's guide, never ink"
    assert got["wmax"][0] > got["wmin"][0] * 1.02, f"the width is a profile, not a constant: {got}"
    assert 0 < got["drawn"][0] < got["len"], "mid-draw: the outline is the drawn prefix"
    whole = _callout_at(browser, 11.0, flags)
    assert whole["drawn"][0] == pytest.approx(whole["len"], abs=0.05), whole
    assert whole["wmin"][0] < whole["sw"] < whole["wmax"][0], f"the authored width is the stroke's mean, the profile about it: {whole}"


def test_r26_365a_flag_off_draws_no_brush(browser):
    got = _callout_at(browser, 10.3, {"curvature_stroke": True})
    assert got["n"] == 0, got
