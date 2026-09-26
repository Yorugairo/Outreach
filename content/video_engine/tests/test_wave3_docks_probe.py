"""P72 T46c - the wave-3 follow-ups on docks, the layout probe and the portrait stage.

Each row closes on its own clause (the plan's T46 acceptance: a test per clause, a frame where it is visible):

  R26-393 (a)  a card that chose `under: hover` lifts LIFT_PX and grows one STEP after its contact (P71 T15). The probe
               scored that pose as `moving` (its STATE_TOL_PX 8 < the 10 px lift), so every hovered dock was never
               parked to M25 / M27. The probe now knows the hover's own reach, from the engine's DOCK_HOVER.
  R26-393 (b)  a card that chose `under: blur` AND parks at its date (`park_at`) kept its veil up for its whole life,
               so after the park the veil blurred the ring and the leader it had just drawn - the join. The veil is
               the READ's focus: it clears over the park, so the join is drawn on the sharp chart.
  R26-394      on a re-value the figure at the bar's top counts WITH the bar (P71 T24) while the bar's own value label
               stands down (P72 T18); M26 read only the label or the callout pill, so it read nothing over the whole
               morph. The probe reads a bar's figure when the bar's own number is not up.
  R26-344 / R26-404  a callout ring on a page parked to a third kept its stage size (45.5 x 37.5 px unparked, 44.8 x
               37.3 parked - T19's measure). The ring is the page's annotation: its reach over its datum, its stroke
               and its label take the page's park scale.
  R26-398      a dock at a depth (P58 T6 (a)) rides its plane's share of the camera - golden `dock-depth` pushed its
               badge row off the bottom of the stage. The depth placement keeps the card's whole box, badges
               included, on the stage.

The browser half needs playwright + chromium and is skipped without them.
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
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import probe as PR  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CALLOUT_MJS = ROOT / "content/video_engine/scripts/species/callout.mjs"
STEEL = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
RAILWAY = "ledger:ev-railway-index-v1:line:139:right;idle=live"   # Steel and Paper H row 5 / 9's own page
RING_DATUM = 53


def _chromium() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:  # noqa: BLE001 - no browser on this machine: the frame tests skip, never pass
        return False


needs_chromium = pytest.mark.skipif(not _chromium(), reason="chromium not available")


@pytest.fixture(scope="module")
def GS():
    import build_golden_sources as gs
    return gs


def _read(tl: dict, uris: dict, ts: list[float], js: str, layers: str = "") -> list[tuple[bytes, object]]:
    """Serve the timeline once, seek each t in order, return (png, js result) per t."""
    import render_baseline as RB
    import served_player as SP
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t46c.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, w, h) as (page, errs):
            if layers:
                page.goto(page.url.split("?")[0] + f"?layers={layers}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
            for t in ts:
                png = RB.frame_png(page, t, (w, h))
                out.append((png, page.evaluate(js)))
            assert not errs, errs
    return out


def _probe(tl: dict, uris: dict, instants: list[tuple[float, str]]) -> dict:
    import render_baseline as RB
    with tempfile.TemporaryDirectory() as td:
        b = Path(td)
        (b / "t46c.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
        (b / "player.html").write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with PR.Probe(b, "t46c.timeline.json") as p:
            return PR.probe_doc(b, probe=p, instants=instants)


# ================================================================== R26-393 (a): the hover is a pose, not a flight
def _engine_hover() -> tuple[float, float]:
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const DOCK_HOVER = Object\.freeze\(\{[^}]*?LIFT_PX: ([\d.]+), STEP: ([\d.]+)", src, re.S)
    assert m, "the engine's DOCK_HOVER is where the probe's hover reach is read from"
    return float(m.group(1)), float(m.group(2))


def test_r26_393_the_probe_s_hover_reach_is_the_engine_s_own():
    lift, step = _engine_hover()
    assert (PR.HOVER_LIFT_PX, PR.HOVER_STEP) == (lift, step), "one dial written twice (as MELT_S is): the probe mirrors DOCK_HOVER"


PLACE = {"x": 600.0, "y": 300.0, "w": 400.0, "h": 250.0}


def _hovered(place: dict, lift: float, step: float, h: float) -> list[float]:
    """the box a card at `place` draws when it hovers: lifted, and grown one step about its centre"""
    w2, h2 = place["w"] * step, h * step
    return [place["x"] - (w2 - place["w"]) / 2, place["y"] - lift - (h2 - h) / 2, w2, h2]


def test_r26_393_a_hovering_card_at_its_place_is_parked_and_only_a_hover_widens_the_tolerance():
    lift, step = _engine_hover()
    box = _hovered(PLACE, lift, step, 280.0)
    assert PR._dock_state({"box": box}, {"place": PLACE, "under": "hover"}) == "parked"
    assert PR._dock_state({"box": box}, {"place": PLACE}) == "moving", "a card that names no hover keeps the old tolerance"
    assert PR._dock_state({"box": box}, {"place": PLACE, "under": "blur"}) == "moving", "a blurring card never lifts"
    far = [box[0], box[1] - 40.0, box[2], box[3]]
    assert PR._dock_state({"box": far}, {"place": PLACE, "under": "hover"}) == "moving", "past the hover's own reach it moves"
    read = dict(PLACE, x=100.0)
    assert PR._dock_state({"box": _hovered(read, lift, step, 280.0)}, {"place": PLACE, "read_place": read, "under": "hover"}) == "reading"


@needs_chromium
def test_r26_393_a_the_probe_scores_a_hovering_card_reading_then_parked(GS):
    """The P71 T23 bench as acceptance 1 names it (`under: hover`): the card reads in the empty room, then parks at its
    date. On the base engine the probe called both `moving` (the lift past STATE_TOL_PX)."""
    tl, uris = GS.card_at_date_surface()
    assert tl["scenes"][0]["docks"][0]["under"] == "hover"
    doc = _probe(tl, uris, [(GS.FRAME_T["card-reads-in-the-empty-room"], "read"),
                            (GS.FRAME_T["card-parks-at-its-date"], "parked")])
    got = [d["state"] for i in doc["instants"] for d in i["docks"]]
    assert got == ["reading", "parked"], (got, [d["box"] for i in doc["instants"] for d in i["docks"]])


# ================================================================== R26-393 (b): the veil clears over the park
VEIL = """() => { const v = document.getElementById('dockveil');
  return { f: v ? (v.style.backdropFilter || v.style.webkitBackdropFilter || '') : null,
           ring: !!document.querySelector('#species-under .parkring'), lead: !!document.querySelector('#species-under .parklead') }; }"""


def _blur_px(f: str | None) -> float:
    m = re.search(r"blur\(([\d.]+)px\)", f or "")
    return float(m.group(1)) if m else 0.0


@needs_chromium
def test_r26_393_b_a_blurring_card_clears_its_veil_over_the_park_so_the_join_is_sharp(GS):
    tl, uris = GS.card_at_date_surface(under="blur")
    d = tl["scenes"][0]["docks"][0]
    assert d["under"] == "blur" and d.get("park_at"), d
    t_read, t_join = GS.FRAME_T["card-reads-in-the-empty-room"], GS.FRAME_T["card-parks-at-its-date"]
    t_mid = GS.DATE_ENTER + GS.DATE_READ_S + 0.35   # halfway through the park (DOCK_PARK_S 0.7)
    (_a, r), (_b, m), (_c, j) = _read(tl, uris, [t_read, t_mid, t_join], VEIL)
    assert _blur_px(r["f"]) > 7.5, ("the veil is up while the card is read", r)
    assert 0.0 < _blur_px(m["f"]) < _blur_px(r["f"]), ("... and clearing through the park", m)
    assert _blur_px(j["f"]) == 0.0 and j["ring"] and j["lead"], ("the join is drawn on the sharp chart", j)


@needs_chromium
def test_r26_393_b_a_blurring_card_with_no_park_at_keeps_its_veil_to_its_leave(GS):
    """The veil's law for a card that does not join a date is unchanged: up from the enter, down on the leave."""
    import build_golden_sources as gs
    tl, uris = gs.card_at_date_surface(under="blur")
    d = tl["scenes"][0]["docks"][0]
    d.pop("park_at")
    t_join = gs.FRAME_T["card-parks-at-its-date"]
    (_a, j), = _read(tl, uris, [t_join], VEIL)
    assert _blur_px(j["f"]) > 7.5, j


