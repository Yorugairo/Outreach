"""P71 T34 - the Bravos recipes (was P69 T44), each PROVED AS A BEAT (E99 s60, s70).

    python content/video_engine/projects/_proofs/p71-recipes/proof_t34.py                          # build + strip every beat
    python content/video_engine/projects/_proofs/p71-recipes/proof_t34.py --beat peak-fall-magnitude  # one beat, no strip
    python content/video_engine/projects/_proofs/p71-recipes/proof_t34.py --strip-only               # re-shoot the strips

The door is P69 T35's (`_proofs/p69-recipes/proof_p69_recipes.py`, IMPORTED, never edited): one real beat per recipe -
its own sentence off the Steel and Paper H scratch take, the words as the clock, the captions paged by the kit - through
the AUTHORING KIT's compile door under a NAMED no-receipt reason. It writes only inside `build-lab-<recipe>/` beside this
file (gitignored) and the strip dir; the Steel and Paper project is read and asserted unmoved. A beat whose page is a
DERIVED object (the three issuance bars, the iceberg) compiles against a private lab project inside its own build dir
(`build-lab-<recipe>/lab/evidence/objects/`), every value READ off a committed file, never re-typed.

THE BEATS (every one on its H row's own words):
  peak-fall-magnitude            row 9, "Railways in the 1840s drew a quarter-billion pounds ... then crashed by nearly
                                 two-thirds" on `ev-railway-index-v1`: the climb lands on the October 1845 peak, a dashed
                                 ring circles it (E56: a datum), the crash draws on "crashed", a light runs the fall on
                                 "nearly two-thirds" and the drop is written at the trough as the page's own arithmetic
                                 (-64%, the object's marks - never the treatment's -66, E77).
  the-epoch-walk                 row 9, "In two thousand the internet crossed ... AI spending just crossed eight" on
                                 `ev-equip-ipp-gdp-v2`: the DOT-COM era shaded and named on "two thousand", the fall lit
                                 on "then the tower came down", the line carried on to today on "AI spending", and the
                                 second era shaded and named - in turn, never at once (DOM 06:11-06:38, BOOM 02:59/03:00).
  the-ratio-read-in-the-gap      row 16's issuance as the dossier's own three bars (C1: 2020-24 average, 2025, 2026E top
                                 of the range): the raw values land with the page, printed at the bar tops, and are HELD
                                 while the sentence says them, then on "It is big enough" the bracket from the average to
                                 2026E writes the multiple, computed (STK 1:54-2:18). No end is a claim (P73 T1), so the
                                 multiple carries no speaker.
  isolate-then-quantify-the-tail row 14 (NOT row 18: row 18's page is one bar and two rules - nothing to isolate), "At the
                                 dot-com peak ... Today it's twenty-eight, the most it has ever been" on
                                 `ev-capital-formation-v1` (long form): the peer ("for scale") mutes on "Today" and the
                                 tech line's end badge takes the accent (its one badge), a light runs its tail from the
                                 dot-com high to today, and a ring circles the tip on "the most it has ever been" (JPN
                                 05:25-05:45). Draft 1 pushed the line on to today AFTER the solo: the solo's accent box
                                 stood EMPTY at the plot's right while the tag waited for the line (P72 T46d's box - a
                                 finding), so the page stands whole and the push is the light.
  the-formula-by-its-words       row 18, "At a fifth of the index, if the AI names fall by half, that erases ten percent"
                                 on `ev-index-concentration-bars-v1` (long form): the 20 bar lit as its term is written,
                                 then the equation in spoken order - P70 T6's golden terms on the take's own words.
  the-bar-halves-its-number      row 18, the same sentence: the 20 written as the bar lands (R26-284), and on "fall by
                                 half" the bar itself halves (T26a, `chart_to compare`, H's own CONC_COMPARE), "10%"
                                 landing on "ten percent", the old top a ghost.
  the-hidden-base                row 16, "And that's the borrowing you can see ... eight hundred and twenty-two billion in
                                 lease commitments ... never landed on a balance sheet": ONE stacked bar (T64's segments) -
                                 the leases under the waterline (a rule at the boundary), the bonds above it - the camera
                                 raised on the tip, then the pedestal down through the waterline (T32) on "lease
                                 commitments", the bar's edge lit (T29). THE DISCOVERY BEAT (plan T34), NO RECIPE: it did
                                 not compose - the raised camera shows the void and the mount's edge above a full-stage
                                 page and the base is still on screen at by 0.21 (the stage is not taller than the frame),
                                 and the glow edges the whole bar, not the hidden part. Kept so the finding re-plays.
"""
from __future__ import annotations

