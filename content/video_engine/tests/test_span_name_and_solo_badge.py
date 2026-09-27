"""P72 T53 (c) + (d) (R26-412 (c), (d); P71 T34's findings) - A SPAN'S NAME CLEARS THE PAGE'S RULE, AND A SOLO'S END
BADGE BOX WAITS FOR ITS TAG.

(c) T34's epoch walk on the GDP page (`ev-equip-ipp-gdp-v2`, its own "Q2 2000 peak - 11.54%" rule): the chart fills its
    box, so a span's name is written INSIDE the band's top - and both "DOT-COM" and "AI" stood ON the rule's dashes
    (base frame: the names' boxes 45.7-87.7 across the rule at 63.0). species/span.mjs now steps a name off any page rule
    it would cross - above it where that is clear of the rule's label, else below - and leaves a name that crosses no
    rule where it stood (span-decade, box-the-last-move).
(d) T34's isolate beat, draft 1: the solo's accent end-badge BOX (P72 T46d's rect under the tag) stood filled and EMPTY
    at the plot's right while the tag waited for the line. The box now takes the tag's own visibility: no tag on the
    page, no box.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

LP = "const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp, PF = st.perform || {};"
BB = "const bb = (el) => { if (!el) return null; const r = el.getBBox(); return [r.x, r.y, r.width, r.height]; };"


def _serve_tl(tl: dict, uris: dict, ts: list[float], js: str):
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t53.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[tl.get("aspect") or "16:9"]
        pg, errs, close = SP.open_served(html, w, h)
        try:
            out = []
            for t in ts:
                pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                out.append(pg.evaluate(js))
            return out, errs
        finally:
            close()


# ---- (c) -------------------------------------------------------------------------------------------------------------------

SPAN_JS = "() => {" + LP + BB + """
  const S = (st.states && st.states.length) ? st.states[st.active | 0] : st;
  const rules = (S.marks || []).filter(m => m.role === 'rule').map(m => m.geom);
  const rl = (S.marks || []).filter(m => m.role === 'rulelabel').map(m => bb(m.el));
  return { rules, rl, names: (PF.spans || []).map(sd => ({ text: sd.label.textContent, op: +(sd.label.getAttribute('opacity') || 0), box: bb(sd.label) })) };
}"""


def test_a_spans_name_never_stands_on_the_pages_peak_rule():
    tl, uris = G.span_clears_the_rule()
    (s,), errs = _serve_tl(tl, uris, [G.FRAME_T["span-clears-the-rule"]], SPAN_JS)
    assert not errs, errs
    assert s["rules"], "the GDP page carries its own peak rule (the fixture's premise)"
    ry = s["rules"][0]["y"]
    assert len(s["names"]) == 2 and all(n["op"] == 1 for n in s["names"]), s["names"]
    for n in s["names"]:
        b = n["box"]
        assert not (b[1] < ry < b[1] + b[3]), (f"R26-412 (c): {n['text']!r} is written ON the rule at y {ry:.1f}", b)
        for r in s["rl"]:
            ov = max(0.0, min(b[0] + b[2], r[0] + r[2]) - max(b[0], r[0])) * max(0.0, min(b[1] + b[3], r[1] + r[3]) - max(b[1], r[1]))
            assert ov == 0, (f"{n['text']!r} steps off the rule onto its label", b, r)


# ---- (d) -------------------------------------------------------------------------------------------------------------------

BADGE_JS = "() => {" + LP + BB + """
  const pp = st.paths.find(p => (p.si | 0) === """ + str(G.SOLO_WAIT_SERIES) + """ && !p.muted);
  const r = pp.badge; if (!r) return { none: true };
  const tagOp = +(pp.name.getAttribute('opacity') ?? 1) * (pp.name.style.opacity === '' ? 1 : +pp.name.style.opacity);
  return { w: +r.getAttribute('width'), op: +(r.getAttribute('opacity') || 0), tagOp };
}"""


def test_the_solo_badge_box_is_not_drawn_before_its_tag_arrives():
    tl, uris = G.solo_badge_waits()
    t_wait, t_tag = G.SOLO_WAIT_T
    (early, late), errs = _serve_tl(tl, uris, [t_wait, t_tag], BADGE_JS)
    assert not errs, errs
    assert not early.get("none"), "the long form's line builder draws the badge's box"
    assert early["tagOp"] == 0, ("the fixture's premise: the solo has landed and the tag has not", early)
    assert early["op"] == 0, ("R26-412 (d): the accent box is drawn EMPTY while its tag waits for the line", early)
    assert late["tagOp"] == 1 and late["op"] == 1 and late["w"] > 0, ("the tag on the page, its box round it", late)


def test_a_box_round_a_standing_tag_is_the_T46d_box_to_the_byte():
    """The committed long-form solo (the tag stood before the word) keeps T46d's box: opacity 1 at 1 s past the word."""
    import test_wave3_page_marks as W3
    s, errs = W3._lf_solo(G.SOLO_CHIPS_AT + 1.0, W3.BADGE_JS)
    assert not errs and s["op"] == "1.000", (s, errs)
