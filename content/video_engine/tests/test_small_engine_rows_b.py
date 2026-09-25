"""P72 T27 (the second half) - the small engine rows, one test group per row, in the order they were committed (the
first half's rows are test_small_engine_rows.py). Each group's header names its row and its ruling.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as BST  # noqa: E402
import build_golden_sources as G  # noqa: E402
import render_baseline as RB  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CHECKLIST = ROOT / "content/video_engine/scripts/species/checklist.mjs"
DROP = ROOT / "content/video_engine/scripts/kinetics/drop.mjs"
TAG = r"\[(?:DERIVED: |MEASURED: |UNSOURCED - )"


def _chromium_available() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _render(tl: dict, uris: dict, times: list[float], probe: str | None = None) -> list[tuple[bytes, object]]:
    """(png, probe result) at each instant, on one served page (the golden's own capture: a pure function of t)."""
    import served_player as SP
    w, h = RB.STAGE[tl.get("aspect") or "16:9"]
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t27b.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, w, h) as (page, errs):
            for t in times:
                png = RB.frame_png(page, t, (w, h))
                out.append((png, page.evaluate(probe) if probe else None))
            assert not errs, errs
    return out


# ---- R26-9 TR-3: the transition numbers carry their sources ------------------------------------------------------

def _transitions_region() -> str:
    src = ENGINE.read_text(encoding="utf-8")
    a = src.index("  const WIPE = ")
    a = src.rindex("/* P72 T27 / R26-9 TR-3", 0, a) if "/* P72 T27 / R26-9 TR-3" in src[:a] else a
    b = src.index("\n", src.index("  const SLIDE_S = "))
    return src[a:b]


def _declared(region: str) -> list[str]:
    names: list[str] = []
    for line in region.splitlines():
        m = re.match(r"\s*const ([A-Z][A-Z0-9_]* = -?[\d.]+(?:, [A-Z][A-Z0-9_]* = -?[\d.]+)*);", line)
        if m:
            names += re.findall(r"([A-Z][A-Z0-9_]*) = ", m.group(1))
    return names


def test_the_transitions_region_declares_the_numbers_the_plan_names() -> None:
    names = _declared(_transitions_region())
    for n in ("WIPE", "DISSOLVE_S", "MOUNT_STEPS", "SUCK_S", "SUCK_TURN", "DIP_S", "BLURZOOM_S", "BLURZOOM_SCALE",
              "BLURZOOM_BLUR", "BLURZOOM_IN", "SLIDE_S"):
        assert n in names, (n, names)


def test_every_transition_constant_carries_a_source_tag() -> None:
    """E42 D6: a shipped number carries its tag - `NAME <value> [DERIVED: ...]`, `[MEASURED: ...]` or `[UNSOURCED - ...]`."""
    region = _transitions_region()
    untagged = [n for n in _declared(region)
                if not re.search(rf"\b{n}\b(?:\s+-?[\d.]+)?\s+{TAG}", region)]
    assert untagged == [], f"transition constants with no source tag: {untagged}"


# ---- R26-302: a checklist column waits for its own instant --------------------------------------------------------

def _card_chart(at=None) -> tuple[dict, dict, dict]:
    tl, uris = G.test_card()
    chart = next(iter(tl["evidence"].values()))["chart"]
    if at is not None:
        chart["checklist"]["at"] = at
    return tl, uris, chart


@pytest.mark.parametrize("at, says", [
    ("6.0", r"checklist: `at` must be a list of one instant per column"),
    ([None, None, 6.0], r"checklist: `at` names 3 columns, the head 4"),
    ([None, None, None, -1.0], r"checklist: `at` column 4 is -1.0"),
    ([None, None, None, True], r"checklist: `at` column 4 is True"),
    ([None, None, None, "6"], r"checklist: `at` column 4 is '6'"),
    ([None, None, None, float("nan")], r"checklist: `at` column 4 is nan"),
])
def test_a_malformed_column_at_is_refused_by_name(at, says) -> None:
    _, _, chart = _card_chart(at)
    problems = BST.checklist_problems(chart)
    assert problems and re.search(says, " | ".join(problems)), problems
    with pytest.raises(ValueError, match=r"ev-x: checklist: `at`"):
        BST.check_checklist("ev-x", chart)


