"""G-l - the vertical safe-box gate (P37 T8): on a 9:16 stage every dock, and the anchored
caption, must sit inside x[80,880] y[280,1340] / the caption strip y[1340,1440].

Two readers, one rule:
  * static  - the template's `html[data-aspect="9:16"]` CSS (fast, runs anywhere, and FAILs the
              template as it shipped before P37 T0, which is this gate's fixture)
  * rendered - a built player's actual dock/caption rectangles at t (needs playwright; run by
              the tests and by hand on a Tokyo build)

    python gate_vertical_safe_box.py docs/content-video-engine/samples/scene-evidence-player.template.html

G-l16 - THE LANDSCAPE MODE (P72 T8, R26-206; the same tool, `--aspect 16:9`): on a 1920x1080 stage every dock box
and the anchored caption clear YouTube's hover-controls band, the bottom 120 px; the anchored caption also keeps its
145 px rails (its own strip, `ledger_page.CAPTION_ANCHOR["16:9"] = (145, 878, 1630, 82)`). The band's sources:
doc 29 s9.15 ruling 7 (the operator, 2026-09-02) and the template's `#caption` comment; MEASURED 2026-09-25 on the
player itself (P72 T8): the normal watch-page player at a 1366x768 screen (942x530) lays `.ytp-chrome-bottom` over
the bottom 120.2 px of the 1080 stage (11.13 %), at 1920x1080 (1344x756) 84.3 px. The controls' own inset is
17-25 px - nothing overlays a side, so a dock is judged on the band alone (the rails are the caption's box, not chrome).

    python gate_vertical_safe_box.py <build-dir> --aspect 16:9 [--rendered]
        reads <build-dir>/player.html's CSS (else the template's) for the slot docks and the caption, and every
        box a PLACED dock occupies in the compiled *.timeline.json: `place`, `read_place`, each of its `moves`.
        The timeline's box is the COMPILER'S estimate: measured on H 2026-09-25 a served card at rest renders
        15-40 px taller than its `place.h` (its rail and chrome; 27 of 29 reads), so `--rendered` also serves the
        player (probe.py) and reads every placed dock's rendered box where it settles, and the anchored caption's,
        against the same band.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SAFE_X = (80, 880)
SAFE_Y = (280, 1340)
CAPTION_STRIP = (1340, 1440)
STAGE_H = 1920
# a dock's height at 800px wide: frame 430 + rail 39 + chrome 45 (measured, P37 T0). Scales with width.
DOCK_H_PER_W = 514 / 800
SRC_G_L = "47 s2 G-l / 49 s49.1, 50: platform chrome covers the top 280, bottom 480 and right 200 px of a 1080x1920 short"

# ---- the LANDSCAPE stage (R26-206) - see the module docstring for the band's sources and its measurement
LAND_STAGE = (1920, 1080)
LAND_BAND_PX = 120               # YouTube's hover-controls bar: ruling 7's 120 px, measured 120.2 px on the normal player
LAND_CAPTION_RAIL = 145          # the anchored caption's own left / right (template `#caption`, CAPTION_ANCHOR["16:9"])
TEMPLATE_REL = "docs/content-video-engine/samples/scene-evidence-player.template.html"
REPO = Path(__file__).resolve().parents[3]
SRC_G_L16 = ("doc 29 s9.15 ruling 7 (operator, 2026-09-02): YouTube's hover-controls bar covers the bottom ~11 % of the "
             "normal and embedded player - nothing that must be read sits in the bottom 120 px of the 1080p stage "
             "(measured 2026-09-25: 120.2 px on the 942x530 normal player, P72 T8)")


@dataclass(frozen=True)
class Finding:
    element: str
    detail: str
    gate: str = "G-l"
    src: str = SRC_G_L

    def line(self) -> str:
        return f"FAIL {self.gate} {self.element}: {self.detail}\n     {self.src}"


def _land(element: str, detail: str) -> Finding:
    return Finding(element, detail, "G-l16", SRC_G_L16)


def _px(rule: str, prop: str) -> float | None:
    m = re.search(rf"(?<![\w-]){prop}:\s*(-?[0-9.]+)px", rule)
    return float(m.group(1)) if m else None


def _rules(css: str, selector_regex: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r'html\[data-aspect="9:16"\]\s*' + selector_regex + r"\s*\{([^}]*)\}", css)]


def check_template_css(css: str) -> list[Finding]:
    """The 9:16 overrides, read as text. Width/left from the .dock and #dock-N rules; height derived."""
    out: list[Finding] = []
    dock = " ".join(_rules(css, r"\.dock"))
    width, top = _px(dock, "width"), _px(dock, "top")
    if width is None or top is None:
        return [Finding("dock", "no html[data-aspect=\"9:16\"] .dock rule with width and top")]
    height = width * DOCK_H_PER_W
    for name in ("#dock-1", "#dock-2"):
        own = " ".join(_rules(css, re.escape(name) + r"(?![.\w-])"))
        left = _px(own, "left")
        t = _px(own, "top") if _px(own, "top") is not None else top
        if left is None:
            out.append(Finding(name, "no 9:16 left rule")); continue
        if left < SAFE_X[0] or left + width > SAFE_X[1]:
            out.append(Finding(name, f"x {left:.0f}-{left + width:.0f} leaves the box x{SAFE_X}"))
        if t < SAFE_Y[0] or t + height > SAFE_Y[1]:
            out.append(Finding(name, f"y {t:.0f}-{t + height:.0f} (height {height:.0f} at {width:.0f} wide) leaves the box y{SAFE_Y}"))
    cap = " ".join(_rules(css, r"#caption\.quiet"))
    bottom = _px(cap, "bottom")
    if bottom is None:
        out.append(Finding("#caption.quiet", "no 9:16 bottom rule - the caption inherits the 16:9 offset and lands in the bottom dead zone"))
    elif not (STAGE_H - CAPTION_STRIP[1] <= bottom <= STAGE_H - CAPTION_STRIP[0]):
        out.append(Finding("#caption.quiet", f"bottom {bottom:.0f}px puts the caption outside the strip y{CAPTION_STRIP}"))
    return out


