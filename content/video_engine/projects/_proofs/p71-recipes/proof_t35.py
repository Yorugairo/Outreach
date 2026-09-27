"""P71 T35 - the chart-and-diagram recipes (was P69 T70), each PROVED AS A BEAT (E99 s60, s70).

    python content/video_engine/projects/_proofs/p71-recipes/proof_t35.py                            # build + strip every beat
    python content/video_engine/projects/_proofs/p71-recipes/proof_t35.py --beat rise-turn-consequence  # one beat, no strip
    python content/video_engine/projects/_proofs/p71-recipes/proof_t35.py --strip-only                 # re-shoot the strips

The door is P69 T35's (`_proofs/p69-recipes/proof_p69_recipes.py`) through P71 T34's (`proof_t34.py`), both IMPORTED,
never edited: one real beat per recipe - its own sentence off the Steel and Paper H scratch take, the words as the clock,
the captions paged by the kit - through the AUTHORING KIT's compile door under a NAMED no-receipt reason. It writes only
inside `build-lab-<recipe>/` beside this file (gitignored) and the strip dir; the Steel and Paper project is read and
asserted unmoved. A DERIVED object (the budget's two bars) lives inside its own build dir, every value READ off a
committed file, never re-typed.

THE BEATS (every one on its H row's own words):
  rise-turn-consequence            ROW 13 (not row 12: row 12's world is the three-manias TABLE, a PNG card with no page
                                   to recede and no fall spoken; "kept working" is row 13's own, and USE-WHEN R19 names it),
                                   "And in 1849 the answer wasn't the paper ... The paper stopped pretending" on row 9's
                                   `ev-railway-index-v1` (the paper). The page opens where T34's peak-fall-magnitude leaves
                                   it (the peak ringed, the fall drawn and lit, -64% at the trough - row 13 does not re-say
                                   the fall, so R18 is CARRIED, not replayed); on "wasn't the paper" the chart PARKS left to
                                   make room; on "It was the steel" a hub lands - THE STEEL - and what hangs off it branches
                                   out on its own words (the certificate, the trains, the towns); on "stopped pretending"
                                   the paper's link FAILS. T12's check has no seat on a flow's rim node (see NOTES).
  doubt-then-the-budget-evidence   ROW 11, "Alex Karp of Palantir says enterprises are paying for tokens that create no
                                   value ... the spend gets harder to justify" on the records' desk (H's MEMO_PLATE): the
                                   doubt as a diagram ABOVE (ENTERPRISES -> TOKENS -> VALUE, the link to value failing on
                                   "no value"), the budget answering BELOW (Uber's year as two bars: the months the budget
                                   was for, the months it lasted), then the source card LAST in the same slot - the COO's
                                   record typed from `ev-doc-macdonald.html`, its own highlighted phrase landing as the
                                   narrator says it.
  the-total-points-back            THE DISCOVERY BEAT (plan T35), NO RECIPE: row 16's three bars (T34's derived object), the
                                   total written at its bar on "a hundred and fifty", then T50's bracket on "It is big
                                   enough". NO card draws a leader - curved or straight - from a figure back to a bar: the
                                   clothoid arrow is the flow's, between two of its own laid-out cards. Kept so the finding
                                   re-plays.
"""
from __future__ import annotations

import argparse
import calendar
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))
sys.path.insert(0, str(HERE.parent / "p69-recipes"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "content/video_engine/tests"))

import proof_p69_recipes as P69                             # noqa: E402  (imported, never edited - the P71 rule)
import proof_t34 as T34                                     # noqa: E402  (imported, never edited)
from authoring import Project                               # noqa: E402
from authoring import docks as D, table as T, words as W    # noqa: E402

sys.path.insert(0, str(P69.EP))
import build_episode_h as H                                 # noqa: E402  (the H door's constants, READ; main() never runs)

TAG = "P71 T35"
EP = P69.EP


# ---------------------------------------------------------------- R19: rise, turn, consequence (row 13)

