"""P69 T35 - the candidate recipes from P69's mechanisms, each PROVED AS A BEAT (E99 s60, s70).

    python content/video_engine/projects/_proofs/p69-recipes/proof_p69_recipes.py                  # build + strip the three kept (two WITHDRAWN 2026-09-23 on the parent's read: the bar never halves - a value morph is owed, R26-273; a bracket draws nothing on a bars page, R26-272)
    python content/video_engine/projects/_proofs/p69-recipes/proof_p69_recipes.py --beat two-clocks  # one beat, no strip
    python content/video_engine/projects/_proofs/p69-recipes/proof_p69_recipes.py --strips <dir>     # strips somewhere else

E99 s60: *"what the operator watches must be a beat a short could carry; a held fixture is a test, not a proof."* So
every recipe here is built as ONE REAL BEAT: its own sentence off the Steel and Paper H scratch take (the audio clipped
to that sentence, the words as the clock, the captions paged by the kit), on the evidence page the recipe names, through
the AUTHORING KIT's own compile door (`authoring.table.compile_timeline`) - never a golden surface with its clock faked.
E99 s70: a recipe is a TIMING that composes, never a scene; the beat is the recipe plus the sentence around it, and the
offsets the recipe files carry are the ones measured off these beats.

WRITES ONLY INSIDE `build-lab-<recipe>/` beside this file (gitignored by `.gitignore`'s `projects/**/build-lab-*/`;
`build-<recipe>/` is NOT ignored, which is why the dirs carry the `lab` word) and the strip dir. Everything in the
Steel and Paper project is READ: the take, the evidence objects, the props, the leases record - and asserted unmoved.
The compile goes in under a NAMED no-receipt reason (the P67 door's escape), because this is a test bed, never a cut.

THE THREE BEATS (the sixth candidate, `the-prop-lands-with-weight`, waits for lane B's resting prop shadow - T6b - to
merge). Two more were WITHDRAWN 2026-09-23 on the parent's read of their frames, and their code removed:
`the-bar-halves-its-number` (R26-273: a bar can't change its value - `chart_to compare` melts "20%" into "10%" but the
bar stays at 20%, so the new number sits at the old gridline; a bar value morph is owed) and `the-ratio-read-in-the-gap` (R26-272: a bracket draws
nothing on bars - `paintBracket` reads `st.linePts`, which a bars page never has, and the compiler accepts the row
silently).
  estimate-opens-as-a-wedge              row 16's sentence on `ev-debt-issuance-line-v1`: the actual line lands, the two
                                         estimate edges draw on "This year", the wedge between them bleeds (`spread`) and
                                         the RANGE is written as the figure ($130-150B, 2026E) - never a midpoint (E53/E77)
  the-stamp-takes-the-room-then-the-card row 16's leases sentence on the debt page: the datacenter prop stamped into the
                                         page's biggest room on "Data centers", then the leases record placed clear of the
                                         mark and its ring on "right there in the filing" (P69 T5; see LEASES_BOX)
  two-clocks                             row 19 on `ev-two-clocks-bars-v1`: one unit (years), the 20-year bar deemphasized,
                                         the 5-year bar crimson, and its figure - the claim - on "about five years"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project                               # noqa: E402
from authoring import docks as D, table as T, words as W    # noqa: E402

EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
OBJECTS = EP / "evidence/objects"
PROPS = REPO / "content/video_engine/assets/props/cutouts"
TAKE, TAKE_STEM = EP / "vo-h-scratch", "scratch-kokoro"
ASPECT = "16:9"                       # the H episode is long form; its pages are stamped full-stage (R26-205)
LEAD_S, TAIL_S = 0.6, 1.8             # the beat opens a breath before its first word and closes after its last
CAPTION_BUDGET, CAPTION_MAX_WORDS = 34, 6   # the long form's caption page (build_episode_h.py CAPTION_*)
KINETICS = {"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False,
            "curvature_stroke": True, "plate_idle_paints": False}   # the H door's own dials, unchanged
READ_ONLY = ("evidence", "vo-h-scratch", "SCRIPT-H-VO.txt", "build_episode_h.py")
STAMP = {"prop": True, "arrive": "stamp", "mass": "ink", "ink": "own"}   # T5's stamp, as its golden row carries it


def _series(name: str) -> dict:
    return json.loads((OBJECTS / (name + ".series.json")).read_text(encoding="utf-8"))


def _label_index(obj: dict, label: str) -> int:
    """A series by its own label, never a typed index (build_episode_h.py DEBT_SPREAD's rule)."""
    return [s["label"] for s in obj["series"]].index(label)


def _datum(i: int, series: int | None = None) -> dict:
    d = {"kind": "datum", "index": i}
    if series is not None:
        d["series"] = series
    return d


# ---------------------------------------------------------------- the beats (a row per beat, anchored on WORDS)

@dataclass(frozen=True)
class Beat:
    slug: str                 # the recipe's slug (recipe:<slug>)
    first: str                # the phrase the beat's first sentence opens on
    last: str                 # a phrase in the beat's last sentence (the beat closes at that sentence's stop)
    row: Callable[[list, float], tuple]   # (the beat's words, its runtime) -> the ONE shot row
    strip: Callable[[list], list]        # the beat's words -> [(t, what the frame shows)] x 4
    register: Callable[[Path], list] = lambda build: []   # dock assets + their META, when the beat docks


DEBT_PAGE = "ev-debt-issuance-line-v1"
DEBT = _series(DEBT_PAGE)
DEBT_ACTUAL, DEBT_HIGH, DEBT_LOW = (_label_index(DEBT, n) for n in ("issuance", "$150B", "$130B"))
DEBT_LAST_AVG = 4                      # 2024, the last year of the 2020-24 AVERAGE the object draws flat
DEBT_2025 = len(DEBT["series"][DEBT_ACTUAL]["pts"]) - 1
DEBT_RANGE_TEXT, DEBT_RANGE_SUB = "$130–150B", "2026E"   # build_episode_h.py DEBT_RANGE_* - the range, never a midpoint


def _wedge_row(ws: list, runtime: float) -> tuple:
    at = lambda p: T.at(ws, p)
    t121, t_year, t_track, t150 = at("a hundred and twenty-one"), at("This year"), at("tracking toward"), \
        at("a hundred and fifty")
    species = [
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": DEBT_ACTUAL, "target": _datum(DEBT_LAST_AVG, DEBT_ACTUAL)},
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": DEBT_HIGH, "target": _datum(0, DEBT_HIGH)},
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": DEBT_LOW, "target": _datum(0, DEBT_LOW)},
        {"kind": "build_to", "at": t121, "dur": 1.0, "series": DEBT_ACTUAL, "target": _datum(DEBT_2025, DEBT_ACTUAL)},
        {"kind": "build_to", "at": t_year, "dur": 1.2, "series": DEBT_HIGH, "target": _datum(1, DEBT_HIGH)},
        {"kind": "build_to", "at": t_year, "dur": 1.2, "series": DEBT_LOW, "target": _datum(1, DEBT_LOW)},
        {"kind": "spread", "at": t_track, "dur": 1.6, "from": DEBT_HIGH, "to": DEBT_LOW},
        {"kind": "figure", "at": t150, "dur": 1.5, "target": _datum(1, DEBT_HIGH), "text": DEBT_RANGE_TEXT,
         "sub": DEBT_RANGE_SUB, "dy": -0.9},
    ]
    return (0.0, runtime, f"ledger:{DEBT_PAGE}:line::right:axes:cut;idle=live", (0, 0, 0), [], None, species)


def _wedge_strip(ws: list) -> list:
    at = lambda p: T.at(ws, p)
    return [(round(at("a hundred and twenty-one") + 1.2, 2), "the actual line lands (2020-24 average, 2025)"),
            (round(at("This year") + 1.3, 2), "the two estimate edges open from 2025"),
            (round(at("tracking toward") + 1.0, 2), "the wedge between them bleeds (spread)"),
            (round(at("a hundred and fifty") + 1.8, 2), "the RANGE written as the figure")]


LEASES_CARD = "ev-doc-leases"
DC_PROP = "prop-hyperscale-datacenter-v1"
LEASES_META = {"asset": LEASES_CARD, "title": "Off-Balance-Sheet Leases", "source": "PIMCO, from 10-Qs",
               "species": "deck",   # copied from build-f/evidence-dock.json (read, never written); a PNG card, not a record
               "badges": [{"label": "COMMITMENTS", "value": "$822B", "tag": "not on a balance sheet"}]}


def _card_aspect(png: Path) -> float:
    from PIL import Image
    with Image.open(png) as im:
        return round(im.height / im.width, 4)


def _stamp_register(build: Path) -> list:
    D.register(DC_PROP, PROPS / (DC_PROP + ".png"))
    D.register(LEASES_CARD, OBJECTS / (LEASES_CARD + ".png"))
    return [LEASES_META]


def _stamp_times(ws: list) -> tuple[float, float]:
    return T.at(ws, "Data centers"), T.at(ws, "right there in the filing")


# THE CARD'S BOX IS AUTHORED, AND THE COMPILER STILL GUARDS THE STAMP. The first cut left the card to E65's placer:
# with the stamp holding the page's biggest room (the right quiet zone) the placer found no room for a 0.36-aspect
# record on this ESTIMATED page and took "the emptiest corner at the legibility floor" - a 100x80 card over the $150B
# tag. The record is placed instead in the plot's own empty room (above the flat 2020-24 line, left of the 2024-25
# rise), and `stamp_clash_error` - T5's refusal - still fails the row if that box touches the mark or its ring.
LEASES_BOX = {"centre": True, "centre_w": 0.36, "centre_x": 0.25, "centre_y": 0.40}


def _stamp_row(ws: list, runtime: float) -> tuple:
    t_dc, t_filing = _stamp_times(ws)
    card = dict(LEASES_BOX, card_aspect=_card_aspect(OBJECTS / (LEASES_CARD + ".png")))
    docks = [(LEASES_CARD, 0, t_filing, runtime, card), (DC_PROP, 1, t_dc, runtime, dict(STAMP))]
    return (0.0, runtime, f"ledger:{DEBT_PAGE}:line::right:axes:cut;idle=live", (0, 0, 0), docks, None, [])


def _stamp_strip(ws: list) -> list:
    t_dc, t_filing = _stamp_times(ws)
    return [(round(t_dc + 0.04, 2), "the mark comes down into the biggest room"),
            (round(t_dc + 0.20, 2), "the ring thrown, hugging the mark"),
            (round(t_filing + 0.4, 2), "the record arrives, clear of mark + ring"),
            (round(t_filing + 2.0, 2), "at rest: the prop in the world, the record beside it")]


CLOCKS_PAGE = "ev-two-clocks-bars-v1"


def _clocks_row(ws: list, runtime: float) -> tuple:
    obj = _series(CLOCKS_PAGE)
    short = min(range(len(obj["bars"])), key=lambda i: obj["bars"][i]["value"])
    text = f"{obj['bars'][short]['value']:g} {obj['unit']}"      # "5 years" - the bar's own value and the page's unit
    species = [{"kind": "figure", "at": W.word_in(ws, "It depreciates in about five years", "five"), "dur": 1.5,
                "text": text, "target": _datum(short)}]
    return (0.0, runtime, f"ledger:{CLOCKS_PAGE}:bars::right:axes:cut;idle=live", (0, 0, 0), [], None, species)


def _clocks_strip(ws: list) -> list:
    t5 = W.word_in(ws, "It depreciates in about five years", "five")
    return [(round(T.at(ws, "two decades") + 0.4, 2), "one unit, two clocks: 20 years deemphasized"),
            (round(T.at(ws, "doesn't sit") + 0.2, 2), "the short bar, crimson, before its word"),
            (round(t5 + 0.7, 2), "its figure writes on the word"),
            (round(t5 + 2.2, 2), "the claim held: 5 years")]


BEATS = {b.slug: b for b in (
    Beat("estimate-opens-as-a-wedge", "Between 2020 and 2024", "tracking toward a hundred", _wedge_row, _wedge_strip),
    Beat("the-stamp-takes-the-room-then-the-card", "Go into the filings", "right there in the filing",
         _stamp_row, _stamp_strip, _stamp_register),
    Beat("two-clocks", "Railway steel sat waiting", "It depreciates in about five years", _clocks_row, _clocks_strip),
)}


# ---------------------------------------------------------------- the take, clipped to the beat's sentences

def _sentence_end(ws: list, i: int) -> int:
    """The index of the word that closes the spoken sentence word `i` sits in."""
    for k in range(i, len(ws)):
        if ws[k]["w"].rstrip().rstrip(W.QUOTE_TAIL)[-1:] in W.HARD_STOPS:
            return k
    return len(ws) - 1


def clip_words(ws_all: list, beat: Beat) -> tuple[list, float, float]:
    """(the beat's words on its own clock, the clip's start in the take, the beat's runtime)."""
    i0, t_first = W.phrase_start(ws_all, beat.first)
    i1 = _sentence_end(ws_all, W.phrase_start(ws_all, beat.last)[0])
    t0 = round(max(0.0, t_first - LEAD_S), 3)
    words = [{"w": w["w"], "start_s": round(w["start_s"] - t0, 3), "end_s": round(w["end_s"] - t0, 3)}
             for w in ws_all[i0:i1 + 1]]
    return words, t0, round(words[-1]["end_s"] + TAIL_S, 2)


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    if path.is_file():
        h.update(path.read_bytes())
    elif path.is_dir():
        for p in sorted(path.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                h.update(f"{p.relative_to(path).as_posix()}|{p.stat().st_size}".encode())
    else:
        return "absent"
    return h.hexdigest()


def _read_only_state() -> dict:
    return {rel: _digest(EP / rel) for rel in READ_ONLY}


def build_dir(slug: str) -> Path:
    return HERE / f"build-lab-{slug}"


def build_beat(beat: Beat) -> int:
    """ONE beat through the kit's compile door, into its own private build dir."""
    before = _read_only_state()
    build = build_dir(beat.slug)
    project = Project(here=EP, build=build, take=TAKE, take_stem=TAKE_STEM, script_name="SCRIPT-H-VO.txt",
                      episode_id=f"p69-t35-{beat.slug}", take_name="vo-h-scratch")
    project.mkdirs()
    words, t0, runtime = clip_words(W.take_words(project), beat)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t0, "-i", str(TAKE / (TAKE_STEM + ".mp3")),
                    "-t", "%.3f" % runtime, "-c:a", "libmp3lame", "-q:a", "2", str(project.audio_master)], check=True)
    W.write_timeline(project, words, runtime)
    T.caption_pages(build, char_budget=CAPTION_BUDGET, max_words=CAPTION_MAX_WORDS)
    (build / "evidence-dock.json").write_text(json.dumps(beat.register(build), indent=1), encoding="utf-8")
    row = beat.row(words, runtime)
    table = build / "SHOT-TABLE-P69-T35.py"
    T.write_shot_table(table, [row], f'"""P69 T35 proof beat - recipe:{beat.slug}. GENERATED by '
                                     f'proof_p69_recipes.py; never a cut."""\n')
    T.print_rows([row], show_docks=True)
    rc = T.compile_timeline(EP, build, timeline_name=f"{beat.slug}.timeline.json",
                            shot_table_file=os.path.relpath(table, EP), title=f"P69 T35 proof - recipe:{beat.slug}",
                            subtitle=f"Steel and Paper H take {t0:.2f}-{t0 + runtime:.2f}s", episode_id=project.episode_id,
                            aspect=ASPECT, caption_style=None, kinetics=KINETICS,
                            no_receipt=f"P69 T35 recipe proof: recipe:{beat.slug} (a private test-bed beat, never a cut)")
    moved = [rel for rel, d in _read_only_state().items() if d != before[rel]]
    if moved:
        raise SystemExit("FAIL: the proof wrote into a READ-ONLY path: " + ", ".join(moved))
    (build / "beat.json").write_text(json.dumps({"recipe": f"recipe:{beat.slug}", "take_from_s": t0, "runtime_s": runtime,
                                                 "words": " ".join(w["w"] for w in words), "row": row,
                                                 "strip": beat.strip(words)}, indent=1, default=str), encoding="utf-8")
    print(f"  beat        : recipe:{beat.slug} - take {t0:.2f}s + {runtime:.2f}s -> {build}")
    return rc


