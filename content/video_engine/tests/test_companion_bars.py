"""P70 T4 (was P69 T52; harvest v2 T39): COMPANION BARS BESIDE A HELD LINE.

The verb is BUILT (P69 T8b-T8e): a panels page stands as its line alone with a bars panel hidden, and a `row` focus
state on a word makes both active - `lpPanelStart` starts a hidden panel's build on the word that shows it. So the beat
is a RECIPE (`recipe:companion-bars-beside-the-held-line`) and a golden (`companion-railway-yardstick`: Steel and Paper
H row 14's yardstick, the railways' ~50 beside US tech's 28).

The honesty rule had a gap, and it is the one new mechanism: E79 groups panels by their unit STRING, so one measure
written in two units ("%" on the line, "¢" on the bars - both a share of every dollar invested) silently drew two
scales. A panel may now name its `measure`; one measure in two units is an E79 / E53 s4 WARN (advice, E99 s106),
never a refusal, and a page whose panels name no measure builds the bytes it always did.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "content/video_engine/scripts"
GOLDEN = REPO / "content/video_engine/tests/golden"
for p in (SCRIPTS, GOLDEN):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import ledger_page as LPG  # noqa: E402
import recipe_walk as RW  # noqa: E402

RECIPE = REPO / "content/video_engine/effects/recipes/companion-bars-beside-the-held-line.json"
RECIPE_SCHEMA = REPO / "content/video_engine/configs/effect_recipe.schema.json"
SURFACE = "companion-railway-yardstick"
MEASURE = "share of all US private investment"
TWO_ERAS = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-tnx-two-eras-v3.series.json"


def _golden():
    import build_golden_sources as G
    return G


def _warns(series: dict) -> list[str]:
    return LPG.build_spec(series, "line").get("warnings") or []


def _measure_rows(warns: list[str]) -> list[str]:
    return [w for w in warns if w.startswith("E79 / E53 s4")]


# ---- the honesty rule: one measure, one unit, one scale -------------------------------------------------------------
def test_one_measure_in_two_units_WARNs_E79_E53_s4_with_the_units_and_the_panels() -> None:
    """The Expected RED: `panel_scale_warnings` was silent for one `measure` in '%' and '¢'."""
    cents = _golden().companion_series(re_express=False)
    rows = _measure_rows(_warns(cents))
    assert len(rows) == 1, _warns(cents)
    assert MEASURE in rows[0] and "'%'" in rows[0] and "'¢'" in rows[0], rows[0]
    assert "'%': panels 0" in rows[0] and "'¢': panels 1" in rows[0], "the WARN names which panel draws which unit"
    assert "one measure, one unit, one scale; re-express one panel" in rows[0], rows[0]


def test_the_WARN_is_advice_the_page_still_builds_on_its_two_scales() -> None:
    """E99 s106: never a refusal - the author's page validates and builds; the build SAYS so."""
    cents = _golden().companion_series(re_express=False)
    assert LPG.validate(cents, "line") == []
    spec = LPG.build_spec(cents, "line")
    doms = [p["axes"]["domain"] for p in spec["panels"]]
    assert doms[0] != doms[1], "two units, two groups: the two scales the WARN is about"


def test_re_expressed_in_the_lines_unit_the_page_prints_none_and_draws_ONE_scale() -> None:
    spec = LPG.build_spec(_golden().companion_series(), "line")
    assert "warnings" not in spec, spec.get("warnings")
    doms = [p["axes"]["domain"] for p in spec["panels"]]
    assert doms[0] == doms[1] and doms[0][0] == 0.0, ("E79 apply 1: one measure, one scale, the bars' zero kept", doms)
    assert spec["panels"][1]["unit"] == "%" and spec["panels"][1]["value_strings"] == ["50", "28"]