RAIL_PAGE, RAIL_PEAK, RAIL_TROUGH, RAIL_DROP = T34.RAIL_PAGE, T34.RAIL_PEAK, T34.RAIL_TROUGH, T34.RAIL_DROP
OPEN_S = 0.4             # the page stands as T34's R18 left it: the fall drawn to the trough over the beat's first breath
PARK_S, PARK_SCALE, PARK_ANCHOR = 1.0, 0.55, "left"   # the chart makes room at the right (chart_to park, P48 T2b)
STEEL_BOX = {"kind": "region", "x0": 0.55, "y0": 0.08, "x1": 0.97, "y1": 0.78}   # the room the park leaves, above the captions
STEEL = [{"id": "steel", "icon": "factory", "label": "THE STEEL"},
         {"id": "paper", "icon": "tag", "label": "THE PAPER"},        # "not the certificate": the share, a price
         {"id": "trains", "icon": "truck", "label": "TRAINS"},        # no rail glyph on disk (A2a's sourced set) - a finding
         {"id": "towns", "icon": "building", "label": "TOWNS"}]


def _steel_times(ws: list) -> tuple:
    return (T.at(ws, "wasn't the paper"), T.at(ws, "It was the steel"), W.word_in(ws, "not the certificate", "certificate"),
            T.at(ws, "trains ran"), T.at(ws, "towns kept"), T.at(ws, "The steel kept"), T.at(ws, "stopped pretending"))


def _steel_row(ws: list, runtime: float) -> tuple:
    _t_wasnt, t_steel, t_cert, t_trains, t_towns, _t_kept, t_stopped = _steel_times(ws)
    datum = lambda i: {"kind": "datum", "index": i, "series": 0}   # noqa: E731
    nodes = [dict(STEEL[0]), dict(STEEL[1], at=t_cert), dict(STEEL[2], at=t_trains), dict(STEEL[3], at=t_towns)]
    species = [
        # T34's peak-fall-magnitude, CARRIED: the page arrives in the state R18 leaves it (ring, fall, light, the drop)
        {"kind": "build_to", "at": 0.0, "dur": OPEN_S, "series": 0, "target": datum(RAIL_TROUGH)},
        {"kind": "ring", "at": 0.0, "dur": round(runtime, 2), "form": "dashed", "target": datum(RAIL_PEAK)},
        {"kind": "lit_stretch", "at": OPEN_S, "dur": T34.LIGHT_S, "from": RAIL_PEAK, "to": RAIL_TROUGH},
        {"kind": "figure", "at": OPEN_S, "dur": T34.DROP_S, "target": datum(RAIL_TROUGH), "text": RAIL_DROP,
         "color": "neg", "dy": T34.DROP_DY},
        # R19's own: the recede, the branch, the consequence
        {"kind": "chart_to", "at": t_steel, "dur": PARK_S, "to": "park", "scale": PARK_SCALE, "anchor": PARK_ANCHOR},
        {"kind": "flow", "at": t_steel, "dur": round(runtime - t_steel, 2), "target": dict(STEEL_BOX), "layout": "hub",
         "nodes": nodes, "edges": [["steel", n["id"]] for n in nodes[1:]],
         "fail": {"edge": ["steel", "paper"], "at": t_stopped}},
    ]
    return (0.0, runtime, T34._line(RAIL_PAGE, RAIL_TROUGH), (0, 0, 0), [], None, species)


def _steel_strip(ws: list) -> list:
    t_wasnt, t_steel, t_cert, t_trains, t_towns, t_kept, t_stopped = _steel_times(ws)
    return [(round(t_wasnt - 0.3, 2), "the fall quantified (R18, carried)"),
            (round(t_steel + 1.3, 2), "parked: the room opens, THE STEEL lands"),
            (round(t_kept + 0.3, 2), "what hangs off it branched, each on its word"),
            (round(t_stopped + 0.9, 2), "the paper's link fails")]


# ---------------------------------------------------------------- R34: the doubt, then the budget evidence (row 11)

