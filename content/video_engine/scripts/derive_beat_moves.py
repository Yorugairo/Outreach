"""The MOVES a beat plan leaves unsaid, READ BACK from a cut that is already on disk (P66 T3b).

    python content/video_engine/scripts/derive_beat_moves.py <build> [--check]

The shape compiler (`authoring/shapes.py`) realises each beat's NAMED moves on its group's row. A
beat plan read back from an approved cut (P66 T7) describes what the cut did in prose, but names no
moves - so the base it compiles to carries the skeleton's choreography and nothing else. This tool
writes the `moves` field into such a plan from THE SPECIES AND DOCKS THAT CUT ACTUALLY CARRIES:

  * a species whose `at` falls inside its own scene's span is attributed to the BEAT that is
    speaking at that instant, and becomes a move anchored on the WORD spoken there (the take's own
    words, `<build>/timeline.json`) with its `target`, its `dur` and its own remaining fields copied;
  * a species the cut fires BEFORE its own scene's span is that scene's ARRIVAL STATE - a returning
    page whose title is already rewritten when it comes back ("a species before its scene is a state",
    the approved cut's own comment on the carried retitle) - so it is read at the SCENE'S START, on
    the first word spoken over it, and named as carried. It was skipped until 2026-09-17, which is why
    the base still read the page's first title where the approved cut reads the retitle;
  * a dock whose `enter` falls inside its scene is a `dock` move naming the same asset id, with the
    options the compiler admits (`build_scene_timeline_f.DOCK_OPTS`) copied and nothing else;
  * a record the cut left empty keeps NO `moves` key - a silent beat is the author's to fill, and
    `shapes.compile` names it in `why`.

It is TRANSCRIPTION, never invention. Nothing is added to a beat the cut left bare, no instant is
invented for a species the cut fired outside its own scene's span (they are listed and skipped), and
no field is translated into a field the cut did not carry. `--check` re-derives and exits 1 on any
drift, so the plan and the cut cannot quietly disagree.

The tool names no episode: the build directory, its plan, its take and its compiled timeline are
arguments and are read off disk.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from authoring import shapes as SH  # noqa: E402

PLAN_NAME = "BEAT-PLAN.jsonl"
WORDS_NAME = "timeline.json"
MOVES_KEY = "moves"
EPS = SH.EPS
MAX_PHRASE = 6          # how many words a move's anchor may grow to before it is given up as ambiguous
SPECIES_OWN = ("kind", "at", "dur", "target")   # what the move schema carries by name; the rest is `options`
# What the COMPILER wrote onto the timeline and the author therefore does not name back. `held` is
# its record of why a held light's duration is what it is (build_scene_timeline_f: `e["held"] = True`
# after the hold is resolved), `id` is the row id it keys a species by, and a RESCALE's `state` is
# "derived from the domain, not named" - its own validator refuses a row that names it.
DERIVED_FIELDS = ("held", "id")
DERIVED_BY_KIND = {("chart_to", "rescale"): ("state",)}
# ... and on a compiled DOCK: its `place` is the PIXEL BOX the placer chose ({x, y, w, h} - build_scene_timeline_f
# writes `{"place": place, "read_s": ..., "park_s": ...}` onto the entry), derived from the options. Since P69 T26d
# (5c6871c) `place` is ALSO an authored option - a PROP's {x, y, w} in stage fractions - so the name alone no longer
# tells the two apart, and the box copied back is a plan the compiler refuses ("place is a PROP's option").
DERIVED_DOCK_FIELDS = ("place",)
DOCK_SLIDE = "slide"    # the compiled dock's asset id field
DOCK_ENTER = "enter"


def compiled_timeline(build: Path) -> Path:
    """The build's own compiled timeline - the `*.timeline.json` that is not the word timeline."""
    found = sorted(p for p in build.glob("*.timeline.json") if p.name != WORDS_NAME)
    if len(found) != 1:
        raise SystemExit(f"FAIL: {build}: expected ONE compiled *.timeline.json, found "
                         f"{[p.name for p in found] or 'none'} - name it with --timeline")
    return found[0]


def take_words(build: Path) -> list:
    """The take's words on the cut's own clock (`<build>/timeline.json`), in the kit's shape."""
    tl = json.loads((build / WORDS_NAME).read_text(encoding="utf-8"))
    return [{"w": w["w"], "start_s": float(w["start"]), "end_s": float(w["end"])} for w in tl["words"]]


