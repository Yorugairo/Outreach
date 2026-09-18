"""Ledger page spec: a ``series.json`` -> the page spec the plate-chart species consumes.

Doctrine: doc 29 s9.26 (data only from a series.json; the source line is written
on the page; exact values never re-rounded; a declared quiet zone; variants
line|bars|race|decline|progress) and s9.28 (surface x builder are two axes). P35 T2.

    ledger_page.py <series.json> --variant line|bars|race|decline|progress
                   [--emphasize n] [--quiet-zone left|right] [--out spec.json]

``--out`` defaults to ``<name>.page.json`` beside the input. Exit 0 on success,
2 when the series is not a page (the message names the file and every failing rule).
Input shapes (every one needs ``title`` and a non-empty ``src``):
  story    {"bars": [{"label", "value", "color", "note"?}]}   <= STORY_MAX_VALUES
  dense    {"series": [{"label"|"name", "color", "pts": [[x, y], ...]}], + AXES_KEYS}
           or {"panels": [{"sub", "series": [...]}]}
  tiers    {"tiers": [{"name", "unit", "series"|"pts"|"bars", + AXES_KEYS}], + AXES_KEYS}
           E79: same-unit tiers share ONE scale by default; ``independent: true`` (on the page, or on
           one tier) declares unrelated measures on their own scales. Undeclared same-unit tiers on
           different y-domains are a WARN (``spec["warnings"]``, printed ``[WARN]``) - see scale_warnings.
  race     {"periods": [...], "series": [{"name", "values": [...], "color"?}]}
           (or dense series sharing one x grid of >= RACE_MIN_PERIODS points)
  decline  exactly one metric (a single dense series, or bars of >= DECLINE_MIN_VALUES);
           first and last are the endpoints
  progress story values in 0..PROGRESS_MAX, or non-negative with a numeric "denominator"
Rejected clearly: "checklist" (a table). "shares" (a donut) is rejected for every variant EXCEPT
  `share`, which E53 s1 as amended (2026-09-07) allows inside four bounds - see SHARE_BOUNDS.
Builder (``pick_builder``): race/decline follow the variant; bars + a pts series ->
combo; > STORY_MAX_VALUES points or > 1 pts series -> dense-line; else story.
Output ``ledger_page.v1`` (ink/paper colours are NOT here - the template owns the
register; ``color`` token names pass through verbatim):
  schema_version, surface "page", builder, variant, title, sub, source, quiet_zone,
  emphasize (index clamped into labels, or null)
  labels / values / value_strings / colors   per datum (story); per series (race, values
           as one list per series); dense carries labels only. value_strings are the
           tokens EXACTLY as the file wrote them (parse_float=str: 3.90 stays "3.90")
  series, axes   dense-line and combo only, verbatim      periods   race only, verbatim
  start, end     decline only: {"label", "value", "value_string"} - label is the datum's token verbatim
  display_labels decline only: {"start", "end", "series"} - the READABLE x labels (s9.22: never a
           raw float): an exact ``xticks`` match, else a top-level ``labels`` list, else a decimal
           year as "Mon 'YY", else the token; ``series`` is the metric's name for the inline label
           (s9.23b; null for bars). A dense-series decline also carries ``axes`` verbatim.
  denominator    progress only, when the file carries one (verbatim token)
"""
from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

STORY_MAX_VALUES = 12    # s9.26 / chart-story: 4-8 values, our ceiling 12
RACE_MIN_PERIODS = 2     # s9.26: ranked bars overtaking ACROSS periods
DECLINE_MIN_VALUES = 2   # s9.26: one metric, a start and an end
PROGRESS_MAX = 100       # s9.26 progress: a share of a whole unless a denominator is given
EXIT_INVALID = 2
SCHEMA_VERSION = "ledger_page.v1"
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
YEAR_RANGE = (1900, 2100)   # a decimal x outside this is a number, not a date
VARIANTS = ("line", "bars", "race", "decline", "progress", "share", "object", "tiers", "treemap")
CHART_VARIANTS = ("line", "bars", "race", "decline", "progress", "share")
# `tiers` (P50 T9, R26-24; Bravos shots 35-36): N SMALL MULTIPLES on one page - N series, each in its
# own band with its own y-scale and its own honest zero (E53 s4), sharing ONE x. Two metrics whose
# units or magnitudes differ cannot share a y without one of them lying; what they CAN honestly share
# is the time axis, which is the comparison the sentence is making. `tiers: true` (a bool) stays what
# it was - the two-band combo's key - and builds byte-identically; `tiers: [...]` is this builder.
TIERS_MIN, TIERS_MAX = 2, 4
# `treemap` (P50 T6): the CENSUS page, under E53 s1's second amendment (ruled 2026-09-10).
# `object` is the page as a WORKING surface rather than an evidence surface: it draws
# a registered prop in ink on the cream instead of a chart. Same page clock, same
# deckle, same focus - so an object page can transform into a chart page without a
# plate change (RULE-the-page-is-the-ground, 2026-09-04).
PROP_PLACEMENTS = ("centre", "left", "right", "datum")
QUIET_ZONES = ("left", "right")
AXES_KEYS = ("overflow", "log", "ylabel", "xticks", "from_zero", "highlight_from", "hlines", "hline", "marks", "eventbars",
             "name_clear",   # lift the inline series name clear of the data it would otherwise be written across
             "ymin", "ymax", "yfmt", "yunit", "panels",
             "domain", "xdomain",   # P48 T2: a derived rescale state names its exact y domain and x window
             "overflow_placeholder", "overflow_capsule", "break_cadence",   # P50 T10 / T13: the breakthrough's furniture (E60)
             "independent")   # E79: this page (or this tier) carries unrelated measures, each on its own scale - nothing implies one
UNCHARTABLE = {
    "checklist": "no chartable values: 'checklist' is a table, not a chart (keep it a dock)",
    "shares": ("'shares' is a donut, and E53 s1 ranks angle and area at the bottom of the perception hierarchy: "
               "it is refused for every variant except --variant share, which the ruling's amendment (2026-09-07) "
               "allows only inside its four bounds - a part-to-whole claim about ONE named slice, that slice "
               "highlighted and the rest muted, the figure WRITTEN on the page, and five slices or fewer. "
               "A whole with MANY parts is a census: --variant treemap (E53 s1's second amendment, 2026-09-10)"),
}
# E53 s1 as amended (2026-09-07). The hierarchy's objection is to COMPARING many encoded angles; a claim about one
# highlighted slice is not that. These are the amendment's bounds, enforced here so the exception cannot widen by use.
SHARE_MAX_SLICES = 5
SHARE_BOUNDS = (
    "a part-to-whole claim about ONE named slice, never a ranking or a comparison across slices",
    "that slice highlighted, every other slice muted context",
    "the figure the claim turns on WRITTEN on the page, so no angle has to be estimated",
    f"{SHARE_MAX_SLICES} slices or fewer",
)
UNCHARTABLE_DEFAULT = "no chartable values: expected bars[], series[].pts, panels[], or periods + series[].values"


def to_number(value: Any) -> float | None:
    """A numeric token -> float; bool, None and non-numeric text -> None."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def value_string(value: Any) -> str:
    """The token as written (strings are already verbatim under parse_float=str)."""
    return value if isinstance(value, str) else repr(value)


def decimal_year_label(value: Any) -> str | None:
    """A decimal year (2026.6489) -> "Aug '26"; None when the token is not a plausible year."""
    year = to_number(value)
    if year is None or not (YEAR_RANGE[0] <= year < YEAR_RANGE[1]):
        return None
    whole = int(year)
    month = min(11, int((year - whole) * 12 + 0.01))   # 2026.0833 is February: a four-decimal year puts 0.0833 * 12 at 0.9996, which truncates to January without a hundredth of a month's tolerance (P48 T2)
    return f"{MONTHS[month]} '{whole % 100:02d}"


def display_label(token: Any, index: int, xticks: list | None = None, labels: list | None = None) -> str:
    """The readable label for an x token: an exact xtick, else labels[index], else the year, else the token."""
    x = to_number(token)
    if x is not None:
        for tick in xticks or []:
            if isinstance(tick, (list, tuple)) and len(tick) == 2 and to_number(tick[0]) == x:
                return str(tick[1])
    if isinstance(labels, list) and 0 <= index < len(labels) and _text(labels[index]):
        return str(labels[index])
    return decimal_year_label(token) or str(token)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _points(entry: dict) -> list:
    return [p for p in entry.get("pts") or [] if isinstance(p, (list, tuple)) and len(p) == 2]


def _bars(series: dict) -> list[dict]:
    return [b for b in series.get("bars") or [] if isinstance(b, dict)]


def dense_series(series: dict) -> list[dict]:
    """Every pts-bearing series in the file, panels flattened in."""
    own = [s for s in series.get("series") or [] if isinstance(s, dict) and "pts" in s]
    panels = [s for p in series.get("panels") or [] if isinstance(p, dict)
              for s in p.get("series") or [] if isinstance(s, dict) and "pts" in s]
    return own + panels


def story_data(series: dict) -> tuple[list, list, list]:
    """(labels, raw values, colors) from bars, or from a single series read as one."""
    bars, dense = _bars(series), dense_series(series)
    if bars:
        return ([b.get("label") for b in bars], [b.get("value") for b in bars], [b.get("color") for b in bars])
    if len(dense) == 1:
        pts = _points(dense[0])
        return ([value_string(p[0]) for p in pts], [p[1] for p in pts], [dense[0].get("color")] * len(pts))
    return [], [], []


def race_periods(series: dict) -> list:
    """Declared ``periods``, else the x grid every pts series shares."""
    if series.get("periods"):
        return list(series["periods"])
    grids = [[p[0] for p in _points(s)] for s in dense_series(series)]
    if grids and all(g == grids[0] for g in grids) and len(grids[0]) >= RACE_MIN_PERIODS:
        return grids[0]
    return []


def race_rows(series: dict) -> list[dict]:
    """Race rows {name, values, color}; values from ``values`` or the pts y column."""
    rows = []
    for entry in (s for s in series.get("series") or [] if isinstance(s, dict)):
        values = entry["values"] if "values" in entry else [p[1] for p in _points(entry)]
        rows.append({"name": entry.get("name") or entry.get("label"),
                     "values": list(values or []), "color": entry.get("color")})
    return rows


def pick_builder(series: dict, variant: str) -> str:
    if variant == "object":
        return "object"
    if variant == "share":
        return "share"
    if variant in ("tiers", "treemap"):   # P50 T9 / T6: the file's shape is the variant's own - there is nothing to infer
        return variant
    """Builder from the data shape and the variant (P35 Builder Architecture)."""
    if variant in ("race", "decline"):
        return variant
    dense = dense_series(series)
    if _bars(series) and dense:
        return "combo"
    if len(dense) > 1 or any(len(_points(s)) > STORY_MAX_VALUES for s in dense):
        return "dense-line"
    return "story"


# ---- P58 T5: THE TWO 2.5D CHART FORMS ----------------------------------------------------------------------
# E98 s3: *"bars with extrusion, a line on a tilted plane - the flat page stays the default"*. A FORM is how a
# page's chart is DRAWN, never what it says: the spec, the scale, the labels, the value capsule and the clock
# stay the flat page's, and the only thing that changes is the surface the marks stand on. Both are opt-in
# (`;form=<name>` on the shot row), and a page that names none compiles and paints byte-for-byte as it did.
#   The fit is a BUILDER's, not a variant's, because the builder is what owns the painter: `pick_builder` already
# turns a variant and a data shape into one of nine, and a form its builder cannot draw is refused BY NAME here -
# ONE rule, read by the compiler (which authors the row) and by `validate` (which reads an object naming one).
CHART_FORMS = ("extruded_bar", "tilted_line")
FORM_BUILDERS = {"extruded_bar": ("story",), "tilted_line": ("dense-line",)}
FORM_READS = {"extruded_bar": "a BARS page - every bar is drawn as a prism",
              "tilted_line": "a LINE page - the line is drawn on a tilted plane"}
TILT_DEG = 14.0        # the tilted plane's default turn about the page's own vertical axis, in degrees (E98 s3)
TILT_DEG_MAX = 89.0    # build_scene_timeline_f.PAGE_DEPTH["TILT_MAX"] - one limit, and the compiler checks it


def form_error(form: str, builder: str, where: str) -> str | None:
    """Is ``form`` a form THIS page's builder can draw? The message, or None. Pure."""
    if form not in CHART_FORMS:
        return (f"{where}: form {form!r} is not one of {'|'.join(CHART_FORMS)} "
                "(the two 2.5D chart forms; the flat page is the reading form and names none)")
    fits = FORM_BUILDERS[form]
    if builder not in fits:
        return (f"{where}: form={form} is {FORM_READS[form]}, and this page is built by {builder!r} "
                f"(the form is drawn by {'|'.join(fits)}). The flat page is the reading form - drop the option")
    return None


