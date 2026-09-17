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

THE VOCABULARY (E99 s70 Apply 2 and 5, 2026-09-17). The first eight words - axes, mount, spiral, suck, cut, dip,
card, hold - were written from memory, so the door, the snap, the throw-then-zoom / throw-then-push pair, park and
the un-park, the recast, the rescale and the compare melt had no name here and M46 could not count them. The list
below is `configs/shape_skeleton.schema.json` `$defs.signature`, where every word carries the CAPABILITIES row and
the shot-table line it was read off.

THE CLASSIFICATION (`method` in the file, verbatim). M46 counts ONE ARRIVAL per scene - how this world got here,
the move a viewer would name - so the walk's events are grouped by scene and the scene takes the first rung it
matches:

  1. the page enters by SPIRAL (`page_enter:spiral`)                            -> spiral
  2. the page enters by MOUNT (`page_enter:mount`)                              -> mount
  3. the page enters ON ITS AXES (`page_enter:axes`)                            -> axes
  4. the page enters by MORPH - the object became the chart                     -> object-becomes-chart
  5. the page GROWS OUT OF a card (`page_enter:snap`): the card was THROWN in
     the scene before it -> throw-then-zoom, else -> snap
  6. the CAMERA pushes to the card (`page_enter:camera`): thrown before it
     -> throw-then-push, else -> snap; `page_enter:{built,throw}`  -> card
  7. THIS scene's own `exit` is the transition that BROUGHT it (the compiled
     schema puts the transition on the INCOMING scene - `door_boundary_error(prev, sc)`
     reads `sc["exit"]` and `prev` is the world that leaves): `door` -> door
  8. no page: a dock arrives over the world (`cls == "dock_enter"`)             -> card
  9. this scene's own exit: `suck` -> suck, `dip` -> dip, every other token
     including the schema's `wipe_left` default                                 -> cut
 10. nothing brought it (the first frame, exit `cut`)                           -> hold

AND THE TRANSFORM VOCABULARY, counted BESIDE the arrivals (never instead of them): every `chart_to` the scenes
carry - rescale, recast, park, the un-park (a park to scale 1.0), morph, remake and the compare MELT - read from
the scenes' own species. `vocabulary` in the file is the DISTINCT words a cut plays, arrivals and transforms
together; it is the number M46's own vocabulary line leans on, and it is why the mix is not just seven arrivals.

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

SCHEMA_REL = "content/video_engine/configs/shape_skeleton.schema.json"

# The ARRIVALS: how a world got onto the stage. One per scene.
ARRIVALS = ["axes", "mount", "spiral", "snap", "throw-then-zoom", "throw-then-push", "door",
            "object-becomes-chart", "suck", "dip", "cut", "card", "hold"]
# The TRANSFORMS: what the page DID while it stood there. Counted beside the arrivals.
TRANSFORMS = ["rescale", "recast", "park", "unpark", "morph", "remake", "melt"]
SIGNATURES = ARRIVALS + TRANSFORMS
PAGE_ENTER_SIGNATURE = {"spiral": "spiral", "mount": "mount", "axes": "axes",
                        "morph": "object-becomes-chart", "built": "card", "throw": "card"}
THROWN_ENTER = {"snap": ("throw-then-zoom", "snap"), "camera": ("throw-then-push", "snap")}
EXIT_SIGNATURE = {"suck": "suck", "dip": "dip", "door": "door"}   # anything else that brought a world reads as a cut
CHART_TO_SIGNATURE = {"rescale": "rescale", "recast": "recast", "morph": "morph",
                      "remake": "remake", "compare": "melt"}
UNPARK_SCALE = 1.0
METHOD = (
    "one ARRIVAL per SCENE (how this world got here), from recipe_walk.events grouped by scene, first rung wins: "
    "(1) page_enter:spiral -> spiral; (2) page_enter:mount -> mount; (3) page_enter:axes -> axes; "
    "(4) page_enter:morph (the object became the chart) -> object-becomes-chart; "
    "(5) page_enter:snap -> throw-then-zoom when a card was THROWN in the scene before it, else snap; "
    "(6) page_enter:camera -> throw-then-push when a card was thrown before it, else snap; "
    "page_enter:{built,throw} -> card; "
    "(7) THIS scene's own exit token is the transition that brought it (the compiled schema carries the "
    "transition on the INCOMING scene): exit:door -> door; "
    "(8) no page but a dock arrives over the world (cls dock_enter) -> card; "
    "(9) this scene's own exit: suck -> suck, dip -> dip, every other token including the schema default "
    "wipe_left -> cut; (10) nothing brought it (the first frame) -> hold. "
    "BESIDE the arrivals, the TRANSFORM words are read from the scenes' own chart_to species: rescale, recast, "
    "morph, remake, compare -> melt, park, and a park at scale 1.0 -> unpark (CAPABILITIES.md:120, the UN-PARK). "
    "`vocabulary` is the DISTINCT words a cut plays, arrivals and transforms together (E99 s70 Apply 5)."
)