# ================================================================== R26-394: the probe reads a re-counted figure
@pytest.fixture(scope="module")
def revalue_probe(tmp_path_factory):
    import test_bar_revalue as TBR
    import test_compare_on_bars as CB
    if not _chromium():
        pytest.skip("chromium not available")
    world = TBR._world(tmp_path_factory.mktemp("t46c-rv"))
    P = TBR._Page(*CB._one_scene(world, copy.deepcopy(TBR.SPECIES)))
    try:
        ts = [TBR.BEFORE_T, *TBR.HOLD_TS, *TBR.UP_TS[2:5], *TBR.AFTER_TS]
        return {"ts": ts, "doc": P.probe(ts), "errs": list(P.errs)}
    finally:
        P.close()


@needs_chromium
def test_r26_394_m26_reads_the_figure_a_re_value_counts_at_the_bars_top(revalue_probe):
    doc = revalue_probe["doc"]
    assert not revalue_probe["errs"], revalue_probe["errs"]
    fails, read, _worst = G._value_faults(doc)
    assert fails == [], fails
    assert read >= len(revalue_probe["ts"]), f"M26 read {read} printed value(s) over {len(revalue_probe['ts'])} instants"
    srcs = {r.get("vs") for i in doc["instants"] for rec in G._records(i) for r in rec.get("b", []) if r.get("v")}
    assert "fig" in srcs, ("a value read off a figure says so (`vs: fig`)", srcs)


