"""P71 T33 - the inset echo, then the question (R36; T40 C16's beside form), PROVED AS A BEAT.

    python content/video_engine/projects/_proofs/p71-recipes/proof_t33.py                       # build + strip both forms
    python content/video_engine/projects/_proofs/p71-recipes/proof_t33.py --form stack          # one form, build + strip
    python content/video_engine/projects/_proofs/p71-recipes/proof_t33.py --build-only --form handoff   # one compile
    python content/video_engine/projects/_proofs/p71-recipes/proof_t33.py --strip-only          # re-shoot the strips

The door is P69 T35's (`_proofs/p69-recipes/proof_p69_recipes.py`, IMPORTED, never edited), driven as P71 T26 drives it:
ONE real beat - its own sentences off the Steel and Paper H scratch take, the words as the clock, the captions paged by
the kit - through the AUTHORING KIT's compile door under a NAMED no-receipt reason. It writes only inside
`build-lab-inset-echo-then-the-question[-handoff]/` beside this file and `build-lab-strips/` (all gitignored); the Steel
and Paper project is read and asserted unmoved.

THE BEAT (E99 s60 - a beat a cut could carry, on its own words): H row 9, "Every transformative technology overshoots.
Railways in the 1840s drew a quarter-billion pounds ... then crashed by nearly two-thirds. In two thousand the internet
crossed seven percent of GDP, then the tower came down. By Bravos' math, AI spending just crossed eight."
  - the HOST is the AI era: `ev-equip-ipp-gdp-v2` read in the window 2015-today (the same BEA series H row 9 lands on
    the AI sentence, its own Q2 2000 peak rule kept - today is back at it). It lands built and PARKS left on
    "overshoots" (the chart makes room by one affine transform, CAPABILITIES `park`).
  - TWIN 1, "Railway shares, 1845": `ev-railway-index-v1` whole (its own source, Campbell & Turner; its own scale, an
    index of 442 railway shares - an unrelated measure keeps its own, E79 (2)) lands in the freed column on "1840s".
  - TWIN 2, "Internet, 2000": `ev-equip-ipp-gdp-v2` read in the window 1995-2005 (its own source, BEA via FRED; its own
    axis) lands on "In two thousand" - on the HOST'S y domain, because it is the same measure (E79 (1)).
  - both leave and the host UN-PARKS (scale 1.0) on "By Bravos' math"; a "?" (P71 T18's `unknown`) lands beside the
    plot, past today's tip by the right axis, on "just crossed eight" - the case the twins cannot close (USE-WHEN :401,
    "don't: the '?' stands in for a claim we could make": the sources give no ending for this one).
TWO FORMS (`Form`, below): `stack` is BOOM's (the twins one above the other); `handoff` gives one slot to one twin at a
time, wide enough that the card keeps each twin's source line. The parent chooses on the two strips.
The three objects are DERIVED here from the committed files (never re-typed: every point is the file's; the window, the
era title, the shared domain and a dropped rule are the only changes, each recorded in `derived_from`) and written into
this beat's PRIVATE episode dir (`build-lab-<recipe>/ep/evidence/objects/`), never the project's. Each twin is drawn FOR
ITS DISPLAYED SIZE by the chart card's `card` profile (P69 T10c), so every word on it sits at the phone floor as displayed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))
sys.path.insert(0, str(HERE.parent / "p69-recipes"))
sys.path.insert(0, str(REPO / "content/video_engine/tests"))
sys.path.insert(0, str(HERE))

import proof_p69_recipes as P69                             # noqa: E402  (imported, never edited - the P71 rule)
import proof_t26 as T26                                     # noqa: E402  (its strip renderer, imported, never edited)
from authoring import Project                               # noqa: E402
from authoring import docks as D, table as T, words as W    # noqa: E402

TAG = "P71 T33"
SLUG = "inset-echo-then-the-question"
FIRST, LAST = "Every transformative", "AI spending just crossed"   # H row 9, whole

# ---------------------------------------------------------------- the objects (derived from the committed files)

GDP_PAGE = "ev-equip-ipp-gdp-v2"          # BEA via FRED: equipment + IP investment, share of GDP, 1970-2026
RAIL_PAGE = "ev-railway-index-v1"         # Campbell & Turner: 442 railway shares, 1843-1850
HOST_ID, RAIL_ID, NET_ID = "fx-ai-era-gdp", "fx-twin-railways-1845", "fx-twin-internet-2000"
HOST_WINDOW = (2015.0, None)              # the AI era: 2015 to the file's last quarter (today)
NET_WINDOW = (1995.0, 2005.0)             # the internet's run-up, its Q2 2000 peak and the fall after it
GDP_DOMAIN = (9.0, 12.0)                  # E79 (1): the host and the internet twin are ONE measure (% of GDP), so they share
#                                           one y scale (their own lows 10.16 / 9.31, highs 11.51 / 11.54, read off the file):
#                                           today's line stands as high as 2000's did - the rhyme read on one scale


def _window(obj: dict, lo: float, hi: float | None, title: str, ticks: list[int], why: str) -> dict:
    """The object read in [lo, hi]: every point the file's own, the end tag re-written to the window's last datum (an
    end tag names the value it stands at), the title the era, everything else the file's."""
    out = json.loads(json.dumps(obj))
    for s in out["series"]:
        s["pts"] = [p for p in s["pts"] if p[0] >= lo and (hi is None or p[0] <= hi)]
        if str(s.get("label", "")).endswith("%"):
            s["label"] = "%.2f%%" % s["pts"][-1][1]
    out["title"] = title
    out["xticks"] = [[y, str(y)] for y in ticks]
    out["domain"] = list(GDP_DOMAIN)   # the dense-line page reads `domain` (ymin / ymax are not its keys: build 5)
    out["derived_from"] = {"object": f"{GDP_PAGE}.series.json", "window": [lo, hi], "domain": list(GDP_DOMAIN),
                           "by": f"{TAG} proof_t33.py", "why": why}
    return out