DOUBT_BOX = {"kind": "region", "x0": 0.34, "y0": 0.03, "x1": 0.96, "y1": 0.34}   # the question ABOVE, right of the desk lamp
DOUBT = [{"id": "firms", "icon": "building", "label": "ENTERPRISES"},
         {"id": "tokens", "icon": "cpu", "label": "TOKENS"},
         {"id": "value", "icon": "coins", "label": "VALUE"}]
SLOT = {"centre": True, "centre_x": 0.5, "centre_y": 0.615, "centre_w": 0.5}     # the answer BELOW, over the captions
BUDGET_CARD = "lab-uber-budget-bars"
COO_REC = "lab-coo-record"
_UBER_META = next(m for m in H.DOCK_META if m["asset"] == H.UBER_CARD)
_MONTHS = {calendar.month_name[i]: i for i in range(1, 13)}


def _budget_lasted() -> tuple[str, int]:
    """The month the budget ran out, READ off H's Uber card badge ("spent by April") - its month number is how long it lasted."""
    said = next(b["value"] for b in _UBER_META["badges"] if "BUDGET" in b["label"])
    month = next(m for m in _MONTHS if m in said)
    return month, _MONTHS[month]


def budget_object() -> dict:
    """Uber's 2026 AI budget as two bars in ONE unit (months): the year it was for (annual: 12) and how long it lasted
    (spent by April: 4) - the record's own words (H's badge, The Information), counted on the calendar; no dollar figure,
    because none is on the record (Bravos HIS 02:05-02:08 draws the same two spans, its budget a '$X')."""
    month, lasted = _budget_lasted()
    year = len(_MONTHS)   # "annual": the calendar's months, never typed
    return {"title": "Uber's 2026 AI budget", "sub": "Months of the year it was for - and how long it lasted",
            "src": f"{_UBER_META['source']} ('{_UBER_META['badges'][0]['value']}'); months counted on the calendar",
            "unit": "months",
            "bars": [{"label": "Budgeted for (Jan-Dec)", "value": year, "color": "deemph", "note": str(year)},
                     {"label": f"Lasted (Jan-{month[:3]})", "value": lasted, "color": "crimson", "note": str(lasted)}]}


def _coo_record() -> tuple[str, dict, tuple]:
    """The COO's record, every field READ off the committed document `ev-doc-macdonald.html` (its <mark> is the phrase)."""
    doc = (EP / "evidence/ev-doc-macdonald.html").read_text(encoding="utf-8")
    text = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()   # noqa: E731
    grab = lambda pat: re.search(pat, doc, re.S).group(1)                                   # noqa: E731
    hdr = [text(s) for s in re.findall(r"<span>(.*?)</span>", grab(r'<div class="hdr">(.*?)</div>'))]
    quote = text(grab(r"<blockquote>(.*?)</blockquote>"))
    mark = text(grab(r"<mark>(.*?)</mark>"))
    record = {"hdr": hdr, "kicker": text(grab(r'<div class="kicker">(.*?)</div>')),
              "attr": text(grab(r'<div class="attr">(.*?)</div>')), "src": text(grab(r'<div class="src">(.*?)</div>'))}
    toks = quote.split()
    k = next(i for i in range(len(toks)) if " ".join(toks[i:]).startswith(mark))
    hl = tuple(toks[k:k + len(mark.split())])
    return quote, record, hl


def _doubt_times(ws: list) -> tuple:
    return (T.at(ws, "says enterprises"), W.word_in(ws, "create no value", "no"), T.at(ws, "Uber's CTO"),
            W.word_in(ws, "they burned their", "burned"), T.at(ws, "And their COO"), T.at(ws, "harder to justify"))


