"""P71 T36 - the line recipes (was P69 T71), each PROVED AS A BEAT (E99 s60, s70).

    python content/video_engine/projects/_proofs/p71-recipes/proof_t36.py                        # build + strip both
    python content/video_engine/projects/_proofs/p71-recipes/proof_t36.py --beat trace-to-the-level   # one beat, no strip
    python content/video_engine/projects/_proofs/p71-recipes/proof_t36.py --strip-only              # re-shoot the strips

The door is P69 T35's (`_proofs/p69-recipes/proof_p69_recipes.py`, IMPORTED, never edited): one real beat per recipe -
its own sentence off the Steel and Paper H scratch take, the words as the clock, the captions paged by the kit - through
the AUTHORING KIT's compile door under a NAMED no-receipt reason. It writes only inside `build-lab-<recipe>/` beside this
file (gitignored) and the strip dir; the Steel and Paper project is read and asserted unmoved.

THE TWO BEATS:
  trace-to-the-level     row 16's "Last year: a hundred and twenty-one billion." on `ev-debt-issuance-line-v1`: the
                         issuance line runs on from the 2020-24 average to 2025 on "Last", the year becomes a pill on
                         the x axis with its guide on "year" (T9), and on "a hundred and twenty-one" the level runs from
                         the tip to the value axis - a ring on the tip, the dashed rule, "$121B" written off the rule
                         (T10's axis form, C14). The plan's row-15 beat is not taken: its 5.5 is a RULE already on that
                         page (R21's own don't, BRAVOS-USE-WHEN.md "the level is a value already on the chart"), and row
                         14's 28 is the tech line's end tag (a level_join would write it twice). This page's end tag is
                         the word "issuance", so the level is written once.
  the-divergence-spread  row 10's "Chipmakers doubling while their customers sit flat at the index is textbook
                         profit-taking" on `ev-divergence-v1` as its OWN page (H draws it as a recast state, where a
                         spread paints nothing - build_episode_h.py's "NO SPREAD ON THIS STATE"): memory held at
                         nothing, the chips drawn on "Chipmakers doubling", the giants and the index on "their customers
                         sit flat", each landing with its end tag, and the gap between the chips and the giants bleeds
                         on "textbook profit-taking" (D40 04:30-04:50: two lines, their end pills, the gap filled).

`todays-boom-against-past-booms` (R32) is NOT built: no committed rebased-cycle evidence object is on disk (the plan's
stop condition - R32 ships only on committed series, never re-typed).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))
sys.path.insert(0, str(HERE.parent / "p69-recipes"))
sys.path.insert(0, str(REPO / "content/video_engine/tests"))

import proof_p69_recipes as P69                             # noqa: E402  (imported, never edited - the P71 rule)
from authoring import Project                               # noqa: E402
from authoring import table as T, words as W                # noqa: E402

TAG = "P71 T36"
PLAIN_LINE = "ledger:%s:line::right:axes:cut;idle=live"     # the P69 door's page form (full stage, plain profile)


# ---------------------------------------------------------------- R21: the trace to its level

DEBT_PAGE = P69.DEBT_PAGE
DEBT = P69.DEBT
DEBT_ACTUAL, DEBT_HIGH, DEBT_LOW = P69.DEBT_ACTUAL, P69.DEBT_HIGH, P69.DEBT_LOW
DEBT_AVG_END = P69.DEBT_LAST_AVG                            # 2024, where the flat 2020-24 average ends
DEBT_TIP = P69.DEBT_2025                                    # 2025, the actual the sentence names
DEBT_TIP_X, DEBT_TIP_Y = DEBT["series"][DEBT_ACTUAL]["pts"][DEBT_TIP]   # read off the object, never typed
DEBT_TIP_TEXT = "$%gB" % DEBT_TIP_Y                          # "$121B" - the object's own value in its own unit (yunit B)
TRACE_S = 0.6            # the rise to 2025 draws on "Last", landing as "year" is said
TAG_S = 0.5              # the year's pill springs on "year" (axis_tag POP_S 0.25 + its text)
LEVEL_S = 1.4            # the level runs on "a hundred and"; its figure (LABEL 0.7-1.0 of dur) writes on "twenty-one"


def _trace_times(ws: list) -> tuple[float, float, float]:
    return T.at(ws, "Last year"), W.word_in(ws, "Last year", "year"), T.at(ws, "a hundred and twenty-one")


def _trace_row(ws: list, runtime: float) -> tuple:
    t_last, t_year, t_level = _trace_times(ws)
    species = [
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": DEBT_ACTUAL, "target": P69._datum(DEBT_AVG_END, DEBT_ACTUAL)},
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": DEBT_HIGH, "target": P69._datum(0, DEBT_HIGH)},
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": DEBT_LOW, "target": P69._datum(0, DEBT_LOW)},
        {"kind": "build_to", "at": t_last, "dur": TRACE_S, "series": DEBT_ACTUAL, "target": P69._datum(DEBT_TIP, DEBT_ACTUAL)},
        {"kind": "axis_tag", "at": t_year, "dur": TAG_S, "x": DEBT_TIP_X, "series": DEBT_ACTUAL},
        {"kind": "level_join", "at": t_level, "dur": LEVEL_S, "from": DEBT_TIP, "to": {"y": DEBT_TIP_Y},
         "series": DEBT_ACTUAL, "label": DEBT_TIP_TEXT},
    ]
    return (0.0, runtime, PLAIN_LINE % DEBT_PAGE, (0, 0, 0), [], None, species)


def _trace_strip(ws: list) -> list:
    t_last, t_year, t_level = _trace_times(ws)
    return [(round(t_last + TRACE_S + 0.05, 2), "the trace lands on 2025, the tip lit"),
            (round(t_year + TAG_S + 0.3, 2), "the year a pill on the x axis, its guide"),
            (round(t_level + 0.5 * LEVEL_S, 2), "the ring on the tip, the level runs"),
            (round(t_level + LEVEL_S + 0.4, 2), "the level written off the rule")]


# ---------------------------------------------------------------- R27: the divergence spread

DIV_PAGE = "ev-divergence-v1"
DIV = P69._series(DIV_PAGE)
_DIV_NAMES = [s.get("name", "") for s in DIV["series"]]
DIV_MEMORY = next(i for i, n in enumerate(_DIV_NAMES) if n.startswith("MEMORY"))    # read by name, never an index
DIV_SEMIS = next(i for i, n in enumerate(_DIV_NAMES) if n.startswith("SEMICONDUCTOR"))
DIV_MEGA = next(i for i, n in enumerate(_DIV_NAMES) if n.startswith("MEGA"))
DIV_INDEX = next(i for i, n in enumerate(_DIV_NAMES) if n.startswith("S&P"))
DIV_LAST = len(DIV["series"][DIV_SEMIS]["pts"]) - 1
# THE PAGE'S DOMAIN is the hook's (build_episode_h.py HOOK_YMIN / HOOK_YMAX, read the same way off the data): memory is
# held at nothing, so the object's own log domain (sized for memory's 1,074) would flatten the three lines it draws.
_DIV_DRAWN = (DIV_SEMIS, DIV_MEGA, DIV_INDEX)
DIV_YMIN = 80.0
DIV_YMAX = float(round(max(v for i in _DIV_DRAWN for _x, v in DIV["series"][i]["pts"]) * 1.06))
DIV_PLATE = PLAIN_LINE % DIV_PAGE + ";domain=%g,%g" % (DIV_YMIN, DIV_YMAX)
CHIPS_S = 1.2            # the chips draw on "Chipmakers doubling" (row 10's 1.2 s line)
FLAT_S = 1.2             # the giants and the index on "their customers sit flat"
SPREAD_S = 2.0           # H row 20's DIV_SPREAD_S: the gap bleeds over "textbook profit-taking"


def _spread_times(ws: list) -> tuple[float, float, float]:
    return T.at(ws, "Chipmakers doubling"), T.at(ws, "their customers"), T.at(ws, "textbook")


def _spread_row(ws: list, runtime: float) -> tuple:
    t_chips, t_flat, t_gap = _spread_times(ws)
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": i, "target": P69._datum(0, i)}
               for i in (DIV_MEMORY, DIV_SEMIS, DIV_MEGA, DIV_INDEX)]      # the page lands on its axes, nothing drawn
    species += [
        {"kind": "build_to", "at": t_chips, "dur": CHIPS_S, "series": DIV_SEMIS, "target": P69._datum(DIV_LAST, DIV_SEMIS)},
        {"kind": "build_to", "at": t_flat, "dur": FLAT_S, "series": DIV_MEGA, "target": P69._datum(DIV_LAST, DIV_MEGA)},
        {"kind": "build_to", "at": t_flat, "dur": FLAT_S, "series": DIV_INDEX, "target": P69._datum(DIV_LAST, DIV_INDEX)},
        {"kind": "spread", "at": t_gap, "dur": SPREAD_S, "from": DIV_MEGA, "to": DIV_SEMIS},
    ]
    return (0.0, runtime, DIV_PLATE, (0, 0, 0), [], None, species)


def _spread_strip(ws: list) -> list:
    t_chips, t_flat, t_gap = _spread_times(ws)
    return [(round(t_chips + CHIPS_S + 0.1, 2), "the chips land with their end tag"),
            (round(t_flat + FLAT_S + 0.1, 2), "the giants and the index land flat"),
            (round(t_gap + 0.5 * SPREAD_S, 2), "the gap bleeds (spread)"),
            (round(t_gap + SPREAD_S + 0.6, 2), "held: two lines, their tags, the gap")]


@dataclass(frozen=True)
class Beat:
    slug: str                 # the recipe's slug (recipe:<slug>)
    first: str                # the phrase the beat's first sentence opens on
    last: str                 # a phrase in the beat's last sentence (the beat closes at that sentence's stop)
    row: Callable[[list, float], tuple]
    strip: Callable[[list], list]


BEATS = {b.slug: b for b in (
    Beat("trace-to-the-level", "Between 2020 and 2024", "a hundred and twenty-one", _trace_row, _trace_strip),
    Beat("the-divergence-spread", "Chipmakers doubling", "textbook profit-taking", _spread_row, _spread_strip),
)}


# ---------------------------------------------------------------- the build (P69 T35's door, this slice's dirs)

def build_dir(slug: str) -> Path:
    return HERE / f"build-lab-{slug}"


def build_beat(beat: Beat) -> int:
    """ONE beat through the kit's compile door, into its own private build dir."""
    before = P69._read_only_state()
    build = build_dir(beat.slug)
    project = Project(here=P69.EP, build=build, take=P69.TAKE, take_stem=P69.TAKE_STEM, script_name="SCRIPT-H-VO.txt",
                      episode_id=f"p71-t36-{beat.slug}", take_name="vo-h-scratch")
    project.mkdirs()
    words, t0, runtime = P69.clip_words(W.take_words(project), beat)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t0, "-i", str(P69.TAKE / (P69.TAKE_STEM + ".mp3")),
                    "-t", "%.3f" % runtime, "-c:a", "libmp3lame", "-q:a", "2", str(project.audio_master)], check=True)
    W.write_timeline(project, words, runtime)
    T.caption_pages(build, char_budget=P69.CAPTION_BUDGET, max_words=P69.CAPTION_MAX_WORDS)
    (build / "evidence-dock.json").write_text("[]", encoding="utf-8")
    row = beat.row(words, runtime)
    table = build / "SHOT-TABLE-P71-T36.py"
    T.write_shot_table(table, [row], f'"""{TAG} proof beat - recipe:{beat.slug}. GENERATED by proof_t36.py; never a cut."""\n')
    T.print_rows([row], show_docks=True)
    rc = T.compile_timeline(P69.EP, build, timeline_name=f"{beat.slug}.timeline.json",
                            shot_table_file=os.path.relpath(table, P69.EP), title=f"{TAG} proof - recipe:{beat.slug}",
                            subtitle=f"Steel and Paper H take {t0:.2f}-{t0 + runtime:.2f}s", episode_id=project.episode_id,
                            aspect=P69.ASPECT, caption_style=None, kinetics=P69.KINETICS,
                            no_receipt=f"{TAG} recipe proof: recipe:{beat.slug} (a private test-bed beat, never a cut)")
    moved = [rel for rel, d in P69._read_only_state().items() if d != before[rel]]
    if moved:
        raise SystemExit("FAIL: the proof wrote into a READ-ONLY path: " + ", ".join(moved))
    (build / "beat.json").write_text(json.dumps({"recipe": f"recipe:{beat.slug}", "take_from_s": t0, "runtime_s": runtime,
                                                 "words": " ".join(w["w"] for w in words), "row": row,
                                                 "strip": beat.strip(words)}, indent=1, default=str), encoding="utf-8")
    print(f"  beat        : recipe:{beat.slug} - take {t0:.2f}s + {runtime:.2f}s -> {build}")
    return rc