import argparse
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
sys.path.insert(0, str(REPO / "content/video_engine/tests"))

import proof_p69_recipes as P69                             # noqa: E402  (imported, never edited - the P71 rule)
from authoring import Project                               # noqa: E402
from authoring import table as T, words as W                # noqa: E402

TAG = "P71 T34"
PAGE_TAIL = ":right:axes:cut;idle=live"                     # the P69 door's page form (full stage, E73's axes, E49)
LONGFORM = ";readability=longform"                          # rows 14 on are drawn in the long form's profile (E99 s97)
EP = P69.EP


def _obj(name: str) -> dict:
    return P69._series(name)


def _nearest(pts: list, x: float) -> int:
    return min(range(len(pts)), key=lambda k: abs(pts[k][0] - x))


def _named(obj: dict, prefix: str) -> int:
    """A series by its own name or label, never a typed index (build_episode_h.py DIV_*'s rule)."""
    return next(i for i, s in enumerate(obj["series"]) if (s.get("name") or s.get("label") or "").startswith(prefix))


def _line(plate_id: str, cap: int, *, longform: bool = False, extra: str = "") -> str:
    return f"ledger:{plate_id}:line:{cap}{PAGE_TAIL}{LONGFORM if longform else ''}{extra}"


def _bars(plate_id: str, *, longform: bool = True, extra: str = "") -> str:
    return f"ledger:{plate_id}:bars:{PAGE_TAIL}{LONGFORM if longform else ''}{extra}"


# ---------------------------------------------------------------- R18: peak, fall, magnitude (row 9)

RAIL_PAGE = "ev-railway-index-v1"
RAIL = _obj(RAIL_PAGE)
_RAIL_PTS = RAIL["series"][0]["pts"]
RAIL_PEAK = _nearest(_RAIL_PTS, RAIL["marks"][0]["x"])      # the October 1845 high, the page's own mark
RAIL_TROUGH = _nearest(_RAIL_PTS, RAIL["marks"][1]["x"])    # April 1850
RAIL_HALF = round(RAIL_PEAK / 2)                            # the climb's half-way cap, where the beat opens
RAIL_DROP = "−%d%%" % abs(round(100 * (RAIL["marks"][1]["y"] / RAIL["marks"][0]["y"] - 1)))   # -64%, the object's own
CRASH_S = 1.2            # H row 9's RAIL_CRASH_S: the fall draws on "crashed"
LIGHT_S = 1.56           # the lit-stretch golden's run over "nearly two-thirds."
DROP_S, DROP_DY = 1.4, -0.9   # H row 9's figure (RAIL_DROP_S / RAIL_DROP_DY: over the trough, under the 1843 rule)


def _peak_times(ws: list) -> tuple[float, float, float, float]:
    return (T.at(ws, "drew a quarter-billion"), T.at(ws, "pounds, more than"), T.at(ws, "crashed by nearly"),
            W.word_in(ws, "crashed by nearly", "nearly"))


def _peak_row(ws: list, runtime: float) -> tuple:
    t_drew, t_peak, t_crash, t_nearly = _peak_times(ws)
    datum = lambda i: {"kind": "datum", "index": i, "series": 0}   # noqa: E731
    species = [
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": datum(RAIL_HALF)},
        {"kind": "build_to", "at": t_drew, "dur": round(t_peak - t_drew, 2), "series": 0, "target": datum(RAIL_PEAK)},
        {"kind": "ring", "at": t_peak, "dur": round(runtime - t_peak, 2), "form": "dashed", "target": datum(RAIL_PEAK)},
        {"kind": "build_to", "at": t_crash, "dur": CRASH_S, "series": 0, "target": datum(RAIL_TROUGH)},
        {"kind": "lit_stretch", "at": t_nearly, "dur": LIGHT_S, "from": RAIL_PEAK, "to": RAIL_TROUGH, "comet": True},
        {"kind": "figure", "at": round(t_nearly + LIGHT_S * 0.8, 2), "dur": DROP_S, "target": datum(RAIL_TROUGH),
         "text": RAIL_DROP, "color": "neg", "dy": DROP_DY},
    ]
    return (0.0, runtime, _line(RAIL_PAGE, RAIL_TROUGH), (0, 0, 0), [], None, species)


