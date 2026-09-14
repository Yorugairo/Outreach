"""R26-48 / P52 T4 - the element-by-element ink diff: WHICH element's box moves warm vs cold.

Reproduces the 2026-09-11 measurement named in BACKLOG R26-48. For each instant it walks a WARM
page in (three seeks, as determinism_check.Frames.warm does) and opens a COLD page (painted twice,
as Frames.cold does), then dumps every element under #stage: tag, class, id, its client rect, and
the geometry attributes a text carries (x, y, font-size, text-anchor, dominant-baseline,
textLength, the transform chain). The two dumps are compared key by key.

    python ink_diff.py <build> 7.49 23.10 79.03
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import determinism_check as DC  # noqa: E402

DUMP = r"""
() => {
  const out = [];
  const seen = {};
  const walk = (el, path) => {
    const cls = (el.getAttribute && el.getAttribute('class')) || '';
    /* the class tokens are SORTED: classList.toggle writes them in the order the history touched them, so an
       unsorted key made one element look like two and its rect was never compared at all. */
    const key = el.tagName + '.' + String(cls).trim().split(/\s+/).filter(Boolean).sort().join('_') + (el.id ? '#' + el.id : '');
    seen[key] = (seen[key] || 0) + 1;
    const r = el.getBoundingClientRect();
    const rec = { k: key + '[' + seen[key] + ']', tag: el.tagName,
                  rect: [+r.x.toFixed(3), +r.y.toFixed(3), +r.width.toFixed(3), +r.height.toFixed(3)] };
    if (el.tagName === 'text' || el.tagName === 'tspan') {
      rec.txt = (el.textContent || '').slice(0, 40);
      for (const a of ['x','y','dx','dy','font-size','text-anchor','dominant-baseline','textLength','opacity','transform','style','class'])
        { const v = el.getAttribute(a); if (v !== null) rec[a] = v; }
      const cs = getComputedStyle(el);
      rec.cs = [cs.fontSize, cs.fontFamily, cs.fontWeight, cs.textRendering, cs.dominantBaseline, cs.strokeWidth, cs.paintOrder].join('|');
      try { const bb = el.getBBox(); rec.bbox = [+bb.x.toFixed(3), +bb.y.toFixed(3), +bb.width.toFixed(3), +bb.height.toFixed(3)]; } catch (e) {}
      try { rec.len = +el.getComputedTextLength().toFixed(4); } catch (e) {}
    }
    rec.path = path;
    rec.cls = String(cls).trim();                       /* the RAW class string, order and all */
    out.push(rec);
    for (const c of el.children) walk(c, path + '/' + el.tagName + (el.id ? '#' + el.id : ''));
  };
  const stage = document.getElementById('stage') || document.body;
  walk(stage, '');
  return { rows: out, fonts: document.fonts.status, size: [innerWidth, innerHeight] };
}
"""


def dump_warm(F, t):
    F.warm(t)                       # the same approach determinism_check uses, then read the DOM
    return F.warm_page.evaluate(DUMP)


def dump_cold(F, t):
    import render_baseline as RB
    page = F._open()
    try:
        RB.frame_png(page, t, (F.w, F.h))
        RB.frame_png(page, t, (F.w, F.h))
        return page.evaluate(DUMP)
    finally:
        page.context.close()


def compare(t, w, c, log=print):
    W = {r["k"]: r for r in w["rows"]}
    C = {r["k"]: r for r in c["rows"]}
    log(f"\n=== t={t:.2f}   warm {len(W)} el / cold {len(C)} el   fonts warm {w['fonts']} cold {c['fonts']}")
    only = sorted(set(W) ^ set(C))
    if only:
        log(f"  elements on one side only ({len(only)}): {only[:12]}")
    diffs = 0
    for k in sorted(set(W) & set(C)):
        a, b = W[k], C[k]
        keys = sorted(set(a) | set(b))
        moved = [kk for kk in keys if kk != "k" and a.get(kk) != b.get(kk)]
        if not moved:
            continue
        diffs += 1
        log(f"  [DIFF] {k}  {a.get('txt', '')!r}")
        for kk in moved:
            log(f"         {kk}: warm {a.get(kk)}   cold {b.get(kk)}")
    if not diffs and not only:
        log("  the DOM is IDENTICAL element by element (box, geometry, computed type) - the raster differs, not the DOM")
    else:
        log(f"  {diffs} element(s) differ")
    return diffs


def main(argv):
    build = Path(argv[0])
    instants = [float(x) for x in argv[1:]] or [7.49, 23.10, 79.03]
    with DC.Frames(build) as F:
        for t in instants:
            w = dump_warm(F, t)
            c = dump_cold(F, t)
            compare(t, w, c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