# ================================================================== R26-344 / R26-404: the ring takes the park
RING = """() => { const s = document.getElementById('stage').getBoundingClientRect(), k = 1920 / s.width;
  const co = document.querySelector('#species .co') || document.querySelector('#species-under .co');
  if (!co) return null; const b = co.getBoundingClientRect();
  const w = [...document.querySelectorAll('.world')].find((e) => e.__lp && e.classList.contains('ledger'));
  const st = w && w.__lp, S = st && ((st.states && st.states[st.active | 0]) || st);
  const q = window.__lpDatum(null, 0, DATUM), svg = S && S.chart; let datum = null;
  if (q && svg) { const p = new DOMPoint(q[0], q[1]).matrixTransform(svg.getScreenCTM()); datum = [(p.x - s.left) * k, (p.y - s.top) * k]; }
  const m = co.getCTM(), sc = m ? Math.hypot(m.a, m.b) : 1;   /* the stroke as drawn: its own width through its group's scale */
  return { box: [(b.x - s.left) * k, (b.y - s.top) * k, b.width * k, b.height * k], sw: parseFloat(getComputedStyle(co).strokeWidth) * sc, datum }; }"""
PARK = {"kind": "chart_to", "to": "park", "at": 12.0, "dur": 0.9, "scale": 0.34, "anchor": "left"}


def _ring_scene(GS, park: bool) -> tuple[dict, dict]:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(RAILWAY, (0, 0, 0), STEEL)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    sp = ([dict(PARK)] if park else []) + [{"kind": "callout", "at": 14.0, "dur": 6.0,
                                             "target": {"kind": "datum", "index": RING_DATUM, "series": 0}}]
    sc = {"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
          "span": [0.0, GS.RUNTIME], "docks": [], "species": sp}
    return GS._timeline("T46c ring on a parked page", [sc], {}, None), GS._base_uris()


@needs_chromium
def test_r26_404_a_ring_on_a_parked_page_takes_the_page_s_park_scale(GS):
    js = RING.replace("DATUM", str(RING_DATUM))
    (_p, full), = _read(*_ring_scene(GS, False), [16.0], js)
    (_q, parked), = _read(*_ring_scene(GS, True), [16.0], js)
    assert full and parked, (full, parked)
    rw, rh = parked["box"][2] / full["box"][2], parked["box"][3] / full["box"][3]
    assert 0.25 <= rw <= 0.5 and 0.25 <= rh <= 0.5, (f"the parked ring is {rw:.2f} x {rh:.2f} of its full size", full, parked)
    assert parked["sw"] < full["sw"], ("the stroke takes the park too", full["sw"], parked["sw"])
    for r in (full, parked):
        cx, cy = r["box"][0] + r["box"][2] / 2, r["box"][1] + r["box"][3] / 2
        assert abs(cx - r["datum"][0]) < 0.15 * r["box"][2] + 2 and abs(cy - r["datum"][1]) < 0.15 * r["box"][3] + 2, \
            ("the ring stays round its datum", r)


def test_r26_404_the_callout_s_park_scale_is_an_opt_in_ctx_field_so_an_unparked_ring_paints_its_old_bytes():
    src = CALLOUT_MJS.read_text(encoding="utf-8")
    assert "parkScale" in src, "the callout reads the page's park scale from its ctx"
    eng = ENGINE.read_text(encoding="utf-8")
    assert re.search(r"parkScale: \(tg\) =>", eng), "the engine hands the species a parkScale(target)"


