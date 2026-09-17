"""DERIVE THE APPROVED MIX - the signature mix of the approved cuts, MEASURED (P66 T2).

    python content/video_engine/scripts/derive_approved_mix.py            # rewrite effects/skeletons/approved-mix.json
    python content/video_engine/scripts/derive_approved_mix.py --check    # exit 1 if the file on disk is stale
    python content/video_engine/scripts/derive_approved_mix.py --out <path>

`approved-mix.json` is MEASURED, never typed (P66 T2): the numbers M46 will lean on come out of the APPROVED
cuts' own compiled timelines, read with `recipe_walk.events` - the same walk the drift gate and the one-shot floor
use, so nobody re-implements it. Re-running this writes the same bytes; T2's test asserts that.

THE APPROVED CUTS are the two the operator approved, in the build dirs their build scripts default to:

  * `tokyo-tea-break/build-short`      (`build_short.py:39`  BUILD = HERE / env("TOKYO_BUILD_DIR", "build-short"))
  * `japan-tariff-trick/build-short`   (`build_short.py:33`  BUILD = HERE / env("TARIFF_BUILD_DIR", "build-short"))

BESIDE them, never in the target, the reworked one-shot #3 (`memory-trades-the-calendar/build-oneshot-3`,
`build_short.py:37`): E99 s67 sent it back, so it is a source of SKELETONS and not of the target mix.

A build dir holds TWO timelines: `timeline.json` is the take's words and sentences, and the compiled
`scene_evidence_timeline.v1` is `<stem>.timeline.json` (tokyo-short / japan-short / calendar-short). The walk
reads the COMPILED one, found the way `gate_one_shot_floor.timeline_path` finds it.

THE CLASSIFICATION (`method` in the file, verbatim). M46 counts ONE signature per BEAT - the move a viewer would
name - so the walk's events are grouped by scene and the scene takes the first rung it matches:

  1. the page enters by SPIRAL (`page_enter:spiral`)                            -> spiral
  2. the page enters by MOUNT (`page_enter:mount`)                              -> mount
  3. the page enters ON ITS AXES (`page_enter:axes`)                            -> axes
  4. the page arrives FROM A CARD (`page_enter:{snap,camera,built,throw}`)      -> card
  5. no page, but a dock arrives over the world (`cls == "dock_enter"`)         -> card
  6. no page and no dock: the transition that BROUGHT this world - the previous
     scene's own exit (`exit:suck` -> suck, `exit:dip` -> dip, anything else,
     including the schema's `wipe_left` default -> cut)                         -> suck | dip | cut
  7. nothing brought it (the first frame)                                       -> hold

Stdlib + `recipe_walk`; no episode facts beyond the three build dirs named above.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import recipe_walk as RW  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
PROJECTS = "content/video_engine/projects/systems-and-blowups"
OUT_REL = "content/video_engine/effects/skeletons/approved-mix.json"

APPROVED = [f"{PROJECTS}/tokyo-tea-break/build-short", f"{PROJECTS}/japan-tariff-trick/build-short"]
BESIDE = [f"{PROJECTS}/memory-trades-the-calendar/build-oneshot-3"]
BESIDE_NOTE = "reworked to E99 s67, on the queue"

SIGNATURES = ["axes", "mount", "spiral", "suck", "cut", "dip", "card", "hold"]
PAGE_ENTER_SIGNATURE = {"spiral": "spiral", "mount": "mount", "axes": "axes",
                        "snap": "card", "camera": "card", "built": "card", "throw": "card"}
EXIT_SIGNATURE = {"suck": "suck", "dip": "dip"}          # anything else that brought a world reads as a cut
METHOD = (
    "one signature per SCENE (the beat M46 counts), from recipe_walk.events grouped by scene, first rung wins: "
    "(1) page_enter:spiral -> spiral; (2) page_enter:mount -> mount; (3) page_enter:axes -> axes; "
    "(4) page_enter:{snap,camera,built,throw} (the page arrives from a card the viewer already met) -> card; "
    "(5) no page but a dock arrives over the world (cls dock_enter) -> card; "
    "(6) no page and no dock: the transition that brought this world - the PREVIOUS scene's exit "
    "(exit:suck -> suck, exit:dip -> dip, every other token including the schema default wipe_left -> cut); "
    "(7) nothing brought it (the first frame) -> hold."
)


def timeline_path(build: Path) -> Path:
    """The COMPILED `*.timeline.json` of a build dir (gate_one_shot_floor.timeline_path's rule), never the words."""
    named = sorted(p for p in build.glob("*.timeline.json") if p.name != "timeline.json")
    if not named:
        raise SystemExit(f"no compiled *.timeline.json in {build}")
    return named[0]


def scene_signatures(timeline: dict) -> list[str]:
    """The signature of every scene, in order - the ladder in this module's docstring."""
    events = RW.events(timeline)
    by_scene: dict[int, list] = {}
    for ev in events:
        by_scene.setdefault(ev.i, []).append(ev)
    scenes = timeline.get("scenes") or []
    out: list[str] = []
    for i, _scene in enumerate(scenes):
        sig = None
        for ev in by_scene.get(i, []):
            if ev.cls == "page_enter" and ev.card:
                sig = PAGE_ENTER_SIGNATURE.get(ev.card.split(":", 1)[1])
                if sig:
                    break
        if sig is None and any(ev.cls == "dock_enter" for ev in by_scene.get(i, [])):
            sig = "card"
        if sig is None:
            if i == 0:
                sig = "hold"
            else:
                token = str((scenes[i - 1] or {}).get("exit") or RW.DEFAULT_EXIT)
                sig = EXIT_SIGNATURE.get(token.split(":")[0], "cut")
        out.append(sig)
    return out


def measure(build_rel: str) -> dict:
    """One cut's measured mix: the compiled timeline it was read from, the per-scene signatures, counts, shares."""
    build = REPO / build_rel
    path = timeline_path(build)
    timeline = json.loads(path.read_text(encoding="utf-8"))
    sigs = scene_signatures(timeline)
    counts = {s: sigs.count(s) for s in SIGNATURES if sigs.count(s)}
    total = len(sigs)
    return {
        "build": build_rel,
        "timeline": path.relative_to(REPO).as_posix(),
        "scenes": total,
        "per_scene": sigs,
        "counts": counts,
        "shares": {s: round(n / total, 4) for s, n in counts.items()},
        "consecutive_repeats": [[i, sigs[i]] for i in range(1, total) if sigs[i] == sigs[i - 1]],
    }


def build_record() -> dict:
    """The whole file: the two approved cuts, their target mix, the maximum share, and #3 beside them."""
    approved = [measure(rel) for rel in APPROVED]
    beside = [dict(measure(rel), approved=False, note=BESIDE_NOTE) for rel in BESIDE]
    scenes = sum(cut["scenes"] for cut in approved)
    counts = {s: sum(cut["counts"].get(s, 0) for cut in approved) for s in SIGNATURES}
    counts = {s: n for s, n in counts.items() if n}
    peaks = sorted(((cut["shares"][s], s, cut["build"], cut["counts"][s], cut["scenes"])
                    for cut in approved for s in cut["shares"]), key=lambda item: (-item[0], item[1], item[2]))
    top = peaks[0][0]
    return {
        "schema_version": "approved_mix.v1",
        "generated_by": "content/video_engine/scripts/derive_approved_mix.py",
        "measured_with": "content/video_engine/scripts/recipe_walk.py events()",
        "measured": "the APPROVED cuts' own compiled timelines; never typed (P66 T2)",
        "signatures": SIGNATURES,
        "method": METHOD,
        "approved": approved,
        "target": {
            "scenes": scenes,
            "counts": counts,
            "shares": {s: round(n / scenes, 4) for s, n in counts.items()},
        },
        "max_share": {
            "value": top,
            "at": [{"signature": s, "cut": build, "count": n, "of": of}
                   for share, s, build, n, of in peaks if share == top],
            "note": "the maximum share ONE signature reaches inside a single approved cut - the number M46 leans on",
        },
        "beside": beside,
    }


def render(record: dict) -> str:
    return json.dumps(record, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(REPO / OUT_REL))
    ap.add_argument("--check", action="store_true", help="exit 1 if the file on disk is not what this derives")
    args = ap.parse_args(argv)
    text = render(build_record())
    out = Path(args.out)
    if args.check:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current != text:
            print(f"STALE {out}: re-run derive_approved_mix.py")
            return 1
        print(f"ok {out}")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
