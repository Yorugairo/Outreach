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
"""
from __future__ import annotations

import argparse
import json
import math
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


# --------------------------------------------------------------------------- cli
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Measure on-screen motion energy of a built player.")
    ap.add_argument("build_dir", type=Path)
    ap.add_argument("--fps", type=float, default=DEFAULT_FPS)
    ap.add_argument("--from", dest="t_from", type=float, default=0.0)
    ap.add_argument("--to", dest="t_to", type=float, default=None)
    ap.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)
    ap.add_argument("--top", type=int, default=TOP_PIECES)
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args(argv)

    build_dir = args.build_dir.resolve()
    timeline = load_timeline(build_dir)
    t_to = args.t_to if args.t_to is not None else float(timeline.get("runtime_s") or 0.0)
    windows = scene_windows(timeline)
    if not windows:
        raise SystemExit(f"the timeline in {build_dir} declares no scenes")

    started = time.time()
    frames = sample_build(build_dir, args.fps, args.t_from, t_to, args.max_depth,
                          progress=lambda i, n: print(f"  sampled {i}/{n} frames", flush=True))
    folded = accumulate(frames, args.fps, windows)
    report = build_report(build_dir, timeline, folded, args.fps, args.t_from, t_to,
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
