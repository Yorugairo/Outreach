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
    python measure_page_boxes.py --write --project content/video_engine/projects/.../tokyo-tea-break/build-short-t0

AN EPISODE'S OWN PAGES (R26-51). A builder has ONE representative here; an episode has as many
pages as it writes titles, and every one of them is an estimate until it is measured - Tokyo's
first page is a one-line title the model calls two, which moves every box under it by 76 px. So
`--project <dir>` reads a build's COMPILED timeline - `world.page` and every `world.page_states`
entry, exactly as the compiler wrote them, never re-derived here - and measures each distinct page
at the aspect that timeline declares, into the fixture's ink-keyed `pages` section (`ledger_page.
measured_pages`). The timelines measured are RECORDED in the fixture, so a later plain `--write`
re-measures them too and reproduces the whole file; a build directory is a gitignored artifact, so
`--write` on a fresh clone quietly keeps whatever timelines it can still find.

THE ROOM INSIDE THE PLOT (E65, 2026-09-11). A page's real boxes showed that Tokyo's pages leave no
band outside the plot wide enough for a card, and the placer answered "no place" - which the engine
painted as a big centred card over the chart. The operator: *"inside of the empty data would be good,
but it can also land underneath partially over-lapping the axis ... we have complete control over the
scale and placement on the page."* So every entry also carries `data_mask` - a 16 x 16 grid over the
plot, `1` where the DATA's ink touches the cell (the line sampled along its drawn length, the bars'
boxes, the value labels: probe.py's own M25 read) - and `axis`, the x tick labels' band under the plot
and the y tick column beside it, which a card MAY partially overlap. `build_scene_timeline_f.page_place`
falls through outside band -> empty room -> axis -> corner on these.

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
  /* THE AXIS BANDS (E65). The x tick labels under the plot and the y tick column beside it: a card
     may partially overlap these - they are furniture, not the data - and may never overlap the data. */
  const roleBox = (roles) => { let u = null;
    for (const mk of (st.marks || [])) { if (!mk.el || roles.indexOf(mk.role) < 0) continue;
      const r = R(mk.el); if (r.w >= 1 || r.h >= 1) u = U(u, r); } return u; };
  /* `tick` is the GRIDLINE (it spans the plot) - furniture the data is drawn over, never a band. */
  out.axis = {x: roleBox(['xtick', 'xlabel']), y: roleBox(['ylabel'])};
  /* THE DATA'S OWN INK (E65), read exactly as probe.py's M25 reads it: a bar or a number is its box;
     a SERIES is a thin wiggle whose bounding box is mostly empty air, so a path is returned as the
     chain of its DRAWN segments. The mask over these is what says where the plot is empty. */
  /* `.lp-cell` is the TREEMAP's own cell (a <g> holding the tile and its labels): probe.py's M25
     selector does not name it, and a mask that misses it would call a full census page empty. */
  const DATA = 'rect.bar, path.ser, path.wedge, text.val, text.callout, rect.cpill, .lp-cell';
  const SEG = 48;
  const dataBoxes = (el) => {
    const r = R(el);
    const full = [[r.x, r.y, r.w, r.h]];
    if (el.tagName !== 'path' || !el.getPointAtLength || !el.getTotalLength) return full;
    const len = el.getTotalLength(); if (!(len > 0)) return full;
    const off = parseFloat(el.getAttribute('stroke-dashoffset') || '0');
    const da = parseFloat((el.getAttribute('stroke-dasharray') || '0').split(/[ ,]/)[0]) || 0;
    const drawn = da > 0 ? Math.max(0, Math.min(len, len - off)) : len;
    if (drawn <= 0) return [];
    const m = el.getScreenCTM(); if (!m) return full;
    const sw = Math.max(2, (parseFloat(getComputedStyle(el).strokeWidth) || 4) * Math.hypot(m.a, m.b) / 2);
    const pts = [];
    for (let i = 0; i <= SEG; i++) { const q = el.getPointAtLength(drawn * i / SEG);
      pts.push([m.a * q.x + m.c * q.y + m.e - stg.x, m.b * q.x + m.d * q.y + m.f - stg.y]); }
    const out2 = [];
    for (let i = 1; i < pts.length; i++) { const a = pts[i - 1], b = pts[i];
      out2.push([Math.min(a[0], b[0]) - sw, Math.min(a[1], b[1]) - sw,
                 Math.abs(b[0] - a[0]) + 2 * sw, Math.abs(b[1] - a[1]) + 2 * sw]); }
    return out2;
  };
  out.data = [];
  if (chart) for (const el of chart.querySelectorAll(DATA)) for (const bx of dataBoxes(el)) out.data.push(bx);
  out.stage = [stg.width, stg.height];
  return out;
}
"""


def _strip(page: dict) -> dict:
    return {k: v for k, v in page.items() if k not in TRANSIENT}


def project_timeline(path: Path) -> Path:
    """The compiled timeline under `path`: the file itself, or the newest `*.timeline.json` in the
    directory, or the newest one in any build directory under it. A project whose build was never
    run has none - and that is a refusal, not a guess."""
    p = Path(path)
    if p.is_file():
        return p
    found = sorted(p.glob("*.timeline.json")) + sorted(p.glob("*/*.timeline.json"))
    found = [f for f in found if f.is_file()]
    if not found:
        raise SystemExit(f"{p}: no compiled *.timeline.json - build the project first, then measure it")
    return max(found, key=lambda f: f.stat().st_mtime)


def timeline_pages(path: Path) -> tuple[str, dict]:
    """`(aspect, {ink: page})` for every ledger page a compiled timeline names - the world's page
    and each of its `page_states`, in the order they are drawn, deduplicated by ink key."""
    tl = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(tl.get("scenes"), list):
        raise SystemExit(f"{path}: not a compiled timeline (no scenes)")
    aspect = tl.get("aspect") or "16:9"
    if aspect not in ASPECTS:
        raise SystemExit(f"{path}: aspect {aspect!r} is not one of {'|'.join(ASPECTS)}")
    pages: dict[str, dict] = {}
    for scene in tl["scenes"]:
        world = scene.get("world") or {}
        found = ([world["page"]] if isinstance(world.get("page"), dict) else []) + \
                [p for p in (world.get("page_states") or []) if isinstance(p, dict)]
        for page in found:
            spec = _strip(page)
            pages.setdefault(LPG.page_ink_key(spec), spec)
    return aspect, pages


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


MASK_N = 16   # E65: the plot is read on a 16 x 16 grid - ~40 px a cell on a 9:16 page, the scale a card is placed at


def data_mask(plot: dict, data: list, n: int = MASK_N) -> list[str]:
    """`n` rows of `n` characters over the PLOT: `1` where the data's ink touches the cell, `0` where
    the plot is empty. The cell is the unit the placer reasons in, so two segments over one pixel
    count once - probe.py's COVER_CELL idea, on the plot's own grid."""
    cw, ch = plot["w"] / n, plot["h"] / n
    rows = []
    for r in range(n):
        y0, y1 = plot["y"] + r * ch, plot["y"] + (r + 1) * ch
        row = []
        for c in range(n):
            x0, x1 = plot["x"] + c * cw, plot["x"] + (c + 1) * cw
            row.append("1" if any(b[0] < x1 and b[0] + b[2] > x0 and b[1] < y1 and b[1] + b[3] > y0
                                  for b in data) else "0")
        rows.append("".join(row))
    return rows


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
    axis = {k: (_box(dom["axis"][k]) if (dom.get("axis") or {}).get(k) else None) for k in ("x", "y")}
    return {"page": page, "boxes": boxes, "axis": axis,
            "data_mask": data_mask(boxes["plot"], dom.get("data") or [])}


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
            "boxes": boxes, "bands": bands, "axis": got["axis"], "data_mask": got["data_mask"]}


def template_sha() -> str:
    """P51 T1: the player is two files now - the fixture is stale when EITHER changes."""
    return hashlib.sha256(RB.TEMPLATE.read_bytes() + RB.ENGINE.read_bytes()).hexdigest()


def recorded_projects() -> list[str]:
    """The timelines the fixture on file was measured from - repo-relative, as recorded."""
    try:
        doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    got = doc.get("projects") if isinstance(doc, dict) else None
    return [str(p) for p in got] if isinstance(got, list) else []


def _rel(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()


def build_pages(timelines: list[str]) -> tuple[dict, list[str]]:
    """The ink-keyed `pages` section for every compiled timeline named, and the ones actually read.
    A recorded timeline that is gone (a build directory is an artifact) is skipped with a line."""
    pages: dict[str, dict] = {}
    read: list[str] = []
    for name in sorted(set(timelines)):
        path = REPO / name if not Path(name).is_absolute() else Path(name)
        if not Path(path).exists():
            print(f"  (skipped) {name}: not on disk - build it to measure its pages")
            continue
        tl = project_timeline(Path(path))
        aspect, found = timeline_pages(tl)
        read.append(_rel(tl))
        for ink, page in found.items():
            got = entry(str(page.get("builder")), aspect, page)
            pages.setdefault(ink, {})[aspect] = dict(got, builder=page.get("builder"), timeline=_rel(tl))
            print(f"  {str(page.get('builder')):11} {aspect}  {ink}  plot={got['boxes']['plot']}"
                  f"  {str(page.get('title'))[:40]!r}")
    return pages, read


def build(builders: list[str], timelines: list[str] | None = None) -> dict:
    out: dict[str, dict] = {}
    for builder in builders:
        page = representative(builder)
        out[builder] = {aspect: entry(builder, aspect, page) for aspect in ASPECTS}
        for aspect in ASPECTS:
            print(f"  {builder:11} {aspect}  plot={out[builder][aspect]['boxes']['plot']}"
                  f"  bands={ {k: v['y'] for k, v in out[builder][aspect]['bands'].items()} }")
    pages, read = build_pages(list(timelines or []))
    return {"schema": LPG.PAGE_BOXES_SCHEMA, "measured": str(date.today()),
            "player_sha256": template_sha(), "stage": {a: list(RB.STAGE[a]) for a in ASPECTS},
            "note": "measured by scripts/measure_page_boxes.py - do not hand-edit",
            "projects": sorted(read), "pages": pages, "builders": out}


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
    ap.add_argument("--project", action="append", default=[], metavar="DIR",
                    help="a project or build directory whose COMPILED timeline names the pages to measure "
                         "(repeatable; the ones already recorded in the fixture are always re-measured)")
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
    timelines = [_rel(Path(p)) for p in args.project] + recorded_projects()
    doc = build(builders, timelines)
    for _ in range(max(0, args.passes - 1)):
        FIXTURE.write_text(dumps(doc), encoding="utf-8")
        doc = build(builders, timelines)
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
    print(f"{FIXTURE.relative_to(REPO)}  {len(builders)} builders x {len(ASPECTS)} aspects"
          f"  + {len(doc['pages'])} project page(s) from {len(doc['projects'])} timeline(s)"
          f"  player {doc['player_sha256'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