def _peak_strip(ws: list) -> list:
    t_drew, t_peak, t_crash, t_nearly = _peak_times(ws)
    return [(round(t_peak + 0.9, 2), "the peak lands, the dashed ring on it"),
            (round(t_crash + CRASH_S + 0.05, 2), "the crash drawn to the trough"),
            (round(t_nearly + LIGHT_S * 0.5, 2), "the light runs the fall"),
            (round(t_nearly + LIGHT_S * 0.8 + DROP_S + 0.4, 2), "-64% written at the trough")]


# ---------------------------------------------------------------- R22: the epoch walk (row 9)

GDP_PAGE = "ev-equip-ipp-gdp-v2"
GDP = _obj(GDP_PAGE)
_GDP_PTS = GDP["series"][0]["pts"]
GDP_LAST = len(_GDP_PTS) - 1
GDP_PEAK = max(range(_nearest(_GDP_PTS, 2001.0)), key=lambda k: _GDP_PTS[k][1])    # Q2 2000, read off the data
GDP_DOTCOM = (_nearest(_GDP_PTS, 1998.0), _nearest(_GDP_PTS, 2003.0))              # H row 9's GDP_DOTCOM_FROM / _TO
GDP_FALL_END = min(range(GDP_PEAK, GDP_DOTCOM[1] + 1), key=lambda k: _GDP_PTS[k][1])   # where the fall bottoms, in the era
GDP_AI = _nearest(_GDP_PTS, 2020.0)                                                # H row 9's GDP_AI_FROM
ERA_DOTCOM, ERA_AI = "DOT-COM", "AI"   # the eras' names, no number (the page's 11.5 is not the voice's 7 / 8); SHORT:
# measured on draft 1, "THE AI BUILD-OUT" was wider than its six-year band and wrote over the "11.51%" end tag and the
# peak rule's label (a span's name is centred on its band, inside its top edge when the plot has no room above)
ERA_S = 2.0              # a span's window: the shade's fade-in (SPAN.IN_S 0.45) and the name's write over half of it
FALL_S = 1.2             # the fall lit over "then the tower came down."
CLIMB_S = 2.0            # H row 9's GDP_CLIMB_S: the line carried on to today on "AI spending just crossed"


def _epoch_times(ws: list) -> tuple[float, float, float, float]:
    return (T.at(ws, "two thousand"), T.at(ws, "then the tower came down"), T.at(ws, "AI spending just"),
            W.word_in(ws, "AI spending just crossed", "crossed"))