def check_rects(rects: dict[str, dict]) -> list[Finding]:
    """Rendered rectangles {id: {x, y, right, bottom}} on the 1080x1920 stage."""
    out: list[Finding] = []
    for name, r in rects.items():
        if name.startswith("dock"):
            if r["x"] < SAFE_X[0] or r["right"] > SAFE_X[1]:
                out.append(Finding(name, f"x {r['x']:.0f}-{r['right']:.0f} leaves x{SAFE_X}"))
            if r["y"] < SAFE_Y[0] or r["bottom"] > SAFE_Y[1]:
                out.append(Finding(name, f"y {r['y']:.0f}-{r['bottom']:.0f} leaves y{SAFE_Y}"))
        elif name == "caption":
            if r["y"] < CAPTION_STRIP[0] - 1 or r["bottom"] > CAPTION_STRIP[1] + 1:
                out.append(Finding(name, f"y {r['y']:.0f}-{r['bottom']:.0f} is not in the strip y{CAPTION_STRIP}"))
    return out


# ---- G-l16: the landscape reader (P72 T8, R26-206) --------------------------------------------------------------

def landscape_rules(css: str) -> dict[str, str]:
    """The UNSCOPED rules - the 16:9 default - by selector: a page's <style> blocks (or bare CSS), comments dropped, every
    `html[...]`-scoped override (9:16, the layer toggles) left out."""
    body = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", css, re.S | re.I)) or css
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    rules: dict[str, str] = {}
    for selectors, decls in re.findall(r"([^{}]+)\{([^{}]*)\}", body):
        for sel in (x.strip() for x in selectors.split(",")):
            if sel and not sel.startswith("html["):
                rules[sel] = rules.get(sel, "") + " " + decls
    return rules


def _band_top() -> int:
    return LAND_STAGE[1] - LAND_BAND_PX


def check_template_css_landscape(css: str) -> list[Finding]:
    """The 16:9 slot docks (#dock-1, #dock-2, the solo card and its two sides) and the anchored caption, read as text.
    A dock's height is derived from its width as the 9:16 reader derives it (DOCK_H_PER_W, measured)."""
    rules = landscape_rules(css)
    px = lambda sel, prop: _px(rules.get(sel, ""), prop)
    out: list[Finding] = []
    top, width = px(".dock", "top"), px(".dock", "width")
    solo_top, solo_w = px("#dock-1.solo", "top"), px("#dock-1.solo", "width")
    slots = [("#dock-1", top, width), ("#dock-2", top, width), ("#dock-1.solo", solo_top, solo_w),
             ("#dock-1.solo.side-r", solo_top, solo_w), ("#dock-1.solo.side-l", solo_top, solo_w)]
    for name, t, w in slots:
        if t is None or w is None:
            continue
        bottom = t + w * DOCK_H_PER_W
        if bottom > _band_top():
            out.append(_land(name, f"bottom {bottom:.0f} (top {t:.0f}, height {w * DOCK_H_PER_W:.0f} at {w:.0f} wide) "
                                   f"is inside the bottom {LAND_BAND_PX} px - the band starts at y {_band_top()}"))
    out += _caption_landscape(rules)
    return out