def validate(series: dict, variant: str) -> list[str]:
    """Error strings; empty means the series is a page for this variant. Pure."""
    errors: list[str] = []
    if series.get("form") is not None:   # P58 T5: an OBJECT naming a form is held to the same one rule the row is
        err = form_error(str(series["form"]), pick_builder(series, variant), "form")
        if err:
            errors.append(err)
    if variant not in VARIANTS:
        errors.append(f"variant {variant!r} is not one of {'|'.join(VARIANTS)}")
    if not _text(series.get("title")):
        errors.append("missing title")
    if not _text(series.get("src")):
        errors.append("missing source line: 'src' is required and is written on the page (s9.26)")
    if series.get("placeholder") is True:   # AGENTS.md: figures are never fabricated - a placeholder never renders
        errors.append("placeholder figures: 'placeholder': true marks values still under SOURCES-TO-VERIFY; a page never renders them")
    if variant == "object":
        return errors + _validate_object(series)
    if variant == "share":
        return errors + _validate_share(series)
    if variant == "tiers":
        return errors + _validate_tiers(series)
    if variant == "treemap":
        return errors + _validate_treemap(series)
    has_race = any(r["values"] for r in race_rows(series))
    if variant != "share" and "shares" in series and not (_bars(series) or dense_series(series)):
        return errors + [UNCHARTABLE["shares"]]
    if not (_bars(series) or dense_series(series) or has_race):
        return errors + [next((v for k, v in UNCHARTABLE.items() if k in series), UNCHARTABLE_DEFAULT)]
    if variant in CHART_VARIANTS:
        errors += _validate_shape_for_variant(series, variant)
    errors += _validate_overflow(series, variant)
    errors += _validate_sign_in_geometry(series)
    errors += badge_key_conflicts(series)
    return errors + _validate_values(series, variant) + _validate_variant(series, variant)


OVERFLOW_MODES = ("burst", "stack", "break")   # E60: burst is THE breakthrough (the rescale), stack an option; "break" is burst's alias
BURST_MODES = ("burst", "break")               # the rescale itself; the stack already steps, so the blend has nothing to add to it
CAPSULE_MODES = ("axis",)                      # P50 T10: the value capsule mounted ON THE AXIS under the bar's end (Bravos 8:02.6);
                                               # absent = the pill above the tip, which stays the default
BREAK_CADENCES = ("stop",)                     # P50 T13 / R26-30 (E60, the operator's blend): the shoot stepped on stopaction's
                                               # cadence rule; absent = the continuous burst, which is the ruled default
PLACEHOLDER_MAX = 3                            # a placeholder is a MARK, not a caption: "?" is the one Bravos uses.
                                               # NOT `placeholder`, which since the intake has meant "these figures are
                                               # still SOURCES-TO-VERIFY and this page never renders" (AGENTS.md: figures
                                               # are never fabricated) - hence the sibling naming, after the mechanic each furnishes


def _validate_overflow(series: dict, variant: str) -> list[str]:
    """E60 (the operator, 2026-09-10: "the re-scale is the way"): a bars page may STATE a scale (`domain`) that ONE value cannot
    fit and name how that bar breaks it (`overflow`). Checked, not trusted: the mechanic is one we have; the scale is stated;
    one bar breaks it; one bar reads on it - a stated scale no bar needs is a lie of the other kind."""
    ovf = series.get("overflow")
    errors: list[str] = []
    # P50 T10 / T13: every piece of furniture belongs to a breakthrough. Declared without one it is a dial nothing
    # reads, which is worse than an error - so it IS one, and it names the key.
    furniture = [k for k in ("overflow_placeholder", "overflow_capsule", "break_cadence") if series.get(k) is not None]
    if ovf is None:
        return errors + [f"{k} is the breakthrough's furniture and this page declares no 'overflow' (E60, P50 T10/T13)"
                         for k in furniture]
    if ovf not in OVERFLOW_MODES:
        errors.append(f"overflow {ovf!r} is not one of {'|'.join(OVERFLOW_MODES)} (E60: burst is the breakthrough, stack an option)")
    if variant != "bars":
        errors.append(f"overflow is a BARS page's device (E60); this page is {variant!r}")
    dom = series.get("domain")
    dom = [to_number(x) for x in dom] if isinstance(dom, list) else None   # floats arrive as their own tokens (load_series parse_float=str)
    if not (isinstance(dom, list) and len(dom) == 2 and all(x is not None for x in dom) and dom[1] > dom[0]):
        errors.append("overflow needs a stated scale: 'domain': [lo, hi] with hi > lo - the scale the honest bar reads on (E60)")
        return errors
    vals = [to_number(b.get("value")) for b in _bars(series)]
    vals = [v for v in vals if v is not None]
    if vals and not any(v > dom[1] for v in vals):
        errors.append(f"overflow declares a breakthrough no bar makes: no value is above the stated scale's top {dom[1]}")
    if vals and not any(v <= dom[1] for v in vals):
        errors.append(f"every bar is above the stated scale's top {dom[1]}: a stated scale no bar reads on is a lie of the other kind (E60)")
    return errors + _validate_burst_furniture(series, ovf)


def _validate_burst_furniture(series: dict, ovf: str) -> list[str]:
    """P50 T10 / T13 - the burst's three options, each off unless the object names it and each checked when it does.
    `overflow_placeholder` is the mark the breaking bar prints until its number is spoken (Bravos 8:01.8: a "?" track);
    `overflow_capsule` mounts the value capsule on the axis with a dotted leader; `break_cadence` steps the shoot on
    stopaction's cadence (E60's blend, R26-30)."""
    errors: list[str] = []
    ph = series.get("overflow_placeholder")
    if ph is not None and ph is not True:
        if not isinstance(ph, str) or not ph.strip():
            errors.append("overflow_placeholder is the MARK the breaking bar prints until its number is spoken: a short string, or true for '?'")
        elif len(ph.strip()) > PLACEHOLDER_MAX:
            errors.append(f"overflow_placeholder {ph!r} is {len(ph.strip())} characters: a placeholder is a mark, not a caption "
                          f"(<= {PLACEHOLDER_MAX}; Bravos stamps '?')")
    cap = series.get("overflow_capsule")
    if cap is not None and cap not in CAPSULE_MODES:
        errors.append(f"overflow_capsule {cap!r} is not one of {'|'.join(CAPSULE_MODES)} (P50 T10: the capsule mounts on the "
                      "AXIS under the bar's end; leave it out for the pill that rides the tip)")
    cad = series.get("break_cadence")
    if cad is not None:
        if cad not in BREAK_CADENCES:
            errors.append(f"break_cadence {cad!r} is not one of {'|'.join(BREAK_CADENCES)} (P50 T13: 'stop' is the blend; "
                          "leave it out for the continuous burst, which E60 ruled the default)")
        elif ovf not in BURST_MODES:
            errors.append(f"break_cadence is the BURST's cadence (E60's blend); this page's overflow is {ovf!r}, which already steps")
    return errors


SIGNED_NOTE_RE = re.compile(r"^\s*[+\u2212-]\s*\d")
MONTH_LABEL_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*'?(\d{2}|\d{4})$")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _validate_share(series: dict) -> list[str]:
    """A share page's contract - E53 s1's amendment, checked rather than trusted. Every failure names the bound it
    broke, because the whole point of writing the exception down was that it not widen by use."""
    errors: list[str] = []
    shares = series.get("shares")
    if not isinstance(shares, list) or len(shares) < 2:
        return ["a share page needs 'shares': at least two slices, the whole they add up to being the page's subject"]
    if len(shares) > SHARE_MAX_SLICES:
        errors.append(f"{len(shares)} slices: E53 s1 allows {SHARE_MAX_SLICES} or fewer ({SHARE_BOUNDS[3]})")
    for i, sh in enumerate(shares):
        if not isinstance(sh, dict):
            errors.append(f"shares[{i}] is not an object"); continue
        if not _text(sh.get("label")):
            errors.append(f"shares[{i}] has no label: a slice is named at its own edge, never in a legend (E53 s8)")
        v = to_number(sh.get("value"))
        if v is None or v <= 0:
            errors.append(f"shares[{i}] value {sh.get('value')!r} is not a positive number: a part of a whole cannot be negative")
    emph = series.get("emphasize")
    if not isinstance(emph, int) or isinstance(emph, bool) or not 0 <= emph < len(shares):
        errors.append(f"a share page must declare 'emphasize': the index of the ONE slice the claim is about ({SHARE_BOUNDS[0]}; {SHARE_BOUNDS[1]})")
    peel = series.get("peel")
    if not isinstance(peel, dict):
        errors.append(f"a share page must declare 'peel': the piece of the named slice the claim is about, with its figure ({SHARE_BOUNDS[2]})")
    else:
        if not _text(peel.get("value_string")):
            errors.append(f"peel.value_string is required: {SHARE_BOUNDS[2]}")
        pv = to_number(peel.get("value"))
        if pv is None:
            errors.append("peel.value must be a number: the size of the piece, signed (a sale is negative - E28)")
        pi = peel.get("index")
        if not isinstance(pi, int) or isinstance(pi, bool) or not 0 <= pi < len(shares):
            errors.append("peel.index must name one of the slices")
        elif isinstance(emph, int) and not isinstance(emph, bool) and pi != emph:
            errors.append(f"peel.index {pi} is not the emphasised slice {emph}: {SHARE_BOUNDS[0]}")
        elif pv is not None:
            whole = to_number(shares[pi].get("value")) or 0.0
            if abs(pv) > whole:
                errors.append(f"peel {pv} is larger than the slice it comes out of ({whole}): a piece cannot exceed its part")
    return errors


# ---- TIERS (P50 T9, R26-24; Bravos shots 35-36) -------------------------------------------------
# N small multiples on ONE page: N bands stacked, each with its own y-scale and its own honest zero
# (E53 s4), sharing ONE x. The tier titles are the series' own names; the page's title stays the
# argument. Two metrics that differ in unit or in magnitude cannot share a y without one of them
# lying; what they can honestly share is the TIME AXIS, which is the comparison being made.
def _tier_entries(series: dict) -> list:
    """The declared tiers, verbatim (an entry that is not an object is kept so the error can name it)."""
    return list(series["tiers"]) if isinstance(series.get("tiers"), list) else []


def _tier_lines(tier: dict) -> list[dict]:
    """A tier's line series: its own ``series`` list, or the ``pts`` shorthand read as one series."""
    if not isinstance(tier, dict):
        return []
    own = [s for s in (tier.get("series") or []) if isinstance(s, dict) and "pts" in s]
    if not own and isinstance(tier.get("pts"), list):
        own = [{k: v for k, v in tier.items() if k not in ("series", "bars", "unit")}]
    return own


def _tier_x(tier: dict) -> tuple | None:
    """This tier's x signature: ``("num", lo, hi)`` for points (or bars carrying their own x),
    ``("cat", labels)`` for category bars. None when the tier has no data to span."""
    xs = [to_number(p[0]) for s in _tier_lines(tier) for p in _points(s)]
    xs += [to_number(b.get("x")) for b in _bars(tier) if b.get("x") is not None]
    xs = [x for x in xs if x is not None]
    if xs:
        return ("num", min(xs), max(xs))
    labels = [str(b.get("label")) for b in _bars(tier)]
    return ("cat", tuple(labels)) if labels else None


def _x_same(a: tuple, b: tuple) -> bool:
    if a[0] != b[0]:
        return False
    if a[0] == "cat":
        return a[1] == b[1]
    span = max(1.0, abs(a[2] - a[1]), abs(b[2] - b[1]))
    return abs(a[1] - b[1]) <= 1e-9 * span and abs(a[2] - b[2]) <= 1e-9 * span