# ================================================================== R26-398: a dock at a depth stays on the stage
CARD = """() => { const s = document.getElementById('stage').getBoundingClientRect(), k = 1920 / s.width;
  const el = [...document.querySelectorAll('.dock')].find((e) => parseFloat(getComputedStyle(e).opacity) > 0.05 && e.getBoundingClientRect().width > 1);
  if (!el) return null; const b = el.getBoundingClientRect();
  const rail = el.querySelector('.rail'), rb = rail ? rail.getBoundingClientRect() : null;
  return { box: [(b.x - s.left) * k, (b.y - s.top) * k, b.width * k, b.height * k],
           rail: rb && rb.height > 0 ? [(rb.x - s.left) * k, (rb.y - s.top) * k, rb.width * k, rb.height * k] : null }; }"""


@needs_chromium
@pytest.mark.parametrize("which", ["hold", "move"])
def test_r26_398_a_dock_at_a_depth_keeps_its_whole_box_badges_included_on_the_stage(GS, which):
    tl, uris = GS.dock_depth()
    t = GS.FRAME_T["dock-depth"] if which == "hold" else 6.56
    (_p, r), = _read(tl, uris, [t], CARD)
    assert r and r["rail"], r
    for x, y, w, h in (r["box"], r["rail"]):
        assert x >= -0.5 and y >= -0.5 and x + w <= 1920.5 and y + h <= 1080.5, (f"t={t}: off the stage", r)


@needs_chromium
def test_r26_398_a_flat_dock_and_a_depth_dock_under_a_still_eye_are_untouched(GS):
    """The keep-on-stage term is the camera's: before the eye moves (t < the focus zoom) the depth card stands at the
    flat card's own box."""
    tl, uris = GS.dock_depth()
    flat = copy.deepcopy(tl)
    flat["scenes"][0]["docks"][0].pop("depth")
    t = GS.CAMERA_LAYERS_AT - 0.2
    (_p, a), = _read(tl, uris, [t], CARD)
    (_q, b), = _read(flat, uris, [t], CARD)
    assert a["box"] == b["box"], (a, b)


# ================================================================== R26-369: the agenda PAGE form holds at 9:16
# doc 49 s49.1: 12 px on a 390 px phone = 34 px on the 1080-wide stage - the least a word on a short may be drawn at
PHONE_FLOOR_PX = 34.0
AGENDA = """() => { const s = document.getElementById('stage').getBoundingClientRect(), k = 1080 / s.width;
  const box = (e) => { const b = e.getBoundingClientRect(); return [(b.x - s.left) * k, (b.y - s.top) * k, b.width * k, b.height * k]; };
  const px = (e) => parseFloat(getComputedStyle(e).fontSize) * (e.getCTM ? Math.hypot(e.getCTM().a, e.getCTM().b) : 1) * k * s.width / 1080;
  const all = (c) => [...document.querySelectorAll('#species .' + c)].filter((e) => e.getBoundingClientRect().width > 1);
  return { rows: all('agrow').map((e) => ({ box: box(e), px: px(e), text: e.textContent })),
           subs: all('agfig').map((e) => ({ box: box(e), px: px(e) })), nums: all('agnum').map((e) => ({ box: box(e), px: px(e) })),
           icons: all('agicon').map((e) => ({ box: box(e) })), meds: all('agmed').map((e) => ({ box: box(e) })) }; }"""


def _agenda(GS, aspect: str | None) -> dict:
    tl, uris = GS.agenda_page()
    if aspect:
        tl["aspect"] = aspect
    (_p, r), = _read(tl, uris, [GS.FRAME_T["agenda-page"]], AGENDA)
    return r


def _meet(a: list[float], b: list[float]) -> float:
    return max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))


@needs_chromium
def test_r26_369_the_agenda_page_form_holds_at_9x16(GS):
    r = _agenda(GS, "9:16")
    assert len(r["rows"]) == 3 and len(r["icons"]) == 3, r
    for row in r["rows"]:
        assert row["px"] >= PHONE_FLOOR_PX, (f"row text {row['px']:.1f} px under the phone floor", row)
    for sub in r["subs"]:
        assert sub["px"] >= PHONE_FLOOR_PX * 0.8, (f"sub {sub['px']:.1f} px", sub)
    for row, sub, icon in zip(r["rows"], r["subs"] or [None] * 3, r["icons"]):
        assert _meet(row["box"], icon["box"]) == 0.0, ("the stamped icon overlaps the row's text", row, icon)
        if sub:
            assert _meet(sub["box"], icon["box"]) == 0.0, ("... or its sub", sub, icon)
    for b in [x["box"] for k in ("rows", "subs", "icons", "meds") for x in r[k]]:
        assert b[0] >= 0 and b[0] + b[2] <= 1080, ("inside the portrait stage", b)


