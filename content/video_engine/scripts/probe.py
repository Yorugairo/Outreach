"""PROBE - the agent's eyes are numbers first (P51 T2).

A DOM probe at t costs ~150 tokens and answers overlaps, sizes and clearances exactly; a
frame costs ~2,800 and answers them worse. Three defects the operator caught by eye on
2026-09-10 were all layout, and all visible in the page's own DOM:

  (i)   a card landed OVER the chart's plot (the fab card over the bars; fixed by parking
        the chart to 0.52)
  (ii)  the page's source line - the citation - stayed full-size UNDER the cards the park
        made room for (E52)
  (iii) the record's paper grew INTO the caption strip

This reads the built player's own DOM at the instants that matter and reports, per instant:
every visible dock, the ledger page's boxes (title / sub / plot / source / rail), the caption
strip, type sizes at the PHONE scale, the overlaps as named pairs with their area, the
clearances to the caption strip and to the safe zone, the camera state and the marks summary.
`--gate` writes `<build>/layout-probe.json` for the M25 row of gate_motion_density.py, which
stays browser-free and reads that file exactly as M18 reads frame-hashes.json.

    python probe.py <build> 58.6 --json
    python probe.py <build> 9.2 36.7 54.5 57.0 58.6 --sheet sheet.png --tile 360
    python probe.py <build> --gate

Every box is [x, y, w, h] in STAGE pixels (1080x1920 portrait, 1920x1080 landscape), read
with getBoundingClientRect so a PARKED chart and a card riding the camera are measured as
DRAWN, not as laid out.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_baseline as RB  # noqa: E402
import gate_motion_density as G  # noqa: E402

PROBE_NAME = "layout-probe.json"          # written beside the timeline, read by M25 (the M18 pattern)
# THE PHONE SCALE. Doc 49 s49.1 states it for type: "12 px on a 390 px phone = 34 px on the
# 1080-wide stage". So a short's stage pixel is 390/1080 of a CSS pixel in the hand; a landscape
# stage is judged on the same phone held sideways, 844 CSS px across 1920.
PHONE_CSS = {"9:16": 390.0, "16:9": 844.0}
# SAFE ZONE (YouTube Shorts chrome): the top 12 % carries the title/search overlay, the bottom
# 20 % the handle, description and action rail, the outer 5 % is lost to rounded corners on some
# devices. A dock inside a band is a WARN - the frame is still legible, the chrome may sit on it.
SAFE_TOP, SAFE_BOTTOM, SAFE_SIDE = 0.12, 0.20, 0.05
# A box this close to `place` / `read_place` is AT it. The spring settles to the pixel, but E49's idle keeps
# breathing afterwards - a 1 % scale on a 1,026 px card is 12 px - so the tolerance is a share of the box.
STATE_TOL_PX, STATE_TOL_SHARE = 8.0, 0.03
DEMOTED_SCALE = 0.95                      # text drawn below this share of its own layout size has been PARKED away (or pulled
                                          # back from): it is a thumbnail beside the card that holds the stage, not reading matter
# AT REST. What a card RESTS on is composition; what it flies over is choreography. A dock is settled
# when it moves less than REST_PX over the next REST_DT - a park covers ~50 px in that window and a throw
# far more, while a settled card's E49 idle drifts well under a pixel.
REST_DT, REST_PX = 0.12, 4.0


def stage_size(aspect: str) -> tuple[int, int]:
    return RB.STAGE.get(aspect or "16:9", RB.STAGE["16:9"])


def phone_css(px: float, aspect: str) -> float:
    """A stage pixel in CSS pixels in the hand."""
    w = stage_size(aspect)[0]
    return px * PHONE_CSS.get(aspect or "16:9", PHONE_CSS["16:9"]) / w


# ---- the page's own DOM, read at t -------------------------------------------------------------------------------

READ_DOCKS = r"""
() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const out = {};
  for (const d of document.querySelectorAll('.dock')) {
    const r = d.getBoundingClientRect(), cs = getComputedStyle(d);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    out[d.dataset.slide || d.id] = [r.x - stg.x, r.y - stg.y, r.width, r.height];
  }
  return out;
}
"""

READ_DOM = r"""
() => {
  /* the DATA and the AXES: what a chart with no declared plot box draws its plot out of */
  const MARKS = 'rect.bar, path.ser, path.wedge, line.ax, line.grid, line.hrule';
  /* the DATA alone - the marks that carry the numbers, and the numbers themselves. A card may sit in
     a chart's empty corner (the Tokyo cup, approved 2026-09-09); it may never sit on the data. */
  const DATA = 'rect.bar, path.ser, path.wedge, text.val, text.callout, rect.cpill';
  const stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect();
    return [r.x - stg.x, r.y - stg.y, r.width, r.height]; };
  const eff = (el) => { let o = 1, e = el;
    while (e && e !== document.documentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity); if (!(o > 0)) return 0;
      const a = e.getAttribute && e.getAttribute('opacity');
      if (a != null && a !== '') o *= parseFloat(a) || 0;
      e = e.parentNode instanceof Element ? e.parentNode : null;
    }
    return o; };
  /* the on-screen scale of an element: an SVG node carries its own CTM (viewBox + the park's
     transform + the camera); an HTML node is measured against its own layout width */
  const sc = (el) => { if (el.getScreenCTM) { const m = el.getScreenCTM(); if (m) return Math.hypot(m.a, m.b); }
    const r = el.getBoundingClientRect(), ow = el.offsetWidth; return ow > 1 ? r.width / ow : 1; };
  const fs = (el) => parseFloat(getComputedStyle(el).fontSize) * sc(el);
  /* an .lp-ink run is WRITTEN glyph by glyph (--w drives the mask): a title the page has
     retitled away still has a box, and no ink in it */
  const written = (el) => { const gs = el.querySelectorAll('.g'); if (!gs.length) return 1;
    let n = 0; for (const g of gs) if (parseFloat(g.style.getPropertyValue('--w') || '0') > 0.02) n++;
    return n / gs.length; };
  /* THE INK, LINE BY LINE. An .lp-ink run is a full-width block whose words sit at its left, and a
     two-line block's bounding box is mostly empty air: the element box made a card parked in the
     page's right-hand quiet space read as "under the sub line" (Tokyo 0:11, approved). What a card
     may not cover is a LINE of written glyphs, so each line is its own box. */
  const inkLines = (el) => {
    const gs = [...el.querySelectorAll('.g')].filter((g) => parseFloat(g.style.getPropertyValue('--w') || '0') > 0.02);
    if (!gs.length) { const b = R(el); return [b]; }
    const boxes = gs.map(R).filter((b) => b[2] >= 1 || b[3] >= 1).sort((a, b) => a[1] - b[1]);
    const rows = [];
    for (const b of boxes) {
      const r = rows[rows.length - 1];
      if (r && b[1] < r[1] + Math.max(4, r[3] * 0.6))
        rows[rows.length - 1] = [Math.min(r[0], b[0]), Math.min(r[1], b[1]), Math.max(r[0] + r[2], b[0] + b[2]) - Math.min(r[0], b[0]),
                                 Math.max(r[1] + r[3], b[1] + b[3]) - Math.min(r[1], b[1])];
      else rows.push(b);
    }
    return rows;
  };
  const txt = (el) => (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40);
  /* WHERE THE DATA IS. A bar or a number is its own box; a SERIES is a thin wiggle, and its bounding
     box is mostly empty air - a card may sit in the corner a rising line leaves free (the Tokyo cup,
     approved 2026-09-09) and may never sit on the line. So a path is returned as the chain of its
     segments, sampled along the part that is DRAWN (the dash offset says how far the pen has got). */
  const SEG = 48;
  const dataBoxes = (el, stg) => {
    const r = el.getBoundingClientRect();
    const full = [[r.x - stg.x, r.y - stg.y, r.width, r.height]];
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
    const out = [];
    for (let i = 1; i < pts.length; i++) { const a = pts[i - 1], b = pts[i];
      out.push([Math.min(a[0], b[0]) - sw, Math.min(a[1], b[1]) - sw,
                Math.abs(b[0] - a[0]) + 2 * sw, Math.abs(b[1] - a[1]) + 2 * sw]); }
    return out;
  };

  const out = { stage: [stg.width, stg.height], docks: [], items: [], plots: [], data: [], nmarks: 0, drawn: [], chart: null, caption: null, marks: null };
  for (const d of document.querySelectorAll('.dock')) {
    const o = eff(d); if (o <= 0.05) continue;
    out.docks.push({ el: d.id, name: d.dataset.slide || d.id, box: R(d), op: o,
                     arriving: d.classList.contains('arriving'), paper: true });
  }
  /* THE PAGE ON SCREEN. Both worlds can hold a ledger page at once - the player paints the PREVIOUS
     scene into wA and THIS scene into wB (`paint(wA, prev || sc); paint(wB, sc)`), and the outgoing one
     keeps its ink and its opacity: it is simply covered. Measured on the Tokyo build at 0:81 and again
     at 0:58 after a backward seek - both times the stale page still stood behind the live one, and
     opacity could not tell them apart. The scene's own world is wB, the last in DOM order, which is
     also the one that paints on top. (The template's own __lpProbe / __camera / __lpDatum take the
     FIRST ledger world and read the stale page when both are pages - reported, not fixed here.) */
  const worlds = [...document.querySelectorAll('.world')];
  const wB = document.getElementById('wB') || worlds[worlds.length - 1];
  const world = wB && wB.__lp && wB.classList.contains('ledger') && eff(wB) > 0.05 ? wB : null;
  /* a pill belongs to the page on screen or to a card - never to the page underneath it */
  for (const p of [...(world ? world.querySelectorAll('.pill') : []), ...document.querySelectorAll('.dock .pill')]) {
    const o = eff(p); if (o <= 0.05) continue;
    const b = R(p); if (b[2] < 1 || b[3] < 1) continue;
    out.docks.push({ el: p.id || 'pill', name: 'pill', box: b, op: o, arriving: false, paper: false });
    /* a pill's own font-size is the box's, 16 px; its LABEL, its number and its tag carry the type */
    const runs = [...p.querySelectorAll('*')].filter((s) => (s.textContent || '').trim() && !s.children.length
      && s.getBoundingClientRect().height >= 2);   /* a run the portrait sheet lays out at nothing is not type on screen */
    out.items.push({ k: 'pill', box: b, px: runs.length ? Math.min(...runs.map(fs)) : fs(p), s: sc(p), txt: txt(p) });
  }
  /* a NOTE carries .lp-sub too (it is the page's ink at the sub's size): named once, as a note */
  const PAGE = { '.lp-title': 'title', '.lp-sub:not(.lp-note)': 'sub', '.lp-src': 'source', '.lp-note': 'note' };
  if (world) {
    const S = world.__lp;
    for (const [sel, k] of Object.entries(PAGE))
      for (const el of world.querySelectorAll(sel)) {
        if (eff(el) <= 0.05 || written(el) <= 0.02) continue;
        for (const b of inkLines(el)) {
          if (b[2] < 2 || b[3] < 2) continue;   /* a page mid-wipe is scaled to nothing */
          out.items.push({ k, box: b, px: fs(el), s: sc(el), txt: txt(el) });
        }
      }
    const rail = world.querySelector('.lp-rail');
    if (rail && eff(rail) > 0.05 && rail.getBoundingClientRect().height > 0) out.items.push({ k: 'rail', box: R(rail), px: 0, s: 1, txt: '' });
    /* the charts as the DOM holds them, not as `__lp` remembers them: a page rebuilt into the world
       can leave __lp pointing at the page BEFORE it, whose chart elements are detached (measured at
       0:58 after a backward seek). The state object is used for one thing only - the plot box it
       declares - and a chart with no state falls back to where its axes and data are drawn. */
    const states = S && S.states && S.states.length ? S.states : (S ? [S] : []);
    let up = 0, chartBox = null, parked = false;
    for (const chart of world.querySelectorAll('.lp-chart')) {
      const o = eff(chart); if (o <= 0.05) continue;
      const st = states.find((x) => x && x.chart === chart) || null;
      up = Math.max(up, o);
      parked = parked || /scale\(0?\.[0-8]/.test(chart.style.transform || '');   /* lpPaintPark writes scale(<1) */
      const cb = R(chart); chartBox = chartBox ? [Math.min(chartBox[0], cb[0]), Math.min(chartBox[1], cb[1]),
        Math.max(chartBox[0] + chartBox[2], cb[0] + cb[2]) - Math.min(chartBox[0], cb[0]),
        Math.max(chartBox[1] + chartBox[3], cb[1] + cb[3]) - Math.min(chartBox[1], cb[1])] : cb;
      const P = st && st.plot; const m = chart.getScreenCTM && chart.getScreenCTM();
      if (P && m) {   /* the PLOT in stage px: the chart's own pin box through its screen CTM (viewBox, park, camera) */
        const pt = (x, y) => [m.a * x + m.c * y + m.e - stg.x, m.b * x + m.d * y + m.f - stg.y];
        const a = pt(P.L, P.T), b = pt(P.W - P.R, P.B);
        out.plots.push({ op: o, box: [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1])] });
      } else {   /* a builder that declares no plot (bars): the plot IS where the data and the axes are drawn */
        let bb = null;
        for (const el of chart.querySelectorAll(MARKS)) {
          if (eff(el) <= 0.05) continue;
          const r = R(el); if (r[2] < 0 && r[3] < 0) continue;
          bb = bb ? [Math.min(bb[0], r[0]), Math.min(bb[1], r[1]), Math.max(bb[0] + bb[2], r[0] + r[2]) - Math.min(bb[0], r[0]),
                     Math.max(bb[1] + bb[3], r[1] + r[3]) - Math.min(bb[1], r[1])] : r;
        }
        if (bb && bb[2] > 1 && bb[3] > 1) out.plots.push({ op: o, box: bb });
      }
      for (const el of chart.querySelectorAll(DATA)) {
        if (eff(el) <= 0.05) continue;
        for (const r of dataBoxes(el, stg)) if (r[2] >= 1 || r[3] >= 1) out.data.push(r);
        out.nmarks++;
        if (el.tagName === 'path' && el.getTotalLength) { const len = el.getTotalLength();
          const da = parseFloat((el.getAttribute('stroke-dasharray') || '0').split(/[ ,]/)[0]) || 0;
          const off = parseFloat(el.getAttribute('stroke-dashoffset') || '0');
          out.drawn.push(len > 0 && da > 0 ? Math.max(0, Math.min(1, (len - off) / len)) : 1); }
      }
      for (const el of chart.querySelectorAll('text')) {
        if (eff(el) <= 0.05) continue;
        const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
        const cls = (el.getAttribute('class') || 'text').split(' ')[0];
        out.items.push({ k: 'chart.' + cls, box: R(el), px: fs(el), s: sc(el), txt: txt(el) });
      }
    }
    out.chart = { up, box: chartBox, parked };
    /* the marks summary from the drawn DOM, not through __lpProbe - that probe takes the first ledger
       world and would answer for the page underneath */
    out.marks = { n: out.nmarks, drawn: out.drawn.length ? out.drawn.reduce((a, b) => a + b, 0) / out.drawn.length : null };
  }
  const cap = document.getElementById('caption');
  if (cap) { const o = eff(cap), t = txt(cap);
    const ws = [...cap.querySelectorAll('.cw')];
    if (o > 0.05 && t) {
      out.caption = { box: R(cap), text: t, mode: cap.classList.contains('stage') ? 'stage' : cap.classList.contains('onpage') ? 'onpage' : 'anchor' };
      out.items.push({ k: 'caption', box: R(cap), px: fs(ws[0] || cap), s: sc(ws[0] || cap), txt: t });
    }
  }
  return out;
}
"""


# ---- derivation: overlaps, type, clearances ----------------------------------------------------------------------

def _rect(b: list[float]) -> tuple[float, float, float, float]:
    return (b[0], b[1], b[0] + b[2], b[1] + b[3])


def intersect_px(a: list[float], b: list[float]) -> float:
    ax0, ay0, ax1, ay1 = _rect(a)
    bx0, by0, bx1, by1 = _rect(b)
    w = min(ax1, bx1) - max(ax0, bx0)
    h = min(ay1, by1) - max(ay0, by0)
    return w * h if w > 0 and h > 0 else 0.0


def gap_px(a: list[float], b: list[float]) -> float:
    """The shortest distance between two boxes; negative (the overlap's smaller side) when they meet."""
    ax0, ay0, ax1, ay1 = _rect(a)
    bx0, by0, bx1, by1 = _rect(b)
    dx = max(bx0 - ax1, ax0 - bx1, 0.0)
    dy = max(by0 - ay1, ay0 - by1, 0.0)
    if dx == 0 and dy == 0:
        return -min(min(ax1, bx1) - max(ax0, bx0), min(ay1, by1) - max(ay0, by0))
    return (dx * dx + dy * dy) ** 0.5


COVER_CELL = 8.0   # px: the grid the many little data boxes are counted on, so two segments over one pixel count once


def cover_px(box: list[float], boxes: list[list[float]], cell: float = COVER_CELL) -> float:
    """How much of `box` the union of `boxes` covers, to a `cell`-px grid."""
    x0, y0, x1, y1 = _rect(box)
    if x1 <= x0 or y1 <= y0 or not boxes:
        return 0.0
    marked: set[tuple[int, int]] = set()
    for b in boxes:
        bx0, by0, bx1, by1 = _rect(b)
        gx0, gy0 = max(x0, bx0), max(y0, by0)
        gx1, gy1 = min(x1, bx1), min(y1, by1)
        if gx1 <= gx0 or gy1 <= gy0:
            continue
        for gx in range(int(gx0 // cell), int((gx1 - 1e-9) // cell) + 1):
            for gy in range(int(gy0 // cell), int((gy1 - 1e-9) // cell) + 1):
                marked.add((gx, gy))
    return len(marked) * cell * cell


def _union(boxes: list[list[float]]) -> list[float] | None:
    if not boxes:
        return None
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    return [x0, y0, x1 - x0, y1 - y0]


def _pair(a_name: str, a_box: list[float], b_name: str, b_box: list[float]) -> dict | None:
    area = intersect_px(a_box, b_box)
    if area <= 0:
        return None
    smaller = min(a_box[2] * a_box[3], b_box[2] * b_box[3]) or 1.0
    return {"a": a_name, "b": b_name, "area_px": int(round(area)), "share_of_smaller": int(round(100 * area / smaller))}


def _dock_state(d: dict, entry: dict | None) -> str:
    """parked | reading | moving - the card's own box against the boxes the compiler named for it.
    `moving` covers the flight, the park's path and a card whose life was too short to park."""
    box = d["box"]
    for key, name in (("place", "parked"), ("read_place", "reading")):
        p = (entry or {}).get(key)
        if not p:
            continue
        # the top-left and the width only: `place.h` is the compiler's PREDICTION and the card's height
        # stays its content's, so a card at its place is rarely at its place's height
        tol = max(STATE_TOL_PX, STATE_TOL_SHARE * float(p["w"]))
        if abs(box[0] - p["x"]) <= tol and abs(box[1] - p["y"]) <= tol and abs(box[2] - p["w"]) <= tol:
            return name
    return "moving"


def moved_px(a: list[float], b: list[float] | None) -> float:
    """The furthest a box's corners travelled between two frames."""
    if not b:
        return 0.0
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[0] + a[2] - b[0] - b[2]), abs(a[1] + a[3] - b[1] - b[3]))


def derive(dom: dict, t: float, why: str, camera: dict, aspect: str, entries: dict[str, dict],
           nxt: dict[str, list[float]] | None = None) -> dict:
    """The DOM at t, reduced to what a layout gate can refuse: boxes, named overlap pairs, type at the
    phone scale, clearances. Rounded to ints - a sub-pixel layout number is noise, and the JSON for one
    instant must stay under 2 KB."""
    sw, sh = stage_size(aspect)
    docks = []
    for d in dom["docks"]:
        if not d["paper"]:
            continue
        rest = moved_px(d["box"], (nxt or {}).get(d["name"]))
        docks.append({"id": d["name"], "state": _dock_state(d, entries.get(d["name"])),
                      "box": [int(round(v)) for v in d["box"]], "rest": int(rest < REST_PX)})
    plot = _union([p["box"] for p in dom.get("plots") or []])
    data = _union(dom.get("data") or [])
    page: dict = {}
    for k in ("title", "sub", "source", "rail", "note"):
        b = _union([i["box"] for i in dom["items"] if i["k"] == k])
        if b:
            page[k] = [int(round(v)) for v in b]
    if plot:
        page["plot"] = [int(round(v)) for v in plot]
    if data:
        page["data"] = [int(round(v)) for v in data]
    if (dom.get("chart") or {}).get("box"):
        page["chart"] = [int(round(v)) for v in dom["chart"]["box"]]

    # TYPE, grouped by kind: the smallest drawn size in the group is what the floor is read against
    groups: dict[str, list[dict]] = {}
    for i in dom["items"]:
        groups.setdefault(i["k"], []).append(i)
    texts = []
    for k, items in sorted(groups.items()):
        if k == "rail":
            continue
        px = min(i["px"] for i in items)
        row = {"k": k, "n": len(items), "px": int(round(px)), "css": round(phone_css(px, aspect), 1)}
        if max(float(i.get("s") or 1.0) for i in items) < DEMOTED_SCALE:
            row["pk"] = 1   # every run in this group rides a park: demoted on purpose, not type to be read
        texts.append(row)

    # OVERLAPS, as named pairs. Every paper/pill against every other and against the page's ink.
    overlaps = []
    solids = [(d["name"], d["box"]) for d in dom["docks"]]
    ink = [(("page." + i["k"]) if i["k"] in ("title", "sub", "source", "note") else i["k"], i["box"])
           for i in dom["items"] if i["k"] != "caption"]
    if plot:
        ink.append(("page.plot", plot))
    for n, (an, ab) in enumerate(solids):
        for bn, bb in solids[n + 1:]:
            p = _pair(an, ab, bn, bb)
            if p:
                overlaps.append(p)
        for bn, bb in ink:
            if bn == an:
                continue
            p = _pair(an, ab, bn, bb)
            if p:
                overlaps.append(p)
        # the DATA is many small boxes (every bar, every segment of every drawn series): one pair, the
        # area they COVER of this card (a grid, so overlapping segments are not counted twice)
        hit = cover_px(ab, dom.get("data") or [])
        if hit > 0:
            overlaps.append({"a": an, "b": "page.data", "area_px": int(round(hit)),
                             "share_of_smaller": int(round(100 * hit / max(1.0, ab[2] * ab[3])))})
    cap = dom.get("caption")
    if cap:
        for an, ab in solids:
            p = _pair(an, ab, "caption", cap["box"])
            if p:
                overlaps.append(p)
    overlaps.sort(key=lambda p: -p["area_px"])

    # CLEARANCES: to the caption strip, and the depth every band of the safe zone is intruded on
    bands = {"top": [0, 0, sw, SAFE_TOP * sh], "bottom": [0, (1 - SAFE_BOTTOM) * sh, sw, SAFE_BOTTOM * sh],
             "left": [0, 0, SAFE_SIDE * sw, sh], "right": [(1 - SAFE_SIDE) * sw, 0, SAFE_SIDE * sw, sh]}
    safe = {}
    for name, band in bands.items():
        depth = max((intersect_px(d["box"], band) / max(1.0, d["box"][2] * d["box"][3]) for d in dom["docks"]), default=0.0)
        safe[name] = int(round(100 * depth))
    clear = {"safe_pct": safe}
    if cap and solids:
        clear["caption_px"] = int(round(min(gap_px(ab, cap["box"]) for _an, ab in solids)))

    out = {"t": round(t, 2), "why": why, "docks": docks, "page": page, "texts": texts,
           "overlaps": overlaps, "clearances": clear,
           "camera": {"scene": camera.get("scene"), "zoom": round(float(camera.get("zoom") or 1), 3),
                      "look": [int(round(v)) for v in (camera.get("look") or [0, 0])]}}
    if cap:
        out["caption"] = {"box": [int(round(v)) for v in cap["box"]], "mode": cap["mode"], "text": cap["text"][:40]}
    ch = dom.get("chart") or {}
    m = dom.get("marks") or {}
    out["marks"] = {"n": int(m.get("n") or 0), "drawn": (round(m["drawn"], 2) if m.get("drawn") is not None else None),
                    "up": round(float(ch.get("up") or 0), 2), "parked": bool(ch.get("parked"))}
    return out


# ---- the probe session -------------------------------------------------------------------------------------------

class Probe:
    """A headless player of one build dir, seekable, read at any t. Mirrors test_camera._Player and
    render_baseline.render_frame - the same page preparation, so the numbers are the rendered frame's."""

    def __init__(self, build: Path, timeline_name: str | None = None, html_name: str = "player.html"):
        from playwright.sync_api import sync_playwright
        self.build = Path(build)
        self.tl_path = G._timeline_path(self.build, timeline_name)
        self.tl = json.loads(self.tl_path.read_text(encoding="utf-8"))
        self.aspect = str(self.tl.get("aspect") or "16:9")
        self.w, self.h = stage_size(self.aspect)
        self.html = self.build / html_name
        if not self.html.exists():
            raise SystemExit(f"no {html_name} in {self.build} - build the episode first")
        self.entries = {d.get("slide"): d for s in self.tl.get("scenes", []) for d in (s.get("docks") or [])}
        self.srv, port = RB.serve(self.build)
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(headless=True)
        self.page = self.br.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        self.errs: list[str] = []
        self.page.on("pageerror", lambda e: self.errs.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{self.html.name}", wait_until="networkidle", timeout=300000)
        RB.prepare_page(self.page, self.w, self.h)

    def seek(self, t: float) -> None:
        # WARM: the first seek settles the page (the tests' rule - a cold seek reads a card before its
        # body has decoded), so every instant is sought twice and the second read is the frame.
        for _ in range(2):
            self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        self.page.evaluate("() => window.__clipsSeeked ? window.__clipsSeeked() : null")

    def at(self, t: float, why: str = "") -> dict:
        self.seek(t)
        dom = self.page.evaluate(READ_DOM)
        cam = self.page.evaluate("t => window.__camera ? window.__camera(t, null) : {}", t)
        self.seek(t + REST_DT)                      # is each card still moving, or is this its composition?
        nxt = self.page.evaluate(READ_DOCKS)
        self.seek(t)                                # leave the page at t: --sheet grabs the frame next
        return derive(dom, t, why, cam or {}, self.aspect, self.entries, nxt)

    def png(self, t: float) -> bytes:
        return RB.frame_png(self.page, t, (self.w, self.h))

    def close(self) -> None:
        self.br.close(); self.pw.stop(); self.srv.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


# ---- the gate's instants -----------------------------------------------------------------------------------------

def gate_instants(tl: dict) -> list[tuple[float, str]]:
    """Every instant M25 must look at: the landings the gate already knows (`_landings`), every species
    onset, every transition end, every dock's enter, its reading size and its contact, and each page's
    last data mark (`_deployed_lives`). Deduped to 0.02 s, clamped inside the runtime."""
    runtime = float(tl.get("runtime_s") or max(s["span"][1] for s in tl.get("scenes", [{"span": [0, 0]}])))
    out: dict[int, tuple[float, str]] = {}

    def add(t: float, why: str) -> None:
        t = max(0.0, min(float(t), runtime - 0.01))
        out.setdefault(int(round(t * 50)), (round(t, 3), why))

    scenes = tl.get("scenes", [])
    for s in scenes:
        sid = str(s.get("scene_id", "?"))
        for t, name in G._landings(s):
            add(t, f"{sid} {name}")
        for sp in s.get("species", []):
            k = str(sp.get("kind", "?"))
            add(float(sp.get("at", 0.0)), f"{sid} {k} onset")
            if k == "chart_to":
                add(G._transition_land(s, sp), f"{sid} chart_to {sp.get('to')} end")
        for d in s.get("docks", []):
            nm = d.get("slide", "?")
            enter = float(d.get("enter", 0.0))
            add(enter, f"{sid} dock {nm} enter")
            read_s, park_s = float(d.get("read_s") or 1.2), float(d.get("park_s") or 0.7)
            add(enter + read_s, f"{sid} dock {nm} reading size")
            if d.get("place") and float(d.get("exit", 0.0)) - enter >= read_s + park_s:
                add(enter + read_s + park_s + 0.05, f"{sid} dock {nm} parked")   # the composition the compiler chose
    for sid, last, _end, _dur in G._deployed_lives(scenes):
        add(last, f"{sid} last data mark")
    return [v for _k, v in sorted(out.items())]


def probe_doc(build: Path, timeline_name: str | None = None, probe: "Probe | None" = None,
              instants: list[tuple[float, str]] | None = None) -> dict:
    """The gate's document: every instant that matters, keyed to the player it was read from."""
    own = probe is None
    p = probe or Probe(build, timeline_name)
    try:
        return {"player_sha256": hashlib.sha256(p.html.read_bytes()).hexdigest(),
                "timeline": p.tl_path.name, "aspect": p.aspect,
                "instants": [p.at(t, why) for t, why in (instants if instants is not None else gate_instants(p.tl))]}
    finally:
        if own:
            p.close()


def write_gate(build: Path, timeline_name: str | None = None, probe: "Probe | None" = None) -> Path:
    """Probe every gate instant and write <build>/layout-probe.json for M25."""
    out = Path(build) / PROBE_NAME
    out.write_text(json.dumps(probe_doc(build, timeline_name, probe), separators=(",", ":")), encoding="utf-8")
    return out


def contact_sheet(pngs: list[tuple[float, bytes]], out: Path, tile: int = 360, per_sheet: int = 12) -> list[Path]:
    """The frames at the given instants, `tile` px wide, 12 to a sheet, each labelled with its t."""
    import io
    from PIL import Image, ImageDraw
    paths: list[Path] = []
    for k in range(0, len(pngs), per_sheet):
        chunk = pngs[k:k + per_sheet]
        ims = [(t, Image.open(io.BytesIO(b)).convert("RGB")) for t, b in chunk]
        th = max(round(tile * im.height / im.width) for _t, im in ims)
        cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
        pad = 22
        sheet = Image.new("RGB", (cols * tile, rows * (th + pad)), (13, 15, 18))
        d = ImageDraw.Draw(sheet)
        for i, (t, im) in enumerate(ims):
            x, y = (i % cols) * tile, (i // cols) * (th + pad)
            sheet.paste(im.resize((tile, th)), (x, y + pad))
            d.text((x + 8, y + 6), f"{t:.2f}s", fill=(220, 227, 234))
        p = out if len(pngs) <= per_sheet else out.with_name(f"{out.stem}.{k // per_sheet + 1}{out.suffix}")
        sheet.save(p, "PNG")
        paths.append(p)
    return paths


def human(inst: dict) -> str:
    d = ", ".join(f"{x['id']} {x['state']}{'' if x['rest'] else ' (moving)'} {x['box']}" for x in inst["docks"]) or "no docks"
    pg = ", ".join(f"{k} {v}" for k, v in inst["page"].items()) or "no page"
    ov = "; ".join(f"{o['a']} over {o['b']} {o['area_px']} px ({o['share_of_smaller']} % of the smaller)" for o in inst["overlaps"][:4])
    ty = ", ".join(f"{x['k']} {x['px']}px/{x['css']}css" for x in inst["texts"])
    return (f"t={inst['t']:.2f}  {inst['why']}\n  docks: {d}\n  page: {pg}\n  type: {ty}\n"
            f"  caption: {inst.get('caption', {}).get('box', '-')} {inst.get('caption', {}).get('text', '')}\n"
            f"  overlaps: {ov or 'none'}\n  clearances: {inst['clearances']}  camera: {inst['camera']}  marks: {inst['marks']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="the layout of a built player at t, from its own DOM")
    ap.add_argument("build", type=Path, help="build dir holding player.html and the compiled timeline")
    ap.add_argument("t", nargs="*", type=float, help="instants in seconds")
    ap.add_argument("--json", action="store_true", help="the probe's JSON (under 2 KB for one instant)")
    ap.add_argument("--sheet", help="write a contact sheet of the frames at these instants")
    ap.add_argument("--tile", type=int, default=360, help="contact-sheet tile width in px")
    ap.add_argument("--gate", action="store_true", help="probe the gate's instants and write <build>/layout-probe.json")
    ap.add_argument("--timeline", help="timeline file name inside the build dir")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not args.t and not args.gate:
        ap.error("give one or more instants, or --gate")
    with Probe(args.build, args.timeline) as p:
        if args.gate:
            out = write_gate(args.build, args.timeline, probe=p)
            n = len(json.loads(out.read_text(encoding="utf-8"))["instants"])
            print(f"{out} - {n} instants")
        if args.t:
            insts = [p.at(t, "asked") for t in args.t]
            if args.sheet:
                sheets = contact_sheet([(t, p.png(t)) for t in args.t], Path(args.sheet), args.tile)
                print("\n".join(str(s) for s in sheets))
            if args.json:
                doc = {"player_sha256": hashlib.sha256(p.html.read_bytes()).hexdigest()[:16], "aspect": p.aspect, "instants": insts}
                print(json.dumps(doc, separators=(",", ":")))
            else:
                print("\n".join(human(i) for i in insts))
        if p.errs:
            print("page errors: " + "; ".join(p.errs[:4]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