def host_object() -> dict:
    obj = P69._series(GDP_PAGE)
    last = int(obj["series"][0]["pts"][-1][0])
    return _window(obj, HOST_WINDOW[0], HOST_WINDOW[1], obj["title"],
                   list(range(2016, last, 2)) + [last], "the host page read in the AI era (the twins carry the past)")


def net_object() -> dict:
    """The internet twin. Its peak rule leaves it (the host keeps the Q2 2000 rule - the rhyme's level - and on a card
    the rule's label took the source's room and ran off the card's left edge: MEASURED, build 2, `frames/strip-b2.png`).
    The end tag carries the unit (%); a card drops the y label "% of GDP" (ledger_page.apply_card) - a finding."""
    out = _window(P69._series(GDP_PAGE), NET_WINDOW[0], NET_WINDOW[1], "Internet, 2000", [1996, 1998, 2000, 2002, 2004],
                  "the internet twin: the same BEA measure in its own era, on its own axis at the host's scale")
    out.pop("hline", None)
    return out


def rail_object() -> dict:
    out = json.loads(json.dumps(P69._series(RAIL_PAGE)))
    out["title"] = "Railway shares, 1845"                   # the era, and what the index measures (a card drops the y label)
    out["src"] = "Campbell & Turner - railway share index, 1843-1850"   # the file's own citation, its authors first: a
    #   card keeps the source's first clause when it fits (ledger_page.card_source) and "Campbell & Turner railway share
    #   index" does not at a twin's width (MEASURED, build 2: no source on the card)
    out.pop("hline", None)   # its "1843 level" label stood over the curve at a twin's width and took the source's room
    #                          (MEASURED, `probe/sheet.png`: 660-860 px, never a source with it); the basis goes with it
    out["derived_from"] = {"object": f"{RAIL_PAGE}.series.json", "window": None, "by": f"{TAG} proof_t33.py",
                           "why": "the railway twin: the whole file, its era as the title, its authors first in the source, its 1843 rule dropped"}
    return out


# ---------------------------------------------------------------- the row

PLATE = "ledger:%s:line::right:built:cut;idle=live;readability=longform" % HOST_ID


@dataclass(frozen=True)
class Form:
    """How the twins stand in the freed column. `stack` is BOOM's (08:48: two twins, one above the other); `handoff` is
    the same beat with ONE twin at a time in one slot (E99 s80's slot hand-off), wide enough for the card profile to
    keep each twin's source line - T10c's card drops the source when its plot needs the room (the engine's
    lpCardPlotNeed, PLOT_MIN 0.4 of the stage): MEASURED on these twins, a source survives from ~860 px (0.45 of the
    stage) and never at 760; two 16:9 cards stacked at 0.45 would take 0.9 of the stage's height, past the title band
    and the caption. The parent chooses on the frames."""
    park: float          # the host keeps this share of itself, anchored left
    w: float             # each twin's displayed width, stage share (a 16:9 card: its height is the same share)
    x: float             # the freed column's centre
    ys: tuple            # twin 1's and twin 2's centre heights (equal = one slot, the hand-off)
    suffix: str          # the build dir's and strip's suffix


