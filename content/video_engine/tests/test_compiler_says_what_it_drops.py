"""P72 T17 - THE COMPILER SAYS WHAT IT DROPS: spans, warnings, twins, WARNs by name.

Ten backlog rows, one rule (E99 s106: "a silent drop is neither advice nor refusal"). Each case below compiled
SILENTLY before this slice; each now either refuses by name (a key the row wrote that nothing can honour) or WARNs /
INFOs with its numbers (timing and placement advise - the frame read and the operator judge):

  R26-249  an UNAUTHORED page's entry + build + leave is checked against its row (a WARN - the clock is the builder's)
  R26-317  a page's E79 WARN (`ledger_page` scale / measure warnings) reaches the door's build log
  R26-43   a tag wider than its chart WARNs by name instead of dropping its tip pill silently
  R26-149  `morph_series=<n>` names the series a morph ENTER's area becomes (default 0), refused by name out of range
  R26-214  `;idle=figure` on a picture (world) plate is refused by name - it breathes the whole room (b)
  R26-209  the open camera at every scene boundary is an INFO line; a key set that holds a zoom into a cut WARNs
  R26-258  a thrown / sprung prop's box is padded by its resting shadow's reach toward the light's fall
  R26-143  `compare` beside `remake` on one page is REFUSED by name (the step-(0) probe: the comparator stands on a
           datum the remake takes away, and is gone after it with no leave)
  R26-333  a decade ruler whose scroll overlaps a `freeze` beat WARNs (the ruler, the beat, the overlap in seconds)

R26-154 (the melt's twins) is pinned where the other melt pairs are: test_transitions_e47.
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
sys.path[:0] = [str(ROOT / "content/video_engine/scripts"), str(ROOT / "content/video_engine/tests/golden"),
                str(ROOT / "content/video_engine/tests")]

import build_scene_timeline_f as B  # noqa: E402

LPG = B.LPG
SERIES = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"
STOPACTION = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"
NODE = "node.exe" if sys.platform == "win32" else "node"


def _ep(tmp_path: Path, objects: dict[str, dict]) -> Path:
    """An episode dir holding the given evidence objects (`<id>.series.json`)."""
    (tmp_path / "evidence/objects").mkdir(parents=True, exist_ok=True)
    for oid, series in objects.items():
        (tmp_path / "evidence/objects" / f"{oid}.series.json").write_text(json.dumps(series), encoding="utf-8")
    return tmp_path


def _line_series() -> dict:
    return json.loads(SERIES.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _landscape(monkeypatch):
    monkeypatch.setattr(B, "ASPECT", "16:9")


# ---- R26-249: every page's entry + build + leave against its row ------------------------------------------------

def _page_scene(span: float, **page) -> dict:
    return {"scene_id": "row-07", "span": [10.0, 10.0 + span],
            "world": {"kind": "ledger", "page": {"builder": "story", "title": "unauthored page", **page}}}


def _default_need(page: dict) -> float:
    build = B.page_build_duration_s(page)
    return B._page_entry_build_s(page, build) + sum(float(v) for v in B.MG.LP_RETRACT_S)


def test_an_unauthored_page_on_a_short_row_is_checked_and_warned_by_name() -> None:
    scene = _page_scene(2.0)
    need = _default_need(scene["world"]["page"])
    B.validate_page_build_spans([scene])   # never refused: the clock is the builder's own, not the author's (s106)
    warns = B.page_build_span_warnings([scene])
    assert len(warns) == 1, warns
    w = warns[0]
    for said in ("shot row 1", "row-07", "'unauthored page'", f"{need:g}s", "2s", "build_s"):
        assert said in w, (said, w)


def test_an_unauthored_page_that_fits_its_row_says_nothing() -> None:
    scene = _page_scene(_default_need(_page_scene(1.0)["world"]["page"]) + 0.01)
    assert B.page_build_span_warnings([scene]) == []


def test_an_authored_page_is_still_refused_and_never_warned_twice() -> None:
    scene = _page_scene(1.0, build_s=2.0, title="authored")
    with pytest.raises(ValueError, match="authored"):
        B.validate_page_build_spans([scene])
    assert B.page_build_span_warnings([scene]) == [], "an authored page is the refusal's, not the advice's"


def test_a_cut_exit_takes_the_leave_out_of_the_unauthored_check_too() -> None:
    page = {"builder": "story", "title": "cut", "exit": "cut"}
    fit = B._page_entry_build_s(page, B.page_build_duration_s(page)) + 0.01
    assert B.page_build_span_warnings([_page_scene(fit, exit="cut", title="cut")]) == []


def test_a_plate_row_is_not_a_page_and_is_never_checked() -> None:
    assert B.page_build_span_warnings([{"scene_id": "p", "span": [0, 0.5], "world": {"asset_id": "plate"}}]) == []


# ---- R26-317: a page's E79 WARN reaches the build log ----------------------------------------------------------------

def test_a_page_s_E79_warn_is_printed_with_its_row(tmp_path: Path) -> None:
    import build_golden_sources as G
    ep = _ep(tmp_path, {"ev-companion-cents": G.companion_series(re_express=False)})
    world = B.world_for_plate("ledger:ev-companion-cents:line", (0, 0, 0), ep)
    stored = [w for w in world["page"].get("warnings") or [] if str(w).startswith("E79")]
    assert stored, "the fixture carries one measure in two units (E79 / E53 s4)"
    lines = B.page_warning_lines(world, 3)
    assert [ln for ln in lines if ln.startswith("[WARN] R26-317 E79: shot row 3: E79")] == \
        [f"[WARN] R26-317 E79: shot row 3: {w}" for w in stored], lines


def test_the_member_and_form_warnings_keep_their_own_tags() -> None:
    world = {"kind": "ledger", "page": {"warnings": ["WARN member: a logo became its name",
                                                     f"{LPG.FORM_WARN} a slice too thin"]}}
    assert B.page_warning_lines(world, 2) == ["[WARN] P69 T45: shot row 2: WARN member: a logo became its name",
                                              f"[WARN] P69 T50: shot row 2: {LPG.FORM_WARN} a slice too thin"]


def test_a_later_state_s_E79_warn_is_printed_with_its_state() -> None:
    world = {"kind": "ledger", "page": {}, "page_states": [{"warnings": ["E79 later: panels in '%' carry two domains"]}]}
    assert B.page_warning_lines(world, 5) == [
        "[WARN] R26-317 E79: shot row 5: state 2: E79 later: panels in '%' carry two domains"]


def test_a_page_with_no_warnings_prints_nothing() -> None:
    assert B.page_warning_lines({"kind": "ledger", "page": {}}, 1) == []
    assert B.page_warning_lines({"asset_id": "plate"}, 1) == []


# ---- R26-43: a tag wider than its chart WARNs by name ---------------------------------------------------------------

def _pill_page(name: str, label: str = "") -> dict:
    return {"builder": "dense-line", "tip_pill": True, "series": [{"name": name, "label": label, "color": "teal"}]}


def test_a_tag_wider_than_its_chart_warns_by_name_with_the_numbers() -> None:
    name = "THE LONGEST SERIES NAME ANYONE EVER WROTE ON A PHONE"   # 51 glyphs
    warns = B.tip_pill_width_warns(_pill_page(name), "9:16")
    assert len(warns) == 1, warns
    tag_u = len(name) * LPG.LAND_TAG_NAME_U
    pill_u = tag_u + 2 * B.TIPPILL_PAD_X
    chart_u = B.TIPPILL_CHART_U["9:16"]
    for said in (repr(name), f"{tag_u:.0f}", f"{pill_u:.0f}", f"{chart_u:g}", f"{chart_u - 2 * B.TIPPILL_BOUND_PAD:g}", "pill"):
        assert said in warns[0], (said, warns[0])


def test_a_tag_that_fits_its_chart_says_nothing_and_a_page_without_the_pill_is_never_read() -> None:
    assert B.tip_pill_width_warns(_pill_page("S&P 500"), "9:16") == []
    long = _pill_page("THE LONGEST SERIES NAME ANYONE EVER WROTE ON A PHONE")
    long.pop("tip_pill")
    assert B.tip_pill_width_warns(long, "9:16") == []


def test_the_landscape_chart_is_wider_so_the_same_tag_can_fit() -> None:
    name = "N" * 45   # 855 units: over the portrait chart's 784 between its bounds, under the landscape one's 984
    assert B.tip_pill_width_warns(_pill_page(name), "9:16")
    assert B.tip_pill_width_warns(_pill_page(name), "16:9") == []


def test_the_pill_s_dials_are_the_player_s_written_twice() -> None:
    tip = ROOT / "content/video_engine/scripts/species/tippill.mjs"
    src = f"import {{ TIPPILL }} from {json.dumps(tip.as_uri())};\nconsole.log(JSON.stringify(TIPPILL.PAD_X));\n"
    out = subprocess.run([NODE, "--input-type=module", "-e", src], capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    assert B.TIPPILL_PAD_X == json.loads(out.stdout.strip().splitlines()[-1])
    engine = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    assert f"bounds: [{B.TIPPILL_BOUND_PAD}, W - {B.TIPPILL_BOUND_PAD}]" in engine, "buildLedgerLine's pill bounds"
    assert re.search(r"const LP_PORTRAIT = [^\n]*\bX: \d+, W: %d\b" % B.TIPPILL_CHART_U["9:16"], engine), "LP_PORTRAIT.W"


def test_the_pill_row_prints_the_warn_through_the_plate_door(tmp_path: Path, capsys) -> None:
    series = _line_series()
    series["series"][0]["name"] = "MEMORY MAKERS AND EVERY SUPPLIER THEY EVER TOUCHED ON EARTH"
    ep = _ep(tmp_path, {"ev-long": series})
    B.world_for_plate("ledger:ev-long:line;pill=yes", (0, 0, 0), ep)
    out = capsys.readouterr().out
    assert "[WARN] R26-43:" in out and "MEMORY MAKERS AND EVERY SUPPLIER" in out, out


# ---- R26-149: the morph's series word -------------------------------------------------------------------------------

def test_morph_series_that_is_not_an_index_is_refused_by_name() -> None:
    for bad in ("x", "-1", "1.5", ""):
        with pytest.raises(ValueError, match="morph_series"):
            B.split_plate_opts(f"ledger:ev:line;morph_series={bad}")


def test_morph_series_past_the_page_s_series_is_refused_by_name(tmp_path: Path) -> None:
    ep = _ep(tmp_path, {"ev-four": _line_series()})
    with pytest.raises(ValueError, match=r"morph_series 4 .*4 series"):
        B.world_for_plate("ledger:ev-four:line;morph_series=4", (0, 0, 0), ep)


def test_morph_series_on_a_page_that_is_not_a_line_is_refused_by_name(tmp_path: Path) -> None:
    bars = {"title": "bars", "src": "s", "unit": "$", "bars": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]}
    ep = _ep(tmp_path, {"ev-bars": bars})
    with pytest.raises(ValueError, match="morph_series"):
        B.world_for_plate("ledger:ev-bars:bars;morph_series=0", (0, 0, 0), ep)


def test_morph_series_with_no_area_under_its_line_is_refused_by_name(tmp_path: Path) -> None:
    series = _line_series()
    series["series"][2]["pts"] = series["series"][2]["pts"][:1]
    ep = _ep(tmp_path, {"ev-stub": series})
    with pytest.raises(ValueError, match=r"morph_series 2 .*no area"):
        B.world_for_plate("ledger:ev-stub:line;morph_series=2", (0, 0, 0), ep)


def test_morph_series_is_written_on_the_world_and_a_row_without_it_is_untouched(tmp_path: Path) -> None:
    ep = _ep(tmp_path, {"ev-four": _line_series()})
    assert B.world_for_plate("ledger:ev-four:line;morph_series=2", (0, 0, 0), ep)["morph_series"] == 2
    assert "morph_series" not in B.world_for_plate("ledger:ev-four:line", (0, 0, 0), ep)


def test_morph_series_on_a_page_that_does_not_enter_by_morph_is_refused_by_name() -> None:
    sc = {"scene_id": "s02", "world": {"kind": "ledger", "morph_series": 1, "page": {"builder": "dense-line", "enter": "axes"}}}
    errs = B.morph_series_errors([sc])
    assert len(errs) == 1 and "s02" in errs[0] and "morph_series" in errs[0] and "'axes'" in errs[0], errs
    sc["world"]["page"]["enter"] = "morph"
    assert B.morph_series_errors([sc]) == []


def _morph_timeline(morph_series: int | None) -> tuple[dict, dict]:
    import build_golden_sources as G
    page = G._morph_target_page()
    page["enter"] = "morph"
    world = {"kind": "ledger", "page": page, "morph": "tab", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    if morph_series is not None:
        world["morph_series"] = morph_series
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    tl = G._timeline("P72 T17: the morph's series", scenes, {}, None)
    tl["kinetics"] = dict(G.MORPH_KINETICS)
    return tl, G._base_uris()


_MORPH_READ = """() => {
  const nums = (d) => (d.match(/-?\\d+(?:\\.\\d+)?/g) || []).map(Number);
  const m = document.querySelector('path.morph'); if (!m) return null;
  const v = nums(m.getAttribute('d')), pts = []; for (let i = 0; i + 1 < v.length; i += 2) pts.push([v[i], v[i + 1]]);
  const half = pts.slice(0, pts.length >> 1);   /* stripOutline: the top row first, the baseline back */
  const chart = [...m.closest('svg').parentElement.querySelectorAll('svg.lp-chart')].find((s) => !s.classList.contains('lp-morph'));
  const sers = [...chart.querySelectorAll('path.ser')].filter((p) => !p.classList.contains('muted')).map((p) => {
    const L = p.getTotalLength(), s = []; for (let k = 0; k <= 400; k++) { const q = p.getPointAtLength(L * k / 400); s.push([q.x, q.y]); }
    return s; });
  const yAt = (s, x) => { let best = null, bd = 1e9; for (const q of s) { const d = Math.abs(q[0] - x); if (d < bd) { bd = d; best = q[1]; } } return best; };
  return sers.map((s) => Math.sqrt(half.reduce((a, [x, y]) => a + (yAt(s, x) - y) ** 2, 0) / half.length));
}"""


def _morph_rms(morph_series: int | None) -> list[float]:
    import render_baseline as RB
    import served_player as SP
    tl, uris = _morph_timeline(morph_series)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "morph.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE["16:9"]
        with SP.served(html, w, h) as (page, errs):
            RB.frame_png(page, 25.0, (w, h))
            rms = page.evaluate(_MORPH_READ)
            assert not errs, errs
    assert rms, "the morph page drew no morph outline"
    return rms


def test_the_morph_s_area_is_the_named_series_and_the_default_is_the_first() -> None:
    """The engine's `buildMorph` (R26-149): the target area is the series `morph_series` names; absent, the first."""
    base = _morph_rms(None)
    assert len(base) == 4, f"the page's four live lines, read in the chart's own svg: {base}"
    assert min(range(len(base)), key=base.__getitem__) == 0, base
    picked = _morph_rms(2)
    assert min(range(len(picked)), key=picked.__getitem__) == 2, picked
    assert picked[2] < 2.0, f"the outline's top is the named line's own points (rms {picked[2]:.2f} viewBox units)"