def _x_text(sig: tuple | None) -> str:
    if sig is None:
        return "nothing"
    return f"{sig[1]:g}..{sig[2]:g}" if sig[0] == "num" else "|".join(sig[1])


def _validate_tiers(series: dict) -> list[str]:
    """A tiers page's contract: N in [TIERS_MIN, TIERS_MAX], every band named, united and fed, one
    shared x. Every failure names the band it came from - a page of small multiples is only honest
    while the x is the same x, so that check is the whole point of the builder."""
    tiers = _tier_entries(series)
    if not isinstance(series.get("tiers"), list) or len(tiers) < TIERS_MIN:
        return [f"a tiers page needs 'tiers': a list of at least {TIERS_MIN} bands, each {{name, unit, "
                "series|pts|bars}} - one band is a line page, and `tiers: true` is the two-band COMBO's key, not this"]
    errors: list[str] = []
    if len(tiers) > TIERS_MAX:
        errors.append(f"{len(tiers)} tiers: the ceiling is {TIERS_MAX}. On a 9:16 stage the plot is ~1060 px tall, so "
                      f"{TIERS_MAX} bands leave each about a quarter of it (~250 px) - a band under that cannot carry "
                      "its own scale, its name and a readable line at once. Split the page.")
    sigs: list[tuple] = []
    for i, tier in enumerate(tiers):
        where = f"tiers[{i}]"
        if not isinstance(tier, dict):
            errors.append(f"{where} is not an object"); continue
        name = tier.get("name") or tier.get("title")
        if not _text(name):
            errors.append(f"{where} has no 'name': the tier titles ARE the series' names on a tiers page (the page's title stays the argument)")
        else:
            where = f"tiers[{i}] {name!r}"
        if not _text(tier.get("unit")):
            errors.append(f"{where} has no 'unit': each band carries its own scale, and a scale with no unit is a number with no meaning (E53 s4)")
        lines, bars = _tier_lines(tier), _bars(tier)
        if not lines and not bars:
            errors.append(f"{where} has no data: a band takes 'series'/'pts' ([x, y] pairs) or 'bars'")
        for j, entry in enumerate(lines):
            raw = entry.get("pts") or []
            bad = [p for p in raw if not (isinstance(p, (list, tuple)) and len(p) == 2
                                          and to_number(p[0]) is not None and to_number(p[1]) is not None)]
            if bad or len(raw) < 2:
                errors.append(f"{where} series[{j}] pts must be at least two [x, y] numeric pairs ({len(bad)} bad of {len(raw)})")
        for j, bar in enumerate(bars):
            if to_number(bar.get("value")) is None:
                errors.append(f"{where} bars[{j}] value {bar.get('value')!r} is not numeric")
            if not _text(bar.get("label")):
                errors.append(f"{where} bars[{j}] has no label (one label per datum)")
        sig = _tier_x(tier)
        sigs.append(sig)
        if sig and sigs[0] and not _x_same(sigs[0], sig):
            errors.append(f"{where} spans x {_x_text(sig)} while tiers[0] spans {_x_text(sigs[0])} - N tiers share ONE x "
                          "(that is what makes them small multiples, and the only thing the page claims across bands); "
                          "window the file to one x, or draw two pages")
    return errors


def _tiers_block(series: dict) -> dict:
    """The bands, normalised: one object per tier with its own data, its own unit and its own x span.
    The page's ``labels`` are the tier NAMES, so every count, emphasis and mark keyed off labels reads
    the bands - a tier is the tiers page's datum."""
    out = []
    for tier in _tier_entries(series):
        lines, bars = _tier_lines(tier), _bars(tier)
        sig = _tier_x(tier)
        band: dict[str, Any] = {
            "name": str(tier.get("name") or tier.get("title") or ""),
            "unit": str(tier.get("unit") or ""),
            "kind": "line" if lines else "bars",
            "axes": {k: copy.deepcopy(tier[k]) for k in AXES_KEYS if k in tier},
        }
        if lines:
            band["series"] = copy.deepcopy(lines)
        else:
            band.update({"labels": [b.get("label") for b in bars],
                         "values": [to_number(b.get("value")) for b in bars],
                         "value_strings": [value_string(b.get("value")) for b in bars],
                         "colors": [b.get("color") for b in bars]})
        if tier.get("color") is not None:
            band["color"] = tier["color"]
        if sig and sig[0] == "num":
            band["x"] = [sig[1], sig[2]]
        elif sig:
            band["x_labels"] = list(sig[1])
        out.append(band)
    axes = {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series}
    return {"tiers": out, "labels": [b["name"] for b in out],
            # the page's OWN axes ride at the top level: the x is shared, so its ticks belong to the page
            # and not to any one band (a band that named the x would be claiming the page's only shared scale)
            **({"axes": axes} if axes else {}),
            "values": [], "value_strings": [], "colors": []}


# ---- E79: side-by-side panels of the same measure share one scale (the operator, 2026-09-13) ------
# The defect: each panel computed its own y-range from its own data, so 4.7% drew above 5.0% under a
# subtitle promising one scale. The `panels` form already shares one scale in the engine; a `tiers`
# band computes its own (tierDomain), so this is where same-unit panels can disagree. The compiler
# WARNs; it does not set the domain, because the engine's band reads only its own data.
TIERS_PAD = 0.08   # mirror of TIERS.PAD in scripts/species/tiers.mjs (proportional, so equal raw domains stay equal)


def _declared_domain(axes: dict) -> tuple[float, float] | None:
    dom = axes.get("domain")
    if isinstance(dom, (list, tuple)) and len(dom) == 2:
        lo, hi = to_number(dom[0]), to_number(dom[1])
        if lo is not None and hi is not None and hi > lo:
            return (lo, hi)
    return None


def tier_domain(tier: dict) -> tuple[float, float] | None:
    """One tier's y-domain before padding: its stated `domain`, else its values with the zero kept
    unless `from_zero: false` (tierDomain's rule), widened by any `ymin`/`ymax`. None without data."""
    if not isinstance(tier, dict):
        return None
    stated = _declared_domain(tier)
    if stated:
        return stated
    vals = [to_number(p[1]) for s in _tier_lines(tier) for p in _points(s)]
    vals += [to_number(b.get("value")) for b in _bars(tier)]
    vals += [to_number(tier.get(k)) for k in ("ymin", "ymax") if tier.get(k) is not None]
    nums = [v for v in vals if v is not None]
    if not nums:
        return None
    lo, hi = min(nums), max(nums)
    if tier.get("from_zero") is not False:
        lo, hi = min(0.0, lo), max(0.0, hi)
    return (lo, hi)


def _same_unit_groups(series: dict) -> dict[str, list[tuple[str, tuple[float, float]]]]:
    """unit -> [(tier name, domain)] for every tier that shares a scale: none when the page declares
    `independent`, and a tier that declares it leaves its group."""
    if series.get("independent") is True:
        return {}
    groups: dict[str, list] = {}
    for i, tier in enumerate(_tier_entries(series)):
        if not isinstance(tier, dict) or tier.get("independent") is True or not _text(tier.get("unit")):
            continue
        dom = tier_domain(tier)
        if dom is not None:
            groups.setdefault(str(tier["unit"]), []).append((str(tier.get("name") or tier.get("title") or f"tiers[{i}]"), dom))
    return {u: g for u, g in groups.items() if len(g) >= 2}


def shared_tier_domains(series: dict) -> dict[str, tuple[float, float]]:
    """E79's standard: the ONE domain each same-unit group should share - min and max across its panels. Pure."""
    return {u: (min(d[0] for _, d in g), max(d[1] for _, d in g)) for u, g in _same_unit_groups(series).items()}


def _dom_text(dom: tuple[float, float]) -> str:
    return f"[{dom[0]:g}, {dom[1]:g}]"


def scale_warnings(series: dict) -> list[str]:
    """E79 WARN rows: same-unit panels on different y-domains with no `independent` declared. Pure."""
    page = series.get("id") or series.get("title") or "page"
    shared = shared_tier_domains(series)
    out = []
    for unit, group in _same_unit_groups(series).items():
        if len({(round(lo, 9), round(hi, 9)) for _, (lo, hi) in group}) < 2:
            continue
        panels = "; ".join(f"{name} {_dom_text(dom)}" for name, dom in group)
        out.append(f"E79 {page!s}: panels in {unit!r} carry different y-domains ({panels}) - panels of the same measure "
                   f"share one scale (shared: {_dom_text(shared[unit])}); if these are unrelated measures, declare "
                   "`independent: true` on the page or the tier")
    return out


# ---- TREEMAP (P50 T6; E53 s1's second amendment, the CENSUS exception, ruled 2026-09-10) ---------
# A whole broken into its parts by AREA. Area is the bottom of Cleveland & McGill's hierarchy, which
# is exactly why the exception is narrow: the page shows BREADTH (how many parts there are, and that
# a few of them are most of it) or marks a NAMED SUBSET and WRITES its share - it never asks anyone to
# compare two areas. A size claim takes its bar, and the builder refuses the file that carries one.
TREEMAP_ASPECT = 1.5        # the aspect the squarify tunes toward: 3:2, never 1:1 (Heer & Bostock 2010's square penalty - a square cell reads as a block, a 3:2 cell as a labelled thing)
TREEMAP_MIN_CELL = (80, 36)     # research s1 (ISO 9241-303 at a 30-40 cm handheld distance): under this, NO text - illegible ink blobs overlap and the mosaic reads as noise
TREEMAP_TWO_LINE = (110, 64)    # ... and the floor for two lines (label + value)
TREEMAP_VALUE_FONT = 18         # the absolute legible floor on a 1080x1920 stage; a value that would be written smaller is not written
TREEMAP_LABEL_FONT = (18, 32)   # the label's clamp
TREEMAP_PAD = 6                 # the cell's inner padding at 1080x1920 (research s2: glyph stems never touch a cell edge)
TREEMAP_CHAR_W = 0.72           # the advance the font clamp assumes. The research's own figure is 0.65 em; our cell labels are BOLD, and at 0.65 "Japan" touched its cell's right edge in the rendered frame (2026-09-11)
TREEMAP_LINE_H = {1: 1.5, 2: 2.2}   # the cell height one line of type needs, and two. The research's clamp divides by 2.2 whatever the line count, which contradicts the same document's 36 px single-line floor: at 2.2 a 44 px cell could never carry 18 px type. 2.2 is the TWO-line allowance; one line takes a line and a half
TREEMAP_MIN_SHARES = 3          # two parts of a whole is a share page (one named slice, the rest muted); a census starts at three
# E53 s1: a SIZE CLAIM takes its bar. The page that says "bigger than" is asking for exactly the
# comparison area cannot carry - the refusal names the bars page rather than silently drawing it.
SIZE_CLAIM_RE = re.compile(
    r"\b(bigger|larger|smaller|biggest|largest|smallest|dwarfs?|outweighs?|twice|thrice|triple|tripled|doubles?|doubled"
    r"|more than|less than|(?:\d+(?:\.\d+)?|two|three|four|five|six|seven|eight|nine|ten)\s*(?:x\b|times))\b", re.I)
SIZE_CLAIM_FIELDS = ("title", "sub", "claim")


def _size_claim(series: dict) -> tuple[str, str] | None:
    """(field, phrase) of the first size comparison the page's own words make, or None."""
    for field in SIZE_CLAIM_FIELDS:
        text = series.get(field)
        if not _text(text):
            continue
        hit = SIZE_CLAIM_RE.search(text)
        if hit:
            return field, hit.group(0)
    return None


def _treemap_shares(series: dict) -> list[dict]:
    return [s for s in (series.get("shares") or []) if isinstance(s, dict)]


