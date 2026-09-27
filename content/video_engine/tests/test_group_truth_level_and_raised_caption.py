"""P72 T53 (l) / R26-419 - P72 T53 (a)-(e)'s three findings.

  (a) while the pedestal holds the camera RAISED, the stage caption stood on the iceberg's tip and its rule label (the
      page is lowered by the pedestal's reach; the caption kept its place) - it now stands in the SKY the raised camera
      shows above the page, and takes its own place back on the pedestal's word.
  (b) a group bracket's label that writes a FIGURE is the group's own total at the label's precision (level_join's
      `_lj_truth`: a figure the page states is the page's arithmetic) - refused by name otherwise; a label with no
      figure ("Decades", "last year and this") is untouched.
  (c) the far bar's level (P72 T53 (e)) on a page with chart states: the level was computed from the build and, re-read
      per frame, found no bar tops at all - it vanished on every page with a `then=` / extend state. It now re-reads the
      bars as they stand THIS frame (lpBarTopsNow, lerped on the extend's clock).
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402

GROUP = {"kind": "bracket", "form": "group", "at": 8.0, "dur": 1.8, "from": 1, "to": 2}
BARS = {"variant": "bars", "values": [28, 121, 150], "labels": ["2020-24, a year", "2025", "2026E"],
        "value_strings": ["$28B", "$121B", "$150B"]}


# ---- (b) a group's figure is its total ----------------------------------------------------------------------------------

@pytest.mark.parametrize("label", ["$271B together", "271", "the two: $271 billion", "last year and this", "Decades"])
def test_a_group_label_writing_the_groups_total_or_no_figure_stands(label):
    assert B.check_brace(dict(BARS), [dict(GROUP, label=label)], "16:9") == []


@pytest.mark.parametrize("label, said", [("$270B together", "270"), ("$150B", "150"), ("2.3x", "2.3"),
                                          ("-$271B", "-"), ("2025-26", "2025")])
def test_a_group_label_writing_another_figure_is_refused_by_name(label, said):
    with pytest.raises(ValueError) as e:
        B.check_brace(dict(BARS), [dict(GROUP, label=label)], "16:9")
    msg = str(e.value)
    assert "group" in msg and "271" in msg and said in msg, msg


def test_the_precision_is_the_labels_own():
    page = dict(BARS, values=[28.0, 121.4, 150.3], value_strings=None)
    assert B.check_brace(page, [dict(GROUP, label="$272B")], "16:9") == []          # 271.7 at a whole number
    assert B.check_brace(page, [dict(GROUP, label="$271.7B")], "16:9") == []
    with pytest.raises(ValueError, match="271.7"):
        B.check_brace(page, [dict(GROUP, label="$271B")], "16:9")


# ---- (c) the far level on a page with chart states ---------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

LC_OBJ = {"title": "Three years and the next", "sub": "fixture", "src": "fixture - synthetic bars", "unit": "$", "unit_suffix": "B",
          "bars": [{"label": "A", "value": 28, "color": "deemph"}, {"label": "B", "value": 121, "color": "deemph"},
                   {"label": "C", "value": 60, "color": "crimson"},
                   {"label": "D", "color": "crimson", "projected": {"value": 300, "label": "DE", "tier": "PLAUSIBLE", "src": "fixture"}}]}
LC_SPECIES = [{"kind": "bracket", "at": 6.0, "dur": 1.8, "from": 2, "to": 0, "label": "2.1x"},
              {"kind": "chart_to", "to": "extend", "at": 11.0, "dur": 2.5, "bar": 3}]

LC_PROBE = """() => { const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')), st = w.__lp, S = st.states[st.active | 0];
  const b = (st.perform || {}).brackets[0], lv = b.main.level, d = lv ? (lv.getAttribute('d') || '') : null;
  const bars = []; for (let i = 0; S.markBy['b:' + i]; i++) { const q = S.markBy['b:' + i].geom; bars.push([q.x, q.end, q.w]); }
  return { active: st.active | 0, d, bars }; }"""


def _lc_read(times: list[float]) -> list:
    import build_golden_sources as G
    import render_baseline as RB
    import served_player as SP
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-lc.series.json").write_text(json.dumps(LC_OBJ), encoding="utf-8")
        plate, saved = "ledger:fx-lc:bars", B.ASPECT
        B.ASPECT = "16:9"
        try:
            assert B.validate_species(copy.deepcopy(LC_SPECIES), (0, 0, 0), plate) == []
            world = B.world_for_plate(plate, (0, 0, 0), ep)
            B.stamp_full_stage(world["page"])
            B.derive_rescale_states(world, LC_SPECIES, plate, ep)
        finally:
            B.ASPECT = saved
        scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
                   "span": [0.0, G.RUNTIME], "docks": [], "species": copy.deepcopy(LC_SPECIES)}]
        html = ep / "p.html"
        html.write_text(RB.instantiate(G._timeline("R26-419 (c)", scenes, {}, "16:9"), G._base_uris()), encoding="utf-8")
        page, errs, close = SP.open_served(html, *RB.STAGE["16:9"])
        try:
            out = []
            for t in times:
                RB.frame_png(page, t, RB.STAGE["16:9"])
                out.append(page.evaluate(LC_PROBE))
            assert not errs, errs
            return out
        finally:
            close()


@needs_browser
def test_the_far_level_stands_on_a_page_with_states_at_the_far_bars_level_now():
    before, after = _lc_read([9.0, 14.5])
    for f, name in ((before, "before the extend"), (after, "after it")):
        assert f["d"], (f"R26-419 (c): {name} the level is not drawn", f)
        ys = {round(float(v), 1) for v in f["d"].replace("M", " ").replace("L", " ").split()[1::2]}
        assert ys == {round(f["bars"][0][1], 1)}, (f"{name}: the level runs at the far bar's top as it stands now", ys, f["bars"][0])
    assert before["active"] == 0 and after["active"] == 1
    assert abs(before["bars"][0][1] - after["bars"][0][1]) > 20, "the extend moved the far bar's top (the fixture's point)"


# ---- (a) the stage caption under a raised camera -----------------------------------------------------------------------

CAP_PROBE = """() => { const cap = document.getElementById('caption'), stage = document.getElementById('stage').getBoundingClientRect();
  const k = 1080 / stage.height, rg = document.createRange(); rg.selectNodeContents(cap); const r = rg.getBoundingClientRect();
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')), st = w.__lp;
  const box = (e) => { const b = e.getBoundingClientRect(); return [(b.left - stage.left) * k, (b.top - stage.top) * k, (b.right - stage.left) * k, (b.bottom - stage.top) * k]; };
  const words = [...w.querySelectorAll('text, .lp-title, .lp-sub')].filter(e => (e.textContent || '').trim() && e.getBoundingClientRect().height > 0).map(box);
  return { cap: [(r.left - stage.left) * k, (r.top - stage.top) * k, (r.right - stage.left) * k, (r.bottom - stage.top) * k],
           text: (cap.textContent || '').trim(), page: box(st.page), words }; }"""


def _cap_read(times: list[float]) -> list:
    import build_golden_sources as G
    import render_baseline as RB
    import served_player as SP
    tl, uris = G.iceberg_stage()
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    page, errs, close = SP.open_served(html, *RB.STAGE["16:9"], cleanup=td.cleanup)
    try:
        out = []
        for t in times:
            RB.frame_png(page, t, RB.STAGE["16:9"])
            out.append(page.evaluate(CAP_PROBE))
        assert not errs, errs
        return out
    finally:
        close()


def _meet(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


@needs_browser
def test_the_stage_caption_stands_in_the_sky_while_the_pedestal_holds_the_camera_raised():
    import build_golden_sources as G
    raised, landed = _cap_read([4.5, G.ICE_AT + G.ICE_S + 1.0])
    assert raised["text"] and landed["text"], (raised, landed)
    hit = [w for w in raised["words"] if _meet(raised["cap"], w)]
    assert not hit, ("R26-419 (a): the raised caption stands on the page's words (the tip's $261B, the rule label)", raised["cap"], hit[:3])
    assert raised["cap"][3] <= raised["page"][1], ("it stands in the sky ABOVE the lowered page", raised["cap"], raised["page"])
    assert landed["cap"][1] > raised["cap"][1] + 200, ("the pedestal's word gives the caption its own place back", landed["cap"])
