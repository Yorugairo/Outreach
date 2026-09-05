"""G-i / G-j / G-k - the grounding gates (P37 T7). A figure composited onto a plate has to
stand ON it: eye height on the plate's horizon (G-i), sprites anchored at the feet and moved
by the floor, never by a screen-space tween (G-j), and any beat that declares contact
declares its solver (G-k). Doc 48 s48.1 / s48.7.

The shot table does not yet carry a horizon or a contact declaration, so each check lands
on the M08 ladder: INFO while the timeline declares nothing, FAIL the moment it declares
something and gets it wrong.

    python gate_grounding.py <timeline.json> [--template <player template>]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EYE_TOL = 0.04                 # 48 s48.7 defect 4: eye height within 4% of stage height of the horizon
SOLVERS = {"fk", "ik"}         # 48 s48.1: the FK/IK boundary - a contact beat names which
SPRITE_ORIGIN = "50% 100%"     # 48 s48.7: grounded sprites pivot at the feet
SRC_G_I = "47 s2 G-i / 48 s48.7 defect 4: a figure whose eyes miss the horizon reads as standing in a pit or leaning back"
SRC_G_J = "47 s2 G-j / 48 s48.7: a grounded sprite is anchored 50% 100% and moves at the floor's velocity, never a screen-space tween"
SRC_G_K = "47 s2 G-k / 48 s48.1: a beat that declares contact declares its solver (fk | ik)"


@dataclass(frozen=True)
class Gate:
    id: str
    level: str      # PASS | FAIL | INFO
    message: str
    src: str

    def line(self) -> str:
        return f"[{self.level:<4}] {self.id} {self.message}\n       {self.src}"


def _cutouts(scene: dict):
    for sp in scene.get("species", []):
        if sp.get("kind") == "plate_life":
            for c in sp.get("cutouts", []):
                yield sp, c


def g_i(scenes: list[dict]) -> Gate:
    declared = [(s, c) for s in scenes for _, c in _cutouts(s) if s.get("world", {}).get("horizon") is not None and c.get("eye_y") is not None]
    if not declared:
        return Gate("G-i", "INFO", "no scene declares world.horizon with a cutout eye_y yet - eye-height check not run (no silent skip)", SRC_G_I)
    bad = [f"{s.get('scene_id', '?')} {c.get('asset', '?')} eye {c['eye_y']:.2f} vs horizon {s['world']['horizon']:.2f}"
           for s, c in declared if abs(float(c["eye_y"]) - float(s["world"]["horizon"])) > EYE_TOL]
    return Gate("G-i", "FAIL" if bad else "PASS", (f"{len(bad)} figure(s) miss the horizon by > {EYE_TOL:.2f}: " + "; ".join(bad[:8])) if bad
                else f"{len(declared)} figure(s) stand on their plate's horizon", SRC_G_I)


def g_j(scenes: list[dict], template: str | None) -> Gate:
    problems = []
    if template is not None:
        m = re.search(r"#plife img\s*\{([^}]*)\}", template)
        if not m or f"transform-origin: {SPRITE_ORIGIN}" not in m.group(1):
            problems.append(f"template: #plife img is not anchored transform-origin: {SPRITE_ORIGIN}")
    tweens = [f"{s.get('scene_id', '?')} {c.get('asset', '?')}" for s in scenes for _, c in _cutouts(s) if str(c.get("tween", "")).lower() == "screen"]
    if tweens:
        problems.append("screen-space tween on " + ", ".join(tweens[:8]))
    if template is None and not any(True for s in scenes for _ in _cutouts(s)):
        return Gate("G-j", "INFO", "no plate-life cutouts and no template given - anchor check not run (no silent skip)", SRC_G_J)
    return Gate("G-j", "FAIL" if problems else "PASS", "; ".join(problems) if problems else f"sprites anchored {SPRITE_ORIGIN}, no screen-space tweens", SRC_G_J)


def g_k(scenes: list[dict]) -> Gate:
    contact = [(s, sp) for s in scenes for sp in s.get("species", []) if sp.get("contact")]
    if not contact:
        return Gate("G-k", "INFO", "no beat declares contact yet - solver check not run (no silent skip)", SRC_G_K)
    bad = [f"{s.get('scene_id', '?')} {sp.get('kind', '?')} solver={sp.get('solver')!r}" for s, sp in contact if str(sp.get("solver", "")).lower() not in SOLVERS]
    return Gate("G-k", "FAIL" if bad else "PASS", (f"{len(bad)} contact beat(s) without a solver: " + "; ".join(bad[:8])) if bad
                else f"{len(contact)} contact beat(s) each name fk or ik", SRC_G_K)


def run(tl: dict, template: str | None = None) -> list[Gate]:
    scenes = tl.get("scenes", [])
    return [g_i(scenes), g_j(scenes, template), g_k(scenes)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline"); ap.add_argument("--template")
    args = ap.parse_args()
    tl = json.loads(Path(args.timeline).read_text(encoding="utf-8"))
    template = Path(args.template).read_text(encoding="utf-8") if args.template else None
    gates = run(tl, template)
    for g in gates:
        print(g.line())
    fails = sum(1 for g in gates if g.level == "FAIL")
    print(f"VERDICT: {'FAIL' if fails else 'PASS'} ({fails} FAIL) - {args.timeline}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