def _validate_treemap(series: dict) -> list[str]:
    """A treemap page's contract. The census exception's own bounds, checked rather than trusted."""
    shares = series.get("shares")
    if not isinstance(shares, list) or len(shares) < TREEMAP_MIN_SHARES:
        return [f"a treemap page needs 'shares': at least {TREEMAP_MIN_SHARES} parts of one whole "
                "({label, value}) - two parts of a whole is a share page (--variant share), not a census"]
    errors: list[str] = []
    claim = _size_claim(series)
    if claim:
        errors.append(f"the page's {claim[0]} says {claim[1]!r}: a SIZE CLAIM takes its BAR (E53 s1) - area is the bottom of the "
                      "perception hierarchy and two cells of a treemap cannot be compared by eye. Draw the named values as "
                      "--variant bars, and keep the treemap for what it is good at: the census (how many parts, and which "
                      "named ones are struck out with their share written)")
    seen: set[str] = set()
    for i, sh in enumerate(_treemap_shares(series)):
        if not _text(sh.get("label")):
            errors.append(f"shares[{i}] has no label: a cell is named on itself, and an unnamed cell is counted in the legend")
        elif sh["label"] in seen:
            errors.append(f"shares[{i}] {sh['label']!r} is listed twice; one part, one cell")
        else:
            seen.add(sh["label"])
        v = to_number(sh.get("value"))
        if v is None or v <= 0:
            errors.append(f"shares[{i}] value {sh.get('value')!r} is not a positive number: a part of a whole has an area, and an area is positive")
    if len(_treemap_shares(series)) != len(shares):
        errors.append("every entry of 'shares' must be an object {label, value}")
    total = to_number(series.get("total"))
    if series.get("total") is not None and (total is None or total <= 0):
        errors.append(f"total {series.get('total')!r} is not a positive number (the whole the parts are parts of)")
    if total is not None and total > 0:
        summed = sum(to_number(s.get("value")) or 0.0 for s in _treemap_shares(series))
        if summed - total > 1e-6 * max(1.0, total):
            errors.append(f"the parts add up to {summed:g}, more than the declared total {total:g}: a part cannot exceed its whole")
    return errors


def _cost(w: float, h: float, target: float) -> float:
    """A cell's aspect COST against the target (Bruls 2000 s2 with the target left free): 1 at the
    target, growing either side of it. The paper minimises toward a SQUARE; Heer & Bostock 2010 found
    the square penalised in reading tasks and 3:2 the sweet spot, so the target is ours to set."""
    if w <= 0 or h <= 0:
        return float("inf")
    r = (w / h) / target
    return max(r, 1 / r)


def _layout_row(row: list[float], x: float, y: float, dx: float, dy: float) -> list[dict]:
    """One row of cells laid along the rectangle's shorter side, in order (Bruls 2000's `layoutrow`)."""
    covered = sum(row)
    out = []
    if covered <= 0 or dx <= 0 or dy <= 0:
        return out
    if dx >= dy:                      # a wide rectangle: the row stands as a COLUMN down its left edge
        w = covered / dy
        yy = y
        for v in row:
            h = v / w
            out.append({"x": x, "y": yy, "w": w, "h": h}); yy += h
    else:                             # a tall rectangle: the row lies along its top edge
        h = covered / dx
        xx = x
        for v in row:
            w = v / h
            out.append({"x": xx, "y": y, "w": w, "h": h}); xx += w
    return out


def _row_cost(row: list[float], x: float, y: float, dx: float, dy: float, target: float) -> float:
    cells = _layout_row(row, x, y, dx, dy)
    return max((_cost(c["w"], c["h"], target) for c in cells), default=float("inf"))


def squarify(areas: list[float], x: float, y: float, dx: float, dy: float,
             target: float = TREEMAP_ASPECT) -> list[dict]:
    """The squarified treemap (Bruls, Huizing & van Wijk 2000) of `areas` - already scaled to fill
    dx*dy and sorted descending - inside the rectangle. Pure, deterministic, order-preserving: cell i
    is areas[i]. The only departure from the paper is the aspect the rows are tuned toward (3:2)."""
    cells: list[dict] = []
    rest = list(areas)
    row: list[float] = []
    while rest:
        v = rest[0]
        if not row or _row_cost(row + [v], x, y, dx, dy, target) <= _row_cost(row, x, y, dx, dy, target):
            row.append(v); rest.pop(0)
            continue
        cells.extend(_layout_row(row, x, y, dx, dy))
        covered = sum(row)
        if dx >= dy:
            w = covered / dy if dy else 0.0
            x += w; dx -= w
        else:
            h = covered / dx if dx else 0.0
            y += h; dy -= h
        row = []
    cells.extend(_layout_row(row, x, y, dx, dy))
    return cells


def _clamp_font(w: float, h: float, chars: int, lines: int) -> float:
    """The research's dynamic font clamp (findings s2.3), for `lines` lines of `chars` characters."""
    inner_w, inner_h = w - 2 * TREEMAP_PAD, h - 2 * TREEMAP_PAD
    lo, hi = TREEMAP_LABEL_FONT
    return max(0.0, min(hi, inner_w / max(1, chars) / TREEMAP_CHAR_W,
                        inner_h / TREEMAP_LINE_H.get(lines, 2.2 * lines / 2))) if inner_w > 0 and inner_h > 0 else 0.0


def label_tier(w: float, h: float, label: str, value_text: str) -> dict:
    """The three-tier label degradation (research s1 and s5's teardown of Bravos 89-91):
      2 - two lines, the label and its value, both at or above the legible floor;
      1 - ONE stacked line: the label alone;
      0 - none. The cell is a tile and the part is counted in the legend instead.
    The floors are the cell's own size in STAGE pixels; the font clamp is what refuses a long name in
    a cell that is wide enough for a short one."""
    lo = TREEMAP_LABEL_FONT[0]
    if w >= TREEMAP_TWO_LINE[0] and h >= TREEMAP_TWO_LINE[1]:
        chars = max(len(label), len(value_text))
        font = _clamp_font(w, h, chars, 2)
        value_font = max(TREEMAP_VALUE_FONT, round(font * 0.72))
        if font >= lo and value_font >= TREEMAP_VALUE_FONT and (font + value_font) * 1.15 <= h - 2 * TREEMAP_PAD:
            return {"tier": 2, "font": round(font, 1), "value_font": round(float(value_font), 1)}
    if w >= TREEMAP_MIN_CELL[0] and h >= TREEMAP_MIN_CELL[1]:
        font = _clamp_font(w, h, len(label), 1)
        if font >= lo:
            return {"tier": 1, "font": round(font, 1), "value_font": 0.0}
    return {"tier": 0, "font": 0.0, "value_font": 0.0}


def treemap_cells(spec: dict, aspect: str) -> dict:
    """The page's cells inside `page_boxes`'s PLOT for this aspect - never a research doc's container.

    Each cell carries its place as a FRACTION of the plot (so the player maps it into its own viewBox
    without re-deriving the layout - E58: a park is an affine transform, never a re-layout) and the
    stage pixels the label tier was decided on. Pure."""
    plot = page_boxes(spec, aspect)["plot"]
    values = [float(v or 0.0) for v in spec.get("values") or []]
    total = float(spec.get("total") or sum(values) or 1.0)
    area = max(1.0, plot["w"]) * max(1.0, plot["h"])
    order = sorted(range(len(values)), key=lambda i: (-values[i], i))   # squarify takes them largest first; `order` keeps the file's own index
    rects = squarify([values[i] / max(1e-12, sum(values)) * area for i in order],
                     0.0, 0.0, float(plot["w"]), float(plot["h"]))
    cells = []
    for k, i in enumerate(order):
        r = rects[k] if k < len(rects) else {"x": 0.0, "y": 0.0, "w": 0.0, "h": 0.0}
        label = str((spec.get("labels") or [None] * len(values))[i] or "")
        vs = str((spec.get("value_strings") or [None] * len(values))[i] or "")
        share = values[i] / total if total else 0.0
        tier = label_tier(r["w"], r["h"], label, vs)
        cells.append({"index": i, "label": label, "value": values[i], "value_string": vs,
                      "share": round(share, 6),
                      "fx": round(r["x"] / max(1e-9, plot["w"]), 6), "fy": round(r["y"] / max(1e-9, plot["h"]), 6),
                      "fw": round(r["w"] / max(1e-9, plot["w"]), 6), "fh": round(r["h"] / max(1e-9, plot["h"]), 6),
                      "w_px": round(r["w"], 1), "h_px": round(r["h"], 1), **tier})
    unnamed = sum(1 for c in cells if c["tier"] == 0)
    return {"plot": plot, "cells": cells, "unnamed": unnamed,
            # the parts the page could not name are COUNTED, never dropped: the census says how many there were
            "legend": f"and {unnamed} others" if unnamed else ""}


def _treemap_block(series: dict) -> dict:
    """The parts verbatim, in the file's own order; the layout is added per aspect by `build_spec`."""
    shares = _treemap_shares(series)
    total = to_number(series.get("total"))
    summed = sum(to_number(s.get("value")) or 0.0 for s in shares)
    return {"labels": [str(s.get("label")) for s in shares],
            "values": [to_number(s.get("value")) for s in shares],
            "value_strings": [value_string(s.get("value_string", s.get("value"))) for s in shares],
            # a part that names no colour takes NONE: the page's own ramp tiles the mosaic in layout
            # order, which is what gives a census its cell boundaries (a whole map in one token is a blob)
            "colors": [str(s["color"]) if s.get("color") else "" for s in shares],
            "total": total if total is not None else summed,
            **({"total_string": value_string(series["total"])} if series.get("total") is not None else {})}


def _validate_object(series: dict) -> list[str]:
    """An object page's contract. No values, so no sign geometry and no badge keying -
    but a prop that carries a FIGURE still owes a source, because a number drawn in ink
    is as much a claim as a number on an axis."""
    errors: list[str] = []
    props = series.get("props")
    if not isinstance(props, list) or not props:
        return ["an object page needs 'props': a non-empty list of registered prop assets"]
    seen: set[str] = set()
    for i, p in enumerate(props):
        if not isinstance(p, dict):
            errors.append(f"props[{i}] is not an object"); continue
        pid = p.get("asset")
        if not _text(pid):
            errors.append(f"props[{i}] missing 'asset': props are registered, never inline art")
        elif pid in seen:
            errors.append(f"props[{i}] '{pid}' is placed twice; one asset, one placement")
        else:
            seen.add(pid)
        place = p.get("at", "centre")
        if place not in PROP_PLACEMENTS:
            errors.append(f"props[{i}] 'at' {place!r} is not one of {'|'.join(PROP_PLACEMENTS)}")
        if place == "datum" and not isinstance(p.get("index"), int):
            errors.append(f"props[{i}] placed at a datum needs an integer 'index' - "
                          "that is how a prop is positioned RELATIVE TO CHART DATA")
        if _text(p.get("figure")) and not _text(series.get("src")):
            errors.append(f"props[{i}] carries the figure {p['figure']!r} but the page has no source line")
    return errors


def _validate_sign_in_geometry(series: dict) -> list[str]:
    """E28 (operator, 2026-09-03): a chart must read right at a glance - a drop is a bar
    going DOWN. A bar whose value is an unsigned magnitude while its note carries the
    minus sign draws every drop as a rise (the trim proof read as seven rises)."""
    errors = []
    for i, bar in enumerate(_bars(series)):
        note, value = str(bar.get("note") or ""), to_number(bar.get("value"))
        if value is not None and value > 0 and SIGNED_NOTE_RE.match(note) and note.strip()[0] in "-\u2212":
            errors.append(f"bars[{i}] {bar.get('label')!r}: the sign lives in the note ({note.strip()}) while the value "
                          f"({value_string(bar.get('value'))}) is an unsigned magnitude - sign the value so the bar goes down (E28)")
    return errors


def _month_index(label: str) -> int | None:
    m = MONTH_LABEL_RE.match(str(label).strip())
    if not m:
        return None
    year = int(m.group(2))
    year = year + (2000 if year < 100 else 0)
    return year * 12 + MONTHS.index(m.group(1))


def review_notes(series: dict) -> list[str]:
    """JUDGE rows for the operator (CHECK-RESPONSIBILITIES: not a tool's verdict). E28: an
    axis of dates with uneven gaps reads as noise unless the page states the selection
    rule - `selection` in the file, written into the sub. Pure."""
    notes = []
    labels = [b.get("label") for b in _bars(series)]
    idx = [_month_index(x) for x in labels]
    if len(idx) >= 3 and all(i is not None for i in idx):
        gaps = [b - a for a, b in zip(idx, idx[1:])]
        if len(set(gaps)) > 1:
            rule = _text(series.get("selection"))
            notes.append("date axis with uneven gaps (months apart: " + ", ".join(str(g) for g in gaps) + ") - "
                         + (f"selection rule declared: {series['selection']!r}; check the sub says it on the page" if rule
                            else "no `selection` rule in the file: the reader sees noise unless the sub says which dates and why (E28)"))
    return notes