def test_the_ledger_page_check_PRINTS_the_WARN_for_cents_and_none_for_percent(tmp_path) -> None:
    """Acceptance 5: compiled WITHOUT the re-expression the page prints the WARN; with it, none."""
    G = _golden()
    out = {}
    for name, re_express in (("cents", False), ("percent", True)):
        path = tmp_path / f"ev-companion-{name}.series.json"
        path.write_text(json.dumps(G.companion_series(re_express), ensure_ascii=False), encoding="utf-8")
        run = subprocess.run([sys.executable, str(SCRIPTS / "ledger_page.py"), str(path), "--variant", "line", "--check"],
                             capture_output=True, text=True, encoding="utf-8", timeout=120,
                             env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        assert run.returncode == 0, run.stderr
        out[name] = [ln for ln in run.stdout.splitlines() if "[WARN]" in ln]
    assert len(out["cents"]) == 1 and "E79 / E53 s4" in out["cents"][0] and MEASURE in out["cents"][0], out["cents"]
    assert out["percent"] == [], out["percent"]


@pytest.mark.parametrize("a, b", [(MEASURE, "  Share of all US   private investment "), (MEASURE, MEASURE.upper())])
def test_one_measure_is_one_however_it_is_cased_or_spaced(a, b) -> None:
    cents = _golden().companion_series(re_express=False)
    cents["panels"][0]["measure"], cents["panels"][1]["measure"] = a, b
    assert len(_measure_rows(_warns(cents))) == 1


def test_different_measures_in_different_units_are_E79s_unrelated_measures_and_say_nothing() -> None:
    cents = _golden().companion_series(re_express=False)
    cents["panels"][1]["measure"] = "cents of every dollar invested, 1840s Britain"
    assert _measure_rows(_warns(cents)) == []
    cents["panels"][1].pop("measure")
    assert _warns(cents) == [], "a panel that names no measure is not part of the rule"


def test_a_measure_that_is_not_text_is_named() -> None:
    series = _golden().companion_series()
    series["panels"][1]["measure"] = 50
    warns = _warns(series)
    assert len(warns) == 1 and "panels[1] measure 50 is not a name" in warns[0], warns


def test_independent_does_not_silence_one_measure_in_two_units() -> None:
    """`independent` declares UNRELATED measures (E79 apply 2); naming one measure on both says they are one."""
    cents = _golden().companion_series(re_express=False)
    cents["independent"] = True
    assert len(_measure_rows(_warns(cents))) == 1


def test_measure_never_reaches_the_spec_a_page_without_it_builds_the_bytes_it_always_did() -> None:
    """Byte identity at the spec: the key is read by the WARN only. The companion page with and without `measure` builds
    the same spec, and a committed panels object (no measure) builds with no new key."""
    G = _golden()
    named, bare = G.companion_series(), G.companion_series()
    for p in bare["panels"]:
        p.pop("measure")
    assert json.dumps(LPG.build_spec(named, "line"), sort_keys=True) == json.dumps(LPG.build_spec(bare, "line"), sort_keys=True)
    eras = LPG.build_spec(LPG.load_series(TWO_ERAS), "line")
    assert "warnings" not in eras and LPG.measure_unit_warnings(LPG.load_series(TWO_ERAS)) == []


# ---- the golden: read from its objects, never re-typed ----------------------------------------------------------------
def test_the_golden_reads_its_two_committed_objects_and_draws_the_railway_50_once() -> None:
    G = _golden()
    line, bars = LPG.load_series(G.COMPANION_LINE), LPG.load_series(G.COMPANION_BARS)
    series = G.companion_series()
    assert series["panels"][0]["series"] == line["series"], "the line's points are the object's"
    assert [b["value"] for b in series["panels"][1]["bars"]] == [b["value"] for b in bars["bars"]] == [50, 28]
    assert [b["note"] for b in series["panels"][1]["bars"]] == ["~50%", "28%"], "cents per dollar written as percent"
    assert "hlines" not in series and all("hlines" not in p for p in series["panels"]), (
        "the railway 50 is the bars panel's; the line object's hline is dropped (a value is drawn once, E53 addendum)")
    assert "domain" not in series["panels"][1] and "overflow" not in series["panels"][1], "the panel's scale is E79's"
    assert "our arithmetic" in series["src"] and line["src"] in series["src"], "the re-expression is said (E77)"
    assert series["panels"][0]["measure"] == series["panels"][1]["measure"] == line["ylabel"] == MEASURE


def test_the_golden_stands_the_line_alone_then_both_on_the_word_then_the_line_again() -> None:
    """Acceptance 1, 2 and 4, on the compiled species (normalised by `check_panels`), on the take's own spacing."""
    G = _golden()
    world, species = G.companion_page()
    assert world["page"]["builder"] == LPG.PANELS and world["idle"] == "live"
    focus = [(e["at"], e["layout"], e["roles"]) for e in species if e["kind"] == "panel_focus"]
    assert focus == [(0.0, "row", ["active", "hidden"]), (9.0, "row", ["active", "active"]),
                     (16.2, "row", ["active", "hidden"])], focus
    assert G.COMPANION_LEAVE_AT - G.COMPANION_REVEAL_AT == pytest.approx(192.36 - 185.16), "as spoken"
    assert "readability" not in (world["page"].get("axes") or {}), "the golden is drawn plain, as every panels golden"
    longform, _sp = G.companion_page(longform=True)
    assert longform["page"]["axes"]["readability"] == LPG.LONGFORM, "... and the row's long form is one flag away"


# ---- the recipe ------------------------------------------------------------------------------------------------------
def _recipe() -> dict:
    return json.loads(RECIPE.read_text(encoding="utf-8"))


def test_the_recipe_is_a_schema_valid_candidate_of_existing_cards() -> None:
    import jsonschema
    r = _recipe()
    jsonschema.validate(r, json.loads(RECIPE_SCHEMA.read_text(encoding="utf-8")))
    assert r["status"] == "candidate" and r["count"] == 0 and "proof" not in r
    assert len(r["does"]) <= 240
    assert [m["card"] for m in r["members"]] == ["page_builder:line", "page_species:panel_focus", "page_species:panel_focus",
                                                 "page_species:figure", "page_species:panel_focus"]
    assert [m.get("optional", False) for m in r["members"]] == [False, False, False, True, False], "the figure is optional"
    cards = {c["id"] for f in (REPO / "content/video_engine/effects/cards").glob("*.json")
             for c in json.loads(f.read_text(encoding="utf-8"))["cards"]}
    assert {m["card"] for m in r["members"]} <= cards


def test_the_walk_names_panel_focus_by_its_card() -> None:
    """Before T4 the walk emitted `species:panel_focus` - a card that does not exist - so no recipe could compose it."""
    assert RW.species_card("panel_focus") == "page_species:panel_focus"


def test_recipe_walk_walks_the_recipe_in_order_inside_its_window_on_the_golden() -> None:
    """Acceptance 6: the golden's timeline, walked; one fire at the page's instant, every member at its own time."""
    tl, _uris = _golden().companion_railway_yardstick()
    r = _recipe()
    fires = RW.match(RW.events(tl), r["members"], r["window_s"], t0=0.0)
    assert len(fires) == 1, [f.members_at for f in fires]
    assert fires[0].members_at == [0.0, 0.0, 9.0, None, 16.2], fires[0].members_at
    assert fires[0].t_end - fires[0].t <= r["window_s"]


def test_the_recipes_offsets_also_hold_row_14s_take() -> None:
    """The offsets span the golden AND H row 14's take (page 162.60, 'railways' 185.16, 'closest' 192.36)."""
    r = _recipe()
    for member, at in zip([m for m in r["members"] if not m.get("optional")], (162.60, 162.60, 185.16, 192.36)):
        lo, hi = RW.band(member["offset_s"])
        assert lo <= round(at - 162.60, 2) <= hi, (member["card"], at)
    assert 192.36 - 162.60 <= r["window_s"]


# ---- the player: the mechanism is T8b-T8e's, read on the golden (the REUSE proof) -----------------------------------------
def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


PANELS_READ = """() => { const s = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp && x.__lp.panels);
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  const op = (e) => { let n = e, o = 1; while (n && n !== document.body) { const cs = getComputedStyle(n);
    if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +(cs.opacity || 1); n = n.parentElement; } return o; };
  return w.__lp.panels.map((S) => ({ kind: S.kind, chart: R(S.chart), op: op(S.chart),
    lines: (S.paths || []).map((p) => ({ stroke: p.p.getAttribute('stroke'), dash: p.p.getAttribute('stroke-dashoffset'),
                                         bloom: p.p.style.filter })),
    bars: (S.bars || []).map((b) => ({ h: R(b.bar)[3], text: b.val.textContent })) })); }"""
TIMES = {"alone": 8.5, "first_seen": 9.7, "both": 14.5, "again": 18.6}


@pytest.fixture(scope="module")
def played(tmp_path_factory) -> dict:
    """The golden played forward through the beat's instants: {name: every panel's read}."""
    if not _chromium():
        pytest.skip("playwright chromium not installed")
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(SURFACE)
    tmp = tmp_path_factory.mktemp("companion")
    html = tmp / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp)
    w, h = RB.STAGE[aspect]
    out = {}
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
            pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=180000)
            RB.prepare_page(pg, w, h)
            for name, x in TIMES.items():
                RB.frame_png(pg, x, (w, h))
                out[name] = pg.evaluate(PANELS_READ)
            br.close()
    finally:
        srv.shutdown()
    return out