def _epoch_row(ws: list, runtime: float) -> tuple:
    t_2000, t_tower, t_ai, t_cross = _epoch_times(ws)
    datum = lambda i: {"kind": "datum", "index": i, "series": 0}   # noqa: E731
    species = [
        {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": datum(GDP_DOTCOM[0])},
        {"kind": "build_to", "at": t_2000, "dur": round(t_tower - t_2000, 2), "series": 0, "target": datum(GDP_DOTCOM[1])},
        {"kind": "span", "at": t_2000, "dur": ERA_S, "from": GDP_DOTCOM[0], "to": GDP_DOTCOM[1], "label": ERA_DOTCOM},
        {"kind": "lit_stretch", "at": t_tower, "dur": FALL_S, "from": GDP_PEAK, "to": GDP_FALL_END},
        {"kind": "build_to", "at": t_ai, "dur": CLIMB_S, "series": 0, "target": datum(GDP_LAST)},
        {"kind": "span", "at": t_cross, "dur": ERA_S, "from": GDP_AI, "to": GDP_LAST, "label": ERA_AI},
    ]
    return (0.0, runtime, _line(GDP_PAGE, GDP_LAST), (0, 0, 0), [], None, species)


def _epoch_strip(ws: list) -> list:
    t_2000, t_tower, t_ai, t_cross = _epoch_times(ws)
    return [(round(t_2000 + ERA_S * 0.9, 2), "era 1 shaded and named"),
            (round(t_tower + FALL_S + 0.2, 2), "the fall lit: the tower came down"),
            (round(t_ai + CLIMB_S * 0.6, 2), "the line carried on to today"),
            (round(t_cross + ERA_S + 0.3, 2), "era 2 shaded and named - in turn")]


# ---------------------------------------------------------------- R20: the ratio read in the gap (row 16)

DEBT = P69.DEBT
_BY = {s["label"]: s["pts"] for s in DEBT["series"]}
RATIO_OID = "lab-issuance-three-bars"
RATIO_AVG = _BY["issuance"][0][1]              # 28: the 2020-24 annual average (the object's flat first point)
RATIO_2025 = _BY["issuance"][-1][1]            # 121: 2025 actual
RATIO_2026 = _BY["$150B"][-1][1]               # 150: the top of the 2026 estimate range
RATIO_MULT = "%.1fx" % (RATIO_2026 / RATIO_AVG)   # "5.4x" - computed off the two bars, never typed


def ratio_object() -> dict:
    """The dossier's own three bars (EVIDENCE-DOSSIER.md C1: "Rebuild as three bars: 2020-24 average $28B -> 2025 $121B
    -> 2026E $130-150B"), every value READ off `ev-debt-issuance-line-v1`; 2026E is the range's TOP, named as such."""
    return {"title": DEBT["title"],
            "sub": "Hyperscaler bond issuance, US$ billions a year - 2020-24 an average; 2026E the top of the $130-150B range",
            "src": DEBT["src"], "unit": "$", "unit_suffix": "B",
            "bars": [{"label": "2020-24, a year", "value": RATIO_AVG, "color": "deemph"},
                     {"label": "2025", "value": RATIO_2025, "color": "deemph"},
                     {"label": "2026E, top of range", "value": RATIO_2026, "color": "crimson"}]}


def _ratio_times(ws: list) -> tuple[float, float, float, float]:
    return (T.at(ws, "twenty-eight billion"), T.at(ws, "a hundred and twenty-one"), T.at(ws, "a hundred and fifty"),
            T.at(ws, "It is big enough"))


BRACKET_S = 1.8          # the span draws, its ticks pop, the multiple writes (P50's bracket clock)


# THE RAW VALUES ARE THE BARS' OWN (measured on draft 1: a `figure` on each bar's word restated the value the page had
# printed as it landed - P72 T18's WARN x3, R26-284 - and nothing visibly landed on the word). So the three values land
# WITH THE PAGE, printed at the bar tops, and are HELD through the whole sentence that says them (STK held 14-16 s);
# the bracket and its multiple come only after, on "It is big enough".
def _ratio_row(ws: list, runtime: float) -> tuple:
    _t28, _t121, _t150, t_big = _ratio_times(ws)
    species = [{"kind": "bracket", "at": t_big, "dur": BRACKET_S, "from": 0, "to": 2, "label": RATIO_MULT,
                "sub": "2026E on the 2020-24 year"}]
    return (0.0, runtime, _bars(RATIO_OID), (0, 0, 0), [], None, species)


def _ratio_strip(ws: list) -> list:
    t28, t121, t150, t_big = _ratio_times(ws)
    return [(round(t28 + 0.6, 2), "the raw values stand, printed as the page landed"),
            (round(t150 + 1.2, 2), "the last raw value said - still held"),
            (round(t_big - 0.3, 2), "HELD: read before the multiple"),
            (round(t_big + BRACKET_S + 0.5, 2), "the bracket: the multiple in the gap")]


# ---------------------------------------------------------------- R24: isolate, then quantify the tail (row 14)

YARD_PAGE = "ev-capital-formation-v1"
YARD = _obj(YARD_PAGE)
YARD_TECH = _named(YARD, "COMPUTERS")
YARD_PEER = _named(YARD, "ALL EQUIPMENT")
_YARD_PTS = YARD["series"][YARD_TECH]["pts"]
YARD_LAST = len(_YARD_PTS) - 1
YARD_HIGH = _nearest(_YARD_PTS, YARD["marks"][0]["x"])    # the dot-com high the page's own mark names (2001, 23%)
SOLO_S = 0.7             # the peer mutes on "Today" (the solo golden's 0.71)
PUSH_S = 1.6             # the light runs the tail, the dot-com high -> today, over "Today it's twenty-eight"
TIP_RING_S = 1.2


def _tail_times(ws: list) -> tuple[float, float, float]:
    return T.at(ws, "Today it's"), W.word_in(ws, "Today it's twenty-eight", "it's"), T.at(ws, "the most it has")


def _tail_row(ws: list, runtime: float) -> tuple:
    t_today, t_its, t_most = _tail_times(ws)
    datum = lambda i, s: {"kind": "datum", "index": i, "series": s}   # noqa: E731
    species = [
        {"kind": "solo", "at": t_today, "dur": SOLO_S, "series": YARD_TECH},
        {"kind": "lit_stretch", "at": t_its, "dur": PUSH_S, "series": YARD_TECH, "from": YARD_HIGH, "to": YARD_LAST,
         "comet": True},
        {"kind": "ring", "at": t_most, "dur": round(runtime - t_most, 2), "form": "dashed",
         "target": datum(YARD_LAST, YARD_TECH)},
    ]
    return (0.0, runtime, _line(YARD_PAGE, YARD_LAST, longform=True), (0, 0, 0), [], None, species)


def _tail_strip(ws: list) -> list:
    t_today, t_its, t_most = _tail_times(ws)
    return [(round(t_today - 0.4, 2), "the dot-com high, both lines in ink"),
            (round(t_today + SOLO_S + 0.05, 2), "isolated: the peer mutes"),
            (round(t_its + PUSH_S * 0.6, 2), "the light runs the tail to its accent badge"),
            (round(t_most + TIP_RING_S + 0.3, 2), "the tip rung: the most it has ever been")]


# ---------------------------------------------------------------- R25 + the halving: row 18's arithmetic

CONC_PAGE = "ev-index-concentration-bars-v1"
CONC = _obj(CONC_PAGE)
CONC_BAR = 0
CONC_SHARE = CONC["bars"][CONC_BAR]["value"]                 # 20, read off the object
CONC_SHARE_TEXT = CONC["bars"][CONC_BAR]["note"]             # "20%", the bar's own note
CONC_HALVED = CONC_SHARE / 2                                 # "if the AI names fall by half" - the script's arithmetic
CONC_HALVED_TEXT = "%d%%" % CONC_HALVED
GLOW_S = 0.68            # the glow golden's edge-up
EQ_REGION = {"kind": "region", "x0": 0.06, "y0": 0.13, "x1": 0.72, "y1": 0.296}   # P70 T6's band: subtitle -> the bar's "20%"
EQ_DUR = 6.0
COMPARE_S = 2.0          # H row 18's CONC_COMPARE_S


def _conc_times(ws: list) -> tuple[float, float, float]:
    return T.at(ws, "At a fifth"), T.at(ws, "fall by half"), T.at(ws, "erases ten percent")


def _formula_row(ws: list, runtime: float) -> tuple:
    t_fifth, t_half, t_erase = _conc_times(ws)
    species = [
        {"kind": "glow", "at": t_fifth, "dur": GLOW_S, "bar": CONC_BAR},
        {"kind": "equation", "at": t_fifth, "dur": round(min(EQ_DUR, runtime - t_fifth), 2), "target": dict(EQ_REGION),
         "terms": [{"text": CONC_SHARE_TEXT, "value": CONC_SHARE, "at": t_fifth, "src": CONC_PAGE, "tier": "PLAUSIBLE",
                    "label": "AI's weight"},
                   {"text": "−½", "value": -0.5, "at": t_half, "tier": "scenario", "label": "a halving"}],
         "ops": ["×"], "result": {"text": "−" + CONC_HALVED_TEXT, "value": -CONC_HALVED, "at": t_erase,
                                  "label": "the index"}},
    ]
    return (0.0, runtime, _bars(CONC_PAGE), (0, 0, 0), [], None, species)


def _formula_strip(ws: list) -> list:
    t_fifth, t_half, t_erase = _conc_times(ws)
    return [(round(t_fifth + 0.9, 2), "the 20 lit as its term is written"),
            (round(t_half + 0.8, 2), "x, then the halving on its word"),
            (round(t_erase + 0.9, 2), "=, the signed result on 'erases'"),
            (round(t_erase + 2.2, 2), "the row held, in spoken order")]


def _halving_compare(at: float) -> dict:
    """H row 18's own CONC_COMPARE (build_episode_h.py), its figures read off the object."""
    return {"kind": "chart_to", "at": at, "dur": COMPARE_S, "to": "compare", "form": "melt", "then": "splash",
            "hold": "metric", "ghost": "yes",
            "metric": {"value": CONC_SHARE, "text": CONC_SHARE_TEXT, "label": "of the S&P 500"},
            "comparator": {"value": CONC_HALVED, "text": CONC_HALVED_TEXT, "label": "of the index, erased if they halve"},
            "inputs": {"share": CONC_SHARE}, "derive": "share / 2",
            "source": "[DERIVED: from ev-index-concentration-bars-v1 (Bravos Research, attributed), a fifth of the index "
                      "falling by half - share / 2]"}


def _halving_row(ws: list, runtime: float) -> tuple:
    _t_fifth, t_half, _t_erase = _conc_times(ws)
    species = [{"kind": "figure", "at": 0.0, "dur": 1.2, "text": CONC_SHARE_TEXT,
                "target": {"kind": "datum", "index": CONC_BAR}},
               _halving_compare(t_half)]
    return (0.0, runtime, _bars(CONC_PAGE), (0, 0, 0), [], None, species)


def _halving_strip(ws: list) -> list:
    t_fifth, t_half, t_erase = _conc_times(ws)
    return [(round(t_fifth + 0.4, 2), "the 20 written as the bar stands"),
            (round(t_half + COMPARE_S * 0.5, 2), "on 'fall by half' the BAR halves"),
            (round(t_half + COMPARE_S + 0.1, 2), "10% landed, the old top a ghost"),
            (round(t_erase + 1.2, 2), "held on 'ten percent'")]


# ---------------------------------------------------------------- R1: the hidden base (row 16) - the discovery

ICE_OID = "lab-leases-iceberg"
_LEASES_HTML = EP / "evidence/ev-doc-leases.html"


def _leases_value() -> float:
    """The filings' lease commitments, READ off the committed record's "Latest filings" row (ev-doc-leases.html: "$675
    billion" at end February 2026, "$822 billion" in the latest filings - the script's figure is the latest)."""
    text = re.sub(r"<[^>]+>", " ", _LEASES_HTML.read_text(encoding="utf-8"))
    m = re.search(r"Latest filings\s*\$(\d[\d,]*)\s*billion", text)
    if not m:
        raise SystemExit(f"FAIL: no 'Latest filings $<n> billion' row in {_LEASES_HTML}")
    return int(m.group(1).replace(",", ""))


ICE_HIDDEN = _leases_value()                                                # 822: off the balance sheet
ICE_VISIBLE = int(sum(p[1] for p in _BY["issuance"]))                     # 5 x 28 + 121 = 261: bonds issued 2020-25
PEDESTAL_BY = 0.21       # the camera raised this share of the stage (T32's dial, Bravos BUB 0:00 measured ~0.21)
PEDESTAL_S = 2.4         # the one move down (T32's test clock; BUB measured one move, then still)


def ice_object() -> dict:
    """ONE stacked bar: the hidden part at the base, the visible part above it - a waterline rule at the boundary."""
    total = ICE_HIDDEN + ICE_VISIBLE
    return {"title": "The borrowing you can see - and what sits under it",
            "sub": "US$ billions: bonds the builders issued 2020-25, over lease commitments never on a balance sheet",
            "src": "Bonds: ev-debt-issuance-line-v1 (5 x the 2020-24 average + 2025); leases: PIMCO from 10-Qs "
                   "(the filings' record) - our arithmetic",
            "unit": "$", "unit_suffix": "B",
            "hlines": [{"y": ICE_HIDDEN, "label": "the balance sheet", "color": "deemph"}],
            "bars": [{"label": "What they owe", "value": total, "color": "deemph",
                      "segments": [{"name": "Lease commitments", "value": ICE_HIDDEN, "color": "crimson"},
                                   {"name": "Bonds issued", "value": ICE_VISIBLE, "color": "deemph"}]}]}


def _ice_times(ws: list) -> tuple[float, float, float]:
    return T.at(ws, "the borrowing you can see"), T.at(ws, "lease commitments"), T.at(ws, "never landed on")


def _ice_row(ws: list, runtime: float) -> tuple:
    t_see, t_lease, t_never = _ice_times(ws)
    species = [{"kind": "glow", "at": t_never, "dur": GLOW_S, "bar": 0}]
    camera = {"keys": [], "pedestal": {"at": t_lease, "dur": PEDESTAL_S, "by": PEDESTAL_BY}}
    return (0.0, runtime, _bars(ICE_OID), (0, 0, 0), [], None, species, camera)


def _ice_strip(ws: list) -> list:
    t_see, t_lease, t_never = _ice_times(ws)
    return [(round(t_see + 0.6, 2), "the tip: what you can see"),
            (round(t_lease + PEDESTAL_S * 0.5, 2), "the pedestal down through the waterline"),
            (round(t_lease + PEDESTAL_S + 0.3, 2), "the base: the hidden part, true proportion"),
            (round(t_never + GLOW_S + 0.4, 2), "the bar lit on 'never landed'")]


# ---------------------------------------------------------------- the beats

@dataclass(frozen=True)
class Beat:
    slug: str                 # the recipe's slug (recipe:<slug>)
    first: str                # the phrase the beat's first sentence opens on
    last: str                 # a phrase in the beat's last sentence (the beat closes at that sentence's stop)
    row: Callable[[list, float], tuple]
    strip: Callable[[list], list]
    objects: Callable[[], dict] | None = None   # a DERIVED page: {object id: series object}, compiled in a lab project


BEATS = {b.slug: b for b in (
    Beat("peak-fall-magnitude", "Railways in the 1840s", "crashed by nearly", _peak_row, _peak_strip),
    Beat("the-epoch-walk", "In two thousand the internet", "AI spending just crossed", _epoch_row, _epoch_strip),
    Beat("the-ratio-read-in-the-gap", "Between 2020 and 2024", "big enough to bend", _ratio_row, _ratio_strip,
         lambda: {RATIO_OID: ratio_object()}),
    Beat("isolate-then-quantify-the-tail", "At the dot-com peak", "the most it has ever", _tail_row, _tail_strip),
    Beat("the-formula-by-its-words", "Run the arithmetic", "erases ten percent", _formula_row, _formula_strip),
    Beat("the-bar-halves-its-number", "At a fifth of the", "erases ten percent", _halving_row, _halving_strip),
    Beat("the-hidden-base", "And that's the borrowing", "never landed on", _ice_row, _ice_strip,
         lambda: {ICE_OID: ice_object()}),
)}


# ---------------------------------------------------------------- the build (P69 T35's door, this slice's dirs)

def build_dir(slug: str) -> Path:
    return HERE / f"build-lab-{slug}"


def _lab_project(beat: Beat, build: Path) -> Path:
    """The project the compile reads its page from: Steel and Paper itself, or - for a derived page - a private lab
    project inside the beat's own (gitignored) build dir holding only the derived object."""
    if beat.objects is None:
        return EP
    lab = build / "lab"
    (lab / "evidence/objects").mkdir(parents=True, exist_ok=True)
    for oid, obj in beat.objects().items():
        (lab / "evidence/objects" / f"{oid}.series.json").write_text(json.dumps(obj, indent=1), encoding="utf-8")
    return lab


def build_beat(beat: Beat) -> int:
    """ONE beat through the kit's compile door, into its own private build dir."""
    before = P69._read_only_state()
    build = build_dir(beat.slug)
    project = Project(here=EP, build=build, take=P69.TAKE, take_stem=P69.TAKE_STEM, script_name="SCRIPT-H-VO.txt",
                      episode_id=f"p71-t34-{beat.slug}", take_name="vo-h-scratch")
    project.mkdirs()
    words, t0, runtime = P69.clip_words(W.take_words(project), beat)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t0, "-i", str(P69.TAKE / (P69.TAKE_STEM + ".mp3")),
                    "-t", "%.3f" % runtime, "-c:a", "libmp3lame", "-q:a", "2", str(project.audio_master)], check=True)
    W.write_timeline(project, words, runtime)
    T.caption_pages(build, char_budget=P69.CAPTION_BUDGET, max_words=P69.CAPTION_MAX_WORDS)
    (build / "evidence-dock.json").write_text("[]", encoding="utf-8")
    row = beat.row(words, runtime)
    ep = _lab_project(beat, build)
    table = build / "SHOT-TABLE-P71-T34.py"
    T.write_shot_table(table, [row], f'"""{TAG} proof beat - recipe:{beat.slug}. GENERATED by proof_t34.py; never a cut."""\n')
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
