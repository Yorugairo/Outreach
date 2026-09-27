"""P72 T53 (a) (R26-412 (a); P71 T34's stopped recipe `the-hidden-base`) - THE ICEBERG STAGE.

Bravos BUB 0:00-0:48 (RUH3BPQ5fTo; BRAVOS-USE-WHEN T1 / A33 / R1): the tip over a waterline, the camera drops through the
water to the base, the hidden part lit - "the hidden part is bigger than the visible part, drawn in true proportion with
its figures written" (s100). T34 composed the page (T64's segments, a rule at the boundary, T29's glow, T32's pedestal)
and stopped on four gaps, each pinned here:

1. THE SKY. A raised pedestal on a full-stage page showed the stage's navy void and the world's cream edge above the page
   (T34's strip at 1.6 s): the page had nothing above y 0. A row with a pedestal now stands its page on a TALL stage -
   the page's own ground carried up over the band the raised camera shows, so the frame opens on the page's sky.
2. THE WATER. `hlines[i].water: true` on a BARS page: the region under that rule is water - a translucent tint from the
   rule down past the page's foot - so the rule reads as the surface and the part under it as submerged. Refused by name
   off a bars page, on a non-boolean, and on a second water rule.
3. THE LIGHT ON THE HIDDEN PART. `glow {bar, segment}`: the edge round ONE part of a stacked bar, not the whole bar
   (T34: "glow edges the WHOLE bar"). Refused by name on a bar with no parts, past its parts, and without `bar`.
4. THE EVIDENCE. `ev-leases-iceberg-v1`, a COMMITTED object pairing the visible and hidden totals - $261B of bonds (the
   issuance series' own 2020-25 points, summed) and $822B of lease commitments (the leases record's "Latest filings"
   row) - DERIVED by `_proofs/p72-t53/derive_iceberg.py`, never typed, recording `derived_from`.
"""
from __future__ import annotations

import copy
import io
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/projects/_proofs/p72-t53"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as L  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
OBJECT = EP / "evidence/objects/ev-leases-iceberg-v1.series.json"
STILL = (0, 0, 0)
# the fixture copies the object's two figures so the engine rows never read the object under test
ICE = {"title": "t", "sub": "s", "src": "fixture", "unit": "$", "unit_suffix": "B",
       "hlines": [{"y": 822, "label": "the balance sheet", "color": "deemph", "water": True}],
       "bars": [{"label": "What they owe", "value": 1083, "color": "deemph",
                 "segments": [{"name": "Lease commitments", "value": 822, "color": "crimson"},
                              {"name": "Bonds issued", "value": 261, "color": "deemph"}]}]}
PED = {"at": 6.0, "dur": 2.0, "by": 0.4}


# ---- 4. the evidence object -------------------------------------------------------------------------------------------------

def test_the_iceberg_object_is_committed_and_derived_never_typed():
    import derive_iceberg as D
    assert OBJECT.exists(), "the committed object pairing the visible and hidden totals"
    obj = json.loads(OBJECT.read_text(encoding="utf-8"))
    assert obj == D.derive(), "the committed object IS the derivation - rerun derive_iceberg.py --write"
    assert set(obj["derived_from"]) == {"ev-debt-issuance-line-v1", "ev-doc-leases"}, obj["derived_from"]
    pair = obj["pair"]
    assert pair["hidden"]["value"] == D.leases_latest() and pair["visible"]["value"] == D.bonds_2020_25()
    seg = obj["bars"][0]["segments"]
    assert [s["value"] for s in seg] == [pair["hidden"]["value"], pair["visible"]["value"]], "the hidden part at the base"
    assert obj["bars"][0]["value"] == pair["hidden"]["value"] + pair["visible"]["value"], "the whole is the two parts"
    rule = obj["hlines"][0]
    assert rule["y"] == pair["hidden"]["value"] and rule["water"] is True, "the waterline stands at the boundary"
    for p in obj["proof"]:
        assert p["quote"] in (ROOT / p["path"]).read_text(encoding="utf-8").replace("\n", " ") or p["kind"] == "html", p
    assert L.validate(obj, "bars") == [] if hasattr(L, "validate") else True


