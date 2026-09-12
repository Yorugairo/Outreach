"""Measure the on-screen motion energy of a built player, per piece / per scene / whole screen (P45 T8).

The 0.22 secondary-motion ratio - `E_secondary <= 0.22 * E_primary`, `E = integral |v|^2 dt` -
comes from `docs/content-video-engine/briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md` A6 and is
reclassified in `47-FINDINGS-TO-CHECKS.md:146` as an INVENTED number whose *shape* is standard
craft. It is a starting reference to measure against, never a threshold to fit to (BACKLOG X2/X11:
"never adopt a guessed threshold - that is precisely the error the metrics exist to catch").

What is measured is what the renderer actually moves: headless Chromium loads the built
`player.html`, seeks `#scrub` to each sampled t, and one `page.evaluate` walks the live DOM under
`#stage`. The template carries no `data-motion` attributes (verified 2026-09-05:
`rg -c data-motion docs/content-video-engine/samples/scene-evidence-player.template.html` returns
no matches), so motion is DISCOVERED by change detection: an element's bounding-box centre and its
effective opacity, frame over frame.

    python content/video_engine/scripts/measure_motion_energy.py <build-dir> --fps 15
    python .../measure_motion_energy.py <build-dir> --from 17 --to 33 --report /tmp/scene4.md

Definitions (all deterministic given fps and the build):
  dt          = 1 / fps
  v(px/s)     = (centre_now - centre_prev) * fps          [stage-local pixels]
  E_trans     = sum |v|^2 dt = sum |dcentre|^2 * fps      [px^2/s]
  E_opacity   = sum (dopacity * fps)^2 dt = sum dopacity^2 * fps   [1/s], a SEPARATE column
                (a fade is motion to the eye but not translation, so it is never summed into E_trans)

Translation energy is counted only when the element is visible in BOTH frames and its content
signature is unchanged - a caption page swapping its words is a cut, not a 700 px/s pan.

THE RACE READ (`--race --window t0 t1`, P52 T17 / R26-3). A second, narrower measurement on the
same headless seek: the racing marks' own trajectories, split onto the two axes a "choppy" race
could be failing on - the CURVATURE of the path (the geometry, which is the clothoid fitter's case)
and the SPEED's second difference over the clock (the timing, which no curve fit touches). See the
block below it is defined in; it prints both and adopts nothing.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"

SECONDARY_REFERENCE_RATIO = 0.22   # A6, invented; the reference we measure AGAINST
DEFAULT_FPS = 15
DEFAULT_MAX_DEPTH = 4              # depth 4 reaches chart series, bars, pills and ink words;
                                   # depth 5 is the per-glyph `span.g` handwriting reveal (~70/frame)
MOVE_EPS_PX = 0.5                  # below this a centre shift is layout noise, not a moving piece
MOVE_EPS_OPACITY = 0.01
TOP_PIECES = 25
STAGE_SIZE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}
# SVG plumbing: present in the DOM, never drawn. Skipped before the walk so they cannot appear
# as UNCLASSIFIED noise with a 0x0 box.
SKIP_TAGS = ("defs", "filter", "clippath", "mask", "pattern", "lineargradient", "radialgradient",
             "stop", "title", "desc", "feturbulence", "fecolormatrix", "fedisplacementmap",
             "fegaussianblur", "fecomposite", "feoffset", "feblend", "femerge", "femergenode")

PRIMARY, SECONDARY, UNCLASSIFIED = "PRIMARY", "SECONDARY", "UNCLASSIFIED"

# The classification table is DECLARED here, not guessed at runtime. `kind` is "id" for elements the
# template gives no class, "class" for the rest; an element is classified by its own class tokens,
# then its own id, then by the nearest classified ancestor in its key path. Anything that resolves
# to nothing is reported as UNCLASSIFIED and never silently dropped.
CLASSIFICATION = (
    # --- PRIMARY: the world/plate layer, the ledger page, the chart draw, the beat's carrier
    ("world",        "class", PRIMARY,   "the world/plate layer - #wA/#wB, the beat's ground"),
    ("clipv",        "class", PRIMARY,   "the generative clip filling a world layer"),
    ("seam",         "id",    PRIMARY,   "the cross-reveal wipe front (29 s9.15) - the transition IS the beat"),
    ("lp",           "class", PRIMARY,   "the ledger page mount"),
    ("lp-page",      "class", PRIMARY,   "the ledger page build/retract/spiral (E22)"),
    ("lp-field",     "class", PRIMARY,   "the page field the ink lands in"),
    ("lp-edge",      "class", PRIMARY,   "the deckle edge - it arrives with the page (E22)"),
    ("lp-ink",       "class", PRIMARY,   "page ink write-on (title/sub/src) - part of the page build"),
    ("w",            "class", PRIMARY,   "an ink word inside .lp-ink (its `.g` glyphs are depth 5)"),
    ("lp-chart",     "class", PRIMARY,   "the chart - proof of one sentence (E25)"),
    ("ser",          "class", PRIMARY,   "a chart series path, drawn on"),
    ("bar",          "class", PRIMARY,   "a chart bar, grown"),
    ("ax",           "class", PRIMARY,   "chart axis"),
    ("grid",         "class", PRIMARY,   "chart gridline"),
    ("lab",          "class", PRIMARY,   "chart axis label - it reads at a glance with the chart (E28)"),
    ("val",          "class", PRIMARY,   "a bar's value, drawn with the bar"),
    ("sname",        "class", PRIMARY,   "a series name, drawn with the series"),
    ("dock",         "class", PRIMARY,   "the evidence dock - the carrier of the scene's evidence (29 Part 8)"),
    ("slide-frame",  "class", PRIMARY,   "the dock's frame"),
    ("i1",           "id",    PRIMARY,   "dock 1 evidence image"),
    ("i2",           "id",    PRIMARY,   "dock 2 evidence image"),
    # --- SECONDARY: captions, badges, species, accents, plate boil
    ("caption",      "id",    SECONDARY, "the caption block - captions ARE the motion, but they ride the beat"),
    ("cg",           "class", SECONDARY, "a caption phrase group"),
    ("cw",           "class", SECONDARY, "a caption word - pop / lift / boil"),
    ("pill",         "class", SECONDARY, "a badge pill"),
    ("pill-label",   "class", SECONDARY, "badge label"),
    ("pill-row",     "class", SECONDARY, "badge row"),
    ("pill-num",     "class", SECONDARY, "badge number"),
    ("pill-tag",     "class", SECONDARY, "badge tag"),
    ("cpill",        "class", SECONDARY, "a chart callout badge"),
    ("callout",      "class", SECONDARY, "a chart callout label"),
    ("species",      "id",    SECONDARY, "species life (41-LEDGER-PAGE-SPECIES)"),
    ("plife",        "id",    SECONDARY, "plate life - boil / jitter"),
    ("lp-grain",     "class", SECONDARY, "paper grain boil on the page"),
    ("lp-rail",      "class", SECONDARY, "the page rail accent"),
    ("rail",         "class", SECONDARY, "a dock rail accent"),
    ("wash",         "id",    SECONDARY, "the atmospheric wash - a full-stage opacity layer"),
    ("spot",         "id",    SECONDARY, "the spotlight (M11) - a full-stage opacity layer"),
)
_BY_CLASS = {n: (lab, why) for n, k, lab, why in CLASSIFICATION if k == "class"}
_BY_ID = {n: (lab, why) for n, k, lab, why in CLASSIFICATION if k == "id"}

WALK_JS = r"""
(args) => {
  const stage = document.getElementById('stage');
  const sr = stage.getBoundingClientRect();
  const cn = (c) => (c.className && c.className.baseVal !== undefined) ? c.className.baseVal : (c.className || '');
  const out = [];
  const walk = (el, depth, parentKey, parentOp) => {
    let i = -1;
    for (const c of el.children) {
      i += 1;
      const tag = c.tagName.toLowerCase();
      if (args.skipTags.indexOf(tag) >= 0) continue;
      const cls = String(cn(c) || '').trim();
      const first = cls ? cls.split(/\s+/)[0] : '';
      const seg = c.id ? ('#' + c.id) : (tag + (first ? '.' + first : '') + ':' + i);
      const key = parentKey + '/' + seg;
      const cs = getComputedStyle(c);
      const own = parseFloat(cs.opacity);
      const eff = parentOp * (isNaN(own) ? 1 : own);
      const hidden = cs.display === 'none' || cs.visibility === 'hidden';
      const r = c.getBoundingClientRect();
      let sig = tag + '|' + cls + '|';
      if (tag === 'img' || tag === 'video') sig += String(c.currentSrc || c.getAttribute('src') || '').slice(-48);
      else if (c.children.length === 0) sig += (c.textContent || '').slice(0, 32);
      out.push({key: key, cls: cls, tag: tag, depth: depth,
                vis: !hidden && eff > 0.005 && r.width > 0 && r.height > 0,
                op: Math.round(eff * 1e4) / 1e4, sig: sig,
                cx: Math.round((r.x + r.width / 2 - sr.x) * 1e3) / 1e3,
                cy: Math.round((r.y + r.height / 2 - sr.y) * 1e3) / 1e3});
      if (depth < args.maxDepth && !hidden) walk(c, depth + 1, key, eff);
    }
  };
  walk(stage, 0, '', 1);
  return out;
}
"""


# --------------------------------------------------------------------------- classification
def classify(cls: str, key: str) -> tuple[str, str]:
    """(label, why) for one element: own classes, then own id, then the nearest classified ancestor."""
    for token in cls.split():
        if token in _BY_CLASS:
            return _BY_CLASS[token]
    segments = [s for s in key.split("/") if s]
    own = segments[-1] if segments else ""
    if own.startswith("#") and own[1:] in _BY_ID:
        return _BY_ID[own[1:]]
    for seg in reversed(segments[:-1]):
        hit = _segment_rule(seg)
        if hit:
            return hit[0], f"inherited from {seg} - {hit[1]}"
    return UNCLASSIFIED, "no rule in CLASSIFICATION matched this element or any ancestor"


def _segment_rule(seg: str) -> tuple[str, str] | None:
    """The CLASSIFICATION row a key segment (`#id` or `tag.class:n`) matches, if any."""
    if seg.startswith("#"):
        return _BY_ID.get(seg[1:])
    head = seg.split(":")[0]
    return _BY_CLASS.get(head.split(".", 1)[1]) if "." in head else None


# --------------------------------------------------------------------------- pure energy maths
def integrate_energy(values, fps: float) -> float:
    """E = sum |v|^2 dt over a sampled trajectory, with v = delta * fps and dt = 1/fps.

    Accepts scalars (an opacity track) or (x, y) pairs (a centre track). Exact for constant
    velocity at any fps; converges to the true integral as fps rises for a smooth trajectory.
    """
    if len(values) < 2:
        return 0.0
    total = 0.0
    for prev, cur in zip(values, values[1:]):
        if isinstance(cur, (tuple, list)):
            d2 = (cur[0] - prev[0]) ** 2 + (cur[1] - prev[1]) ** 2
        else:
            d2 = (cur - prev) ** 2
        total += d2 * fps          # (delta*fps)^2 * (1/fps)
    return total


def scene_windows(timeline: dict) -> list[tuple[str, float, float]]:
    """(scene_id, t_start, t_end) per timeline row, half-open [t_start, t_end)."""
    rows = []
    for i, sc in enumerate(timeline.get("scenes") or []):
        span = sc.get("span") or [0.0, 0.0]
        rows.append((str(sc.get("scene_id") or f"s{i + 1:02d}"), float(span[0]), float(span[1])))
    return rows


def scene_for(t: float, windows: list[tuple[str, float, float]]) -> str:
    """The scene whose half-open span contains t; the last scene owns anything past its end."""
    for scene_id, t0, t1 in windows:
        if t0 <= t < t1:
            return scene_id
    if windows and t >= windows[-1][2]:
        return windows[-1][0]
    return "(outside)"


def ratio_row(e_primary: float, e_secondary: float) -> dict:
    ratio = (e_secondary / e_primary) if e_primary > 0 else None
    return {
        "e_primary": e_primary,
        "e_secondary": e_secondary,
        "ratio": ratio,
        "reference": SECONDARY_REFERENCE_RATIO,
        "difference": None if ratio is None else ratio - SECONDARY_REFERENCE_RATIO,
        "over_reference": None if ratio is None else ratio > SECONDARY_REFERENCE_RATIO,
    }


# --------------------------------------------------------------------------- frame accumulation
def accumulate(frames, fps: float, windows: list[tuple[str, float, float]]) -> dict:
    """Fold sampled frames into per-element and per-scene energy.

    `frames` is [(t, [element dicts])] in time order, as `sample_build` returns it.
    """
    pieces: dict[str, dict] = {}
    scenes: dict[str, dict] = {sid: _empty_scene(sid, t0, t1) for sid, t0, t1 in windows}
    prev_by_key: dict[str, dict] = {}
    for t, elements in frames:
        bucket = scenes.setdefault(scene_for(t, windows), _empty_scene(scene_for(t, windows), t, t))
        movers = 0
        for el in elements:
            piece = pieces.setdefault(el["key"], _empty_piece(el))
            piece["labels"].add(classify(el["cls"], el["key"])[0])
            piece["classes"].add(el["cls"] or el["tag"])
            piece["frames_present"] += 1
            movers += _fold_pair(prev_by_key.get(el["key"]), el, fps, piece, bucket)
        bucket["frames"] += 1
        bucket["movers_total"] += movers
        bucket["movers_max"] = max(bucket["movers_max"], movers)
        prev_by_key = {el["key"]: el for el in elements}
    return {"pieces": pieces, "scenes": scenes}


def _fold_pair(prev: dict | None, cur: dict, fps: float, piece: dict, bucket: dict) -> int:
    """Add one frame-pair's energy for one element. Returns 1 if the element moved this frame."""
    if prev is None or prev["sig"] != cur["sig"]:
        return 0                                    # a new element or a content swap is a cut
    label = classify(cur["cls"], cur["key"])[0]
    moved = 0
    d_op = cur["op"] - prev["op"]
    if d_op:
        e_op = d_op * d_op * fps
        piece["e_opacity"] += e_op
        bucket["e_opacity"][label] += e_op
        if abs(d_op) > MOVE_EPS_OPACITY:
            moved = 1
    if prev["vis"] and cur["vis"]:
        d2 = (cur["cx"] - prev["cx"]) ** 2 + (cur["cy"] - prev["cy"]) ** 2
        if d2:
            e_tr = d2 * fps
            piece["e_trans"] += e_tr
            bucket["e_trans"][label] += e_tr
            # The largest single-frame step is the tell for a re-layout masquerading as motion:
            # a rebuilt subtree jumps once, a real move spreads over consecutive frames.
            step = math.sqrt(d2)
            piece["max_step_px"] = max(piece["max_step_px"], step)
            bucket["max_step_px"] = max(bucket["max_step_px"], step)
            if d2 > MOVE_EPS_PX ** 2:
                piece["frames_moving"] += 1
                moved = 1
    return moved