def _doubt_register(build: Path, ws: list) -> list:
    # the object sits BESIDE the card's PNG (<asset>.series.json): the compiler hands it to the player as a LIVE chart
    # payload, so the bars GROW in the card on its landing (dock_payload:chart), the PNG the static fallback
    live = build / "docks" / f"{BUDGET_CARD}.series.json"
    live.parent.mkdir(parents=True, exist_ok=True)
    live.write_text(json.dumps(budget_object(), indent=1), encoding="utf-8")
    D.chart_card(BUDGET_CARD, live, build, variant="bars", card_w=round(SLOT["centre_w"] * 1920, 2))
    D.record_asset(COO_REC, build)
    quote, record, hl = _coo_record()
    sync = {w.strip(".,;:!?()").lower(): w.strip(".,;:!?()”").lower() for w in hl if w[:1].isalpha()}
    typed, span, end = D.record_words(quote, round(_doubt_times(ws)[4] + 0.4, 2), ws, "gets harder to justify", sync, hl)
    budget_badge = [dict(b) for b in _UBER_META["badges"] if "BUDGET" in b["label"]]   # the record's own words (B3)
    return [{"asset": BUDGET_CARD, "title": "Uber's AI budget", "source": _UBER_META["source"], "species": "chart",
             "badges": budget_badge},
            {"asset": COO_REC, "title": "Andrew Macdonald, Uber COO", "source": record["hdr"][0], "species": "record",
             "badges": [], "record": dict(record, words=typed, hl=span, end=end)}]


def _doubt_row(ws: list, runtime: float) -> tuple:
    t_says, t_no, t_uber, t_burned, t_coo, _t_harder = _doubt_times(ws)
    flow = {"kind": "flow", "at": t_says, "dur": round(runtime - t_says, 2), "target": dict(DOUBT_BOX),
            "nodes": [dict(n) for n in DOUBT], "edges": [["firms", "tokens"], ["tokens", "value"]],
            "fail": {"edge": ["tokens", "value"], "at": t_no},
            # "they burned their entire annual AI budget": the money runs into the tokens (T11's tokens, the coins glyph)
            "tokens": {"n": 2, "from_at": t_burned, "glyph": "coins"}}
    bars = dict(SLOT, card_aspect=D.card_aspect(BUDGET_CARD, build_dir("doubt-then-the-budget-evidence")),
                arrive="throw", mass="paper")
    rec = dict(SLOT, card_aspect=H.COO_ASPECT, arrive="throw", mass="paper")
    docks = [(BUDGET_CARD, 0, t_uber, t_coo, bars), (COO_REC, 0, t_coo, runtime, rec)]
    # DRAFT 2 asked for a dashed ring on the 4-month bar on "four months" (P72 T48's docked datum) - REFUSED: a docked
    # BARS card has no series ("series 0 is not on its chart (0..-1)", R26-367) - a finding, not worked round here
    return (0.0, runtime, H.MEMO_PLATE, H.MEMO_KEN, docks, None, [flow])


def _doubt_strip(ws: list) -> list:
    t_says, t_no, t_uber, t_burned, t_coo, t_harder = _doubt_times(ws)
    return [(round(t_no + 0.8, 2), "the doubt above: the link to value fails"),
            (round(t_burned + 2.6, 2), "the budget below: 12 months, 4; money into tokens"),
            (round(t_coo + 1.6, 2), "the source card last, in the same slot"),
            (round(t_harder + 1.2, 2), "its own phrase highlighted as it is said")]


# ---------------------------------------------------------------- R35: the total points back (row 16) - the discovery

def _total_times(ws: list) -> tuple:
    return T.at(ws, "twenty-eight billion"), T.at(ws, "a hundred and fifty"), T.at(ws, "It is big enough")


def _total_row(ws: list, runtime: float) -> tuple:
    _t28, t150, t_big = _total_times(ws)
    species = [{"kind": "figure", "at": t150, "dur": 1.4, "target": {"kind": "datum", "index": 2},
                "text": "$%dB" % T34.RATIO_2026, "sub": "the total"},
               {"kind": "bracket", "at": t_big, "dur": T34.BRACKET_S, "from": 0, "to": 2, "label": T34.RATIO_MULT,
                "sub": "2026E on the 2020-24 year"}]
    return (0.0, runtime, T34._bars(T34.RATIO_OID), (0, 0, 0), [], None, species)


