"""P69 T45 - THE MEMBERSHIP STACK: equal tiles (logos, names) inside ONE bar (E99 s101; s109 (2); s110 (1)).

E99 s101: "A bar may be filled with EQUAL tiles naming who is in it (logos, names) when the bar is ONE value, the tiles
carry no value of their own (equal height, never sized), and the bar's total is written on the page" - Bravos's AI
hidden-debt bar with its Google / Microsoft / Amazon / Meta / Oracle tiles. It reads as MEMBERSHIP, not as segments to
compare. s110 (1) later made a stack of VALUES valid too - that is the stacked bar (P69 T64, `segments`), never this
form: a `members` entry that carries a value is refused here by name.

  (1) THE FIELD      a bar datum may carry `members: [{name, logo?, short?}]` (2..MEMBERS_MAX, names unique); the page
                     carries them per bar and writes its key "each tile = one <member_noun>" (default "member")
  (2) HONESTY        a member with a value (value / share / weight / size / pct / amount / ...) or any field the form
                     does not know is refused; so is a membership on a range bar, a zero bar, a breakthrough page, a
                     page that is not a bars page, or a panel's / tier's bars; a name that cannot fit its tile at the
                     phone floor (E99 s90: 12 px on a 390-px phone) is a WARN with its numbers
  (3) LOGOS          a logo is a CATALOGUED, operator-approved cutout (E94; 11-ARCHIVAL s4: "Logos and organization
                     marks require recorded permission; otherwise use text") - one the catalogue does not carry is
                     dropped and the NAME is written, with a WARN; never an invented mark
  (4) THE PAINT      the bar stands at its one value; its tiles divide it EQUALLY, bottom-up from zero, inside it; the
                     total is written over it; the key is written beside it
  (5) THE LANDING    by default the tiles land one per member after the bar stands (the badge spring, springPop, on the
                     count array's step); a `member` page species lands a tile on its WORD, and `light` lights it while
                     the bar's other tiles dim to E67's 0.45; a seek lands what play lands
  (6) OFF            a bars page with no members is the page it was (no key, no tile, the same world)

Fixtures: the five biggest builders' cash capital spending in Q1 2026 ($148.4B - ev-capex-funding-v1: "Company
filings, aggregated by Epoch AI (Jun 2026) - MSFT, AMZN, GOOGL, META, ORCL"), and the calendar project's
hynix + Micron basket (ev-into-vs-after-v1) whose Micron has the catalogue's own mark. The browser half needs
playwright + chromium.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MICRON = "prop-icon-micron-memory-orbit-v1"
FIVE = ["Microsoft", "Amazon", "Alphabet", "Meta", "Oracle"]

BUILDERS = {
    "title": "Five companies, one quarter's bill",
    "sub": "Cash capital spending, Q1 2026, US$ billions - the five biggest builders together",
    "src": "Company filings, aggregated by Epoch AI (Jun 2026) - MSFT, AMZN, GOOGL, META, ORCL",
    "unit": "$", "member_noun": "company",
    "bars": [{"label": "Q1 2026", "value": 148.4, "color": "crimson", "members": [{"name": n} for n in FIVE]}],
}
BASKET = {
    "title": "The month's gain lands before the print",
    "sub": "hynix + Micron, mean move in the half-month INTO the print vs AFTER it - 25 prints",
    "src": "Operator backtest 2026-08-30: hynix + Micron vs the KCS print calendar, 25 months; n = 25, one regime",
    "unit": "%", "member_noun": "stock",
    "bars": [{"label": "INTO the print", "value": 6.8, "color": "teal",
              "members": [{"name": "SK hynix"}, {"name": "Micron", "logo": MICRON}]},
             {"label": "AFTER the print", "value": 2.2, "color": "deemph",
              "members": [{"name": "SK hynix"}, {"name": "Micron", "logo": MICRON}]}],
}


def _obj(base: dict, **patch) -> dict:
    o = copy.deepcopy(base)
    o.update(patch)
    return o


def _with_members(members, **bar) -> dict:
    o = copy.deepcopy(BUILDERS)
    o["bars"][0]["members"] = members
    o["bars"][0].update(bar)
    return o


def _sha(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


# ---- (1) the field ---------------------------------------------------------------------------------------------------

def test_a_bar_carries_its_members_and_the_page_writes_its_key():
    assert LPG.validate(BUILDERS, "bars") == []
    spec = LPG.build_spec(BUILDERS, "bars", 0, "right")
    assert spec["builder"] == "story"
    assert spec[LPG.MEMBERS_KEY] == [[{"name": n} for n in FIVE]]
    assert spec["member_key"] == "each tile = one company"
    assert spec["values"] == [148.4] and spec["value_strings"] == ["148.4"], "the bar is its ONE value"


def test_the_key_names_a_member_by_default_and_a_bar_without_members_is_null():
    o = _obj(BASKET)
    o.pop("member_noun")
    o["bars"][1].pop("members")
    spec = LPG.build_spec(o, "bars", 0, "right")
    assert spec["member_key"] == "each tile = one member"
    assert spec["members"][1] is None and len(spec["members"][0]) == 2
    assert spec["members"][0][1] == {"name": "Micron", "logo": MICRON}


def test_a_bars_page_without_members_is_the_spec_it_was():
    plain = _obj(BUILDERS)
    plain.pop("member_noun")
    plain["bars"][0].pop("members")
    spec = LPG.build_spec(plain, "bars", 0, "right")
    assert "members" not in spec and "member_key" not in spec
    assert LPG.validate(plain, "bars") == []


def test_a_member_may_carry_a_short_name_for_its_tile():
    o = _with_members([{"name": "Alphabet (Google)", "short": "Alphabet"}, {"name": "Meta"}])
    assert LPG.validate(o, "bars") == []
    assert LPG.build_spec(o, "bars")["members"][0][0] == {"name": "Alphabet (Google)", "short": "Alphabet"}


# ---- (2) honesty: refused by name ------------------------------------------------------------------------------------

@pytest.mark.parametrize("member,pattern", [
    ({"name": "Microsoft", "value": 40}, r"carries a value.*E99 s101"),
    ({"name": "Microsoft", "share": 0.27}, r"carries a value.*E99 s101"),
    ({"name": "Microsoft", "weight": 2}, r"carries a value.*E99 s101"),
    ({"name": "Microsoft", "pct": "27%"}, r"carries a value.*E99 s101"),
    ({"name": "Microsoft", "amount": 40.1}, r"carries a value.*E99 s101"),
    ({"name": "Microsoft", "color": "teal"}, r"'color' is not a member field"),
    ({"name": ""}, r"needs a name"),
    ({"logo": MICRON}, r"needs a name"),
    ("Microsoft", r"is an object"),
    ({"name": "Microsoft", "logo": "Microsoft Logo.png"}, r"logo 'Microsoft Logo.png' is not a catalogue id"),
    ({"name": "Microsoft", "short": "The Microsoft Corporation"}, r"short .* is not shorter than its name"),
])
def test_a_member_that_is_not_one_equal_tile_is_refused_by_name(member, pattern):
    errs = LPG.validate(_with_members([member, {"name": "Meta"}]), "bars")
    assert any(re.search(pattern, e) for e in errs), errs


def test_a_stack_of_values_is_pointed_at_its_own_form():
    errs = LPG.validate(_with_members([{"name": "A", "value": 1}, {"name": "B", "value": 3}]), "bars")
    assert any("segments" in e and "T64" in e for e in errs), "a stack of VALUES is the stacked bar's, s110 (1): " + str(errs)


@pytest.mark.parametrize("members,pattern", [
    ([{"name": "Meta"}], r"2 to 8 members"),
    ([{"name": f"M{i}"} for i in range(9)], r"2 to 8 members"),
    ([{"name": "Meta"}, {"name": "meta"}], r"'meta' twice"),
    ("Microsoft, Meta", r"is a list"),
])
def test_the_members_list_is_a_set_of_two_to_eight(members, pattern):
    errs = LPG.validate(_with_members(members), "bars")
    assert any(re.search(pattern, e) for e in errs), errs


def test_a_membership_is_refused_on_a_range_a_zero_bar_and_a_breakthrough():
    assert any("RANGE" in e for e in LPG.validate(_with_members([{"name": "A"}, {"name": "B"}], value=["+55", "60"]), "bars"))
    assert any("zero" in e for e in LPG.validate(_with_members([{"name": "A"}, {"name": "B"}], value=0), "bars"))
    o = _obj(BUILDERS, overflow="burst", domain=[0, 100])
    assert any("breakthrough" in e for e in LPG.validate(o, "bars")), LPG.validate(o, "bars")


def test_a_membership_is_a_bars_pages_and_nowhere_else():
    combo = _obj(BUILDERS, series=[{"name": "L", "pts": [[0, 1], [1, 2]]}])
    assert any("bars page" in e for e in LPG.validate(combo, "bars")), LPG.validate(combo, "bars")
    prog = _obj(BUILDERS)
    assert any("bars page" in e for e in LPG.validate(prog, "progress")), LPG.validate(prog, "progress")
    panel = {"title": "t", "src": "s", "yunit": "%",
             "panels": [{"sub": "a", "series": [{"name": "A", "pts": [[2020, 1], [2021, 2]]}]},
                        {"sub": "b", "builder": "bars", "unit": "x",
                         "bars": [{"label": "One", "value": 1, "members": [{"name": "A"}, {"name": "B"}]}]}]}
    assert any("membership" in e.lower() for e in LPG.validate(panel, "line")), LPG.validate(panel, "line")


@pytest.mark.parametrize("noun,ok", [("company", True), ("stock", True), ("central bank", True), ("", False),
                                     ("A Company", False), ("x" * 30, False), (3, False)])
def test_the_member_noun_is_a_short_lowercase_word(noun, ok):
    errs = LPG.validate(_obj(BUILDERS, member_noun=noun), "bars")
    assert (errs == []) is ok, errs


def test_a_member_noun_with_no_members_is_refused():
    o = _obj(BUILDERS)
    o["bars"][0].pop("members")
    assert any("member_noun" in e for e in LPG.validate(o, "bars"))


def test_a_name_that_cannot_fit_its_tile_at_the_phone_floor_is_a_warn_with_its_numbers():
    wide = _with_members([{"name": "Microsoft Corporation"}, {"name": "Meta"}])
    spec = LPG.build_spec(wide, "bars", 0, "right")
    warns = LPG.member_fit_warnings(spec, "16:9")
    hit = [w for w in warns if "'Microsoft Corporation'" in w]
    assert hit and hit[0].startswith("WARN member:"), warns
    assert re.search(r"\d+ px", hit[0]) and "phone floor" in hit[0], hit[0]
    assert not [w for w in warns if "'Meta'" in w], "a four-letter name fits a 196 px tile at the floor"
    assert LPG.member_fit_warnings(LPG.build_spec(BASKET, "bars", 0, "right"), "9:16") == []


# ---- (3) logos: catalogued or the name ------------------------------------------------------------------------------

def _world(obj: dict, tmp: Path, opt: str = "", aspect: str = "16:9", oid: str = "fx-members") -> dict:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(f"ledger:{oid}:bars{opt}", (0, 0, 0), tmp)
        if aspect == "16:9":
            B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


def test_a_catalogued_logo_rides_the_asset_map_by_its_catalogue_key(tmp_path):
    world = _world(BASKET, tmp_path)
    assert world["page"]["members"][0][1] == {"name": "Micron", "logo": MICRON}
    tl = {"aspect": "16:9", "scenes": [{"world": world}]}
    uris = B.member_assets(tl)
    assert list(uris) == [B.PROP_PREFIX + MICRON]
    assert uris[B.PROP_PREFIX + MICRON] == B.catalogue_icon_uri(MICRON), "the file on disk, byte for byte"


def test_a_logo_the_catalogue_does_not_carry_is_dropped_and_the_name_written(tmp_path, capsys):
    o = _with_members([{"name": "Microsoft", "logo": "prop-logo-microsoft-v1"}, {"name": "Meta"}])
    world = _world(o, tmp_path)
    assert world["page"]["members"][0][0] == {"name": "Microsoft"}, "never an invented mark: the NAME is the tile"
    warns = [w for w in world["page"].get("warnings", []) if w.startswith("WARN member:")]
    assert any("prop-logo-microsoft-v1" in w and "'Microsoft'" in w for w in warns), warns
    assert B.member_assets({"aspect": "16:9", "scenes": [{"world": world}]}) == {}


def test_a_page_with_no_members_carries_no_member_asset_and_is_the_world_it_was(tmp_path):
    plain = _obj(BUILDERS)
    plain.pop("member_noun")
    plain["bars"][0].pop("members")
    a = _world(plain, tmp_path / "a")
    assert "members" not in a["page"] and "warnings" not in a["page"]
    assert B.member_assets({"aspect": "16:9", "scenes": [{"world": a}]}) == {}


# ---- (5) the row: the `member` species, and what a membership page may not do ---------------------------------------

def _check(world: dict, species: list) -> None:
    B.check_members(world, species)


def test_member_is_a_page_species_with_its_own_when(tmp_path):
    assert B.SPECIES_MEMBER == "member"
    assert "member" in B.SPECIES_KINDS and "member" in B.PAGE_SPECIES
    assert "WHO" in B.SPECIES_WHEN["member"] and "never to compare" in B.SPECIES_WHEN["member"]
    ok = [{"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0}, {"kind": "member", "at": 8.6, "dur": 0.45, "tile": [1, 2]},
          {"kind": "member", "at": 9.2, "dur": 0.45, "tile": "all"}, {"kind": "member", "at": 10.0, "dur": 0.45, "tile": 3, "light": True}]
    assert B.validate_species(ok, (0, 0, 0), "ledger:fx-members:bars") == []
    world = _world(BUILDERS, tmp_path)
    _check(world, ok)


@pytest.mark.parametrize("sp,pattern", [
    ({"kind": "member", "at": 8.0, "dur": 0.45}, r"member: needs a 'tile'"),
    ({"kind": "member", "at": 8.0, "dur": 0.45, "tile": -1}, r"member: tile -1 is not"),
    ({"kind": "member", "at": 8.0, "dur": 0.45, "tile": "first"}, r"member: tile 'first' is not"),
    ({"kind": "member", "at": 8.0, "dur": 0.45, "tile": [0, 0]}, r"member: tile \[0, 0\] names a tile twice"),
    ({"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0, "light": "yes"}, r"member: light must be true or false"),
    ({"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0, "bar": 1.5}, r"member: bar 1.5 is not"),
    ({"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0, "value": 3}, r"member: 'value' is not a member field"),
])
def test_a_malformed_member_species_is_refused_by_name(sp, pattern):
    errs = B.validate_species([sp], (0, 0, 0), "ledger:fx-members:bars")
    assert any(re.search(pattern, e) for e in errs), errs


def test_a_member_species_must_name_a_tile_and_a_bar_the_page_has(tmp_path):
    world = _world(BUILDERS, tmp_path)
    with pytest.raises(ValueError, match=r"tile 5 .* 5 tiles"):
        _check(world, [{"kind": "member", "at": 8.0, "dur": 0.45, "tile": 5}])
    with pytest.raises(ValueError, match=r"bar 1 .*no members|bar 1 is not"):
        _check(world, [{"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0, "bar": 1}])
    plain = _obj(BUILDERS)
    plain.pop("member_noun")
    plain["bars"][0].pop("members")
    with pytest.raises(ValueError, match=r"no membership bar"):
        _check(_world(plain, tmp_path / "p"), [{"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0}])
    basket = _world(BASKET, tmp_path / "b")
    with pytest.raises(ValueError, match=r"2 bars carry members.*'bar'"):
        _check(basket, [{"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0}])
    _check(basket, [{"kind": "member", "at": 8.0, "dur": 0.45, "tile": 0, "bar": 1}])


def test_a_membership_page_takes_park_and_nothing_that_moves_its_bar(tmp_path):
    world = _world(BUILDERS, tmp_path)
    _check(world, [{"kind": "chart_to", "to": "park", "at": 9.0, "dur": 0.8, "scale": 0.7}])
    for verb in ("rescale", "compare", "morph", "remake", "extend", "recast"):
        with pytest.raises(ValueError, match=r"membership"):
            _check(world, [{"kind": "chart_to", "to": verb, "at": 9.0, "dur": 0.8, "state": 1}])


def test_a_membership_page_is_not_a_prism(tmp_path):
    with pytest.raises(ValueError, match=r"extruded_bar.*membership|membership.*extruded_bar"):
        _world(BUILDERS, tmp_path, ";form=extruded_bar")
    assert _world(BUILDERS, tmp_path / "soft", ";bar_style=soft")["page"]["bar_style"] == "soft"


def test_the_species_is_wired_everywhere_a_species_is_read():
    sys.path.insert(0, str(ROOT / "content/video_engine/scripts/authoring"))
    import gate_motion_density as MG
    import lint_species_choice as LSC
    import recipe_walk as RW
    from authoring import shapes as SH
    assert MG.SPECIES_EVENTS["member"] == ("at",), "a tile landing on its word is one event"
    assert "member" in LSC.ACT_SPECIES["DIVIDES"]
    assert "member" in RW.PAGE_SPECIES_KINDS
    assert "member" in SH.PLOT_MARKS


# ---- (4) + (5) the player -------------------------------------------------------------------------------------------

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, stage = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  const op = (el) => { let o = 1; for (let e = el; e && e !== st.chart; e = e.parentNode) { const a = e.getAttribute && e.getAttribute('opacity'); if (a != null) o *= +a; } return o; };
  return {
    tiles: (st.memberTiles || []).map(m => ({ bar: m.bar, j: m.j, name: m.name, logo: m.logo || null, box: R(m.box),
      op: op(m.box), tf: m.g.getAttribute('transform') || '', stroke: m.box.style.stroke || '',
      img: m.img ? m.img.getAttribute('href') : null, imgBox: m.img ? R(m.img) : null,
      text: m.text ? m.text.textContent : null, textBox: m.text ? R(m.text) : null,
      fs: m.text ? parseFloat(m.text.style.fontSize) : null })),
    keys: (st.memberKeys || []).map(k => ({ bar: k.bar, text: k.el.textContent, box: R(k.el), op: op(k.el) })),
    bars: (st.bars || []).map(b => ({ box: R(b.bar), val: b.val && getComputedStyle(b.val).display !== 'none' && op(b.val) > 0.01 ? R(b.val) : null })),
    pill: st.callout && op(st.callout) > 0.01 ? R(st.callout) : null,
    hatch: !!st.soft, buildDur: st.buildDur || null,
    ink: [...st.page.querySelectorAll('.lp-src, .lp-sub, .lp-title')].map(R).concat((st.bars || []).map(b => R(b.lab))),
    tileEls: st.chart.querySelectorAll('.lp-tile').length, keyEls: st.chart.querySelectorAll('.lp-member-key').length,
  };
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

BAR_UP = 6.05    # bar 0 stands at cb 0.55 of the build (4.4 + 0.55 x 3.0): its value lands by then
CASCADE0 = 4.4 + 3.0 + 0.25   # the default cascade: the ordinary build over, then LPMEMBER.LEAD_S
STEP, LAND = 0.34, 0.45       # the count array's step and landing (COUNT_ARRAY_STEP / COUNT_ARRAY_LAND_S)
SPOKEN = [8.0, 8.9, 9.6, 10.4, 11.2]   # a tile on each name's word
LIGHT_AT = 12.5

# key -> (object, row options, species, aspect, instants)
CASES = {
    "builders": (BUILDERS, "", [], "16:9", [BAR_UP - 0.2, CASCADE0 + 0.5 * STEP + 0.1, 11.0]),
    "spoken": (BUILDERS, "", [{"kind": "member", "at": t, "dur": 0.45, "tile": j} for j, t in enumerate(SPOKEN)]
               + [{"kind": "member", "at": LIGHT_AT, "dur": 0.45, "tile": 2, "light": True}], "16:9",
               [SPOKEN[1] - 0.05, SPOKEN[1] + LAND + 0.05, LIGHT_AT - 0.05, LIGHT_AT + 0.6]),
    "basket": (BASKET, "", [], "16:9", [11.0]),
    "basket-portrait": (BASKET, "", [], "9:16", [11.0]),   # two bars on a portrait page: no side holds the key, so it stands OVER the bar
    "soft": (BUILDERS, ";bar_style=soft", [], "16:9", [11.0]),
    "portrait": (BUILDERS, "", [], "9:16", [11.0]),
    "plain": ({k: v for k, v in BUILDERS.items() if k != "member_noun"} | {"bars": [{k: v for k, v in BUILDERS["bars"][0].items() if k != "members"}]},
              "", [], "16:9", [11.0]),
}


@pytest.fixture(scope="module")
def painted(tmp_path_factory):
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright

    tmp = tmp_path_factory.mktemp("members")
    out = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for key, (obj, opt, species, aspect, ts) in CASES.items():
                w, h = RB.STAGE[aspect]
                world = _world(obj, tmp / key, opt, aspect)
                scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
                           "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": copy.deepcopy(species)}]
                tl = G._timeline("P69 T45 " + key, scenes, {}, aspect)
                uris = dict(G._base_uris(), **B.member_assets(tl))
                html = tmp / f"{key}.html"
                html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
                srv, port = RB.serve(html.parent)
                page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                errors: list[str] = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                try:
                    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(page, w, h)
                    page.wait_for_function("document.fonts.status === 'loaded'")
                    got = {"errors": errors, "at": {}, "uris": uris}
                    for t in ts:
                        RB.frame_png(page, t, (w, h))
                        got["at"][t] = page.evaluate(PROBE)
                    if key == "spoken":   # a cold seek BACK lands what forward play landed
                        RB.frame_png(page, ts[0], (w, h))
                        got["back"] = page.evaluate(PROBE)
                    out[key] = got
                finally:
                    page.context.close()
                    srv.shutdown()
        finally:
            browser.close()
    return out


def _inside(a, b, tol=1.0) -> bool:
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[0] + a[2] <= b[0] + b[2] + tol and a[1] + a[3] <= b[1] + b[3] + tol


def _meets(a, b) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


@needs_browser
@pytest.mark.parametrize("key", ["builders", "soft", "portrait"])
def test_the_tiles_divide_the_bar_equally_bottom_up_inside_it(painted, key):
    got = painted[key]
    assert not got["errors"], got["errors"]
    p = got["at"][11.0]
    tiles, bar = p["tiles"], p["bars"][0]["box"]
    assert [t["name"] for t in tiles] == FIVE and [t["j"] for t in tiles] == list(range(5))
    hs = [t["box"][3] for t in tiles]
    assert max(hs) - min(hs) <= 0.75, ("EQUAL tiles - never sized (s101)", hs)
    ws = {round(t["box"][2], 1) for t in tiles}
    assert len(ws) == 1, ws
    for t in tiles:
        assert t["op"] > 0.99 and _inside(t["box"], bar), (t, bar)
    ys = [t["box"][1] for t in tiles]
    assert ys == sorted(ys, reverse=True), "tile 0 stands on the zero line; the stack runs UP"
    gaps = [ys[k] - (ys[k + 1] + hs[k + 1]) for k in range(4)]
    assert max(gaps) - min(gaps) <= 0.75 and min(gaps) > 0, gaps
    span = (ys[0] + hs[0]) - ys[-1]
    assert span >= 0.9 * bar[3], ("the tiles fill the bar they divide", span, bar)


@needs_browser
@pytest.mark.parametrize("key", ["builders", "soft", "portrait", "basket", "basket-portrait"])
def test_the_total_is_written_over_the_bar_and_the_key_beside_it(painted, key):
    p = painted[key]["at"][11.0]
    noun = "stock" if key.startswith("basket") else "company"
    for bi, b in enumerate(p["bars"]):
        total = b["val"] or (p["pill"] if bi == 0 else None)   # its value, or the emphasized bar's pill (T6: the value yields to it)
        assert total, "the bar's total is written"
        assert total[1] + total[3] <= b["box"][1] + 1, ("... ABOVE the bar, never inside the tiles", total, b["box"])
    keys = p["keys"]
    assert keys and all(k["text"].replace(" ", " ") == f"each tile = one {noun}" for k in keys), keys
    for k in keys:
        assert k["op"] > 0.99
        for t in p["tiles"]:
            assert not _meets(k["box"], t["box"]), ("the key never sits on a tile", k, t)
        for b in p["bars"]:
            assert not _meets(k["box"], b["box"]), ("... nor on a bar", k, b)
        for box in p["ink"] + [b2["val"] for b2 in p["bars"] if b2["val"]] + ([p["pill"]] if p["pill"] else []):
            assert not _meets(k["box"], box), ("... nor on the page's words (title, sub, source, a bar's name, a total)", k, box)
    assert len(keys) == 1, "one key for the page, beside its first membership bar"


@needs_browser
@pytest.mark.parametrize("key", ["builders", "soft", "portrait"])
def test_every_name_is_written_inside_its_own_tile(painted, key):
    for t in painted[key]["at"][11.0]["tiles"]:
        assert t["text"] and t["img"] is None
        assert _inside(t["textBox"], t["box"], tol=0.5), ("a name never leaves its tile", t)


@needs_browser
def test_a_catalogued_logo_is_the_tile_and_a_member_without_one_is_its_name(painted):
    got = painted["basket"]
    p = got["at"][11.0]
    by = {(t["bar"], t["name"]): t for t in p["tiles"]}
    assert set(by) == {(0, "SK hynix"), (0, "Micron"), (1, "SK hynix"), (1, "Micron")}
    for bi in (0, 1):
        assert by[(bi, "SK hynix")]["text"] == "SK hynix" and by[(bi, "SK hynix")]["img"] is None
    mu = by[(0, "Micron")]
    assert mu["img"] == got["uris"][B.PROP_PREFIX + MICRON] and mu["text"] is None, "the catalogue's own mark"
    assert _inside(mu["imgBox"], mu["box"], tol=0.5) and mu["imgBox"][2] >= 48 - 0.5, "drawn at a size that reads"
    small = by[(1, "Micron")]   # the AFTER bar's tiles are short: its cutout would be a smudge, so the tile NAMES Micron
    assert small["img"] is None and small["text"] == "Micron" and small["logo"] is None, small
    assert _inside(small["textBox"], small["box"], tol=0.5)


@needs_browser
def test_by_default_the_tiles_land_one_per_member_after_the_bar_stands(painted):
    got = painted["builders"]
    before, mid, after = (got["at"][t] for t in CASES["builders"][4])
    assert before["bars"][0]["box"][3] > 0, "the bar is growing"
    assert all(t["op"] < 0.01 for t in before["tiles"]), "no tile before its bar stands"
    ops = [t["op"] for t in mid["tiles"]]
    assert ops[0] > 0.5 and ops[-1] < 0.01, ("one per member, bottom-up", ops)
    assert all(t["op"] > 0.99 and "scale(1)" in t["tf"].replace("scale(1.0000)", "scale(1)") for t in after["tiles"]), after["tiles"]
    assert after["buildDur"] == pytest.approx(3.0 + 0.25 + 4 * STEP + LAND, abs=1e-6), "the cascade is the page's own build"


@needs_browser
def test_a_member_species_lands_its_tile_on_its_word(painted):
    got = painted["spoken"]
    pre, post = got["at"][SPOKEN[1] - 0.05], got["at"][SPOKEN[1] + LAND + 0.05]
    assert pre["buildDur"] is None, "every tile is spoken: the page's build is the plain bars build"
    assert [t["op"] > 0.99 for t in pre["tiles"]] == [True, False, False, False, False], [t["op"] for t in pre["tiles"]]
    assert [t["op"] > 0.99 for t in post["tiles"]] == [True, True, False, False, False], [t["op"] for t in post["tiles"]]
    assert got["back"] == pre, "a seek back lands what play landed (a pure function of t)"


@needs_browser
def test_light_keeps_the_named_tile_and_dims_the_rest_to_e67(painted):
    got = painted["spoken"]
    pre, lit = got["at"][LIGHT_AT - 0.05], got["at"][LIGHT_AT + 0.6]
    assert len(pre["tiles"]) == len(lit["tiles"]) == 5
    assert all(t["op"] > 0.99 and not t["stroke"] for t in pre["tiles"])
    for t in lit["tiles"]:
        if t["j"] == 2:
            assert t["op"] > 0.99 and t["stroke"], t
        else:
            assert t["op"] == pytest.approx(0.45, abs=0.02), t


@needs_browser
def test_without_members_a_bars_page_draws_no_tile_and_no_key(painted):
    p = painted["plain"]["at"][11.0]
    assert p["tileEls"] == 0 and p["keyEls"] == 0 and p["tiles"] == [] and p["keys"] == []
    assert p["buildDur"] is None


def test_the_engine_names_its_dials_once():
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LPMEMBER = Object\.freeze\(\{([^}]*)\}\)", src)
    assert m, "the engine carries the LPMEMBER dial block"
    dials = dict(re.findall(r"([A-Z_]+): ([\d.]+)", m.group(1)))
    assert float(dials["STEP_S"]) == B.COUNT_ARRAY_STEP and float(dials["LAND_S"]) == B.COUNT_ARRAY_LAND_S, dials
    assert float(dials["DIM"]) == 0.45, "E67's dim"
    assert [ln for ln in src.split("\n") if "springPop" in ln and "LPMEMBER" in ln], "the badge spring lands a tile"
