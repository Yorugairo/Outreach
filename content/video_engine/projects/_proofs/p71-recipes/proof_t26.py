"""P71 T26 - the push to now then the unknown (R5), and the evidence then the conditional future (R26), PROVED AS BEATS.

    python content/video_engine/projects/_proofs/p71-recipes/proof_t26.py                                  # build + strip both
    python content/video_engine/projects/_proofs/p71-recipes/proof_t26.py --beat push-to-now-then-the-unknown   # one beat
    python content/video_engine/projects/_proofs/p71-recipes/proof_t26.py --strip-only                        # re-shoot

The door is P69 T35's (`_proofs/p69-recipes/proof_p69_recipes.py`, IMPORTED, never edited) as P71 T36 drives it: one
real beat per recipe - its own sentences off the Steel and Paper H scratch take, the words as the clock, the captions
paged by the kit - through the AUTHORING KIT's compile door under a NAMED no-receipt reason. It writes only inside
`build-lab-<recipe>/` beside this file and `build-lab-strips/` (both gitignored); the Steel and Paper project is read and
asserted unmoved.

THE TWO BEATS (E99 s60 - each a beat a cut could carry, on its own words):
  push-to-now-then-the-unknown          H row 22's "That's the July release ... The flip: if memory breaks while the
                                        buildout holds, the scarcity story is wrong - and so am I." on the COMMITTED
                                        `ev-memory-monitor-row22-v1` (the page lands built: three and a half years of
                                        the monitor). On "Customs printed one soft month" the axes RESCALE onto the last
                                        year, so the view lands on TODAY - the June dip and the July print at the plot's
                                        right edge (E59: the push lands on a named datum, one move, never a continuous
                                        push). On "The flip" a "?" (T18's `unknown`) lands PAST the plot's right edge,
                                        beside today's tip (BOOM 03:19's place): the future this sentence names is a
                                        condition, not a figure, so no path is drawn - a drawn path would be a number the
                                        sources do not give (E77).
  evidence-then-the-conditional-future  H row 16's "Then the bills got bigger than the cash. Between 2020 and 2024 ...
                                        This year they're tracking toward a hundred and fifty." The evidence (the
                                        2020-24 average, then the 2025 actual, each written) holds about eleven seconds
                                        on the page, then the projection arrives in a visibly NEW grammar: T16's dashed,
                                        unbloomed continuation from the last actual, tagged "2026E" with its tier. The
                                        object is P71 T16's golden composition (`build_golden_sources.projection_series`,
                                        imported, never re-typed: the committed `ev-debt-issuance-line-v1` read in place,
                                        its `$150B` edge as the labelled projection) written into this beat's PRIVATE
                                        episode dir (`build-lab-<recipe>/ep/evidence/objects/`), never the project's.
  the-box-then-the-dated-rule           P72 T46g (Bravos A56, BOOM 17:55.5-18:00.5; R26-407's box form): the SAME row 16
                                        words and page. On "a hundred and twenty-one" a dashed BOX goes round the last actual
                                        move (2024 -> 2025, the leap) - the box names the move - and leaves on "This year";
                                        on "tracking toward" the extend re-fits the page and draws the dashed 2026E from the
                                        last actual, and as the dash lands the DATED RULE lands: the axis's own "2026E" tick
                                        (the committed object's, put back on this beat's private copy) springs into T9's
                                        `axis_tag` pill - the rule names the date, as the estimate it is (E77).
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
sys.path.insert(0, str(REPO / "content/video_engine/tests/golden"))

import proof_p69_recipes as P69                             # noqa: E402  (imported, never edited - the P71 rule)
from authoring import Project                               # noqa: E402
from authoring import table as T, words as W                # noqa: E402

TAG = "P71 T26"
LONG_LINE = "ledger:%s:line::right:%s:cut;idle=live;readability=longform"   # both rows take the long form (rule (g))


# ---------------------------------------------------------------- R5: the push to now, then the unknown

MON_PAGE = "ev-memory-monitor-row22-v1"
MON = P69._series(MON_PAGE)
MON_LAST_X = max(p[0] for s in MON["series"] for p in s["pts"])          # the July 2026 print - TODAY, read off the object
MON_WINDOW = [round(MON_LAST_X - 1.0, 4), MON_LAST_X]                   # the last year: June's dip and July's print in view
MON_PLATE = LONG_LINE % (MON_PAGE, "built")                             # the evidence lands whole: 2023-26 on the page
PUSH_S = 1.4             # the rescale's clock (the chart_to card's example; lands inside "one soft month in June")
UNKNOWN_SIZE = 122       # BOOM 08:52.5's chart-side "?" (species:unknown's default, written for the reader)
UNKNOWN_AT = {"kind": "point", "x": 0.935, "y": 0.44}   # past the plot's right edge, under today's tip and its tags (BOOM 03:19;
                                                         # at y 0.34 it sat on the DRAM end tag - frames/crop-push-16.51.png)
UNKNOWN_TAIL_S = 0.3     # the "?" holds through "and so am I." and leaves a breath after it


def _push_times(ws: list) -> tuple[float, float, float]:
    return T.at(ws, "Customs printed"), T.at(ws, "The flip"), W.word_in(ws, "and so am I", "i")   # word_in matches lower case


def _push_row(ws: list, runtime: float) -> tuple:
    t_push, t_flip, t_i = _push_times(ws)
    end = min(runtime, round(t_i + 0.4 + UNKNOWN_TAIL_S, 2))
    species = [
        {"kind": "chart_to", "at": t_push, "dur": PUSH_S, "to": "rescale", "window": list(MON_WINDOW)},
        {"kind": "unknown", "at": t_flip, "dur": round(end - t_flip, 2), "size": UNKNOWN_SIZE, "target": dict(UNKNOWN_AT)},
    ]
    return (0.0, runtime, MON_PLATE, (0, 0, 0), [], None, species)


def _push_strip(ws: list) -> list:
    t_push, t_flip, t_i = _push_times(ws)
    return [(round(t_push - 0.3, 2), "the evidence: the monitor, 2023-26, whole"),
            (round(t_push + PUSH_S + 0.3, 2), "the rescale lands on today (June's dip, July's print)"),
            (round(t_flip + 0.6, 2), "the '?' lands past the edge on 'The flip'"),
            (round(t_i, 2), "held through 'and so am I'")]


# ---------------------------------------------------------------- R26: the evidence, then the conditional future

DEBT_ID = "fx-issuance-2026e"                                          # the beat's PRIVATE object (T16's golden composition)
DEBT_PLATE = LONG_LINE % (DEBT_ID, "axes")
DEBT_AVG_END = P69.DEBT_LAST_AVG                                       # 2024, where the flat 2020-24 average ends
DEBT_TIP = P69.DEBT_2025                                               # 2025, the actual the sentence names
DEBT_AVG_MID = 2                                                       # 2022, the figure's pin over the flat average
AVG_S = 1.2              # the average draws on "Between 2020 and 2024"
TIP_S = 1.0              # the rise to 2025 on "Last year" (the wedge beat's 1.0 s)
FIG_S = 1.5              # a figure's write (the wedge beat's)
PROJ_DY = -1.4           # the 2025 figure sits above the tip (lines), clear of the projection's tag


def _debt_object() -> dict:
    import build_golden_sources as G       # T16's composition, read off the committed object (never re-typed)
    return G.projection_series()


def _debt_texts(obj: dict) -> tuple[str, str]:
    actual = obj["series"][0]["pts"]
    return "$%gB a year" % actual[DEBT_AVG_MID][1], "$%gB" % actual[DEBT_TIP][1]


def _evidence_times(ws: list) -> tuple[float, float, float, float, float, float]:
    return (T.at(ws, "Between 2020 and 2024"), T.at(ws, "twenty-eight billion"), T.at(ws, "Last year"),
            T.at(ws, "a hundred and twenty-one"), T.at(ws, "tracking toward"),
            W.word_in(ws, "toward a hundred and fifty", "fifty"))


def _evidence_row(ws: list, runtime: float) -> tuple:
    t_avg, t_28, t_last, t_121, t_track, t_50 = _evidence_times(ws)
    avg_text, tip_text = _debt_texts(_debt_object())
    species = [
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": P69._datum(0, 0)},   # the page on its axes
        {"kind": "build_to", "at": t_avg, "dur": AVG_S, "series": 0, "target": P69._datum(DEBT_AVG_END, 0)},
        {"kind": "figure", "at": t_28, "dur": FIG_S, "target": P69._datum(DEBT_AVG_MID, 0), "text": avg_text,
         "sub": "2020–24 average"},
        {"kind": "build_to", "at": t_last, "dur": TIP_S, "series": 0, "target": P69._datum(DEBT_TIP, 0)},
        {"kind": "figure", "at": t_121, "dur": FIG_S, "target": P69._datum(DEBT_TIP, 0), "text": tip_text,
         "dy": PROJ_DY},
        # the NEW grammar, on the projection's word: T16's dashed continuation from the last actual, tagged "2026E"
        {"kind": "chart_to", "at": t_track, "dur": round(t_50 + 0.4 - t_track, 2), "to": "extend", "series": 1},
    ]
    return (0.0, runtime, DEBT_PLATE, (0, 0, 0), [], None, species)


def _evidence_strip(ws: list) -> list:
    t_avg, t_28, t_last, t_121, t_track, t_50 = _evidence_times(ws)
    return [(round(t_28 + FIG_S + 0.2, 2), "the evidence: the 2020-24 average, written"),
            (round(t_track - 0.2, 2), "held: the 2025 actual written - the page read"),
            (round(t_track + 0.8 * (t_50 + 0.4 - t_track), 2), "the dashed projection draws from 2025"),   # re-fit, then dash
            (round(t_50 + 1.4, 2), "landed: dashed, unbloomed, '2026E' + tier")]


BOX_FIG_DY = -2.4        # this page's axis carries 2026 from birth, so the estimate climbs more steeply off the tip: at R26's
                         # -1.4 the dash ran through "$121B" (frames/crop-boxbeat-14.90.png) - two more lines up, clear of it
DEBT_2026 = 2026         # the projection's own x - the date the rule names (the object's 2026E, never typed from memory: asserted below)


def _box_row(ws: list, runtime: float) -> tuple:
    """P72 T46g: R26's page and words; the box round the last actual move, then the dated rule with the forward draw."""
    t_avg, t_28, t_last, t_121, t_track, t_50 = _evidence_times(ws)
    t_this = T.at(ws, "This year")
    obj = _debt_object()
    assert obj["series"][1]["pts"][-1][0] == DEBT_2026, obj["series"][1]["pts"]   # the rule's date is the object's own
    _, tip_text = _debt_texts(obj)
    extend_dur = round(t_50 + 0.4 - t_track, 2)
    species = [
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": P69._datum(0, 0)},
        {"kind": "build_to", "at": t_avg, "dur": AVG_S, "series": 0, "target": P69._datum(DEBT_AVG_END, 0)},
        {"kind": "build_to", "at": t_last, "dur": TIP_S, "series": 0, "target": P69._datum(DEBT_TIP, 0)},
        {"kind": "figure", "at": t_121, "dur": FIG_S, "target": P69._datum(DEBT_TIP, 0), "text": tip_text, "dy": BOX_FIG_DY},
        # A56: the box names the MOVE on its number, and leaves as the next sentence opens
        {"kind": "span", "form": "box", "at": t_121, "dur": round(t_this - t_121, 2), "from": DEBT_AVG_END, "to": DEBT_TIP},
        {"kind": "chart_to", "at": t_track, "dur": extend_dur, "to": "extend", "series": 1},
        # ... and the rule names the DATE as the forward draw lands on it (an axis tag pops when its page stands - the
        # extend's end; earlier it is WARNed and waits, P71 T9)
        {"kind": "axis_tag", "at": round(t_track + extend_dur, 2), "dur": round(runtime - t_track - extend_dur, 2),
         "x": DEBT_2026, "guide": "rule"},   # P72 T53 (i) / R26-415: Bravos's full-height dated rule (BOOM 18:00.5)
    ]
    return (0.0, runtime, DEBT_PLATE, (0, 0, 0), [], None, species)