BADGE_ACCENT_TO_SERIES = {"coral": "crimson", "teal": "teal", "cobalt": "cobalt", "ink": "deemph", "sunflower": "amber"}


KEY_STOP = {"THE", "OF", "A", "AND", "STOCKS", "STOCK", "SHARE", "PRICE", "PRICES", "INDEX", "MARKET"}


def _key_tokens(text: str) -> set[str]:
    return {w.strip("()+,:;.'\"").upper() for w in str(text or "").split()} - KEY_STOP - {""}


def badge_key_conflicts(series: dict, extra: list | None = None) -> list[str]:
    """E28 addendum (operator, 2026-09-03: the +613% line was labelled MEGA-CAP TECH while
    its badge said MEMORY BUILDERS): a badge's label must name the line its accent keys.
    A badge word that appears in ANOTHER series' name and not in the keyed one is a swap."""
    errors = []
    dense = dense_series(series)
    for b in (series.get("badges") or []) + list(extra or []):
        col = BADGE_ACCENT_TO_SERIES.get(str(b.get("accent") or ""))
        keyed = [s for s in dense if s.get("color") == col]
        if not col or not keyed:
            continue
        words = _key_tokens(b.get("label"))
        mine = _key_tokens(keyed[0].get("name"))
        for other in dense:
            if other is keyed[0]:
                continue
            hit = (words & _key_tokens(other.get("name"))) - mine
            if hit:
                errors.append(f"badge {b.get('label')!r} ({b.get('accent')}) keys the {col} line {keyed[0].get('name')!r} "
                              f"but names the {other.get('color')} line {other.get('name')!r} ({', '.join(sorted(hit))}) - a swapped label (E28)")
    return errors


def badges_for(series: dict, extra: list | None = None) -> list[dict]:
    """The page's badges (operator, 2026-09-03: 'we need the badges back - that's how we were
    quickly conveying information and applying a key for the viewer'): the file's own
    ``badges`` plus any handed in from the evidence dock, each {label, value, tag, accent}.
    BADGE-CHART SYNC (build_scene_timeline_f, 2026-08-30): a badge whose accent maps to a
    series colour takes that series' CURRENT label as its value, so the pill never drifts
    from the line it keys. Pure."""
    raw = [b for b in (series.get("badges") or []) + list(extra or []) if isinstance(b, dict)]
    out = []
    for b in raw:
        bd = {"label": str(b.get("label") or ""), "value": str(b.get("value") or ""),
              "tag": str(b.get("tag") or ""), "accent": str(b.get("accent") or "sunflower")}
        col = BADGE_ACCENT_TO_SERIES.get(bd["accent"])
        for entry in dense_series(series):
            if col and entry.get("color") == col and _text(entry.get("label")):
                bd["value"] = str(entry["label"]).split()[0]
        # a badge that keys a dense series becomes that line's DYNAMIC LABEL (operator, 2026-09-03:
        # 'grouped below the chart, or dynamic labels - not label + pill + captions on one real estate')
        bd["inline"] = bool(col) and any(e.get("color") == col for e in dense_series(series))
        out.append(bd)
    return out


def _validate_shape_for_variant(series: dict, variant: str) -> list[str]:
    """The REQUESTED variant must have data of its own shape: a chartable file is not
    a page for every variant (a race file asked for bars would build an empty page)."""
    builder = pick_builder(series, variant)
    if builder in ("story", "decline", "progress") and not story_data(series)[1]:
        return [f"variant {variant!r} needs story values (bars, or one short series); this file has none - pick the variant its shape supports"]
    if builder == "dense-line" and not dense_series(series):
        return [f"variant {variant!r} needs a dense series ([x, y] points); this file has none"]
    if builder == "combo" and not (_bars(series) and dense_series(series)):
        return ["combo needs both bars and a dense series"]
    return []


def _validate_values(series: dict, variant: str) -> list[str]:
    """Numeric values, one label per datum, named series, [x, y] pairs, story ceiling."""
    errors, bars = [], _bars(series)
    for i, bar in enumerate(bars):
        if to_number(bar.get("value")) is None:
            errors.append(f"bars[{i}] value {bar.get('value')!r} is not numeric")
        if not _text(bar.get("label")):
            errors.append(f"bars[{i}] has no label (one label per datum)")
    if bars and pick_builder(series, variant) == "story" and len(bars) > STORY_MAX_VALUES:
        errors.append(f"story shape carries {len(bars)} values; the ceiling is {STORY_MAX_VALUES}")
    for i, entry in enumerate(dense_series(series)):
        if not (_text(entry.get("label")) or _text(entry.get("name"))):
            errors.append(f"series[{i}] has neither label nor name (s9.23b: series are named inline)")
        raw = entry.get("pts") or []
        bad = [p for p in raw if not (isinstance(p, (list, tuple)) and len(p) == 2
                                      and to_number(p[0]) is not None and to_number(p[1]) is not None)]
        if bad or not raw:
            errors.append(f"series[{i}] pts must be [x, y] numeric pairs ({len(bad)} bad of {len(raw)})")
    return errors


def _validate_variant(series: dict, variant: str) -> list[str]:
    """Race needs periods; decline one metric with two ends; progress a bounded share."""
    errors: list[str] = []
    if variant == "race":
        periods = race_periods(series)
        if len(periods) < RACE_MIN_PERIODS:
            return [f"race needs periods: a 'periods' list of >= {RACE_MIN_PERIODS}, or series sharing one x grid"]
        for i, row in enumerate(race_rows(series)):
            if not _text(row["name"]):
                errors.append(f"series[{i}] has no name for the race")
            if len(row["values"]) != len(periods):
                errors.append(f"series[{i}] has {len(row['values'])} values for {len(periods)} periods")
            if any(to_number(v) is None for v in row["values"]):
                errors.append(f"series[{i}] race values must all be numeric")
    if variant == "decline":
        metrics = (1 if _bars(series) else 0) + len(dense_series(series))
        if metrics != 1:
            return [f"decline takes exactly one metric (a single series or one bars list); found {metrics}"]
        if len(story_data(series)[1]) < DECLINE_MIN_VALUES:
            return [f"decline needs a start and an end (>= {DECLINE_MIN_VALUES} values); found {len(story_data(series)[1])}"]
    if variant == "progress":
        labels, raw, _colors = story_data(series)
        if not raw:
            return ["progress needs story values (bars or one short series)"]
        denominator = to_number(series.get("denominator"))
        ceiling = denominator if denominator and denominator > 0 else PROGRESS_MAX
        bound = (f"0..{value_string(series['denominator'])} (denominator)" if denominator
                 else f"0..{PROGRESS_MAX} and no denominator is given")
        for label, value in zip(labels, raw):
            number = to_number(value)
            if number is None or number < 0 or number > ceiling:
                errors.append(f"progress value {value_string(value)} at {label!r} is outside {bound}")
    return errors


def build_spec(series: dict, variant: str, emphasize: int | None = None,
               quiet_zone: str = "right", builder: str | None = None) -> dict:
    """The page spec; pure and deterministic - the input dict is never mutated. `builder` forces the page's builder
    (P48 T2: a derived rescale state keeps the PAGE's builder even when its window holds too few points to read as dense)."""
    if quiet_zone not in QUIET_ZONES:
        raise ValueError(f"quiet_zone must be one of {'|'.join(QUIET_ZONES)}")
    builder = builder or pick_builder(series, variant)
    spec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "surface": "page", "builder": builder,
        "variant": variant, "title": series.get("title"), "sub": series.get("sub", ""),
        "source": series.get("src"), "quiet_zone": quiet_zone,
        **({"src_style": series["src_style"]} if series.get("src_style") in ("compact",) else {}),   # the design pass (2026-09-07): a citation takes minimal space
        **({"line_unit": series["line_unit"]} if isinstance(series.get("line_unit"), str) else {}),   # P47 T9: a combo's lines take their own right axis in this unit
        **({"legend_in_sub": True} if series.get("legend_in_sub") else {}),   # the sub names the lines by colour: no inline name (it would repeat and collide)
        **({"tiers": True} if series.get("tiers") is True else {}),   # the macro-chart intake: bars and lines in two bands sharing one x, each on its own scale (a `tiers` LIST is the N-tier builder below, not this key)
        **({"build_s": float(to_number(series["build_s"]))} if to_number(series.get("build_s")) is not None and to_number(series["build_s"]) > 0 else {}),   # load_series decodes floats as their own tokens (parse_float=str): 1.2 arrives as "1.2", so the number is read, not the type   # the page draws over its own seconds
        "labels": [], "values": [], "value_strings": [], "colors": [],
    }
    if builder == "object":
        spec.update(_object_block(series))
        spec["unit"] = ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        spec["emphasize"] = None
        return spec
    if builder == "share":
        spec.update(_share_block(series))
        spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        spec["emphasize"] = int(series.get("emphasize") if emphasize is None else emphasize)
        return spec
    if builder in ("tiers", "treemap"):
        spec.update(_tiers_block(series) if builder == "tiers" else _treemap_block(series))
        warnings = scale_warnings(series) if builder == "tiers" else []
        if warnings:   # only when there is one: an untroubled page's spec stays byte-identical
            spec["warnings"] = warnings
        spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        count = len(spec["labels"])
        spec["emphasize"] = None if emphasize is None or not count else max(0, min(int(emphasize), count - 1))
        if builder == "treemap":
            # the layout is computed HERE, at build time, in page_boxes' own plot - both aspects, because the
            # page does not know which stage it will be read on and a treemap laid out at paint time is a
            # re-layout waiting to happen (E58 / Sondag 2018: a park is one affine transform)
            spec["layout"] = {aspect: treemap_cells(spec, aspect) for aspect in STAGE_PX}
        return spec
    if builder == "race":
        spec.update(_race_block(series))
    elif builder == "dense-line":
        spec.update(_dense_block(series))
    else:
        spec.update(_story_block(series))
    if builder == "combo":
        spec.update({k: v for k, v in _dense_block(series).items() if k != "labels"})
    if builder == "decline":
        spec.update(_decline_block(series, spec))
    if variant == "progress" and "denominator" in series:
        spec["denominator"] = value_string(series["denominator"])
    spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
    spec["judge"] = review_notes(series)
    spec["badges"] = badges_for(series)
    count = len(spec["labels"])
    spec["emphasize"] = None if emphasize is None or not count else max(0, min(int(emphasize), count - 1))
    return spec


def _object_block(series: dict) -> dict:
    """Props, normalised. `at: "datum"` keeps its index so the renderer can resolve the
    prop against a chart datum - the same resolveTarget the callout and spotlight species
    already use, which is what lets an object be manipulated in relation to data."""
    props = []
    for p in series.get("props") or []:
        if not isinstance(p, dict):
            continue
        entry = {"asset": p.get("asset"), "at": p.get("at", "centre")}
        for k in ("index", "figure", "label", "scale", "draw_s", "enters_at"):
            if p.get(k) is not None:
                entry[k] = p[k]
        props.append(entry)
    return {"props": props, "labels": [], "values": [], "value_strings": [], "colors": []}


def _share_block(series: dict) -> dict:
    """The slices verbatim, plus the peel. E53 s1(b): every slice but the claim's is muted context, so a slice that
    declares no colour takes the de-emphasis token rather than a series accent it did not ask for."""
    shares = series.get("shares") or []
    emph = series.get("emphasize")
    peel = dict(series.get("peel") or {})
    return {"labels": [str(s.get("label")) for s in shares],
            # a wedge is narrow: a slice may name itself short for the page and keep its full name for the record
            "short_labels": [str(s.get("short") or s.get("label")) for s in shares],
            "values": [to_number(s.get("value")) for s in shares],
            "value_strings": [value_string(s.get("value_string", s.get("value"))) for s in shares],
            "colors": [str(s.get("color") or ("crimson" if i == emph else "deemph")) for i, s in enumerate(shares)],
            "peel": peel}


def _decline_block(series: dict, spec: dict) -> dict:
    """start/end verbatim, display_labels readable; a dense-series decline keeps its axes."""
    dense = dense_series(series)
    axes = _dense_block(series)["axes"] if dense else {}
    labels = series.get("labels") if isinstance(series.get("labels"), list) else None
    ends, displays = {}, {}
    for key, i in (("start", 0), ("end", len(spec["labels"]) - 1)):
        token = spec["labels"][i]
        ends[key] = {"label": token, "value": spec["values"][i], "value_string": spec["value_strings"][i]}
        displays[key] = display_label(token, i, axes.get("xticks"), labels) if dense else str(token)
    displays["series"] = (dense[0].get("name") or dense[0].get("label")) if dense else None
    return {**ends, "display_labels": displays, **({"axes": axes} if dense else {})}