FORMS = {
    # 672 px: at 0.345 the card's plot was a strip under its words (build 2); at 0.37 the top twin covered the host
    # title's tail (build 3) - 0.35 stands between the title band and the caption
    "stack": Form(park=0.58, w=0.35, x=0.79, ys=(0.30, 0.665), suffix=""),
    "handoff": Form(park=0.50, w=0.45, x=0.745, ys=(0.47, 0.47), suffix="-handoff"),
}
TWIN_ARRIVE = {"arrive": "throw", "mass": "paper"}
PARK_S, PARK_ANCHOR = 1.0, "left"                       # the host makes room on "overshoots", keeping its left side
UNPARK_S = 1.0
TWIN_OFF_LEAD_S = 0.2                                   # the twins leave just before "By Bravos' math" (BOOM 08:51.5)
TWIN_HOLD_MAX_S = 9.9    # E25 / M12: a chart dock proves its sentence and leaves inside CHART_HOLD_MAX_S (10 s). BOOM's
#                          twins stand 6 s and 3.5 s; H row 9's two sentences run 13 s, so the FIRST twin leaves once the
#                          second has landed and been read (MEASURED, build 1: both held to "By Bravos'" -> M12 FAIL,
#                          dock-t33-twin-railways-1845 held 13.4 s) - the stack stands ~2.6 s, then the second alone
UNKNOWN_SIZE = 122                                      # BOOM 08:52.5's chart-side "?" (species:unknown's default)
UNKNOWN_AT = {"kind": "point", "x": 0.945, "y": 0.40}   # right of the plot, by the right axis (BOOM 08:52.5)
UNKNOWN_TAIL_S = 1.2
RAIL_CARD, NET_CARD = "dock-t33-twin-railways-1845", "dock-t33-twin-internet-2000"


def _times(ws: list) -> tuple[float, float, float, float, float]:
    return (W.word_in(ws, "Every transformative technology overshoots", "overshoots"), W.word_in(ws, "Railways in the 1840s", "1840s"),
            T.at(ws, "In two thousand the internet"), T.at(ws, "By Bravos"),
            W.word_in(ws, "AI spending just crossed eight", "crossed"))


def _row(ws: list, runtime: float, form: Form) -> tuple:
    t_park, t_rail, t_net, t_bravos, t_crossed = _times(ws)
    off = round(t_bravos - TWIN_OFF_LEAD_S, 2)
    rail_off = t_net if form.ys[0] == form.ys[1] else min(off, round(t_rail + TWIN_HOLD_MAX_S, 2))   # one slot: hand off
    twin = lambda y, aid: dict(TWIN_ARRIVE, centre=True, centre_w=form.w, centre_x=form.x, centre_y=y,
                               card_aspect=D.card_aspect(aid, build_dir(form)))
    docks = [(RAIL_CARD, 0, t_rail, rail_off, twin(form.ys[0], RAIL_CARD)),
             (NET_CARD, 1, t_net, off, twin(form.ys[1], NET_CARD))]
    species = [
        {"kind": "chart_to", "at": round(t_park - 0.4, 2), "dur": PARK_S, "to": "park", "scale": form.park,
         "anchor": PARK_ANCHOR},
        {"kind": "chart_to", "at": off, "dur": UNPARK_S, "to": "park", "scale": 1.0, "anchor": PARK_ANCHOR},
        {"kind": "unknown", "at": t_crossed, "dur": round(min(runtime, t_crossed + UNKNOWN_TAIL_S + 1.0) - t_crossed, 2),
         "size": UNKNOWN_SIZE, "target": dict(UNKNOWN_AT)},
    ]
    return (0.0, runtime, PLATE, (0, 0, 0), docks, None, species)


def _strip(ws: list, form: Form) -> list:
    t_park, t_rail, t_net, t_bravos, t_crossed = _times(ws)
    return [(round(t_park + 1.0, 2), "the AI-era page parks left: room"),
            (round(t_net - 0.3, 2), "twin 1 'Railway shares, 1845' beside it"),
            (round(t_net + 1.6, 2), "twin 2 'Internet, 2000' " + ("in its slot" if form.suffix else "stacked under")),
            (round(t_crossed + 0.8, 2), "twins gone, page restored, '?' by the axis")]


# ---------------------------------------------------------------- the build (P69 T35's door, this slice's dirs)

def build_dir(form: Form | None = None) -> Path:
    return HERE / f"build-lab-{SLUG}{(form or FORMS['stack']).suffix}"


def _objects(ep: Path) -> dict:
    objects = ep / "evidence/objects"
    objects.mkdir(parents=True, exist_ok=True)
    paths = {}
    for oid, obj in ((HOST_ID, host_object()), (RAIL_ID, rail_object()), (NET_ID, net_object())):
        paths[oid] = objects / f"{oid}.series.json"
        paths[oid].write_text(json.dumps(obj, indent=1), encoding="utf-8")
    return paths


