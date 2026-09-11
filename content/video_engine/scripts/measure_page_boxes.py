"""Measure a ledger page's boxes in the PLAYER and write the fixture the compiler reads (P50 T16, R26-27).

`ledger_page.page_boxes` models where a page puts its ink. The model's LAW is the template's own -
given the ink heights, the chart's top, the plot's L/R/T/B and the source line land on the player's
pixel - but the INK is estimated, because only the browser can measure Kalam. A title the player
writes in one line is estimated at two, and every box under it moves 76 px on a 9:16 page: R26-27,
"the x maths is exact, only y is off", and the tea cup that landed on the chart in the sixth watch.

This tool renders ONE representative page per builder per aspect through the same headless player
`render_baseline.py` renders the goldens with, reads the boxes off the DOM, and writes them to
`content/video_engine/assets/page-boxes.v1.json` with the sha of the template they were measured
from. `page_boxes` then returns the MEASURED boxes for any page whose ink matches (a page's boxes
are a pure function of its ink - see `ledger_page.page_ink_key`), so `free_bands`, `page_place` and
`centred_place` place against the player's own numbers instead of against three estimates of them.

    python measure_page_boxes.py --list
    python measure_page_boxes.py --write                     # re-measure everything, rewrite the fixture
    python measure_page_boxes.py --check                     # re-measure, diff against the file, exit 1 on drift
    python measure_page_boxes.py --builder tiers --aspect 9:16   # one page, printed, nothing written

THE PAGES. Four are the committed golden sources' own (the cheapest pages in the repo to
instantiate - they are already JSON on disk); `share` has no golden and carries its own synthetic
series here, deterministic and stdlib-only like `build_golden_sources.py`'s.

THE TREEMAP'S ONE LOOP. `ledger_page.treemap_cells` squarifies into `page_boxes`' plot, so writing a
treemap entry changes the layout of the NEXT treemap page built - which changes the plot the player
fits it into. `--passes` re-measures until the numbers stop moving (2 is enough in practice); a
single pass plus `--check` says the same thing more cheaply.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "content/video_engine/scripts"
GOLDEN = REPO / "content/video_engine/tests/golden"
FIXTURE = REPO / "content/video_engine/assets/page-boxes.v1.json"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(GOLDEN))

import build_scene_timeline_f as BST  # noqa: E402  (free_bands: the bands the fixture records)
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

ASPECTS = ("16:9", "9:16")
MEASURE_T = 20.0   # well past the page's build (roll 0.7 + savor 0.8 + field + punch + build = 7.4 s), before nothing

# The representative page per builder: `(golden surface, page_states index or None)`. A page's boxes
# are a function of its ink alone, so ONE page per builder is the whole of what there is to measure.
GOLDEN_PAGES = {
    "dense-line": ("ledger-page-mid-build", None),
    "story": ("ledger-keyed", 0),      # the `then=` bars state of the keyed recast golden
    "tiers": ("tiers-two", None),
    "treemap": ("treemap-cross", None),
}
# `share` has no golden surface: its series lives here, and is a SHAPE, not a figure about the world.
SHARE_SERIES = {
    "title": "One holder, four claims",
    "sub": "share of the whole, one year",
    "src": "Synthetic shares for the box fixture; not a figure about the world",
    "unit": "%",
    "peel": 0,
    "shares": [{"label": "Memory", "value": 46.0}, {"label": "Chips", "value": 24.0},
               {"label": "Mega-cap", "value": 18.0}, {"label": "The rest", "value": 12.0}],
    "total": 100,
}
# keys a page carries about how it ARRIVES, not about where its ink lands: stripped so every page is
# measured on the same plain roll-out clock
TRANSIENT = ("enter", "exit", "mount_s", "morph_s", "spiral_from", "snap_from")

READ_BOXES = r"""
() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect();
    return {x: r.x - stg.x, y: r.y - stg.y, w: r.width, h: r.height}; };
  const U = (a, b) => !a ? b : !b ? a : {x: Math.min(a.x, b.x), y: Math.min(a.y, b.y),
    w: Math.max(a.x + a.w, b.x + b.w) - Math.min(a.x, b.x), h: Math.max(a.y + a.h, b.y + b.h) - Math.min(a.y, b.y)};
  const worlds = [...document.querySelectorAll('.world')];
  const wB = document.getElementById('wB') || worlds[worlds.length - 1];
  if (!wB || !wB.__lp) return null;
  const st = wB.__lp, out = {};
  const one = (sel) => { const el = wB.querySelector(sel); return el ? R(el) : null; };
  out.title = one('.lp-title'); out.sub = one('.lp-sub:not(.lp-note)');
  out.source = one('.lp-src'); out.chart = one('.lp-chart');
  const rail = one('.lp-rail');
  out.rail = rail || (out.source ? {x: out.source.x, y: out.source.y + out.source.h, w: out.source.w, h: 0} : null);
  /* THE PLOT. The chart's own declared pin box through its screen CTM (viewBox + park + camera) when the
     builder declares one; the marks it drew when it does not (bars). Then WIDENED over the ink that lives
     inside the plot - the basis label above it and the x tick labels below the axis - which is exactly what
     `ledger_page.page_boxes` promises its `plot` is, and what a card may never cover. */
  const chart = wB.querySelector('.lp-chart');
  let plot = null;
  if (chart) {
    const m = chart.getScreenCTM();
    if (st.plot && m) { const P = st.plot;
      const pt = (x, y) => [m.a * x + m.c * y + m.e - stg.x, m.b * x + m.d * y + m.f - stg.y];
      const a = pt(P.L, P.T), b = pt(P.W - P.R, P.B);
      plot = {x: Math.min(a[0], b[0]), y: Math.min(a[1], b[1]), w: Math.abs(b[0] - a[0]), h: Math.abs(b[1] - a[1])};
    } else {
      for (const el of chart.querySelectorAll('rect.bar, path.ser, path.wedge, line.ax, line.grid, line.hrule')) {
        const r = R(el); if (r.w >= 1 || r.h >= 1) plot = U(plot, r);
      }
    }
    for (const mk of (st.marks || [])) {
      if (mk.role !== 'axislabel' && mk.role !== 'xtick') continue;
      const r = mk.el ? R(mk.el) : null; if (r && (r.w >= 1 || r.h >= 1)) plot = U(plot, r);
    }
  }
  out.plot = plot;
  out.stage = [stg.width, stg.height];
  return out;
}
"""


def _strip(page: dict) -> dict:
    return {k: v for k, v in page.items() if k not in TRANSIENT}


def representative(builder: str) -> dict:
    """The page spec this builder is measured on - pure, and the same one the tests rebuild."""
    if builder == "share":
        return LPG.build_spec(SHARE_SERIES, "share", 0, "right")
    surface, state = GOLDEN_PAGES[builder]
    tl = json.loads((RB.SOURCES / f"{surface}.timeline.json").read_text(encoding="utf-8"))
    world = next(s["world"] for s in tl["scenes"] if (s.get("world") or {}).get("page"))
    page = world["page"] if state is None else world["page_states"][state]
    if page.get("builder") != builder:
        raise SystemExit(f"{surface}: expected a {builder} page, found {page.get('builder')!r}")
    return _strip(page)


BUILDERS = tuple(sorted(set(GOLDEN_PAGES) | {"share"}))


def _timeline(page: dict, aspect: str) -> dict:
    """One scene, one page, no docks, no species, no Ken Burns: nothing that could move a box."""
    tl = {
        "schema_version": "scene_evidence_timeline.v1", "runtime_s": 30.0,
        "title": "page-boxes measurement", "subtitle": f"{page.get('builder')} {aspect}",
        "episode_id": "page-boxes", "project_id": "page-boxes",
        "narration": {"canonical_hash": "0" * 64, "words_path": ""},
        "captions": [], "caption_pages": [], "caption_modes": ["stage", "anchor"], "sound": [], "evidence": {},
        "scenes": [{"scene_id": "s01", "exit": "cut", "span": [0.0, 30.0], "docks": [], "species": [],
                    "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}}],
    }
    if aspect == "9:16":
        tl["aspect"] = aspect
    return tl


def _box(raw: dict) -> dict:
    return {"x": round(raw["x"]), "y": round(raw["y"]), "w": round(raw["w"]), "h": round(raw["h"])}


def measure(builder: str, aspect: str, page: dict | None = None) -> dict:
    """The player's own boxes for this builder's representative page, in stage pixels."""
    page = page if page is not None else representative(builder)
    w, h = RB.STAGE[aspect]
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "page-boxes.html"
        html.write_text(RB.instantiate(_timeline(page, aspect), {"__audio__": _silence()}), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(pg, w, h)
                RB.frame_png(pg, MEASURE_T, (w, h))   # seek to t and let the page settle, exactly as a golden does
                dom = pg.evaluate(READ_BOXES)
                br.close()
        finally:
            srv.shutdown()
    if not dom or any(dom.get(k) is None for k in LPG.BOX_KEYS):
        missing = [k for k in LPG.BOX_KEYS if not dom or dom.get(k) is None]
        raise SystemExit(f"{builder} {aspect}: the player drew no {', '.join(missing)} - nothing to measure")
    if [round(v) for v in dom["stage"]] != [w, h]:
        raise SystemExit(f"{builder} {aspect}: stage measured {dom['stage']}, expected {[w, h]}")
    boxes = {k: _box(dom[k]) for k in LPG.BOX_KEYS}
    return {"page": page, "boxes": boxes}


def _silence() -> str:
    sys.path.insert(0, str(GOLDEN))
    import build_golden_sources as BGS
    return BGS.uri("audio/wav", BGS.silent_wav(2.0))


def entry(builder: str, aspect: str, page: dict | None = None) -> dict:
    """One fixture entry: the ink it is valid for, the measured boxes, and the free bands they leave."""
    got = measure(builder, aspect, page)
    boxes = got["boxes"]
    full = dict(LPG.page_boxes(got["page"], aspect), **boxes)   # safe / caption_anchor / stage, over the MEASURED ink
    bands = {b["band"]: {k: round(b[k]) for k in ("x", "y", "w", "h")} for b in BST.free_bands(full)}
    return {"ink": LPG.page_ink_key(got["page"]), "title": got["page"].get("title"),
            "boxes": boxes, "bands": bands}


def template_sha() -> str:
    """P51 T1: the player is two files now - the fixture is stale when EITHER changes."""
    return hashlib.sha256(RB.TEMPLATE.read_bytes() + RB.ENGINE.read_bytes()).hexdigest()


def build(builders: list[str]) -> dict:
    out: dict[str, dict] = {}
    for builder in builders:
        page = representative(builder)
        out[builder] = {aspect: entry(builder, aspect, page) for aspect in ASPECTS}
        for aspect in ASPECTS:
            print(f"  {builder:11} {aspect}  plot={out[builder][aspect]['boxes']['plot']}"
                  f"  bands={ {k: v['y'] for k, v in out[builder][aspect]['bands'].items()} }")
    return {"schema": LPG.PAGE_BOXES_SCHEMA, "measured": str(date.today()),
            "player_sha256": template_sha(), "stage": {a: list(RB.STAGE[a]) for a in ASPECTS},
            "note": "measured by scripts/measure_page_boxes.py - do not hand-edit",
            "builders": out}


def dumps(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--builder", choices=BUILDERS)
    ap.add_argument("--aspect", choices=ASPECTS)
    ap.add_argument("--passes", type=int, default=1, help="re-measure N times (the treemap's layout reads the fixture)")
    args = ap.parse_args(argv)
    if args.list:
        for b in BUILDERS:
            print(f"{b:11} {representative(b).get('title')}")
        return 0
    if args.builder and not (args.write or args.check):
        for aspect in ([args.aspect] if args.aspect else list(ASPECTS)):
            print(json.dumps({args.builder: {aspect: entry(args.builder, aspect)}}, indent=1, sort_keys=True))
        return 0
    builders = [args.builder] if args.builder else list(BUILDERS)
    doc = build(builders)
    for _ in range(max(0, args.passes - 1)):
        FIXTURE.write_text(dumps(doc), encoding="utf-8")
        doc = build(builders)
    if args.check:
        was = FIXTURE.read_text(encoding="utf-8") if FIXTURE.exists() else ""
        now = dumps(doc)
        if was != now:
            print(f"DRIFT: {FIXTURE.relative_to(REPO)} is not what the player draws - run --write", file=sys.stderr)
            return 1
        print(f"PASS {len(builders)} builders x {len(ASPECTS)} aspects measured identical")
        return 0
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(dumps(doc), encoding="utf-8")
    print(f"{FIXTURE.relative_to(REPO)}  {len(builders)} builders x {len(ASPECTS)} aspects  player {doc['player_sha256'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