# ---- R26-214 (b): `;idle=figure` on a world plate -------------------------------------------------------------------

def test_idle_figure_on_a_picture_plate_is_refused_by_name(monkeypatch) -> None:
    monkeypatch.setattr(B, "_world_for_bare_plate", lambda pid, ken, ep, meta=None: {
        "asset_id": pid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    with pytest.raises(ValueError, match=r"idle=figure.*plate_option:world"):
        B.world_for_plate("world-host-desk-v1;idle=figure", (0, 0, 0), ROOT)
    assert B.world_for_plate("world-host-desk-v1;idle=breath", (0, 0, 0), ROOT)["idle"] == "breath"


def test_idle_figure_elsewhere_is_what_it_was() -> None:
    assert B.plate_idle_error({"kind": "ledger", "page": {}, "idle": "figure"}, "ledger:x") is None
    assert B.plate_idle_error({"kind": B.SPECIES_CLIP, "idle": "figure"}, "clip:x") is None
    assert B.plate_idle_error({"asset_id": "p", "idle": "live"}, "p") is None
    assert B.split_idle("plate-07;idle=figure") == ("plate-07", "figure"), "the grammar is unchanged"


# ---- R26-209: the camera at every scene boundary ----------------------------------------------------------------

def _cam_scene(sid: str, a: float, b: float, keys: list | None) -> dict:
    return {"scene_id": sid, "span": [a, b], "camera": {"keys": keys or [], "attention": "locked"}, "world": {}}


def test_a_key_set_that_holds_a_zoom_into_the_cut_warns_with_its_numbers() -> None:
    s1 = _cam_scene("s01", 0.0, 10.0, [{"t": 4.0, "zoom": 1.0, "look": [0.5, 0.5]}, {"t": 5.0, "zoom": 1.2, "look": [0.6, 0.4]}])
    notes = B.camera_boundary_notes([s1, _cam_scene("s02", 10.0, 20.0, None)])
    warns = [m for lvl, m in notes if lvl == "WARN"]
    assert len(warns) == 1, notes
    for said in ("s01 -> s02", "10s", "zoom 1.20", "look (0.600, 0.400)", "identity"):
        assert said in warns[0], (said, warns[0])
    assert any(lvl == "INFO" and "1 open" in m for lvl, m in notes), notes


def test_a_next_row_that_opens_on_the_same_zoom_is_a_carry_and_only_informs() -> None:
    s1 = _cam_scene("s01", 0.0, 10.0, [{"t": 5.0, "zoom": 1.2, "look": [0.6, 0.4]}])
    s2 = _cam_scene("s02", 10.0, 20.0, [{"t": 10.0, "zoom": 1.2, "look": [0.6, 0.4]}, {"t": 12.0, "zoom": 1.0, "look": [0.6, 0.4]}])
    notes = B.camera_boundary_notes([s1, s2])
    assert [lvl for lvl, _ in notes].count("WARN") == 0, notes
    assert any(lvl == "INFO" and "carried" in m and "s01 -> s02" in m for lvl, m in notes), notes


def test_a_key_set_that_returns_to_identity_is_one_quiet_info_line() -> None:
    s1 = _cam_scene("s01", 0.0, 10.0, [{"t": 4.0, "zoom": 1.2, "look": [0.6, 0.4]}, {"t": 6.0, "zoom": 1.0, "look": [0.6, 0.4]}])
    notes = B.camera_boundary_notes([s1, _cam_scene("s02", 10.0, 20.0, None)])
    assert notes == [("INFO", "1 scene boundary, 0 open - every key set is back at identity by its row's end")], notes


# ---- R26-258: the prop's box keeps its resting shadow ----------------------------------------------------------

def _stopaction(expr: str):
    src = (f"import {{ PROP_SHADOW }} from {json.dumps(STOPACTION.as_uri())};\n"
           f"console.log(JSON.stringify(({expr})));\n")
    out = subprocess.run([NODE, "--input-type=module", "-e", src], capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_the_shadow_s_reach_is_the_stage_light_s_throw_written_twice() -> None:
    light, offset = _stopaction("[PROP_SHADOW.LIGHT_DEG, PROP_SHADOW.OFFSET_PX]")
    assert (B.PROP_SHADOW_LIGHT_DEG, B.PROP_SHADOW_OFFSET_PX) == (light, offset)
    fall = math.radians(light + 180)
    dx, dy = B.PROP_SHADOW_REACH_PX
    assert dx == pytest.approx(offset * math.cos(fall) + B.PROP_SHADOW_EDGE_PX)
    assert dy == pytest.approx(offset * math.sin(fall) + B.PROP_SHADOW_EDGE_PX)
    assert dx > 0 and dy > 0, "the light is up and to the left: the shadow falls down and to the right"


def test_a_thrown_prop_s_box_is_padded_toward_the_light_s_fall() -> None:
    box = {"x": 100.0, "y": 200.0, "w": 400.0, "h": 300.0, "room": "right"}
    dx, dy = B.PROP_SHADOW_REACH_PX
    padded = B.prop_dock_box(box, {"prop": True, "arrive": "throw"}, fitted=False)
    assert padded == {"x": 100.0, "y": 200.0, "w": round(400.0 - dx, 1), "h": round(300.0 - dy, 1), "room": "right"}
    assert box["w"] == 400.0, "the page's placement is never mutated"


def test_a_card_a_stamp_and_an_authored_place_keep_their_box() -> None:
    box = {"x": 1.0, "y": 2.0, "w": 3.0, "h": 4.0}
    assert B.prop_dock_box(box, {"arrive": "throw"}, fitted=False) is box, "a card casts the card's own shadow"
    assert B.prop_dock_box(box, {"prop": True, "arrive": "stamp"}, fitted=True) is box, "the stamp fit keeps 16.8 px clear"
    assert B.prop_dock_box(box, {"prop": True, "place": {"x": .5, "y": .5, "w": .2}}, fitted=True) is box, "the author's place stands"
    assert B.prop_dock_box(None, {"prop": True}, fitted=False) is None, "E45's solo card has no box to pad"


# ---- R26-143 (second half): compare beside remake on one page ---------------------------------------------------

_FIG = {"kind": "figure", "at": 3.0, "dur": 2.0, "text": "1,190", "series": 0, "dy": -7, "target": {"kind": "datum", "index": 8}}
_CMP = {"kind": "chart_to", "at": 6.0, "dur": 2.4, "to": "compare", "hold": "metric",
        "metric": {"value": 1190.0, "text": "1,190", "label": "holdings, $bn"},
        "comparator": {"value": 0.02, "text": "2 % up", "label": "on the first print"},
        "inputs": {"now": 1190.0, "first": 1166.7}, "derive": "now / first - 1", "source": "[DERIVED: synthetic]"}
_RMK = {"kind": "chart_to", "at": 12.0, "dur": 2.4, "to": "remake", "state": 1}
_PLATE = "ledger:golden-level:line;then=golden-prints:bars"


@pytest.mark.parametrize("order", ["compare-first", "remake-first"])
def test_compare_beside_remake_on_one_page_is_refused_by_name(order) -> None:
    species = [dict(_FIG), dict(_CMP), dict(_RMK)] if order == "compare-first" else \
        [dict(_FIG), dict(_RMK, at=4.0), dict(_CMP, at=12.0)]
    errs = B.validate_species(species, (0, 0, 0), _PLATE)
    hit = [e for e in errs if "compare" in e and "remake" in e]
    assert len(hit) == 1 and "one page" in hit[0] and "R26-143" in hit[0], errs


def test_compare_alone_and_remake_alone_still_compile() -> None:
    assert B.validate_species([dict(_FIG), dict(_CMP)], (0, 0, 0), _PLATE) == []
    assert B.validate_species([dict(_RMK)], (0, 0, 0), _PLATE) == []


# ---- R26-333: a ruler's scroll across a freeze beat ------------------------------------------------------------

_FREEZE = {"kind": "freeze", "at": 5.0, "dur": 1.5, "target": {"kind": "datum", "series": 0, "index": 3}}


def _ruler(at: float) -> dict:
    return {"kind": "ruler", "at": at, "dur": 6.0, "from": 1990, "to": 2020}


def test_a_ruler_whose_scroll_overlaps_a_freeze_warns_with_the_numbers() -> None:
    row = [dict(_FREEZE), _ruler(4.0)]
    assert B._freeze_row_errors(row, "ledger:x") == [], "a WARN, never a refusal (s106: timing advises)"
    warns = B.freeze_ruler_advice(row)
    assert len(warns) == 1, warns
    for said in ("ruler[1]", "1990-2020", "4-5.5s", "5-6.5s", "0.50s"):
        assert said in warns[0], (said, warns[0])


def test_a_ruler_clear_of_every_freeze_prints_nothing() -> None:
    assert B.freeze_ruler_advice([dict(_FREEZE), _ruler(1.0)]) == []    # scroll 1.0-2.5, the beat 5.0-6.5
    assert B.freeze_ruler_advice([dict(_FREEZE), _ruler(3.5)]) == []    # scroll ends exactly on the beat
    assert B.freeze_ruler_advice([_ruler(4.0)]) == []                   # no freeze on the row


def test_a_ruler_that_starts_inside_the_beat_is_still_the_refusal_it_was() -> None:
    row = [dict(_FREEZE), _ruler(5.5)]
    assert B._freeze_row_errors(row, "ledger:x"), "nothing starts in the beat (P69 T49) - unchanged"
    assert B.freeze_ruler_advice(row) == [], "the refusal already names it; the advice does not say it twice"