def render_strip(slug: str, out_dir: Path) -> Path:
    """Four instants of the compiled beat through ONE served player (served_player: the guarded driver)."""
    from PIL import Image, ImageDraw
    import render_baseline as RB
    import served_player as SPL
    build = build_dir(slug)
    beat = json.loads((build / "beat.json").read_text(encoding="utf-8"))
    tl = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    words = [{"w": w["w"], "start_s": w["start"], "end_s": w["end"]} for w in tl["words"]]
    w, h = RB.STAGE[P69.ASPECT]
    shots = []
    with SPL.served(build / "player.html", w, h) as (page, errors):
        for t, what in beat["strip"]:
            png = build / f"strip-{t:05.2f}.png"
            png.write_bytes(RB.frame_png(page, t, (w, h)))
            shots.append((t, what, png))
        if errors:
            raise SystemExit(f"FAIL: the player threw on recipe:{slug}: {errors[:3]}")
    scale, pad, head, foot = 0.34, 12, 40, 44
    fw, fh = int(w * scale), int(h * scale)
    sheet = Image.new("RGB", (pad + len(shots) * (fw + pad), head + fh + foot), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), f"{TAG} - recipe:{slug}  |  take {beat['take_from_s']:.2f}s + {beat['runtime_s']:.2f}s  |  "
                         f"one real beat, its own words, on its own page (E99 s60)", fill=(235, 235, 235))
    for i, (t, what, png) in enumerate(shots):
        x = pad + i * (fw + pad)
        with Image.open(png) as im:
            sheet.paste(im.convert("RGB").resize((fw, fh), Image.LANCZOS), (x, head))
        draw.text((x + 2, head - 14), f"{t:.2f}s  {what}", fill=(245, 200, 90))
        draw.text((x + 2, head + fh + 6), f"\"{P69._spoken_at(words, t)}\"", fill=(200, 200, 200))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{slug}-strip.png"
    sheet.save(out)
    print(f"  strip       : {out}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--beat", choices=sorted(BEATS), help="build ONE beat in this process (no strip)")
    ap.add_argument("--strips", type=Path, default=HERE, help="where the <recipe>-strip.png sheets go")
    ap.add_argument("--strip-only", nargs="*", choices=sorted(BEATS), metavar="RECIPE",
                    help="re-shoot the strips of beats already built (all of them when none is named)")
    args = ap.parse_args()
    if args.beat:
        return build_beat(BEATS[args.beat])
    if args.strip_only is None:
        for slug in BEATS:   # one process per beat: the compiler keeps module state between compiles
            rc = subprocess.run([sys.executable, __file__, "--beat", slug], cwd=str(REPO)).returncode
            if rc:
                print(f"FAIL: recipe:{slug} did not compile (rc {rc})")
                return rc
    for slug in (args.strip_only or list(BEATS)):
        render_strip(slug, args.strips)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