def test_the_bars_carry_no_ink_before_their_word_and_stand_on_the_lines_scale_after_it(played) -> None:
    """Acceptance 1 and 2 (the REUSE proof - green on the base): the page stands as the line ALONE over the region, the
    bars panel hidden with no bar drawn; after the word both are active and the bars stand in true proportion, valued."""
    alone, both = played["alone"], played["both"]
    assert alone[1]["op"] == 0 and [b["h"] for b in alone[1]["bars"]] == [0, 0], alone[1]
    assert alone[0]["chart"][2] > 1.8 * both[0]["chart"][2], ("the line alone spans the region (T8c)", alone[0], both[0])
    assert both[1]["op"] == pytest.approx(1.0) and [b["text"] for b in both[1]["bars"]] == ["50%", "28%"]
    h50, h28 = (b["h"] for b in both[1]["bars"])
    assert h28 / h50 == pytest.approx(28 / 50, abs=0.01), "one zero, one scale: 28 is 0.56 of 50"
    assert both[0]["chart"][3] == pytest.approx(both[1]["chart"][3], abs=1), "the two plots side by side, one height"


def test_the_line_keeps_its_ink_its_bloom_and_its_draw_through_the_beat(played) -> None:
    """Acceptance 3: the line never re-inks, never loses its bloom (T37b's hot core on the primary), never un-draws."""
    reads = [played[k][0]["lines"] for k in ("alone", "both", "again")]
    for lines in reads:
        assert [ln["stroke"] for ln in lines] == [ln["stroke"] for ln in reads[0]], lines
        assert all(float(ln["dash"]) == 0.0 for ln in lines), "drawn whole"
        assert lines[0]["bloom"].startswith('url("#lphot'), ("the primary line blooms (E99 s117)", lines[0]["bloom"])


def test_on_the_leave_the_bars_go_and_the_line_stands_alone_again(played) -> None:
    """Acceptance 4: [active, hidden] again - the bars panel gone, the line re-grown over the whole region (T8c)."""
    again, alone = played["again"], played["alone"]
    assert again[1]["op"] == 0
    assert again[0]["chart"] == pytest.approx(alone[0]["chart"], abs=1.5), (again[0]["chart"], alone[0]["chart"])


@pytest.mark.xfail(strict=True, reason="P70 T4 FINDING (engine, outside T4): a hidden panel builds while invisible - "
                   "lpPanelStart starts its build on the focus word, the move fades it in from ~u 0.6, so the bars are "
                   "~95 % built when first seen (NOTES.md). Flips to a pass when the engine starts the build as it shows.")
def test_the_bars_are_seen_BUILDING_on_their_word(played) -> None:
    first = played["first_seen"][1]
    assert first["op"] > 0.1, first
    tall = max(b["h"] for b in played["both"][1]["bars"])
    assert max(b["h"] for b in first["bars"]) < 0.5 * tall, "when the panel is first seen, its bars are still building"