# ---------------------------------------------------------------- the strip (4 instants, read by the parent)

def _spoken_at(words: list, t: float) -> str:
    near = [w["w"] for w in words if w["start_s"] <= t + 0.05 and w["end_s"] >= t - 1.6]
    return " ".join(near[-6:])


def render_strip(slug: str, out_dir: Path) -> Path:
    """Four instants of the compiled beat, shot through ONE served player, side by side with their words."""
    from PIL import Image, ImageDraw
    from playwright.sync_api import sync_playwright
    import render_baseline as RB
    build = build_dir(slug)
    beat = json.loads((build / "beat.json").read_text(encoding="utf-8"))
    tl = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    words = [{"w": w["w"], "start_s": w["start"], "end_s": w["end"]} for w in tl["words"]]
    w, h = RB.STAGE[ASPECT]
    srv, port = RB.serve(build)
    shots = []
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            page = br.new_context(viewport={"width": w, "height": h}).new_page()
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{port}/player.html", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            for t, what in beat["strip"]:
                png = build / f"strip-{t:05.2f}.png"
                png.write_bytes(RB.frame_png(page, t, (w, h)))
                shots.append((t, what, png))
            br.close()
            if errors:
                raise SystemExit(f"FAIL: the player threw on recipe:{slug}: {errors[:3]}")
    finally:
        srv.shutdown()
    scale, pad, head, foot = 0.34, 12, 40, 44
    fw, fh = int(w * scale), int(h * scale)
    sheet = Image.new("RGB", (pad + len(shots) * (fw + pad), head + fh + foot), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), f"P69 T35 - recipe:{slug}  |  take {beat['take_from_s']:.2f}s + {beat['runtime_s']:.2f}s  |  "
                         f"one real beat, its own words, on its own page (E99 s60)", fill=(235, 235, 235))
    for i, (t, what, png) in enumerate(shots):
        x = pad + i * (fw + pad)
        with Image.open(png) as im:
            sheet.paste(im.convert("RGB").resize((fw, fh), Image.LANCZOS), (x, head))
        draw.text((x + 2, head - 14), f"{t:.2f}s  {what}", fill=(245, 200, 90))
        draw.text((x + 2, head + fh + 6), f"\"{_spoken_at(words, t)}\"", fill=(200, 200, 200))
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