def _total_strip(ws: list) -> list:
    t28, t150, t_big = _total_times(ws)
    return [(round(t28 + 0.6, 2), "the 28 bar - what the total must point back to"),
            (round(t150 + 1.6, 2), "the total at its bar: nothing can lead from it"),
            (round(t_big - 0.3, 2), "no leader card: figure -> bar has no join"),
            (round(t_big + T34.BRACKET_S + 0.5, 2), "only the bracket: a vertical span, not a pointer")]


# ---------------------------------------------------------------- the beats

@dataclass(frozen=True)
class Beat:
    slug: str                 # the recipe's slug (recipe:<slug>)
    first: str                # the phrase the beat's first sentence opens on
    last: str                 # a phrase in the beat's last sentence (the beat closes at that sentence's stop)
    row: Callable[[list, float], tuple]
    strip: Callable[[list], list]
    objects: Callable[[], dict] | None = None               # a DERIVED page: {object id: series object}, a lab project
    register: Callable[[Path, list], list] | None = None   # dock assets + their META, when the beat docks


BEATS = {b.slug: b for b in (
    Beat("rise-turn-consequence", "And in 1849 the answer", "stopped pretending", _steel_row, _steel_strip),
    Beat("doubt-then-the-budget-evidence", "Alex Karp of Palantir", "harder to justify", _doubt_row, _doubt_strip,
         register=_doubt_register),
    Beat("the-total-points-back", "Between 2020 and 2024", "big enough to bend", _total_row, _total_strip,
         lambda: {T34.RATIO_OID: T34.ratio_object()}),
)}


# ---------------------------------------------------------------- the build (P69 T35's door, this slice's dirs)

def build_dir(slug: str) -> Path:
    return HERE / f"build-lab-{slug}"


def _write_lab(build: Path, oid: str, obj: dict) -> Path:
    """A derived object inside the beat's own (gitignored) build dir - never beside the episode's evidence."""
    out = build / "lab/evidence/objects" / f"{oid}.series.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    return out


def _lab_project(beat: Beat, build: Path) -> Path:
    """Steel and Paper itself, or - for a derived PAGE - a private lab project holding only the derived object."""
    if beat.objects is None:
        return EP
    for oid, obj in beat.objects().items():
        _write_lab(build, oid, obj)
    return build / "lab"


def build_beat(beat: Beat) -> int:
    """ONE beat through the kit's compile door, into its own private build dir."""
    before = P69._read_only_state()
    build = build_dir(beat.slug)
    project = Project(here=EP, build=build, take=P69.TAKE, take_stem=P69.TAKE_STEM, script_name="SCRIPT-H-VO.txt",
                      episode_id=f"p71-t35-{beat.slug}", take_name="vo-h-scratch")
    project.mkdirs()
    words, t0, runtime = P69.clip_words(W.take_words(project), beat)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t0, "-i", str(P69.TAKE / (P69.TAKE_STEM + ".mp3")),
                    "-t", "%.3f" % runtime, "-c:a", "libmp3lame", "-q:a", "2", str(project.audio_master)], check=True)
    W.write_timeline(project, words, runtime)
    T.caption_pages(build, char_budget=P69.CAPTION_BUDGET, max_words=P69.CAPTION_MAX_WORDS)
    meta = beat.register(build, words) if beat.register else []
    (build / "evidence-dock.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    row = beat.row(words, runtime)
    ep = _lab_project(beat, build)
    table = build / "SHOT-TABLE-P71-T35.py"
    T.write_shot_table(table, [row], f'"""{TAG} proof beat - recipe:{beat.slug}. GENERATED by proof_t35.py; never a cut."""\n')
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
    """Four instants of the compiled beat through ONE served player (T34's strip, this slice's tag)."""
    T34.TAG = TAG
    T34.build_dir = build_dir
    return T34.render_strip(slug, out_dir)


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