def test_the_derivation_reads_the_two_committed_records():
    import derive_iceberg as D
    issuance = json.loads((EP / "evidence/objects/ev-debt-issuance-line-v1.series.json").read_text(encoding="utf-8"))
    pts = next(s["pts"] for s in issuance["series"] if s["label"] == "issuance")
    assert D.bonds_2020_25() == sum(v for x, v in pts if 2020 <= x <= 2025)
    assert "Latest filings" in (EP / "evidence/ev-doc-leases.html").read_text(encoding="utf-8")
    assert D.leases_latest() > D.bonds_2020_25(), "the hidden part is the larger (T1: the claim the form makes)"


# ---- 2. the water ---------------------------------------------------------------------------------------------------------

def test_a_water_rule_stands_on_a_bars_page_and_is_refused_by_name_elsewhere():
    assert L.water_errors(ICE, "bars") == []
    line = {"series": [{"name": "a", "pts": [[0, 1], [1, 2]]}], "hlines": [{"y": 1.5, "water": True}]}
    assert any("water" in e and "bars" in e for e in L.water_errors(line, "line")), L.water_errors(line, "line")
    bad = copy.deepcopy(ICE); bad["hlines"][0]["water"] = "yes"
    assert any("water" in e and "true" in e for e in L.water_errors(bad, "bars"))
    two = copy.deepcopy(ICE); two["hlines"].append({"y": 200, "water": True})
    assert any("one" in e for e in L.water_errors(two, "bars")), L.water_errors(two, "bars")
    plain = copy.deepcopy(ICE); plain["hlines"][0].pop("water")
    assert L.water_errors(plain, "bars") == [], "a plain rule is untouched"


# ---- 3. the light on the hidden part: the compiler --------------------------------------------------------------------------

def test_a_glow_may_name_one_part_of_its_bar():
    ok = {"kind": "glow", "at": 1.0, "dur": 0.7, "bar": 0, "segment": 0}
    assert B._validate_glow(ok) == []
    assert any("segment" in e for e in B._validate_glow(dict(ok, segment=-1)))
    assert any("segment" in e and "bar" in e for e in B._validate_glow({"kind": "glow", "at": 1, "dur": 1, "span": 0, "segment": 0}))


def _ice_world(tmp: Path, obj=ICE, plate_tail=""):
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / "evidence/objects/fx-ice.series.json").write_text(json.dumps(obj), encoding="utf-8")
    plate = "ledger:fx-ice:bars::right:axes:cut;idle=live;readability=longform" + plate_tail
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(plate, STILL, tmp)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world, plate


def test_the_page_check_refuses_a_part_the_bar_does_not_have(tmp_path):
    world, _ = _ice_world(tmp_path)
    sp = {"kind": "glow", "at": 1.0, "dur": 0.7, "bar": 0, "segment": 0}
    assert B.check_glow(world, [sp]) == []
    with pytest.raises(ValueError, match="segment 2"):
        B.check_glow(world, [dict(sp, segment=2)])
    flat = copy.deepcopy(ICE); flat["bars"][0].pop("segments")
    world2, _ = _ice_world(tmp_path / "flat", flat)
    with pytest.raises(ValueError, match="no parts"):
        B.check_glow(world2, [sp])


# ---- the served player: the water, the part lit, the sky ----------------------------------------------------------------------

def _timeline(tmp: Path, species: list, camera: dict | None = None):
    world, plate = _ice_world(tmp)
    assert B.validate_species(copy.deepcopy(species), STILL, plate) == []
    sc = {"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
          "span": [0.0, G.RUNTIME], "docks": [], "species": copy.deepcopy(species)}
    if camera:
        sc["camera"] = camera
    tl = G._timeline("P72 T53 (a): the iceberg stage", [sc], {}, "16:9")
    tl["kinetics"] = dict(tl.get("kinetics") or {}, camera=True)
    return tl, dict(G._base_uris(), **B.longform_assets(tl))


PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp, PF = st.perform || {};
  const bb = (el) => { if (!el) return null; const r = el.getBBox(); return [r.x, r.y, r.width, r.height]; };
  const rule = (st.marks || []).find(m => m.role === 'rule'), water = st.water || null;
  const rec = (st.bars || [])[0], segs = (rec && rec.segs) || [];
  const g = (PF.glows || [])[0];
  return { ruleY: rule ? rule.geom.y : null, water: water ? { box: bb(water.el), fill: water.el.getAttribute('fill') || water.el.style.fill,
             op: +(water.el.getAttribute('fill-opacity') || water.el.style.fillOpacity || 0) } : null,
           segs: segs.map(s => bb(s.el)), glow: g ? { d: g.path.getAttribute('d'), op: +(g.path.getAttribute('opacity') || 0), box: g.path.getAttribute('d') ? bb(g.path) : null } : null,
           H: (st.geom || {}).H };
}"""


def _serve(tl, uris, ts, probe=PROBE, shots=()):
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "ice.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        page, errs, close = SP.open_served(html, 1920, 1080)
        try:
            out = []
            for t in ts:
                page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                out.append(page.evaluate(probe))
            pngs = [RB.frame_png(page, t, (1920, 1080)) for t in shots]
            return out, pngs, errs
        finally:
            close()


def test_the_water_stands_under_its_rule(tmp_path):
    tl, uris = _timeline(tmp_path, [])
    (s,), _, errs = _serve(tl, uris, [4.0])
    assert not errs, errs
    assert s["water"], "a water rule draws its water"
    wb = s["water"]["box"]
    assert abs(wb[1] - s["ruleY"]) < 1.0, ("the water's surface IS the rule", wb, s["ruleY"])
    assert wb[1] + wb[3] >= s["H"] - 1, "down past the page's foot - the base is under water"
    assert 0 < s["water"]["op"] < 0.6, "translucent: the part under it reads submerged, never erased"


def test_the_glow_lights_the_hidden_part_only(tmp_path):
    sp = {"kind": "glow", "at": 5.0, "dur": 0.7, "bar": 0, "segment": 0}
    tl, uris = _timeline(tmp_path, [sp])
    (s,), _, errs = _serve(tl, uris, [7.0])
    assert not errs, errs
    assert s["glow"] and s["glow"]["op"] == 1, s["glow"]
    gb, hidden, visible = s["glow"]["box"], s["segs"][0], s["segs"][1]
    assert abs(gb[1] - hidden[1]) < 2 and abs(gb[1] + gb[3] - (hidden[1] + hidden[3])) < 2, ("the edge round the HIDDEN part", gb, hidden)
    # the visible part's rect reaches its corner radius down under the boundary (lpSegRects' `foot`): its TOP is the test
    assert gb[1] > visible[1] + 0.5 * visible[3], ("and not round the visible part above it", gb, visible)


def _band_rgb(png: bytes, y0: int, y1: int):
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    px = [im.getpixel((x, y)) for y in range(y0, y1, 7) for x in range(40, 1880, 37)]
    return px


def test_a_raised_pedestal_opens_on_the_pages_own_sky(tmp_path):
    tl, uris = _timeline(tmp_path, [], camera={"keys": [], "pedestal": dict(PED)})
    (s,), (raised, landed), errs = _serve(tl, uris, [3.0], shots=[3.0, 9.0])
    assert not errs, errs
    band = _band_rgb(raised, 4, int(PED["by"] * 1080) - 8)
    ground = _band_rgb(landed, 4, 12)[0]   # the page's own ground at the frame's top, the camera landed (its foot is water)
    VOID, CREAM = (8, 24, 36), (244, 230, 199)
    near = lambda a, b, d=6: all(abs(p - q) <= d for p, q in zip(a, b))   # noqa: E731
    assert not any(near(p, VOID) for p in band), "R26-412 (a): the stage's navy void shows over the raised page"
    assert not any(near(p, CREAM, 12) for p in band), "R26-412 (a): the world's cream edge shows over the raised page"
    assert sum(near(p, ground, 10) for p in band) >= 0.95 * len(band), ("the band over the page is the page's own ground", ground, band[:4])
