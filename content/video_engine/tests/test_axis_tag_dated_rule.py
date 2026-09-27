"""P72 T53 (i) / R26-415 - THE DATED RULE THAT HANGS FROM NO DATUM, AND ONE PRINT OF ITS DATE.

Bravos A56 (BOOM 18:00.5) drops a full-height dashed rule at the projected date with its pill on the axis. Our `axis_tag`
guide dropped only from a datum of its series, and the only datum at the projected year is the estimate's (refused as
data by E77), so P72 T46g's beat carried the pill alone - and "2026E" printed twice (the estimate's end tag and the pill).
`guide: "rule"` is the axis tag's own option (not a new species): the rule belongs to the named x label - it shares the
pill's truth (a tick or a datum the page carries, inside its domain), its clock (axtagStart), its leave and its covering.
It drops from the plot's top to the pill's top, dashed, cut round the page's labels (C14). A page word writing the pill's
own string yields while the pill says it. The fixture is the golden `dated-rule` (H row 16's issuance and its 2026E).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402

TAG = {"kind": "axis_tag", "at": 9.2, "dur": 10.0, "x": 2026}


# ---- the grammar ------------------------------------------------------------------------------------------------------

def test_rule_is_a_guide_word_and_anything_else_is_refused_by_name():
    assert B._validate_axis_tag(dict(TAG, guide="rule")) == []
    assert B._validate_axis_tag(dict(TAG, guide=False)) == [] and B._validate_axis_tag(dict(TAG, guide=True)) == []
    for bad in ("dashed", "Rule", 1, None):
        errs = B._validate_axis_tag(dict(TAG, guide=bad))
        assert errs and "guide" in errs[0] and "'rule'" in errs[0], (bad, errs)


def test_a_rule_at_a_tick_with_no_datum_is_not_warned_as_a_guide_with_nothing_to_drop_from():
    import build_golden_sources as G
    spec = G.dated_rule_series()
    spec = dict(spec, axes={"xticks": spec["xticks"]})
    _xv, warns = B._axis_tag_line(spec, dict(TAG, guide="rule"), "t")
    assert not [w for w in warns if "no datum" in w], warns
    _xv, warns = B._axis_tag_line(spec, dict(TAG, guide=True), "t")
    assert [w for w in warns if "no datum" in w], "a datum guide at a bare tick still says it has nothing to drop from"


def test_a_rule_on_a_bars_page_is_reported_never_refused():
    spec = {"labels": ["a", "b"], "values": [1, 2]}
    _i, warns = B._axis_tag_bars(spec, {"kind": "axis_tag", "at": 1.0, "x": 1, "guide": "rule"}, "t")
    assert warns and "draws no guide" in warns[0]


def test_the_recipe_asks_for_the_rule():
    import json
    r = json.loads((ROOT / "content/video_engine/effects/recipes/the-box-then-the-dated-rule.json").read_text(encoding="utf-8"))
    tag = [m for m in r["members"] if m["card"] == "page_species:axis_tag"]
    assert tag and tag[0]["options"].get("guide") == "rule"
    proof = (ROOT / "content/video_engine/projects/_proofs/p71-recipes/proof_t26.py").read_text(encoding="utf-8")
    assert '"guide": "rule"' in proof, "the proof beat draws Bravos's full-height rule"


# ---- the served page --------------------------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const w = [wA, wB].filter(e => e.__lp && e.classList.contains('ledger')).pop(), st = w.__lp, PF = st.perform || {};
  const at = PF.axisTags, td = at && at.tags[0];
  if (!td) return null;
  const S = st.states[st.active | 0], P = S.lfPanel || { y: S.plot.T };
  const vis = (e) => { if (getComputedStyle(e).visibility === 'hidden') return false;
    for (let n = e; n && n.id !== 'stage'; n = n.parentElement) { const c = getComputedStyle(n);
      if (c.display === 'none' || +c.opacity < 0.05 || (n.getAttribute && n.getAttribute('opacity') != null && +n.getAttribute('opacity') < 0.05)) return false; }
    return true; };
  const prints = [...w.querySelectorAll('text')].filter(e => (e.textContent || '').trim() === '2026E' && vis(e)).length;
  const d = td.guide.getAttribute('d') || '', ys = [...d.matchAll(/[ML]([\\d.]+) ([\\d.]+)/g)].map(m => +m[2]);
  return { d, op: +td.guide.getAttribute('opacity'), dash: td.guide.getAttribute('stroke-dasharray'), top: P.y,
           ymin: ys.length ? Math.min(...ys) : null, ymax: ys.length ? Math.max(...ys) : null, prints };
}"""


def _read(times: list[float]) -> list:
    import build_golden_sources as G
    import render_baseline as RB
    import served_player as SP
    tl, uris = G.dated_rule()
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    page, errs, close = SP.open_served(html, *RB.STAGE["16:9"], cleanup=td.cleanup)
    try:
        out = []
        for t in times:
            RB.frame_png(page, t, RB.STAGE["16:9"])
            out.append(page.evaluate(PROBE))
        assert not errs, errs
        return out
    finally:
        close()


@needs_browser
def test_the_rule_drops_the_plots_full_height_at_the_date_and_the_date_prints_once():
    import build_golden_sources as G
    before, landed = _read([G.DATED_RULE_AT - 0.3, G.DATED_RULE_AT + 1.0])
    assert before["op"] == 0, ("before the word: no rule", before)
    assert landed["op"] == 1 and landed["d"], landed
    assert landed["dash"] and "3 7" not in landed["dash"], ("dashed, not the datum leader's dots", landed["dash"])
    assert abs(landed["ymin"] - landed["top"]) < 1.0, ("from the plot's own top", landed)
    assert landed["ymax"] > landed["top"] + 300, ("... the plot's full height, down to the pill", landed)
    assert landed["prints"] == 1, ("'2026E' prints ONCE - the pill; the end tag yields", landed["prints"])