def _box_object() -> dict:
    """T16's composition with the COMMITTED object's own estimate tick put back ([2026, '2026E'] - read off
    ev-debt-issuance-line-v1, never typed): the axis carries the projected year, labelled as the estimate it is, so the
    dated rule stands on a date the page draws (s109) and names it as an estimate (E77) - Bravos's axis runs to 2028 with
    the future's room in view (BOOM 17:56.5)."""
    import build_golden_sources as G
    obj = _debt_object()
    committed = json.loads(G.PROJ_OBJECT.read_text(encoding="utf-8"))
    est = [t for t in committed["xticks"] if t[0] == DEBT_2026]
    assert est and str(est[0][1]).endswith("E"), committed["xticks"]   # the committed tick names itself an estimate
    obj["xticks"] = obj["xticks"] + est
    return obj


def _box_objects(ep: Path) -> None:
    objects = ep / "evidence/objects"
    objects.mkdir(parents=True, exist_ok=True)
    (objects / f"{DEBT_ID}.series.json").write_text(json.dumps(_box_object(), indent=1), encoding="utf-8")


def _box_strip(ws: list) -> list:
    t_avg, t_28, t_last, t_121, t_track, t_50 = _evidence_times(ws)
    return [(round(t_121 + 0.3, 2), "the box goes round the last move (the pen)"),
            (round(t_121 + 1.2, 2), "the box stands round 2024 -> 2025"),
            (round(T.at(ws, "This year") + 0.2, 2), "the box has left"),
            (round(t_50 + 1.4, 2), "the dated rule (2026E) and the dashed estimate to it")]