def _empty_piece(el: dict) -> dict:
    return {"key": el["key"], "tag": el["tag"], "depth": el["depth"], "classes": set(), "labels": set(),
            "e_trans": 0.0, "e_opacity": 0.0, "frames_present": 0, "frames_moving": 0,
            "max_step_px": 0.0}


def _empty_scene(sid: str, t0: float, t1: float) -> dict:
    return {"scene_id": sid, "t0": t0, "t1": t1, "frames": 0, "movers_total": 0, "movers_max": 0,
            "max_step_px": 0.0, "e_trans": defaultdict(float), "e_opacity": defaultdict(float)}


# --------------------------------------------------------------------------- headless sampling
def sample_build(build_dir: Path, fps: float, t_from: float, t_to: float,
                 max_depth: int = DEFAULT_MAX_DEPTH, progress=None):
    """Seek the built player to each sampled t and walk the live DOM under #stage."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from render_baseline import prepare_page, serve                     # noqa: PLC0415 - optional dep
    from playwright.sync_api import sync_playwright                     # noqa: PLC0415

    player = build_dir / "player.html"
    if not player.exists():
        raise SystemExit(f"no player.html in {build_dir}")
    aspect = str(load_timeline(build_dir).get("aspect") or "16:9")
    width, height = STAGE_SIZE[aspect]
    times = frame_times(t_from, t_to, fps)
    frames = []
    srv, port = serve(build_dir)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": width, "height": height},
                                       device_scale_factor=1).new_page()
            page.goto(f"http://127.0.0.1:{port}/player.html", wait_until="networkidle", timeout=180000)
            prepare_page(page, width, height)
            walk_args = {"maxDepth": max_depth, "skipTags": list(SKIP_TAGS)}
            for i, t in enumerate(times):
                page.evaluate("t => { const s = document.getElementById('scrub');"
                              " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                page.evaluate("() => window.__clipsSeeked ? window.__clipsSeeked() : null")
                frames.append((t, page.evaluate(WALK_JS, walk_args)))
                if progress and i % 100 == 0:
                    progress(i, len(times))
            browser.close()
    finally:
        srv.shutdown()
    return frames


def frame_times(t_from: float, t_to: float, fps: float) -> list[float]:
    n = int(math.floor((t_to - t_from) * fps + 1e-9))
    return [round(t_from + i / fps, 6) for i in range(n + 1)]


def load_timeline(build_dir: Path) -> dict:
    for p in sorted(build_dir.glob("*.timeline.json")) + [build_dir / "timeline.json"]:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise SystemExit(f"no *.timeline.json in {build_dir}")


# --------------------------------------------------------------------------- report
def build_report(build_dir: Path, timeline: dict, folded: dict, fps: float,
                 t_from: float, t_to: float, elapsed_s: float, max_depth: int) -> dict:
    pieces = [_piece_row(p) for p in folded["pieces"].values()]
    pieces.sort(key=lambda r: r["e_trans"], reverse=True)
    scenes = sorted((_scene_row(s) for s in folded["scenes"].values()), key=lambda r: r["t0"])
    buckets = folded["scenes"].values()
    whole = ratio_row(sum(s["e_trans"][PRIMARY] for s in buckets),
                      sum(s["e_trans"][SECONDARY] for s in buckets))
    whole["e_unclassified"] = sum(s["e_trans"][UNCLASSIFIED] for s in buckets)
    whole["opacity"] = ratio_row(sum(s["e_opacity"][PRIMARY] for s in buckets),
                                 sum(s["e_opacity"][SECONDARY] for s in buckets))
    return {
        "build_dir": _rel(build_dir),
        "episode_id": timeline.get("episode_id"), "aspect": timeline.get("aspect"),
        "fps": fps, "from_s": t_from, "to_s": t_to, "max_depth": max_depth,
        "frames": sum(s["frames"] for s in buckets),
        "reference_ratio": SECONDARY_REFERENCE_RATIO,
        "reference_source": ("ANSWERS-RESEARCH-BRIEF-animation-craft.md A6 - invented, "
                             "reclassified in 47-FINDINGS-TO-CHECKS.md:146"),
        "elapsed_s": round(elapsed_s, 1),
        "whole_screen": whole, "scenes": scenes, "pieces": pieces,
        "unclassified": [r["key"] for r in pieces if UNCLASSIFIED in r["labels"]],
        "classification_table": [{"name": n, "kind": k, "label": lab, "why": why}
                                 for n, k, lab, why in CLASSIFICATION],
    }


def _rel(p: Path) -> str:
    try:
        return p.relative_to(REPO).as_posix()
    except ValueError:
        return str(p)


def _piece_row(p: dict) -> dict:
    return {"key": p["key"], "tag": p["tag"], "depth": p["depth"],
            "classes": sorted(p["classes"]), "labels": sorted(p["labels"]),
            "e_trans": p["e_trans"], "e_opacity": p["e_opacity"], "max_step_px": p["max_step_px"],
            "frames_present": p["frames_present"], "frames_moving": p["frames_moving"]}


def _scene_row(s: dict) -> dict:
    row = ratio_row(s["e_trans"][PRIMARY], s["e_trans"][SECONDARY])
    row.update({"scene_id": s["scene_id"], "t0": s["t0"], "t1": s["t1"], "frames": s["frames"],
                "e_unclassified": s["e_trans"][UNCLASSIFIED],
                "e_opacity_primary": s["e_opacity"][PRIMARY],
                "e_opacity_secondary": s["e_opacity"][SECONDARY],
                "mean_movers": (s["movers_total"] / s["frames"]) if s["frames"] else 0.0,
                "max_movers": s["movers_max"], "max_step_px": s["max_step_px"]})
    return row


def _fmt(v, nd: int = 3) -> str:
    return "-" if v is None else f"{v:,.{nd}f}"


def markdown(report: dict, top: int = TOP_PIECES) -> str:
    """The operator-readable report: three tables, a read, the declared table, the leftovers."""
    return "\n".join(_head(report) + _whole_table(report) + _scene_table(report)
                     + _piece_table(report, top)
                     + ["", "## 4. The read", "", _read_paragraph(report), ""]
                     + _classification_table(report) + _unclassified_block(report)
                     + _blind_spots(report))


def _head(report: dict) -> list[str]:
    return [f"# Motion energy - {report['episode_id'] or report['build_dir']}", "",
            f"`E = integral |v|^2 dt`, sampled from the built `player.html` at **{report['fps']:g} fps** "
            f"({report['from_s']:g}-{report['to_s']:g} s, {report['frames']} frames, DOM depth <= "
            f"{report['max_depth']}), measured in {report['elapsed_s']} s.", "",
            f"Reference: **{report['reference_ratio']}** - {report['reference_source']}. It is a "
            "starting reference, not a threshold; a scene over it is a question, not a failure.", "",
            "The template carries no `data-motion` attributes, so motion is discovered by change "
            "detection on each element's bounding-box centre and effective opacity. Opacity energy "
            "is reported separately: a fade is motion to the eye but not translation.", ""]


def _whole_table(report: dict) -> list[str]:
    w = report["whole_screen"]
    o = w["opacity"]
    return ["## 1. Whole screen", "",
            "| | E_primary | E_secondary | ratio | reference | difference |",
            "|---|---:|---:|---:|---:|---:|",
            f"| translation (px^2/s) | {_fmt(w['e_primary'], 1)} | {_fmt(w['e_secondary'], 1)} | "
            f"**{_fmt(w['ratio'])}** | {report['reference_ratio']} | {_fmt(w['difference'])} |",
            f"| opacity (1/s) | {_fmt(o['e_primary'], 1)} | {_fmt(o['e_secondary'], 1)} | "
            f"**{_fmt(o['ratio'])}** | {report['reference_ratio']} | {_fmt(o['difference'])} |", ""]


def _scene_table(report: dict) -> list[str]:
    rows = ["## 2. Per scene", "",
            "| scene | span (s) | E_primary | E_secondary | ratio | vs 0.22 | movers mean/max | max step (px) |",
            "|---|---|---:|---:|---:|---|---:|---:|"]
    for s in report["scenes"]:
        verdict = "-" if s["ratio"] is None else ("OVER" if s["over_reference"] else "under")
        rows.append(f"| {s['scene_id']} | {s['t0']:.2f}-{s['t1']:.2f} | {_fmt(s['e_primary'], 1)} | "
                    f"{_fmt(s['e_secondary'], 1)} | **{_fmt(s['ratio'])}** | {verdict} | "
                    f"{s['mean_movers']:.1f} / {s['max_movers']} | {s['max_step_px']:.0f} |")
    return rows + ["", "`max step` is the largest single-frame centre displacement in the scene - the tell "
                   "for a re-layout counted as motion. A rebuilt subtree jumps once; a real move spreads "
                   "over consecutive frames.", ""]


def _piece_table(report: dict, top: int) -> list[str]:
    rows = [f"## 3. Per piece (top {top} by translation energy)", "",
            "| element | class | label | E_trans | E_opacity | frames moving |",
            "|---|---|---|---:|---:|---:|"]
    for p in report["pieces"][:top]:
        rows.append(f"| `{p['key']}` | {' / '.join(p['classes']) or p['tag']} | {' '.join(p['labels'])} | "
                    f"{_fmt(p['e_trans'], 1)} | {_fmt(p['e_opacity'], 2)} | {p['frames_moving']} |")
    return rows


def _classification_table(report: dict) -> list[str]:
    rows = ["## 5. Classification table (declared, not guessed)", "",
            "| name | kind | label | why |", "|---|---|---|---|"]
    return rows + [f"| `{r['name']}` | {r['kind']} | {r['label']} | {r['why']} |"
                   for r in report["classification_table"]] + [""]


def _unclassified_block(report: dict) -> list[str]:
    unc = report["unclassified"]
    body = ("None - every element under `#stage` resolved to PRIMARY or SECONDARY."
            if not unc else "\n".join(f"- `{k}`" for k in unc))
    return ["## 6. Unclassified", "", body, ""]


def _blind_spots(report: dict) -> list[str]:
    """What a DOM measurement structurally cannot see. Named so a zero is never read as stillness."""
    silent = [s["scene_id"] for s in report["scenes"] if s["e_primary"] == 0.0]
    lines = ["## 7. What this measurement cannot see", "",
             "This is DOM geometry, not pixels. Four kinds of on-screen motion are invisible to it:", "",
             "1. **Motion inside a `<video>`** - a generative clip filling a world layer has a fixed "
             "bounding box, so a scene carried entirely by clip motion measures `E_primary = 0`.",
             "2. **Motion inside a raster plate or canvas** - the same reason.",
             "3. **Shape change that leaves the bounding-box centre where it was** - a symmetric "
             "grow, a boil, a colour or stroke-width change.",
             "4. **Motion across a content swap** - when an element's text or `src` changes, identity "
             "is reset and the step is dropped, because a caption page turning over is a cut, not a pan."]
    if silent:
        lines += ["", f"Scenes measuring `E_primary = 0` here: **{', '.join(silent)}**. Read that as "
                  "\"no primary DOM element translated\", never as \"nothing moved\" - check the scene's "
                  "world layer before drawing any conclusion from it."]
    return lines + [""]


def _read_paragraph(report: dict) -> str:
    w, scenes = report["whole_screen"], report["scenes"]
    over = [s for s in scenes if s["over_reference"]]
    lead = (f"Whole-screen secondary/primary translation ratio is **{_fmt(w['ratio'])}** against the "
            f"0.22 reference ({'over' if w.get('over_reference') else 'under'} it).")
    scene_bit = ("No scene exceeds 0.22." if not over else
                 f"{len(over)} of {len(scenes)} scenes exceed it: "
                 + ", ".join(f"{s['scene_id']} ({_fmt(s['ratio'])})" for s in over) + ".")
    piece_bit = ("The pieces that dominate are "
                 + ", ".join(f"`{p['key'].split('/')[-1]}` ({' '.join(p['labels'])}, "
                             f"{_fmt(p['e_trans'], 0)})" for p in report["pieces"][:5]) + ".")
    return " ".join([lead, scene_bit, piece_bit,
                     "Read the ratio as a description of this build, not a verdict on it - the number "
                     "it is compared against was invented, and the point of measuring is to replace it "
                     "with one derived from our own footage and the references (BACKLOG X2)."])


# --------------------------------------------------------------------------- P52 T17: the race read
# R26-3's open half. The operator, 2026-09-06: "the race needs to be smoother, it feels a bit choppy."
# Two candidate causes, and they are not the same defect:
#
#   GEOMETRY - curvature at the segment JOINS. A racing mark's path through (value, rank) is a chain
#              of eased segments between period knots; where two segments meet, the curvature can
#              jump. That is the clothoid fitter's case (`kinetics/clothoid.mjs`, doc 42 s42.4:
#              Euler spirals hold dk/ds const and minimise E_MVS = integral (dk/ds)^2 ds).
#   TIMING   - the mark's SPEED over the clock. `LPX.RACE_PERIOD` gives every segment the same
#              duration and eases it in and out, so the speed can fall to nothing at every period.
#              No curve fit touches that.
#
# The two are separated by measuring each on its own axis, so neither can be read as the other:
#   * the geometry read resamples the traced path BY ARCLENGTH at a fixed spacing before it reads
#     curvature, so the clock cannot show up in it at all (a mark that crawls and a mark that
#     sprints along the same path give the same curvature),
#   * the timing read is the speed's SECOND DIFFERENCE over time plus the depth of the speed dip at
#     the period instants, which are properties of the clock and of no shape.
#
# Curvature is Menger's 1 / circumradius signed by the turn - the same law the fitter's own
# `curvatureOf` uses (`kinetics/clothoid.mjs:276`), so an arm measured here and a curve measured
# there are on one scale.
RACE_RESAMPLE_PX = 2.0     # the arclength spacing the geometry read is taken at
RACE_JOIN_GUARD = 3        # ... and how many of those samples either side of a join the jump is read across
RACE_STALL_FRAC = 0.10     # a frame under this share of the window's mean speed is a STALL to the eye

RACE_JS = r"""
(args) => {
  const stage = document.getElementById('stage');
  const sr = stage.getBoundingClientRect();
  const out = [];
  let i = -1;
  for (const b of document.querySelectorAll('svg.lp-chart rect.bar')) {
    i += 1;
    const r = b.getBoundingClientRect();
    const row = b.parentElement, lab = row ? row.querySelector('text.lab') : null;
    const name = lab ? String(lab.textContent || '').trim() : '';
    /* the TIP of the racing mark - the bar's growing end at its own row - is what the eye tracks */
    out.push({mark: name || ('bar' + i),
              x: Math.round((r.x + r.width - sr.x) * 1e3) / 1e3,
              y: Math.round((r.y + r.height / 2 - sr.y) * 1e3) / 1e3});
  }
  return out;
}
"""


def race_tracks(frames) -> dict:
    """[(t, [{mark, x, y}])] -> {mark: [(x, y)]}, keyed by the row's own NAME.

    The engine repaints the rows in value order every frame (the overtaker comes forward), so DOM
    order is not identity - the label is. A mark missing from a frame is dropped from every track,
    because a trajectory with a hole in it is not a trajectory.
    """
    names = None
    for _, marks in frames:
        seen = {m["mark"] for m in marks}
        names = seen if names is None else (names & seen)
    tracks = {n: [] for n in sorted(names or ())}
    for _, marks in frames:
        by_name = {m["mark"]: m for m in marks}
        for n in tracks:
            tracks[n].append((by_name[n]["x"], by_name[n]["y"]))
    return tracks


# ---- the TIMING axis: speed over the clock -----------------------------------------------------
def speed_track(track, fps: float) -> list[float]:
    """|v| per frame pair, px/s. Length is len(track) - 1; pair k spans [t_k, t_k+1]."""
    return [math.hypot(b[0] - a[0], b[1] - a[1]) * fps for a, b in zip(track, track[1:])]


def timing_energy(speeds, fps: float) -> float:
    """E_timing = sum (d2|v| / dt2)^2 dt, px^2/s^5 - the SECOND difference of speed.

    Zero for any motion at a constant speed, however curved its path; large for a clock that
    accelerates and brakes inside every period. It is the timing signal because it is blind to
    where the mark goes and sees only how its speed is being driven.
    """
    if len(speeds) < 3:
        return 0.0
    return sum(((speeds[k + 1] - 2 * speeds[k] + speeds[k - 1]) * fps * fps) ** 2
               for k in range(1, len(speeds) - 1)) / fps


def stall_fraction(speeds, frac: float = RACE_STALL_FRAC) -> float:
    """The share of frame pairs whose speed is under `frac` of the window's mean - the stop-and-go."""
    if not speeds:
        return 0.0
    mean = sum(speeds) / len(speeds)
    if mean <= 0:
        return 1.0
    return sum(1 for v in speeds if v < frac * mean) / len(speeds)