def _story_block(series: dict) -> dict:
    labels, raw, colors = story_data(series)
    # a BARS page carries its axes too, so it can declare a comparator rule (`hlines`) - the device that lets the
    # GAP between a reference and a taller bar be drawn instead of subtracted (E53 s6, operator 2026-09-08)
    axes = {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series}
    return {"labels": list(labels), "values": [to_number(v) for v in raw],
            "value_strings": [value_string(v) for v in raw], "colors": list(colors),
            **({"axes": axes} if axes else {})}


def _dense_block(series: dict) -> dict:
    # P48 T3: a series marked `later: true` waits off the page - an `extend` derives the state that draws it on
    return {"labels": [s.get("name") or s.get("label") for s in dense_series(series) if not s.get("later")],
            "series": copy.deepcopy([s for s in (series.get("series") or []) if not (isinstance(s, dict) and s.get("later"))]),
            "axes": {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series}}


def _race_block(series: dict) -> dict:
    rows = race_rows(series)
    return {"periods": copy.deepcopy(race_periods(series)), "labels": [r["name"] for r in rows],
            "values": [[to_number(v) for v in r["values"]] for r in rows],
            "value_strings": [[value_string(v) for v in r["values"]] for r in rows],
            "colors": [r["color"] for r in rows]}


# ---- PAGE GEOMETRY (ruling E45 §1, 2026-09-06) ------------------------------------------------
# "The placement is computed from the page's own geometry by the compiler, not hand-placed per
# shot." The page's boxes live in the PLAYER (the template lays a portrait page out top-down in
# stage px and a landscape page in fractions of the board), so this is a READ-ONLY MIRROR of that
# layout: the same constants, the same order of operations, reported in stage pixels so the
# compiler can park a dock clear of the ink. It adds an accessor and changes no existing output -
# `build_spec` is untouched and the golden frames stay pinned.
#
# The one thing the template does that Python cannot is MEASURE the handwriting. Title, sub and
# source wrap at run time in Kalam; here they are wrapped greedily with an average advance
# calibrated against the rendered golden page (bold 0.52 em, regular 0.44 em - the golden's
# 3-line title, 2-line sub and 1-line source all reproduce). A page whose ink lands one line off
# the estimate shifts these boxes by one line height, which is why the dock placement leaves a pad
# and parks against the PLOT's edge (protecting the chart, per E45) rather than the title's.
STAGE_PX = {"16:9": (1920, 1080), "9:16": (1080, 1920)}
# doc 49 §49.1 / doc 50: platform chrome covers the top 280, the bottom 480 and the right 200 of a
# 1080x1920 short; everything that must be read lives in x[80,880] y[280,1340].
SAFE_BOX = {"9:16": (80, 280, 800, 1060), "16:9": (64, 64, 1792, 814)}
# the anchored caption's strip - a dock demotes the caption to it, so a dock may never sit there
CAPTION_ANCHOR = {"9:16": (80, 1290, 800, 150), "16:9": (145, 878, 1630, 82)}
PORTRAIT_LAYOUT = {"TOP": 150, "X": 80, "W": 800, "TITLE_W": 920, "BOTTOM": 1280, "GAP": 24, "CHART_MIN": 320}
PORTRAIT_INK = {"title": (68, 1.12, 0.52, 920), "sub": (40, 1.25, 0.44, 800), "src": (40, 1.25, 0.44, 800)}
PORTRAIT_PLOT = {"L": 150, "R": 70, "T": 90, "B": 80}
PORTRAIT_PILL_H, PORTRAIT_PILLS_PER_ROW = 132, 3   # the badge rail's row height and how many fit 800px
YLABEL_H = 52          # axes.ylabel floats top-left INSIDE the plot (template: lpYLabel at T-12)
XTICK_H = 62           # the x tick labels hang below the axis line (y = B + 52, 40px type)
LAND_BOARD = (0.06, 0.08, 0.88, 0.84)   # s9.26 default board; the punch crops to 1/PUNCH_SCALE
PUNCH_SCALE = 1.16
LAND_PLOT = {"L": 0.070, "R": 0.220, "T": 0.071, "B": 0.839}   # dense-line margins / the 1000x560 viewBox

# ---- THE PAGE IS THE PLATE AT 16:9 (R26-205 / E99 s82, 2026-09-18) ----------------------------
# The operator, on a bare frame of the H unit's copy d: *"why is the ledger being used at like 20%
# size? the whole point of a ledger plate is that the chart IS the world, you have it restricted to
# this square even when bare, it should be the whole plate."* Measured: the bare page's plot was
# `[180, 236, 403, 244]` of a 1920x1080 stage - 21 % of the stage's width - because the landscape
# chart box is `(0.6 if quiet_zone else 0.9) * cb.w`: a COLUMN was kept for the stage caption
# (`build_scene_timeline_f.caption_strip_x`) and for the card that lands in the quiet zone.
#
# At 16:9 a page that carries `full_stage` takes this box instead, and its caption goes to the
# anchored strip (`CAPTION_ANCHOR["16:9"]`), where it can never be in the plot's column. The numbers
# are in RENDERED stage fractions - the punch is already in them - because every one of them was
# read off a frame:
# THE BOX CARRIES THE viewBox's OWN ASPECT (1000:560), so the chart is drawn at the box's size with
# no letterbox and this estimate is exact. Its four numbers are the largest box whose THREE feet all
# land on the stage - each measured on the served player, not reasoned about:
#   (1) THE END TAGS. The dense-line species writes each series' name BESIDE its last point, inside
#       the chart's own units, so the tag grows with the chart. Measured on the `ledger-page-mid-build`
#       golden (the longest names and tags in the repo - "+613% MEMORY MAKERS (hynix+Micron) our
#       layer"): the widest ends `LAND_TAG_REACH` of the chart's own width from its left edge. The
#       first pass put the box on the whole stage and those tags ran 305 px off the right of the
#       frame (measured). So `X + LAND_TAG_REACH * W <= 0.979` - the stage less a hair - which is what
#       caps W at 1334 px. X is not free either: at X = 0.010 the y tick column landed 36 px outside
#       the 16:9 SAFE_BOX, and every pixel X gains costs `LAND_TAG_REACH` of W.
#   (2) THE X TICK LABELS clear the anchored caption. Their foot is `LAND_TICK_B` of the box's own
#       height, so 197 + 0.911 * 747 = 878 - level with `CAPTION_ANCHOR["16:9"]`'s top, and 39 px
#       clear of the caption's own one-line box, which sits at the strip's FOOT (measured: y 919-960).
#   (3) THE SOURCE LINE clears the strip's foot. Written `LAND_SRC_GAP` under the box, it runs
#       959-1000, under the strip's 960 - which is where the landscape source line sits today.
# (2) and (3) pull against each other (a taller box drops the ticks into the strip, a shorter one
# lifts the source into it): together they hold the box's height inside 4 px, and Y is the value that
# satisfies both. Nothing here is free to be rounded.
#
# MEASURED on the `ledger-page-mid-build` golden at 16:9, t = 20 s (the served player, the probe
# `measure_page_boxes.READ_BOXES`): the plot goes 784 -> 966 px, 40.8 % -> 50.3 % of the stage width;
# the widest end tag ends at 1896 of 1920; the y tick column starts at x 67, inside the safe box; the
# x ticks' foot is 880 against the caption's box at 919; the source line runs 967-1008, under it.
#
# WHAT THIS DOES NOT REACH, and the arithmetic, because the row asked for 70 % of the stage: the plot
# is `(1 - L - R) = 0.710` of the chart, so 1344 px of plot needs a chart 1893 px wide and - at this
# aspect - 1060 px tall, which is the whole stage. Two things stand in the way and neither is this
# row's: the inline END TAG would need portrait's treatment (right-anchored above the line's end,
# `buildLedgerLine`'s `P` branch) instead of its own column, and the chart's viewBox would have to
# follow the box's aspect rather than letterbox inside it, which is seven landscape builders' own
# absolute margins. R26-205-NOTE.md carries the table.
LAND_FULL = {"X": 0.0300, "Y": 0.1824, "W": 0.6948, "H": 0.6917}
LAND_TAG_REACH = 1.365   # how far past the chart's own left edge the widest end tag reaches, in chart widths [MEASURED: ledger-page-mid-build at 16:9, the tag at x 1006-1638 with the chart drawn 1105 wide from x 131]
# THE END TAG COLUMN, per page. `LAND_TAG_REACH` is the RENDERED worst case and sizes the BOX; this
# sizes the page's OWN column, so a card is refused the room this page's names actually take and no
# other.
#
# TWO ADVANCES, because the element is TWO type sizes: the series' NAME in the big bold, then the
# badge's tag in its own smaller type (E22's dynamic label - one reveal, one real estate). One advance
# cannot bound both: fitted on a short mixed-case name alone it is 14.8 units a glyph, on an all-caps
# name 18.8, and on a name diluted by a long badge tag 13.0 - so a single number either puts a card on
# a name or keeps it off half the stage. These two are an UPPER BOUND on every tag measured, which is
# the side to be wrong on [MEASURED at 16:9 on the dense-line golden's own four tags and on a short-name
# page: (34 name, 9 tag) 561 units, (26, 16) 554, (25, 18) 560, (25, 10) 411, (12, 0) 178; this model
# gives 691, 574, 565, 525, 228]. The column starts `LAND_TAG_GAP` past the last datum
# (`buildLedgerLine` writes the name at `mx(last) + 12`). Only the builders that write an inline end
# name have a column at all.
LAND_TAG_NAME_U, LAND_TAG_BADGE_U, LAND_TAG_GAP = 19.0, 5.0, 12
LAND_TAG_BUILDERS = ("dense-line", "combo")
BADGE_ACCENT_COL = {"coral": "crimson", "teal": "teal", "cobalt": "cobalt", "ink": "deemph", "sunflower": "amber"}
"""A badge's accent -> the SERIES COLOUR it keys: the mirror of the engine's `LP_BADGE_COL`, one law in
two languages. An inline badge rides that series' end name inside the same element (the dynamic label,
E22: one reveal, one real estate), so the compiler cannot size the tag column without it."""


def tag_units(spec: dict) -> float:
    """The widest inline end name this page will write, in the chart's own 1000 units.

    Per series: `<label> <name>` as `buildLedgerLine` composes it, at `LAND_TAG_NAME_U` a glyph, plus
    the tag of the INLINE BADGE that keys it (matched by `BADGE_ACCENT_COL`, as the player matches it)
    at `LAND_TAG_BADGE_U`. 0 when this page's builder writes no inline name, or when every series is
    muted history (which carries none)."""
    if str(spec.get("builder")) not in LAND_TAG_BUILDERS:
        return 0.0
    rides = {BADGE_ACCENT_COL.get(str(b.get("accent"))): str(b.get("tag") or "")
             for b in spec.get("badges") or [] if b.get("inline")}
    out = 0.0
    for s in spec.get("series") or []:
        if s.get("muted"):
            continue
        tag = rides.get(str(s.get("color")), "")
        name = ((s.get("label") or "") + " " + (s.get("name") or "")).strip()
        out = max(out, len(name) * LAND_TAG_NAME_U + (len(tag) + 1) * LAND_TAG_BADGE_U if tag
                  else len(name) * LAND_TAG_NAME_U)
    return out
# the x tick labels' FOOT as a fraction of the chart's viewBox height: the line builder writes them
# at `B + 52` of its 560 units and they are 40 px type, so 510/560 - read off the dense-line entry
# (plot bottom 806 with the chart drawn from y 258.5 at scale 1.083: (806 - 258.5) / 1.083 = 506).
LAND_TICK_B = 0.911
# the RENDERED heights of the landscape page's ink, off the dense-line entry's measured boxes (the
# type is the template's and does not move with the chart box): a one-line title, sub and source,
# and one badge row. `_landscape_boxes` models the CSS box and leaves the punch to the player; the
# full-stage branch reports what the FRAME holds, so these are the punched numbers.
LAND_FULL_INK = {"title": 63, "sub": 30, "src": 41, "pill": 56}
LAND_SRC_GAP, LAND_RAIL_GAP = 0.012, 0.044   # the source / rail tops under the chart box (the engine's own 1.2 % / 4.4 %)