def scene_beats(scene: dict, plan: list) -> list:
    """The plan records whose sentence sits INSIDE this scene - a sentence belongs to the world it is
    mostly spoken over, so its midpoint decides and no beat is claimed by two scenes."""
    t0, t1 = (float(x) for x in scene["span"])
    return [r for r in plan if t0 - EPS <= (float(r["t0"]) + float(r["t1"])) / 2 < t1 + EPS]


def beat_at(beats: list, t: float):
    """The beat SPEAKING at `t`; an instant in the pause after a sentence belongs to that sentence."""
    inside = next((b for b in beats if float(b["t0"]) - EPS <= t < float(b["t1"])), None)
    if inside is not None:
        return inside
    before = [b for b in beats if float(b["t0"]) <= t]
    return before[-1] if before else (beats[0] if beats else None)


def anchor(ws: list, beat: dict, t: float):
    """The PHRASE of this beat's own sentence that opens at `t` - the shortest run of words from the
    word being spoken there that `shapes.word_at` resolves back to the same instant inside the
    beat's window. None when no run under MAX_PHRASE words is unambiguous (the move is skipped)."""
    b0, b1 = float(beat["t0"]), float(beat["t1"])
    mine = [w for w in ws if b0 - EPS <= float(w["start_s"]) < b1]   # half-open, as `shapes.word_at` reads it
    if not mine:
        return None
    here = next((i for i, w in enumerate(mine) if float(w["start_s"]) - EPS <= t < float(w["end_s"])), None)
    if here is None:
        before = [i for i, w in enumerate(mine) if float(w["start_s"]) <= t + EPS]
        here = before[-1] if before else 0
    for n in range(1, MAX_PHRASE + 1):
        phrase = " ".join(w["w"] for w in mine[here:here + n])
        if SH.word_at(ws, phrase, b0, b1) == round(float(mine[here]["start_s"]), 2):
            return phrase
    return None


def species_move(sp: dict, phrase: str) -> dict:
    """One compiled species as a move: its kind, its word, and what it carries - copied, never
    translated. The field a kind writes its words in becomes `label` (`shapes.LABEL_FIELD`)."""
    kind = sp["kind"]
    label_field = SH.LABEL_FIELD.get(kind)
    move = {"kind": kind, "at_word": phrase}
    if sp.get("target") is not None:
        move["target"] = sp["target"]
    if label_field and sp.get(label_field) is not None:
        move["label"] = sp[label_field]
    if sp.get("dur") is not None:
        move["dur"] = sp["dur"]
    derived = DERIVED_FIELDS + DERIVED_BY_KIND.get((kind, sp.get("to")), ())
    options = {k: v for k, v in sp.items()
               if k not in SPECIES_OWN and k != label_field and k not in derived}
    if options:
        move["options"] = options
    return move


def dock_option_fields() -> tuple:
    """The options a derived `dock` move may carry: the compiler's own (`SH.dock_option_keys`), less the
    lane (carried as `slot`) and less what the compiler DERIVES onto the compiled dock (`DERIVED_DOCK_FIELDS`)."""
    return tuple(k for k in SH.dock_option_keys() if k != SH.MOVE_SLOT and k not in DERIVED_DOCK_FIELDS)


def dock_move(dock: dict, phrase: str, allowed: tuple) -> dict:
    """One compiled dock as a `dock` move: the same asset, the same lane, and only the options the
    compiler itself admits (the compiled `place` is DERIVED from them and is never copied back)."""
    options = {k: dock[k] for k in allowed if k in dock}
    if dock.get("slot") is not None:
        options[SH.MOVE_SLOT] = dock["slot"]
    move = {"kind": SH.MOVE_DOCK, "at_word": phrase, "asset": dock[DOCK_SLIDE]}
    if options:
        move["options"] = options
    return move