def join_speed_dip(speeds, times, joins, half_window_s: float) -> dict:
    """How far the speed falls AT the period instants, as a share of the window's mean speed.

    `dip` near 0 means the mark stops dead at every period and starts again - the stop-and-go a
    viewer calls choppy. Near 1 means the clock runs through the join.
    """
    if not speeds:
        return {"dip": None, "joins_read": 0, "mean_px_s": 0.0}
    mid = [0.5 * (times[k] + times[k + 1]) for k in range(len(speeds))]
    mean = sum(speeds) / len(speeds)
    at_join = [min((abs(m - j), v) for m, v in zip(mid, speeds))[1]
               for j in joins if min(abs(m - j) for m in mid) <= half_window_s]
    if not at_join or mean <= 0:
        return {"dip": None, "joins_read": len(at_join), "mean_px_s": mean}
    return {"dip": (sum(at_join) / len(at_join)) / mean, "joins_read": len(at_join),
            "mean_px_s": mean, "min_at_join_px_s": min(at_join)}


# ---- the GEOMETRY axis: curvature of the path, with the clock resampled out ---------------------
def arclengths(track) -> list[float]:
    """Cumulative arclength along a sampled trajectory, in px. Same length as the track."""
    out = [0.0]
    for a, b in zip(track, track[1:]):
        out.append(out[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return out


def resample_by_arclength(track, spacing: float = RACE_RESAMPLE_PX) -> list[tuple[float, float]]:
    """The same PATH, sampled every `spacing` px - the clock removed, the shape kept.

    This is what makes the geometry read a geometry read: a mark that crawls through a join and a
    mark that sprints through it resample to the same points, so curvature measured after this step
    cannot be a disguised timing signal.
    """
    s = arclengths(track)
    total = s[-1]
    if total < spacing or spacing <= 0:
        return []
    out, i = [], 0
    for n in range(int(total / spacing) + 1):
        target = n * spacing
        while i + 1 < len(s) - 1 and s[i + 1] < target:
            i += 1
        span = s[i + 1] - s[i]
        f = 0.0 if span <= 0 else (target - s[i]) / span
        out.append((track[i][0] + (track[i + 1][0] - track[i][0]) * f,
                    track[i][1] + (track[i + 1][1] - track[i][1]) * f))
    return out


def curvature_of(pts) -> list[float]:
    """Menger's 1 / circumradius, signed by the turn - `kinetics/clothoid.mjs:276`, in Python.

    The ends copy their neighbours: three points are the smallest thing a curvature can be read
    from. Units 1/px.
    """
    n = len(pts)
    k = [0.0] * n
    for i in range(1, n - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        abx, aby = b[0] - a[0], b[1] - a[1]
        bcx, bcy = c[0] - b[0], c[1] - b[1]
        den = math.hypot(abx, aby) * math.hypot(bcx, bcy) * math.hypot(c[0] - a[0], c[1] - a[1])
        k[i] = (2 * (abx * bcy - aby * bcx) / den) if den > 0 else 0.0
    if n > 2:
        k[0], k[n - 1] = k[1], k[n - 2]
    return k


def curvature_energy(track, spacing: float = RACE_RESAMPLE_PX) -> dict:
    """The two curvature integrals doc 42 s42.4 names, on the arclength-resampled path.

      bending  = integral k^2 ds       [1/px]   - how hard the path bends at all
      fairness = integral (dk/ds)^2 ds [1/px^3] - E_MVS, the functional Euler spirals MINIMISE;
                 this is the one that answers "is the choppiness curvature at the joins", because a
                 curvature that jumps at a join is exactly a large (dk/ds)^2 there.
    """
    pts = resample_by_arclength(track, spacing)
    if len(pts) < 3:
        return {"samples": len(pts), "length_px": arclengths(track)[-1], "bending": 0.0,
                "fairness": 0.0, "kappa_max": 0.0}
    k = curvature_of(pts)
    fairness = sum(((k[i + 1] - k[i]) / spacing) ** 2 for i in range(len(k) - 1)) * spacing
    return {"samples": len(pts), "length_px": arclengths(track)[-1],
            "bending": sum(ki * ki for ki in k) * spacing, "fairness": fairness,
            "kappa_max": max(abs(ki) for ki in k)}


def join_curvature(track, times, joins, spacing: float = RACE_RESAMPLE_PX,
                   guard: int = RACE_JOIN_GUARD) -> dict:
    """The curvature AT each period join, two ways - because a join can fail in two ways.

      peak = max |k| within `guard` arclength samples of the join. A CORNER - two segments meeting
             at an angle - is a curvature SPIKE, and a spike is what peak sees.
      step = |k after - k before| across the same window. A join whose two sides are each smooth but
             bend by different amounts is a curvature STEP, which is what G2 continuity forbids and
             what a clothoid chain is fitted to remove.

    The join's position is found in ARCLENGTH (where the mark had got to at that instant), not in
    frames, so a mark that is barely moving at the join is still read at the right place on its path.
    """
    s = arclengths(track)
    pts = resample_by_arclength(track, spacing)
    empty = {"joins": [], "peak_max": None, "peak_mean": None, "step_max": None, "step_mean": None}
    if len(pts) < 2 * guard + 3:
        return empty
    k = curvature_of(pts)
    rows = []
    for j in joins:
        if j <= times[0] or j >= times[-1]:
            continue
        f = (j - times[0]) / (times[-1] - times[0]) * (len(times) - 1)
        i = min(int(f), len(s) - 2)
        s_join = s[i] + (s[i + 1] - s[i]) * (f - i)
        n = int(round(s_join / spacing))
        if n - guard < 0 or n + guard >= len(k):
            continue
        rows.append({"at_s": round(j, 3), "arclength_px": round(s_join, 2),
                     "k_before": k[n - guard], "k_after": k[n + guard],
                     "step": abs(k[n + guard] - k[n - guard]),
                     "peak": max(abs(v) for v in k[n - guard:n + guard + 1])})
    if not rows:
        return empty
    peaks = [r["peak"] for r in rows]
    steps = [r["step"] for r in rows]
    return {"joins": rows, "peak_max": max(peaks), "peak_mean": sum(peaks) / len(peaks),
            "step_max": max(steps), "step_mean": sum(steps) / len(steps)}


# ---- the two reads, folded per mark and over the window ----------------------------------------
def race_read(frames, fps: float, joins, spacing: float = RACE_RESAMPLE_PX) -> dict:
    """Both axes on every racing mark in the window, and the window's totals."""
    times = [t for t, _ in frames]
    tracks = race_tracks(frames)
    half = 1.0 / fps   # the frame PAIR that straddles a join, with a frame of slack for the float
    marks = []
    for name, track in tracks.items():
        speeds = speed_track(track, fps)
        geom = curvature_energy(track, spacing)
        jn = join_curvature(track, times, joins, spacing)
        dip = join_speed_dip(speeds, times, joins, half)
        mean = (sum(speeds) / len(speeds)) if speeds else 0.0
        sd = math.sqrt(sum((v - mean) ** 2 for v in speeds) / len(speeds)) if speeds else 0.0
        marks.append({
            "mark": name, "length_px": geom["length_px"], "samples": geom["samples"],
            "timing_energy": timing_energy(speeds, fps), "speed_cv": (sd / mean) if mean > 0 else 0.0,
            "stall_fraction": stall_fraction(speeds), "join_speed_dip": dip["dip"],
            "mean_px_s": mean, "max_px_s": max(speeds) if speeds else 0.0,
            "bending": geom["bending"], "fairness": geom["fairness"], "kappa_max": geom["kappa_max"],
            "join_peak_mean": jn["peak_mean"], "join_peak_max": jn["peak_max"],
            "join_step_mean": jn["step_mean"], "join_step_max": jn["step_max"], "joins": jn["joins"],
        })
    marks.sort(key=lambda m: m["mark"])
    dips = [m["join_speed_dip"] for m in marks if m["join_speed_dip"] is not None]
    return {
        "fps": fps, "frames": len(frames), "from_s": times[0] if times else 0.0,
        "to_s": times[-1] if times else 0.0, "joins": list(joins), "resample_px": spacing,
        "marks": marks,
        "totals": {
            "marks": len(marks),
            "timing_energy": sum(m["timing_energy"] for m in marks),
            "speed_cv": (sum(m["speed_cv"] for m in marks) / len(marks)) if marks else 0.0,
            "stall_fraction": (sum(m["stall_fraction"] for m in marks) / len(marks)) if marks else 0.0,
            "join_speed_dip": (sum(dips) / len(dips)) if dips else None,
            "bending": sum(m["bending"] for m in marks),
            "fairness": sum(m["fairness"] for m in marks),
            "join_peak_mean": _mean_of([m["join_peak_mean"] for m in marks]),
            "join_peak_max": max([m["join_peak_max"] for m in marks if m["join_peak_max"] is not None] or [0.0]),
            "join_step_mean": _mean_of([m["join_step_mean"] for m in marks]),
            "join_step_max": max([m["join_step_max"] for m in marks if m["join_step_max"] is not None] or [0.0]),
        },
    }


def _mean_of(values) -> float | None:
    vals = [v for v in values if v is not None]
    return (sum(vals) / len(vals)) if vals else None


def race_markdown(read: dict, build_dir: Path) -> str:
    t = read["totals"]
    lines = [f"# The race read - {_rel(build_dir)}", "",
             f"{read['frames']} frames at {read['fps']:g} fps over {read['from_s']:g}-{read['to_s']:g} s; "
             f"{t['marks']} racing marks; the geometry axis resampled every {read['resample_px']:g} px of "
             "arclength so the clock is out of it.", "",
             "| axis | reading | value | what it is |", "|---|---|---:|---|",
             f"| TIMING | timing energy (px^2/s^5) | {t['timing_energy']:,.0f} | "
             "`integral (d2|v|/dt2)^2 dt` - zero at any constant speed, whatever the shape |",
             f"| TIMING | speed CV | {t['speed_cv']:.3f} | the speed's own spread over the window |",
             f"| TIMING | stall fraction | {t['stall_fraction']:.3f} | share of frames under "
             f"{RACE_STALL_FRAC:.0%} of the mean speed |",
             f"| TIMING | join speed dip | {_fmt(t['join_speed_dip'])} | speed AT a period, over the mean. "
             "Near 0 = the mark stops dead at every period |",
             f"| GEOMETRY | bending `integral k^2 ds` (1/px) | {t['bending']:.6f} | how hard the path bends |",
             f"| GEOMETRY | fairness `E_MVS = integral (dk/ds)^2 ds` (1/px^3) | {t['fairness']:.6g} | "
             "the functional Euler spirals minimise (42 s42.4) |",
             f"| GEOMETRY | join curvature PEAK, mean (1/px) | {_fmt(t['join_peak_mean'], 6)} | "
             "max |k| at the period knots - a CORNER is a spike |",
             f"| GEOMETRY | join curvature peak, max (1/px) | {t['join_peak_max']:.6f} | the worst join |",
             f"| GEOMETRY | join curvature STEP, mean (1/px) | {_fmt(t['join_step_mean'], 6)} | "
             "|k after - k before| - what G2 continuity forbids, and what the fitter removes |", "",
             "## Per mark", "",
             "| mark | path (px) | mean px/s | timing energy | speed CV | stalls | join dip | bending | fairness | join peak | join step |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for m in read["marks"]:
        lines.append(f"| {m['mark']} | {m['length_px']:,.0f} | {m['mean_px_s']:,.0f} | "
                     f"{m['timing_energy']:,.0f} | {m['speed_cv']:.3f} | {m['stall_fraction']:.3f} | "
                     f"{_fmt(m['join_speed_dip'])} | {m['bending']:.6f} | {m['fairness']:.6g} | "
                     f"{_fmt(m['join_peak_max'], 6)} | {_fmt(m['join_step_max'], 6)} |")
    return "\n".join(lines + ["", "Read the two axes against the OTHER ARM, never against a threshold: "
                              "neither number has a published floor, and the A/B is the whole point.", "",
                              "## What this read does and does not see", "",
                              "- The GEOMETRY axis is measured on the mark\'s path in SCREEN pixels, which "
                              "carries the axis glide (the race retargets `scaleMax` every frame as the "
                              "leader grows). Both arms carry the same glide, so the A/B is fair, but an "
                              "absolute curvature here is not the curvature of the data-space path a fitter "
                              "would be fitting.",
                              "- A row that never changes rank travels a straight horizontal line whatever "
                              "the clock does, so its curvature is zero BY CONSTRUCTION. That row is the "
                              "control: whatever choppiness it has cannot be curvature.",
                              "- This is DOM geometry - the bar\'s tip, not pixels. Blur, colour, stroke "
                              "width and anything inside a raster are invisible to it.", ""])


def sample_race(build_dir: Path, fps: float, t_from: float, t_to: float, progress=None):
    """Seek the built player to each sampled t and read every racing mark's tip under `svg.lp-chart`."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from render_baseline import prepare_page, serve                     # noqa: PLC0415 - optional dep
    from playwright.sync_api import sync_playwright                     # noqa: PLC0415

    player = build_dir / "player.html"
    if not player.exists():
        raise SystemExit(f"no player.html in {build_dir}")
    aspect = str(load_timeline(build_dir).get("aspect") or "16:9")
    width, height = STAGE_SIZE[aspect]
    times = frame_times(t_from, t_to, fps)
    frames = []
    srv, port = serve(build_dir)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": width, "height": height},
                                       device_scale_factor=1).new_page()
            page.goto(f"http://127.0.0.1:{port}/player.html", wait_until="networkidle", timeout=180000)
            prepare_page(page, width, height)
            for i, t in enumerate(times):
                page.evaluate("t => { const s = document.getElementById('scrub');"
                              " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                marks = page.evaluate(RACE_JS, {})
                if not marks:
                    raise SystemExit(f"no racing marks under svg.lp-chart at t={t} - is {build_dir} a race?")
                frames.append((t, marks))
                if progress and i % 50 == 0:
                    progress(i, len(times))
            browser.close()
    finally:
        srv.shutdown()
    return frames


RACE_CLOCK_KEYS = ("ROLL", "SAVOR", "FIELD", "RACE_IN", "RACE_PERIOD")


def race_clock(engine_text: str) -> dict:
    """The page's own clock, READ OFF THE ENGINE the build was written against - never guessed.

    `LP.ROLL + LP.SAVOR + LP.FIELD` is the lead before the build beat (`t3`, engine's paint call),
    then `LPX.RACE_IN` of grow-in and `LPX.RACE_PERIOD` per period. A key that does not resolve to
    exactly one number raises, because a measurement window derived from the wrong constant is worse
    than no measurement.
    """
    clock = {}
    for key in RACE_CLOCK_KEYS:
        hits = re.findall(rf"\b{key}:\s*([0-9]+(?:\.[0-9]+)?)\s*,", engine_text)
        if len(hits) != 1:
            raise SystemExit(f"{key} resolves to {len(hits)} numbers in the engine, expected 1")
        clock[key] = float(hits[0])
    clock["lead"] = clock["ROLL"] + clock["SAVOR"] + clock["FIELD"]
    return clock


def build_engine_text(build_dir: Path) -> str:
    """The engine COPY a split build carries (`player.json` names it), else the repo's own."""
    manifest = build_dir / "player.json"
    if manifest.exists():
        name = (json.loads(manifest.read_text(encoding="utf-8")) or {}).get("engine")
        if name and (build_dir / name).exists():
            return (build_dir / name).read_text(encoding="utf-8")
    return (REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")


def race_scene(timeline: dict) -> tuple[dict, dict]:
    """The first scene whose world is a ledger page built by the RACE builder, and that page."""
    for sc in timeline.get("scenes") or []:
        page = ((sc.get("world") or {}).get("page")) or {}
        if page.get("builder") == "race" or page.get("variant") == "race":
            return sc, page
    raise SystemExit("no scene in this timeline carries a race page (world.page.builder == 'race')")


def race_joins(timeline: dict, clock: dict) -> list[float]:
    """The period instants, in episode seconds: the knots of the path AND the beats of the clock."""
    scene, page = race_scene(timeline)
    t0 = float((scene.get("span") or [0.0])[0]) + clock["lead"] + clock["RACE_IN"]
    return [round(t0 + i * clock["RACE_PERIOD"], 4) for i in range(len(page.get("periods") or []))]


# --------------------------------------------------------------------------- cli
def run_race(build_dir: Path, timeline: dict, fps: float, window, report: Path | None) -> int:
    """P52 T17: both arms of the race A/B are run through this - one page, one clock, two numbers."""
    clock = race_clock(build_engine_text(build_dir))
    joins = race_joins(timeline, clock)
    if len(joins) < 2:
        raise SystemExit("a race with fewer than two periods has no joins to read")
    t_from, t_to = (float(window[0]), float(window[1])) if window else (joins[0], joins[-1])
    started = time.time()
    frames = sample_race(build_dir, fps, t_from, t_to,
                         progress=lambda i, n: print(f"  sampled {i}/{n} frames", flush=True))
    read = race_read(frames, fps, [j for j in joins if t_from <= j <= t_to])
    read["build_dir"] = _rel(build_dir)
    read["engine"] = (json.loads((build_dir / "player.json").read_text(encoding="utf-8"))
                      if (build_dir / "player.json").exists() else {})
    read["clock"] = clock
    read["elapsed_s"] = round(time.time() - started, 1)
    md_path = report or (build_dir / "RACE-MOTION.md")
    json_path = md_path.with_suffix(".json") if md_path.suffix == ".md" else build_dir / "RACE-MOTION.json"
    md_path.write_text(race_markdown(read, build_dir), encoding="utf-8")
    json_path.write_text(json.dumps(read, indent=2), encoding="utf-8")
    t = read["totals"]
    print(f"{md_path}\n{json_path}")
    print(f"race read: {read['frames']} frames {t_from:g}-{t_to:g}s, {t['marks']} marks, "
          f"{len(read['joins'])} joins ({read['elapsed_s']}s)")
    print(f"  TIMING    energy {t['timing_energy']:,.0f} px^2/s^5 | speed CV {t['speed_cv']:.3f} | "
          f"stalls {t['stall_fraction']:.3f} | join dip {_fmt(t['join_speed_dip'])}")
    print(f"  GEOMETRY  bending {t['bending']:.6f} 1/px | fairness {t['fairness']:.6g} 1/px^3")
    print(f"  GEOMETRY  join curvature peak mean {_fmt(t['join_peak_mean'], 6)} "
          f"max {t['join_peak_max']:.6f} | join curvature step mean {_fmt(t['join_step_mean'], 6)} "
          f"max {t['join_step_max']:.6f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Measure on-screen motion energy of a built player.")
    ap.add_argument("build_dir", type=Path)
    ap.add_argument("--fps", type=float, default=DEFAULT_FPS)
    ap.add_argument("--from", dest="t_from", type=float, default=0.0)
    ap.add_argument("--to", dest="t_to", type=float, default=None)
    ap.add_argument("--window", nargs=2, type=float, metavar=("T0", "T1"),
                    help="measure this window only; with --race it defaults to the race's own "
                         "first-to-last period, read off the engine the build carries")
    ap.add_argument("--race", action="store_true",
                    help="the RACE read (P52 T17 / R26-3): per racing mark, the CURVATURE of its path "
                         "with the clock resampled out (the geometry axis, the clothoid fitter's case) "
                         "and the SPEED's second difference over the clock (the timing axis)")
    ap.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)
    ap.add_argument("--top", type=int, default=TOP_PIECES)
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args(argv)

    build_dir = args.build_dir.resolve()
    timeline = load_timeline(build_dir)
    if args.race:
        return run_race(build_dir, timeline, args.fps, args.window, args.report)
    t_from = args.window[0] if args.window else args.t_from
    t_to = args.window[1] if args.window else (
        args.t_to if args.t_to is not None else float(timeline.get("runtime_s") or 0.0))
    windows = scene_windows(timeline)
    if not windows:
        raise SystemExit(f"the timeline in {build_dir} declares no scenes")

    started = time.time()
    frames = sample_build(build_dir, args.fps, t_from, t_to, args.max_depth,
                          progress=lambda i, n: print(f"  sampled {i}/{n} frames", flush=True))
    folded = accumulate(frames, args.fps, windows)
    report = build_report(build_dir, timeline, folded, args.fps, t_from, t_to,
                          time.time() - started, args.max_depth)

    md_path = args.report or (build_dir / "MOTION-ENERGY.md")
    json_path = (md_path.with_suffix(".json") if md_path.suffix == ".md"
                 else build_dir / "MOTION-ENERGY.json")
    md_path.write_text(markdown(report, args.top), encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"{md_path}\n{json_path}")
    print(f"whole-screen ratio {_fmt(report['whole_screen']['ratio'])} vs "
          f"{SECONDARY_REFERENCE_RATIO} ({report['frames']} frames, {report['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