def _punch_pt(f: float) -> float:
    """A point's RENDERED stage fraction from its CSS one.

    The punch (E22 addendum 6) scales the page by `PUNCH_SCALE` about the BOARD's centre, which for
    the s9.26 default board is the stage's own centre - so a page that declares its own `board` or
    `chart_box` (a host plate) is never a full-stage page and never comes through here."""
    return 0.5 + (f - 0.5) * PUNCH_SCALE


def full_stage(spec: dict, aspect: str) -> bool:
    """Does this page's chart fill the STAGE (R26-205)? 16:9 only, and never a HOST PLATE.

    The compiler stamps `full_stage` on a 16:9 ledger page row; a page that declares its own
    `board`, `chart_box` or `punch: False` is a host plate whose board was measured around a hand
    (`proofs/ledger/derive_host_boards.py`), so its chart box is the host's and not the stage's."""
    return bool(spec.get("full_stage")) and aspect == "16:9" and not (
        spec.get("board") or spec.get("chart_box") or spec.get("punch") is False)


def _ink_lines(text: str, size_px: float, box_w: float, advance: float) -> int:
    """Greedy word wrap at `advance` ems per character - the line count the page will write."""
    words = str(text or "").split()
    if not words:
        return 0
    char, lines, run = size_px * advance, 1, 0.0
    for word in words:
        want = len(word) * char
        if run and run + char + want > box_w:
            lines, run = lines + 1, want
        else:
            run = run + char + want if run else want
    return lines


def _ink_height(text: str, key: str) -> float:
    size, line_h, advance, box_w = PORTRAIT_INK[key]
    return _ink_lines(text, size, box_w, advance) * size * line_h


def first_clause(text: str, sentence: bool) -> str:
    """The portrait copy rule, mirrored: the sub keeps its first clause (to ';' or the first
    sentence end), the source its first clause (to ';') - one column has no room for the rest."""
    value = str(text or "")
    cuts = [i for i in (value.find(";"), value.find(". ") if sentence else -1) if i > 0]
    if not cuts:
        return value
    i = min(cuts)
    return value[: i + (1 if value[i] == "." else 0)].strip()


def _box(x: float, y: float, w: float, h: float) -> dict:
    return {"x": round(x), "y": round(y), "w": round(w), "h": round(h)}


TIER_GAP = 0.20   # the gutter between two bands, as a share of a band's own height [DERIVED, read off the first frame: at 0.10 a band's NAME sat on the floor tick label of the band above it; 0.20 is one line of type between them and still leaves four bands ~230 px each on a 9:16 plot]


def tier_bands(plot: dict, n: int) -> list[dict]:
    """The N band boxes inside a tiers page's plot, top to bottom, in stage pixels.

    The MIRROR of `tierBands` in scripts/species/tiers.mjs - one law in two languages, the same two
    dials, pinned on both sides (test_ledger_page and tests/kinetics/tiers.test.mjs). The compiler
    needs it to park a dock clear of a band; the player needs it to draw one."""
    if n < 1:
        return []
    h = plot["h"] / (n + (n - 1) * TIER_GAP)
    return [_box(plot["x"], plot["y"] + i * h * (1 + TIER_GAP), plot["w"], h) for i in range(n)]