def _meta(aid: str, obj: dict) -> dict:
    return {"asset": aid, "title": obj["title"], "source": obj["src"], "species": "chart", "badges": []}


def build_beat(form: Form) -> int:
    """The beat through the kit's compile door, into its own private build dir."""
    before = P69._read_only_state()
    build = build_dir(form)
    project = Project(here=P69.EP, build=build, take=P69.TAKE, take_stem=P69.TAKE_STEM, script_name="SCRIPT-H-VO.txt",
                      episode_id=f"p71-t33-{SLUG}", take_name="vo-h-scratch")
    project.mkdirs()
    ep = build / "ep"
    paths = _objects(ep)
    card_w = round(form.w * 1920, 2)
    D.chart_card(RAIL_CARD, paths[RAIL_ID], build, "line", card_w=card_w)
    D.chart_card(NET_CARD, paths[NET_ID], build, "line", card_w=card_w)
    beat = P69.Beat(SLUG, FIRST, LAST, lambda ws, rt: _row(ws, rt, form), lambda ws: _strip(ws, form))
    words, t0, runtime = P69.clip_words(W.take_words(project), beat)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t0, "-i", str(P69.TAKE / (P69.TAKE_STEM + ".mp3")),
                    "-t", "%.3f" % runtime, "-c:a", "libmp3lame", "-q:a", "2", str(project.audio_master)], check=True)
    W.write_timeline(project, words, runtime)
    T.caption_pages(build, char_budget=P69.CAPTION_BUDGET, max_words=P69.CAPTION_MAX_WORDS)
    metas = [_meta(RAIL_CARD, rail_object()), _meta(NET_CARD, net_object())]
    (build / "evidence-dock.json").write_text(json.dumps(metas, indent=1), encoding="utf-8")
    row = _row(words, runtime, form)
    table = build / "SHOT-TABLE-P71-T33.py"
    T.write_shot_table(table, [row], f'"""{TAG} proof beat - recipe:{SLUG}. GENERATED by proof_t33.py; never a cut."""\n')
    T.print_rows([row], show_docks=True)
    rc = T.compile_timeline(ep, build, timeline_name=f"{SLUG}.timeline.json",
                            shot_table_file=os.path.relpath(table, ep), title=f"{TAG} proof - recipe:{SLUG}",
                            subtitle=f"Steel and Paper H take {t0:.2f}-{t0 + runtime:.2f}s", episode_id=project.episode_id,
                            aspect=P69.ASPECT, caption_style=None, kinetics=P69.KINETICS,
                            no_receipt=f"{TAG} recipe proof: recipe:{SLUG} (a private test-bed beat, never a cut)")
    moved = [rel for rel, d in P69._read_only_state().items() if d != before[rel]]
    if moved:
        raise SystemExit("FAIL: the proof wrote into a READ-ONLY path: " + ", ".join(moved))
    (build / "beat.json").write_text(json.dumps({"recipe": f"recipe:{SLUG}", "take_from_s": t0, "runtime_s": runtime,
                                                 "words": " ".join(w["w"] for w in words), "row": row,
                                                 "form": form.suffix or "-stack", "strip": _strip(words, form)},
                                                indent=1, default=str), encoding="utf-8")
    print(f"  beat        : recipe:{SLUG} - take {t0:.2f}s + {runtime:.2f}s -> {build}")
    return rc


def render_strip(form: Form, out_dir: Path) -> Path:
    """Four instants through ONE served player - proof_t26's renderer (imported, never edited), its two module names
    pointed at this beat: the build dir it reads and the tag it writes on the sheet."""
    T26.build_dir = lambda slug: build_dir(form)
    T26.TAG = TAG
    return T26.render_strip(SLUG + form.suffix, out_dir)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--form", choices=sorted(FORMS), action="append",
                    help="the twins' form (repeatable; default both - the parent chooses on the frames)")
    ap.add_argument("--build-only", action="store_true", help="compile ONE --form in this process (no strip)")
    ap.add_argument("--strip-only", action="store_true", help="re-shoot the strips of the forms already built")
    ap.add_argument("--strips", type=Path, default=HERE / "build-lab-strips", help="where the <recipe>-strip.png goes")
    args = ap.parse_args()
    names = args.form or list(FORMS)
    if args.build_only:
        if len(names) != 1:
            ap.error("--build-only compiles one --form")
        return build_beat(FORMS[names[0]])
    for name in names:
        if not args.strip_only:   # its own process: the compiler keeps module state between compiles
            rc = subprocess.run([sys.executable, __file__, "--build-only", "--form", name], cwd=str(REPO)).returncode
            if rc:
                print(f"FAIL: recipe:{SLUG} ({name}) did not compile (rc {rc})")
                return rc
        render_strip(FORMS[name], args.strips)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