def test_a_good_column_at_and_none_both_pass() -> None:
    assert BST.checklist_problems(_card_chart()[2]) == []
    assert BST.checklist_problems(_card_chart([None, None, None, 6.0])[2]) == []
    assert BST.checklist_problems(_card_chart([0, 1.5, None, 6])[2]) == []


def _node(js: str) -> object:
    url = CHECKLIST.resolve().as_uri()
    code = f"import * as C from {json.dumps(url)};\n{js}"
    r = subprocess.run(["node", "--input-type=module", "-e", code], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_the_cell_clock_waits_for_its_column_and_is_the_old_clock_without_one() -> None:
    got = _node("""
      const V = C.CHECKLIST, clk = (t, d, k, at) => C.checklistCellClock(t, d, k, false, V, at);
      console.log(JSON.stringify({
        plain: [clk(5, 1, 3), clk(5, 1, 3, null), clk(5, 1, 3, undefined)],
        waits: clk(5, 1, 3, 6), after: clk(7, 1, 3, 6), early: clk(5, 4, 3, 2),
        recap: C.checklistCellClock(5, 1, 3, true, V, 6)}));""")
    assert got["plain"] == [5 - 1 - 1.6] * 3, got          # no `at`: tRel - rowDelay - OFFS[k], as it always was
    assert got["waits"] == pytest.approx(-1.0), got           # the column's instant is later than the row's: it waits
    assert got["after"] == pytest.approx(1.0), got
    assert got["early"] == pytest.approx(5 - 4 - 1.6), got    # an instant BEFORE the row's own clock never draws early
    assert got["recap"] == pytest.approx(-1.0), got           # ... on a recap too


def test_the_engine_carries_the_species_column_clock() -> None:
    src = ENGINE.read_text(encoding="utf-8")
    assert "const checklistCellClock = (tRel, rowDelay, k, recap, V = CHECKLIST, at = null) => {" in src
    assert "checklistCellClock(tRel, rowDelay, k, recap, V, c.at)" in src


# every cell of the test card's rows: its text, its column and the opacity its group carries
CELLS = """() => [...document.querySelectorAll('.dock svg.chartbox text.cs')].map((e) => ({
  text: e.textContent, fill: e.getAttribute('fill'), o: +(e.parentNode.getAttribute('opacity') || 1) }))"""


@needs_browser
def test_the_paper_column_writes_on_its_own_instant() -> None:
    """Row 20's defect on the golden card: the Believed column waits for its word at tRel 6.0 (t 8.45 on this card's
    clock - enter 2.0 + CARD_IN x 0.6). Before it, row 1's answer (+1.6 on its row, long due) is not on the card;
    after it, it is; every other cell reads exactly as the card without `at`."""
    tl0, uris, _ = _card_chart()
    tl1, _, _ = _card_chart([None, None, None, 6.0])
    t_before, t_after = 2.45 + 6.0 - 0.05, 2.45 + 6.0 + 0.40
    base = [p for _, p in _render(tl0, uris, [t_before, t_after], CELLS)]
    colat = [p for _, p in _render(tl1, uris, [t_before, t_after], CELLS)]
    believed = G.test_card()[0]["evidence"]["ev-golden-test-card"]["chart"]["checklist"]["rows"][0]["cells"][3]
    pick = lambda cells, txt: next(c for c in cells if c["text"] == txt)   # noqa: E731
    assert pick(base[0], believed)["o"] == 1, base[0]                       # the card without `at`: already written
    assert pick(colat[0], believed)["o"] == 0, colat[0]                     # with it: waiting for its instant
    assert pick(colat[1], believed)["o"] == 1, colat[1]                     # ... and written after it
    others = lambda cells: [c for c in cells if c["fill"] != "#ff8a8c"]    # noqa: E731 - every column but Believed
    assert others(colat[0]) == others(base[0]) and others(colat[1]) == others(base[1])


# ---- R26-257: the prism takes the stage light ------------------------------------------------------------------------

def _drop_light_deg() -> float:
    m = re.search(r"^\s*LIGHT_DEG:\s*(-?[\d.]+),", DROP.read_text(encoding="utf-8"), re.M)
    assert m, "kinetics/drop.mjs states DROP.LIGHT_DEG"
    return float(m.group(1))


def test_the_prism_light_is_the_stage_light() -> None:
    src = ENGINE.read_text(encoding="utf-8")
    block = src.split("const EXTRUDE = {", 1)[1].split("};", 1)[0]
    assert re.search(r"^\s*LIGHT_DEG: DROP\.LIGHT_DEG,", block, re.M), "the prism's light is DROP's, not its own number"
    assert re.search(r"^\s*VIEW_DEG: 35,", block, re.M), "the depth direction is the view's own dial"


PRISMS = """() => {
  const svg = [...document.querySelectorAll('svg')].find((s) => s.querySelector('.bx-shadow'));
  if (!svg) return [];
  const pts = (e) => e.getAttribute('points').trim().split(/\\s+/).map((p) => p.split(',').map(Number));
  const bars = [...svg.querySelectorAll('rect.bar')], shadows = [...svg.querySelectorAll('.bx-shadow')];
  return shadows.map((s, i) => { const b = bars[i];
    return { shadow: pts(s), x: +b.getAttribute('x'), y: +b.getAttribute('y'), w: +b.getAttribute('width'),
             h: +b.getAttribute('height'), neg: b.classList.contains('neg') }; });
}"""


@needs_browser
def test_the_cast_shadow_falls_away_from_the_stage_light() -> None:
    """Measured on the golden's own polygons: each positive bar's shadow is thrown from its face along
    DROP.LIGHT_DEG + 180 (down and to the right, as the drop, the melt, a card's lift and a prop's rest are)."""
    tl, uris = G.SURFACES["form-extruded-bar"]()
    [(_, prisms)] = _render(tl, uris, [G.FRAME_T["form-extruded-bar"]], PRISMS)
    pos = [p for p in prisms if not p["neg"] and p["h"] > 40]
    assert len(pos) >= 3, prisms
    want = (_drop_light_deg() + 180) % 360
    for p in pos:
        sx, sy = p["shadow"][0][0] - p["x"], p["shadow"][0][1] - p["y"]
        got = math.degrees(math.atan2(sy, sx)) % 360
        assert abs(got - want) < 1.0, (round(got, 2), want, p)


# ---- R26-2: the harmonisation pass on a composited cutout -----------------------------------------------------------

HEAD = ROOT / "content/video_engine/tests/golden/inputs/head_bessent_cutout.png"
GROUND = "#2b343c"   # the golden's plate-plain (43, 52, 60): the ground the sprite sits on, named by the build


def test_the_harmonise_dial_is_named_and_off_by_default() -> None:
    src = ENGINE.read_text(encoding="utf-8")
    dials = src.split("const KINETICS_DIALS = Object.freeze({", 1)[1].split("});", 1)[0]
    assert re.search(r"^\s*harmonise: \"", dials, re.M), "named in KINETICS_DIALS (a dial, not a capability flag)"
    defaults = src.split("const KINETICS_DEFAULTS = Object.freeze({", 1)[1].split("});", 1)[0]
    assert "harmonise" not in defaults
    assert "const HARMONISE = Object.freeze({" in src and 'feTurbulence' in src


@pytest.mark.parametrize("bad", ["cream", "#f4e6c", "f4e6c7", 1, None])
def test_the_compiler_refuses_a_malformed_harmonise_by_name(bad, monkeypatch) -> None:
    monkeypatch.setattr(BST, "KINETICS", {"harmonise": bad})
    with pytest.raises(ValueError, match=r"KINETICS\['harmonise'\] is .* it must be true \(the cream ground\), false or a #rrggbb"):
        BST.build_kinetics()


def test_the_compiler_passes_the_three_good_forms(monkeypatch) -> None:
    for v in (True, False, GROUND):
        monkeypatch.setattr(BST, "KINETICS", {"harmonise": v})
        assert BST.build_kinetics()["harmonise"] == v
    monkeypatch.setattr(BST, "KINETICS", {})
    assert "harmonise" not in BST.build_kinetics(), "absent is absent - no build carries the dial unless it asks"


IMG_BOX = """() => { const st = document.getElementById('stage').getBoundingClientRect();
  const im = document.querySelector('.dock.cutout .slide-frame img'); if (!im) return null;
  const r = im.getBoundingClientRect();
  return { x: r.x - st.x, y: r.y - st.y, w: r.width, h: r.height, filter: getComputedStyle(im).filter }; }"""


def _lum(img):
    import numpy as np
    a = np.asarray(img.convert("RGB"), dtype=np.float64)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def harmonise_measure(png_off: bytes, png_on: bytes, box: dict, ground: str = GROUND) -> dict:
    """The acceptance's two numbers on one frame pair: the edge ring's mean distance to the ground (off, on) and the
    interior's grain (the std of on/off - 1, and its mean). The ring is the cutout's alpha edge, 6 px deep, above
    its foot fade; the interior is 14 px inside it."""
    import io
    import numpy as np
    from PIL import Image, ImageFilter
    off, on = (Image.open(io.BytesIO(p)).convert("RGB") for p in (png_off, png_on))
    x, y, w, h = (int(round(box[k])) for k in ("x", "y", "w", "h"))
    alpha = Image.open(HEAD).convert("RGBA").getchannel("A").resize((w, h), Image.BILINEAR)
    solid = alpha.point(lambda v: 255 if v > 128 else 0)
    core6, core14 = (solid.filter(ImageFilter.MinFilter(2 * r + 1)) for r in (6, 14))
    S, C6, C14 = (np.asarray(m) > 0 for m in (solid, core6, core14))
    keep = np.zeros_like(S)
    keep[: int(h * 0.70)] = True                              # above the foot's dissolve (a bust's cue, not the pass)
    ring, inner = S & ~C6 & keep, C14 & keep
    Loff, Lon = (_lum(im.crop((x, y, x + w, y + h))) for im in (off, on))
    g = [int(ground[i:i + 2], 16) for i in (1, 3, 5)]
    Lg = 0.2126 * g[0] + 0.7152 * g[1] + 0.0722 * g[2]
    lit = inner & (Loff > 24)
    ratio = Lon[lit] / Loff[lit] - 1
    return {"ring_px": int(ring.sum()), "inner_px": int(lit.sum()),
            "edge_to_ground_off": float(np.abs(Loff[ring] - Lg).mean()),
            "edge_to_ground_on": float(np.abs(Lon[ring] - Lg).mean()),
            "grain_std": float(ratio.std()), "grain_mean": float(ratio.mean())}


@needs_browser
def test_the_pass_wraps_the_edge_toward_the_ground_and_grains_the_interior() -> None:
    tl, uris = G.SURFACES["newsreel-band"]()
    t = G.FRAME_T["newsreel-band"]
    [(png_off, box_off)] = _render(tl, uris, [t], IMG_BOX)
    [(png_on, box_on)] = _render(dict(tl, kinetics={"harmonise": GROUND}), uris, [t], IMG_BOX)
    assert box_off and box_on and box_off["filter"] == "none" and "url(" in box_on["filter"], (box_off, box_on)
    m = harmonise_measure(png_off, png_on, box_on)
    assert m["ring_px"] > 500 and m["inner_px"] > 5000, m
    assert m["edge_to_ground_on"] < m["edge_to_ground_off"] - 2.0, m     # the wrap: the edge moves toward its ground
    assert 0.02 < m["grain_std"] < 0.12, m                               # the grain: present, inside kappa's reach
    assert abs(m["grain_mean"]) < 0.03, m                                # ... and centred - it tints nothing


@needs_browser
def test_a_malformed_harmonise_is_ignored_by_name_and_paints_nothing() -> None:
    import served_player as SP
    tl, uris = G.SURFACES["newsreel-band"]()
    tl = dict(tl, kinetics={"harmonise": "cream"})
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "bad.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE["16:9"]
        with SP.served(html, w, h, prepare=False) as (page, errs):
            logs: list[str] = []
            page.on("console", lambda m: logs.append(m.text))
            page.reload(wait_until="networkidle")
            RB.prepare_page(page, w, h)
            RB.frame_png(page, G.FRAME_T["newsreel-band"], (w, h))
            box = page.evaluate(IMG_BOX)
    assert box["filter"] == "none", box
    assert any("kinetics: harmonise 'cream' is not true or a #rrggbb ground - ignored" in x for x in logs), logs