def timeline_path(build: Path) -> Path:
    """The COMPILED `*.timeline.json` of a build dir (gate_one_shot_floor.timeline_path's rule), never the words."""
    named = sorted(p for p in build.glob("*.timeline.json") if p.name != "timeline.json")
    if not named:
        raise SystemExit(f"no compiled *.timeline.json in {build}")
    return named[0]


def _thrown_in(events: list) -> bool:
    """Did a card ARRIVE over the world in this scene? (The throw half of the throw-then-zoom pair.)"""
    return any(ev.cls == "dock_enter" for ev in events)


def scene_signatures(timeline: dict) -> list[str]:
    """The ARRIVAL of every scene, in order - the ladder in this module's docstring."""
    events = RW.events(timeline)
    by_scene: dict[int, list] = {}
    for ev in events:
        by_scene.setdefault(ev.i, []).append(ev)
    scenes = timeline.get("scenes") or []
    out: list[str] = []
    for i, scene in enumerate(scenes):
        sig = None
        for ev in by_scene.get(i, []):
            if ev.cls != "page_enter" or not ev.card:
                continue
            enter = ev.card.split(":", 1)[1]
            if enter in THROWN_ENTER:
                pair, alone = THROWN_ENTER[enter]
                sig = pair if (i and _thrown_in(by_scene.get(i - 1, []))) else alone
            else:
                sig = PAGE_ENTER_SIGNATURE.get(enter)
            if sig:
                break
        token = str((scene or {}).get("exit") or RW.DEFAULT_EXIT).split(":")[0]
        if sig is None and token == "door":
            sig = "door"
        if sig is None and any(ev.cls == "dock_enter" for ev in by_scene.get(i, [])):
            sig = "card"
        if sig is None:
            sig = "hold" if i == 0 and token == "cut" else EXIT_SIGNATURE.get(token, "cut")
        out.append(sig)
    return out


def scene_transforms(timeline: dict) -> list[list[str]]:
    """The TRANSFORM words every scene plays, in scene order - what the page DID while it stood.

    Read off the scenes' own `chart_to` species rather than off `recipe_walk`'s cards, because the
    un-park is a park at `scale: 1.0` (CAPABILITIES.md:120) and only the species carries the scale.
    """
    out: list[list[str]] = []
    for scene in timeline.get("scenes") or []:
        words: list[str] = []
        for sp in scene.get("species") or []:
            if str(sp.get("kind")) != "chart_to":
                continue
            to = str(sp.get("to") or "")
            word = ("unpark" if float(sp.get("scale", 0.72) or 0.72) == UNPARK_SCALE else "park") \
                if to == "park" else CHART_TO_SIGNATURE.get(to)
            if word and word not in words:
                words.append(word)
        out.append(words)
    return out


def measure(build_rel: str) -> dict:
    """One cut's measured mix: the compiled timeline it was read from, the per-scene signatures, counts, shares."""
    build = REPO / build_rel
    path = timeline_path(build)
    timeline = json.loads(path.read_text(encoding="utf-8"))
    sigs = scene_signatures(timeline)
    moves = scene_transforms(timeline)
    counts = {s: sigs.count(s) for s in SIGNATURES if sigs.count(s)}
    flat = [w for scene in moves for w in scene]
    transforms = {s: flat.count(s) for s in TRANSFORMS if flat.count(s)}
    total = len(sigs)
    vocabulary = sorted(set(sigs) | set(flat), key=SIGNATURES.index)
    return {
        "build": build_rel,
        "timeline": path.relative_to(REPO).as_posix(),
        "scenes": total,
        "per_scene": sigs,
        "per_scene_transforms": moves,
        "counts": counts,
        "transforms": transforms,
        "vocabulary": vocabulary,
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
    vocabularies = [set(cut["vocabulary"]) for cut in approved]
    return {
        "schema_version": "approved_mix.v1",
        "generated_by": "content/video_engine/scripts/derive_approved_mix.py",
        "vocabulary_source": SCHEMA_REL + " $defs.signature (E99 s70 Apply 2: every word cites its CAPABILITIES "
                                          "row and the shot-table line it was read off)",
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
        "vocabulary": {
            "arrivals": ARRIVALS,
            "transforms": TRANSFORMS,
            "per_cut": {cut["build"]: cut["vocabulary"] for cut in approved},
            "union": sorted(set().union(*vocabularies) if vocabularies else [], key=SIGNATURES.index),
            "min_distinct": min((len(v) for v in vocabularies), default=0),
            "note": "min_distinct is the NARROWEST vocabulary an approved cut plays - the floor M46's vocabulary "
                    "line leans on (E99 s70 Apply 5). Measured, never typed.",
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