# ================================================================== R26-365 (b) / R26-171: the 9:16 rail is SCALED
# R26-171 AMENDED (2026-09-17, E99 s71): "the rail is SCALED to the stage, never dropped - dropping it at 9:16 left the
# badge ladder a still card for five seconds". The kit dropped it (`_aspect_clean`) and the player drew a portrait
# dock's pills at the landscape card's 13 / 23 px - 13 stage px is 4.7 px on the phone.
def test_r26_365_b_the_kit_emits_a_portrait_dock_s_rail():
    import authoring.shapes as SH
    badges = [{"label": "MAMAA", "value": "+20%"}]
    docks = [("ev-card", 1.0, 5.0, 0, {"badges": list(badges)})]
    out, _species, notes = SH._aspect_clean(docks, [], "9:16", SH.DEFAULTS)
    assert out[0][4].get("badges") == badges, ("the rail is scaled to the stage, never dropped (R26-171 amended)", out, notes)
    assert not [n for n in notes if "not emitted" in n], notes


RAIL = """() => { const s = document.getElementById('stage').getBoundingClientRect(), k = 1080 / s.width;
  const out = [];
  for (const d of document.querySelectorAll('.dock')) {
    if (parseFloat(getComputedStyle(d).opacity) < 0.5 || d.getBoundingClientRect().width < 2) continue;
    for (const p of d.querySelectorAll('.rail .pill')) {
      const b = p.getBoundingClientRect(), sz = (sel) => { const e = p.querySelector(sel); return e && getComputedStyle(e).display !== 'none' && e.textContent.trim()
        ? parseFloat(getComputedStyle(e).fontSize) * b.width / p.offsetWidth * k : null; };
      out.push({ box: [(b.x - s.left) * k, (b.y - s.top) * k, b.width * k, b.height * k], label: sz('.pill-label'), num: sz('.pill-num'), tag: sz('.pill-tag') });
    }
  }
  return out; }"""


def _solo_9x16(GS) -> tuple[dict, dict]:
    """`dock-pair-9x16`'s first card alone: a SOLO portrait dock with its two-badge rail (the pair's mount is open)."""
    tl, uris = GS.SURFACES["dock-pair-9x16"]()
    for sc in tl["scenes"]:
        sc["docks"] = sc["docks"][:1]
        for d in sc["docks"]:
            d.pop("side", None)
    return tl, uris


@needs_chromium
def test_r26_365_b_a_portrait_dock_s_rail_reads_at_the_phone_floor_and_stays_on_the_stage(GS):
    tl, uris = _solo_9x16(GS)
    (_p, pills), = _read(tl, uris, [GS.FRAME_T.get("dock-pair-9x16", 9.0)], RAIL)
    assert len(pills) >= 2, pills
    for p in pills:
        for key in ("label", "num", "tag"):
            if p[key] is not None:
                assert p[key] >= PHONE_FLOOR_PX - 0.5, (f"a pill's {key} at {p[key]:.1f} stage px - under the phone floor", p)
        x, y, w, h = p["box"]
        assert x >= 0 and x + w <= 1080 and y >= 0 and y + h <= 1920, ("the rail stays on the stage", p)


def test_r26_365_b_the_landscape_dock_rail_is_untouched():
    css = (ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html").read_text(encoding="utf-8")
    assert ".pill-label { font-size: 13px;" in css and ".pill-num { font-size: 23px;" in css, "16:9 keeps its pills"


@needs_chromium
def test_r26_369_the_title_fits_its_board_at_9x16(GS):
    js = """() => { const s = document.getElementById('stage').getBoundingClientRect(), k = 1080 / s.width;
      const t = document.querySelector('#species .agtitle'), r = document.querySelector('#species .agrule');
      const b = (e) => { const q = e.getBoundingClientRect(); return [(q.x - s.left) * k, (q.y - s.top) * k, q.width * k, q.height * k]; };
      return { title: b(t), rule: b(r) }; }"""
    tl, uris = GS.agenda_page()
    tl["aspect"] = "9:16"
    (_p, r), = _read(tl, uris, [GS.FRAME_T["agenda-page"]], js)
    assert r["title"][0] + r["title"][2] <= r["rule"][0] + r["rule"][2] + 1.0, ("the title ends inside its own rule", r)