def _caption_landscape(rules: dict[str, str]) -> list[Finding]:
    cap = rules.get("#caption", "")
    bottom, left, right = _px(cap, "bottom"), _px(cap, "left"), _px(cap, "right")
    if bottom is None or left is None or right is None:
        return [_land("#caption", "no unscoped #caption rule with bottom, left and right - the anchor is not declared")]
    out: list[Finding] = []
    if bottom < LAND_BAND_PX:
        out.append(_land("#caption", f"bottom {bottom:.0f}px puts the anchored caption inside the bottom "
                                     f"{LAND_BAND_PX} px"))
    if left < LAND_CAPTION_RAIL or right < LAND_CAPTION_RAIL:
        out.append(_land("#caption", f"left {left:.0f} / right {right:.0f} px leave the strip's "
                                     f"{LAND_CAPTION_RAIL} px rails (CAPTION_ANCHOR[\"16:9\"])"))
    return out


def dock_boxes(dock: dict) -> list[tuple[str, dict]]:
    """Every box a PLACED dock occupies: its `place`, the `read_place` it pops at, and each pose its `moves` end on (a
    move is a whole box in stage px, its height kept at the placed card's aspect - the engine's `propPose`). A slot dock
    (no `place`) reads at the template's slot rule, judged by `check_template_css_landscape`."""
    place = dock.get("place")
    if not place:
        return []
    boxes = [("place", place)] + ([("read_place", dock["read_place"])] if dock.get("read_place") else [])
    aspect = place["h"] / place["w"] if place.get("w") else 0.0
    boxes += [(f"move at {float(mv['at']):.2f}s", {"x": mv["x"], "y": mv["y"], "w": mv["w"], "h": mv["w"] * aspect})
              for mv in dock.get("moves") or []]
    return boxes


def check_timeline_landscape(timeline: dict) -> tuple[list[Finding], int]:
    """(findings, docks checked): every dock of every scene, each box against the bottom band."""
    out: list[Finding] = []
    n = 0
    for scene in timeline.get("scenes") or []:
        for dock in scene.get("docks") or []:
            n += 1
            for what, box in dock_boxes(dock):
                bottom = box["y"] + box["h"]
                if bottom > _band_top():
                    out.append(_land(f"{scene.get('scene_id')} {dock.get('slide')}",
                                     f"{what} x {box['x']:.0f} y {box['y']:.0f} w {box['w']:.0f} h {box['h']:.0f} - "
                                     f"bottom {bottom:.0f} is inside the bottom {LAND_BAND_PX} px (the band starts at "
                                     f"y {_band_top()})"))
    return out, n


def lowest_box(timeline: dict) -> str:
    """The dock box nearest the band (its bottom, the scene, the dock, which box) - how close a PASS came."""
    boxes = [(box["y"] + box["h"], scene.get("scene_id"), dock.get("slide"), what)
             for scene in timeline.get("scenes") or [] for dock in scene.get("docks") or []
             for what, box in dock_boxes(dock)]
    if not boxes:
        return "no placed dock"
    bottom, sid, slide, what = max(boxes, key=lambda b: b[0])
    return (f"the lowest placed box ends at y {bottom:.0f} ({sid} {slide} {what}), "
            f"{_band_top() - bottom:.0f} px above the band")


def check_rects_landscape(rects: dict[str, dict]) -> list[Finding]:
    """Rendered rectangles {name: {x, y, right, bottom}} on the 1920x1080 stage, against the band (the rendered
    caption's glyph run may pass its CSS box by a few px - its rails are judged on the CSS, its band here)."""
    return [_land(name, f"rendered y {r['y']:.0f}-{r['bottom']:.0f} is inside the bottom {LAND_BAND_PX} px (the band "
                        f"starts at y {_band_top()})")
            for name, r in rects.items() if r["bottom"] > _band_top() + 1]


SETTLE_PAD_S = 0.15    # past a landing / a park / a move before the box is read
EXIT_PAD_S = 0.10      # before the dock's exit or its scene's end - a card leaving (a snap's zoom, a dip) is a path


def settle_instants(timeline: dict) -> list[tuple[float, str, str]]:
    """(t, scene, slide) for every placed dock where it SETTLES: at its read box, after its read + park at its place
    (a card that does not park rests after its landing, one read_s), and after each move - each instant inside the
    dock's life AND its own scene, so a card carried into the next scene's hand-off is not read mid-flight (R26-202 (a))."""
    out = []
    for scene in timeline.get("scenes") or []:
        span_end = float((scene.get("span") or [0.0, float("inf")])[1])
        for dock in scene.get("docks") or []:
            if not dock.get("place"):
                continue
            enter = float(dock["enter"])
            last = min(float(dock["exit"]), span_end) - EXIT_PAD_S
            read_s, park_s = float(dock.get("read_s") or 1.2), float(dock.get("park_s") or 0.7)
            ts = [enter + (read_s + park_s if dock.get("park") else read_s) + SETTLE_PAD_S]
            ts += [enter + 0.8 * read_s] if dock.get("read_place") else []
            ts += [float(mv["at"]) + float(mv.get("dur") or 0.0) + SETTLE_PAD_S for mv in dock.get("moves") or []]
            out += [(round(min(t, last), 2), scene.get("scene_id"), dock.get("slide")) for t in ts if enter < min(t, last)]
    return sorted(set(out))                          # a short life clips two instants onto one