def _portrait_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    P, PL = PORTRAIT_LAYOUT, PORTRAIT_PLOT
    title_h = _ink_height(spec.get("title"), "title")
    sub_h = _ink_height(first_clause(spec.get("sub"), True), "sub")
    src_h = _ink_height(first_clause(spec.get("source"), False), "src")
    rail = [b for b in spec.get("badges") or [] if not b.get("inline")]
    rail_h = PORTRAIT_PILL_H * -(-len(rail) // PORTRAIT_PILLS_PER_ROW) if rail else 0
    sub_top = P["TOP"] + title_h + 16
    chart_top = sub_top + sub_h + P["GAP"] + 8
    chart_h = max(P["CHART_MIN"], P["BOTTOM"] - chart_top
                  - (src_h + P["GAP"] if src_h else 0) - (rail_h + P["GAP"] if rail_h else 0))
    src_top = chart_top + chart_h + P["GAP"]
    plot_top = chart_top + PL["T"] - (YLABEL_H if (spec.get("axes") or {}).get("ylabel") else 0)
    plot_bot = chart_top + chart_h - PL["B"] + XTICK_H
    return {
        "title": _box(P["X"], P["TOP"], P["TITLE_W"], title_h),
        "sub": _box(P["X"], sub_top, P["W"], sub_h),
        "chart": _box(P["X"], chart_top, P["W"], chart_h),
        "plot": _box(P["X"] + PL["L"], plot_top, P["W"] - PL["L"] - PL["R"], plot_bot - plot_top),
        "source": _box(P["X"], src_top, P["W"], src_h),
        "rail": _box(P["X"], src_top + (src_h + P["GAP"] if src_h else 0), P["W"], rail_h),
    }


def _landscape_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    bx, by, bw, bh = LAND_BOARD
    half = 0.5 / PUNCH_SCALE
    vx, vy = bx + bw / 2 - half, by + bh / 2 - half
    rx, ry = max(bx, vx), max(by, vy)
    rw, rh = min(bx + bw, vx + 2 * half) - rx, min(by + bh, vy + 2 * half) - ry
    cx, cy, cw, ch = rx + 0.03 * rw, ry + 0.15 * rh, 0.94 * rw, 0.74 * rh
    qz = spec.get("quiet_zone")
    chart_w = (0.6 if qz else 0.9) * cw
    chart_x = cx + (0.4 if qz == "left" else 0.05) * cw
    L = LAND_PLOT
    return {
        "title": _box(max(bx + 0.027, vx + 0.03) * w_s, max(by + 0.024, vy + 0.035) * h_s, chart_w * w_s, 46),
        "sub": _box(chart_x * w_s, (max(by + 0.024, vy + 0.035) + 0.056) * h_s, chart_w * w_s, 54),
        "chart": _box(chart_x * w_s, cy * h_s, chart_w * w_s, ch * h_s),
        "plot": _box((chart_x + L["L"] * chart_w) * w_s, (cy + L["T"] * ch) * h_s,
                     (1 - L["L"] - L["R"]) * chart_w * w_s, (L["B"] - L["T"]) * ch * h_s + 40),
        "source": _box(chart_x * w_s, (cy + ch + 0.012) * h_s, chart_w * w_s, 32),
        "rail": _box(chart_x * w_s, (cy + ch + 0.044) * h_s, chart_w * w_s, 48),
    }


def _landscape_full_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    """R26-205: the 16:9 page whose CHART IS THE WORLD - its boxes in RENDERED stage pixels.

    `_landscape_boxes` models the page's CSS box and leaves the punch to the player, which is why its
    estimate of a chart box is `PUNCH_SCALE` short of the frame's. Every number here is where the
    FRAME puts it: the chart box is declared in rendered fractions (`LAND_FULL`) and the page's ink
    is carried through `_punch_pt`, so these boxes can be read straight against a probe.

    The plot is a fraction of the DRAWN chart, not of the box: the chart's SVG is 1000x560 under the
    default preserveAspectRatio, so it is fit inside the box and centred (the same letterbox
    `treemap_plot` has had to do since P50 T9), and the box's spare width is air."""
    bx, by, bw, bh = LAND_BOARD
    half = 0.5 / PUNCH_SCALE
    vx, vy = bx + bw / 2 - half, by + bh / 2 - half
    F, L, I = LAND_FULL, LAND_PLOT, LAND_FULL_INK
    cx, cy, cw, ch = F["X"] * w_s, F["Y"] * h_s, F["W"] * w_s, F["H"] * h_s
    # the title and the sub keep the places they have always had at 16:9 - the same two CSS
    # expressions the engine writes - read through the punch. The ink's own column is the title's,
    # as the 9:16 page's one column is (`PORTRAIT_LAYOUT["X"]`): nothing is aligned to the chart's
    # letterbox, which moves with the data's shape.
    ink_x = _punch_pt(max(bx + 0.027, vx + 0.03)) * w_s
    title_y = _punch_pt(max(by + 0.024, vy + 0.035)) * h_s
    sub_y = _punch_pt(max(by + 0.024, vy + 0.035) + 0.056) * h_s
    ink_w = cx + cw - ink_x
    src_y = cy + ch + LAND_SRC_GAP * PUNCH_SCALE * h_s
    rail = [b for b in spec.get("badges") or [] if not b.get("inline")]
    vw, vh = LAND_VIEWBOX
    s = min(cw / vw, ch / vh)
    ox, oy = cx + (cw - vw * s) / 2, cy + (ch - vh * s) / 2
    ylab = YLABEL_H if (spec.get("axes") or {}).get("ylabel") else 0
    return {
        "title": _box(ink_x, title_y, ink_w, I["title"]),
        "sub": _box(ink_x, sub_y, ink_w, I["sub"]),
        "chart": _box(cx, cy, cw, ch),
        "plot": _box(ox + L["L"] * vw * s, oy + L["T"] * vh * s - ylab,
                     (1 - L["L"] - L["R"]) * vw * s, (LAND_TICK_B - L["T"]) * vh * s + ylab),
        "source": _box(ink_x, src_y, ink_w, I["src"]),
        "rail": _box(ink_x, cy + ch + LAND_RAIL_GAP * PUNCH_SCALE * h_s, ink_w,
                     I["pill"] * -(-len(rail) // PORTRAIT_PILLS_PER_ROW) if rail else 0),
        # the END TAG COLUMN: the page's own inline names, beside the plot and part of the chart's ink.
        # It was air while a quiet zone kept the chart to 60 % of its board; at full stage it is the
        # only thing between the plot and the frame, so `free_bands` has to know it is there.
        "tags": _box(ox + (1 - L["R"]) * vw * s + LAND_TAG_GAP * s, oy + L["T"] * vh * s,
                     tag_units(spec) * s, (L["B"] - L["T"]) * vh * s),
    }


LAND_VIEWBOX = (1000, 560)   # the landscape chart's viewBox; a portrait chart's viewBox IS its pixel box (the template: "builders draw in stage px")


def treemap_plot(chart: dict, aspect: str) -> dict:
    """The rect a TREEMAP's cells are laid out in: the page's own plot margins inside the chart box,
    with the landscape viewBox's LETTERBOX applied.

    Every other builder can live with this module's estimate of where the ink lands, because being a
    line out is a line out. A treemap cannot: its layout is tuned to the plot's ASPECT, and a plot
    estimated at 1.19 when the player will draw at 1.65 turns every squarified cell into a strip and
    scales its label with it (read off the first rendered frame, 2026-09-11). The landscape chart's
    viewBox is 1000x560 with the default preserveAspectRatio, so it is scaled to FIT the chart box and
    centred in it; the page's plot margins are then the line builder's own."""
    if aspect == "9:16":
        P = PORTRAIT_PLOT
        return _box(chart["x"] + P["L"], chart["y"] + P["T"], chart["w"] - P["L"] - P["R"], chart["h"] - P["T"] - P["B"])
    vw, vh = LAND_VIEWBOX
    s = min(chart["w"] / vw, chart["h"] / vh)
    ox, oy = chart["x"] + (chart["w"] - vw * s) / 2, chart["y"] + (chart["h"] - vh * s) / 2
    L = LAND_PLOT
    return _box(ox + L["L"] * vw * s, oy + L["T"] * vh * s,
                (1 - L["L"] - L["R"]) * vw * s, (L["B"] - L["T"]) * vh * s)


# ---- ONE PLACEMENT TRUTH (P50 T16, R26-27) -------------------------------------------------
# Everything above this line is an ESTIMATE of where the player will put the page's ink. The layout
# LAW in `_portrait_boxes` is the template's own, line for line (measured 2026-09-11: given the ink
# heights, the chart's top, the plot's L/R/T/B and the source line all land on the player's pixel).
# What Python cannot see is the INK: `_ink_lines` wraps at an average advance, and a title the
# player writes in ONE line is estimated at two - which moves every box under it by 76 px on a 9:16
# page. That is R26-27 exactly ("the x maths is exact, only y is off").
#
# THE FIXTURE. `measure_page_boxes.py` renders a representative page per builder per aspect in the
# headless player and writes what it MEASURES to `assets/page-boxes.v1.json`. A page's boxes are a
# pure function of its INK - the builder, the title, the sub's and the source's first clause, the
# rail's badge count, the basis label and the quiet zone are the ONLY inputs `_portrait_boxes` and
# `_landscape_boxes` read - so `page_ink_key` hashes exactly that, and a measured entry is valid for
# any page carrying the same ink, and for no other page at all. A page whose ink is not on file
# keeps today's estimate and SAYS so: `boxes["measured"]` is False and the compiler writes one line
# per estimated page into the build's report. The truth is never guessed - either the player's own
# numbers are on file for this ink, or the caller knows it is holding an estimate.
_REPO = Path(__file__).resolve().parents[3]
PAGE_BOXES_FIXTURE = _REPO / "content/video_engine/assets/page-boxes.v1.json"
PAGE_BOXES_SCHEMA = "page_boxes.v1"
BOX_KEYS = ("title", "sub", "chart", "plot", "source", "rail")
TAGS_KEY = "tags"   # R26-205: the end tag column, on a full-stage page only (the fixture measures the six above)
INK_KEYS = ("builder", "title", "sub", "source", "quiet_zone")


def page_ink_key(spec: dict) -> str:
    """The fingerprint of everything about `spec` that moves a box: its ink, its rail and its zone.

    Two pages with the same key lay out identically at a given aspect - the DATA never moves a box,
    it is drawn inside the plot - so one measurement serves both. Stable across runs and machines."""
    rail = [b for b in spec.get("badges") or [] if not b.get("inline")]
    ink = {
        **{k: spec.get(k) for k in INK_KEYS},
        "sub_clause": first_clause(spec.get("sub"), True),
        "src_clause": first_clause(spec.get("source"), False),
        "rail_n": len(rail),
        "ylabel": (spec.get("axes") or {}).get("ylabel"),
        "tiers_n": len(spec.get("tiers")) if isinstance(spec.get("tiers"), list) else 0,
    }
    blob = json.dumps(ink, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


@functools.lru_cache(maxsize=4)
def _doc(path: str, mtime: float) -> dict:
    """The whole fixture document. A missing or malformed file reads as empty: the fixture is a
    measurement the compiler may not have, never a dependency it fails on. `mtime` is in the cache
    key so a re-measurement inside one process is seen."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("schema") != PAGE_BOXES_SCHEMA:
        return {}
    return data


def _section(name: str, path: Path | None = None) -> dict:
    p = Path(path or PAGE_BOXES_FIXTURE)
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return {}
    section = _doc(str(p), mtime).get(name)
    return section if isinstance(section, dict) else {}


def fixture(path: Path | None = None) -> dict:
    """builder -> aspect -> entry, from `assets/page-boxes.v1.json` (or `path`): ONE representative
    page per builder, the fallback for any page carrying that representative's ink."""
    return _section("builders", path)


def measured_pages(path: Path | None = None) -> dict:
    """ink key -> aspect -> entry: the pages a PROJECT's compiled timeline named, measured one by
    one (`measure_page_boxes.py --project`). A builder has one representative but an episode has as
    many pages as it writes titles, so the pages an episode actually compiles are keyed by ink."""
    return _section("pages", path)


def measured_entry(spec: dict, aspect: str) -> dict | None:
    """The fixture entry that measured THIS page's ink at this aspect, or None.

    The ink-keyed `pages` section first (this very page, measured by name), then the per-builder
    representative - either way the entry is used only when its `ink` is this page's own."""
    # R26-205: a FULL-STAGE page lays out nothing like the same ink in the old landscape box, so it is
    # never served a measurement of that box. The refusal is HERE and not in `page_ink_key`, because
    # the flag is not INK - it is a geometry the same ink takes at ONE aspect, and the key does not
    # know the aspect. (It was in the key for one round, and it re-keyed every 9:16 page any caller
    # stamped with the compiler's ASPECT unset: the Tokyo cut's measured pages fell back to the
    # estimate and E65's placer lost the plot's own room - `test_dock_over_build.py` caught it.)
    if full_stage(spec, aspect):
        return None
    key = page_ink_key(spec)
    entry = (measured_pages().get(key) or {}).get(aspect)
    if not isinstance(entry, dict):
        entry = (fixture().get(str(spec.get("builder"))) or {}).get(aspect)
    if not isinstance(entry, dict) or entry.get("ink") != key:
        return None
    return entry


def measured_boxes(spec: dict, aspect: str) -> dict | None:
    """The player's own boxes for THIS page's ink, or None when nothing on file measured it."""
    entry = measured_entry(spec, aspect)
    boxes = (entry or {}).get("boxes")
    if not isinstance(boxes, dict) or not all(k in boxes for k in BOX_KEYS):
        return None
    return {k: dict(boxes[k]) for k in BOX_KEYS}


def measured_room(spec: dict, aspect: str) -> dict:
    """E65's room, for a page the fixture has measured: ``data_mask`` (16 rows of 16 characters over
    the PLOT, `1` where the data's ink touches the cell) and ``axis`` (the x tick labels' band under
    the plot, the y tick column beside it - furniture a card MAY partially overlap, unlike the data).

    ``{}`` when this page is not measured or was measured before E65: the placer then has boxes but
    no room, and falls back to the bands outside the plot exactly as it did before."""
    entry = measured_entry(spec, aspect) or {}
    mask = entry.get("data_mask")
    axis = entry.get("axis")
    out: dict = {}
    if isinstance(mask, list) and mask and all(isinstance(r, str) and len(r) == len(mask) for r in mask):
        out["data_mask"] = list(mask)
    if isinstance(axis, dict):
        out["axis"] = {k: (dict(v) if isinstance(v, dict) else None) for k, v in axis.items() if k in ("x", "y")}
    return out


def page_boxes(spec: dict, aspect: str = "16:9") -> dict:
    """Where this page puts its ink, in STAGE pixels (E45 §1).

    Keys: ``stage``/``safe``/``caption_anchor`` (the frame's own bands) and ``title``/``sub``/
    ``chart``/``plot``/``source``/``rail`` (the page's), each ``{x, y, w, h}``; ``quiet_zone``
    passes the spec's declared side through. ``plot`` is the DATA box plus the ink that lives
    inside it - the basis label above it (``axes.ylabel``) and the x tick labels below the axis -
    because a card over either of them covers the chart just as surely.

    ``measured`` says whose numbers these are (P50 T16): True when the fixture holds the player's
    own boxes for this page's INK (`measured_boxes`), False when this is `_portrait_boxes`' estimate.
    A measured page also carries ``data_mask`` and ``axis`` - E65's room INSIDE the plot.
    A caller that PLACES something by these boxes - `free_bands`, `page_place`, `centred_place` - is
    reading one truth or the other, and the compiler reports which for every page it compiles.

    Pure and deterministic; the spec is never mutated. An `object` page (no chart) reports the
    prop's field as its chart and an empty plot."""
    if aspect not in STAGE_PX:
        raise ValueError(f"aspect must be one of {'|'.join(STAGE_PX)}")
    w_s, h_s = STAGE_PX[aspect]
    # R26-205: at 16:9 a page stamped `full_stage` puts its chart on the whole stage, so its boxes
    # come from the full-stage law rather than from the board's inner box with a column kept out
    boxes = (_portrait_boxes if aspect == "9:16" else
             _landscape_full_boxes if full_stage(spec, aspect) else _landscape_boxes)(spec, w_s, h_s)
    if spec.get("builder") == "object":
        boxes["plot"] = _box(boxes["chart"]["x"], boxes["chart"]["y"], 0, 0)
    if spec.get("builder") == "tiers":
        boxes["bands"] = tier_bands(boxes["plot"], len(spec.get("tiers") or []))
    if spec.get("builder") == "treemap":
        boxes["plot"] = treemap_plot(boxes["chart"], aspect)
    measured = measured_boxes(spec, aspect)
    if measured:                      # the player's own numbers for this ink win over every estimate above
        tags = boxes.get(TAGS_KEY)    # ... except the end tag column, which the fixture does not measure
        boxes.update(measured)
        if tags is not None:
            boxes[TAGS_KEY] = tags
        boxes.update(measured_room(spec, aspect))   # E65: the plot's empty room and the axis bands travel with them
        if spec.get("builder") == "tiers":   # the tier bands are a law over the PLOT: re-cut them on the measured one
            boxes["bands"] = tier_bands(boxes["plot"], len(spec.get("tiers") or []))
    sx, sy, sw, sh = SAFE_BOX[aspect]
    cx, cy, cw, ch = CAPTION_ANCHOR[aspect]
    return {"aspect": aspect, "stage": _box(0, 0, w_s, h_s), "safe": _box(sx, sy, sw, sh),
            "caption_anchor": _box(cx, cy, cw, ch), "quiet_zone": spec.get("quiet_zone"),
            "measured": bool(measured), **boxes}


def load_series(path: Path) -> dict:
    """Decode with parse_float=str so every float stays the file's own token."""
    data = json.loads(path.read_text(encoding="utf-8"), parse_float=str)
    if not isinstance(data, dict):
        raise ValueError("top level must be a JSON object")
    return data


def infer_variant(series: dict) -> str | None:
    """The variant this file's SHAPE names, or None when it is the author's call (`--check` alone).

    Only the unambiguous shapes: a `tiers` LIST is a tiers page, `props` an object page, `shares` the
    census (treemap) unless the file declares the donut's `peel`. A bars/pts file is a line page, a
    bars page, a decline or a progress page depending on what the SENTENCE does with it - which is
    not in the file, so it is never guessed."""
    if isinstance(series.get("tiers"), list):
        return "tiers"
    if isinstance(series.get("props"), list) and series["props"]:
        return "object"
    if isinstance(series.get("shares"), list):
        return "share" if series.get("peel") is not None else "treemap"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="series.json -> ledger page spec (doc 29 s9.26)")
    parser.add_argument("series", help="the ev-*.series.json beside the asset")
    parser.add_argument("--variant", default=None, choices=VARIANTS)   # `share` is the donut exception; see SHARE_BOUNDS
    parser.add_argument("--check", action="store_true",
                        help="validate only - nothing is written, and the variant may be left to the file's own shape")
    parser.add_argument("--emphasize", type=int, default=None, help="index of the emphasized datum")
    parser.add_argument("--quiet-zone", default="right", choices=QUIET_ZONES, help="where docks land (s9.28 B3)")
    parser.add_argument("--out", default=None, help="spec path; default <name>.page.json beside the input")
    args = parser.parse_args(argv)
    path = Path(args.series)
    try:
        series = load_series(path)
    except (OSError, ValueError) as exc:
        print(f"ledger_page: cannot read {path}: {exc}", file=sys.stderr)
        return EXIT_INVALID
    variant = args.variant or infer_variant(series)
    if variant is None:
        print(f"ledger_page: {path}: name the variant (--variant {'|'.join(VARIANTS)}) - "
              "this file's shape does not name one on its own", file=sys.stderr)
        return EXIT_INVALID
    errors = validate(series, variant)
    if errors:
        print(f"ledger_page: {path} is not a page ({variant}):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return EXIT_INVALID
    spec = build_spec(series, variant, args.emphasize, args.quiet_zone)
    for note in spec.get("judge", []):
        print(f"  [JUDGE] {note}")
    for warning in spec.get("warnings", []):
        print(f"  [WARN] {warning}")
    if args.check:   # a check writes nothing: it says what the file IS a page of, and what the page will carry
        extra = (f" {len(spec['tiers'])} tiers sharing x" if spec["builder"] == "tiers" else
                 f" {len(spec['labels'])} cells, {spec['layout']['16:9']['unnamed']} unnamed (16:9)" if spec["builder"] == "treemap" else
                 f" {len(spec['labels'])} values")
        print(f"OK {path.name}: {spec['builder']} {variant}{extra} source={spec['source']!r}")
        return 0
    stem = path.name[: -len(".series.json")] if path.name.endswith(".series.json") else path.stem
    out = Path(args.out) if args.out else path.with_name(f"{stem}.page.json")
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    count = (sum(len(_points(s)) for s in spec.get("series", []))
             + sum(len(v) if isinstance(v, list) else 1 for v in spec["values"]))
    print(f"{spec['builder']} {spec['variant']} {count} values source={spec['source']!r} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