def derive(build: Path, timeline=None) -> tuple:
    """`{beat number: [moves]}` read off the cut, and the list of everything SKIPPED, with its reason."""
    plan = SH.load_plan(build / PLAN_NAME)
    ws = take_words(build)
    tl = json.loads((timeline or compiled_timeline(build)).read_text(encoding="utf-8"))
    allowed = dock_option_fields()
    out = {}
    skipped = []
    carried = []

    def place(t: float, what: str, beats: list, make) -> None:
        beat = beat_at(beats, t)
        if beat is None:
            skipped.append(f"skipped: {what} at {t:.2f}s: no sentence is spoken over that scene")
            return
        phrase = anchor(ws, beat, t)
        if phrase is None:
            skipped.append(f"skipped: {what} at {t:.2f}s: no unambiguous phrase of beat {beat['beat']}'s "
                           "sentence opens there")
            return
        out.setdefault(int(beat["beat"]), []).append(make(phrase))

    for scene in tl.get("scenes") or []:
        s0, s1 = (float(x) for x in scene["span"])
        beats = scene_beats(scene, plan)
        for sp in scene.get("species") or []:
            t = round(float(sp["at"]), 2)
            what = f"the {sp['kind']} of {scene['scene_id']}"
            if t < s0 - EPS:
                # the CARRIED species: the cut fires it before the scene so the world ARRIVES with it
                # already done. The beat that speaks at that instant belongs to the world BEFORE this
                # one (a plate has no title to rewrite), so it is read at this scene's own start.
                carried.append(f"carried: {what} at {t:.2f}s: fired before its own scene ({s0:.2f}-{s1:.2f}s) - the scene "
                               f"ARRIVES with it, so the plan reads it at {s0:.2f}s, on that scene's first word")
                place(s0, what, beats, lambda phrase, sp=sp: species_move(sp, phrase))
                continue
            if t > s1 + EPS:
                skipped.append(f"skipped: {what} at {t:.2f}s: past its own scene's span ({s0:.2f}-{s1:.2f}s)")
                continue
            place(t, what, beats, lambda phrase, sp=sp: species_move(sp, phrase))
        for dock in scene.get("docks") or []:
            t = round(float(dock[DOCK_ENTER]), 2)
            what = f"the card {dock.get(DOCK_SLIDE)} of {scene['scene_id']}"
            if not (s0 - EPS <= t < s1 + EPS):
                skipped.append(f"skipped: {what} at {t:.2f}s: enters outside its own scene's span "
                               f"({s0:.2f}-{s1:.2f}s)")
                continue
            place(t, what, beats, lambda phrase, dock=dock: dock_move(dock, phrase, allowed))
    return {n: moves for n, moves in sorted(out.items())}, carried + skipped


def render(build: Path, moves: dict) -> tuple:
    """The plan file as it stands, and as it reads with the derived moves - bytes, so `--check`
    compares what is on disk. The record's own keys keep their order and their values; `moves` is
    appended, and a `moves` already there is replaced, so a second run changes nothing."""
    raw = (build / PLAN_NAME).read_bytes()
    term = b"\r\n" if b"\r\n" in raw else b"\n"
    done = []
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        rest = {k: v for k, v in record.items() if k != MOVES_KEY}
        mine = moves.get(int(record["beat"]))
        done.append(json.dumps({**rest, MOVES_KEY: mine} if mine else rest))
    return raw, term.join(x.encode("utf-8") for x in done) + term


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("build", type=Path, help="the build directory (its BEAT-PLAN.jsonl is rewritten)")
    ap.add_argument("--timeline", type=Path, default=None,
                    help="the compiled timeline, when the build holds more than one")
    ap.add_argument("--check", action="store_true", help="re-derive and exit 1 on any drift - write nothing")
    args = ap.parse_args(argv)
    build = args.build.resolve()
    if not (build / PLAN_NAME).is_file():
        raise SystemExit(f"FAIL: no {PLAN_NAME} in {build} - the plan is AUTHORED (E99 s66); this tool only fills "
                         "its `moves` from a cut that already exists")
    moves, skipped = derive(build, args.timeline)
    was, now = render(build, moves)
    kinds = {}
    for beat_moves in moves.values():
        for m in beat_moves:
            kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    total = sum(len(v) for v in moves.values())
    print(f"{build.parent.name}/{build.name}: {total} moves on {len(moves)} beats "
          f"({', '.join(f'{k} {n}' for k, n in sorted(kinds.items()))})")
    for line in skipped:
        print(f"  {line}")
    if args.check:
        if was == now:
            print(f"  {PLAN_NAME} is in sync with the cut")
            return 0
        print(f"FAIL: {build / PLAN_NAME} has drifted from the cut - re-run without --check to rewrite it")
        return 1
    (build / PLAN_NAME).write_bytes(now)
    print(f"  wrote {build / PLAN_NAME} ({len(now)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