def check_rendered_landscape(build: Path) -> tuple[list[Finding], int, int]:
    """Serve the build's player (probe.py - playwright) and read each placed dock's RENDERED box at its settle instants
    - only where the probe reads it AT REST (a moving card is on its path, R26-202 (a)) - and the anchored caption's box
    at the same instants. Returns (findings, instants read, dock reads skipped because the card was still moving)."""
    import probe                                     # noqa: PLC0415 - playwright is only needed for this reader
    timeline = json.loads(compiled_timeline(Path(build)).read_text(encoding="utf-8"))
    instants = settle_instants(timeline)
    out: list[Finding] = []
    moving = 0
    with probe.Probe(Path(build), compiled_timeline(Path(build)).name) as player:
        for t, sid, slide in instants:
            inst = player.at(t, f"G-l16 {sid} {slide}")
            mine = [d for d in inst.get("docks") or [] if d.get("id") == slide]
            moving += sum(1 for d in mine if not d.get("rest"))
            rects = {f"{sid} {d['id']} @ {t:.2f}s": _xywh(d["box"]) for d in mine if d.get("rest")}
            cap = (inst.get("caption") or {}).get("box")
            if cap and (inst.get("caption") or {}).get("mode") == "anchor":
                rects[f"#caption @ {t:.2f}s"] = _xywh(cap)
            out += check_rects_landscape(rects)
    return out, len(instants), moving


def _xywh(box: list) -> dict:
    x, y, w, h = box
    return {"x": x, "y": y, "right": x + w, "bottom": y + h}


def compiled_timeline(build: Path) -> Path:
    """A build dir's compiled `*.timeline.json` (the words file `timeline.json` is not it)."""
    found = sorted(p for p in build.glob("*.timeline.json") if p.name != "timeline.json")
    if not found:
        raise SystemExit(f"no compiled *.timeline.json in {build}")
    return found[0]


def check_build_landscape(build: Path) -> tuple[list[Finding], int]:
    """A build dir at 16:9: its player's CSS (the repo template when the build has no player.html) and its compiled
    timeline's docks. Returns (findings, docks checked)."""
    build = Path(build)
    player = build / "player.html"
    css = (player if player.is_file() else REPO / TEMPLATE_REL).read_text(encoding="utf-8")
    timeline = json.loads(compiled_timeline(build).read_text(encoding="utf-8"))
    placed, n = check_timeline_landscape(timeline)
    return check_template_css_landscape(css) + placed, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("template", help="9:16: the player template (or a built player) to read the CSS from; 16:9: a "
                                     "build dir (its player.html and compiled timeline) or a template / player")
    ap.add_argument("--aspect", choices=("9:16", "16:9"), default="9:16",
                    help="the stage to judge (default 9:16, G-l; 16:9 is G-l16, the landscape band - P72 T8)")
    ap.add_argument("--rendered", action="store_true",
                    help="16:9 build dir: also serve the player and read every placed dock's rendered box (playwright)")
    args = ap.parse_args()
    if args.rendered and not (args.aspect == "16:9" and Path(args.template).is_dir()):
        ap.error("--rendered reads a 16:9 BUILD DIR (--aspect 16:9 <build-dir>)")
    target = Path(args.template)
    checked = ""
    if args.aspect == "9:16":
        findings = check_template_css(target.read_text(encoding="utf-8"))
    elif target.is_dir():
        findings, n = check_build_landscape(target)
        timeline = compiled_timeline(target)
        low = lowest_box(json.loads(timeline.read_text(encoding="utf-8")))
        checked = f"{n} docks in {timeline.name} ({low}), the 16:9 slot rules and the anchored caption - "
        if args.rendered:
            served, k, moving = check_rendered_landscape(target)
            findings += served
            checked += f"{k} settle instants rendered ({moving} dock reads still moving, not judged) - "
    else:
        findings = check_template_css_landscape(target.read_text(encoding="utf-8"))
    for f in findings:
        print(f.line())
    print(f"VERDICT: {'FAIL' if findings else 'PASS'} ({len(findings)} finding{'s' if len(findings) != 1 else ''}) - "
          f"{checked}{args.template}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