def _evidence_objects(ep: Path) -> None:
    objects = ep / "evidence/objects"
    objects.mkdir(parents=True, exist_ok=True)
    (objects / f"{DEBT_ID}.series.json").write_text(json.dumps(_debt_object(), indent=1), encoding="utf-8")


@dataclass(frozen=True)
class Beat:
    slug: str                 # the recipe's slug (recipe:<slug>)
    first: str                # the phrase the beat's first sentence opens on
    last: str                 # a phrase in the beat's last sentence (the beat closes at that sentence's stop)
    row: Callable[[list, float], tuple]
    strip: Callable[[list], list]
    objects: Callable[[Path], None] | None = None   # a beat whose page is a composed object writes it into a PRIVATE ep


BEATS = {b.slug: b for b in (
    Beat("push-to-now-then-the-unknown", "That's the July release", "and so am I", _push_row, _push_strip),
    Beat("evidence-then-the-conditional-future", "Then the bills got bigger", "tracking toward a hundred",
         _evidence_row, _evidence_strip, _evidence_objects),
    Beat("the-box-then-the-dated-rule", "Then the bills got bigger", "tracking toward a hundred",
         _box_row, _box_strip, _box_objects),   # P72 T46g: A56 on R26's page and words
)}


# ---------------------------------------------------------------- the build (P69 T35's door, this slice's dirs)

