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
    python measure_page_boxes.py --check                     # re-measure, diff the boxes against the file, exit 1 on drift
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

THE FULL-STAGE PAGE (R26-235, 2026-09-18). At 16:9 the compiler stamps a ledger page row `full_stage`
(R26-205: the page IS the plate) and its ink goes into a different box - `ledger_page.
_landscape_full_boxes` instead of `_landscape_boxes`. That geometry was never measured, so
`measured_entry` refused the fixture to a full-stage page and the compiler placed every card and every
camera move on it by the ESTIMATE: the estimate puts the dense-line page's title at y 44 where the frame
draws 39.2 (R26-27's own error, 5 px), so the reachable zoom came out 1.3 px short and E65's `empty` /
`axis` rooms - which need the measured `data_mask` - fell through to `corner` at the legibility floor.
So every 16:9 page is measured TWICE here: as it is declared, and stamped as the compiler stamps it
(`full_stage_variant` calls `build_scene_timeline_f.stamp_full_stage` itself, so the fixture can only
carry a geometry the compiler actually writes). The two are filed under `16:9` and `16:9|full_stage` -
`ledger_page.box_key`, the aspect key with the flag on it - and an entry records its own `full_stage`,
so a page can only ever be served the geometry it is drawn in. A page that is never stamped (a host
plate: its board was measured around a hand) has one 16:9 entry exactly as before.

THE LONG FORM'S PAGES (REVIEW-P69-LANE-B-MERGE-2 N3, 2026-09-23). A `;readability=longform[:<preset>]` page lays
its ink out by its own measure (`ledger_page._longform_full_boxes` estimates it), and a preset moves every box - so
the `profiles` section measures the builders the profile is legal on (`ledger_page.READABILITY_BUILDERS`) each at
every preset, full-stage as the compiler stamps it, keyed `<builder>|longform:<preset>`. `--check` diffs them like
every other entry, a page with that ink is placed by them, and the tests hold the estimate to them. They are
measured with the WHOLE fixture (a one-builder `--builder` run leaves them out, as it leaves the other builders).

THE TREEMAP'S ONE LOOP. `ledger_page.treemap_cells` squarifies into `page_boxes`' plot, so writing a
treemap entry changes the layout of the NEXT treemap page built - which changes the plot the player
fits it into. `--passes` re-measures until the numbers stop moving (2 is enough in practice); a
single pass plus `--check` says the same thing more cheaply.
"""
from __future__ import annotations

import argparse
import copy
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
FULL_STAGE_VARIANT = "full_stage"
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
  /* P69 T10: a longform page's KEY RAIL (the names its end tags gave up), in the top band - only when it holds a pill */
  const key = wB.querySelector('.lp-key');
  if (key && key.querySelector('.lp-kpill')) out.key = R(key);
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
    """`(aspect, {ink: page})` for every ledger page a compiled timeline names.

    The world's page and every `page_states` entry are read in draw order and deduplicated by ink.
    `variant_pages` expands a representative into the flat geometry keys used by the fixture; this
    reader stays a source-timeline view and never invents a nested full-stage family.
    """
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


def full_stage_variant(page: dict) -> dict | None:
    """This page as the COMPILER stamps it at 16:9 (`build_scene_timeline_f.stamp_full_stage`), or None
    for a page that is never stamped - a host plate, whose board was measured around a hand. The stamp
    is the compiler's own and is not re-derived here, so the fixture cannot hold a geometry no build
    writes; `ASPECT` is pinned around the call because the stamp reads that global (a 9:16 build leaves
    it set, and this tool measures both aspects in one process)."""
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        stamped = BST.stamp_full_stage(copy.deepcopy(page))
    finally:
        BST.ASPECT = saved
    return stamped if stamped.get("full_stage") else None


def variant_pages(page: dict, aspect: str) -> dict[str, dict]:
    """`{fixture key: the page as the player draws it}` - every GEOMETRY this page's ink takes at this
    aspect (R26-235). At 9:16 there is one; at 16:9 there are the page as declared and the full-stage
    page the compiler stamps, keyed `16:9` and `16:9|full_stage` by `ledger_page.box_key`. A page that
    already carries the stamp (a 16:9 project's compiled page) measures once, under its own key: the
    fixture records the geometry the timeline draws, never one it does not."""
    out = {LPG.box_key(page, aspect): copy.deepcopy(page)}
    if aspect == "16:9":
        stamped = full_stage_variant(page)
        if stamped is not None:
            out.setdefault(LPG.box_key(stamped, aspect), stamped)
    return out


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
PROFILED = tuple(b for b in BUILDERS if b in LPG.READABILITY_BUILDERS[LPG.LONGFORM])   # N3: dense-line and story


def profile_name(builder: str, preset: str) -> str:
    """The `profiles` section's key for this builder's representative under `longform:<preset>`."""
    return f"{builder}|{LPG.LONGFORM}:{preset}"


def profile_representative(builder: str, preset: str) -> dict:
    """This builder's representative page as a 16:9 row naming `;readability=longform:<preset>` compiles it: stamped
    full-stage (the compiler's own stamp) and then the profile (`ledger_page.apply_longform`, as `world_for_plate`
    does). Pure; the same page the tests rebuild."""
    page = full_stage_variant(representative(builder))
    if page is None:
        raise SystemExit(f"{builder}: its representative is a host plate - the long form is never drawn on one")
    return LPG.apply_longform(page, preset)


def _timeline(page: dict, aspect: str, full_stage: bool | None = None) -> dict:
    """One scene, one page, no docks, no species, no Ken Burns: nothing that could move a box.

    ``aspect`` and the optional full-stage stamp are written into the timeline consumed by the
    renderer.  The optional argument is explicit for callers that need to measure both geometries;
    ``None`` preserves the page's own flag while avoiding mutation of the caller's spec.
    """
    rendered_page = dict(page)
    if full_stage is True:
        rendered_page["full_stage"] = True
    elif full_stage is False:
        rendered_page.pop("full_stage", None)
    tl = {
        "schema_version": "scene_evidence_timeline.v1", "runtime_s": 30.0,
        "title": "page-boxes measurement", "subtitle": f"{page.get('builder')} {aspect}",
        "episode_id": "page-boxes", "project_id": "page-boxes",
        "narration": {"canonical_hash": "0" * 64, "words_path": ""},
        "captions": [], "caption_pages": [], "caption_modes": ["stage", "anchor"], "sound": [], "evidence": {},
        "scenes": [{"scene_id": "s01", "exit": "cut", "span": [0.0, 30.0], "docks": [], "species": [],
                    "world": {"kind": "ledger", "page": rendered_page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}}],
        "aspect": aspect,
    }
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


def measure(builder: str, aspect: str, page: dict | None = None, *, full_stage: bool | None = None) -> dict:
    """The player's own boxes for this builder's representative page, in stage pixels."""
    page = page if page is not None else representative(builder)
    if full_stage is not None:
        page = dict(page)
        if full_stage:
            page["full_stage"] = True
        else:
            page.pop("full_stage", None)
    w, h = RB.STAGE[aspect]
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "page-boxes.html"
        tl = _timeline(page, aspect)
        uris = {"__audio__": _silence(), **BST.longform_assets(tl)}   # N3: a longform page is measured in its own face
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
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
    if dom.get(LPG.KEY_BOX):   # P69 T10: the key rail, on a longform page that has one
        boxes[LPG.KEY_BOX] = _box(dom[LPG.KEY_BOX])
    axis = {k: (_box(dom["axis"][k]) if (dom.get("axis") or {}).get(k) else None) for k in ("x", "y")}
    return {"page": page, "boxes": boxes, "axis": axis,
            "data_mask": data_mask(boxes["plot"], dom.get("data") or [])}


def _silence() -> str:
    sys.path.insert(0, str(GOLDEN))
    import build_golden_sources as BGS
    return BGS.uri("audio/wav", BGS.silent_wav(2.0))


def entry(builder: str, aspect: str, page: dict | None = None, *, full_stage: bool | None = None) -> dict:
    """One fixture entry: the ink it is valid for, the measured boxes, and the free bands they leave.

    ``full_stage`` is kept out of ``page_ink_key`` by design.  The flat fixture key carries the
    geometry, while the entry's boolean marker makes a mismatched hand-edited record fail closed.
    """
    if full_stage is None:
        got = measure(builder, aspect, page)
    else:
        got = measure(builder, aspect, page, full_stage=full_stage)
    boxes = got["boxes"]
    full = dict(LPG.page_boxes(got["page"], aspect), **boxes)   # safe / caption_anchor / stage, over the MEASURED ink
    bands = {b["band"]: {k: round(b[k]) for k in ("x", "y", "w", "h")} for b in BST.free_bands(full)}
    out = {"ink": LPG.page_ink_key(got["page"]), "title": got["page"].get("title"),
           "boxes": boxes, "bands": bands, "axis": got["axis"], "data_mask": got["data_mask"]}
    if LPG.full_stage(got["page"], aspect):   # R26-235: the GEOMETRY this entry was measured in, on the entry itself
        out["full_stage"] = True
    return out


def template_sha() -> str:
    """P51 T1: bind both player files after normalizing checkout line endings. R26-241: recorded on
    `--write` as provenance and never compared by `--check` - a byte is not a box."""
    template = RB.TEMPLATE.read_bytes().replace(b"\r\n", b"\n")
    engine = RB.ENGINE.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(template + engine).hexdigest()


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
            for key, drawn in variant_pages(page, aspect).items():   # R26-235: both 16:9 geometries
                got = entry(str(page.get("builder")), aspect, drawn)
                pages.setdefault(ink, {})[key] = dict(got, builder=page.get("builder"), timeline=_rel(tl))
                print(f"  {str(page.get('builder')):11} {key:16}  {ink}  plot={got['boxes']['plot']}"
                      f"  {str(page.get('title'))[:40]!r}")
    return pages, read


def build(builders: list[str], timelines: list[str] | None = None) -> dict:
    out: dict[str, dict] = {}
    for builder in builders:
        page = representative(builder)
        out[builder] = {}
        for aspect in ASPECTS:
            for key, drawn in variant_pages(page, aspect).items():   # R26-235: both 16:9 geometries
                out[builder][key] = entry(builder, aspect, drawn)
        for key, got in out[builder].items():
            print(f"  {builder:11} {key:16}  plot={got['boxes']['plot']}"
                  f"  bands={ {k: v['y'] for k, v in got['bands'].items()} }")
    pages, read = build_pages(list(timelines or []))
    return {"schema": LPG.PAGE_BOXES_SCHEMA, "measured": str(date.today()),
            "player_sha256": template_sha(), "stage": {a: list(RB.STAGE[a]) for a in ASPECTS},
            "note": "measured by scripts/measure_page_boxes.py - do not hand-edit",
            "projects": sorted(read), "pages": pages, "builders": out,
            "profiles": build_profiles(list(PROFILED)) if set(builders) >= set(BUILDERS) else {}}   # N3: with the whole fixture


def build_profiles(builders: list[str]) -> dict:
    """N3: the `profiles` section - each profiled builder's representative at every longform preset, full-stage."""
    out: dict[str, dict] = {}
    for builder in builders:
        for preset in LPG.LONGFORM_PRESETS:
            page = profile_representative(builder, preset)
            key = LPG.box_key(page, "16:9")
            got = entry(builder, "16:9", page)
            out[profile_name(builder, preset)] = {key: dict(got, builder=builder)}
            print(f"  {profile_name(builder, preset):26} {key:16}  chart={got['boxes']['chart']}"
                  f"  source={got['boxes']['source']}")
    return out


def dumps(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


# R26-241: WHEN the fixture was measured and FROM WHICH player bytes. Both stay on file as provenance
# and neither is compared: an engine byte that moves no box (a stamp's easing, a comment) is not drift,
# and a byte-for-byte compare against the sha and the date turned `--check` red on every engine slice.
PROVENANCE = ("measured", "player_sha256")
SECTIONS = ("builders", "pages", "profiles")   # compared entry by entry, so a drift line can say WHICH box moved
NAMED_PARTS = {"boxes": "", "bands": "band ", "axis": "axis "}   # an entry's parts whose members are boxes


def _short(value) -> str:
    text = json.dumps(value, sort_keys=True)
    return text if len(text) <= 80 else text[:77] + "..."


def _entry_drift(where: str, was, now) -> list[str]:
    """One line per difference between two measurements of one page in one geometry."""
    if was is None:
        return [f"{where}: measured now, not on file"]
    if now is None:
        return [f"{where}: on file, no longer measured"]
    if not (isinstance(was, dict) and isinstance(now, dict)):
        return [f"{where}: {_short(was)} -> {_short(now)}"] if was != now else []
    out = []
    for key in sorted(set(was) | set(now)):
        a, b = was.get(key), now.get(key)
        if a == b:
            continue
        if key in NAMED_PARTS and isinstance(a, dict) and isinstance(b, dict):
            out += [f"{where} {NAMED_PARTS[key]}{box}: {_short(a.get(box))} -> {_short(b.get(box))}"
                    for box in sorted(set(a) | set(b)) if a.get(box) != b.get(box)]
        else:
            out.append(f"{where} {key}: {_short(a)} -> {_short(b)}")
    return out


def _builder_of(*entries) -> str:
    return str(next((e["builder"] for e in entries if isinstance(e, dict) and e.get("builder")), None))


def drift(was: dict, now: dict) -> list[str]:
    """Every difference between the fixture on file and a fresh measurement, the provenance excluded.

    A representative is named `<builder> <aspect> <box>` and a project page `<builder> <ink> <aspect>
    <box>`, the aspect being the fixture key - a full-stage page reads `16:9|full_stage`."""
    was = was if isinstance(was, dict) else {}
    out = [f"{key}: {_short(was.get(key))} -> {_short(now.get(key))}"
           for key in sorted(set(was) | set(now))
           if key not in PROVENANCE and key not in SECTIONS and was.get(key) != now.get(key)]
    for section in SECTIONS:
        sa, sb = was.get(section) or {}, now.get(section) or {}
        for name in sorted(set(sa) | set(sb)):
            fa, fb = sa.get(name) or {}, sb.get(name) or {}
            if not (isinstance(fa, dict) and isinstance(fb, dict)):
                out.append(f"{section} {name}: {_short(fa)} -> {_short(fb)}")
                continue
            for aspect in sorted(set(fa) | set(fb)):
                ea, eb = fa.get(aspect), fb.get(aspect)
                label = name if section != "pages" else f"{_builder_of(eb, ea)} {name}"
                out += _entry_drift(f"{label} {aspect}", ea, eb)
    return out


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
        page = representative(args.builder)
        for aspect in ([args.aspect] if args.aspect else list(ASPECTS)):
            for key, drawn in variant_pages(page, aspect).items():
                print(json.dumps({args.builder: {key: entry(args.builder, aspect, drawn)}}, indent=1, sort_keys=True))
        return 0
    builders = [args.builder] if args.builder else list(BUILDERS)
    timelines = [_rel(Path(p)) for p in args.project] + recorded_projects()
    doc = build(builders, timelines)
    for _ in range(max(0, args.passes - 1)):
        FIXTURE.write_text(dumps(doc), encoding="utf-8")
        doc = build(builders, timelines)
    if args.check:
        try:
            was = json.loads(FIXTURE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            was = {}
        lines = drift(was, doc)
        if lines:
            print(f"DRIFT: {_rel(FIXTURE)} is not what the player draws - run --write", file=sys.stderr)
            for line in lines:
                print(f"  {line}", file=sys.stderr)
            return 1
        print(f"PASS {len(builders)} builders x "
              f"{sum(len(v) for v in doc['builders'].values())} geometr(ies) measured identical")
        return 0
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(dumps(doc), encoding="utf-8")
    print(f"{FIXTURE.relative_to(REPO)}  {len(builders)} builders x "
          f"{sum(len(v) for v in doc['builders'].values())} geometr(ies)"
          f"  + {len(doc['pages'])} project page(s) from {len(doc['projects'])} timeline(s)"
          f"  player {doc['player_sha256'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
