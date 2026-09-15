"""G49 - THE THUMBNAIL'S TEXT IS NOT CLIPPED (the operator, 2026-09-02, ledger 3570a6280d20).

    > "it's better but still aprtially cut, i dont know why you can't see that."

G45 and J12 check the thumbnail's WORDS - that the first sentence answers what the packaging
posed. Neither of them, and nothing else in the registry, ever measured a PIXEL: a headline or a
sticker whose glyph box runs off the frame reads as a cut word at 320 px wide in the feed, and the
operator had to say so twice. `docs/operator-ledger/TRIAGE-DIGEST.md` (slug `thumbnail-text-clipping`):
*"Measure each glyph's pixel box on the thumbnail or sticker against the frame edges at display size.
G45 and J12 only check the words."*

  G49  every text box on the thumbnail - the headline, the badge, the      FAIL   (ledger 3570a6280d20;
       sticker - sits inside the frame by the margin dial. A box that              PASS when every box
       crosses an edge is a cut word at display size                               clears the edge)

TWO READERS, ONE RULE - gate_vertical_safe_box.py's shape:

  * declared - a LAYOUT json the packaging step writes or an author hands over:
      {"frame": [W, H], "boxes": [{"role": "headline", "text": "...", "box": [x, y, w, h]}, ...]}
    Boxes are in the frame's own pixels; `role` and `text` only name the row.

  * probed   - a page's landing frame IS the thumbnail (E67 s4, PACKAGING-PLAYBOOK: "a page's
    landing frame must read at 320 px wide with its line, its title and its one figure"), and
    probe.py --gate already wrote every one of its text boxes. `--probe <build>/layout-probe.json
    --at <t>` reads the page's own runs and every chart label at that instant against the stage.

Clipping is scale-invariant, so the geometry is decided in the frame's own pixels; `--display`
(default 320, the feed width E67 s4 names) only says how many pixels of the word are gone where
the viewer sees it, because that is the number the operator was looking at.

    python gate_thumbnail_text.py --layout thumb-layout.json
    python gate_thumbnail_text.py --probe <build>/layout-probe.json --at 9.0
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

MARGIN_PX = 0.0        # the dial: how far INSIDE every edge a text box must sit. 0 = refuse only what is
                       # actually clipped, which is the operator's complaint and nothing more. Raise it to
                       # buy platform chrome or a rounded corner back.
DISPLAY_W = 320        # E67 s4 / PACKAGING-PLAYBOOK: the width a thumbnail is actually read at
PROBE_PAGE_RUNS = ("title", "sub", "source", "note")   # probe.py's own page keys, the runs a page writes
STAGE = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
SRC_G49 = ("thumbnail-text-clipping (the operator, 2026-09-02, ledger 3570a6280d20; "
           "docs/operator-ledger/TRIAGE-DIGEST.md): each glyph's pixel box on the thumbnail or the sticker, "
           "measured against the frame edges - G45 and J12 check only the WORDS. E67 s4 / "
           "docs/portable/PACKAGING-PLAYBOOK.md:78: the thumbnail is read at 320 px wide")


@dataclass(frozen=True)
class Gate:
    id: str
    level: str
    message: str
    src: str


@dataclass(frozen=True)
class Clip:
    """One text box and the worst edge it crosses."""
    name: str
    box: tuple[float, float, float, float]
    edge: str
    px: float

    def line(self, frame: tuple[float, float], display: float) -> str:
        at = self.px * display / max(1.0, frame[0])
        return (f"\"{self.name}\" runs {self.px:.0f} px off the {self.edge} edge "
                f"({at:.1f} px at {display:.0f} wide); box {self.box[0]:.0f},{self.box[1]:.0f} "
                f"{self.box[2]:.0f}x{self.box[3]:.0f} in a {frame[0]:.0f}x{frame[1]:.0f} frame")


def clip_of(box: tuple[float, float, float, float], frame: tuple[float, float], margin: float) -> tuple[str, float] | None:
    """(edge, px) of the worst edge this box crosses, None when it clears every edge by `margin`."""
    x, y, w, h = box
    over = (("left", margin - x), ("top", margin - y),
            ("right", (x + w) - (frame[0] - margin)), ("bottom", (y + h) - (frame[1] - margin)))
    edge, px = max(over, key=lambda e: e[1])
    return (edge, px) if px > 0 else None


def clipped(boxes: list[tuple[str, tuple[float, float, float, float]]], frame: tuple[float, float],
            margin: float = MARGIN_PX) -> list[Clip]:
    """Every (name, box) the frame cuts, worst edge first. The whole rule, in one function."""
    out = [Clip(name, box, *hit) for name, box in boxes if (hit := clip_of(box, frame, margin))]
    return sorted(out, key=lambda c: -c.px)


def gate(boxes: list[tuple[str, tuple[float, float, float, float]]], frame: tuple[float, float],
         margin: float = MARGIN_PX, display: float = DISPLAY_W, where: str = "") -> Gate:
    """G49, from boxes already measured. INFO when there is no text to measure - never a silent skip."""
    tail = f" ({where})" if where else ""
    if not boxes:
        return Gate("G49", "INFO", f"no text box to measure{tail} - the layout carries none", SRC_G49)
    cuts = clipped(boxes, frame, margin)
    if cuts:
        return Gate("G49", "FAIL", f"{len(cuts)} of {len(boxes)} text box(es) clipped by the frame{tail}: "
                    + "; ".join(c.line(frame, display) for c in cuts[:6]) + (" ..." if len(cuts) > 6 else "")
                    + f" - re-line or re-place the text; the dial is {margin:.0f} px inside every edge", SRC_G49)
    return Gate("G49", "PASS", f"{len(boxes)} text box(es) all inside the {frame[0]:.0f}x{frame[1]:.0f} frame "
                f"by {margin:.0f} px{tail}", SRC_G49)


# ---- the two readers ---------------------------------------------------------------------------

def boxes_from_layout(doc: dict) -> tuple[list[tuple[str, tuple[float, float, float, float]]], tuple[float, float]]:
    """A declared layout: {"frame": [W, H], "boxes": [{"role", "text", "box": [x, y, w, h]}]}."""
    fr = doc.get("frame") or doc.get("size")
    if not fr or len(fr) != 2:
        raise SystemExit("the layout needs a \"frame\": [W, H]")
    out = []
    for b in doc.get("boxes") or []:
        box = b.get("box")
        if not box or len(box) != 4:
            continue
        name = ":".join(p for p in (str(b.get("role") or "text"), str(b.get("text") or "")[:40]) if p)
        out.append((name, tuple(float(v) for v in box)))
    return out, (float(fr[0]), float(fr[1]))


def boxes_from_probe(doc: dict, at: float) -> tuple[list[tuple[str, tuple[float, float, float, float]]], tuple[float, float], float]:
    """E67 s4: a page's landing frame is the thumbnail. The instant nearest `at` in layout-probe.json,
    its page runs and its chart labels, against the stage the probe names."""
    instants = doc.get("instants") or []
    if not instants:
        raise SystemExit("layout-probe.json carries no instants - run probe.py <build> --gate")
    inst = min(instants, key=lambda i: abs(float(i.get("t", 0.0)) - at))
    out = []
    for k in PROBE_PAGE_RUNS:
        if (b := (inst.get("page") or {}).get(k)):
            out.append((f"page.{k}", tuple(float(v) for v in b)))
    for la in inst.get("labels") or []:
        if (b := la.get("box")):
            out.append((f"{la.get('role', 'label')}:{(la.get('text') or '')[:40]}", tuple(float(v) for v in b)))
    frame = STAGE.get(str(doc.get("aspect") or "16:9"), STAGE["16:9"])
    return out, (float(frame[0]), float(frame[1])), float(inst.get("t", 0.0))


def main() -> int:
    ap = argparse.ArgumentParser(description="G49 - the thumbnail's text is not clipped")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--layout", type=Path, help="a declared thumbnail layout json (frame + boxes)")
    src.add_argument("--probe", type=Path, help="a build's layout-probe.json (E67 s4: the page's landing frame)")
    ap.add_argument("--at", type=float, default=0.0, help="with --probe: the instant the thumbnail is taken at")
    ap.add_argument("--margin", type=float, default=MARGIN_PX, help=f"px inside every edge (default {MARGIN_PX:.0f})")
    ap.add_argument("--display", type=float, default=DISPLAY_W, help=f"display width px (default {DISPLAY_W})")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.layout:
        boxes, frame = boxes_from_layout(json.loads(args.layout.read_text(encoding="utf-8")))
        where = args.layout.name
    else:
        boxes, frame, t = boxes_from_probe(json.loads(args.probe.read_text(encoding="utf-8")), args.at)
        where = f"{args.probe.name} at t={t:.2f}"
    g = gate(boxes, frame, args.margin, args.display, where)
    print(f"[{g.level:5}] {g.id} {g.message}\n        {g.src}")
    return 1 if g.level == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