def build_dir(slug: str) -> Path:
    return HERE / f"build-lab-{slug}"


def build_beat(beat: Beat) -> int:
    """ONE beat through the kit's compile door, into its own private build dir."""
    before = P69._read_only_state()
    build = build_dir(beat.slug)
    project = Project(here=P69.EP, build=build, take=P69.TAKE, take_stem=P69.TAKE_STEM, script_name="SCRIPT-H-VO.txt",
                      episode_id=f"p71-t26-{beat.slug}", take_name="vo-h-scratch")
    project.mkdirs()
    ep = P69.EP
    if beat.objects is not None:
        ep = build / "ep"
        beat.objects(ep)
    words, t0, runtime = P69.clip_words(W.take_words(project), beat)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t0, "-i", str(P69.TAKE / (P69.TAKE_STEM + ".mp3")),
                    "-t", "%.3f" % runtime, "-c:a", "libmp3lame", "-q:a", "2", str(project.audio_master)], check=True)
    W.write_timeline(project, words, runtime)
    T.caption_pages(build, char_budget=P69.CAPTION_BUDGET, max_words=P69.CAPTION_MAX_WORDS)
    (build / "evidence-dock.json").write_text("[]", encoding="utf-8")
    row = beat.row(words, runtime)
    table = build / "SHOT-TABLE-P71-T26.py"
    T.write_shot_table(table, [row], f'"""{TAG} proof beat - recipe:{beat.slug}. GENERATED by proof_t26.py; never a cut."""\n')
    T.print_rows([row], show_docks=True)
    rc = T.compile_timeline(ep, build, timeline_name=f"{beat.slug}.timeline.json",
                            shot_table_file=os.path.relpath(table, ep), title=f"{TAG} proof - recipe:{beat.slug}",
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
    ap.add_argument("--strips", type=Path, default=HERE / "build-lab-strips", help="where the <recipe>-strip.png sheets go")
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
