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
           (P69 T8d: a value may be a RANGE [lo, hi] - the bar at its near end, a band to the far one, written "lo–hi")
           (P69 T45: a bar may carry "members": [{"name", "logo"?, "short"?}] - equal tiles naming who is in its ONE
           value, the page's "member_noun" writing what a tile is: "each tile = one company")
           (P69 T64: a bar may carry "segments": [{"name", "value", "value_string"?, "color"?}] - a stack of VALUES that
           sums to the bar's written total, one key per page; any other bar key is refused by name, BAR_FIELDS)
           (P72 T13: "unit": "$" + "unit_suffix": "B" writes "$480B" on the value, the ticks and the pill; a word unit
           takes a space, "20 years" - `with_unit`, the engine's lpWithUnit)
  combo   story bars + ONE pts series; with segments, "line_unit" (+ "line_label", "ylabel") gives the line its own axis
  dense    {"series": [{"label"|"name", "color", "pts": [[x, y], ...]}], + AXES_KEYS}
           or {"panels": [{"sub", "series": [...]} | {"sub", "builder": "bars", "unit", "bars": [...]}]}
           (P70 T4: a panel may name its "measure"; one measure in two units is an E79 / E53 s4 WARN)
  tiers    {"tiers": [{"name", "unit", "series"|"pts"|"bars", + AXES_KEYS}], + AXES_KEYS}
           E79: same-unit tiers share ONE scale by default; ``independent: true`` (on the page, or on
           one tier) declares unrelated measures on their own scales. Undeclared same-unit tiers on
           different y-domains are a WARN (``spec["warnings"]``, printed ``[WARN]``) - see scale_warnings.
  race     {"periods": [...], "series": [{"name", "values": [...], "color"?}]}
           (or dense series sharing one x grid of >= RACE_MIN_PERIODS points)
  decline  exactly one metric (a single dense series, or bars of >= DECLINE_MIN_VALUES);
           first and last are the endpoints
  progress story values in 0..PROGRESS_MAX, or non-negative with a numeric "denominator"
Rejected clearly: "checklist" (a table). "shares" (a part-to-whole) has no bars or points to draw for the other
  variants and is ROUTED to `share` (a pie or a donut) or `treemap` - P69 T50 / E99 s100: a form is judged by its
  honesty (every area true, the figures written), never refused by type; a finding is a `WARN form:` line (s106).
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
import math
import re
import sys
from numbers import Real
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
# P69 T8b (E99 s104, amended twice): a `panels` object - the format the card's `chart_dock:panels` already draws - is
# a PAGE of 2-4 plots, each its own chart (its sub, its axes, its end tags), one scale across them by default (E79;
# `independent: true` gives each its own). The builder is `panels`; each panel is drawn by the dense-line builder
# inside its own box, and the boxes move by FOCUS STATES (`panel_focus`, the compiler's) - see `panel_layout`.
PANELS = "panels"
PANELS_MIN, PANELS_MAX = 2, 4
# P69 T8d (E99 s104 amended x2): a panel names its BUILDER - `line` (the default: T8b's panel) or `bars` (row 21's wafer
# ratio and its contract prices) - and a bar's value may be a RANGE `[lo, hi]` (the source says "+55-60%"): the bar
# stands at lo, a lighter band runs lo -> hi, and the page writes the range as the source states it, never a midpoint.
PANEL_LINE, PANEL_BARS = "line", "bars"
PANEL_BUILDERS = (PANEL_LINE, PANEL_BARS)
BARS_PAD = 0.14   # the bars builder's own air on the side away from zero (the engine's `pad = (hi0 - lo0) * 0.14`)
RANGE_DASH = "–"   # a range is written lo<en dash>hi ("+55-60%" in the source, "+55–60%" on the page)
REPRESENTATIVE_SEP = "+"   # page-boxes.v1.json: a builder's SECOND representative is filed `<builder>+<shape>` (T8d: panels+bars)
# `treemap` (P50 T6): the CENSUS page, under E53 s1's second amendment (ruled 2026-09-10).
# `object` is the page as a WORKING surface rather than an evidence surface: it draws
# a registered prop in ink on the cream instead of a chart. Same page clock, same
# deckle, same focus - so an object page can transform into a chart page without a
# plate change (RULE-the-page-is-the-ground, 2026-09-04).
PROP_PLACEMENTS = ("centre", "left", "right", "datum")
QUIET_ZONES = ("left", "right")
LANDSCAPE_PHONE = "landscape-phone"
# P69 T8 (E99 s97): the LONG FORM's page, measured off Bravos's frames (`docs/research/bravos-style/
# BRAVOS-LONGFORM-CHART-SPEC.md` (b)) - a flat ground, a framed plot panel, no gridlines, Inter - set in one of
# three named type presets (`longform:bravos|middle|phone`, LONGFORM_TYPE_SCALE below); on a dense-line page it
# widens the chart the way T17 does, for its own end tags.
LONGFORM = "longform"
READABILITY_PROFILES = (LANDSCAPE_PHONE, LONGFORM)
# E99 s122 amended (P69 T37c): THE DEFAULT (shorts) PAGE'S TITLE FACE - the one token the operator's pick changes.
# `hand` Kalam 700 (today; Kalam's heaviest weight), `heavy` Kalam 700 thickened by an ink stroke, `sans` the long
# form's Inter 700. The compiler stamps it on the timeline (`title_face`) only when it is not `hand`, so a `hand`
# build is byte-identical; `sans` also ships the long form's face (build_scene_timeline_f.longform_assets). The long
# form's own title is Inter already and never takes it.
TITLE_FACES = ("hand", "heavy", "sans")
TITLE_FACE = "hand"
# P71 T30 (the Bravos harvest v2's S10 and S11; was P69 T78): TWO LONG-FORM CHROME OPTIONS on the series file - each an
# option and never a default, each the long form's alone (refused by name off it: `_validate_longform_chrome` for the
# file, `readability_error` for a row that draws the page in another profile). `source_lines` is the two-line source
# (BRAVOS-LONGFORM-CHART-SPEC.md (b) `source: {lines: ["Date: ...", "Source: ..."]}`; STK 04:14, BOOM, D40): two lines
# written as two, which between them carry the page's `src` and each projection's source, so the page still cites
# what its provenance says. `title_style: capsule` is the title in the page's accent capsule (D40 04:16, measured:
# 304 x 79 px round 45 px of type - pad 17 v / 22 h, a ~2 px corner - so its pads are ems of the title's own size;
# BOOM's capsules are its SUBTITLES', a finding, not built). The engine's LP_TITLE_CAPSULE is TITLE_CAPSULE_EM.
SOURCE_LINES_KEY = "source_lines"
SOURCE_LINES_N = 2
TITLE_STYLE_KEY = "title_style"
TITLE_STYLES = ("capsule",)
TITLE_CAPSULE_EM = {"pad_v": 0.37, "pad_h": 0.48, "radius": 0.05}
# ... and their ROOM (found on the frame: the long fixture at `longform:phone` with both options drew its chart box 99 px
# tall, the plot a strip and the end tags on each other). Each option takes height from the chart; past this share of
# the chart box the page carries a WARN with its numbers (s106: the author's call - drop one, or a smaller preset).
# The share is ours to tune, set off the fixture's own M28 read (no reference measures it): at `middle` the capsule
# takes 4 % and M28 is clean; at `phone` the capsule alone takes 22 % and the end tags already meet (M28 FAIL), the two
# lines 33 %, both 55 % - so a sixth is the line.
CHROME_WARN = "WARN chrome:"
CHROME_ROOM_SHARE = 0.15
# the builders each profile is legal on (T14's inventory: the body's pages are dense-line and bars/`story`)
READABILITY_BUILDERS = {LANDSCAPE_PHONE: ("dense-line",), LONGFORM: ("dense-line", "story", PANELS)}   # P69 T8b: a panels page, each panel framed
AXES_KEYS = ("overflow", "log", "ylabel", "xticks", "from_zero", "highlight_from", "hlines", "hline", "marks", "eventbars",
             "name_clear",   # lift the inline series name clear of the data it would otherwise be written across
             "readability",  # R26-? closed, page-scoped chart typography/geometry profile
             "left_gutter",  # native story-bars y-axis reservation; absent preserves legacy geometry
             "ymin", "ymax", "yfmt", "yunit", "panels",
             "domain", "xdomain",   # P48 T2: a derived rescale state names its exact y domain and x window
             "overflow_placeholder", "overflow_capsule", "break_cadence",   # P50 T10 / T13: the breakthrough's furniture (E60)
             "independent",   # E79: this page (or this tier) carries unrelated measures, each on its own scale - nothing implies one
             "break")   # P69 T66 / E99 s111: one x axis across two eras, cut where no datum is and the cut drawn (`_validate_break`)
UNCHARTABLE = {
    "checklist": "no chartable values: 'checklist' is a table, not a chart (keep it a dock)",
    # P69 T50 (E99 s100, s109 (5)): a part-to-whole is no longer refused as a TYPE - this variant simply has nothing to
    # draw it with (a `shares` object carries no bars and no points), so the message ROUTES it to the two forms that do
    "shares": ("'shares' is a part-to-whole - a pie, a donut or a treemap - and this variant draws bars or lines, which "
               "the file does not carry: draw it as --variant share (a pie or a donut, flat or 3D: every angle true to "
               "its share, the figures written) or --variant treemap (every area true to its value, the figures the "
               "claim turns on written). E53 s1's perception hierarchy is guidance on which form reads fastest, not a "
               "refusal (E99 s100)"),
}
# P69 T50 / E99 s100 (amends E53 s1): "the donut's and the treemap's four-point exceptions are superseded by those two
# tests" - every angle true to its share, and the figures the claim turns on WRITTEN. SHARE_MAX_SLICES is no longer a
# bound: it is the count a reader names at a glance, and a page past it is REPORTED with its numbers (s106,
# `share_honesty_warnings`). SHARE_BOUNDS keeps the words the flat pie's own fields cite (its emphasised slice, its peel).
SHARE_MAX_SLICES = 5
FORM_WARN = "WARN form:"   # the prefix of every honesty finding a page reports (the compiler prints it as a [WARN] line)
SHARE_BOUNDS = (
    "a part-to-whole claim about ONE named slice, never a ranking or a comparison across slices",
    "that slice highlighted, every other slice muted context",
    "the figure the claim turns on WRITTEN on the page, so no angle has to be estimated",
    f"{SHARE_MAX_SLICES} slices or fewer",
)
# P69 T48 / E99 s109 (4) + its amendment: THE SOLID SHARE PAGE - a pie or a DONUT (`hole`), flat or EXTRUDED with a tilt
# (`extrude`: a 2.5D projection of the TRUE-ANGLE slices), one slice EXPLODED out of the whole (`explode`; the `explode`
# page species says when). Truthful by s100's two tests: every angle is the slice's share of the whole, whatever the
# tilt, and every slice's figure is WRITTEN on it - the number, not the area, is the claim. A page naming none of these
# keys is the P48 T4 pie, byte for byte (its `peel` and its one written figure).
SHARE_SOLID_KEYS = ("hole", "extrude", "explode")
PIE_HOLE_MAX = 0.75         # a donut's hole as a share of the radius: past three quarters the ring is a hairline, not a slice
PIE_TILT_DEG = 50           # the default tilt, degrees back from face-on - see PIE_AREA_LIE_MAX for why it is no steeper
PIE_TILT_RANGE = (10, 60)   # under 10 the tilt reads as a mistake; past 60 the top is a sliver and the near rim dominates
PIE_DEPTH = 0.12            # the extrusion's thickness, a share of the radius (in the pie's own plane, before the tilt)
PIE_DEPTH_RANGE = (0.02, 0.30)
PIE_EXPLODE_OUT = 0.14      # how far the exploded slice leaves, a share of the radius along its own bisector [DERIVED: clear of
                            # its neighbours' names, still obviously OF the whole - the peel's own 0.17 less a margin for the rim]
PIE_EXPLODE_RANGE = (0.04, 0.30)
# THE HONESTY MEASURE. Under the orthographic tilt every TOP face scales by cos(tilt) alike, so the tops keep their true
# proportions; what a tilt adds is the RIM, and only the near half of it - so a slice at six o'clock owns a strip the far
# slices do not. The worst factor any slice's apparent area (top + visible rim) reads against its share is a thin slice
# at six o'clock: (1 + q) / (1 + q / pi), q = 2 depth tan(tilt); the far slice reads 1 / (1 + q / pi) of its share.
# PIE_AREA_LIE_MAX is what a WRITTEN figure carries: perceived area grows about as area^0.7 (Stevens' exponent for
# area), so 1.2 in area reads as ~1.14 - a 39 % slice read as ~44 % with "39%" written on it, which the figure corrects
# at a glance. The default tilt/depth (50 deg, 0.12) is 1.18; a page past the bound is REPORTED with its number (s106).
PIE_AREA_LIE_MAX = 1.2
# the shares must sum to their whole within the WRITTEN figures' own rounding: half a unit of the finest decimal place,
# per slice (three thirds written 33 % each are 99, not a missing 1 %)
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


# ---- P69 T8d: a bar's value may be a RANGE [lo, hi] -------------------------------------------------------------------
def _is_range(value: Any) -> bool:
    """A bar value written as a list: a RANGE (checked by `bar_value_errors`)."""
    return isinstance(value, (list, tuple))


def bar_range(bar: dict) -> tuple[float, float] | None:
    """(lo, hi) of a bar whose value is a well-formed RANGE `[lo, hi]`; None for a single value or a malformed one."""
    v = bar.get("value") if isinstance(bar, dict) else None
    if _is_range(v) and len(v) == 2:
        lo, hi = to_number(v[0]), to_number(v[1])
        if lo is not None and hi is not None:
            return (lo, hi)
    return None


def range_foot(lo: float, hi: float) -> float:
    """The value a range's BAR is drawn to - the end NEAREST ZERO, the part every source guarantees (lo for a rise, hi
    for a fall: a range never straddles zero); the band runs from it to the far end."""
    return hi if hi <= 0 else lo


def range_string(bar: dict) -> str:
    """The range as the source states it: its two tokens, verbatim, joined by an en dash ("+55" and "60" -> "+55–60")."""
    lo, hi = bar["value"]
    return f"{value_string(lo)}{RANGE_DASH}{value_string(hi)}"


def bar_value_errors(where: str, bar: dict, unit: str) -> list[str]:
    """One bar's value: a number, or an honest RANGE - [lo, hi] (two numbers, lo <= hi), on one side of zero (E28: the
    sign is geometry, and a range across zero has none), and a unit (the range is WRITTEN, and "55-60" is not a
    figure). The single-value message is the one it always was."""
    v = bar.get("value")
    if not _is_range(v):
        return [] if to_number(v) is not None else [f"{where} value {v!r} is not numeric"]
    rng = bar_range(bar)
    if rng is None:
        return [f"{where} value {list(v)!r}: a RANGE is [lo, hi] - two numbers, as the source states them (P69 T8d)"]
    lo, hi = rng
    errors = []
    if lo > hi:
        errors.append(f"{where} range {list(v)!r} runs backwards: lo {lo:g} > hi {hi:g} - a range is [lo, hi] (P69 T8d)")
    if lo < 0 < hi:
        errors.append(f"{where} range {list(v)!r} straddles zero: a bar's side of the zero line IS its sign (E28), and "
                      "this range has none - draw the two ends as two bars, or state the range in words")
    if not _text(unit):
        errors.append(f"{where} range {list(v)!r} has no unit: the page writes the range as the source states it "
                      "('+55–60%'), and a range without its unit is not a figure (P69 T8d)")
    return errors


# ---- P69 T45 (E99 s101; s109 (2)): THE MEMBERSHIP STACK - equal tiles naming who is in ONE bar ---------------------
# s101: "A bar may be filled with EQUAL tiles naming who is in it (logos, names) when the bar is ONE value, the tiles carry
# no value of their own (equal height, never sized), and the bar's total is written on the page" - Bravos's AI hidden-debt
# bar with its company tiles. It reads as MEMBERSHIP, not as segments to compare. A member is a NAME, and - where the
# operator's catalogue carries that member's own mark - a `logo`: a catalogue id the compiler resolves (E94; 11-ARCHIVAL
# s4: "Logos and organization marks require recorded permission; otherwise use text"). The page WRITES what a tile is
# ("each tile = one company"), so no one reads a tile as a value. A stack of VALUES is the stacked bar (`segments`, P69
# T64, s110 (1)) - never this form, and a member that carries a value is refused here by name.
MEMBERS_KEY = "members"
MEMBER_NOUN_KEY = "member_noun"
MEMBER_NOUN_DEFAULT = "member"
MEMBER_KEY_TEXT = "each tile = one {noun}"
MEMBER_FIELDS = ("name", "logo", "short")
MEMBER_VALUE_FIELDS = ("value", "values", "share", "shares", "weight", "size", "pct", "percent", "amount", "height",
                       "count", "total", "segments")
# [DERIVED] two to eight: one member is a label, not a set; past eight a full-height bar on the 16:9 page (a 556 px plot,
# the bar at its 88 % after the builder's 14 % air) leaves a tile under 61 px - under one line of a name at the phone
# floor (59 px) - and a count that large is the count array's to show (species:count_array)
MEMBERS_MIN, MEMBERS_MAX = 2, 8
MEMBER_NOUN_RE = re.compile(r"^[a-z][a-z -]{0,22}[a-z]$")   # a short lowercase noun, written as the author wrote it
MEMBER_LOGO_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")        # a catalogue asset id (build_scene_timeline_f.PROP_ID)
# the tile's geometry in STAGE px - mirrors of the engine's LPMEMBER (INSET_PX, GAP_PX, PAD_PX) and LPBAR.W_PX, read by
# the phone-floor check below (an estimate: the engine fits the drawn name; this names the one that cannot fit)
MEMBER_TILE_PX = {"inset": 8.0, "gap": 6.0, "pad": 8.0}
MEMBER_BAR_W_PX = 196.0
MEMBER_LOGO_MIN_PX = 48.0   # the engine's LPMEMBER.LOGO_MIN_PX: a cutout drawn smaller reads as a smudge, and the tile writes the NAME
MEMBER_LINE_H = 1.15


def _nested_bars(series: dict) -> list[tuple[str, list]]:
    """Bars that live INSIDE a panel or a tier - where a membership stack is not drawn."""
    out = [(f"panels[{k}]", p.get("bars") or []) for k, p in enumerate(series.get("panels") or []) if isinstance(p, dict)]
    out += [(f"tiers[{k}]", t.get("bars") or []) for k, t in enumerate(_tier_entries(series)) if isinstance(t, dict)]
    return [(w, [b for b in bars if isinstance(b, dict)]) for w, bars in out if isinstance(bars, list)]


def member_bars(series: dict) -> list[int]:
    """The indices of the page's bars that carry `members`."""
    return [i for i, b in enumerate(_bars(series)) if MEMBERS_KEY in b]


def member_errors(where: str, bar: dict) -> list[str]:
    """One bar's membership: ONE value (never a range, never zero), 2..MEMBERS_MAX members, each a name (unique), an
    optional catalogue `logo` id and an optional `short` name for its tile - and NOTHING that carries a value (s101)."""
    errors, ms = [], bar.get(MEMBERS_KEY)
    if _is_range(bar.get("value")):
        errors.append(f"{where} is a RANGE and carries members: a range states two values, and a membership stack "
                      "fills ONE value with equal tiles (E99 s101)")
    elif to_number(bar.get("value")) == 0:
        errors.append(f"{where} is zero and carries members: a bar at zero has no height to hold its tiles")
    if not isinstance(ms, list):
        return errors + [f"{where} members {ms!r}: members is a list of {{name, logo?, short?}} - one per tile"]
    if not MEMBERS_MIN <= len(ms) <= MEMBERS_MAX:
        errors.append(f"{where}: {len(ms)} member(s) - a membership stack holds {MEMBERS_MIN} to {MEMBERS_MAX} members "
                      "(one is a label; past eight no tile holds a name at the phone floor - count them with the "
                      "count array)")
    seen: set[str] = set()
    for j, m in enumerate(ms):
        w = f"{where} members[{j}]"
        if not isinstance(m, dict):
            errors.append(f"{w} {m!r} is an object {{name, logo?, short?}}")
            continue
        valued = [k for k in m if k in MEMBER_VALUE_FIELDS
                  or (k not in MEMBER_FIELDS and isinstance(m[k], Real) and not isinstance(m[k], bool))]
        if valued:
            errors.append(f"{w} carries a value ({', '.join(valued)}): E99 s101 - a membership tile carries no value of "
                          "its own (equal height, never sized). A stack of VALUES is the stacked bar (`segments`, "
                          "P69 T64, E99 s110 (1)); to compare the members' sizes, draw them as bars")
        errors += [f"{w}: {k!r} is not a member field ({'|'.join(MEMBER_FIELDS)})" for k in m
                   if k not in MEMBER_FIELDS and k not in valued]
        name = m.get("name")
        if not _text(name):
            errors.append(f"{w} needs a name - the tile writes it, or names the logo it carries")
            continue
        key = str(name).strip().lower()
        if key in seen:
            errors.append(f"{where}: the member {key!r} twice - each tile is ONE member")
        seen.add(key)
        logo = m.get("logo")
        if logo is not None and not (isinstance(logo, str) and MEMBER_LOGO_RE.match(logo)):
            errors.append(f"{w}: logo {logo!r} is not a catalogue id - a logo is one of the operator's catalogued "
                          "cutouts (assets/icons, E94), never a file or an invented mark")
        short = m.get("short")
        if short is not None and not (_text(short) and len(str(short).strip()) < len(str(name).strip())):
            errors.append(f"{w}: short {short!r} is not shorter than its name {name!r}")
    return errors


def _validate_members(series: dict, variant: str) -> list[str]:
    """P69 T45: every `members` on the page - a BARS page's bars only (never a panel's or a tier's, a combo's or a
    progress page's), never on a breakthrough page (its bar runs past the scale its tiles would divide) - and the
    `member_noun` its key writes. A page with neither is untouched."""
    errors = [f"{where}: a membership (members) is a BARS PAGE's - one bar of one value, its tiles naming who is in it "
              "(P69 T45); draw it on a bars page of its own"
              for where, bars in _nested_bars(series) if any(MEMBERS_KEY in b for b in bars)]
    held = member_bars(series)
    if MEMBER_NOUN_KEY in series:
        noun = series[MEMBER_NOUN_KEY]
        if not held:
            errors.append("member_noun names what a membership tile is, and no bar carries members")
        if not (isinstance(noun, str) and MEMBER_NOUN_RE.match(noun)):
            errors.append(f"member_noun {noun!r}: a short lowercase noun ('company', 'stock') - the page writes "
                          f"{MEMBER_KEY_TEXT.format(noun='<noun>')!r}")
    if not held:
        return errors
    builder = pick_builder(series, variant)
    if variant != "bars" or builder != "story":
        errors.append(f"bars{held} carry members: a membership stack is a bars page's (variant bars, one value per "
                      f"bar) - this page draws {variant!r} as {builder!r}")
    if series.get("overflow") is not None:
        errors.append(f"bars{held} carry members on a breakthrough page (overflow): the breakthrough shoots a bar past "
                      "its stated scale, and a membership divides ONE standing value - give it a page of its own scale")
    for i in held:
        errors += member_errors(f"bars[{i}]", _bars(series)[i])
    return errors


def _with_member_tiles(block: dict, series: dict) -> dict:
    """P69 T45: a bars block whose bars carry members - `members` per bar (None for a bar without) and the key the page
    writes. A block with none is returned untouched - no key, the page it always was."""
    bars = _bars(series)
    if not any(MEMBERS_KEY in b for b in bars):
        return block
    block[MEMBERS_KEY] = [[{k: m[k] for k in MEMBER_FIELDS if m.get(k) is not None} for m in b[MEMBERS_KEY]]
                          if MEMBERS_KEY in b else None for b in bars]
    block["member_key"] = MEMBER_KEY_TEXT.format(noun=series.get(MEMBER_NOUN_KEY) or MEMBER_NOUN_DEFAULT)
    return block


def _two_lines(words: list[str]) -> list[str]:
    """A name broken at the space nearest its middle (by characters) - the engine's own break."""
    best = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
    return [" ".join(words[:best]), " ".join(words[best:])]


def member_fit_warnings(spec: dict, aspect: str = "16:9") -> list[str]:
    """P69 T45 (the acceptance's (3)): a WARN - never a refusal (E99 s106) - for each membership tile whose NAME cannot
    be written at E99 s90's phone floor (12 px on a 390-px-wide phone) inside it, on one line or two, with the numbers.
    The tile is estimated the engine's way: the bar at its width (the 196 px cap, or its pitch less the builder's 0.34
    air), its height on the bars law's scale (zero kept, 14 % air), divided equally, less the tile's inset, gaps and
    padding. A logo tile writes no name and is not checked - unless its cutout would be drawn under
    MEMBER_LOGO_MIN_PX, where the engine writes the name instead. Pure."""
    members = spec.get(MEMBERS_KEY)
    if not isinstance(members, list) or not any(members):
        return []
    vals = [float(v) for v in spec.get("values") or []]
    if not vals:
        return []
    floor = card_floor_px(STAGE_PX[aspect][0])
    chart = page_boxes(spec, aspect)["chart"]   # the bars builder's OWN plot inside it (buildLedgerBars, not the line's margins):
    plot = ({"w": chart["w"] - 150 - 30, "h": chart["h"] - 150 - 70} if aspect == "9:16"     # portrait: stage px, top 150, foot 70
            else {"w": chart["w"] * 920 / 1000, "h": chart["h"] * 350 / 560})              # landscape: x 60-980, y 90-440 of 1000 x 560
    lo, hi = min(0.0, *vals), max(0.0, *vals)
    pad = (hi - lo) * BARS_PAD
    span = (hi + (pad if hi > 0 else 0.0)) - (lo - (pad if lo < 0 else 0.0)) or 1.0
    T = MEMBER_TILE_PX
    tile_w = min(MEMBER_BAR_W_PX, plot["w"] / len(vals) * (1 - 0.34)) - 2 * T["inset"] - 2 * T["pad"]
    out = []
    for i, ms in enumerate(members):
        if not ms:
            continue
        bar_h = abs(vals[i]) / span * plot["h"]
        tile_h = (bar_h - (len(ms) + 1) * T["gap"]) / len(ms) - 2 * T["pad"]
        for m in ms:
            if m.get("logo") and min(tile_w, tile_h) >= MEMBER_LOGO_MIN_PX:
                continue   # the catalogued cutout is drawn, big enough to read; a smaller one gives way to the name, checked below
            text = str(m.get("short") or m.get("name") or "")
            one = longform_text_px(text, "title", floor)
            words = text.split()
            two = max(longform_text_px(ln, "title", floor) for ln in _two_lines(words)) if len(words) > 1 else one
            line = floor * MEMBER_LINE_H
            if (one <= tile_w and line <= tile_h) or (two <= tile_w and 2 * line <= tile_h):
                continue
            label = (spec.get("labels") or [None] * len(vals))[i]
            out.append(f"WARN member: {text!r} on bar {i} ({label!r}) cannot be written at the phone floor "
                       f"({floor:.0f} px, E99 s90) in its tile ({tile_w:.0f} x {tile_h:.0f} px): it needs {one:.0f} px "
                       + (f"on one line or {two:.0f} px on two" if len(words) > 1 else "on its one line")
                       + " - give it a `short` name, fewer members, or its catalogued logo. REPORTED, the frame read "
                       "decides (E99 s106)")
    return out


# ---- P69 T64 (E99 s110 (1); s100; s102; s106; s109): THE STACKED BAR OF VALUES, AND THE STACKED-BAR-PLUS-LINE COMBO ---
# s110 (1): "allowed, I think one legitimate case I can think of in finance is ... when you're looking at financial
# metrics against business metrics ... where you could have a stacked bar and a line." A stack of VALUES is valid on
# s109's honesty tests - s100's two: every segment drawn TRUE to its value, and the figures WRITTEN (each segment's, and
# the bar's total). The bar's own `value` IS the total, written over it as any bar's is; its `segments` stand bottom-up
# from zero inside it in ONE order and ONE set of colours for the page, named once by the page's key. Its home is the
# COMBO: the stacks and ONE line over them, the line on the stacks' scale when its unit is theirs and on its OWN
# labelled right axis when it is not (s102 (b)(c): each axis names its unit, its ticks in its own series' colour) - the
# combo's own `line_unit` axis (P47 T9), never a third axis system. Refused as UNTRUE: segments that do not add up to
# the written total, a negative segment (there is no signed baseline - the stack stands on zero, E28), two units on one
# axis. A segment too thin to hold its figure is REPORTED (s106) and the engine writes its figure beside the bar on a
# leader. A page with no `segments` is the page it was, to the byte.
SEGMENTS_KEY = "segments"
SEGMENT_KEY_KEY = "segment_key"
LINE_LABEL_KEY = "line_label"
SEGMENT_FIELDS = ("name", "value", "value_string", "color")
# [DERIVED] two to four: one segment is the bar itself; past four the field's four electric inks (E67) repeat, and a
# key of five names no longer fits the plot's head at the phone floor
SEGMENTS_MIN, SEGMENTS_MAX = 2, 4
SEGMENT_INKS = ("teal", "crimson", "cobalt", "amber")   # E67's cycle (the engine's LP_CYCLE), by the segment's place in the key
SEGMENT_COLOURS = SEGMENT_INKS + ("deemph",)            # the field's tokens (LP_INK): deemph is explicit de-emphasis, declared only
SEGMENT_BUILDERS = ("story", "combo")
# every key a bar datum may carry; anything else is refused BY NAME (R26-307: `segments` - and any misspelt key - was
# silently dropped). `value_string` stays legal: 27 bars on disk carry it (the record's own token, read by no builder);
# `x` is P47 T9's combo bar on the lines' time axis (buildLedgerCombo reads a bar's own x)
PROJECTED_KEY = "projected"   # P71 T25: a bar whose height is a sourced PROJECTION (E77) - `projected: {value, label, tier, src}`
BAR_FIELDS = ("label", "value", "color", "note", "value_string", "x", MEMBERS_KEY, SEGMENTS_KEY, PROJECTED_KEY)
# the figure's box in the ENGINE's units (LPSEG, `lpSegBuild`): the value type, a line of it, the padding inside a segment
SEGMENT_FIG = {"story": 26.0, "story_p": 44.0, "combo": 24.0, "combo_p": 30.0, "line": 1.25, "pad": 6.0,
               "min": 0.8}   # a figure a little too wide for its part shrinks to fit it, never under 0.8 of its size (LPSEG.FIG_MIN)


def _bar_lists(series: dict) -> list[tuple[str, list]]:
    """Every bars list on the page with the address an error names: its own, each panel's, each tier's."""
    own = [("", series.get("bars"))] if isinstance(series.get("bars"), list) else []
    nested = [(f"panels[{k}] ", p.get("bars")) for k, p in enumerate(series.get("panels") or []) if isinstance(p, dict)]
    nested += [(f"tiers[{k}] ", t.get("bars")) for k, t in enumerate(_tier_entries(series)) if isinstance(t, dict)]
    return own + [(w, b) for w, b in nested if isinstance(b, list)]


def _validate_bar_fields(series: dict) -> list[str]:
    """P69 T64 / R26-307: a bar datum carries only the fields the form draws - anything else is refused by name."""
    errors = []
    for where, bars in _bar_lists(series):
        for j, b in enumerate(bars):
            unknown = sorted(k for k in b if k not in BAR_FIELDS) if isinstance(b, dict) else []
            if unknown:
                errors.append(f"{where}bars[{j}]: unknown key(s) {unknown} - a bar takes {', '.join(BAR_FIELDS)} "
                              "(a key the form does not know would be dropped, and its page drawn without it)")
    return errors


# ---- P72 T13 (R26-274, R26-287; E28: an axis states its unit) - THE UNIT AS THE PAGE WRITES IT ------------------------
# The engine's `lpWithUnit`, in Python: a PREFIX unit ("$") stands before the figure and its sign after ("-$40"); a WORD
# unit takes a space - it opens with a letter and runs three letters or more ("20 years", "5 yen"); a SYMBOL unit none
# ("12%", "3.2x", "96Mb"); a unit the author already spaced (" years") is written as given. R26-287: a prefix AND a
# suffix - `unit: "$"` + `unit_suffix: "B"` writes "$480B" on the value, the ticks, the pill and the card. The suffix
# completes a PREFIX, so it is refused beside any other unit, and it is refused by name when malformed (s106: a silent
# drop is neither advice nor refusal).
UNIT_SUFFIX_KEY = "unit_suffix"
UNIT_PREFIXES = ("$",)            # the engine's one prefix unit (lpWithUnit)
UNIT_SUFFIX_MAX = 8               # "B", "bn", "trillion": a magnitude word, never a phrase (the sub says what the bars show)
UNIT_SUFFIX_BUILDERS = ("story",)  # the bars page (and its card) - the builder that writes a value, its ticks and its pill
UNIT_WORD_RE = re.compile(r"^(?=[^\W\d_])[\s\S]*?[^\W\d_]{3}")   # the engine's LP_UNIT_WORD: /^(?=\p{L})[\s\S]*?\p{L}{3}/u


def unit_gap(unit: str) -> str:
    """" " before a WORD unit, "" before a symbol (and before a unit the author spaced). Pure."""
    return " " if UNIT_WORD_RE.match(str(unit or "")) else ""


def with_unit(text: str, unit: str, suffix: str = "") -> str:
    """The figure as the engine writes it (`lpWithUnit`). Pure."""
    s, u = str(text), str(unit or "")
    if suffix:
        neg = s.startswith("-")
        return ("-" if neg else "") + u + (s[1:] if neg else s) + unit_gap(suffix) + suffix
    if u in UNIT_PREFIXES:
        return ("-" + u + s[1:]) if s.startswith("-") else u + s
    return s + unit_gap(u) + u


def _validate_unit_suffix(series: dict, variant: str) -> list[str]:
    """R26-287: `unit_suffix` completes a prefix unit on a bars page; anything else is refused by name."""
    if UNIT_SUFFIX_KEY not in series:
        return []
    suf, unit = series[UNIT_SUFFIX_KEY], str(series.get("unit") or "")
    if not isinstance(suf, str) or not suf or suf != suf.strip() or not re.fullmatch(r"[^\W\d_]+", suf)             or len(suf) > UNIT_SUFFIX_MAX:
        return [f"{UNIT_SUFFIX_KEY} {suf!r} must be the magnitude the figure is in - letters only, 1 to {UNIT_SUFFIX_MAX} "
                "('B' writes $480B; the sub says what the bars show)"]
    if unit not in UNIT_PREFIXES:
        return [f"{UNIT_SUFFIX_KEY} {suf!r} completes a PREFIX unit ({', '.join(repr(u) for u in UNIT_PREFIXES)}); this "
                f"page's unit is {unit!r}{' (a suffix already)' if unit else ''} - write the one unit (`unit`)"]
    builder = pick_builder(series, variant)
    if builder not in UNIT_SUFFIX_BUILDERS:
        return [f"{UNIT_SUFFIX_KEY} is written by a bars page ({'|'.join(UNIT_SUFFIX_BUILDERS)}); this page draws "
                f"{builder!r}, which would drop it - fold the magnitude into its `unit`, or draw it as bars"]
    return []


def segment_bars(series: dict) -> list[int]:
    """The indices of the page's bars that carry `segments`."""
    return [i for i, b in enumerate(_bars(series)) if SEGMENTS_KEY in b]


def _fmt_sum(x: float) -> str:
    return f"{round(x, 6):g}"


def segment_errors(where: str, bar: dict, unit: str) -> list[str]:
    """One stacked bar: ONE positive total (never a range, never members), SEGMENTS_MIN..MAX segments, each a unique
    name and a positive figure in the page's unit, and the figures adding up to the written total within their own
    rounding (half a unit of each figure's finest place - s109: a stack that does not sum to its total is untrue)."""
    errors, segs, v = [], bar.get(SEGMENTS_KEY), bar.get("value")
    total = None if _is_range(v) else to_number(v)
    if _is_range(v):
        errors.append(f"{where} is a RANGE and carries segments: a stack stands on ONE written total, which its "
                      "segments sum to (P69 T64)")
    elif total is not None and total <= 0:
        errors.append(f"{where} total {value_string(v)} is {'negative' if total < 0 else 'zero'}: a stacked bar stands "
                      "bottom-up from zero, and a negative stack needs a signed baseline, which it does not draw (E28)")
    if MEMBERS_KEY in bar:
        errors.append(f"{where} carries members and segments: a bar is divided ONE way - WHO is in it (members, equal "
                      "tiles, E99 s101) or what it is made of (segments, values, s110 (1))")
    if not isinstance(segs, list):
        return errors + [f"{where} segments {segs!r}: segments is a list of {{{', '.join(SEGMENT_FIELDS)}}} - one per "
                         "stacked part"]
    if not SEGMENTS_MIN <= len(segs) <= SEGMENTS_MAX:
        errors.append(f"{where}: {len(segs)} segment(s) - a stacked bar holds {SEGMENTS_MIN} to {SEGMENTS_MAX} (one "
                      "is the bar itself; past four the field's four inks repeat, E67)")
    seen: set[str] = set()
    figures = []
    for j, s in enumerate(segs):
        w = f"{where} segments[{j}]"
        if not isinstance(s, dict):
            errors.append(f"{w} {s!r} is an object {{{', '.join(SEGMENT_FIELDS)}}}")
            continue
        if "unit" in s and str(s["unit"]) != unit:
            errors.append(f"{w} is in {s['unit']!r} on a page in {unit!r}: two units on one axis - a stack's segments "
                          "stand on the bar's scale in the page's unit (E99 s102: a second unit takes its own labelled "
                          "axis - the combo's line, never a segment)")
        errors += [f"{w}: {k!r} is not a segment field ({'|'.join(SEGMENT_FIELDS)})" for k in s
                   if k not in SEGMENT_FIELDS and not (k == "unit" and str(s["unit"]) != unit)]
        name = s.get("name")
        if not _text(name):
            errors.append(f"{w} needs a name - the page's key writes it")
        else:
            key = str(name).strip().lower()
            if key in seen:
                errors.append(f"{where}: the segment {key!r} twice - each part of a stack is named once")
            seen.add(key)
        c = s.get("color")
        if c is not None and c not in SEGMENT_COLOURS:
            errors.append(f"{w}: color {c!r} is not one of {'|'.join(SEGMENT_COLOURS)} (the field's inks, E67)")
        vs = s.get("value_string")
        if vs is not None and not _text(vs):
            errors.append(f"{w}: value_string {vs!r} is the figure as the source writes it - text")
        sv = s.get("value")
        n = None if _is_range(sv) else to_number(sv)
        if n is None:
            errors.append(f"{w} value {sv!r} is not numeric - a segment is a figure the page writes")
            continue
        if n < 0:
            errors.append(f"{w} is a negative segment ({value_string(sv)}): a stacked bar stands bottom-up from zero, "
                          "and a negative segment needs a signed baseline, which a stack does not draw (E28: the sign "
                          "is geometry) - draw the negative part as a bar of its own")
        elif n == 0:
            errors.append(f"{w} is zero: a segment of zero has no height to hold its figure - leave it out and say "
                          "so in the sub")
        figures.append((n, sv))
    if total is not None and figures and len(figures) == len(segs):
        got = sum(n for n, _ in figures)
        tol = sum(0.5 * 10 ** -_decimals(sv) for _, sv in figures) + 0.5 * 10 ** -_decimals(v) + 1e-9
        if abs(got - total) > tol:
            errors.append(f"{where}: its segments sum to {_fmt_sum(got)}, and the bar's written total is "
                          f"{value_string(v)} - a stack that does not add up to its total is untrue (E99 s109; the "
                          f"figures' own rounding allows {_fmt_sum(tol)})")
    return errors


def segment_key(series: dict) -> list[dict]:
    """The page's ONE key: the first stacked bar's names in stack order (bottom-up), each in its colour - declared on
    any bar (the first declaration), else E67's ink for its place."""
    held = segment_bars(series)
    if not held:
        return []
    segs = [s for s in _bars(series)[held[0]].get(SEGMENTS_KEY) or [] if isinstance(s, dict)]
    declared: dict[str, str] = {}
    for i in held:
        for s in _bars(series)[i].get(SEGMENTS_KEY) or []:
            if isinstance(s, dict) and _text(s.get("name")) and s.get("color") is not None:
                declared.setdefault(str(s["name"]).strip().lower(), str(s["color"]))
    return [{"name": str(s.get("name") or "").strip(),
             "color": declared.get(str(s.get("name") or "").strip().lower(), SEGMENT_INKS[j % len(SEGMENT_INKS)])}
            for j, s in enumerate(segs)]


def _segment_key_errors(series: dict, held: list[int]) -> list[str]:
    """The key is the page's: every stacked bar carries the same names in the same order, a name keeps ONE colour, and
    no two names share one (they would read as one part)."""
    errors, first, colour = [], None, {}
    for i in held:
        segs = _bars(series)[i].get(SEGMENTS_KEY)
        if not isinstance(segs, list):
            continue
        names = [str(s.get("name") or "").strip() for s in segs if isinstance(s, dict)]
        if first is None:
            first = (i, names)
        elif [n.lower() for n in names] != [n.lower() for n in first[1]]:
            errors.append(f"bars[{i}] stacks {names} and bars[{first[0]}] stacks {first[1]}: the segments' order is the "
                          "page's ONE key - every stacked bar carries the same names in the same order, bottom-up")
        for s in segs:
            if isinstance(s, dict) and _text(s.get("name")) and s.get("color") is not None:
                nm = str(s["name"]).strip()
                was = colour.setdefault(nm.lower(), (s["color"], i))
                if was[0] != s["color"]:
                    errors.append(f"bars[{i}] segment {nm!r} is {s['color']!r} and {was[0]!r} on bars[{was[1]}]: a "
                                  "segment's colour is keyed once for the page")
    inks = [k["color"] for k in segment_key(series)]
    for c in sorted({c for c in inks if inks.count(c) > 1}):
        errors.append(f"two segments in {c!r}: each part of the stack takes one colour of its own, or two parts read as "
                      f"one - the key gives {[k['name'] for k in segment_key(series) if k['color'] == c]} one colour")
    return errors


def _stacked_combo_errors(series: dict) -> list[str]:
    """s110 (1) + s102: the stacks and ONE line. One unit is one axis; two units are two axes, both NAMED - the stacks'
    `ylabel` on the left, the line's `line_label` on its own right axis (written in the line's colour)."""
    errors, lines = [], dense_series(series)
    if len(lines) != 1:
        errors.append(f"a stacked combo lays ONE line over its stacks (the business metric against the financial "
                      f"ones, E99 s110 (1)) - this page carries {len(lines)}: give the others a page of their own")
    if series.get("tiers") is True:
        errors.append("tiers: true on a stacked combo: the line rides OVER the stacks on one plot (s110 (1)); two bands "
                      "are not built for segments (P69 T64) - drop tiers")
    unit, lu = series.get("unit"), series.get("line_unit")
    if not _text(unit):
        errors.append("a stacked combo's bars need their `unit`: each axis names its unit (E99 s102 (b)) and the "
                      "stacks' axis writes it on its ticks")
    two = _text(lu) and str(lu) != str(unit or "")
    if two:
        if not _text(series.get("ylabel")):
            errors.append(f"the line is in {lu!r} and the stacks in {unit!r}: two units, two axes, and each axis names "
                          "its unit (E99 s102 (b)) - the stacks' axis needs its `ylabel`")
        if not _text(series.get(LINE_LABEL_KEY)):
            errors.append(f"the line is in {lu!r} and the stacks in {unit!r}: two units, two axes, and each axis names "
                          f"its unit (E99 s102 (b)) - the line's own right axis needs its `{LINE_LABEL_KEY}`")
    elif series.get(LINE_LABEL_KEY) is not None:
        errors.append(f"{LINE_LABEL_KEY} names the line's OWN right axis, and this line shares the stacks' scale (its "
                      "unit is theirs) - one unit is one axis")
    axis_unit = str(lu) if two else str(unit or "")
    inks = {k["color"] for k in segment_key(series)}
    for si, ln in enumerate(lines):
        nm = ln.get("name") or ln.get("label") or f"series[{si}]"
        col = ln.get("color") or SEGMENT_INKS[si % len(SEGMENT_INKS)]
        if col in inks:
            errors.append(f"the line {nm!r} is {col!r}, a segment's colour: the key gives each colour ONE meaning - give "
                          "the line an ink of its own (E67)")
        if "unit" in ln and str(ln["unit"]) != axis_unit:
            errors.append(f"the line {nm!r} is in {ln['unit']!r} on an axis in {axis_unit!r}: two units on one axis - "
                          "a second unit takes its own labelled axis (E99 s102), `line_unit`")
    return errors


def _validate_segments(series: dict, variant: str) -> list[str]:
    """P69 T64: every `segments` on the page - a BARS page's bars or a COMBO's (never a panel's or a tier's, a progress
    or a decline page's, a breakthrough's) - held to the honesty tests, one key for the page, and the combo's axes."""
    errors = [f"{where}bars: a stacked bar (segments) is a BARS page's or a COMBO's (P69 T64) - a panel's or a tier's "
              "bars stand alone; draw the stack on a page of its own"
              for where, bars in _bar_lists(series)[(1 if isinstance(series.get("bars"), list) else 0):]
              if any(isinstance(b, dict) and SEGMENTS_KEY in b for b in bars)]
    held = segment_bars(series)
    if not held:
        return errors
    builder = pick_builder(series, variant)
    if not (builder == "combo" or (builder == "story" and variant == "bars")):
        errors.append(f"bars{held} carry segments: a stacked bar is a bars page's (variant bars) or a combo's (bars + "
                      f"one line) - this page draws {variant!r} as {builder!r}")
    if series.get("overflow") is not None:
        errors.append(f"bars{held} carry segments on a breakthrough page (overflow): the breakthrough shoots ONE bar past "
                      "its stated scale, and a stack's segments are drawn true on the scale they stand on")
    if member_bars(series) and set(member_bars(series)) != set(held):
        errors.append(f"bars{member_bars(series)} carry members and bars{held} segments: a page divides its bars ONE "
                      "way - who is in them (s101) or what they are made of (s110 (1))")
    unit = str(series.get("unit") or "")
    for i in held:
        errors += segment_errors(f"bars[{i}]", _bars(series)[i], unit)
    errors += _segment_key_errors(series, held)
    if builder == "combo":
        errors += _stacked_combo_errors(series)
    return errors


def _with_segments(block: dict, series: dict) -> dict:
    """P69 T64: a bars block whose bars carry segments - per bar (None for a plain bar) each segment's name, value, the
    figure as written, and its colour from the page's ONE key; and the key. A block with none is returned untouched."""
    bars = _bars(series)
    if not any(SEGMENTS_KEY in b for b in bars):
        return block
    key = segment_key(series)
    ink = {k["name"].lower(): k["color"] for k in key}

    def seg(s: dict) -> dict:
        nm = str(s.get("name") or "").strip()
        return {"name": nm, "value": to_number(s.get("value")),
                "value_string": value_string(s["value_string"] if s.get("value_string") is not None else s.get("value")),
                "color": ink.get(nm.lower(), SEGMENT_INKS[0])}

    block[SEGMENTS_KEY] = [[seg(s) for s in b[SEGMENTS_KEY]] if SEGMENTS_KEY in b else None for b in bars]
    block[SEGMENT_KEY_KEY] = key
    return block


def _stack_plot_px(spec: dict, aspect: str) -> tuple[float, float, float]:
    """(plot height, one bar's width, chart units -> stage px) of a stacked page's bars, estimated the engine's way:
    the bars builder's plot (buildLedgerBars: the 196 px cap, 0.34 air) or the combo's (buildLedgerCombo: y 110-470 of
    560, x 96-806 of 1000, 0.62 of a slot). An estimate - the engine measures the drawn figure; this names the one
    that cannot fit."""
    chart = page_boxes(spec, aspect)["chart"]
    n = max(1, len(spec.get("values") or []))
    if spec.get("builder") == "combo":
        k = chart["w"] / 1000.0
        return chart["h"] * 360 / 560, (806 - 96) / n * 0.62 * k, k
    if aspect == "9:16":
        pw, ph, k = chart["w"] - 150 - 30, chart["h"] - 150 - 70, 1.0
    else:
        pw, ph, k = chart["w"] * 920 / 1000, chart["h"] * 350 / 560, chart["w"] / 1000.0
    return ph, min(MEMBER_BAR_W_PX, pw / n * (1 - 0.34)), k


def _stack_span(spec: dict) -> float:
    """The value the plot's height stands for: the bars law's 14 % air, or the combo's 1.12 - over the line too, when it
    shares the stacks' scale."""
    vals = [float(v) for v in spec.get("values") or [] if v is not None]
    if spec.get("builder") == "combo":
        if not stacked_line_own_axis(spec):
            vals += [float(p[1]) for s in spec.get("series") or [] for p in s.get("pts") or []]
        return (max([0.0, *vals]) - min([0.0, *vals])) * 1.12 or 1.0
    hi, lo = max([0.0, *vals]), min([0.0, *vals])
    return (hi - lo) * (1 + BARS_PAD) or 1.0


def stacked_line_own_axis(spec: dict) -> bool:
    """A stacked combo's line takes its own right axis when its unit is not the stacks' (s102); else it shares theirs."""
    lu = spec.get("line_unit")
    return isinstance(lu, str) and bool(lu.strip()) and lu != str(spec.get("unit") or "")


def segment_fit_warnings(spec: dict, aspect: str = "16:9") -> list[str]:
    """P69 T64 (s106): a WARN - never a refusal - for each segment too short or too narrow to hold its own figure inside
    it at the engine's value type: that figure is written BESIDE its bar on a leader (the engine's `lpSegBuild`), so no
    figure is ever unwritten; the frame read decides whether the page still reads. Pure."""
    segs = spec.get(SEGMENTS_KEY)
    if not isinstance(segs, list) or not any(segs):
        return []
    ph, bw, k = _stack_plot_px(spec, aspect)
    span, unit = _stack_span(spec), str(spec.get("unit") or "")
    kind = ("combo" if spec.get("builder") == "combo" else "story") + ("_p" if aspect == "9:16" else "")
    fs, pad = SEGMENT_FIG[kind] * k, SEGMENT_FIG["pad"] * k   # k is 1 on the portrait bars page (its units are stage px)
    out = []
    for i, ss in enumerate(segs):
        for s in ss or []:
            h = abs(float(s["value"])) / span * ph
            text = with_unit(s["value_string"], unit, str(spec.get(UNIT_SUFFIX_KEY) or ""))   # P72 T13: as lpWithUnit writes it
            tw = longform_text_px(text, "title", fs)
            q = min(1.0, (bw - 2 * pad) / tw) if tw > 0 else 1.0
            need_w, need_h = tw * SEGMENT_FIG["min"] + 2 * pad, fs * max(q, SEGMENT_FIG["min"]) * SEGMENT_FIG["line"] + 2 * pad
            if q >= SEGMENT_FIG["min"] and h >= need_h:
                continue
            label = (spec.get("labels") or [None] * len(segs))[i]
            out.append(f"WARN segment: {s['name']!r} on bar {i} ({label!r}) is {s['value_string']} - about {h:.0f} px "
                       f"tall and {bw:.0f} px wide at {aspect}, and its figure {text!r} needs {need_w:.0f} x "
                       f"{need_h:.0f} px: the figure is written beside the bar on a leader (E99 s106). REPORTED, the "
                       "frame read decides")
    return out


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
    if variant == "line" and isinstance(series.get("panels"), list):   # P69 T8b: a PANELS object is a page of 2-4 plots
        return PANELS
    if variant == "line" and isinstance(series.get(SCHEMATIC_KEY), dict):   # P70 T2: a schematic is a dense line it generates
        return "dense-line"
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
# P70 T3 (was P69 T51; Bravos D40 17:24, harvest v2 T34): the FILL GAUGE is the third form - one share of one whole drawn
# as a capsule filling to it. It draws a PROGRESS page only (the variant that bounds a share: 0..PROGRESS_MAX, or
# 0..its denominator), so it is the one form whose fit reads the VARIANT as well as the builder (`FORM_VARIANTS`).
CHART_FORMS = ("extruded_bar", "tilted_line", "gauge")
FORM_BUILDERS = {"extruded_bar": ("story",), "tilted_line": ("dense-line",), "gauge": ("story",)}
FORM_VARIANTS = {"gauge": ("progress",)}   # a form named here fits these variants only; the two 2.5D forms fit any
FORM_READS = {"extruded_bar": "a BARS page - every bar is drawn as a prism",
              "tilted_line": "a LINE page - the line is drawn on a tilted plane",
              "gauge": "a PROGRESS page - one share of one whole, drawn as a capsule"}
TILT_DEG = 14.0        # the tilted plane's default turn about the page's own vertical axis, in degrees (E98 s3)
TILT_DEG_MAX = 89.0    # build_scene_timeline_f.PAGE_DEPTH["TILT_MAX"] - one limit, and the compiler checks it


GAUGE_DIRS = ("h",)    # P72 T6 (R26-319): `gauge:h`, the horizontal capsule - M26 reads its fill as a WIDTH


def form_error(form: str, builder: str, where: str, variant: str | None = None) -> str | None:
    """Is ``form`` a form THIS page's builder can draw? The message, or None. Pure. ``variant`` is read only by a form
    `FORM_VARIANTS` names (the gauge: a progress page); the two 2.5D forms ignore it, so their rule is what it was.
    P72 T6: an OBJECT may name `gauge:h` (the row's grammar, `page_form_geom`); any other gauge setting is refused."""
    name, sep, rest = str(form).partition(":")
    if name == "gauge" and sep:
        if rest not in GAUGE_DIRS:
            return (f"{where}: form={form!r} - form=gauge takes no setting but :h (the horizontal capsule; form=gauge "
                    "alone is the vertical one)")
        form = name
    if form not in CHART_FORMS:
        return (f"{where}: form {form!r} is not one of {'|'.join(CHART_FORMS)} "
                "(the two 2.5D chart forms and the progress gauge; the flat page is the reading form and names none)")
    if form in FORM_VARIANTS and variant not in FORM_VARIANTS[form]:
        return (f"{where}: form={form} is {FORM_READS[form]}, and this page is variant {variant!r} built by "
                f"{builder!r} (the form draws --variant {'|'.join(FORM_VARIANTS[form])}). The flat page is the "
                "reading form - drop the option")
    fits = FORM_BUILDERS[form]
    if builder not in fits:
        return (f"{where}: form={form} is {FORM_READS[form]}, and this page is built by {builder!r} "
                f"(the form is drawn by {'|'.join(fits)}). The flat page is the reading form - drop the option")
    return None


# ---- P70 T3: THE GAUGE'S WHOLE -----------------------------------------------------------------------------------
# The capsule's full length IS the whole - the progress ceiling (`PROGRESS_MAX`, or the page's denominator) - and the
# whole is NAMED on the page: the label of a comparator rule standing AT the ceiling (the 94 page's "every dollar from
# operations"). A capsule whose whole has no name is a bar in a box (E28: a chart reads at a glance or it is not on the
# page), so it is refused; a stated scale other than 0..the whole would draw the capsule as something else, refused too.
# Read off the compiled PAGE (`axes.hlines`, `axes.domain`) or off an OBJECT (`hlines`, `domain`) - one rule, twice.
def gauge_ceiling(page: dict) -> float:
    """The whole a gauge's capsule stands for: the page's denominator, else PROGRESS_MAX (`_validate_variant`'s bound)."""
    denominator = to_number(page.get("denominator"))
    return denominator if denominator and denominator > 0 else float(PROGRESS_MAX)


def _gauge_axes(page: dict) -> dict:
    axes = page.get("axes") if isinstance(page.get("axes"), dict) else {}
    return {"hlines": axes.get("hlines", page.get("hlines")) or [], "domain": axes.get("domain", page.get("domain"))}


def gauge_whole(page: dict) -> str | None:
    """The whole's NAME - the label of the first hline standing at the ceiling - or None."""
    ceiling = gauge_ceiling(page)
    for rule in _gauge_axes(page)["hlines"]:
        y = to_number(rule.get("y")) if isinstance(rule, dict) else None
        if y is not None and abs(y - ceiling) < 1e-9 and _text(rule.get("label")):
            return str(rule["label"]).strip()
    return None


def gauge_error(page: dict, where: str) -> str | None:
    """Can this progress page be drawn as a gauge whose capsule IS its whole? The message, or None. Pure."""
    ceiling = gauge_ceiling(page)
    top = f"{ceiling:g}"
    domain = _gauge_axes(page)["domain"]
    if isinstance(domain, (list, tuple)) and len(domain) == 2:
        lo, hi = to_number(domain[0]), to_number(domain[1])
        if lo is None or hi is None or abs(lo) > 1e-9 or abs(hi - ceiling) > 1e-9:
            return (f"{where}: form=gauge draws the capsule as the WHOLE, 0..{top}, and the page states the scale "
                    f"[{value_string(domain[0])}, {value_string(domain[1])}] - a gauge's scale is its whole: state "
                    f"[0, {top}] or none")
    if gauge_whole(page) is None:
        return (f"{where}: form=gauge draws the capsule as the WHOLE ({top}), and the page never names it - give it a "
                f"comparator rule AT {top} with a label naming the whole (an hline at y {top} with a label, as the 94 "
                "page's 'every dollar from operations'). E28: a chart reads at a glance or it is not on the page")
    return None


GAUGE_TEXT_FLOOR = 4.5   # series_inks.TEXT_FLOOR (BUILD-PIPELINE.md:307): a figure is text, and owes the text tier


def gauge_figure_ink(page: dict, i: int) -> tuple[str, str, str]:
    """(the hex the engine writes bar i's figure in, its token, the ground under it) - the engine's own rule for a gauge
    figure (`dcol || sign`: the declared token's ink, else the sign colour), read off the engine's palette and the
    template's grounds by series_inks, never re-typed. A page on a plate's cream surface stands on the cream."""
    import series_inks as SINKS
    pal = SINKS.palette()
    tok = (page.get("colors") or [None] * (i + 1))[i]
    value = to_number((page.get("values") or [0])[i]) or 0.0
    hx, name = (pal["ink"][tok], str(tok)) if tok in pal["ink"] else ((pal["neg"], "--lp-neg") if value < 0 else (pal["pos"], "--lp-pos"))
    if page.get("surface_from"):
        m = re.search(r"--lp-cream:\s*(#[0-9A-Fa-f]{6})", SINKS.TEMPLATE.read_text(encoding="utf-8"))
        return hx, name, m.group(1) if m else "#F4E6C7"
    return hx, name, SINKS.ground_of(page)


def gauge_warnings(page: dict) -> list[str]:
    """P70 T3 / E99 s106: REPORTED with their numbers, never refused - (a) a gauge page with a SECOND bar is drawn, one
    capsule per bar, because comparing shares is a bars page's job (USE-WHEN T34: "don't: comparing shares (use bars)");
    (b) a figure whose bar's ink reads under the text floor on its ground (the review's finding 7: T37b's s118 check
    reads line and combo pages only). [] on a page that names no gauge. Pure: the compiler prints it, never stores it."""
    if ((page.get("form") or {}).get("kind")) != "gauge":
        return []
    import series_inks as SINKS
    out = []
    for i, label in enumerate(page.get("labels") or []):
        hx, tok, ground = gauge_figure_ink(page, i)
        ratio = SINKS.contrast(hx, ground)
        if ratio < GAUGE_TEXT_FLOOR:
            out.append(f"{FORM_WARN} gauge: the figure of {str(label)!r} is written in its bar's ink {tok} {hx} at "
                       f"{ratio:.2f}:1 on the ground {ground} - under the text floor {GAUGE_TEXT_FLOOR}:1 "
                       "(BUILD-PIPELINE.md:307). REPORTED, the frame read decides (E99 s106): declare a brighter token")
    if len(page.get("values") or []) < 2:
        return out
    unit = str(page.get("unit") or "")
    shares = ", ".join(f"{str(lab)!r} {vs}{unit}"
                       for lab, vs in zip(page.get("labels") or [], page.get("value_strings") or []))
    n = len(page["values"])
    return [f"{FORM_WARN} gauge: {n} bars on one gauge page - {n} capsules, each its own share of "
            f"{gauge_ceiling(page):g}{unit} ({shares}). A gauge reads ONE share of one whole; comparing "
            "shares is a bars page's job - use bars (USE-WHEN T34). REPORTED, the frame read decides (E99 s106)"] + out


def _validate_readability(series: dict, variant: str) -> list[str]:
    """Validate the closed chart-readability profile before it can enter ``page.axes``.

    The profile is intentionally a source-level option, like ``ylabel`` and ``name_clear``;
    the renderer narrows its effect to the stamped 16:9 full-stage dense-line route.  Rejecting
    unknown values here keeps a typo from silently selecting legacy geometry or typography.
    """
    value = series.get("readability")
    if value is None:
        return []
    err = readability_error(series, value, pick_builder(series, variant))
    return [err] if err else []


def readability_error(page: dict, value: Any, builder: str) -> str | None:
    """Is ``value`` a profile THIS page can take? The message, or None. Pure.

    ONE rule, read by the series file's own field (`_validate_readability`) and by the shot row's
    ``;readability=<profile>`` (the compiler, P69 T8): the profile is closed, each is legal only on the
    builders `READABILITY_BUILDERS` names (refused by name elsewhere), never on a host plate (whose board
    was measured around a hand), and a dense-line page must fit its enlarged end tags on the stage."""
    parsed = parse_readability(value)
    if parsed is None:
        return (f"readability {value!r} is not one of {LANDSCAPE_PHONE}|{LONGFORM}"
                f"[:{'|'.join(LONGFORM_PRESETS)}]")
    value, preset = parsed
    chrome = [k for k in (SOURCE_LINES_KEY, TITLE_STYLE_KEY) if k in page]
    if chrome and value != LONGFORM:   # P71 T30: the long form's chrome is never accepted and ignored
        return (f"{', '.join(chrome)}: the long form's chrome (P71 T30) - readability={value!r} draws this page in "
                f"another profile, which writes one plain source line and a plain title; draw it '{LONGFORM}' or drop "
                "the key")
    legal = READABILITY_BUILDERS[value]
    if builder not in legal:
        if value == LANDSCAPE_PHONE:
            return f"readability={value!r} is only supported by the dense-line builder; this page uses {builder!r}"
        return (f"readability={value!r} is only supported by the {' and '.join(legal)} builders "
                f"(a line page and a bars page); this page uses {builder!r}")
    # `full_stage` is a compiler stamp, not a series-file field: the normal 16:9 page route adds it
    # after this source validation, while portrait leaves it absent.  Explicit host-plate geometry
    # is nevertheless incompatible and must not silently accept an option the renderer ignores.
    if page.get("board") or page.get("chart_box") or page.get("punch") is False:
        if value == LANDSCAPE_PHONE:
            return "readability='landscape-phone' is only supported by a 16:9 full_stage dense-line page"
        return f"readability={value!r} is only supported by a 16:9 full_stage page (a host plate keeps its own board)"
    if builder == "dense-line" and value == LANDSCAPE_PHONE:
        return _readability_fit_error(dict(page, readability=value))
    if builder == "dense-line" and longform_tag_form(page, preset) is None:
        return (f"readability={LONGFORM}:{preset} cannot keep even its end values inside the 16:9 stage "
                "(a value alone is the shortest end tag there is)")
    return None


# P69 T10b (the operator, 2026-09-22, on the T6 frames: "I think it should also have some sort of rounded edges, maybe
# shadows"; AMENDED the same day: the shadow is the prop's own cross-hatch, T6b v2): `;bar_style=soft` - every bar of a
# bars page gets ROUNDED SHOULDERS (its two corners away from zero; the two on zero stay square, so a bar still stands
# on its baseline) and a HATCHED SHADOW cast from the one stage light (the player's `LPBAR_SOFT` and `PROP_SHADOW`).
# A row option, legal on the bars (`story`) builder only, and never beside `;form=extruded_bar` - the prism is the 3D
# bar; soft is weight on the flat one. Absent, a page is byte-identical.
BAR_STYLES = ("soft",)
BAR_STYLE_BUILDERS = ("story",)


def bar_style_error(page: dict, value: Any, builder: str) -> str | None:
    """Is ``value`` a bar style THIS page can take? The message, or None. Pure."""
    if value not in BAR_STYLES:
        return f"bar_style {value!r} is not one of {'|'.join(BAR_STYLES)}"
    if builder not in BAR_STYLE_BUILDERS:
        return (f"bar_style={value} is how a BARS page draws its bars (the {'|'.join(BAR_STYLE_BUILDERS)} builder); "
                f"this page uses {builder!r}")
    if ((page.get("form") or {}).get("kind")) == "extruded_bar":
        return (f"bar_style={value} and form=extruded_bar are two bars on one page - the prism is the 3D bar, soft is "
                "weight on the flat one. Keep one")
    if ((page.get("form") or {}).get("kind")) == "gauge" and (page.get("form") or {}).get("dir") == "h":   # P72 T6
        return (f"bar_style={value} and form=gauge:h - the soft bar's shoulders and its hatched shadow are laid for an "
                "upright bar under the one stage light, and the horizontal capsule lies on its side. Draw it flat, or "
                "draw the gauge vertical (form=gauge)")
    return None


# ---- P70 T2 (was P69 T46) / E99 s109 (1): THE SCHEMATIC - a shape drawn with no data, carrying the narrative ---------
# The operator, 2026-09-23: "I think we can draw with no data - that is the art and narrative coming to life in the
# world". s109 (1): a schematic (the hype cycle, the debt cycle, a mania arc, phase waves) "carries no axis values and no
# figures it cannot source, and says it is a shape, not a series". The Bravos harvest v2 T7 (n=5; Jw8ykhoOVBQ 04:24).
#   A LINE object carries `schematic: {shape, phases: [{name, from, to, side?}], n?, name?, color?}` IN PLACE OF
# `series`: `schematic_series` GENERATES one dense series from the named closed form - fixed N points, x in [0, 1],
# y in [0, 1], pure and deterministic - and the existing dense-line builder draws it, so T36's `lit_stretch`, `span` and
# `bracket` address it unchanged (a phase's `from` / `to` IS the x-fraction they take). The spec keeps `schematic`
# (shape, phases, the tag) so the player writes no value - no tick number on either axis, no end tag - and
# writes the TAG and the phase names instead. Data beside a schematic is refused (`series`, `pts`, `bars`, a unit, a
# rule, a tick, a domain ...): a schematic carries no data. A bracket, figure, note or span whose words carry a digit
# is refused on a schematic page unless it names its `src` (`schematic_text_errors`, a truth rule - hard).
#   E99 s125 (a REAL series laid over a schematic, on its own labelled axis) is P71's. Nothing here prevents it: the
# shape is `spec.series[0]` on x in [0, 1], and `spec.schematic` names its phases in the same fractions.
SCHEMATIC_KEY = "schematic"
SCHEMATIC_SHAPES = ("hype", "waves", "debt_cycle", "candles", "motif")   # P71 T20: + the two illustrations
SCHEMATIC_NAMES = {"hype": "Hype cycle", "waves": "Phase waves", "debt_cycle": "Debt cycle",
                   "candles": "Price action", "motif": "Motif"}   # the series' name (the record;
#   the page writes no end tag - the title names the one shape, s120 (3))
SCHEMATIC_N = 121                          # the generated points: x steps of 1/120 - a dense line, never a bars page
SCHEMATIC_N_RANGE = (STORY_MAX_VALUES + 1, 401)   # fewer than the story ceiling would read as a story page's values
SCHEMATIC_PHASES_MAX = 6
SCHEMATIC_NAME_MAX = 40
SCHEMATIC_FIELDS = ("shape", "phases", "n", "name", "color")
SCHEMATIC_PHASE_FIELDS = ("name", "from", "to", "side", "ink")   # P71 T20 / A55: + the phase's own ink (the comet paints it)
SCHEMATIC_SIDES = ("above", "below")      # a phase's name over or under the curve (absent: the engine's concavity rule)
SCHEMATIC_INKS = ("teal", "crimson", "cobalt", "amber")   # E67's electric inks (the engine's LP_CYCLE)
SCHEMATIC_INK = "teal"                    # declared, so the lone line never takes a SIGN colour: a shape rises, it gains nothing
SCHEMATIC_DOMAIN = (-0.45, 1.3)   # the page's y domain round the shape's [0, 1]: [DERIVED, the first frame read] room UNDER the
#                                   lowest stretch and OVER the peak for a two-line phase name at the s90 floor - never written
SCHEMATIC_TAG = "a shape, not a series"   # s109 (1): the page says what it is (s125 (3): it keeps it under a real series)
SCHEMATIC_BOX = "schematic"               # page_boxes' key for the tag's box
SCHEMATIC_RULING = "E99 s109 (1)"
SCHEMATIC_DATA_KEYS = ("series", "pts", "bars", "panels", "tiers", "shares", "props", "periods", "values", "unit",
                       "denominator", "line_unit", "members")
SCHEMATIC_AXES_KEPT = ("ylabel", "name_clear", "readability")   # words and the page's own profile; every other axes key is a value
SCHEMATIC_TEXT_SPECIES = {"bracket": ("label", "sub"), "figure": ("text", "sub"), "note": ("text",), "span": ("label",)}
DIGIT_RE = re.compile(r"\d")
# ---- P71 T20 (was P69 T62; the Bravos harvest v2 T8, T46, A14, A55) / E99 s109 (1): ILLUSTRATIONS DRAWN AS SCHEMATICS ----
#   `candles` (T8, BUB 04:47.3): candlestick bodies and wicks GENERATED along a GHOST wave - price action as an
# illustration, never a series. The line the page draws is the ghost (context: `deemph`, it never blooms, E99 s117); the
# candles ride it, each printing as the pen passes its x, green up / red down in the page's sign inks. `schematic_candles`
# generates them from the ghost (pure: an integer LCG jitters them, never a float hash), the spec carries them, the player
# draws them - no value is written, and the tag stays.
#   `motif` (T46, JPN 09:09-09:11 "Market"): an AXIS-FREE rising wave named by one word (the page's title): no axis rule,
# no tick, no label on either side - a `ylabel` beside it is refused by name. Its turning points are where a
# `datum_badge` lands (`vertex: k`, `schematic_vertices`) - the X at each named vertex.
#   A phase may name its `ink` (A55): a `lit_stretch` with `phase_ink: true` paints each phase it passes in that ink.
#   Neither illustration names phases (a price chart and a motif are not phase models): `phases` is optional on these two
# and still required on the three phase models.
SCHEMATIC_ILLUSTRATIONS = ("candles", "motif")   # phases optional: absent is none (an empty list is still refused)
SCHEMATIC_AXIS_FREE = ("motif",)                 # the player draws no axis rule (the spec block's `axis_free`)
SCHEMATIC_GHOST = "deemph"                       # the candles' ghost wave: context, never blooms (E99 s117)
SCHEMATIC_PHASE_INKS = SCHEMATIC_INKS + ("pos", "neg")   # A55: a phase's ink - E67's four, or a sign ink (BOOM 09:45-10:04 green / red)
SCHEMATIC_CANDLES = 30          # [MEASURED: ~30 candles across the panel, BUB 04:47.3 frame_0025.jpg]
SCHEMATIC_CANDLE_OC = 0.5       # open / close read off the ghost at the candle's pitch edges (a candle spans its own stretch of the wave)
SCHEMATIC_CANDLE_JITTER = 0.07  # [DERIVED, the frame read against BUB 04:47.3: bodies 7-17 % of the panel] a body's ends wander this far off the ghost (price action, not a trace)
SCHEMATIC_CANDLE_WICK = (0.015, 0.06)   # a wick reaches this far past its body (min, max; the LCG picks between)
SCHEMATIC_CANDLE_BODY_MIN = 0.025        # a body never thinner than this (a doji would hide its colour: the first frame read drew "+" marks)
SCHEMATIC_CANDLE_SEED = 7120             # the LCG's seed (P71 T20): fixed, so the same object draws the same candles
SCHEMATIC_ILLUSTRATION_DOMAIN = (-0.08, 1.08)   # [DERIVED, the first frame read] an illustration that names no phase needs no room
#                                          for names: the shape fills its plot (JPN 09:09's motif fills its panel)


def _smooth01(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * (3.0 - 2.0 * u)


def _hype_y(x: float) -> float:
    """Gartner's hype cycle: a Gaussian peak of expectations over a logistic rise to the plateau (the trough between)."""
    return 0.06 + 0.84 * math.exp(-((x - 0.2) / 0.085) ** 2) + 0.5 / (1.0 + math.exp(-(x - 0.6) / 0.07))


def _waves_y(x: float) -> float:
    """Phase waves: two whole cycles from a trough, the phases the author names on them."""
    return 0.5 - 0.4 * math.cos(4.0 * math.pi * x)


def _debt_cycle_y(x: float) -> float:
    """The long-term debt cycle: short cycles riding a rising burden to the top, then the deleveraging and a floor."""
    rise = 0.12 + 0.72 * (min(x, 0.8) / 0.8) ** 1.6
    fall = 0.5 * _smooth01((x - 0.8) / 0.1) - 0.12 * _smooth01((x - 0.9) / 0.1)
    return rise - fall + 0.04 * math.sin(12.0 * math.pi * x) * (1.0 - 0.6 * _smooth01((x - 0.8) / 0.1))


def _candles_y(x: float) -> float:
    """The candles' GHOST wave: one and a half cycles from a trough (BUB 04:35-04:47's sine, left faded under the candles)."""
    return 0.5 - 0.3 * math.cos(3.0 * math.pi * x)


def _motif_y(x: float) -> float:
    """The motif: a wave of growing swings on a rising trend, from a trough at the bottom-left to past its last peak on a
    rise (JPN 09:09 "Market") - eight interior turning points."""
    return 0.1 + 0.55 * x - (0.1 + 0.12 * x) * math.cos(2.0 * math.pi * 4.4 * x)


SCHEMATIC_FORMS = {"hype": _hype_y, "waves": _waves_y, "debt_cycle": _debt_cycle_y, "candles": _candles_y, "motif": _motif_y}


def schematic_series(schematic: dict) -> dict:
    """The ONE series a schematic draws: its closed form sampled at n points on x in [0, 1] (4 dp). No `label` (no value);
    its `name` is the series' own for the record - the player writes no end tag on a schematic. Pure and deterministic."""
    n = int(schematic.get("n") or SCHEMATIC_N)
    f = SCHEMATIC_FORMS[str(schematic["shape"])]
    xs = [i / (n - 1) for i in range(n)]
    ghost = str(schematic["shape"]) == "candles"   # P71 T20: the candles' line is their ghost - context, never an ink of its own
    return {"name": str(schematic.get("name") or SCHEMATIC_NAMES[str(schematic["shape"])]),
            "color": SCHEMATIC_GHOST if ghost else str(schematic.get("color") or SCHEMATIC_INK),
            "pts": [[round(x, 4), round(min(1.0, max(0.0, f(x))), 4)] for x in xs]}


def schematic_vertices(schematic: dict) -> list[int]:
    """P71 T20: the generated series' INTERIOR turning points, as indices into its points - where the slope changes sign
    (a flat run turns at its first point). The player reads the same rule off the same numbers (lpSchematicVertices), so a
    `datum_badge` naming `vertex: k` lands on the k-th. Pure."""
    return series_vertices(schematic_series(schematic)["pts"])


def series_vertices(pts: list) -> list[int]:
    """The interior turning points of a run of [x, y] points (schematic_vertices' rule, on any points): the index where the
    slope changes sign, a flat run turning at its first point. Pure."""
    out: list[int] = []
    sign, start = 0, 0   # the last non-zero slope's sign, and the index its run of flat steps began at
    for k in range(1, len(pts)):
        d = pts[k][1] - pts[k - 1][1]
        if d == 0:
            continue
        s = 1 if d > 0 else -1
        if sign and s != sign:
            out.append(start)
        sign, start = s, k
    return out


def _lcg(seed: int):
    """A 31-bit linear congruential generator: the same floats on every platform (no float hash, no `random` state)."""
    state = seed & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state / 2147483648.0


def schematic_candles(schematic: dict) -> list[list[float]]:
    """P71 T20: the candles along the ghost wave - [x, open, high, low, close] each (4 dp), SCHEMATIC_CANDLES of them
    centred on their pitch. Open and close are the ghost's own y SCHEMATIC_CANDLE_OC of a pitch before and after the
    centre, each wandering +-SCHEMATIC_CANDLE_JITTER; the wicks reach past the body; a body is never thinner than
    SCHEMATIC_CANDLE_BODY_MIN. Everything stays inside [0, 1] (the shape's room). Pure and deterministic."""
    n, r = SCHEMATIC_CANDLES, _lcg(SCHEMATIC_CANDLE_SEED)
    lo, hi = SCHEMATIC_CANDLE_WICK
    out: list[list[float]] = []
    for k in range(n):
        x = (k + 0.5) / n
        o = _candles_y(x - SCHEMATIC_CANDLE_OC / n) + (2.0 * next(r) - 1.0) * SCHEMATIC_CANDLE_JITTER
        c = _candles_y(x + SCHEMATIC_CANDLE_OC / n) + (2.0 * next(r) - 1.0) * SCHEMATIC_CANDLE_JITTER
        if abs(c - o) < SCHEMATIC_CANDLE_BODY_MIN:   # keep its colour readable: widen about the middle, the way it leaned
            m, s = (o + c) / 2.0, (1.0 if c >= o else -1.0)
            o, c = m - s * SCHEMATIC_CANDLE_BODY_MIN / 2.0, m + s * SCHEMATIC_CANDLE_BODY_MIN / 2.0
        o, c = _unit(o), _unit(c)
        h = _unit(max(o, c) + lo + (hi - lo) * next(r))
        low = _unit(min(o, c) - lo - (hi - lo) * next(r))
        out.append([round(x, 4), round(o, 4), round(h, 4), round(low, 4), round(c, 4)])
    return out


def _unit(v: float) -> float:
    return min(1.0, max(0.0, v))


def with_schematic(series: dict) -> dict:
    """The object with its schematic's generated series in place (a new dict), or the object itself when it names none."""
    sch = series.get(SCHEMATIC_KEY)
    if not isinstance(sch, dict) or sch.get("shape") not in SCHEMATIC_SHAPES:
        return series
    return {**series, "series": [schematic_series(sch)]}


def schematic_block(schematic: dict) -> dict:
    """The spec's `schematic`: the shape, its tag and its phases with their edges as numbers (the file's tokens read)."""
    phases = []
    for p in schematic.get("phases") or []:
        entry = {"name": str(p["name"]), "from": float(to_number(p["from"])), "to": float(to_number(p["to"]))}
        if p.get("side") in SCHEMATIC_SIDES:
            entry["side"] = p["side"]
        if p.get("ink") in SCHEMATIC_PHASE_INKS:   # P71 T20 / A55 (absent: not one key)
            entry["ink"] = p["ink"]
        phases.append(entry)
    block = {"shape": str(schematic["shape"]), "tag": SCHEMATIC_TAG, "phases": phases}
    if block["shape"] == "candles":   # P71 T20: the candles the player draws along the ghost (only on this shape)
        block["candles"] = schematic_candles(schematic)
    if block["shape"] in SCHEMATIC_AXIS_FREE:   # P71 T20: the motif draws no axis rule (only on this shape)
        block["axis_free"] = True
    return block


def schematic_domain(schematic: dict) -> tuple:
    """The page's y domain round the shape: SCHEMATIC_DOMAIN (room for the phase names), or - P71 T20 - an illustration
    that names no phase fills its plot (SCHEMATIC_ILLUSTRATION_DOMAIN)."""
    if schematic.get("shape") in SCHEMATIC_ILLUSTRATIONS and not schematic.get("phases"):
        return SCHEMATIC_ILLUSTRATION_DOMAIN
    return SCHEMATIC_DOMAIN


def _schematic_phase_errors(phases: Any) -> list[str]:
    if not isinstance(phases, list) or not 1 <= len(phases) <= SCHEMATIC_PHASES_MAX:
        return [f"schematic: phases must be a list of 1 to {SCHEMATIC_PHASES_MAX} {{name, from, to}} - the model's named "
                "stretches, each an x-fraction of the shape"]
    errs: list[str] = []
    prev_to = None
    for i, p in enumerate(phases):
        where = f"schematic: phases[{i}]"
        if not isinstance(p, dict):
            errs.append(f"{where} must be an object {{name, from, to}}")
            continue
        extra = sorted(k for k in p if k not in SCHEMATIC_PHASE_FIELDS)
        if extra:
            errs.append(f"{where}: {', '.join(map(repr, extra))} is not a phase key ({'|'.join(SCHEMATIC_PHASE_FIELDS)}) - "
                        f"a phase is a name over a stretch of the shape, never a value ({SCHEMATIC_RULING})")
        name = p.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > SCHEMATIC_NAME_MAX:
            errs.append(f"{where} needs a non-empty name of at most {SCHEMATIC_NAME_MAX} characters")
        edges = {}
        for f in ("from", "to"):
            v = to_number(p.get(f)) if not isinstance(p.get(f), bool) else None
            if v is None or not 0.0 <= v <= 1.0:
                errs.append(f"{where}: {f!r} must be an x-fraction of the shape (0..1)")
            else:
                edges[f] = v
        if len(edges) == 2:
            if not edges["from"] < edges["to"]:
                errs.append(f"{where}: from {value_string(p['from'])} is not before to {value_string(p['to'])} - a phase "
                            "is a stretch, not a point")
            elif prev_to is not None and edges["from"] < prev_to - 1e-9:
                errs.append(f"{where} ({name!r}) overlaps the phase before it: phases run in order along the shape, "
                            "each starting where (or after) the last one ends")
            prev_to = edges["to"]
        if "side" in p and p["side"] not in SCHEMATIC_SIDES:
            errs.append(f"{where}: side must be above or below (the name over or under the curve; absent = the "
                        "curve's own shape decides)")
        if "ink" in p and p["ink"] not in SCHEMATIC_PHASE_INKS:   # P71 T20 / A55
            errs.append(f"{where}: ink must be one of {'|'.join(SCHEMATIC_PHASE_INKS)} (the ink a `lit_stretch` with "
                        "`phase_ink` paints this phase in; absent = the light's own)")
    return errs


def _validate_schematic(series: dict, variant: str) -> list[str]:
    """P70 T2: the schematic object's own rules - a LINE page's shape, no data beside it, a closed key list."""
    sch = series.get(SCHEMATIC_KEY)
    if not isinstance(sch, dict):
        return [f"schematic must be an object {{shape, phases, n?, name?, color?}} ({SCHEMATIC_RULING})"]
    errs: list[str] = []
    if variant != "line":
        errs.append(f"a schematic is a LINE page's shape (variant line), and this page asks for {variant!r} "
                    f"({SCHEMATIC_RULING})")
    data = [k for k in SCHEMATIC_DATA_KEYS if k in series]
    if data:
        errs.append(f"{', '.join(map(repr, data))} beside a schematic: a schematic carries no data ({SCHEMATIC_RULING}) - "
                    "the shape is generated from its closed form; a measured series is a page of its own (laying one "
                    "over a shape is E99 s125's, P71)")
    axes = [k for k in AXES_KEYS if k in series and k not in SCHEMATIC_AXES_KEPT]
    if axes:
        errs.append(f"{', '.join(map(repr, axes))} on a schematic: a schematic carries no axis values "
                    f"({SCHEMATIC_RULING}) - it keeps only {'|'.join(SCHEMATIC_AXES_KEPT)}")
    extra = sorted(k for k in sch if k not in SCHEMATIC_FIELDS)
    if extra:
        errs += [f"schematic: {k!r} is not a schematic key ({'|'.join(SCHEMATIC_FIELDS)})" for k in extra]
    if sch.get("shape") not in SCHEMATIC_SHAPES:
        errs.append(f"schematic: shape {sch.get('shape')!r} is not one of {'|'.join(SCHEMATIC_SHAPES)}")
    n = sch.get("n")
    if n is not None and (isinstance(n, bool) or not isinstance(n, int) or not SCHEMATIC_N_RANGE[0] <= n < SCHEMATIC_N_RANGE[1]):
        errs.append(f"schematic: n must be an integer from {SCHEMATIC_N_RANGE[0]} to {SCHEMATIC_N_RANGE[1] - 1} (the "
                    f"generated points; absent = {SCHEMATIC_N})")
    if "name" in sch and not (isinstance(sch["name"], str) and sch["name"].strip()):
        errs.append("schematic: name must be a non-empty string (the series' name on record - never drawn; absent = the shape's own)")
    if "color" in sch and sch["color"] not in SCHEMATIC_INKS:
        errs.append(f"schematic: color must be one of {'|'.join(SCHEMATIC_INKS)} (absent = {SCHEMATIC_INK})")
    errs += _schematic_illustration_errors(series, sch)
    if sch.get("shape") in SCHEMATIC_ILLUSTRATIONS and "phases" not in sch:   # P71 T20: an illustration names no phases
        return errs
    return errs + _schematic_phase_errors(sch.get("phases"))


def _schematic_illustration_errors(series: dict, sch: dict) -> list[str]:
    """P71 T20: the two illustrations' own refusals, by name. A candles schematic's line is its ghost (context) and its
    bodies wear the sign inks, so it takes no `color`; the motif is axis-free, so a `ylabel` beside it has no axis."""
    errs: list[str] = []
    if sch.get("shape") == "candles" and "color" in sch:
        errs.append("schematic: a candles schematic takes no color - its line is the ghost wave (context, never "
                    "bloomed, E99 s117) and each candle wears the page's sign ink, up or down")
    if sch.get("shape") in SCHEMATIC_AXIS_FREE and "ylabel" in series:
        errs.append(f"'ylabel' beside a {sch.get('shape')}: the motif is axis-free - no axis rule, no tick, no label "
                    f"on either side; the page's title names it in one word ({SCHEMATIC_RULING})")
    return errs


def schematic_text_errors(page: dict, species: list) -> list[str]:
    """P70 T2 / E99 s109 (1) - "no figures it cannot source", a TRUTH rule (hard): on a schematic page, a bracket, figure,
    note or span whose words carry a digit is refused unless the species names its `src`. Words pass (a bracket may name
    a lag in words). A page with no schematic returns [] whatever its species write. Pure."""
    if not isinstance((page or {}).get(SCHEMATIC_KEY), dict):
        return []
    out: list[str] = []
    for sp in species or []:
        if not isinstance(sp, dict):
            continue
        kind = sp.get("kind")
        fields = SCHEMATIC_TEXT_SPECIES.get(kind)
        if not fields or _text(sp.get("src")):
            continue
        for f in fields:
            v = sp.get(f)
            if isinstance(v, str) and DIGIT_RE.search(v):
                out.append(f"{kind} at {sp.get('at')}: its {f} {v!r} writes a figure on a schematic - a schematic carries "
                           f"no figures it cannot source ({SCHEMATIC_RULING}): name the figure's `src` on the {kind}, or "
                           "say it in words")
    return out


def schematic_tag_box(plot: dict) -> dict:
    """The tag's box ESTIMATED from the plot (a page the fixture has not measured): the right half of the x tick band
    under the axis, where the player writes it - the band carries no tick on a schematic."""
    return _box(plot["x"] + plot["w"] / 2.0, plot["y"] + plot["h"] - XTICK_H, plot["w"] / 2.0, XTICK_H)


# ---- P71 T13 (was P69 T43b; R26-307, E99 s102): A SECOND AXIS, AND AN INVERTED ONE, FOR A CO-MOVEMENT CLAIM ---------
# R26-307: a page's `y2` was ACCEPTED AND IGNORED - validate returned [] and build_spec dropped it (E99 s106: "a silent drop
# is neither advice nor refusal"). It now DRAWS on the one builder with a draw path (a dense line page: the right axis in
# the engine's shared `lpRightAxis`, the block the combo's own right axis was lifted into) and is refused BY NAME on every
# other page. s102's three conditions are truth rules, so they refuse: (a) the page states its `claim`, co-movement or
# lead/lag; (b) each axis names its unit - the left by `ylabel`, the right by `unit` + `label` - and an inverted axis
# writes "inverted" beside its unit (`y2_header`); (c) each axis's ticks wear their own line's ink (the engine's, T37b's
# style fill). E28 binds every single-axis page: without `y2` not one key changes.
Y2_KEY = "y2"
Y2_FIELDS = ("series", "unit", "label", "invert")
Y2_CLAIMS = ("comove", "lead_lag")     # s102 (a): "these move together" / "this one leads that one"
Y2_RULING = "E99 s102"
Y2_INVERTED = "inverted"               # s102 (b): the word an inverted axis writes beside its unit
Y2_BOX = "y2"                          # page_boxes' key for the right axis's words (its ticks and its name)
Y2_BUILDER = "dense-line"
Y2_SIDES = ("LHS", "RHS")              # Bravos's own legend words ("S&P 500 (LHS)", "Dow Jones/S&P 500 (RHS)", BOOM 04:18)
Y2_AXES = ("left", "right")            # a y2 page's reference rule names the axis it is read on (`hlines[i].axis`)
Y2_HELD = {                            # page keys a second axis cannot follow yet - each refused by name
    "log": "the left axis is a log scale and the right is linear: one page, two laws of the y - not built",
    "break": "a broken x cuts both lines where the right axis's scale was fitted over the whole run - not built",
    SCHEMATIC_KEY: "a real series over a shape on its own axis is E99 s125's (P71 T39), through this slice's right axis",
    "form": "a 2.5D form lays the plot on a plane the right tick column does not follow - drawn flat",
}
Y2_TICK_ADV_EM = 0.58   # the chart face's mean figure advance, for the right column's ESTIMATED width (page_boxes' estimate)
Y2_GAP_U = 14.0         # the engine's LP_Y2.GAP: chart units between the plot's right edge and its right tick column


def y2_header(y2: dict) -> str:
    """The right axis's name as the page writes it over its ticks: its label, then its unit and - when inverted - the word
    (s102 (b): "an inverted axis says 'inverted' on the page"), e.g. "10-year yield (%, inverted)"."""
    unit = str(y2.get("unit") or "").strip()
    return f"{str(y2.get('label') or '').strip()} ({unit}{', ' + Y2_INVERTED if y2.get('invert') is True else ''})"


def y2_side(series: dict, i: int) -> str | None:
    """The axis series `i` is read on - "LHS", "RHS" or "RHS, inverted" - or None when the page has no second axis."""
    y2 = series.get(Y2_KEY)
    if not isinstance(y2, dict) or not isinstance(y2.get("series"), list):
        return None
    if i not in y2["series"]:
        return Y2_SIDES[0]
    return Y2_SIDES[1] + (f", {Y2_INVERTED}" if y2.get("invert") is True else "")


def _y2_index_errors(series: dict, idx: Any) -> list[str]:
    own = series.get("series") if isinstance(series.get("series"), list) else []
    live = [i for i, s in enumerate(own) if isinstance(s, dict) and "pts" in s and not s.get("later")]
    if not isinstance(idx, list) or not idx:
        return ["y2: series must be a non-empty list of the page's series indices (the lines read on the right axis)"]
    bad = [i for i in idx if isinstance(i, bool) or not isinstance(i, int) or i not in live]
    if bad:
        return [f"y2: series {bad!r} - not one of the page's drawn series ({live}); a second axis names the lines it carries"]
    if len(set(idx)) != len(idx):
        return [f"y2: series {idx!r} names a series twice"]
    if not set(live) - set(idx):
        return ["y2: every series is on the right axis - at least one line stays on the left (a page of one axis is "
                "drawn without y2)"]
    return []


def _y2_nested_errors(series: dict) -> list[str]:
    """A `y2` inside a series or a panel: an unbuilt path, refused by name (R26-307) - never dropped."""
    errs = [f"series {i}: `y2` belongs to the PAGE (`y2: {{series: [{i}], ...}}`) - a series naming its own second axis is "
            "not built (R26-307)" for i, q in enumerate(series.get("series") or []) if isinstance(q, dict) and Y2_KEY in q]
    for k, p in enumerate(series.get("panels") or []):
        if isinstance(p, dict) and (Y2_KEY in p or any(isinstance(q, dict) and Y2_KEY in q for q in p.get("series") or [])):
            errs.append(f"panel {k}: a second axis on a panel is not built (R26-307) - a y2 draws on a line page of its own")
    return errs


def _y2_rules(series: dict) -> list:
    return series.get("hlines") or ([series["hline"]] if isinstance(series.get("hline"), dict) else [])


def _y2_rule_errors(series: dict) -> list[str]:
    """A y2 page's reference rule is read on ONE of two scales, so it names which (`axis: left|right`) or it is refused -
    an unnamed rule would read on the wrong scale. On a single-axis page an `axis` names nothing drawn: refused too."""
    has_y2 = Y2_KEY in series
    errs = []
    for i, rule in enumerate(_y2_rules(series)):
        if not isinstance(rule, dict):
            continue
        if has_y2 and rule.get("axis") not in Y2_AXES:
            errs.append(f"hlines[{i}] on a y2 page: a rule names the axis it is read on - axis: {'|'.join(Y2_AXES)}, not "
                        f"{rule.get('axis')!r} ({Y2_RULING}: two scales, one rule)")
        elif not has_y2 and "axis" in rule:
            errs.append(f"hlines[{i}]: `axis` names a side of a second axis, and this page has no `y2` - one axis, one scale")
    return errs


def _validate_y2(series: dict, variant: str) -> list[str]:
    """R26-307 / s102: `y2` draws on a dense line page with its claim and both units named, or it is refused BY NAME.
    Without `y2` a co-movement `claim` or a page-level `invert` is refused as well (each names what it would need)."""
    y2, claim = series.get(Y2_KEY), series.get("claim")
    nested = _y2_nested_errors(series) + _y2_rule_errors(series)
    if Y2_KEY not in series:
        errs = nested
        if claim in Y2_CLAIMS:
            errs.append(f"claim {claim!r} is a second axis's claim ({Y2_RULING} (a)) and this page names no `y2` - a "
                        "co-movement drawn on one axis states nothing the page does not already draw")
        if "invert" in series:
            errs.append("`invert` belongs to the second axis: `y2: {series, unit, label, invert: true}` - a page-level "
                        "invert is refused by name (E28: a single axis's drops go DOWN)")
        return errs
    if not isinstance(y2, dict):
        return [f"y2 must be an object {{{', '.join(Y2_FIELDS)}?}} naming the lines drawn on a second (right) axis "
                f"({Y2_RULING})"]
    builder = SCHEMATIC_KEY if isinstance(series.get(SCHEMATIC_KEY), dict) else pick_builder(series, variant)
    if builder != Y2_BUILDER:
        return [f"y2 on a {builder} page: a second axis draws on a LINE page (dense-line) only (R26-307: a key nothing "
                "draws is refused by name, never dropped)" + ("; a combo's line names its own right axis with "
                                                              "`line_unit`" if builder == "combo" else "")]
    errs = nested + [f"y2: {k!r} is not a y2 key ({'|'.join(Y2_FIELDS)})" for k in sorted(y2) if k not in Y2_FIELDS]
    errs += [f"y2 with {k!r}: {why}" for k, why in Y2_HELD.items() if series.get(k) not in (None, False)]
    if "invert" in series:
        errs.append("`invert` beside y2 at the page's level: it belongs INSIDE the second axis, `y2: {..., invert: true}` "
                    "(the left axis is never inverted - E28)")
    if any(isinstance(s, dict) and s.get("later") for s in series.get("series") or []):
        errs.append("y2 with a `later` series: a line that joins on an extend is a chart state, and a y2 page takes none "
                    "(the right axis is fitted to the lines it carries)")
    errs += _y2_index_errors(series, y2.get("series"))
    if not _text(y2.get("unit")):
        errs.append(f"y2: unit is required - each axis names its unit ({Y2_RULING} (b); E28)")
    if not _text(y2.get("label")):
        errs.append(f"y2: label is required - the right axis's name, written over its ticks ({Y2_RULING} (b))")
    if "invert" in y2 and not isinstance(y2["invert"], bool):
        errs.append("y2: invert must be true or false (an inverted axis writes 'inverted' beside its unit)")
    if claim is None:
        errs.append(f"y2 without a claim: a second axis is allowed only when the claim is co-movement or lead/lag - name "
                    f"it, `claim: {'|'.join(Y2_CLAIMS)}` ({Y2_RULING} (a)); a level or a change stays on one axis (E28)")
    elif claim not in Y2_CLAIMS:
        errs.append(f"y2: claim {claim!r} is not one of {'|'.join(Y2_CLAIMS)} ({Y2_RULING} (a): a level or a change "
                    "stays on one axis, E28)")
    if not _text(series.get("ylabel")):
        errs.append(f"y2 without a ylabel: the LEFT axis names its unit too ({Y2_RULING} (b); E28) - the page writes it "
                    "over the left ticks")
    return errs


def y2_block(series: dict) -> dict:
    """The spec's `y2`: the right axis's lines, its unit, its label, whether it is inverted, the claim, and the header the
    page writes (one string, read by the engine and by page_boxes' estimate)."""
    y2 = series[Y2_KEY]
    return {"series": [int(i) for i in y2["series"]], "unit": str(y2["unit"]).strip(), "label": str(y2["label"]).strip(),
            "invert": y2.get("invert") is True, "claim": str(series["claim"]), "header": y2_header(y2)}


def _y2_left_names_unit(series: dict, unit: str) -> bool:
    """The left axis is in `unit`: its `unit` / `yunit`, or its `ylabel` writing the unit as a word of its own ("10-year
    yield, %", "rate (%)") - the ylabel is the field y2 requires, so the one that most often carries the unit."""
    if unit in (str(series.get("unit") or "").strip(), str(series.get("yunit") or "").strip()):
        return True
    return bool(re.search(r"(^|[\s,(])" + re.escape(unit) + r"($|[\s,)])", str(series.get("ylabel") or "")))


def y2_warnings(series: dict) -> list[str]:
    """s106: WARNs, not refusals - (1) both axes in ONE unit put one measure on two scales (E75 s3: the gap between the
    lines reads as a difference it is not; s102 allows it for co-movement, Bravos DOM 01:00: two yields, two scales);
    (2) a right-axis line drawn MUTED: the right axis is fitted to a line the page shows as context."""
    y2 = series.get(Y2_KEY)
    if not isinstance(y2, dict):
        return []
    out, unit = [], str(y2.get("unit") or "").strip()
    if unit and _y2_left_names_unit(series, unit):
        out.append(f"{FORM_WARN} y2: both axes are in {unit!r} - one measure on two scales, so the gap between the lines is "
                   f"not a reading (E75 s3); {Y2_RULING} allows it for a {series.get('claim')!r} claim - the frame read decides")
    own = series.get("series") or []
    muted = [i for i in y2.get("series") or [] if isinstance(i, int) and 0 <= i < len(own)
             and isinstance(own[i], dict) and own[i].get("muted")]
    if muted:
        out.append(f"{FORM_WARN} y2: series {muted} on the right axis {'is' if len(muted) == 1 else 'are'} drawn muted - the "
                   "axis's scale and ink come from a line the page shows as context")
    return out


def y2_extent(spec: dict) -> list[float] | None:
    """The right axis's data extent (its lines' values), which sizes its tick column - the one data a y2 page's boxes
    depend on, so the ink key carries it."""
    y2 = spec.get(Y2_KEY)
    if not isinstance(y2, dict):
        return None
    own = spec.get("series") or []
    vals = [float(to_number(v)) for i in y2.get("series") or [] if 0 <= i < len(own)
            for _x, v in (own[i] or {}).get("pts") or [] if to_number(v) is not None]
    return [round(min(vals), 6), round(max(vals), 6)] if vals else None


def y2_axis_box(spec: dict, plot: dict, aspect: str) -> dict:
    """The right axis's box ESTIMATED (a page the fixture has not measured): its tick column right of the plot, as wide as
    its widest tick written in the unit, from the plot's top (its name over it) to its bottom."""
    y2 = spec[Y2_KEY]
    ext = y2_extent(spec) or [0.0, 1.0]
    chars = max(len(f"{v:g}") for v in ext) + len(str(y2.get("unit") or ""))
    k = STAGE_PX[aspect][0] / LAND_VIEWBOX[0]
    px = LAND_PHONE_FONT_PX if aspect == "9:16" else 24.0 * k
    w = chars * Y2_TICK_ADV_EM * px + Y2_GAP_U * k
    return _box(plot["x"] + plot["w"], plot["y"] - px, w, plot["h"] + px)


# ---- P71 T16 (was P69 T41; harvest v2 A17 / T23 / S3; E77, E99 s93): `project` - A LABELLED DASHED CONTINUATION -------
# A `later: true` series of a dense line page may carry `projection: {label, tier, src}`: an ESTIMATE past the last
# real point, drawn on its word by `chart_to extend {series: k}` FROM the last actual datum of the line it continues -
# dashed (S3: every dashed series is a projection, BOOM 03:18 / 17:59.5 / 18:52), in its line's ink, never blooming
# (s117: context, not a primary line), its end tag writing its LABEL and the page's source line naming it and its source
# (s93: "its source line says what it is"). E77 / an estimate is never data: the refusals below are TRUTH rules (s106) -
# an unlabelled, untiered or unsourced projection, a label that is a bare figure (it reads as a datum), and a path that
# does not open from the real line. The compiler refuses any mark that would read the projected stretch as a datum
# (`build_scene_timeline_f.check_projection`). A label with no estimate word is advice (WARN, s106).
PROJECTION_KEY = "projection"
PROJECTION_FIELDS = ("label", "tier", "src")
PROJECTION_TIERS = ("CONFIRMED", "PLAUSIBLE", "DERIVED", "scenario")   # the research gate's two usable tiers, our derived
                                                                       # layer (E77), or the sentence's own "if"
PROJECTION_RULING = "E77 / E99 s93"
# A label that is a figure and nothing else ("$150B", "+24%", "1,250", "$130-150B") reads as a DATUM on the page.
PROJECTION_FIGURE_RE = re.compile(r"^[\s$£€¥+\-−–~≈]*[\d.,]+(\s*[–\-]\s*[\d.,]+)?\s*[%xX×]?\s*([kKmMbBtT]|bn|tn)?\s*$")
# ... and a label reads as a projection when it carries an estimate word (else the WARN names it).
PROJECTION_WORDS_RE = re.compile(r"\d{2,4}E\b|\best\b|estimat|consensus|forecast|project|scenario|guidance|target|"
                                 r"expect|outlook|trend|\bif\b|could|would|may\b|path|pace", re.IGNORECASE)


def _projection_actual(own: list, i: int) -> int | None:
    """The live line series `i`'s projection continues: the first standing (not `later`, not a projection) series whose
    LAST datum is the projection's FIRST point, exactly (the page's own tokens, read as numbers)."""
    pts = _points(own[i])
    if not pts:
        return None
    x0, y0 = to_number(pts[0][0]), to_number(pts[0][1])
    for j, s in enumerate(own):
        if j == i or not isinstance(s, dict) or s.get("later") or PROJECTION_KEY in s:
            continue
        sp = _points(s)
        if sp and x0 is not None and y0 is not None and to_number(sp[-1][0]) == x0 and to_number(sp[-1][1]) == y0:
            return j
    return None


def _projection_field_errors(where: str, proj) -> list[str]:
    if not isinstance(proj, dict):
        return [f"{where}: a projection is an object {{label, tier, src}} ({PROJECTION_RULING}: an estimate is labelled, "
                f"tiered and sourced), not {proj!r}"]
    errs = [f"{where}: `{k}` is not a projection key ({'|'.join(PROJECTION_FIELDS)}) - a projection carries no value of "
            "its own: its points are its series' (E77)" for k in proj if k not in PROJECTION_FIELDS]
    label = proj.get("label")
    if not _text(label):
        errs.append(f"{where}: a projection with no `label` - an estimate is labelled as one on the page "
                    f"({PROJECTION_RULING}: '2026E', 'consensus')")
    elif PROJECTION_FIGURE_RE.match(label):
        errs.append(f"{where}: the label {label!r} is a bare figure - it reads as a datum on the page; name the estimate "
                    f"('2026E', 'consensus') ({PROJECTION_RULING})")
    if proj.get("tier") not in PROJECTION_TIERS:
        errs.append(f"{where}: a projection's `tier` is one of {'|'.join(PROJECTION_TIERS)}, not {proj.get('tier')!r} - "
                    f"the tier rides the object ({PROJECTION_RULING})")
    if not _text(proj.get("src")):
        errs.append(f"{where}: a projection with no `src` - its source line says what it is and where it comes from "
                    f"({PROJECTION_RULING})")
    return errs


def _projection_path_errors(where: str, own: list, i: int) -> list[str]:
    s, errs = own[i], []
    if i == 0:
        errs.append(f"{where}: the page's first series is its line, never a projection - a projection continues a live "
                    "line from its last datum")
    if s.get("later") is not True:
        errs.append(f"{where}: a projection draws on its word - it is a `later: true` series drawn by "
                    "`chart_to extend {series: k}`")
    pts = _points(s)
    xs = [to_number(p[0]) for p in pts]
    if len(pts) < 2 or any(x is None for x in xs) or any(b <= a for a, b in zip(xs, xs[1:])):
        errs.append(f"{where}: a projection runs forward from the last actual - two or more points, each x past the one "
                    "before it")
    if pts and _projection_actual(own, i) is None:
        errs.append(f"{where}: its first point {list(pts[0])} is not the last actual of a live line - the path opens from "
                    f"the real line, never from nowhere ({PROJECTION_RULING})")
    return errs


def _validate_projection(series: dict, variant: str) -> list[str]:
    """P71 T16: `projection` on a later series of a dense line page, whole and truthful, or refused BY NAME (s106: never
    accepted and ignored, the key's state before this slice). [] when no series names it."""
    own = [s for s in series.get("series") or []]
    panel_hits = [(pi, si) for pi, p in enumerate(series.get("panels") or []) if isinstance(p, dict)
                  for si, s in enumerate(p.get("series") or []) if isinstance(s, dict) and PROJECTION_KEY in s]
    errs = [f"panels[{pi}].series[{si}]: a projection is not built on a panel - a panel's lines draw with the page's "
            "build and take no `extend` (P71 T16)" for pi, si in panel_hits]
    hits = [i for i, s in enumerate(own) if isinstance(s, dict) and PROJECTION_KEY in s]
    if not hits:
        return errs
    builder = pick_builder(series, variant)
    if builder != "dense-line":
        return errs + [f"series[{i}]: a projection draws on a dense line page's own line; this page draws as "
                       f"{builder!r} (P71 T16)" for i in hits]
    for i in hits:
        where = f"series[{i}] projection"
        errs += _projection_field_errors(where, own[i][PROJECTION_KEY])
        errs += _projection_path_errors(where, own, i)
    return errs


def projection_warnings(series: dict) -> list[str]:
    """s106 advice: a label that carries no estimate word ('2026E', 'consensus', 'forecast', 'if ...') may still read as
    a name; the frame read decides."""
    out = []
    for i, s in enumerate(series.get("series") or []):
        proj = s.get(PROJECTION_KEY) if isinstance(s, dict) else None
        if isinstance(proj, dict) and _text(proj.get("label")) and not PROJECTION_WORDS_RE.search(proj["label"]):
            out.append(f"{FORM_WARN} series[{i}] projection: the label {proj['label']!r} carries no estimate word - it "
                       "may read as a name, not an estimate ('2026E', 'consensus', 'forecast')")
    return out


def projection_source(series: dict) -> str | None:
    """The page's source line with each projection named and sourced (s93) - `<src> · <label>: <projection src>`; a
    projection whose source the line already names adds nothing. None when the file carries no projection."""
    src = series.get("src")
    projs = [s[PROJECTION_KEY] for s in series.get("series") or []
             if isinstance(s, dict) and isinstance(s.get(PROJECTION_KEY), dict)]
    if not projs or not isinstance(src, str):
        return None
    out = src
    for p in projs:
        if _text(p.get("src")) and p["src"] not in out:
            out += f" · {p.get('label')}: {p['src']}"
    return out


# ---- P71 T25 (was P69 T74; harvest v2 A50 / A51 / R31, Bravos D40 15:02-15:30): THE SCALE-OUT AND THE OVERTAKE --------
# D40, measured (P71 T25 step (0)): ONE bar ("Stablecoin Issuers (Today)", $120B) stands alone on its own 0-150 scale; on
# the word the view widens to the WHOLE FIELD of holders (the neighbours enter at the plot's edges, the scale runs to
# 1,200) and a pill names its place, "18th Largest Holder" - a rank COMPUTED from the field; later a NEW bar, "(2030)",
# surges past the field's leader and a bracket names the margin. Two object keys carry it, on a STORY bars page:
#   `opens_on: {bar: <label>, rank?: <phrase>}` - the page is BORN on that bar alone; `chart_to extend` (no key) brings
#       the field, and the pill writes "<ordinal> <phrase>" - the ordinal is computed here, never typed (a digit in the
#       phrase is refused; so is a word that ranks the other way, "smallest").
#   a bar `{label, projected: {value, label, tier, src}}` - a bar whose height IS a sourced projection: it carries no
#       `value` (an estimate is never a datum, E77), it is not drawn until `chart_to extend {bar: k}` names it, and it
#       stands DASHED with its label written (S3; C15). #1 is the tallest ACTUAL bar; the bracket's gap is computed.
# The refusals are TRUTH rules (s106): an unlabelled, untiered or unsourced projection, a label that is a bare figure, a
# `value` beside it, and a rank phrase that would contradict the computed ordinal. A projection that does not pass #1,
# a label with no estimate word and a tie at the subject's value are advice (WARN).
PROJECTED_FIELDS = ("value", "label", "tier", "src", "value_string")
PROJECTED_RULING = "E77 / C15 (P71 T25)"
OPENS_ON_KEY = "opens_on"
OPENS_ON_FIELDS = ("bar", "rank")
# a phrase that ranks the other way would print the wrong ordinal beside the right one: the rank is by value, largest first
RANK_OPPOSITE_RE = re.compile(r"\b(smallest|lowest|least|fewest|bottom|worst|last|minimum|min)\b", re.IGNORECASE)
RANK_DIGIT_RE = re.compile(r"\d")
# the page shapes neither key is drawn on: a bar with two ends, a stack, a membership, a breakthrough or a comparator
# rule each lay the field out by their own law, and a projection or a one-bar view on top of that is two laws at once
OUT_REFUSED_BESIDE = (("ranges", "a bar written as a range"), ("segments", "a stacked bar"), ("members", "a membership bar"))


def _own_bars_raw(series: dict) -> list:
    return [b for b in (series.get("bars") or []) if isinstance(b, dict)]


def with_projected_values(series: dict) -> dict:
    """The series with each projected bar's `value` its projection's (its HEIGHT is the projection); the input when
    no bar is projected - one object, not a copy, so every other page reads exactly as it did. Pure."""
    bars = series.get("bars")
    if not isinstance(bars, list) or not any(isinstance(b, dict) and isinstance(b.get(PROJECTED_KEY), dict) for b in bars):
        return series
    out = []
    for b in bars:
        if isinstance(b, dict) and isinstance(b.get(PROJECTED_KEY), dict) and "value" not in b:
            pj = b[PROJECTED_KEY]
            b = dict(b, value=pj.get("value_string", pj.get("value")))
        out.append(b)
    return dict(series, bars=out)


def _projected_index(series: dict) -> int | None:
    hits = [i for i, b in enumerate(_own_bars_raw(series)) if PROJECTED_KEY in b]
    return hits[0] if len(hits) == 1 else None


def _out_shape_errors(series: dict, where: str) -> list[str]:
    errs = []
    bars = _own_bars_raw(series)
    for key, what in OUT_REFUSED_BESIDE:
        hit = [j for j, b in enumerate(bars) if (bar_range(b) if key == "ranges" else b.get(key))]
        if hit:
            errs.append(f"{where}: not on a page with {what} (bars{hit}) - its field is laid out by its own law (P71 T25)")
    if series.get("overflow") is not None:
        errs.append(f"{where}: not on a breakthrough page (`overflow`) - the breakthrough rewrites the scale by its own "
                    "law (P71 T25)")
    return errs


def _validate_projected_bars(series: dict, variant: str) -> list[str]:
    """P71 T25: a `projected` bar, whole and truthful, or refused BY NAME (a bar key the form did not know was refused
    as unknown before this slice). [] when no bar names it."""
    nested = [(w, j) for w, bars in _bar_lists(series) if w for j, b in enumerate(bars)
              if isinstance(b, dict) and PROJECTED_KEY in b]
    errs = [f"{w}bars[{j}]: a projected bar stands in a page's OWN field - not a panel's or a tier's (P71 T25)"
            for w, j in nested]
    own = _own_bars_raw(series)
    hits = [i for i, b in enumerate(own) if PROJECTED_KEY in b]
    if not hits:
        return errs
    builder = pick_builder(with_projected_values(series), variant)
    if builder != "story":
        return errs + [f"bars[{i}]: a projected bar is drawn on a STORY bars page; this page draws as {builder!r} "
                       "(P71 T25)" for i in hits]
    if len(hits) > 1:
        errs.append(f"bars{hits}: ONE projected bar per page - the overtake is one estimate passing the field "
                    f"({PROJECTED_RULING})")
    for i in hits:
        where, pj = f"bars[{i}] projected", own[i][PROJECTED_KEY]
        if not isinstance(pj, dict):
            errs.append(f"{where}: a projection is an object {{value, label, tier, src}} ({PROJECTED_RULING})")
            continue
        errs += [f"{where}: `{k}` is not a projected bar's key ({'|'.join(PROJECTED_FIELDS)})" for k in pj
                 if k not in PROJECTED_FIELDS]
        if "value" in own[i]:
            errs.append(f"bars[{i}]: a projected bar's height IS its projection - `projected.value`, and no `value` "
                        f"beside it (an estimate is never a datum, {PROJECTED_RULING})")
        v = to_number(pj.get("value"))
        if v is None or not math.isfinite(v):
            errs.append(f"{where}: `value` {pj.get('value')!r} is not a number - the height the estimate is drawn to")
        elif v <= 0:
            errs.append(f"{where}: `value` {pj.get('value')!r} - a projected bar surges UP from the zero line past the "
                        "field; an estimate at or under zero is a page of its own")
        errs += _projection_field_errors(where, {k: pj[k] for k in PROJECTION_FIELDS if k in pj})
        if not any(j != i and to_number(b.get("value")) is not None for j, b in enumerate(own)):
            errs.append(f"bars[{i}]: a projected bar needs a FIELD of actual bars beside it - there is no #1 to "
                        "overtake (P71 T25)")
        errs += _out_shape_errors(series, where)
    return errs


def _validate_opens_on(series: dict, variant: str) -> list[str]:
    """P71 T25: `opens_on` names the ONE actual bar the page is born on, and the phrase its rank is written in - or it
    is refused BY NAME (the key was accepted and ignored before this slice). [] when absent."""
    if OPENS_ON_KEY not in series:
        return []
    oo, where = series[OPENS_ON_KEY], OPENS_ON_KEY
    if not isinstance(oo, dict):
        return [f"{where}: an object {{bar: <label>, rank?: <phrase>}} - the bar the page opens on, alone (P71 T25)"]
    errs = [f"{where}: `{k}` is not an opens_on key ({'|'.join(OPENS_ON_FIELDS)})" for k in oo if k not in OPENS_ON_FIELDS]
    builder = pick_builder(with_projected_values(series), variant)
    if builder != "story":
        errs.append(f"{where}: a page opens on one bar of a STORY bars page; this page draws as {builder!r} (P71 T25)")
    own = _own_bars_raw(series)
    labels = [b.get("label") for b in own]
    if not _text(oo.get("bar")) or oo.get("bar") not in labels:
        errs.append(f"{where}: bar {oo.get('bar')!r} is not a bar on this page ({labels}) - it names a bar by its label")
    elif PROJECTED_KEY in own[labels.index(oo["bar"])]:
        errs.append(f"{where}: bar {oo['bar']!r} is the projection - a page opens on an ACTUAL bar ({PROJECTED_RULING})")
    if len([b for b in own if PROJECTED_KEY not in b]) < 2:
        errs.append(f"{where}: a page of one actual bar has no field to open onto (P71 T25)")
    if "rank" in oo:
        r = oo["rank"]
        if not _text(r):
            errs.append(f"{where}: rank is the phrase the computed ordinal is written with ('largest holder') - a "
                        "non-empty string")
        elif RANK_DIGIT_RE.search(r):
            errs.append(f"{where}: rank {r!r} carries a figure - the ordinal is COMPUTED from the field and written "
                        "before the phrase, never typed (P71 T25)")
        elif RANK_OPPOSITE_RE.search(r):
            errs.append(f"{where}: rank {r!r} ranks the other way - the ordinal is by value, LARGEST first, so the "
                        "phrase would contradict its own number (P71 T25)")
    if series.get("hlines") or series.get("hline"):
        errs.append(f"{where}: not on a page with a comparator rule - the rule is a later beat, on the field (P71 T25)")
    errs += _out_shape_errors(series, where)
    return errs


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _decimal(token: Any):
    import decimal
    try:
        return decimal.Decimal(str(token))
    except (decimal.InvalidOperation, ValueError):
        return None


def _decimal_text(d) -> str:
    t = format(d.normalize(), "f")
    return t[:-2] if t.endswith(".0") else t


def bars_out_block(series: dict) -> dict:
    """The spec keys a STORY page's `opens_on` / projected bar compile to - {} when it names neither (every other page
    is the bytes it was). `opens_on: {index, rank, of, text?}` - rank = 1 + the ACTUAL bars strictly taller; `projected`
    per bar (None, or {label, tier, src}); `projected_to: {index, lead, gap, text}` - #1 the tallest actual bar, the gap
    the projection less #1 in the page's own unit, signed. Pure."""
    own = _own_bars_raw(series)
    k = _projected_index(series)
    out: dict[str, Any] = {}
    actual = [(j, to_number(b.get("value"))) for j, b in enumerate(own) if PROJECTED_KEY not in b]
    actual = [(j, v) for j, v in actual if v is not None]
    if isinstance(series.get(OPENS_ON_KEY), dict):
        oo = series[OPENS_ON_KEY]
        idx = next(j for j, b in enumerate(own) if b.get("label") == oo.get("bar"))
        v = to_number(own[idx].get("value"))
        rank = 1 + sum(1 for j, w in actual if j != idx and w > v)
        out[OPENS_ON_KEY] = {"index": idx, "rank": rank, "of": len(actual),
                             **({"text": f"{_ordinal(rank)} {oo['rank'].strip()}"} if _text(oo.get("rank")) else {})}
    if k is not None:
        pj = own[k][PROJECTED_KEY]
        out[PROJECTED_KEY] = [({"label": str(pj.get("label")), "tier": pj.get("tier"), "src": pj.get("src")}
                               if j == k else None) for j in range(len(own))]
        lead = max(actual, key=lambda jv: (jv[1], -jv[0]))[0]   # the tallest actual bar; a tie goes to the first
        dp, dl = _decimal(pj.get("value_string", pj.get("value"))), _decimal(own[lead].get("value_string", own[lead].get("value")))
        gap = (dp - dl) if dp is not None and dl is not None else None
        unit, suffix = str(series.get("unit") or ""), series.get(UNIT_SUFFIX_KEY) if isinstance(series.get(UNIT_SUFFIX_KEY), str) else ""
        text = None
        if gap is not None:
            body = with_unit(_decimal_text(abs(gap)), unit, suffix or "")
            text = ("+" if gap > 0 else "-" if gap < 0 else "") + body
        out["projected_to"] = {"index": k, "lead": lead, "gap": float(gap) if gap is not None else None, "text": text}
    return out


def projected_source(series: dict) -> str | None:
    """The page's source line with its projected bar named and sourced (s93, T16's form) - None when no bar is
    projected, or its source is already on the line."""
    k, src = _projected_index(series), series.get("src")
    if k is None or not isinstance(src, str):
        return None
    pj = _own_bars_raw(series)[k].get(PROJECTED_KEY)
    if not isinstance(pj, dict) or not _text(pj.get("src")) or pj["src"] in src:
        return None
    return src + f" · {pj.get('label')}: {pj['src']}"


def bars_out_warnings(series: dict) -> list[str]:
    """s106 advice on the scale-out and the overtake: a projection that does not pass #1, a projection label with no
    estimate word, and a tie at the subject's value (two bars share its ordinal)."""
    out, own = [], _own_bars_raw(series)
    blk = bars_out_block(series)
    pt = blk.get("projected_to")
    if pt and pt.get("gap") is not None and pt["gap"] <= 0:
        out.append(f"{FORM_WARN} bars[{pt['index']}] projected: {pt['text']} against #1 ({own[pt['lead']].get('label')!r}) - "
                   "the projection does not pass the leader; the bracket writes the gap, and the sentence must not say "
                   "it overtakes")
    k = _projected_index(series)
    if k is not None:
        lab = (own[k].get(PROJECTED_KEY) or {}).get("label")
        if _text(lab) and not PROJECTION_WORDS_RE.search(lab):
            out.append(f"{FORM_WARN} bars[{k}] projected: the label {lab!r} carries no estimate word - it may read as a "
                       "name, not an estimate ('2030E', 'consensus', 'forecast')")
    oo = blk.get(OPENS_ON_KEY)
    if oo:
        v = to_number(own[oo["index"]].get("value"))
        ties = [b.get("label") for j, b in enumerate(own) if j != oo["index"] and PROJECTED_KEY not in b
                and to_number(b.get("value")) == v]
        if ties:
            out.append(f"{FORM_WARN} opens_on: {own[oo['index']].get('label')!r} ties {ties} at {v:g} - the "
                       f"{_ordinal(oo['rank'])} is shared")
    return out


def _source_lines_ok(value: Any) -> bool:
    """Is `value` the two-line source's shape - exactly two non-empty strings? Pure."""
    return (isinstance(value, list) and len(value) == SOURCE_LINES_N
            and all(isinstance(x, str) and x.strip() for x in value))


def _validate_longform_chrome(series: dict) -> list[str]:
    """P71 T30: `source_lines` and `title_style`, each refused BY NAME when malformed or placed off the long form (the
    base accepted and ignored both). The two lines must carry the page's `src` and every projection's own source -
    the words its provenance names - so the two-line form never cites less than the one line did. A file naming
    another profile is refused by `readability_error`; one naming none is refused here. Pure."""
    named = [k for k in (SOURCE_LINES_KEY, TITLE_STYLE_KEY) if k in series]
    if not named:
        return []
    errors: list[str] = []
    if SOURCE_LINES_KEY in series:
        lines = series[SOURCE_LINES_KEY]
        if not _source_lines_ok(lines):
            errors.append(f"{SOURCE_LINES_KEY} {lines!r} is not the two-line source: exactly {SOURCE_LINES_N} non-empty "
                          "strings, 'Date: ...' then 'Source: ...' (BRAVOS-LONGFORM-CHART-SPEC.md (b), P71 T30)")
        else:
            said = " ".join(lines)
            owed = [series.get("src")] + [s[PROJECTION_KEY].get("src") for s in series.get("series") or []
                                          if isinstance(s, dict) and isinstance(s.get(PROJECTION_KEY), dict)]
            missing = [x for x in owed if _text(x) and x not in said]
            if missing:
                errors.append(f"{SOURCE_LINES_KEY} never names {', '.join(repr(x) for x in missing)} - the two lines are "
                              "the page's source, so they carry its src and each projection's source word for word")
    if TITLE_STYLE_KEY in series and series[TITLE_STYLE_KEY] not in TITLE_STYLES:
        errors.append(f"{TITLE_STYLE_KEY} {series[TITLE_STYLE_KEY]!r} is not one of {'|'.join(TITLE_STYLES)} "
                      "(the title in the page's accent capsule, P71 T30)")
    if (series.get("readability") or (series.get("axes") or {}).get("readability")) is None:
        errors.append(f"{', '.join(named)}: the long form's chrome (P71 T30) - this series file names no profile; give "
                      f"it readability '{LONGFORM}' (a long form page) or drop the key")
    return errors


# ---- P71 T28 (was P69 T76; harvest v2 A21, n=3: HIS 05:58 "red after the peak", BUB 19:45, BOOM (G)): THE LINE CHANGES
# INK AT A POINT. A dense line page's series may carry `ink_from: {x, color}`: from x on, its stroke is drawn in the new
# ink - the stroke AND its bloom (P69 T37b's layers, s117) - so the stretch past x draws in it on the word that draws it
# (the page's own build, or the `build_to` that crosses x: H row 9's "crashed"). `color` is E67's four electric inks or a
# SIGN ink (pos / neg, the phase ink's own list, P71 T20); absent, the stretch takes its SIGN (E28: a rise green, a fall
# blood red). E53 s7: a declared colour outranks the default - but only where it does not lie (E28, "sign is colour too"):
# a sign ink on the wrong sign is refused with its numbers. Byte-identical absent the key.
INK_FROM_KEY = "ink_from"
INK_FROM_FIELDS = ("x", "color")
INK_FROM_INKS = SCHEMATIC_PHASE_INKS   # teal|crimson|cobalt|amber|pos|neg
INK_FROM_SIGN = {"pos": 1, "neg": -1}
INK_FROM_RULING = "E28 / E53 s7"


def _value_at(pts: list, x: float) -> float | None:
    """The series' value at x, read along its own straight segments (the stroke the page draws). Pure."""
    xy = [(to_number(p[0]), to_number(p[1])) for p in pts]
    for (xa, ya), (xb, yb) in zip(xy, xy[1:]):
        if None in (xa, ya, xb, yb):
            return None
        if xa <= x <= xb:
            return ya if xb == xa else ya + (yb - ya) * (x - xa) / (xb - xa)
    return None


def ink_from_sign(series_entry: dict) -> tuple[int, float, float] | None:
    """The stretch from `ink_from.x` to the series' last datum: its sign (+1 rises, -1 falls, 0 flat), its value at x
    and its last value - E28's read, end against start. None when x is off the line. Pure."""
    inkf, pts = series_entry.get(INK_FROM_KEY), _points(series_entry)
    x = to_number(inkf.get("x")) if isinstance(inkf, dict) else None
    if x is None or not pts:
        return None
    v0, v1 = _value_at(pts, x), to_number(pts[-1][1])
    if v0 is None or v1 is None:
        return None
    return (1 if v1 > v0 else -1 if v1 < v0 else 0), v0, v1


def ink_from_color(series_entry: dict) -> str | None:
    """The ink the stretch past x is drawn in: the declared one, else the stretch's sign ink (None: flat). Pure."""
    inkf = series_entry.get(INK_FROM_KEY)
    if not isinstance(inkf, dict):
        return None
    if inkf.get("color") is not None:
        return inkf["color"]
    sign = ink_from_sign(series_entry)
    return None if not sign or sign[0] == 0 else ("pos" if sign[0] > 0 else "neg")


def _ink_from_errors(where: str, s: dict) -> list[str]:
    inkf = s[INK_FROM_KEY]
    if not isinstance(inkf, dict):
        return [f"{where}: ink_from is an object {{x, color?}} - the x the stroke changes ink at, and its new ink "
                f"({'|'.join(INK_FROM_INKS)}; absent, the stretch's sign) - not {inkf!r}"]
    errs = [f"{where}: `{k}` is not an ink_from key ({'|'.join(INK_FROM_FIELDS)})" for k in inkf if k not in INK_FROM_FIELDS]
    if s.get(PROJECTION_KEY) is not None:
        errs.append(f"{where}: a projection never changes ink - an estimate is context, drawn dashed in its line's ink "
                    "(P71 T16, E77)")
    raw, pts = inkf.get("x"), _points(s)
    x = None if isinstance(raw, bool) else to_number(raw)   # a series file's numbers load as tokens (load_series)
    xs = [to_number(p[0]) for p in pts]
    if x is None:
        errs.append(f"{where}: ink_from.x must be a number on the series' own x (a date the line passes), not {raw!r}")
    elif len(xs) < 2 or None in xs or not xs[0] < x < xs[-1]:
        span = f"{xs[0]}..{xs[-1]}" if len(xs) >= 2 and None not in (xs[0], xs[-1]) else "no x span"
        errs.append(f"{where}: ink_from.x {x} is not inside the line ({span}) - the ink changes AT A POINT the line "
                    "passes; a whole line in one ink is its `color`")
    col = inkf.get("color")
    if col is not None and col not in INK_FROM_INKS:
        errs.append(f"{where}: ink_from.color must be one of {'|'.join(INK_FROM_INKS)} (E67's inks or a sign ink), "
                    f"not {col!r}")
    if errs:
        return errs
    sign, v0, v1 = ink_from_sign(s)
    if col in INK_FROM_SIGN and INK_FROM_SIGN[col] != sign:
        moves = "rises" if sign > 0 else "falls" if sign < 0 else "neither rises nor falls"
        errs.append(f"{where}: ink_from paints the stretch from x {x} in the {col} ink, and it {moves} "
                    f"({value_string(round(v0, 4))} -> {value_string(v1)}) - a sign ink on the wrong sign lies "
                    f"({INK_FROM_RULING}: a drop is blood red, a rise green); name an electric ink, or drop the colour "
                    "for the stretch's own sign")
    if col is None and sign == 0:
        errs.append(f"{where}: ink_from names no colour and the stretch from x {x} is flat "
                    f"({value_string(round(v0, 4))} -> {value_string(v1)}) - it has no sign to take; name an ink "
                    f"({'|'.join(INK_FROM_INKS)})")
    return errs


def _validate_ink_from(series: dict, variant: str) -> list[str]:
    """P71 T28: `ink_from` on a dense line page's series, whole and truthful, or refused BY NAME (s106: before this slice
    it was accepted and ignored). [] when no series names it."""
    errs = [f"panels[{pi}].series[{si}]: ink_from is not built on a panel - a panel's lines draw with the page's build "
            "(P71 T28)" for pi, p in enumerate(series.get("panels") or []) if isinstance(p, dict)
            for si, s in enumerate(p.get("series") or []) if isinstance(s, dict) and INK_FROM_KEY in s]
    hits = [i for i, s in enumerate(series.get("series") or []) if isinstance(s, dict) and INK_FROM_KEY in s]
    if not hits:
        return errs
    builder = pick_builder(series, variant)
    if builder != "dense-line":
        return errs + [f"series[{i}]: ink_from changes the ink of a dense line page's stroke; this page draws as "
                       f"{builder!r} (P71 T28)" for i in hits]
    if series.get("highlight_from") is not None:
        return errs + [f"series[{i}]: ink_from beside highlight_from - the highlight already re-inks this line's story "
                       "window; one change of ink per line (P71 T28)" for i in hits]
    for i in hits:
        errs += _ink_from_errors(f"series[{i}]", series["series"][i])
    return errs


def ink_from_line(s: dict) -> dict:
    """The series as the page DRAWS it: its ink_from with the colour resolved (the stretch's sign when it names none).
    A copy; the file is never mutated."""
    out = copy.deepcopy(s)
    out[INK_FROM_KEY]["color"] = ink_from_color(s)
    return out


def projection_line(own: list, i: int) -> dict:
    """The series a projection is DRAWN as: its tag writes the projection's label (never a value, never the series'
    own name), in its line's ink when it names none. A copy; the file is never mutated."""
    s = copy.deepcopy(own[i])
    s["label"] = s[PROJECTION_KEY].get("label")
    s.pop("name", None)
    j = _projection_actual(own, i)
    if "color" not in s and j is not None and own[j].get("color") is not None:
        s["color"] = own[j]["color"]
    return s


def validate(series: dict, variant: str) -> list[str]:
    """Error strings; empty means the series is a page for this variant. Pure."""
    if SCHEMATIC_KEY in series:   # P70 T2: the shape's own rules first; a clean one is validated as the line it generates
        errs = _validate_schematic(series, variant)
        if errs:
            return errs
        series = with_schematic(series)
    errors: list[str] = []
    errors += _validate_projected_bars(series, variant)   # P71 T25 / E77: a projected bar is labelled, tiered, sourced, and has a field to pass
    errors += _validate_opens_on(series, variant)         # P71 T25: the bar the page opens on, and its rank's phrase (the ordinal is computed)
    series = with_projected_values(series)                # ... and then its height is its projection's (the same object when none)
    errors += _validate_readability(series, variant)
    errors += _validate_break(series, variant)   # P69 T66: [] unless the object names a `break`
    errors += _validate_members(series, variant)   # P69 T45: a membership is a bars page's, and a tile carries no value
    errors += _validate_bar_fields(series)          # P69 T64 / R26-307: a bar key the form does not know is refused by name
    errors += _validate_segments(series, variant)   # P69 T64: a stack of values is true to its total, one key per page
    errors += _validate_unit_suffix(series, variant)   # P72 T13 / R26-287: a prefix AND a suffix ($...B), refused by name when malformed
    errors += _validate_y2(series, variant)         # P71 T13 / R26-307: a second axis draws (a line page) or is refused by name
    errors += _validate_projection(series, variant)   # P71 T16 / E77: a projection is labelled, tiered, sourced and opens from the last actual
    errors += _validate_ink_from(series, variant)     # P71 T28 / E28: the line changes ink at a point - never a sign ink on the wrong sign
    errors += _validate_longform_chrome(series)       # P71 T30: the two-line source and the title capsule, the long form's alone
    if "left_gutter" in series:
        gutter = series["left_gutter"]
        if isinstance(gutter, bool) or not isinstance(gutter, int) or not 60 <= gutter <= 300:
            errors.append("left_gutter must be an integer from 60 to 300 SVG units")
        if not series.get("bars") or pick_builder(series, variant) != "story":
            errors.append("left_gutter requires a story/bar chart")
    if series.get("form") is not None:   # P58 T5: an OBJECT naming a form is held to the same one rule the row is
        err = form_error(str(series["form"]), pick_builder(series, variant), "form", variant)
        if not err and str(series["form"]).partition(":")[0] == "gauge":   # P70 T3: ... and a gauge's whole is named, as on the row
            err = gauge_error(series, "form")
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
    if pick_builder(series, variant) == PANELS:   # P69 T8b
        return errors + _validate_panels(series)
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


# ---- P69 T66 (E99 s111): THE BROKEN CROSS-ERA AXIS ----------------------------------------------------------------------
# The operator, on Bravos's "AI and Railway Spending As a % of GDP" (the 1860s and 1985-on joined by a `//`): "yes". A
# line may run across two eras on ONE x axis with a visible break when the claim is that the LEVELS are comparable era
# to era; the y is one unit for both, both eras are labelled, and the break is drawn so the gap is never read as
# continuous time (E53 s3's "never a continuous axis" is met by the break). When the claim is that the SHAPES match,
# the rebased overlay stays the form. `break: {after, before, eras}` on a dense-line object: the last x of the first
# era, the first x of the second, and the two eras' names; `claim: "level"` beside it. Not E60's retired zigzag - that
# broke a bar's SCALE, which is never abbreviated; an x axis across two eras IS abbreviated, and the mark says so.
BREAK_KEYS = ("after", "before", "eras")
BREAK_CLAIMS = ("level", "shape")
BREAK_RULING = "E99 s111"
BREAK_OVERLAY = ("the rebased overlay - each era counted from its own start on one x (row 15's \"years from each era's "
                 "start\", ev-tnx-two-eras-v4)")
BREAK_YEARS = (1000, 3000)   # an edge in this range is written as its year ("1849 // 1985"); the railway era is a date
ERA_VOID_SHARE = 0.4    # a stretch with no datum this share of the page's x span is a VOID between two eras ...
ERA_VOID_RATIO = 4.0    # ... when it is also this many times the next widest step (a sparse series is not two eras)


def _era_year(value: Any) -> str:
    n = to_number(value)
    return str(math.floor(n)) if n is not None and BREAK_YEARS[0] <= n < BREAK_YEARS[1] else value_string(value)


def break_gap_label(brk: dict) -> str:
    """The gap written at the break in the eras' own years - the engine's `lpBreakYear` writes the same string."""
    return f"{_era_year(brk.get('after'))} // {_era_year(brk.get('before'))}"


def _dense_xs(series: dict) -> list[float]:
    return sorted({x for s in dense_series(series) for x in (to_number(p[0]) for p in _points(s)) if x is not None})


def _break_shape_errors(series: dict, variant: str, where: str) -> list[str]:
    """The claim and the ONE unit: a level claim on one measure, or it is another form."""
    errors: list[str] = []
    claim = series.get("claim")
    if claim is None:
        errors.append(f"{where}: a broken axis states its claim - `claim: \"level\"`: the eras' LEVELS are comparable. "
                      f"A claim that their SHAPES match is {BREAK_OVERLAY}")
    elif claim == "shape":
        errors.append(f"{where}: claim 'shape' - when the SHAPES match, the form is {BREAK_OVERLAY}, not a broken axis; "
                      "a break is for a LEVEL claim")
    elif claim not in BREAK_CLAIMS:
        errors.append(f"{where}: claim {claim!r} is not one of {'|'.join(BREAK_CLAIMS)}")
    unit = series.get("yunit")
    if not _text(unit):
        errors.append(f"{where}: a broken axis writes its ONE unit (`yunit`) - both eras are read on that one y")
    for i, s in enumerate(dense_series(series)):
        own = s.get("unit", s.get("yunit"))
        if own is not None and str(own) != str(unit):
            errors.append(f"{where}: series[{i}] is in {own!r} and the page in {unit!r} - the eras share ONE unit on one y. "
                          "Two measures are E79's panels (each panel its own axes, `independent`), never one broken axis")
    if series.get("independent"):
        errors.append(f"{where}: `independent` declares unrelated measures on their own scales (E79's panels) - a broken "
                      "axis is ONE measure on one y")
    if series.get("line_unit") is not None:
        errors.append(f"{where}: `line_unit` gives the lines a right axis in a second unit - a broken axis has one y")
    if "xdomain" in series:
        errors.append(f"{where}: `xdomain` is a window on a continuous x - a broken axis is its two eras whole")
    return errors


def _break_data_errors(series: dict, a: float, b: float, eras: list, where: str) -> list[str]:
    """Tight to the data: the break is cut where no datum is, at the first era's last datum and the second's first,
    and both eras print their own dates at their ticks."""
    errors: list[str] = []
    xs = _dense_xs(series)
    inside = [x for x in xs if a < x < b]
    if inside:
        errors.append(f"{where}: a datum at {inside[0]:g} stands in the gap ({a:g} to {b:g}) - the break is cut where "
                      "there is no datum, and no point is ever drawn across it")
    first, second = [x for x in xs if x <= a], [x for x in xs if x >= b]
    if not first or max(first) != a:
        errors.append(f"{where}: break.after {a:g} is not the first era's last datum"
                      + (f" ({max(first):g})" if first else " (the first era has none)"))
    if not second or min(second) != b:
        errors.append(f"{where}: break.before {b:g} is not the second era's first datum"
                      + (f" ({min(second):g})" if second else " (the second era has none)"))
    if len(first) < 2 or len(second) < 2:
        errors.append(f"{where}: each era carries two data at least - a lone point is a mark, not an era")
    ticks = [(to_number(t[0]), t) for t in series.get("xticks") or [] if isinstance(t, (list, tuple)) and len(t) == 2]
    if not (first and second):
        return errors
    # a tick a hair outside its era's data still belongs to it (the panels' own rule: "2021" on data from 2021.0082)
    tol = (PANEL_TICK_EDGE * (a - xs[0]), PANEL_TICK_EDGE * (xs[-1] - b))
    for x, t in ticks:
        if x is not None and a + tol[0] < x < b - tol[1]:
            errors.append(f"{where}: the x tick {t[1]!r} ({x:g}) stands in the gap - the years between the eras are not drawn")
    names = eras if isinstance(eras, list) and len(eras) == 2 else ["the first era", "the second era"]
    for name, lo, hi in ((names[0], xs[0] - tol[0], a + tol[0]), (names[1], b - tol[1], xs[-1] + tol[1])):
        if not any(x is not None and lo <= x <= hi for x, _t in ticks):
            errors.append(f"{where}: {str(name).strip() or 'an era'} prints no tick of its own dates ({lo:g} to {hi:g}) - "
                          "both eras' dates are printed at their ticks")
    return errors


def _validate_break(series: dict, variant: str) -> list[str]:
    """E99 s111: a `break` is refused by name unless it is a sound broken axis. An object naming none is untouched."""
    if "break" not in series:
        return []
    brk, where = series["break"], f"break ({BREAK_RULING})"
    if not isinstance(brk, dict):
        return [f"{where}: must be {{after, before, eras}} - the first era's last x, the second era's first x, and the "
                "two eras' names"]
    errors = [f"{where}: {k!r} is not a break key ({'|'.join(BREAK_KEYS)})" for k in sorted(set(brk) - set(BREAK_KEYS))]
    a, b = to_number(brk.get("after")), to_number(brk.get("before"))
    if a is None or b is None:
        errors.append(f"{where}: break.after and break.before must be numbers - the first era's last x and the second "
                      "era's first x")
    elif a >= b:
        errors.append(f"{where}: break.before ({b:g}) must come after break.after ({a:g})")
    eras = brk.get("eras")
    if not (isinstance(eras, list) and len(eras) == 2 and all(_text(e) for e in eras)):
        errors.append(f"{where}: both eras are LABELLED on the page - break.eras is the two eras' names, [first, second]; "
                      "an unlabelled era is refused")
    builder = pick_builder(series, variant)
    if builder != "dense-line":
        return errors + [f"{where}: a broken x axis is a dense-line page's - this page draws as {builder!r}"]
    errors += _break_shape_errors(series, variant, where)
    if a is None or b is None or a >= b:
        return errors
    return errors + _break_data_errors(series, a, b, eras, where)


def era_void(series: dict) -> tuple[float, float] | None:
    """The widest stretch of a line page's x with no datum in it, when it reads as the void between two eras: at least
    ERA_VOID_SHARE of the span, ERA_VOID_RATIO times the next widest step, two data or more on each side."""
    xs = _dense_xs(series)
    if len(xs) < 4:
        return None
    steps = sorted(((xs[i + 1] - xs[i], i) for i in range(len(xs) - 1)), reverse=True)
    (wide, i), nxt = steps[0], steps[1][0]
    if wide < ERA_VOID_SHARE * (xs[-1] - xs[0]) or wide < ERA_VOID_RATIO * nxt or i < 1 or len(xs) - i - 1 < 2:
        return None
    return xs[i], xs[i + 1]


def era_void_warning(series: dict, name: str, variant: str = "line") -> str | None:
    """The compiler's WARN for two eras on one CONTINUOUS x (E53 s3): it names both honest forms - the broken axis for
    a LEVEL claim (s111), the rebased overlay for a SHAPE claim. A page that declares its break is answered, not warned;
    a page that is not ONE line plot (panels, tiers, bars) has no one x to warn about."""
    if "break" in series or pick_builder(series, variant) != "dense-line":
        return None
    void = era_void(series)
    if void is None:
        return None
    a, b = void
    return (f"{name}: E53 s3 - its x has no datum from {a:g} to {b:g}, and on one continuous axis those empty years read "
            f"as time. If the claim is that the eras' LEVELS are comparable, declare `break: {{\"after\": {a:g}, "
            f"\"before\": {b:g}, \"eras\": [..]}}` with `claim: \"level\"` (E99 s111: the `//` drawn); if the claim is "
            f"that their SHAPES match, {BREAK_OVERLAY} stays the form")


SIGNED_NOTE_RE = re.compile(r"^\s*[+\u2212-]\s*\d")
MONTH_LABEL_RE = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*'?(\d{2}|\d{4})$")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def share_solid(series: dict) -> bool:
    """P69 T48: does this share object name a donut, an extrusion or an explode? Pure."""
    return any(series.get(k) not in (None, False) for k in SHARE_SOLID_KEYS)


def pie_area_lie(tilt_deg: float, depth: float) -> float:
    """P69 T48: the worst factor a slice's APPARENT area (its top + the rim it shows) reads against its true share, on a
    pie tilted `tilt_deg` back from face-on and extruded `depth` of its radius. 1.0 is honest area. Pure."""
    q = 2.0 * float(depth) * math.tan(math.radians(float(tilt_deg)))
    return max((1.0 + q) / (1.0 + q / math.pi), 1.0 + q / math.pi)


def _decimals(v: Any) -> int:
    text = v if isinstance(v, str) else repr(v)
    return len(text.split(".", 1)[1]) if "." in text else 0


def _in_range(v: Any, lo: float, hi: float) -> bool:
    n = to_number(v)
    return n is not None and not isinstance(v, bool) and lo <= n <= hi


def _pie_options(series: dict) -> tuple[dict | None, dict | None, float | None]:
    """(extrude, explode, hole) as the spec carries them - every default written out - or None where not named."""
    ex, xp, hole = series.get("extrude"), series.get("explode"), series.get("hole")
    ext = None
    if ex not in (None, False):
        d = ex if isinstance(ex, dict) else {}
        ext = {"tilt": to_number(d["tilt"]) if "tilt" in d else PIE_TILT_DEG,
               "depth": to_number(d["depth"]) if "depth" in d else PIE_DEPTH,
               "hatch": bool(d.get("hatch", False))}
    exp = None
    if xp not in (None, False):
        d = xp if isinstance(xp, dict) else {}
        exp = {"index": d["index"] if "index" in d else series.get("emphasize"),
               "out": to_number(d["out"]) if "out" in d else PIE_EXPLODE_OUT}
    return ext, exp, (to_number(hole) if hole not in (None, False) else None)


def _validate_option(name: str, value: Any, fields: dict) -> list[str]:
    """`true` or an object of the named fields, each checked by its own (predicate, message)."""
    if value is True:
        return []
    if not isinstance(value, dict):
        return [f"{name} must be true or {{{', '.join(fields)}}} (P69 T48), not {value!r}"]
    unknown = sorted(set(value) - set(fields))
    errs = [f"{name}: unknown key(s) {unknown} - it takes {', '.join(fields)}"] if unknown else []
    return errs + [f"{name}.{k} {value[k]!r} {msg}" for k, (ok, msg) in fields.items() if k in value and not ok(value[k])]


def _validate_share_solid(series: dict, shares: list) -> list[str]:
    """P69 T48 / E99 s109 (4): the solid share page's contract. The truth rules are hard (the shares sum to their whole,
    the options name real slices); how steep a tilt reads is advice, reported by `_share_block` with its number."""
    errors: list[str] = []
    n = len(shares)
    if series.get("peel") is not None:
        errors.append("peel is the flat pie's piece that leaves (P48 T4); a donut or a 3D page EXPLODES its slice instead "
                      "(`explode` + the `explode` species on its word) - drop `peel`")
    hole = series.get("hole")
    if hole not in (None, False) and not (_in_range(hole, 0.0, PIE_HOLE_MAX) and to_number(hole) > 0):
        errors.append(f"hole {hole!r} must be the donut's hole as a share of the radius, in (0, {PIE_HOLE_MAX}]")
    tlo, thi = PIE_TILT_RANGE
    dlo, dhi = PIE_DEPTH_RANGE
    olo, ohi = PIE_EXPLODE_RANGE
    if series.get("extrude") not in (None, False):
        errors += _validate_option("extrude", series["extrude"], {
            "tilt": (lambda v: _in_range(v, tlo, thi), f"is outside {tlo}..{thi} degrees back from face-on"),
            "depth": (lambda v: _in_range(v, dlo, dhi), f"is outside {dlo}..{dhi} of the radius"),
            "hatch": (lambda v: isinstance(v, bool), "must be true or false (T6b's engraving on the side away from the light)")})
    if series.get("explode") not in (None, False):
        errors += _validate_option("explode", series["explode"], {
            "index": (lambda v: isinstance(v, int) and not isinstance(v, bool) and 0 <= v < n,
                      f"does not name a slice (0..{n - 1})"),
            "out": (lambda v: _in_range(v, olo, ohi), f"is outside {olo}..{ohi} of the radius")})
    total = to_number(series.get("total"))
    if total is None or total <= 0:
        errors.append(f"a solid share page must declare 'total': the whole its slices are shares of (100 for percent), "
                      f"not {series.get('total')!r} - the angles are shares of the WHOLE (E99 s109 (4))")
        return errors
    vals = [to_number(s.get("value")) for s in shares if isinstance(s, dict)]
    if any(v is None for v in vals):
        return errors
    summed = sum(vals)
    tol = sum(0.5 * 10 ** -_decimals(s.get("value")) for s in shares) + 1e-9
    if summed - total > tol:
        errors.append(f"the shares sum to {summed:g}, more than the whole {total:g}: a part cannot exceed its whole")
    elif total - summed > tol:
        rest = total - summed
        errors.append(f"the shares sum to {summed:g} of the whole {total:g}: {rest:g} is unaccounted for - name it as its "
                      f"own slice ({{\"label\": \"Other\", \"value\": {rest:g}}}) or correct the figures. A pie of the "
                      "named slices alone would draw each of them larger than its share (E99 s109 (4))")
    return errors


def _validate_share(series: dict) -> list[str]:
    """A share page's contract - E53 s1's amendment, checked rather than trusted. Every failure names the bound it
    broke, because the whole point of writing the exception down was that it not widen by use."""
    errors: list[str] = []
    shares = series.get("shares")
    if not isinstance(shares, list) or len(shares) < 2:
        return ["a share page needs 'shares': at least two slices, the whole they add up to being the page's subject"]
    # P69 T50 / E99 s100: the slice count is no longer refused - past SHARE_MAX_SLICES the page is REPORTED with its
    # numbers (`share_honesty_warnings`); what stays hard here is untruth (a slice that is not a positive part)
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
    if share_solid(series):   # P69 T48: every figure is written on its slice, so no `peel` carries the claim's
        return errors + _validate_share_solid(series, shares)
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


def share_honesty_warnings(series: dict) -> list[str]:
    """P69 T50 / E99 s100 + s106: a share page past SHARE_MAX_SLICES is a page, REPORTED with its numbers - how many
    slices, how many of their figures the page writes (a solid page writes every one; the flat pie the peel's alone),
    and the thinnest slice's share and angle, so the frame read knows what to look at. Every angle is its value's
    share of the whole by construction (the solid page's sum is refused when it is untrue). Pure; [] inside the
    guidance, so such a page's spec is byte-identical."""
    shares = [s for s in series.get("shares") or [] if isinstance(s, dict)]
    vals = [to_number(s.get("value")) for s in shares]
    n = len(shares)
    if n <= SHARE_MAX_SLICES or any(v is None or v <= 0 for v in vals):
        return []
    whole = to_number(series.get("total")) if share_solid(series) else None
    whole = whole if whole and whole > 0 else sum(vals)
    k = min(range(n), key=lambda i: (vals[i], i))
    share = vals[k] / whole
    solid = share_solid(series)
    written = n if solid else (1 if _text((series.get("peel") or {}).get("value_string")) else 0)
    how = ("every slice writes its figure" if solid else
           "a flat pie writes the peel's figure alone - a donut or a solid page (hole / extrude) writes every one, "
           "E99 s100 (b)")
    return [f"{FORM_WARN} share: {n} slices, past the {SHARE_MAX_SLICES} a reader names at a glance (E53 s1, guidance "
            f"since E99 s100). Every angle is true to its share; {written} of {n} figures are written on the page "
            f"({how}); the thinnest, {str(shares[k].get('label'))!r}, is {share * 100:.1f}% of the whole "
            f"({share * 360:.1f} deg) - read its name and figure in the frame. REPORTED, the frame read decides "
            "(E99 s106)"]


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


def _tier_band_px(series: dict) -> str:
    """P72 T13 (R26-217): the band heights THIS page would get, per stage, as page_boxes lays them out - the ceiling's
    reason measured on the stage the page renders on, not a portrait figure baked into the message."""
    try:
        spec = build_spec(series, "tiers")
        per = {a: page_boxes(spec, a).get("bands") or [] for a in STAGE_PX}
        return ("Its bands would stand " + " and ".join(f"{int(round(b[0]['h']))} px tall at {a}" for a, b in per.items() if b)
                + f" (page_boxes; at the ceiling each of {TIERS_MAX} bands takes a quarter of the plot, " + " and ".join(
                    f"{int(round(v))} px at {a}" for a, v in _tier_band_ceiling_px().items()) + ") ")
    except Exception:   # the page is refused either way; a band it cannot lay out has no height to report
        return ""


def _tier_band_ceiling_px() -> dict[str, float]:
    """The band height at the ceiling (TIERS_MAX bands), per stage, from page_boxes' own tiers layout."""
    probe = {"title": "t", "src": "s", "tiers": [{"name": f"t{i}", "unit": "u", "pts": [[0, 0], [1, 1]]}
                                                 for i in range(TIERS_MAX)]}
    spec = build_spec(probe, "tiers")
    return {a: page_boxes(spec, a)["bands"][0]["h"] for a in STAGE_PX}


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
        errors.append(f"{len(tiers)} tiers: the ceiling is {TIERS_MAX}. {_tier_band_px(series)}- a band under the "
                      f"ceiling's cannot carry its own scale, its name and a readable line at once. Split the page.")
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
        dom_err = _tier_domain_error(tier, where)   # P72 T46d (R26-370): a band's own `domain` is drawn now - refused when malformed
        if dom_err:
            errors.append(dom_err)
        sig = _tier_x(tier)
        sigs.append(sig)
        if sig and sigs[0] and not _x_same(sigs[0], sig):
            errors.append(f"{where} spans x {_x_text(sig)} while tiers[0] spans {_x_text(sigs[0])} - N tiers share ONE x "
                          "(that is what makes them small multiples, and the only thing the page claims across bands); "
                          "window the file to one x, or draw two pages")
    return errors + shared_domains_errors(series)


def _tier_domain_error(tier: dict, where: str) -> str | None:
    """P72 T46d (R26-370): a band's declared `domain` (species/tiers.mjs `tierDeclared` draws it verbatim) must be two
    numbers low to high - anything else is refused BY NAME rather than dropped (s106: a silent drop is neither advice
    nor refusal)."""
    if "domain" not in tier:
        return None
    dom = tier.get("domain")
    ok = (isinstance(dom, (list, tuple)) and len(dom) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                                                   for v in dom) and float(dom[1]) > float(dom[0]))
    return None if ok else (f"{where} domain {dom!r} must be [low, high] - two numbers, low first: the band is drawn on "
                            "exactly that scale")


SHARED_TIER_KEY = "shared_tier_domains"   # P72 T46d (R26-370): E79's one scale per unit, the page key the engine reads


def shared_domains_errors(series: dict) -> list[str]:
    """P72 T46d (R26-370): an AUTHORED `shared_tier_domains` - {unit: [low, high]} for units the page's bands carry -
    refused by name when malformed (the compiler writes the key itself otherwise, `shared_domains_key`)."""
    if SHARED_TIER_KEY not in series:
        return []
    val, units = series.get(SHARED_TIER_KEY), {str(t.get("unit")) for t in _tier_entries(series) if isinstance(t, dict)}
    if not isinstance(val, dict) or not val:
        return [f"{SHARED_TIER_KEY} {val!r} must be an object {{unit: [low, high]}} naming the bands' units (E79)"]
    errs = []
    for unit, dom in val.items():
        if unit not in units:
            errs.append(f"{SHARED_TIER_KEY}: unit {unit!r} is not a unit of this page's bands ({sorted(units)})")
        elif not (isinstance(dom, (list, tuple)) and len(dom) == 2
                  and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in dom) and float(dom[1]) > float(dom[0])):
            errs.append(f"{SHARED_TIER_KEY}[{unit!r}] {dom!r} must be [low, high] - two numbers, low first")
    return errs


def shared_domains_key(series: dict) -> dict:
    """P72 T46d (R26-370): E79's shared scale as the COMPILER'S DEFAULT - the page key `shared_tier_domains`
    ({unit: [low, high]}, before the engine's pad) for every same-unit group of two or more bands, written unless the
    page declares `independent` (a band that does leaves its group: `_same_unit_groups`). An authored key (validated
    above) is taken as written. {} when nothing is shared - the page is then drawn exactly as before."""
    if isinstance(series.get(SHARED_TIER_KEY), dict):
        return {SHARED_TIER_KEY: {str(u): [float(d[0]), float(d[1])] for u, d in series[SHARED_TIER_KEY].items()}}
    shared = shared_tier_domains(series)
    return {SHARED_TIER_KEY: {u: [float(lo), float(hi)] for u, (lo, hi) in shared.items()}} if shared else {}


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
    return {"tiers": out, "labels": [b["name"] for b in out], **shared_domains_key(series),
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


# ---- PANELS (P69 T8b; E99 s104, amended twice) ---------------------------------------------------
# The operator: "no reason it shouldn't be able to, we already handle 2 evidence docks on world plates, it rhymes to
# have 2 data panels/charts on ledger plates when needed" - and, for row 21's four charts, "whatever is less important
# to be held on background/off-focus and brought back up at relevant times". The page is 2-4 LINE plots, each its own
# chart; the SCALE is E79's: panels of one measure share ONE y domain (the card's own rule - min and max over every
# panel, the reference rules and a declared ymin / ymax, the air on top and on the bottom unless ymin names the floor -
# `shared_panel_domain`), written onto each panel's axes so the engine's line builder draws it verbatim; `independent:
# true` on the page gives every panel its own, on a panel takes that one out of the group. A panel that DECLARES its
# own `domain` keeps it (the author places, the engine advises - E99 s106) and, if it shares a unit with the group, the
# build says so as E79's WARN (`panel_scale_warnings`), never a refusal.
PANEL_Y_PAD = 0.06   # the card's own air on the shared scale (scene-evidence-engine's chart_dock: `pad = (gy1 - gy0) * 0.06`)
PANEL_TICK_EDGE = 0.02   # a page x tick this share of a panel's span outside its data still belongs to it (1998 on a series from 1998.0027)


def _panel_entries(series: dict) -> list:
    """The declared panels, verbatim (a non-object entry is kept so the error can name it)."""
    return list(series["panels"]) if isinstance(series.get("panels"), list) else []


def _panel_lines(panel: dict) -> list[dict]:
    """A panel's line series (its `series` list; a `later` series waits off the page, as on a line page)."""
    return [s for s in (panel.get("series") or []) if isinstance(s, dict) and "pts" in s and not s.get("later")]


def _validate_panels(series: dict) -> list[str]:
    """A panels page's contract: 2-4 panels, each a named plot fed by line series. Every failure names its panel."""
    panels = _panel_entries(series)
    if len(panels) < PANELS_MIN:
        return [f"a panels page needs 'panels': a list of at least {PANELS_MIN} plots, each {{sub, series}} - one plot "
                "is a line page"]
    errors: list[str] = []
    if len(panels) > PANELS_MAX:
        errors.append(f"{len(panels)} panels: the ceiling is {PANELS_MAX} (E99 s104 amended: up to FOUR on a page, the "
                      "rest held in focus states - a fifth chart is a new page)")
    for i, panel in enumerate(panels):
        where = f"panels[{i}]"
        if not isinstance(panel, dict):
            errors.append(f"{where} is not an object")
            continue
        if not _text(panel.get("sub")):
            errors.append(f"{where} has no 'sub': a panel's sub IS its title line - two plots side by side must say "
                          "which is which")
        if panel.get("builder", PANEL_LINE) not in PANEL_BUILDERS:   # P69 T8d
            errors.append(f"{where}: builder {panel.get('builder')!r} is not one of {'|'.join(PANEL_BUILDERS)} (a panel "
                          "draws a line chart - the default - or a bars chart)")
        elif panel_is_bars(panel):
            errors += _validate_bars_panel(series, panel, where)
        elif panel.get("bars"):
            errors.append(f"{where} {panel.get('sub')!r} carries 'bars' and is a line panel: a panel of bars says "
                          "`builder: bars` (P69 T8d) - one panel, one chart")
        elif not _panel_lines(panel):
            errors.append(f"{where} {panel.get('sub')!r} has no line series ('series': [{{name, pts}}])")
        if "independent" in panel and not isinstance(panel["independent"], bool):
            errors.append(f"{where}: independent must be true or false (E79)")
    return errors + _validate_values(series, "line") + badge_key_conflicts(series)


def panel_is_bars(panel: Any) -> bool:
    """P69 T8d: is this panel drawn by the BARS builder?"""
    return isinstance(panel, dict) and panel.get("builder") == PANEL_BARS


def _panel_bars(panel: dict) -> list[dict]:
    return [b for b in panel.get("bars") or [] if isinstance(b, dict)] if panel_is_bars(panel) else []


PANEL_BARS_REFUSED = ("overflow", "overflow_placeholder", "overflow_capsule", "break_cadence", "series")


def _validate_bars_panel(series: dict, panel: dict, where: str) -> list[str]:
    """P69 T8d: a bars panel is a bars page in a box - 1..STORY_MAX_VALUES bars, each named, each a number or an honest
    range in the panel's unit. The breakthrough (overflow) rewrites its OWN scale, and a panel's scale is its unit
    group's (E79), so it is refused here by name; a line series on a bars panel is a second chart."""
    bars, errors = _panel_bars(panel), []
    if not bars:
        return [f"{where} {panel.get('sub')!r} is a bars panel and has no bars ('bars': [{{label, value}}])"]
    if len(bars) > STORY_MAX_VALUES:
        errors.append(f"{where}: {len(bars)} bars; a bars chart's ceiling is {STORY_MAX_VALUES}")
    for key in (k for k in PANEL_BARS_REFUSED if panel.get(k) is not None):
        errors.append(f"{where}: {key!r} on a bars panel - " + ("a bars panel draws bars, not lines (one panel, one chart)"
                      if key == "series" else "the breakthrough rewrites its own scale; a panel's scale is its unit "
                      "group's (E79) - break it on a bars page of its own"))
    unit = panel_unit(series, panel)
    for j, bar in enumerate(bars):
        errors += bar_value_errors(f"{where} bars[{j}]", bar, unit)
        if not _text(bar.get("label")):
            errors.append(f"{where} bars[{j}] has no label (one label per datum)")
    return errors


def panel_unit(series: dict, panel: dict) -> str:
    """The unit a panel's y axis measures: its own `yunit` / `unit`, else the page's."""
    for src in (panel, series):
        for key in ("yunit", "unit"):
            if _text(src.get(key)):
                return str(src[key])
    return ""


def _panel_raw_extent(series: dict, panel: dict) -> tuple[float, float] | None:
    """A panel's data extent, the page's reference rules and any declared ymin / ymax - the card's own inputs.
    P69 T8d: a BARS panel's extent is its bars (both ends of a range), its OWN rules and ymin / ymax, and ZERO - a bar
    stands on the zero line (E28); the page's rules are its line panels' (a rule in one measure is not drawn across
    another's bars)."""
    if panel_is_bars(panel):
        vals = [0.0]
        for b in _panel_bars(panel):
            rng = bar_range(b)
            vals += list(rng) if rng else [to_number(b.get("value"))]
        vals += [to_number(h.get("y")) for h in panel.get("hlines") or [] if isinstance(h, dict)]
        vals += [to_number(panel.get(k)) for k in ("ymin", "ymax") if panel.get(k) is not None]
    else:
        vals = [to_number(p[1]) for s in _panel_lines(panel) for p in _points(s)]
        rules = series.get("hlines") or ([series["hline"]] if isinstance(series.get("hline"), dict) else [])
        vals += [to_number(h.get("y")) for h in rules if isinstance(h, dict)]
        vals += [to_number(src.get(k)) for src in (series, panel) for k in ("ymin", "ymax") if src.get(k) is not None]
    nums = [v for v in vals if v is not None]
    return (min(nums), max(nums)) if nums else None


def _padded(lo: float, hi: float, floor_named: bool) -> list[float]:
    pad = (hi - lo) * PANEL_Y_PAD or 1.0
    return [lo if floor_named else lo - pad, hi + pad]


def _bars_padded(lo: float, hi: float) -> list[float]:
    """P69 T8d: a scale that holds a BAR - the bars builder's own law (buildLedgerBars): zero inside it, BARS_PAD of air
    on each side that carries data away from zero, none past the zero line itself."""
    lo, hi = min(0.0, lo), max(0.0, hi)
    pad = (hi - lo) * BARS_PAD or 1.0
    return [lo - (pad if lo < 0 else 0.0), hi + (pad if hi > 0 else 0.0)]


def _panel_groups(series: dict) -> dict[str, list[dict]]:
    """E79's groups: the panels that share a scale, by the unit they measure (P69 T8d: panels in different units never
    share one - a bars panel in `x` beside a line in `%` stands on its own). The declared-own-scale panels are out."""
    groups: dict[str, list[dict]] = {}
    for p in _panel_entries(series):
        if isinstance(p, dict) and not _panel_own_scale(series, p):
            groups.setdefault(panel_unit(series, p), []).append(p)
    return groups


def _group_domain(series: dict, group: list[dict]) -> list[float] | None:
    ext = [e for e in (_panel_raw_extent(series, p) for p in group) if e]
    if not ext:
        return None
    lo, hi = min(e[0] for e in ext), max(e[1] for e in ext)
    if any(panel_is_bars(p) for p in group):   # P69 T8d: a group that holds a bar keeps the zero (E28)
        return _bars_padded(lo, hi)
    return _padded(lo, hi, series.get("ymin") is not None)


def shared_panel_domains(series: dict) -> dict[str, list[float]]:
    """E79: the ONE y domain each unit's non-independent panels draw on - the card's own rule, verbatim (min and max
    over the group's data, the reference rules and a declared ymin / ymax, padded 6 % unless ymin names the floor), or
    the bars law when the group holds a bars panel. Empty when every panel is independent. Pure."""
    out = {}
    for unit, group in _panel_groups(series).items():
        dom = _group_domain(series, group)
        if dom is not None:
            out[unit] = dom
    return out


def shared_panel_domain(series: dict) -> list[float] | None:
    """The shared domain of a page whose grouped panels measure ONE unit (T8b's page); None otherwise. Pure."""
    doms = shared_panel_domains(series)
    return next(iter(doms.values())) if len(doms) == 1 else None


def _panel_own_scale(series: dict, panel: dict) -> bool:
    return series.get("independent") is True or panel.get("independent") is True or _declared_domain(panel) is not None


def _panel_domain(series: dict, panel: dict, shared: dict[str, list[float]]) -> list[float] | None:
    """The domain one panel is drawn on: its declared one, else (independent) its own padded extent, else its unit's."""
    own = _declared_domain(panel)
    if own:
        return [own[0], own[1]]
    if not _panel_own_scale(series, panel):
        return shared.get(panel_unit(series, panel))
    ext = _panel_raw_extent(series, panel)
    if ext and panel_is_bars(panel):
        return _bars_padded(ext[0], ext[1])
    return _padded(ext[0], ext[1], panel.get("ymin", series.get("ymin")) is not None) if ext else None


def panel_scale_warnings(series: dict) -> list[str]:
    """E79 on a panels page: a panel that DECLARES a domain of its own while it shares a unit with the grouped panels
    (no `independent`) - the author's domain stands (E99 s106), and the build says so. P70 T4: and one `measure` drawn
    in two units (`measure_unit_warnings`). Pure."""
    shared = shared_panel_domains(series)
    measures = measure_unit_warnings(series)   # P70 T4: [] on every page whose panels name no measure
    if series.get("independent") is True or not shared:
        return measures
    page = series.get("id") or series.get("title") or "page"
    out = []
    for i, p in enumerate(_panel_entries(series)):
        own = _declared_domain(p) if isinstance(p, dict) else None
        unit = panel_unit(series, p) if isinstance(p, dict) else ""
        if own is None or p.get("independent") is True or unit not in shared:
            continue
        dom = shared[unit]
        if (round(own[0], 9), round(own[1], 9)) != (round(dom[0], 9), round(dom[1], 9)):
            out.append(f"E79 {page!s}: panels[{i}] {str(p.get('sub') or '')!r} declares y-domain {_dom_text(own)} while the "
                       f"other panels in {unit!r} share {_dom_text(tuple(dom))} - panels of the same "
                       "measure share one scale; if this is an unrelated measure, declare `independent: true` on it")
    return out + measures


# ---- P70 T4 (E79 apply 1; E53 s4 "the honest zero, and one unit before two"): ONE MEASURE, ONE UNIT -----------------
# E79 groups panels by the unit STRING they measure (`_panel_groups`), so one measure written in two units - a share of
# every dollar invested as "%" on the line and as "¢" on the bars beside it - falls into two groups and silently draws
# two scales. A panel may NAME the quantity it draws (`measure`, text); panels naming one measure in different units
# are a WARN with the units and the panels - one measure, one unit, one scale; re-express one panel. Advice, never a
# refusal (E99 s106); there is no unit-equivalence table (the author names the measure). The key never reaches the
# spec: a page whose panels name no measure builds the bytes it always did.
PANEL_MEASURE = "measure"


def _measure_key(value: str) -> str:
    return " ".join(value.split()).casefold()   # one measure however it is cased or spaced


def measure_unit_warnings(series: dict) -> list[str]:
    """E79 / E53 s4 WARN rows: two or more panels naming one `measure` in different units; a `measure` that is not
    text is named too (it groups nothing). Pure."""
    page = series.get("id") or series.get("title") or "page"
    names: dict[str, str] = {}
    units: dict[str, dict[str, list[int]]] = {}
    out: list[str] = []
    for i, panel in enumerate(_panel_entries(series)):
        if not isinstance(panel, dict) or PANEL_MEASURE not in panel:
            continue
        measure = panel[PANEL_MEASURE]
        if not _text(measure):
            out.append(f"E79 {page!s}: panels[{i}] measure {measure!r} is not a name - a panel's `measure` is the "
                       "quantity it draws, written as text (or left out)")
            continue
        key = _measure_key(str(measure))
        names.setdefault(key, " ".join(str(measure).split()))
        units.setdefault(key, {}).setdefault(panel_unit(series, panel), []).append(i)
    for key, by_unit in units.items():
        if len(by_unit) < 2:
            continue
        drawn = " and ".join(repr(u) for u in by_unit)
        where = "; ".join(f"{u!r}: panels {', '.join(str(i) for i in idx)}" for u, idx in by_unit.items())
        out.append(f"E79 / E53 s4 {page!s}: {names[key]} is drawn in {drawn} ({where}) - one measure, one unit, one "
                   "scale; re-express one panel")
    return out


def _panel_xticks(series: dict, panel: dict) -> list:
    """The page's x ticks that fall inside THIS panel's own x span (the card's rule: a tick outside it is not drawn),
    or the panel's own when it declares them."""
    if isinstance(panel.get("xticks"), list):
        return copy.deepcopy(panel["xticks"])
    xs = [to_number(p[0]) for s in _panel_lines(panel) for p in _points(s)]
    xs = [x for x in xs if x is not None]
    if not xs:
        return []
    lo, hi = min(xs), max(xs)
    edge = (hi - lo) * PANEL_TICK_EDGE   # a tick a hair outside the data's first or last x still states the span (E28)
    return [copy.deepcopy(t) for t in (series.get("xticks") or [])
            if isinstance(t, (list, tuple)) and len(t) == 2 and to_number(t[0]) is not None
            and lo - edge <= to_number(t[0]) <= hi + edge]


PANEL_PAGE_AXES = ("log", "from_zero", "name_clear", "yfmt")   # the page's axes every panel draws with
PANEL_RULE_TAIL = 0.4   # the share of a panel's own x span, at its right end, a rule's name is written over


def _panel_rule_home(series: dict) -> int:
    """Which panel NAMES the page's reference rules (a rule is named once - the card's rule): the one whose data stand
    LOWEST over the right end of its span, where the line builder writes a rule's name (right-aligned over the rule) -
    so the name reads on the panel's own ground, not across a line. The first panel on a tie."""
    best, where = None, 0
    for i, panel in enumerate(_panel_entries(series)):
        pts = [(to_number(p[0]), to_number(p[1])) for s in _panel_lines(panel) if isinstance(panel, dict) for p in _points(s)]
        pts = [(x, y) for x, y in pts if x is not None and y is not None]
        if not pts:
            continue
        lo, hi = min(x for x, _ in pts), max(x for x, _ in pts)
        tail = [y for x, y in pts if x >= hi - (hi - lo) * PANEL_RULE_TAIL]
        top = max(tail) if tail else max(y for _, y in pts)
        if best is None or top < best:
            best, where = top, i
    return where


def plain_panel_tag_form(series: dict, panel: dict) -> str:
    """A PLAIN (not long-form) panel's end-tag form: the fullest whose widest tag stands inside the panel's own right
    margin (the line builder's 220 units, less its tag gap) - a tag past it runs into the next panel or off the stage.
    `badge` keeps the value and the badge's chip, `value` the value alone."""
    room = LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
    lines = _panel_lines(panel)
    for form in ("full", "badge", "value"):
        view = [dict(s, name="") if form != "full" and str(s.get("label") or "").strip() else s for s in lines]
        badges = [b for b in series.get("badges") or [] if isinstance(b, dict)] if form != "value" else []
        if tag_units({"builder": "dense-line", "series": view, "badges": badges}) <= room:
            return form
    return "value"


def _panels_block(series: dict) -> dict:
    """The panels, normalised - each a dense-line chart of its own: its `sub` (its title line), its live series, and
    its `axes` (the page's shared ones, its x ticks cut to its own span, the reference rules with their NAMES on the
    first panel only - the card's rule, a rule is named once - its unit on the tick labels, and the domain E79 gives
    it). The page's `labels` are the panels' subs: a panel is this page's datum, as a band is a tiers page's."""
    shared = shared_panel_domains(series)
    rules = series.get("hlines") or ([series["hline"]] if isinstance(series.get("hline"), dict) else [])
    named = _panel_rule_home(series)
    out = []
    for i, panel in enumerate(_panel_entries(series)):
        if not isinstance(panel, dict):
            continue
        if panel_is_bars(panel):   # P69 T8d: a bars chart in the panel's box
            out.append(_bars_panel_entry(series, panel, shared))
            continue
        axes = {k: copy.deepcopy(series[k]) for k in PANEL_PAGE_AXES if k in series}
        axes.update({k: copy.deepcopy(panel[k]) for k in AXES_KEYS if k in panel and k not in ("xticks", "domain")})
        axes["xticks"] = _panel_xticks(series, panel)
        if rules and "hlines" not in panel:
            axes["hlines"] = [dict(h) for h in copy.deepcopy(rules) if isinstance(h, dict)]   # every panel can name them; the
            # engine shows the names on ONE visible panel per focus state - `panel_rule_home` when it is in focus
        unit = panel_unit(series, panel)
        if unit:
            axes["unit"] = unit
        dom = _panel_domain(series, panel, shared)
        if dom is not None:
            axes["domain"] = [round(dom[0], 6), round(dom[1], 6)]
        axes["tag_form"] = plain_panel_tag_form(series, panel)   # the long form re-fits it at its preset (apply_longform)
        entry = {"sub": str(panel.get("sub") or ""), "series": copy.deepcopy(_panel_lines(panel)), "axes": axes}
        if panel.get("independent") is True:
            entry["independent"] = True
        out.append(entry)
    axes = {k: copy.deepcopy(series[k]) for k in AXES_KEYS if k in series and k != "panels"}   # the panels are the spec's own key
    return {"panels": out, "labels": [p["sub"] for p in out],
            **({"panel_rule_home": named} if rules else {}),
            **({"axes": axes} if axes else {}),
            "values": [], "value_strings": [], "colors": []}


def _bars_panel_entry(series: dict, panel: dict, shared: dict[str, list[float]]) -> dict:
    """P69 T8d: one BARS panel, normalised as a bars page's own block (`_story_block`'s labels, values, the tokens
    verbatim, colours, and `ranges` when a bar carries one), its unit (on the entry, which the bars builder reads, and
    on its axes), its own axes (its comparator rules; never the page's line rules) and the domain E79 gives its unit
    group. No x ticks and no end tags: a bar's name is under it and its value on it."""
    bars = _panel_bars(panel)
    axes = {k: copy.deepcopy(panel[k]) for k in AXES_KEYS if k in panel and k not in ("xticks", "domain")}
    unit = panel_unit(series, panel)
    if unit:
        axes["unit"] = unit
    dom = _panel_domain(series, panel, shared)
    if dom is not None:
        axes["domain"] = [round(dom[0], 6), round(dom[1], 6)]
    raw = [b.get("value") for b in bars]
    entry = _with_ranges({"sub": str(panel.get("sub") or ""), "builder": PANEL_BARS, "labels": [b.get("label") for b in bars],
                          "values": [to_number(v) for v in raw], "value_strings": [value_string(v) for v in raw],
                          "colors": [b.get("color") for b in bars], "unit": unit, "axes": axes}, bars)
    if isinstance(panel.get("emphasize"), int) and not isinstance(panel["emphasize"], bool):
        entry["emphasize"] = max(0, min(panel["emphasize"], len(bars) - 1))
    if panel.get("independent") is True:
        entry["independent"] = True
    return entry


# ---- TREEMAP (P50 T6; E53 s1's second amendment, the CENSUS exception, ruled 2026-09-10) ---------
# A whole broken into its parts by AREA. P69 T50 / E99 s100: the census exception's four bounds are SUPERSEDED by the
# two honesty tests - every area true to its value (the squarify is exact: a cell's area is its value's share of the
# plot, `treemap_area_error` measures it) and the figures the claim turns on WRITTEN. A treemap may carry a SIZE claim
# ("bigger than"): the story chooses the form, and the page REPORTS, with its numbers, every cell whose figure it cannot
# write - the frame read decides (s106). The perception hierarchy is guidance: bars read a size fastest.
TREEMAP_ASPECT = 1.5        # the aspect the squarify tunes toward: 3:2, never 1:1 (Heer & Bostock 2010's square penalty - a square cell reads as a block, a 3:2 cell as a labelled thing)
TREEMAP_MIN_CELL = (80, 36)     # research s1 (ISO 9241-303 at a 30-40 cm handheld distance): under this, NO text - illegible ink blobs overlap and the mosaic reads as noise
TREEMAP_TWO_LINE = (110, 64)    # ... and the floor for two lines (label + value)
TREEMAP_VALUE_FONT = 18         # the absolute legible floor on a 1080x1920 stage; a value that would be written smaller is not written
TREEMAP_LABEL_FONT = (18, 32)   # the label's clamp
TREEMAP_PAD = 6                 # the cell's inner padding at 1080x1920 (research s2: glyph stems never touch a cell edge)
TREEMAP_CHAR_W = 0.72           # the advance the font clamp assumes. The research's own figure is 0.65 em; our cell labels are BOLD, and at 0.65 "Japan" touched its cell's right edge in the rendered frame (2026-09-11)
TREEMAP_LINE_H = {1: 1.5, 2: 2.2}   # the cell height one line of type needs, and two. The research's clamp divides by 2.2 whatever the line count, which contradicts the same document's 36 px single-line floor: at 2.2 a 44 px cell could never carry 18 px type. 2.2 is the TWO-line allowance; one line takes a line and a half
# P72 T13 (R26-217, audit G-13): THE FLOORS ARE THE STAGE'S. The five px constants above were read off a 1080x1920 stage;
# `treemap_floors(aspect)` resolves them for the stage a cell renders on, scaled by the stage's SHORT side. The 16:9
# value is the same number, and that is a finding, not a default [DERIVED: a short plays upright and a long form plays
# sideways, full screen, on the same phone - both stages put their 1080-px side across the phone's short side, so one
# stage px is one physical size on both, and the research's handheld floor (ISO 9241-303, s1) is the same count of px].
TREEMAP_STAGE_SHORT = 1080


def treemap_floors(aspect: str = "9:16") -> dict:
    """The treemap's legibility floors, in stage px, for this stage (unknown aspect -> the portrait reference). Pure."""
    w, h = STAGE_PX.get(aspect, STAGE_PX["9:16"])
    k = min(w, h) / TREEMAP_STAGE_SHORT
    return {"min_cell": (TREEMAP_MIN_CELL[0] * k, TREEMAP_MIN_CELL[1] * k),
            "two_line": (TREEMAP_TWO_LINE[0] * k, TREEMAP_TWO_LINE[1] * k),
            "value_font": TREEMAP_VALUE_FONT * k, "label_font": (TREEMAP_LABEL_FONT[0] * k, TREEMAP_LABEL_FONT[1] * k),
            "pad": TREEMAP_PAD * k}
TREEMAP_MIN_SHARES = 2          # P69 T50: a whole broken into parts - one part is the whole, not a division (three was the census exception's TYPE bound; E99 s100)
# E53 s1 -> E99 s100: a SIZE CLAIM is found in the page's own words, and REPORTED (`treemap_honesty_warnings`) unless
# every figure it could compare is written on its cell.
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
                "({label, value}) - one part is the whole itself, not a division of it"]
    errors: list[str] = []   # P69 T50: a size claim is no longer refused here - build_spec REPORTS it (E99 s100, s106)
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


def _clamp_font(w: float, h: float, chars: int, lines: int, aspect: str = "9:16") -> float:
    """The research's dynamic font clamp (findings s2.3), for `lines` lines of `chars` characters."""
    f = treemap_floors(aspect)
    inner_w, inner_h = w - 2 * f["pad"], h - 2 * f["pad"]
    lo, hi = f["label_font"]
    return max(0.0, min(hi, inner_w / max(1, chars) / TREEMAP_CHAR_W,
                        inner_h / TREEMAP_LINE_H.get(lines, 2.2 * lines / 2))) if inner_w > 0 and inner_h > 0 else 0.0


def label_tier(w: float, h: float, label: str, value_text: str, aspect: str = "9:16") -> dict:
    """The three-tier label degradation (research s1 and s5's teardown of Bravos 89-91):
      2 - two lines, the label and its value, both at or above the legible floor;
      1 - ONE stacked line: the label alone;
      0 - none. The cell is a tile and the part is counted in the legend instead.
    The floors are the cell's own size in STAGE pixels; the font clamp is what refuses a long name in
    a cell that is wide enough for a short one."""
    f = treemap_floors(aspect)   # P72 T13 (R26-217): the floors of the stage the cell is drawn on
    lo = f["label_font"][0]
    if w >= f["two_line"][0] and h >= f["two_line"][1]:
        chars = max(len(label), len(value_text))
        font = _clamp_font(w, h, chars, 2, aspect)
        value_font = max(f["value_font"], round(font * 0.72))
        if font >= lo and value_font >= f["value_font"] and (font + value_font) * 1.15 <= h - 2 * f["pad"]:
            return {"tier": 2, "font": round(font, 1), "value_font": round(float(value_font), 1)}
    if w >= f["min_cell"][0] and h >= f["min_cell"][1]:
        font = _clamp_font(w, h, len(label), 1, aspect)
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
        tier = label_tier(r["w"], r["h"], label, vs, aspect)
        cells.append({"index": i, "label": label, "value": values[i], "value_string": vs,
                      "share": round(share, 6),
                      "fx": round(r["x"] / max(1e-9, plot["w"]), 6), "fy": round(r["y"] / max(1e-9, plot["h"]), 6),
                      "fw": round(r["w"] / max(1e-9, plot["w"]), 6), "fh": round(r["h"] / max(1e-9, plot["h"]), 6),
                      "w_px": round(r["w"], 1), "h_px": round(r["h"], 1), **tier})
    unnamed = sum(1 for c in cells if c["tier"] == 0)
    return {"plot": plot, "cells": cells, "unnamed": unnamed,
            # the parts the page could not name are COUNTED, never dropped: the census says how many there were
            "legend": f"and {unnamed} others" if unnamed else ""}


def treemap_area_error(spec: dict) -> float:
    """P69 T50 / E99 s100 (a), MEASURED: the worst gap, over both stages, between a cell's share of its plot and its
    value's share of the parts drawn - 0 is every area true to its value. Pure."""
    worst = 0.0
    for lay in (spec.get("layout") or {}).values():
        cells = lay.get("cells") or []
        drawn = sum(float(c.get("value") or 0.0) for c in cells) or 1.0
        for c in cells:
            worst = max(worst, abs(float(c["fw"]) * float(c["fh"]) - float(c.get("value") or 0.0) / drawn))
    return worst


def treemap_honesty_warnings(series: dict, spec: dict) -> list[str]:
    """P69 T50 / E99 s100 + s106: a treemap whose own words make a SIZE claim ("bigger than", "twice") is a page; it is
    honest when every area is true (measured) and the figures it compares are WRITTEN. The WARN names, per stage, how
    many cells write their figure and which cannot (the label floors cull a small cell's value first). [] for a census
    with no size claim, or one whose every figure is written - such a spec gains no key. Pure."""
    claim = _size_claim(series)
    layout = spec.get("layout") or {}
    if not claim or not layout:
        return []
    order = [str(x) for x in spec.get("labels") or []]
    stages = sorted(layout, key=lambda a: (a != "16:9", a))
    unwritten = {a: {str(c["label"]) for c in layout[a].get("cells") or [] if int(c.get("tier") or 0) < 2} for a in stages}
    if not any(unwritten.values()):
        return []
    n = len(order)
    counts = " and ".join(f"{n - len(unwritten[a])} of {n} cells at {a}" for a in stages)
    names = [x for x in order if any(x in u for u in unwritten.values())]
    shown = ", ".join(names[:6]) + (f" and {len(names) - 6} more" if len(names) > 6 else "")
    return [f"{FORM_WARN} treemap: the page's {claim[0]} says {claim[1]!r} - a SIZE claim read off areas. Every cell is "
            f"drawn true to its value (off by {treemap_area_error(spec):.1e} of the plot at worst); the figures are "
            f"written on {counts} - unwritten: {shown}. A size claim needs the figures it compares WRITTEN "
            f"(E99 s100 (b)): name them in the {claim[0]}, cross them with their share, or draw them as --variant bars "
            "(the fastest read of a size, E53 s1). REPORTED, the frame read decides (E99 s106)"]


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
        keyed = next((i for i, e in enumerate(series.get("series") or []) if col and isinstance(e, dict)
                      and e.get("color") == col), None)
        side = y2_side(series, keyed) if keyed is not None else None
        if side:   # P71 T13: on a y2 page the badge says which axis its line is read on (Bravos's "(LHS)" / "(RHS)")
            bd["label"] = f"{bd['label']} ({side})"
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
    ranged = [i for i, bar in enumerate(bars) if _is_range(bar.get("value"))]
    if ranged and pick_builder(series, variant) != "story":   # P69 T8d
        errors.append(f"bars{ranged} carry a range: a range is a BARS chart's (a bar at its near end, a band to its far "
                      f"one) - this page draws its values as {pick_builder(series, variant)!r}")
    if ranged and series.get("overflow") is not None:
        errors.append(f"bars{ranged} carry a range on a breakthrough page (overflow): the breakthrough shoots ONE value "
                      "past its stated scale, and a range has two - state the range on a page of its own scale")
    unit = str(series.get("unit") or "")
    for i, bar in enumerate(bars):
        errors += bar_value_errors(f"bars[{i}]", bar, unit)   # P69 T8d: a number, or an honest range
        if not _text(bar.get("label")):
            errors.append(f"bars[{i}] has no label (one label per datum)")
    if bars and pick_builder(series, variant) == "story" and len(bars) > STORY_MAX_VALUES:
        errors.append(f"story shape carries {len(bars)} values; the ceiling is {STORY_MAX_VALUES}")
    for i, entry in enumerate(dense_series(series)):
        proj = entry.get(PROJECTION_KEY)   # P71 T16: a projection is named by its own label (its tag writes it)
        if not (_text(entry.get("label")) or _text(entry.get("name")) or (isinstance(proj, dict) and _text(proj.get("label")))):
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
    series = with_schematic(series)   # P70 T2: a schematic object draws the series it generates (itself when it names none)
    out_series = series                        # P71 T25: the object as written - `projected` read before it stands in as a value
    series = with_projected_values(series)     # P71 T25: a projected bar's height is its projection (the same object when none)
    builder = builder or pick_builder(series, variant)
    spec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "surface": "page", "builder": builder,
        "variant": variant, "title": series.get("title"), "sub": series.get("sub", ""),
        "source": series.get("src"), "quiet_zone": quiet_zone,
        **({"src_style": series["src_style"]} if series.get("src_style") in ("compact",) else {}),   # the design pass (2026-09-07): a citation takes minimal space
        **({SOURCE_LINES_KEY: [str(x) for x in series[SOURCE_LINES_KEY]]} if _source_lines_ok(series.get(SOURCE_LINES_KEY)) else {}),   # P71 T30: the long form's two-line source (absent: not one key)
        **({TITLE_STYLE_KEY: series[TITLE_STYLE_KEY]} if series.get(TITLE_STYLE_KEY) in TITLE_STYLES else {}),   # P71 T30: the title in the accent capsule (absent: not one key)
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
        if "explode" in spec and not (isinstance(series.get("explode"), dict) and "index" in series["explode"]):
            spec["explode"] = dict(spec["explode"], index=spec["emphasize"])   # P69 T48: `explode: true` is the claim's slice
        honesty = share_honesty_warnings(series)   # P69 T50: only past the guidance - a page inside it gains no key
        if honesty:
            spec["warnings"] = list(spec.get("warnings") or []) + honesty
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
            honesty = treemap_honesty_warnings(series, spec)   # P69 T50: only a size claim with a figure unwritten
            if honesty:
                spec["warnings"] = honesty
        return spec
    if builder == PANELS:   # P69 T8b: 2-4 line plots on one page, one scale by default (E79)
        spec.update(_panels_block(series))
        warnings = panel_scale_warnings(series)
        if warnings:
            spec["warnings"] = warnings
        spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
        spec["judge"] = review_notes(series)
        spec["badges"] = badges_for(series)
        spec["emphasize"] = None
        parsed = parse_readability((spec.get("axes") or {}).get("readability"))
        if parsed and parsed[0] == LONGFORM:
            apply_longform(spec, parsed[1])
        return spec
    if builder == "race":
        spec.update(_race_block(series))
    elif builder == "dense-line":
        spec.update(_dense_block(series))
        if isinstance(series.get(SCHEMATIC_KEY), dict):   # P70 T2: the shape, its phases and its tag (absent: not one key)
            spec[SCHEMATIC_KEY] = schematic_block(series[SCHEMATIC_KEY])
            spec["axes"]["domain"] = list(schematic_domain(series[SCHEMATIC_KEY]))   # the shape floats with its names' room; no tick writes it
        if isinstance(series.get(Y2_KEY), dict):   # P71 T13 / s102: the second axis (absent: not one key)
            spec[Y2_KEY] = y2_block(series)
            if y2_warnings(series):
                spec["warnings"] = list(spec.get("warnings") or []) + y2_warnings(series)
        if projection_source(series) is not None:   # P71 T16 / s93: the source line names each projection (absent: not one key)
            spec["source"] = projection_source(series)
            if projection_warnings(series):
                spec["warnings"] = list(spec.get("warnings") or []) + projection_warnings(series)
    else:
        spec.update(_story_block(series))
        if builder == "story" and (OPENS_ON_KEY in out_series or _projected_index(out_series) is not None):   # P71 T25 (absent: not one key)
            spec.update(bars_out_block(out_series))
            if projected_source(out_series) is not None:
                spec["source"] = projected_source(out_series)
            if bars_out_warnings(out_series):
                spec["warnings"] = list(spec.get("warnings") or []) + bars_out_warnings(out_series)
    if builder == "combo":
        spec.update({k: v for k, v in _dense_block(series).items() if k != "labels"})
        if spec.get(SEGMENTS_KEY) and _text(series.get(LINE_LABEL_KEY)):   # P69 T64: the stacked combo's right axis, named (s102 (b))
            spec[LINE_LABEL_KEY] = str(series[LINE_LABEL_KEY])
    if builder == "decline":
        spec.update(_decline_block(series, spec))
    if variant == "progress" and "denominator" in series:
        spec["denominator"] = value_string(series["denominator"])
    spec["unit"] = str(series["unit"]) if _text(series.get("unit")) else ""
    if isinstance(series.get(UNIT_SUFFIX_KEY), str) and series[UNIT_SUFFIX_KEY]:
        spec[UNIT_SUFFIX_KEY] = series[UNIT_SUFFIX_KEY]   # P72 T13 / R26-287: "$480B" (absent: not one key)
    spec["judge"] = review_notes(series)
    spec["badges"] = badges_for(series)
    count = len(spec["labels"])
    spec["emphasize"] = None if emphasize is None or not count else max(0, min(int(emphasize), count - 1))
    parsed = parse_readability((spec.get("axes") or {}).get("readability"))
    if parsed and parsed[0] == LONGFORM:   # P69 T8: the series file's own `readability: longform[:<preset>]`
        apply_longform(spec, parsed[1])
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
            "peel": peel, **(_pie_block(series) if share_solid(series) else {})}


def _pie_block(series: dict) -> dict:
    """P69 T48: the solid share page's keys - only on a page that names one (the P48 T4 pie gains nothing). Every
    slice's figure is written: its own `value_string`, else its value and the page's unit."""
    ext, exp, hole = _pie_options(series)
    unit = str(series.get("unit") or "")
    sep = "" if unit in ("%", "pp", "x") else " "
    out: dict[str, Any] = {"total": to_number(series.get("total")),
                           "value_strings": [value_string(s["value_string"]) if s.get("value_string") is not None
                                             else (value_string(s.get("value")) + (sep + unit if unit else ""))
                                             for s in series.get("shares") or []]}
    if hole is not None:
        out["hole"] = hole
    if ext is not None:
        out["extrude"] = ext
        lie = pie_area_lie(ext["tilt"], ext["depth"])
        if lie > PIE_AREA_LIE_MAX + 1e-9:
            out["warnings"] = [f"WARN share: the tilt {ext['tilt']:g} deg at depth {ext['depth']:g} lets a slice's apparent "
                               f"area read {lie:.2f}x its share (bound {PIE_AREA_LIE_MAX:g}x; the default "
                               f"{PIE_TILT_DEG} deg / {PIE_DEPTH:g} reads {pie_area_lie(PIE_TILT_DEG, PIE_DEPTH):.2f}x). "
                               "Every figure is written on its slice, so the number carries the claim - REPORTED, "
                               "the frame read decides (E99 s106, s109 (4))"]
    if exp is not None:
        out["explode"] = exp
    return out


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
    block = {"labels": list(labels), "values": [to_number(v) for v in raw],
             "value_strings": [value_string(v) for v in raw], "colors": list(colors),
             **({"axes": axes} if axes else {})}
    return _with_segments(_with_member_tiles(_with_ranges(block, _bars(series)), series), series)   # P69 T45 / T64: absent members and segments, untouched


def _with_ranges(block: dict, bars: list[dict]) -> dict:
    """P69 T8d: a bars block whose bars carry a RANGE - each range bar's value is the end it is DRAWN to (`range_foot`),
    its string the range as stated (`range_string`), and `ranges` names both ends per bar (None for a single value).
    A block with no range is returned untouched - no `ranges` key, the page it always was."""
    rngs = [bar_range(b) for b in bars]
    if not any(rngs):
        return block
    block["values"] = [range_foot(*r) if r else v for r, v in zip(rngs, block["values"])]
    block["value_strings"] = [range_string(b) if r else s for r, b, s in zip(rngs, bars, block["value_strings"])]
    block["ranges"] = [[r[0], r[1]] if r else None for r in rngs]
    return block


def _dense_block(series: dict) -> dict:
    # P48 T3: a series marked `later: true` waits off the page - an `extend` derives the state that draws it on
    own = series.get("series") or []
    if any(isinstance(s, dict) and isinstance(s.get(PROJECTION_KEY), dict) for s in own):   # P71 T16: its tag is its label (absent: not one byte)
        series = dict(series, series=[projection_line(own, i) if isinstance(s, dict) and isinstance(s.get(PROJECTION_KEY), dict)
                                      else s for i, s in enumerate(own)])
    if any(isinstance(s, dict) and isinstance(s.get(INK_FROM_KEY), dict) for s in series.get("series") or []):   # P71 T28 (absent: not one byte)
        series = dict(series, series=[ink_from_line(s) if isinstance(s, dict) and isinstance(s.get(INK_FROM_KEY), dict) else s
                                      for s in series.get("series") or []])
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
FULL_STAGE_BANDS_KEY = "full_stage_bands"
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


def _full_stage_bands(w_s: int, h_s: int) -> dict:
    """R26-230's explicit 16:9 bands, derived from the page and caption constants.

    The evidence rectangle is the vertical area in which the page's PLOT ink may live. The chart
    box itself can extend below it for SVG letterbox air; the boundary protects the ink, not an
    empty chart canvas. The top and bottom bands are full-stage strips so a long-form page can be
    re-staged as a 9:16 layout instead of cropped into one.
    """
    safe_x, _safe_y, safe_w, _safe_h = SAFE_BOX["16:9"]
    caption_top = CAPTION_ANCHOR["16:9"][1]
    evidence_top = LAND_FULL["Y"] * h_s
    return {
        "top": _box(0, 0, w_s, evidence_top),
        "bottom": _box(0, caption_top, w_s, h_s - caption_top),
        "evidence_safe": _box(safe_x, evidence_top, safe_w, caption_top - evidence_top),
    }


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

    The plot is a fraction of the DRAWN chart, not of the box. Legacy pages use the 1000x560 SVG
    under the default preserveAspectRatio and retain its measured letterbox law. T17's opt-in
    changes both the chart width and the SVG viewBox width, so the matched profile has no spare
    horizontal air and the actual plot grows."""
    if _readability_profile(spec) == LONGFORM:   # P69 T8: the long form lays its own page out (the engine measures it)
        return _longform_full_boxes(spec, w_s, h_s)
    bx, by, bw, bh = LAND_BOARD
    half = 0.5 / PUNCH_SCALE
    vx, vy = bx + bw / 2 - half, by + bh / 2 - half
    F, L, I = LAND_FULL, LAND_PLOT, LAND_FULL_INK
    profile = _landscape_profile_geometry(spec, w_s, h_s)
    cx, cy = F["X"] * w_s, F["Y"] * h_s
    if profile:
        cw, ch = profile["w"], profile["h"]
        vw, vh, s = profile["vw"], profile["vh"], profile["scale"]
        ox, oy = cx, cy
    else:
        cw, ch = F["W"] * w_s, F["H"] * h_s
        vw, vh = LAND_VIEWBOX
        s = min(cw / vw, ch / vh)
        ox, oy = cx + (cw - vw * s) / 2, cy + (ch - vh * s) / 2
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
    # The phone profile increases the SVG label face, so mirror the renderer's local face
    # height and its slightly lifted baseline here.  Legacy pages keep the measured values.
    ylab = (LAND_PHONE_FONT_PX * s if profile else YLABEL_H) if (spec.get("axes") or {}).get("ylabel") else 0
    tick_b = LAND_PHONE_TICK_B if profile else LAND_TICK_B
    tag_b = profile["B"] if profile else L["B"]
    title_h = I["title"] * LAND_PHONE_TEXT_PX / 34 if profile else I["title"]
    sub_h = I["sub"] * LAND_PHONE_TEXT_PX / 21 if profile else I["sub"]
    src_h = I["src"] * LAND_PHONE_TEXT_PX / 22 if profile else I["src"]
    # The native dense-line margins are SVG units, not fractions of the variable
    # phone viewBox. Multiplying legacy fractions by vw misplaces both plot/tags.
    plot_left = LAND_PHONE_PLOT_L if profile else L["L"] * vw
    if spec.get("builder") == "story" and "left_gutter" in (spec.get("axes") or {}):
        plot_left = max(plot_left, float(spec["axes"]["left_gutter"]))
    plot_right = LAND_PLOT["R"] * LAND_VIEWBOX[0] if profile else L["R"] * vw
    return {
        "title": _box(ink_x, title_y, ink_w, title_h),
        "sub": _box(ink_x, sub_y, ink_w, sub_h),
        "chart": _box(cx, cy, cw, ch),
        "plot": _box(ox + plot_left * s, oy + L["T"] * vh * s - ylab,
                     (vw - plot_left - plot_right) * s, (tick_b - L["T"]) * vh * s + ylab),
        "source": _box(ink_x, src_y, ink_w, src_h),
        "rail": _box(ink_x, cy + ch + LAND_RAIL_GAP * PUNCH_SCALE * h_s, ink_w,
                     I["pill"] * -(-len(rail) // PORTRAIT_PILLS_PER_ROW) if rail else 0),
        # the END TAG COLUMN: the page's own inline names, beside the plot and part of the chart's ink.
        # It was air while a quiet zone kept the chart to 60 % of its board; at full stage it is the
        # only thing between the plot and the frame, so `free_bands` has to know it is there.
        "tags": _box(ox + (vw - plot_right + LAND_TAG_GAP) * s, oy + L["T"] * vh * s,
                     (profile["tag_units"] if profile else tag_units(spec)) * s,
                     (tag_b - L["T"]) * vh * s),
    }


LAND_VIEWBOX = (1000, 560)   # the landscape chart's viewBox; a portrait chart's viewBox IS its pixel box (the template: "builders draw in stage px")

# T17: this is deliberately a geometry profile, not a global type dial. The chart keeps the
# existing 560-unit vertical viewBox and fixed line-builder margins; only its horizontal user
# extent follows the page's safe rendered width. `sname` and its inline `tagchip` are 46px in the
# opt-in renderer (44px was the starting point; the browser floor required a two-pixel margin),
# so both advances are scaled from the existing 24px/18px bounds.
LAND_PHONE_VIEWBOX_H = LAND_VIEWBOX[1]
LAND_PHONE_NAME_U = LAND_TAG_NAME_U * 46.0 / 24.0
LAND_PHONE_BADGE_U = LAND_TAG_BADGE_U * 46.0 / 18.0
LAND_PHONE_MIN_VIEWBOX_W = LAND_VIEWBOX[0]
LAND_PHONE_SAFE_RIGHT = 0.979
LAND_PHONE_FONT_PX = 46
LAND_PHONE_PLOT_L = 120
LAND_PHONE_TEXT_PX = 52
LAND_PHONE_B = 458
LAND_PHONE_TICK_B = (LAND_PHONE_B + 32) / LAND_PHONE_VIEWBOX_H
# P69 T8 - THE LONG FORM'S TYPE SCALE (the parent's frame read, 2026-09-23: the look is right, the SCALE is the
# operator's call). E99 s90 (B's roughly 12.5 px phone type) and E99 s97 (Bravos's measured 15-18 px ticks) pull
# the page's type opposite ways, so the profile carries THREE named presets and the row picks one -
# `;readability=longform:bravos|middle|phone` (plain `longform` is `middle`) - for P69-HG3 to rule on. Every size is
# a FONT SIZE in px as RENDERED on the 1920 x 1080 stage (the page ink through the punch, the chart's through its
# own rest scale); the engine's `LP_LONGFORM.TYPE_SCALE` is the same table.
#   bravos  [DERIVED: BRAVOS-LONGFORM-CHART-SPEC.md (a)/(b), a cap or digit height / Inter's 0.727 cap ratio] - the
#           title cap 28 (t530) -> 38.5; the tick digit 16.5 (t170 15 / t530 18) -> 22.7; the line badge's 14 px
#           digits (t170) -> 19.3 for an end tag, its chip at 0.8 of it; the value beside a bar, 31.5 (t1088) ->
#           43.3; the source cap 10.5 (t170/t530) -> 14.4; the sub, unmeasured on a chart page, sits at 24.
#   middle  the working default (the parent, 2026-09-23): title 44, sub 26, ticks 26, end tags 30, source 20.
#   phone   E99 s90's floor, T17's own render: the page ink 52 CSS px x the 1.16 punch = 60.3, the chart's 46 units
#           x its 1.334 rest scale = 61.4 (~12.5 px on a 390 px phone).
LONGFORM_PRESETS = ("bravos", "middle", "phone")
LONGFORM_DEFAULT_PRESET = "middle"
LONGFORM_TYPE_SCALE = {
    "bravos": {"title": 38.5, "sub": 24.0, "tick": 22.7, "tag": 19.3, "chip": 15.4, "value": 43.3, "src": 14.4},
    "middle": {"title": 44.0, "sub": 26.0, "tick": 26.0, "tag": 30.0, "chip": 24.0, "value": 34.0, "src": 20.0},
    "phone": {"title": 60.3, "sub": 60.3, "tick": 61.4, "tag": 61.4, "chip": 61.4, "value": 61.4, "src": 60.3},
}
# The layout the engine MEASURES and this module ESTIMATES (the fixture outranks the estimate, as `PORTRAIT_INK`'s):
# the title, sub and source wrap in one ink column (to the stage's safe right edge) at a 1.1 leading, the sub
# LONGFORM_SUB_GAP CSS px under the title's last line. The chart box then takes the room that is left: its plot
# top stands M28's half-figure of air (half the tick size) plus the ink it carries above the plot (the y label,
# LONGFORM_YLAB_GAP_PX over the plot; a rule's name; half the top tick) under the sub - the chart moves DOWN,
# never onto the sub - and its foot rises only when the wrapped source would leave the stage (LONGFORM_EDGE_PX).
# Advances are Inter's in ems per character (Bold title and end tag, Regular sub and source, the 600 chip).
LONGFORM_LINE_H = 1.1
LONGFORM_SUB_GAP = 8
LONGFORM_TAG_EM = {"name": 0.68, "chip": 0.64}
LONGFORM_CHIP_DX_PX = 12
LONGFORM_YLAB_GAP_PX = 14
LONGFORM_EDGE_PX = 16
LONGFORM_PLOT_T = {"dense-line": 40.0, "story": 90.0, PANELS: 0.0}   # each builder's own plot top, in chart units (P69 T8b: a panels page's region IS its top - each panel carries its own plot top inside its box)
# REVIEW-P69-LANE-B-MERGE-2 N3 - THE PAGE INK'S ADVANCES, READ OFF THE FACE ITSELF. The first estimate wrapped the
# title, sub and source at a flat 0.56 / 0.5 em a character, and a one-line miscount moved every box under it (the
# long page at `phone`: the chart 73 px below the engine's). The page writes each glyph as its own inline-block
# (`lpGlyphsWrap`: no kerning, no shaping across glyphs) and each word as an unbreakable run, so a line's width IS the
# sum of the glyphs' advances - exactly computable from Inter's `hmtx`. The face is VARIABLE on two axes (wght 100-900,
# opsz 14-32) and the browser sets opsz to the CSS font size (font-optical-sizing: auto), so the advances are stored
# at the weight each role is set in (the title 700; the sub and the source 400) at opsz 14 and 32, in font units of
# 2048 per em, and interpolated linearly in opsz between them [MEASURED 2026-09-23 on the tracked
# `src/assets/fonts/Inter-Variable.ttf` with fontTools' instancer; the linear interpolation is within 0.5 units of
# the instanced advance at opsz 20.69 for every character - `test_longform_profile` regenerates the table].
# A character outside the table takes its weight's mean advance.
LONGFORM_ADV_CHARS = (" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
                      "‘’“”–—·•…é€£¥×→°½")
LONGFORM_ADV_UPM = 2048
LONGFORM_OPSZ = (14.0, 32.0)
LONGFORM_WEIGHT = {"title": 700, "sub": 400, "source": 400, "key": 500}   # P69 T10: the key pill's name is Inter Medium (the spec's pill)
LONGFORM_ADVANCES = {   # (weight, opsz) -> the advance of each LONGFORM_ADV_CHARS character, in font units
    (400, 14): tuple(int(v) for v in (
        "576 589 954 1297 1314 2011 1319 614 747 747 1026 1355 590 942 590 738 1292 833 1249 1265 1323 1215 1270 1159 1267 1270 590 618 1355 1355 1355 1047 "
        "1978 1413 1340 1496 1478 1231 1209 1528 1522 550 1169 1376 1158 1850 1543 1566 1308 1566 1318 1314 1322 1524 1413 2018 1397 1390 1288 747 738 747 965 934 "
        "661 1150 1254 1170 1254 1194 758 1256 1211 496 496 1124 496 1794 1210 1228 1254 1254 771 1081 670 1211 1151 1676 1118 1151 1131 873 681 873 1355 534 "
        "534 902 902 1024 2048 590 1152 1770 1194 1365 1251 1126 1355 1954 933 1735").split()),
    (400, 32): tuple(int(v) for v in (
        "512 450 826 1228 1258 1728 1246 520 612 612 960 1286 450 878 450 666 1256 742 1149 1226 1265 1181 1196 1056 1192 1196 450 456 1286 1286 1286 1073 "
        "1994 1338 1307 1479 1412 1187 1135 1496 1450 476 1095 1299 1096 1756 1454 1534 1253 1534 1295 1258 1250 1440 1338 1944 1322 1316 1256 612 666 612 896 930 "
        "494 1060 1158 1071 1158 1098 627 1158 1120 422 422 1039 422 1718 1120 1124 1158 1158 660 972 637 1120 1048 1540 1038 1048 980 788 606 788 1286 390 "
        "390 694 696 1024 2048 450 1024 1350 1098 1298 1192 1058 1286 1890 866 1548").split()),
    (700, 14): tuple(int(v) for v in (
        "485 692 1129 1329 1341 2080 1376 694 772 772 1145 1390 684 958 684 795 1381 883 1289 1322 1385 1274 1330 1191 1333 1330 684 702 1390 1390 1390 1146 "
        "2081 1529 1355 1515 1479 1244 1202 1537 1530 575 1197 1473 1158 1908 1561 1578 1327 1591 1345 1341 1367 1499 1529 2125 1512 1497 1360 772 795 772 997 975 "
        "748 1189 1291 1205 1291 1220 815 1294 1275 555 555 1188 555 1869 1275 1256 1291 1291 834 1147 750 1275 1228 1741 1188 1233 1173 960 761 960 1390 636 "
        "636 1106 1089 1024 2048 684 971 2052 1220 1402 1308 1168 1390 1954 941 1805").split()),
    (500, 14): tuple(int(v) for v in (   # P69 T10: the key pill's Medium, read the same way
        "546 623 1012 1308 1323 2034 1338 641 755 755 1066 1367 621 947 621 757 1322 850 1262 1284 1344 1235 1290 1170 1289 1290 621 646 1367 1367 1367 1080 "
        "2012 1452 1345 1502 1478 1235 1207 1531 1525 558 1178 1408 1158 1869 1549 1570 1314 1574 1327 1323 1337 1516 1452 2054 1435 1426 1312 755 757 755 976 948 "
        "690 1163 1266 1182 1266 1203 777 1269 1232 516 516 1145 516 1819 1232 1237 1266 1266 792 1103 697 1232 1177 1698 1141 1178 1145 902 708 902 1367 568 "
        "568 970 964 1024 2048 621 1092 1864 1203 1377 1270 1140 1367 1954 936 1758").split()),
    (500, 32): tuple(int(v) for v in (
        "488 468 873 1245 1284 1792 1272 532 634 634 1006 1304 467 889 467 692 1281 761 1175 1240 1292 1197 1219 1079 1214 1219 467 472 1304 1304 1304 1103 "
        "2017 1379 1311 1482 1420 1206 1154 1500 1457 494 1114 1334 1111 1781 1464 1533 1266 1533 1307 1284 1267 1441 1374 1976 1357 1348 1270 634 692 634 913 944 "
        "531 1084 1180 1093 1180 1115 671 1180 1146 449 449 1068 449 1749 1146 1146 1180 1180 695 1003 676 1146 1077 1585 1059 1077 1010 825 641 825 1304 415 "
        "415 758 754 1024 2048 467 975 1401 1115 1317 1211 1079 1304 1896 875 1592").split()),
    (700, 32): tuple(int(v) for v in (
        "439 505 967 1280 1336 1920 1325 556 679 679 1097 1341 501 911 501 745 1332 798 1226 1269 1345 1229 1264 1126 1258 1264 501 505 1341 1341 1341 1162 "
        "2062 1461 1320 1487 1436 1245 1191 1507 1471 530 1151 1404 1140 1831 1485 1531 1293 1531 1332 1336 1301 1442 1445 2041 1428 1413 1299 679 745 679 948 973 "
        "604 1132 1224 1137 1224 1150 759 1224 1199 503 504 1127 503 1810 1199 1189 1224 1224 764 1065 755 1199 1134 1676 1100 1134 1071 900 710 900 1341 464 "
        "464 887 871 1024 2048 501 877 1502 1150 1354 1250 1120 1341 1907 893 1680").split()),
}
# N1 - WHAT STANDS UNDER THE CHART, and where. The anchored caption's STRIP runs from `full_stage_bands`' bottom band's
# top to the one-line caption's own foot (CAPTION_ANCHOR: 878-960 at 1920 x 1080). The source line and the key rail
# NEVER stand in it: each writes under the chart (the source LAND_SRC_GAP under it, the rail LAND_RAIL_GAP under it or
# LONGFORM_STACK_GAP_PX under the source's last line), and one that would meet the strip moves under its foot; when
# that leaves the stage (LONGFORM_EDGE_PX), the chart's foot rises until the source - then the rail - stands above
# the strip instead. The rail's pills are the template's own (a 41 CSS px row at 16:9 - 47.56 px rendered - 6 CSS px
# apart) [MEASURED: the `rail` fixture's one pill, 2026-09-23].
LONGFORM_STRIP = (CAPTION_ANCHOR["16:9"][1], CAPTION_ANCHOR["16:9"][1] + CAPTION_ANCHOR["16:9"][3])
LONGFORM_STACK_GAP_PX = 8
LONGFORM_PILL_PX = 41 * PUNCH_SCALE
LONGFORM_PILL_GAP_PX = 6 * PUNCH_SCALE
LONGFORM_PILLS_PER_ROW = 4
# the face's own line box: a chart label's box reaches its ascent above its baseline and its descent below it
# [MEASURED: Inter-Variable.ttf hhea 1984 / -494 of 2048 units per em]
LONGFORM_ASCENT, LONGFORM_DESCENT = 1984 / 2048, 494 / 2048
# An END TAG that will not fit the stage at its preset gives up its long name for its badge (the value and the short
# chip), then for its value alone - never a refusal (the parent, 2026-09-23). The long names belong in a key: that is
# P69 T10's badge key (below); the spec keeps every name for it.
LONGFORM_TAG_FORMS = ("full", "badge", "value")
# P69 T9 (3) (E99 s90: "x-tick labels must clear the axis line (main measured 18 px, T17 measured 0 px)"): a longform
# page's x labels - a line page's ticks, a bars page's names - stand with their box's top this far under the panel's
# foot line (its border, LONGFORM_BORDER_PX, the engine's LP_LONGFORM.BORDER_PX) [DERIVED: main's measured 18 px and
# two for the rendered box's rounding; T8's page measured 7].
LONGFORM_XLAB_CLEAR_PX = 20.0
LONGFORM_BORDER_PX = 1.5
# P69 T10 (E99 s90 "apply badges as the key"; E99 s84 "prefer to land on even pills (2 or 4)") - THE KEY RAIL. A line
# page whose end tags gave up their long names (`tag_form` badge or value) writes those names on a KEY: one pill per
# series, the Bravos category pill (BRAVOS-LONGFORM-CHART-SPEC.md (b) `category_pill`, t1088: a white capsule 40 px
# tall, r = h/2, a 15 px cap in #1E1F22 Inter 500, a 10 px dot on its left end) with the dot in the SERIES' own line
# colour, scaled to the preset. It stands in the page's TOP BAND - Bravos's own legend band (t170 / t1078), between the
# sub and the plot - hugging the chart's top ink with M28's half-figure of air, and when that band is too short the
# chart moves down to make it (the right margin is the end tags', and the stack under the chart is N1's source and
# rail over the caption strip). The key is ONE ROW, as Bravos's legend band is: set at the preset's size when its pills
# fit one row of the ink column, else at the largest size that does (the compiler fits it, as it fits the end tags:
# `axes.key_px`) - never under the spec's own pill (LONGFORM_KEY_MIN_PX), where a longer key wraps, greedily, as the
# browser's flex row does. At `phone` a key of long names therefore sets under s90's floor (the stage has no room for
# four of them at 61 px and a readable plot: the P69-HG3 card says so).
#   LONGFORM_KEY_PX  the pill's type, a FONT SIZE in rendered px [DERIVED: bravos, the spec's 15 px cap / Inter's 0.727
#                    cap ratio; middle, the preset's own chip (24); phone, E99 s90's floor at the preset's own 61.4].
#   LONGFORM_KEY_EM  the pill's box in ems of that size: h and the dot from the spec (40 / 20.6, 10 / 20.6), the pads
#                    and gaps [DERIVED: t1088's pill read at x5 - the dot a half-dot in from the left end, the name a
#                    dot's width after it].
# Every pill springs on recipe:badge-ladder's own clock (FIRST_BADGE_S 2.05 s after the chart has built, then
# BADGE_GAP_S 1.30 apart - the engine's LP_LONGFORM.KEY_FIRST / KEY_STEP). The key lands on an EVEN pill count where
# the series allow: an odd key takes one more of the page's lines, one whose end tag kept its own name - never an
# invented pill, so three shortened lines and nothing else to key stay three.
LONGFORM_KEY_PX = {"bravos": 20.6, "middle": 24.0, "phone": 61.4}
LONGFORM_KEY_EM = {"h": 40 / 20.6, "dot": 10 / 20.6, "pad_l": 0.55, "dot_gap": 0.4, "pad_r": 0.7, "gap": 0.5,
                   "row_gap": 0.35}
LONGFORM_KEY_MIN_PX = LONGFORM_KEY_PX["bravos"]   # the spec's measured pill: the key never sets smaller
LONGFORM_KEY_FIT_PX = 2.0   # the one-row fit's margin inside the column [DERIVED: the browser's sub-pixel layout]
LONGFORM_KEY_CLOCK = (2.05, 1.30)   # recipe:badge-ladder: FIRST_BADGE_S, BADGE_GAP_S
KEY_BOX = "key"   # page_boxes' key for the key rail's box (a longform page with a key only)


def longform_key(spec: dict) -> list[dict]:
    """The key rail's pills for a longform dense-line page: ``[{"series": i, "name": full name}]`` in the series' own
    order - every live series whose end tag gave up its name (`tag_form` badge or value, a label AND a name), then, if
    that is an odd count, the first other live series that names itself (the even pill count, E99 s84). ``[]`` when the
    tags keep their names."""
    axes = spec.get("axes") or {}
    if spec.get("builder") != "dense-line" or axes.get("tag_form") in (None, "full"):
        return []
    live = [(i, s) for i, s in enumerate(spec.get("series") or []) if isinstance(s, dict) and not s.get("muted")]

    def text(s: dict) -> str:
        return str(s.get("name") or s.get("label") or "").strip()

    keyed = {i for i, s in live if str(s.get("label") or "").strip() and str(s.get("name") or "").strip()}
    if len(keyed) % 2:
        extra = next((i for i, s in live if i not in keyed and text(s)), None)
        if extra is not None:
            keyed.add(extra)
    sided = spec if isinstance(spec.get(Y2_KEY), dict) else None   # P71 T13: on a y2 page each pill names its axis
    return [{"series": i, "name": text(s) + (f" ({y2_side(sided, i)})" if sided else "")} for i, s in live if i in keyed]


def longform_key_pill_w(name: str, px: float) -> float:
    """One key pill's width in rendered px at the key's size `px`: its pads, its dot and its name's Medium advances (the
    engine sets the pill with no kerning or ligatures, so the name's width IS the sum of its advances)."""
    em = LONGFORM_KEY_EM
    return longform_text_px(name, "key", px) + (em["pad_l"] + em["dot"] + em["dot_gap"] + em["pad_r"]) * px


def _longform_key_row(key: list, px: float) -> float:
    """The key's pills in one row at `px`, rendered px wide."""
    return sum(longform_key_pill_w(k["name"], px) for k in key) + LONGFORM_KEY_EM["gap"] * px * (len(key) - 1)


def longform_key_px(spec: dict, w_s: int = 1920) -> float:
    """The size the key is set in: the preset's own when its pills fit one row of the ink column, else the largest
    size (to the tenth of a px) at which they do, never under LONGFORM_KEY_MIN_PX."""
    key = (spec.get("axes") or {}).get("key") or []
    px0, room = LONGFORM_KEY_PX[longform_preset(spec)], _longform_ink_col(w_s)[1] - LONGFORM_KEY_FIT_PX
    if not key or _longform_key_row(key, px0) <= room:
        return px0
    lo, hi = min(LONGFORM_KEY_MIN_PX, px0), px0
    if _longform_key_row(key, lo) > room:
        return lo
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _longform_key_row(key, mid) <= room else (lo, mid)
    return math.floor(lo * 10) / 10


def longform_key_box(spec: dict, col_w: float) -> tuple[float, float]:
    """The key rail's (w, h) in rendered px in an ink column `col_w` wide: the pills wrapped greedily into rows (the
    browser's flex-wrap), the box as wide as its one row or the column. (0, 0) when the page has no key.
    REVIEW-P69-LANE-B-MERGE-3 M1: a page whose `then=` states key more than it does carries the band they need
    (`axes.key_w` / `key_h`, apply_longform_states) - its key box is the larger of the two."""
    axes = spec.get("axes") or {}
    w, h = _longform_key_own(spec, col_w)
    return max(w, float(axes.get("key_w") or 0.0)), max(h, float(axes.get("key_h") or 0.0))


def _longform_key_own(spec: dict, col_w: float) -> tuple[float, float]:
    """The (w, h) of this spec's OWN key, wrapped in the column; (0, 0) when it has none."""
    axes = spec.get("axes") or {}
    key = axes.get("key") or []
    if not key:
        return 0.0, 0.0
    px, em = float(axes.get("key_px") or LONGFORM_KEY_PX[longform_preset(spec)]), LONGFORM_KEY_EM
    gap = em["gap"] * px
    rows, run = 1, 0.0
    for k in key:
        w = longform_key_pill_w(k["name"], px)
        if run and run + gap + w > col_w + 0.5:
            rows, run = rows + 1, w
        else:
            run = run + gap + w if run else w
    one_row = sum(longform_key_pill_w(k["name"], px) for k in key) + gap * (len(key) - 1)
    return min(one_row, col_w), rows * em["h"] * px + (rows - 1) * em["row_gap"] * px


def parse_readability(value: Any) -> tuple[str, str | None] | None:
    """``landscape-phone`` | ``longform`` | ``longform:<preset>`` -> (profile, preset), or None when not one."""
    if not isinstance(value, str):
        return None
    profile, colon, preset = value.partition(":")
    if profile == LANDSCAPE_PHONE and not colon:
        return profile, None
    if profile == LONGFORM and (not colon or preset in LONGFORM_PRESETS):
        return profile, preset or LONGFORM_DEFAULT_PRESET
    return None


def longform_preset(spec: dict) -> str:
    """The preset a longform page is set in."""
    preset = (spec.get("axes") or {}).get("type_scale")
    return preset if preset in LONGFORM_TYPE_SCALE else LONGFORM_DEFAULT_PRESET


def longform_type(spec: dict) -> dict:
    """The preset's sizes (rendered px) a longform page is set in."""
    return LONGFORM_TYPE_SCALE[longform_preset(spec)]


def longform_geom(t: dict, top: float, bot: float, floor: float | None = None) -> dict:
    """The chart-unit geometry a longform chart is drawn in, for a chart box from `top` to `bot` (rendered px): the
    engine's `lpLongformGeom`, line for line. The x ticks and the bar names hang under the plot with their box's top
    LONGFORM_XLAB_CLEAR_PX clear of the panel's foot line (P69 T9 (3), E99 s90: "x-tick labels must clear the axis
    line" - main measured 18 px, T17 0, T8's page 7), and the plot's floor rises until they clear `floor` - the anchored
    caption's strip, or (N1) the source line when the stack under the chart stands above the strip (`longform_stack`)."""
    s = (bot - top) / LAND_VIEWBOX[1]
    tick, cap_u = t["tick"] / s, ((LONGFORM_STRIP[0] if floor is None else floor) - top) / s
    xlab = LONGFORM_ASCENT * tick + (LONGFORM_XLAB_CLEAR_PX + LONGFORM_BORDER_PX / 2) / s   # T9 (3): the label's box top
    return {"scale": s, "tick": tick, "plot_l": max(70.0, 12 + 2.3 * tick),                  # clears the panel's foot
            "line_b": min(458.0, cap_u - 5 - xlab - LONGFORM_DESCENT * tick), "xtick_dy": xlab,
            "gutter": max(60.0, 40 + 2.6 * tick), "xlab_dy": xlab,
            "bars_b": min(440.0, cap_u - 5 - xlab - 1.4 * tick),
            "ylab_gap": LONGFORM_YLAB_GAP_PX / s, "rule_dy": (8 + 0.25 * t["tag"]) / s}


def longform_scale0(h_s: int = 1080) -> float:
    """One chart unit in rendered px on the UNSHIFTED longform chart box (LAND_FULL's height over the viewBox's): the
    scale every end-tag form is fitted at, because a chart the layout moves down only shrinks it."""
    return LAND_FULL["H"] * h_s / LAND_VIEWBOX[1]


def longform_tag_px(spec: dict, t: dict, form: str) -> float:
    """The widest end tag of a longform dense-line page in `form`, in rendered px (estimated at LONGFORM_TAG_EM)."""
    rides = {BADGE_ACCENT_COL.get(str(b.get("accent"))): str(b.get("tag") or "")
             for b in spec.get("badges") or [] if isinstance(b, dict) and b.get("inline")}
    out = 0.0
    for s in spec.get("series") or []:
        if not isinstance(s, dict) or s.get("muted"):
            continue
        label, name = str(s.get("label") or ""), str(s.get("name") or "")
        text = (label + " " + name).strip() if form == "full" else (label or name)
        px = len(text) * LONGFORM_TAG_EM["name"] * t["tag"]
        chip = rides.get(str(s.get("color")), "")
        if chip and form != "value":
            px += LONGFORM_CHIP_DX_PX + len(chip) * LONGFORM_TAG_EM["chip"] * t["chip"]
        out = max(out, px)
    return out


def longform_tag_units(spec: dict, t: dict, form: str, scale: float) -> float:
    """The widest end tag of a longform dense-line page in `form`, in chart units at `scale` (estimated)."""
    return longform_tag_px(spec, t, form) / scale


def _longform_max_vw(tags_u: float, scale: float, w_s: int = 1920) -> float:
    return ((LAND_PHONE_SAFE_RIGHT - LAND_FULL["X"]) * w_s / scale
            + LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP - tags_u)


def longform_tag_form(spec: dict, preset: str) -> str | None:
    """The fullest end-tag form that keeps every tag on the stage at the unshifted chart scale (a chart the layout
    moves down only shrinks its scale, which gives the tags more room), or None when not even the values fit."""
    t, scale = LONGFORM_TYPE_SCALE[preset], longform_scale0()
    for form in LONGFORM_TAG_FORMS:
        if _longform_max_vw(longform_tag_units(spec, t, form, scale), scale) >= LAND_PHONE_MIN_VIEWBOX_W:
            return form
    return None


def longform_page_vw(spec: dict, scale: float | None = None, w_s: int = 1920) -> float:
    """The viewBox width a longform chart is drawn in (the engine's `lpLongformVW`): a dense-line page's is narrowed
    until its widest end tag - its own, in its own form, or (N2) the widest its `then=` states write, carried as
    `axes.tag_room` - ends inside the stage's safe right edge; a bars page keeps the legacy 1000 (at `phone`, its own
    `longform_bars_vw`)."""
    if spec.get("builder") != "dense-line":
        return float(LAND_VIEWBOX[0])
    scale = longform_scale0() if scale is None else scale
    axes = spec.get("axes") or {}
    px = max(longform_tag_px(spec, longform_type(spec), axes.get("tag_form") or "full"), float(axes.get("tag_room") or 0))
    return max(float(LAND_PHONE_MIN_VIEWBOX_W), _longform_max_vw(px / scale, scale, w_s))


def longform_bars_vw(spec: dict, scale: float, w_s: int = 1920) -> float:
    """P72 T12 (R26-339; D1 keeps the `phone` preset): the viewBox width a longform BARS page is drawn in - the legacy
    1000 at every preset but `phone`, where the chart runs to the stage's safe right edge (its 61.4 px words leave it a
    small scale, and 1000 units left the plot on the left 41 % of the stage: the key sat over the total). The engine's
    `lpLongformBarsVW`, line for line; a dense-line page has its own (`longform_page_vw`). A `then=` LINE state is drawn
    in the same viewBox, so its widest end tag (`axes.tag_room`, apply_longform_states) keeps its room at the right, as
    a dense-line page's own does."""
    if spec.get("builder") == "dense-line" or longform_preset(spec) != "phone" or not scale > 0:
        return float(LAND_VIEWBOX[0])
    room = float((spec.get("axes") or {}).get("tag_room") or 0)
    vw = _longform_max_vw(room / scale, scale, w_s) if room > 0 else (LAND_PHONE_SAFE_RIGHT - LAND_FULL["X"]) * w_s / scale
    return max(float(LAND_VIEWBOX[0]), round(vw * 1000) / 1000)


def apply_longform(page: dict, preset: str | None = None) -> dict:
    """Stamp a page with the long form's profile: `axes.readability`, the preset it is set in (`type_scale`) and, on a
    dense-line page, the end-tag form that fits (`tag_form`). In place; the page is returned."""
    axes = page.setdefault("axes", {})
    axes["readability"] = LONGFORM
    axes["type_scale"] = preset if preset in LONGFORM_PRESETS else (
        axes.get("type_scale") if axes.get("type_scale") in LONGFORM_PRESETS else LONGFORM_DEFAULT_PRESET)
    if page.get("builder") == "dense-line":
        axes["tag_form"] = longform_tag_form(page, axes["type_scale"]) or "value"
    else:
        axes.pop("tag_form", None)
    if page.get("builder") == PANELS:   # P69 T8b: each panel's end tags fitted to ITS box; one key for the page
        return _chrome_room(_apply_longform_panels(page))
    key = longform_key(page)   # P69 T10: the names the end tags gave up, and the size their one row is set in
    axes.pop("key_px", None)
    if key:
        axes["key"] = key
        axes["key_px"] = longform_key_px(page)
    else:
        axes.pop("key", None)
    return _chrome_room(page)


def _chrome_room(page: dict) -> dict:
    """P71 T30: a page naming the long form's chrome carries a WARN (CHROME_WARN) when the two options take more than
    CHROME_ROOM_SHARE of its chart box - the box with them against the box without, both the estimate's
    (`_longform_full_boxes`, held to the engine's page by test_longform_chrome). Re-fitted on every call (a stale finding
    is dropped); a page naming neither option is never touched. In place; the page is returned."""
    named = [k for k in (SOURCE_LINES_KEY, TITLE_STYLE_KEY) if page.get(k)]
    if not named:
        return page
    kept = [w for w in page.get("warnings") or [] if not str(w).startswith(CHROME_WARN)]
    w_s, h_s = STAGE_PX["16:9"]
    h_on = _longform_full_boxes(page, w_s, h_s)["chart"]["h"]
    h_off = _longform_full_boxes({k: v for k, v in page.items() if k not in named}, w_s, h_s)["chart"]["h"]
    if h_off > 0 and h_on < (1 - CHROME_ROOM_SHARE) * h_off:
        preset = (page.get("axes") or {}).get("type_scale") or LONGFORM_DEFAULT_PRESET
        kept.append(f"{CHROME_WARN} {' and '.join(named)} at longform:{preset} leave the chart box {h_on:.0f} px of the "
                    f"{h_off:.0f} it has without them ({100 * (1 - h_on / h_off):.0f} % taken, over "
                    f"{100 * CHROME_ROOM_SHARE:.0f} %) - read the frame; drop one, or take a smaller preset (P71 T30, s106)")
    if kept:
        page["warnings"] = kept
    else:
        page.pop("warnings", None)
    return page


def apply_longform_states(page: dict, states: list) -> str | None:
    """REVIEW-P69-LANE-B-MERGE-2 N2: a longform page's `then=` states are drawn in ITS chart box, viewBox and preset,
    so each is stamped with the page's profile and preset and fitted its OWN end-tag form; and a dense-line page's
    viewBox makes room for the widest tag any line state writes (`axes.tag_room`, rendered px - written only when a
    state's tags are wider than the page's own, so a page whose states fit carries nothing new). In place. The
    refusal (a message) when a state cannot keep even its values on the stage, else None."""
    axes = page.get("axes") or {}
    preset = axes.get("type_scale") if axes.get("type_scale") in LONGFORM_PRESETS else LONGFORM_DEFAULT_PRESET
    t, room = LONGFORM_TYPE_SCALE[preset], 0.0
    for i, state in enumerate(states):
        if not isinstance(state, dict):
            continue
        if state.get("builder") == "dense-line" and longform_tag_form(state, preset) is None:
            return (f"then= state {i + 1} cannot keep even its end values inside the 16:9 stage at "
                    f"readability={LONGFORM}:{preset} (a value alone is the shortest end tag there is)")
        apply_longform(state, preset)   # REVIEW-P69-LANE-B-MERGE-3 M1: a state keeps ITS key - the names ITS tags gave up
        if state.get("builder") == "dense-line":
            room = max(room, longform_tag_px(state, t, state["axes"]["tag_form"]))
    if page.get("builder") == "dense-line" and room > longform_tag_px(page, t, axes.get("tag_form") or "full"):
        page["axes"]["tag_room"] = math.ceil(room * 10) / 10   # up to the tenth: the page's viewBox never grows past a state's fit
    elif page.get("builder") != "dense-line" and preset == "phone" and room > 0:
        page["axes"]["tag_room"] = math.ceil(room * 10) / 10   # P72 T12: a phone bars page's widened viewBox keeps a line state's tags on the stage
    # ... and every key stands in ONE band over the chart (the recast swaps the key, never the chart's box): the page
    # reserves the tallest - written only when a state's key needs more than the page's own, so every other page is
    # the page it was
    page["axes"].pop("key_w", None)
    page["axes"].pop("key_h", None)
    page["axes"].pop("state_ink", None)
    col = _longform_ink_col()[1]
    own_w, own_h = _longform_key_own(page, col)
    band = [(own_w, own_h)] + [_longform_key_own(s, col) for s in states if isinstance(s, dict)]
    band_w, band_h = max(b[0] for b in band), max(b[1] for b in band)
    if band_h > own_h + 1e-9:
        page["axes"]["key_w"] = math.ceil(band_w * 10) / 10
        page["axes"]["key_h"] = math.ceil(band_h * 10) / 10
    # ... and the key stands over EVERY chart's top ink, not only the page's own: a state that writes higher (a line's
    # plot over a bars page's, a y label) carries what it writes, so the band clears it (a keyed page only)
    if band_h > 0:
        own_ink = longform_state_ink(page)
        extra = [longform_state_ink(s) for s in states if isinstance(s, dict)]
        extra = [i for i in extra if i != own_ink]
        if extra:
            page["axes"]["state_ink"] = extra
    return None


def _longform_panel_scale(page: dict) -> float:
    """P69 T8b: the SMALLEST rendered scale (px per chart unit) a longform panels page draws a panel at in its home
    layout - the page's own estimated region (its ink, its key band) cut by the default layout. The end tags are fitted
    at it, so every panel's tags hold."""
    n = len(page.get(PANELS_KEY) or [])
    if not n:
        return longform_scale0()
    # P72 T47 (R26-366): the region the panels ARE drawn in - the floor cut (`_panels_region`, the engine's) - and, at
    # phone, the band a page the phone layout holds stands its plots under (0.888 px a unit was read on the two-era page
    # at phone where its panels drew at 0.771)
    fit = _panels_phone_fit(page)
    if fit is not None and fit["band"] is not None:
        return min(b[3] - fit["band"] for b in fit["homes"]) / LAND_VIEWBOX[1]
    boxes = _longform_full_boxes(page, *STAGE_PX["16:9"])
    region = _panels_region(page, boxes["chart"], "16:9", boxes.get("_floor"))
    return min(b[3] for b in panel_home_boxes(n, region)) / (LAND_VIEWBOX[1] + PANEL_SUB_U)


def longform_panel_tag_form(page: dict, panel: dict, preset: str, scale: float) -> str:
    """The fullest end-tag form whose widest tag fits a panel's OWN right margin (the line builder's 220 units, less
    its tag gap) at `scale`; `value` when none does - the name then rides the page's key (never a refusal)."""
    t, room = LONGFORM_TYPE_SCALE[preset], LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
    view = {"series": panel.get("series") or [], "badges": page.get("badges") or []}
    for form in LONGFORM_TAG_FORMS:
        if longform_tag_units(view, t, form, scale) <= room:
            return form
    return "value"


def longform_panel_key(page: dict) -> list[dict]:
    """The page's ONE key rail: every name a panel's end tag gave up, once - `[{"panel", "series", "name"}]` in panel
    order, a name and colour two panels share keyed by the first (E53 s8: one name, in one place)."""
    out, seen = [], set()
    for pi, panel in enumerate(page.get(PANELS_KEY) or []):
        if ((panel.get("axes") or {}).get("tag_form") or "full") == "full":
            continue
        for si, s in enumerate(panel.get("series") or []):
            if not isinstance(s, dict) or s.get("muted"):
                continue
            name = str(s.get("name") or "").strip()
            if not (name and str(s.get("label") or "").strip()) or (name, s.get("color")) in seen:
                continue
            seen.add((name, s.get("color")))
            out.append({"panel": pi, "series": si, "name": name})
    return out


def _apply_longform_panels(page: dict) -> dict:
    """The long form on a panels page: each panel's tag form at the page's home scale (fitted with no key, then again
    under the key those forms give up, which moves the region down), and the page's one key rail. In place."""
    axes = page["axes"]
    for key in ("key", "key_px", PANEL_BAND_KEY):   # P72 T47: the band is recomputed by every fit, never authored
        axes.pop(key, None)
    for _ in range(2):
        scale = _longform_panel_scale(page)
        for panel in page.get(PANELS_KEY) or []:
            if panel.get("builder") == PANEL_BARS:   # P69 T8d: a bars panel writes no end tags
                continue
            panel.setdefault("axes", {})["tag_form"] = longform_panel_tag_form(page, panel, axes["type_scale"], scale)
        key = longform_panel_key(page)
        axes.pop("key", None)
        axes.pop("key_px", None)
        if key:
            axes["key"] = key
            axes["key_px"] = longform_key_px(page)
    warns = [w for w in page.get("warnings") or [] if not str(w).startswith(FIT_WARN)]   # re-fitted: its own finding, once
    fit = longform_panels_fit_warning(page)
    if fit:
        warns.append(fit)
    phone = _panels_phone_fit(page)
    if phone is not None and phone["band"] is not None:   # P72 T47: the phone layout holds it - the engine draws the band
        axes[PANEL_BAND_KEY] = round(phone["band"], 3)
    if warns:
        page["warnings"] = warns
    else:
        page.pop("warnings", None)
    return page


# P72 T12 (R26-316; D1 keeps `phone`, E99 s106: a fit finding is advice) - A PANELS PAGE AT `longform:phone` IS WARNED,
# never refused, and renders as it does. Its words at 61.4 px leave the panels a small region under the page's own ink,
# and the panel is laid out for the middle preset: the WARN says the region it gets against the one it needs, and which
# of the five measured faults apply (P72 T12's frames), with their numbers. The build that makes it hold is its own slice.
# The NEED is one panel's own ink at the floor, stacked: its sub (a floor line, LONGFORM_LINE_H, over the y label's gap),
# two y ticks TICK_SPACE figures apart (E28: an axis states its scale) and its x labels' box under the plot.
FIT_WARN = "WARN fit:"
PANEL_SUB_K, PANEL_SUB_MAX = 1.15, 0.8   # the engine's LP_PANELS.SUB_K / SUB_MAX: a panel's sub, in ticks, capped by its band
LONGFORM_TICK_SPACE = 1.25               # the engine's LP_LONGFORM.TICK_SPACE: two y ticks this many figures apart
PANEL_LINE_TOP_U = 40.0                  # the line builder's plot top (LONGFORM_PLOT_T["dense-line"])
PANEL_BARS_TOP_U = 40.0                  # the engine's LPBAR_PANEL.TOP: a bars panel's plot top


def longform_panels_need_px(t: dict) -> float:
    """The height (rendered px) one panel needs at a preset: its sub, two y ticks, its x labels (see FIT_WARN)."""
    return (CARD_TYPE_PX * LONGFORM_LINE_H + LONGFORM_YLAB_GAP_PX + 2 * LONGFORM_TICK_SPACE * t["tick"]
            + (LONGFORM_ASCENT + LONGFORM_DESCENT) * t["tick"] + LONGFORM_XLAB_CLEAR_PX)


def _panel_faults(page: dict, t: dict, boxes: list) -> list[str]:
    """The five faults a panels page shows at `phone`, each named with its number, for every panel it applies to."""
    out, subs, bars, ticks, xlab, rules = [], [], [], [], [], []
    for i, (panel, b) in enumerate(zip(page.get(PANELS_KEY) or [], boxes)):
        s = b[3] / (LAND_VIEWBOX[1] + PANEL_SUB_U)   # rendered px per unit in its home box
        g = longform_geom(t, 0.0, LAND_VIEWBOX[1] * s, LAND_VIEWBOX[1] * s)
        axes = panel.get("axes") or {}
        lo, hi = (list(axes.get("domain") or [0.0, 1.0]) + [1.0])[:2]
        span = (float(hi) - float(lo)) or 1.0
        if str(panel.get("sub") or "").strip():
            subs.append(min(PANEL_SUB_K * t["tick"], PANEL_SUB_MAX * PANEL_SUB_U * s))
        if panel.get("builder") == PANEL_BARS:
            plot = (g["bars_b"] - PANEL_BARS_TOP_U) * s
            vals = [abs(float(v)) for v in panel.get("values") or [] if isinstance(v, (int, float))]
            if vals and max(vals) / span * plot < t["tick"]:
                bars.append((i, max(vals) / span * plot))
            continue
        plot = (g["line_b"] - PANEL_LINE_TOP_U) * s
        if plot < 2 * LONGFORM_TICK_SPACE * t["tick"]:
            ticks.append((i, plot))
        labels = [str(x[1]) for x in axes.get("xticks") or [] if isinstance(x, (list, tuple)) and len(x) == 2]
        width = (b[2] / s - g["plot_l"] - LAND_PLOT["R"] * LAND_VIEWBOX[0]) * s
        need = sum(longform_text_px(x, "sub", t["tick"]) for x in labels) + 0.3 * t["tick"] * max(0, len(labels) - 1)
        if labels and need > width:
            xlab.append((i, need, width))
        ys = sorted(float(h["y"]) for h in axes.get("hlines") or [] if isinstance(h, dict) and h.get("label"))
        if any((y2 - y1) / span * plot < (LONGFORM_ASCENT + LONGFORM_DESCENT) * t["tag"] for y1, y2 in zip(ys, ys[1:])):
            rules.append(i)
    if subs and min(subs) < CARD_TYPE_PX:
        out.append(f"the panel subs at {min(subs):.1f} px (floor {CARD_TYPE_PX:.2f})")
    for i, plot in ticks:
        out.append(f"panel {i}'s plot {plot:.0f} px - under two y ticks' {2 * LONGFORM_TICK_SPACE * t['tick']:.0f}")
    for i, need, width in xlab:
        out.append(f"panel {i}'s x labels overprint ({need:.0f} px of labels on a {width:.0f} px plot)")
    if rules:
        out.append("the rule names overprint on panel" + ("s " if len(rules) > 1 else " ") + ", ".join(map(str, rules)))
    for i, h in bars:
        out.append(f"panel {i}'s bars at most {h:.1f} px tall")
    return out


def longform_panels_fit_warning(page: dict) -> str | None:
    """P72 T12 (R26-316): the FIT_WARN a panels page at `longform:phone` carries - the region its panels get against the
    height one needs, and the faults that apply - or None (every other preset, a page that holds as drawn, and - P72
    T47 - a page the phone layout holds: it is drawn in that layout, `axes.panel_band_px`)."""
    fit = _panels_phone_fit(page)
    if fit is None or fit["band"] is not None or not fit["phone_faults"]:
        return None
    region, need, faults = fit["region"], fit["need"], fit["faults"]
    return (f"{FIT_WARN} a panels page at readability={LONGFORM}:phone gets a {region[3]:.0f} px region and a panel needs "
            f"~{need:.0f} px (its sub at the floor, two y ticks, its x labels)" + (": " + "; ".join(faults) if faults else "")
            + " - it renders as drawn (E99 s106: advice; P72 T47's phone layout - the subs at the floor, the rule names"
            " laddered, two y ticks - does not hold it: " + "; ".join(fit["phone_faults"]) + ")")


# P72 T47 (R26-366, R26-316's build half) - THE PANELS PAGE AT `longform:phone`, BUILT, where the arithmetic allows.
# T12's WARN measured five faults of the MIDDLE preset's panel layout drawn at phone. The phone layout, for a page whose
# as-drawn layout T12 warns: every panel's plot stands under a BAND (rendered px) of
#   - its SUB at the floor (CARD_TYPE_PX, 59.08) - the band's first CARD_TYPE_PX / PANEL_SUB_MAX (the sub's own law), and
#   - its RULE NAMES laddered under it, one line each at the floor, LONGFORM_LINE_H apart, highest rule first, in the
#     rule's ink and right-aligned in the panel (at the plot's right end when every name on the panel fits there, else at
#     its right edge less LONGFORM_EDGE_PX): two rules 1 % apart cannot each carry a 60 px name at its own rule;
# the band is the page's (the most names any line panel carries), so every panel keeps one plot and one scale. Its y
# axis steps at the finest nice step (<= 5 divisions) whose TWO ticks stand LONGFORM_TICK_SPACE figures apart (E28), its
# x labels thin by the card's rule (both ends kept). The page HOLDS when every line panel writes those two ticks, every rule name
# fits its panel and every bars panel's tallest bar stands a tick figure tall; then `_apply_longform_panels` stamps the
# band as `axes.panel_band_px` and the engine draws it (lpBuildPanel, `longform:phone` only). A page it does not hold
# keeps its WARN, whose tail names why (four panels in two rows; the companion's 210 px), and is drawn as it was.
PANEL_BAND_KEY = "panel_band_px"   # axes: the phone band (rendered px), the compiler's - recomputed by every fit, never authored


def _panel_nice_step(x: float) -> float:
    """The engine's lpNiceStep: 1, 2, 5 or 10 times a power of ten, at least `x`."""
    e = 10 ** math.floor(math.log10(x))
    f = x / e
    return e * (1 if f <= 1 else 2 if f <= 2 else 5 if f <= 5 else 10)


def longform_phone_divs(plot_px: float, lo: float, hi: float, tick_px: float) -> int | None:
    """The divisions a phone panel's y axis is drawn in (the engine's lpPhoneDivs, line for line): the most, at most 5,
    whose nice step writes two ticks or more inside [lo, hi] at least LONGFORM_TICK_SPACE tick figures apart on a plot
    `plot_px` tall - or None (no two ticks fit: the axis cannot state its scale, E28)."""
    span = hi - lo
    if not (plot_px > 0 and span > 0 and tick_px > 0):
        return None
    for d in range(5, 0, -1):
        step = _panel_nice_step(max(1e-9, span / d))
        n, tv = 0, math.ceil(lo / step - 1e-9) * step
        while tv <= hi + 1e-9:
            n, tv = n + 1, tv + step
        if n >= 2 and step / span * plot_px >= LONGFORM_TICK_SPACE * tick_px:
            return d
    return None


def _finite(v) -> bool:
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def _panel_y_range(page: dict, panel: dict) -> tuple[float, float]:
    """A line panel's y range as the line builder sets it (buildLedgerLine: the data and the rules, padded 6 %, from zero
    if asked, then the domain - the page's shared one unless the panel is independent - over both)."""
    axes = dict(panel.get("axes") or {})
    page_dom = (page.get("axes") or {}).get("domain")
    if isinstance(page_dom, list) and not panel.get("independent"):
        axes["domain"] = page_dom
    f = (lambda v: math.log10(v)) if axes.get("log") else (lambda v: v)   # noqa: E731
    vals = [f(float(v)) for sr in panel.get("series") or [] if isinstance(sr, dict) for _x, v in sr.get("pts") or []]
    vals += [f(float(h["y"])) for h in axes.get("hlines") or [] if isinstance(h, dict) and _finite(h.get("y"))]
    lo, hi = (min(vals), max(vals)) if vals else (0.0, 1.0)
    pad = (hi - lo) * 0.06 or 1.0
    lo, hi = lo - pad, hi + pad
    if axes.get("from_zero") and not axes.get("log"):
        lo = 0.0
    dom = axes.get("domain")
    if isinstance(dom, list):
        if len(dom) > 0 and dom[0] is not None and _finite(dom[0]):
            lo = f(float(dom[0]))
        if len(dom) > 1 and dom[1] is not None and _finite(dom[1]):
            hi = f(float(dom[1]))
    return lo, hi


def _panel_rule_names(panel: dict) -> list[str]:
    """A panel's labelled rules' names, highest rule first (the ladder's order)."""
    rules = [h for h in (panel.get("axes") or {}).get("hlines") or [] if isinstance(h, dict) and _finite(h.get("y"))
             and str(h.get("label") or "").strip()]
    return [str(h["label"]) for h in sorted(rules, key=lambda h: -float(h["y"]))]


def longform_panels_phone_band(page: dict) -> float:
    """The phone band (rendered px) every panel's plot stands under: the sub at the floor, then the page's longest
    ladder of rule names, one floor line each."""
    rows = max([len(_panel_rule_names(p)) for p in page.get(PANELS_KEY) or [] if p.get("builder") != PANEL_BARS] or [0])
    return CARD_TYPE_PX / PANEL_SUB_MAX + rows * LONGFORM_LINE_H * CARD_TYPE_PX


def _panel_phone_faults(page: dict, t: dict, boxes: list, band: float) -> list[str]:
    """What the phone layout cannot hold on each panel (none: the page holds)."""
    out = []
    for i, (panel, b) in enumerate(zip(page.get(PANELS_KEY) or [], boxes)):
        u = (b[3] - band) / LAND_VIEWBOX[1]
        if u <= 0:
            out.append(f"panel {i} has no plot under its {band:.0f} px band ({b[3]:.0f} px box)")
            continue
        g = longform_geom(t, 0.0, LAND_VIEWBOX[1] * u, LAND_VIEWBOX[1] * u)
        if panel.get("builder") == PANEL_BARS:
            plot = max(0.0, (g["bars_b"] - PANEL_BARS_TOP_U) * u)
            lo, hi = (list((panel.get("axes") or {}).get("domain") or [0.0, 1.0]) + [1.0])[:2]
            span = (float(hi) - float(lo)) or 1.0
            vals = [abs(float(v)) for v in panel.get("values") or [] if isinstance(v, (int, float))]
            if vals and plot <= 0:
                out.append(f"panel {i}'s bars get no plot under the band")
            elif vals and max(vals) / span * plot < t["tick"]:
                out.append(f"panel {i}'s bars at most {max(vals) / span * plot:.1f} px tall")
            continue
        plot = max(0.0, (g["line_b"] - PANEL_LINE_TOP_U) * u)
        if longform_phone_divs(plot, *_panel_y_range(page, panel), t["tick"]) is None:
            out.append(f"panel {i} writes no two y ticks {LONGFORM_TICK_SPACE * t['tick']:.0f} px apart on its "
                       f"{plot:.0f} px plot")
        for name in _panel_rule_names(panel):
            w = longform_text_px(name, "title", CARD_TYPE_PX)
            if w > b[2] - LONGFORM_EDGE_PX:
                out.append(f"panel {i}'s rule name '{name}' is wider than its panel ({w:.0f} px on {b[2]:.0f})")
    return out


def _panels_phone_fit(page: dict) -> dict | None:
    """A panels page at `longform:phone`: its region and home boxes, T12's need and the faults of the layout as drawn,
    and - when T12 warns it - the phone layout's band if it holds (`band`) or what it cannot hold (`phone_faults`).
    None on every other page and preset."""
    if page.get("builder") != PANELS or longform_preset(page) != "phone" or not page.get(PANELS_KEY):
        return None
    t, boxes = longform_type(page), _longform_full_boxes(page, *STAGE_PX["16:9"])
    region = _panels_region(page, boxes["chart"], "16:9", boxes.get("_floor"))
    homes = panel_home_boxes(len(page[PANELS_KEY]), region)
    need, faults = longform_panels_need_px(t), _panel_faults(page, t, homes)
    out = {"region": region, "homes": homes, "need": need, "faults": faults, "band": None, "phone_faults": []}
    if region[3] >= need and not faults:
        return out   # it holds as drawn: no WARN, no band
    band = longform_panels_phone_band(page)
    out["phone_faults"] = _panel_phone_faults(page, t, homes, band)
    if not out["phone_faults"]:
        out["band"] = band
    return out


def longform_panel_right_u(page: dict, panel: dict, scale: float) -> float:
    """A phone panel's right margin (units at `scale`): the builder's 220, or its widest end tag's gap, tag and edge air
    when those are wider (the engine's lpPanelTagR)."""
    view = {"series": panel.get("series") or [], "badges": page.get("badges") or []}
    form = (panel.get("axes") or {}).get("tag_form") or "full"
    return max(LAND_PLOT["R"] * LAND_VIEWBOX[0], LAND_TAG_GAP + longform_tag_units(view, longform_type(page), form, scale)
               + LONGFORM_EDGE_PX / scale)


def panel_band(spec: dict) -> float:
    """The phone band a page is drawn under (`axes.panel_band_px` at `longform:phone`), or 0 - the engine's own read."""
    v = (spec.get("axes") or {}).get(PANEL_BAND_KEY)
    return float(v) if (spec.get("builder") == PANELS and longform_preset(spec) == "phone" and _finite(v)
                        and float(v) > 0) else 0.0


def _longform_place(y: float, h: float) -> float:
    """Where an item `h` tall that would stand at `y` does stand: at `y`, or under the caption strip's foot if it
    would meet the strip (N1)."""
    return LONGFORM_STRIP[1] if h > 0 and y + h > LONGFORM_STRIP[0] and y < LONGFORM_STRIP[1] else y


def longform_stack(bot: float, src_h: float, rail_h: float, h_s: int = 1080) -> dict:
    """The source's and the key rail's tops under a chart whose foot is `bot` (rendered px), and whether both stay on
    the stage: the engine's `lpLongformStack`, line for line (N1)."""
    g_src, g_rail = LAND_SRC_GAP * PUNCH_SCALE * h_s, LAND_RAIL_GAP * PUNCH_SCALE * h_s
    src_y = _longform_place(bot + g_src, src_h)
    rail_y = _longform_place(max(bot + g_rail, src_y + src_h + LONGFORM_STACK_GAP_PX if src_h > 0 else bot + g_rail), rail_h)
    end = max(src_y + src_h if src_h > 0 else 0.0, rail_y + rail_h if rail_h > 0 else 0.0)
    first = src_y if src_h > 0 else rail_y if rail_h > 0 else float(h_s)
    return {"bot": bot, "src_y": src_y, "rail_y": rail_y, "floor": min(float(LONGFORM_STRIP[0]), first),
            "fits": end <= h_s - LONGFORM_EDGE_PX}


def longform_chart_box(spec: dict, t: dict, sub_bottom: float, src_h: float, rail_h: float = 0.0,
                       h_s: int = 1080, key_h: float = 0.0) -> dict:
    """The longform chart box in rendered px - `top`, `bot` - and what stands under it (`src_y`, `rail_y`, the `floor`
    its ticks clear): the engine's `lpLongformBox`, line for line. The foot is the full-stage box's, raised (N1) to the
    first of: the source standing above the caption strip, then the source and the rail both above it. P69 T10: a key
    `key_h` tall stands in the top band (`key_y`), M28's air under the sub and over the chart's top ink - the chart
    moves down to make that room, never the key onto the sub."""
    top0, bot0 = LAND_FULL["Y"] * h_s, (LAND_FULL["Y"] + LAND_FULL["H"]) * h_s
    g_src, g_rail = LAND_SRC_GAP * PUNCH_SCALE * h_s, LAND_RAIL_GAP * PUNCH_SCALE * h_s
    cands = (bot0, LONGFORM_STRIP[0] - g_src - src_h,
             LONGFORM_STRIP[0] - rail_h - max(g_rail, g_src + src_h + LONGFORM_STACK_GAP_PX))
    stack: dict = {}
    for cand in cands:
        stack = longform_stack(min(bot0, cand), src_h, rail_h, h_s)
        if stack["fits"]:
            break
    bot = stack["bot"]
    tu, vh = LONGFORM_PLOT_T.get(str(spec.get("builder")), LONGFORM_PLOT_T["story"]), LAND_VIEWBOX[1]
    axes = spec.get("axes") or {}
    band = key_h + 0.5 * t["tick"] if key_h > 0 else 0.0   # P69 T10: the key and M28's air under it
    base = sub_bottom + 0.5 * t["tick"] + band
    # REVIEW-P69-LANE-B-MERGE-3 M1: every chart the page can become stands in this box, each with its OWN plot top and
    # the ink above it (`axes.state_ink`) - the box clears the highest of them, and the key stands over that one
    reach = _longform_reaches(spec, t)
    top = max([top0] + [(base + above - tu_i * bot / vh) / (1 - tu_i / vh) for tu_i, above in reach])
    key_y = top + min(tu_i * (bot - top) / vh - above for tu_i, above in reach) - 0.5 * t["tick"] - key_h
    return dict(stack, top=top, key_y=key_y)


def _longform_above(t: dict, ylabel: bool, rules: bool) -> float:
    """The ink a chart carries above its plot top, rendered px: half a tick, the y label's row, a rule's name."""
    return max(0.5 * t["tick"], LONGFORM_YLAB_GAP_PX + t["tick"] if ylabel else 0.0,   # a label's box
               8 + 1.25 * t["tag"] if rules else 0.0)                                    # reaches ~1 em up


def longform_state_ink(spec: dict) -> dict:
    """What moves a chart's top ink: its builder's plot top (viewBox units) and whether it writes a y label or a named
    rule above the plot. The shape `axes.state_ink` carries per `then=` state (M1)."""
    axes = spec.get("axes") or {}
    if spec.get("builder") == PANELS:   # P69 T8b: the region's top is the panels' own - their y labels and rules are inside their boxes
        return {"tu": LONGFORM_PLOT_T[PANELS], "ylabel": False, "rules": False}
    rules = any(isinstance(h, dict) and h.get("label") for h in (axes.get("hlines") or ([axes["hline"]] if axes.get("hline") else [])))
    return {"tu": float(LONGFORM_PLOT_T.get(str(spec.get("builder")), LONGFORM_PLOT_T["story"])),
            "ylabel": bool(axes.get("ylabel")), "rules": rules}


def _longform_reaches(spec: dict, t: dict) -> list[tuple[float, float]]:
    """(plot top in viewBox units, ink above it in rendered px) for the page and each state it names."""
    own = longform_state_ink(spec)
    inks = [own] + [s for s in ((spec.get("axes") or {}).get("state_ink") or []) if isinstance(s, dict)]
    return [(float(i["tu"]), _longform_above(t, bool(i.get("ylabel")), bool(i.get("rules")))) for i in inks]


def longform_text_px(text: str, role: str, px: float) -> float:
    """The rendered width of `text` in a longform page role (`title` | `sub` | `source`) set at `px` rendered: its
    glyphs' Inter advances at the role's weight and at the opsz the browser picks (the CSS size, px / the punch)."""
    weight = LONGFORM_WEIGHT[role]
    lo, hi = LONGFORM_ADVANCES[(weight, 14)], LONGFORM_ADVANCES[(weight, 32)]
    k = (min(LONGFORM_OPSZ[1], max(LONGFORM_OPSZ[0], px / PUNCH_SCALE)) - LONGFORM_OPSZ[0]) / (LONGFORM_OPSZ[1] - LONGFORM_OPSZ[0])
    mean = (sum(lo) + (sum(hi) - sum(lo)) * k) / len(lo)
    units = 0.0
    for ch in str(text):
        i = LONGFORM_ADV_CHARS.find(ch)
        units += mean if i < 0 else lo[i] + (hi[i] - lo[i]) * k
    return units * px / LONGFORM_ADV_UPM


def longform_lines(text: str, role: str, px: float, box_w: float) -> int:
    """The lines a longform page role writes `text` in, `box_w` px wide: the browser's greedy break at the spaces
    between words (a word is one unbreakable run - `lpGlyphsWrap`), measured at the face's own advances."""
    words = str(text or "").split()
    if not words:
        return 0
    space = longform_text_px(" ", role, px)
    lines, run = 1, 0.0
    for word in words:
        want = longform_text_px(word, role, px)
        if run and run + space + want > box_w + 0.5:
            lines, run = lines + 1, want
        else:
            run = run + space + want if run else want
    return lines


def _longform_rail_h(spec: dict) -> float:
    n = len([b for b in spec.get("badges") or [] if isinstance(b, dict) and not b.get("inline")])
    rows = -(-n // LONGFORM_PILLS_PER_ROW)
    return rows * LONGFORM_PILL_PX + max(0, rows - 1) * LONGFORM_PILL_GAP_PX


def _longform_ink_col(w_s: int = 1920) -> tuple[float, float]:
    """The longform page's ink column in rendered px: its left edge (the title's) and its width (to the stage's safe
    right edge) - the column the title, sub and source wrap in and the key rail's row fills."""
    bx, by, bw, _bh = LAND_BOARD
    vx = bx + bw / 2 - 0.5 / PUNCH_SCALE
    ink_x = _punch_pt(max(bx + 0.027, vx + 0.03)) * w_s
    return ink_x, LAND_PHONE_SAFE_RIGHT * w_s - ink_x


# P70 T9 (was P69 T61, A34; the parent's ruling 2026-09-25, option A) - A PAGE MAKES ROOM FOR ITS ACT. Bravos's
# chapter pill stands where our long-form page writes its title (BUB 12:35: the pill 84-121 px, the title from 137), so
# a long-form page inside a chapter's window carries `chapter_room` - the whole CSS px its title moves DOWN (the pill's
# height and Bravos's 16 px under it; the compiler's `chapter_room_css`) - and the sub, the key, the chart and the
# stack under it follow, exactly as the engine lays them out off the title's own box. A page without the key is the
# page it always was.
CHAPTER_ROOM_KEY = "chapter_room"


def _longform_title_frac() -> float:
    """The long-form title's top as the engine writes it (a CSS stage fraction, toFixed(2) %)."""
    bx, by, bw, bh = LAND_BOARD
    vy = by + bh / 2 - 0.5 / PUNCH_SCALE
    return round(max(by + 0.024, vy + 0.035) * 100, 2) / 100


def longform_ink_origin(w_s: int = 1920, h_s: int = 1080) -> tuple[float, float]:
    """The long-form page's INK ORIGIN in rendered stage px: its column's left edge and its title's top as laid out
    with no room - where a chapter pill stands (P70 T9)."""
    return _longform_ink_col(w_s)[0], _punch_pt(_longform_title_frac()) * h_s


def _longform_full_boxes(spec: dict, w_s: int, h_s: int) -> dict:
    """A longform page's boxes, ESTIMATED the way the engine lays it out (the fixture measures and outranks it; N3:
    held to the engine's own boxes at every preset by `test_longform_profile` and `test_page_boxes`)."""
    t, dense = longform_type(spec), spec.get("builder") == "dense-line"
    ink_x = _longform_ink_col(w_s)[0]
    title_frac = _longform_title_frac()   # the engine writes the title's top toFixed(2) %
    room = int(spec.get(CHAPTER_ROOM_KEY) or 0)   # P70 T9: the whole CSS px the title moves down for a chapter pill
    title_y = _punch_pt(title_frac) * h_s + room * PUNCH_SCALE   # a room of 0 adds 0.0: the page it always was, to the bit
    ink_w = LAND_PHONE_SAFE_RIGHT * w_s - ink_x
    # P71 T30: the title's capsule pads its box (CSS px, ems of the title's own size) and outdents it by its side pad, so
    # its words keep the column's left and its right edge stays inside the safe column; a page naming none pads 0
    cap = spec.get(TITLE_STYLE_KEY) == "capsule"
    pad_v, pad_h = ((round(TITLE_CAPSULE_EM[k] * round(t["title"] / PUNCH_SCALE, 3), 3) if cap else 0.0)
                    for k in ("pad_v", "pad_h"))
    wrap_w = {"title": ink_w - pad_h * PUNCH_SCALE, "sub": ink_w, "source": ink_w}
    # the engine lays the ink out in the page's own CSS px and READS it back whole (offsetTop / offsetHeight), so the
    # layout's heights are snapped to whole CSS px here too; the boxes report the ink's own (unsnapped) extent
    lines = {role: (max(1, longform_lines(spec.get(key), role, t[size], wrap_w[role])) if str(spec.get(key) or "").strip() else 0)
             for role, key, size in (("title", "title", "title"), ("sub", "sub", "sub"), ("source", "source", "src"))}
    if _source_lines_ok(spec.get(SOURCE_LINES_KEY)):   # P71 T30: two lines written as two, each wrapping in the column
        lines["source"] = sum(max(1, longform_lines(ln, "source", t["src"], ink_w)) for ln in spec[SOURCE_LINES_KEY])
    css_h = {role: lines[role] * round(t[size] / PUNCH_SCALE, 3) * LONGFORM_LINE_H
             for role, size in (("title", "title"), ("sub", "sub"), ("source", "src"))}
    css_h["title"] += 2 * pad_v
    whole = lambda v: math.floor(v + 0.5)  # noqa: E731
    rend = lambda css_y: h_s / 2 + (css_y - h_s / 2) * PUNCH_SCALE  # noqa: E731
    title_top = whole(title_frac * h_s) + room
    sub_top = title_top + whole(css_h["title"]) + LONGFORM_SUB_GAP
    title_h, sub_h, src_h = (css_h[r] * PUNCH_SCALE for r in ("title", "sub", "source"))
    sub_y = rend(sub_top)
    sub_bottom = rend(sub_top + whole(css_h["sub"])) if lines["sub"] else rend(title_top + whole(css_h["title"]))
    rail_h = _longform_rail_h(spec)
    key_w, key_h = longform_key_box(spec, ink_w)   # P69 T10: the key rail, measured by the engine off its whole CSS px
    key_h = whole(key_h / PUNCH_SCALE) * PUNCH_SCALE
    box = longform_chart_box(spec, t, sub_bottom, whole(css_h["source"]) * PUNCH_SCALE,
                             whole(rail_h / PUNCH_SCALE) * PUNCH_SCALE, h_s, key_h)
    top, bot = box["top"], box["bot"]
    g = longform_geom(t, top, bot, box["floor"])
    s, cx, tu = g["scale"], LAND_FULL["X"] * w_s, LONGFORM_PLOT_T["dense-line" if dense else "story"]
    if dense:
        tags_u = longform_tag_units(spec, t, (spec.get("axes") or {}).get("tag_form") or "full", s)
        vw, left, right = longform_page_vw(spec, s, w_s), g["plot_l"], LAND_PLOT["R"] * LAND_VIEWBOX[0]
        floor, foot = g["line_b"], g["line_b"] + g["xtick_dy"] + LONGFORM_DESCENT * g["tick"]
    else:   # the bars page's plot is its PANEL (the tick rules' own extent, x0 - 20 to x1 + 20) over its names
        tags_u, vw, right = 0.0, longform_bars_vw(spec, s, w_s), 0.0
        left = max(g["gutter"], float((spec.get("axes") or {}).get("left_gutter") or 0)) - 20
        floor, foot = g["bars_b"], g["bars_b"] + g["xlab_dy"] + 1.4 * g["tick"]
    ylab = LONGFORM_YLAB_GAP_PX + LONGFORM_ASCENT * t["tick"] if (spec.get("axes") or {}).get("ylabel") else 0.0
    out = {
        "title": _box(ink_x - pad_h * PUNCH_SCALE, title_y, ink_w + pad_h * PUNCH_SCALE, title_h),   # P71 T30: a capsule's outdent
        "sub": _box(ink_x, sub_y, ink_w, sub_h),
        "chart": _box(cx, top, vw * s, bot - top),
        "plot": _box(cx + left * s, top + tu * s - ylab, (vw - left - right) * s, (foot - tu) * s + ylab),
        "source": _box(ink_x, box["src_y"], ink_w, src_h),
        "rail": _box(ink_x, box["rail_y"], ink_w, rail_h),
        "tags": _box(cx + (vw - LAND_PLOT["R"] * LAND_VIEWBOX[0] + LAND_TAG_GAP) * s, top + tu * s, tags_u * s, (floor - tu) * s),
    }
    if key_h > 0:
        out[KEY_BOX] = _box(ink_x, box["key_y"], key_w, key_h)
    if spec.get("builder") == PANELS:   # P69 T8b: the floor its panels stop over (page_boxes pops it)
        out["_floor"] = box["floor"]
    return out

def _readability_profile(spec: dict) -> str | None:
    """The page-scoped profile carried by the dense page's axes, if any."""
    value = (spec.get("axes") or {}).get("readability")
    return value if value in READABILITY_PROFILES else None


def _profile_tag_units(spec: dict, profile: str | None = None) -> float:
    """Inline end-tag width in the profile's chart user units.

    ``spec`` may be the normalized page or the source series passed through validation. The
    profile is only called for a dense-line page; an absent builder on source is therefore valid.
    """
    if profile != "landscape-phone":
        return tag_units(spec)
    builder = spec.get("builder")
    if builder is not None and str(builder) not in LAND_TAG_BUILDERS:
        return 0.0
    raw = spec.get("series") or []
    if not isinstance(raw, list):
        return 0.0
    rides = {BADGE_ACCENT_COL.get(str(b.get("accent"))): str(b.get("tag") or "")
             for b in spec.get("badges") or [] if isinstance(b, dict) and b.get("inline")}
    out = 0.0
    for s in raw:
        if not isinstance(s, dict) or s.get("muted"):
            continue
        tag = rides.get(str(s.get("color")), "")
        name = ((s.get("label") or "") + " " + (s.get("name") or "")).strip()
        out = max(out, len(name) * LAND_PHONE_NAME_U
                  + ((len(tag) + 1) * LAND_PHONE_BADGE_U if tag else 0.0))
    return out


def _readability_fit_error(series: dict) -> str | None:
    """Refuse a profile whose enlarged end tags cannot fit without stage clipping."""
    value = series.get("readability") or (series.get("axes") or {}).get("readability")
    if value != "landscape-phone":
        return None
    stage_w, stage_h = STAGE_PX["16:9"]
    scale = LAND_FULL["H"] * stage_h / LAND_PHONE_VIEWBOX_H
    max_vw = ((LAND_PHONE_SAFE_RIGHT * stage_w - LAND_FULL["X"] * stage_w) / scale
              + LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
              - _profile_tag_units(series, "landscape-phone"))
    if max_vw < LAND_PHONE_MIN_VIEWBOX_W:
        return ("readability='landscape-phone' cannot fit its enlarged inline end tags inside the "
                f"16:9 stage (maximum viewBox width {max_vw:.1f} < {LAND_PHONE_MIN_VIEWBOX_W})")
    return None


def _landscape_profile_geometry(spec: dict, w_s: int, h_s: int) -> dict | None:
    """Return the rendered chart/viewBox geometry for T17, or None for legacy geometry."""
    if _readability_profile(spec) != "landscape-phone" or not full_stage(spec, "16:9"):
        return None
    cx, cy = LAND_FULL["X"] * w_s, LAND_FULL["Y"] * h_s
    ch = LAND_FULL["H"] * h_s
    scale = ch / LAND_PHONE_VIEWBOX_H
    max_vw = ((LAND_PHONE_SAFE_RIGHT * w_s - cx) / scale
              + LAND_PLOT["R"] * LAND_VIEWBOX[0] - LAND_TAG_GAP
              - _profile_tag_units(spec, "landscape-phone"))
    vw = max(LAND_PHONE_MIN_VIEWBOX_W, round(max_vw, 3))
    return {"vw": vw, "vh": LAND_PHONE_VIEWBOX_H, "scale": scale, "B": LAND_PHONE_B / LAND_PHONE_VIEWBOX_H,
            "x": cx, "y": cy, "w": vw * scale, "h": ch,
            "tag_units": _profile_tag_units(spec, "landscape-phone")}


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


# ---- P69 T8b: WHERE THE PANELS STAND - the layout law, and the focus states that move it ----------------------------
# E99 s104 amended again: "focus is a COMPOSABLE state, not a fixed mode". A FOCUS STATE names (a) a LAYOUT - `row`
# (side by side), `stack`, `quad` (a 2 x 2 grid: two active take a row, one takes the page) or `free` (a box per panel,
# stage fractions) - laid over the ACTIVE panels, and (b) per panel a ROLE: `active` (sharp, full ink, its species
# live), `receded` (at its HOME box, scaled back, dimmed and blurred behind the active ones - each a dial with a
# default, PANEL_RECEDE), or `hidden`. The page's HOME is its default layout with every panel active; a change of
# state on a word is ONE transition - every panel's box, ink and blur on the transition's own clock (the engine's
# `lpPanelPoses`). Every panel keeps its own viewBox's aspect in every box (the fit is `meet`, centred - the chart is
# the same chart at another size, never a stretched one), and a layout is packed to the region's left edge and centred
# on its height, so ONE active panel stands exactly where a single-chart page's chart stands (the resize from a
# standing chart into its slot is a move between two boxes of that one aspect). This is the engine's law, mirrored.
PANEL_LAYOUTS = ("row", "stack", "quad", "free")
PANEL_ROLES = ("active", "receded", "hidden")
PANEL_RECEDE = {"scale": 0.86, "dim": 0.55, "blur": 5.0}   # the engine's LP_PANELS.RECEDE: scale-back about the home box's
# centre, the share of the panel's ink taken away, and the depth-of-field blur in stage px (the blur-zoom's own backdrop
# blur is 18 px - a rack focus keeps the receded chart READABLE as a chart, only soft) [DERIVED: the rack-focus frames]
PANEL_RECEDE_BOUNDS = {"scale": (0.3, 1.0), "dim": (0.0, 0.95), "blur": (0.0, 24.0)}
PANEL_GAP = 0.03   # the gutter between two cells, a share of the region's WIDTH, both ways (the card's 44 of 1056 units)
PANELS_KEY = "panels"   # page_boxes' per-panel boxes (a panels page only)
# a landscape panel's SUB BAND: its viewBox reaches this many units ABOVE the line builder's own 0 (the builder keeps 40
# over its plot - a y label's row, never a title's), so the panel's sub stands inside its own box at any size
PANEL_SUB_U = 56.0
PANEL_FLOOR_AIR = 6.0   # rendered px a full-stage panels region stops over its FLOOR (a panel's x ticks are inside its box)
PANEL_BARS_PLOT = {"L": 40.0, "TB": (90.0, 440.0)}   # P69 T8d: a bars panel's plot in its units - buildLedgerBars' gutter 60
# less its 20-unit rule overhang, its top and floor; its right edge the viewBox's (a bars panel runs x1 = W - 20, + 20)


def default_panel_layout(n: int, aspect: str = "16:9") -> str:
    """The page's HOME layout: stacked on a 9:16 stage, a quad for four on 16:9, else side by side."""
    if aspect == "9:16":
        return "stack"
    return "quad" if n >= 4 else "row"


def panel_grid(layout: str, k: int) -> tuple[int, int]:
    """(columns, rows) of `layout` for `k` panels: a quad's two take a row and its one takes the page."""
    return ((1, k) if layout == "stack" else (2, 2) if layout == "quad" and k >= 3
            else (2, 1) if layout == "quad" and k == 2 else (k, 1))


def panel_cells(layout: str, k: int, region: tuple) -> list[tuple]:
    """`k` cells of `layout` over `region` (x, y, w, h), in reading order."""
    x, y, w, h = region
    if k <= 0:
        return []
    cols, rows = panel_grid(layout, k)
    g = PANEL_GAP * w
    cw, ch = (w - g * (cols - 1)) / cols, (h - g * (rows - 1)) / rows
    return [(x + (i % cols) * (cw + g), y + (i // cols) * (ch + g), cw, ch) for i in range(k)]


def panel_fit(cell: tuple, aspect: float, fill: bool = True) -> tuple:
    """A panel's box inside `cell`, centred. P69 T8c: a landscape panel (`fill`) takes the cell's WHOLE WIDTH - the line
    builder re-lays its plot out at any viewBox width - and the cell's height, or the aspect's when the cell is taller
    (its plot is a fixed height). `fill=False` is T8b's: the largest box of `aspect` (w / h), the svg's own `meet`."""
    x, y, w, h = cell
    if fill:
        fh = min(h, w / aspect)
        return (x, y + (h - fh) / 2, w, fh)
    fw, fh = (h * aspect, h) if w / h > aspect else (w, w / aspect)
    return (x + (w - fw) / 2, y + (h - fh) / 2, fw, fh)


def panel_layout(layout: str, k: int, region: tuple, aspect: float, fill: bool = True) -> list[tuple]:
    """`k` panel boxes laid out as `layout` in `region`: ONE box size for the grid, hung from the region's TOP (the page
    reads title, sub, charts). P69 T8c (`fill`, every landscape page): a box is its CELL's full width - a lone panel
    spans the whole region, as a single-chart page's chart does - and its cell's height, or `aspect`'s when the cell is
    taller (the line builder's landscape plot is a fixed height; a quad panel growing to the page keeps T8b's box).
    `fill=False` (portrait) is T8b's law: boxes of `aspect`, the largest the tighter axis allows, a group centred
    across the region and a lone panel on its left edge. Pure."""
    if k <= 0:
        return []
    x, y, w, h = region
    cols, rows = panel_grid(layout, k)
    g = PANEL_GAP * w
    if fill:
        cw, ch = (w - g * (cols - 1)) / cols, (h - g * (rows - 1)) / rows
        bh = min(ch, cw / aspect)
        return [(x + (i % cols) * (cw + g), y + (i // cols) * (bh + g), cw, bh) for i in range(k)]
    bw = min((w - g * (cols - 1)) / cols, aspect * (h - g * (rows - 1)) / rows)
    bh = bw / aspect
    x0 = x if k == 1 else x + (w - (cols * bw + (cols - 1) * g)) / 2
    return [(x0 + (i % cols) * (bw + g), y + (i // cols) * (bh + g), bw, bh) for i in range(k)]


def panel_aspect(n: int, region: tuple, aspect: str = "16:9") -> float:
    """A panel's viewBox aspect: its HOME CELL's (the page's default layout over its region), so the home layout FILLS
    the region - the line builder draws at any viewBox width (its plot runs L..W-R), and the panel's viewBox is
    `panel_view_w` x (560 + its sub band). A quad's cell and the whole region have nearly one aspect, so a quad
    panel growing to the page fills it too. A row's cell is narrower than the region: since P69 T8c a landscape box of
    another aspect is the same chart RE-LAID OUT at that width (`panel_layout`'s `fill`), so a lone panel spans it."""
    cell = panel_cells(default_panel_layout(n, aspect), n, region)[0]
    return cell[2] / cell[3]


def panel_view_w(a: float) -> float:
    """A landscape panel's viewBox width for aspect `a`: its height is the line builder's 560 plus its sub band."""
    return a * (LAND_VIEWBOX[1] + PANEL_SUB_U)


def panel_home_boxes(n: int, region: tuple, aspect: str = "16:9") -> list[tuple]:
    """Every panel's HOME box: the default layout, every panel active."""
    # the home cells ARE of the panel aspect, so both laws agree; the engine keeps T8b's arithmetic for them, to the bit
    return panel_layout(default_panel_layout(n, aspect), n, region, panel_aspect(n, region, aspect), fill=False)


def _panels_region(spec: dict, chart: dict, aspect: str, floor: float | None = None) -> tuple:
    """The region a panels page lays its panels in, stage px: its chart box - which a FULL-STAGE 16:9 page widens to
    the stage's safe right edge (a panels page keeps no end-tag margin of its own: every panel carries its own) and
    stops PANEL_FLOOR_AIR over its `floor` (the anchored caption's strip, or the long form's first ink under the
    chart): a line page raises its ticks over that strip, and a panel's ticks are inside its box."""
    w, h = chart["w"], chart["h"]
    if aspect == "16:9" and full_stage(spec, aspect):
        w = LAND_PHONE_SAFE_RIGHT * STAGE_PX["16:9"][0] - chart["x"]
        f = CAPTION_ANCHOR["16:9"][1] if floor is None else floor
        h = min(h, f - PANEL_FLOOR_AIR - chart["y"])
    return (chart["x"], chart["y"], w, h)


def _panel_plot(box: tuple, spec_panel: dict, band: float = 0.0, page: dict | None = None) -> dict:
    """One panel's plot in stage px: the line builder's own margins inside the panel's box (its viewBox fills it).
    P72 T47: `band` > 0 - a page drawn in the phone layout - stands the plot under that band (rendered px), its right
    margin holding its end tag (`longform_panel_right_u`)."""
    x, y, w, h = box
    s = (h - band) / LAND_VIEWBOX[1] if band > 0 else h / (LAND_VIEWBOX[1] + PANEL_SUB_U)   # px per unit
    top = band / s if band > 0 else PANEL_SUB_U
    if (spec_panel or {}).get("builder") == PANEL_BARS:   # P69 T8d: the bars builder's plot - its tick rules' own extent
        vw, l_u, (t_u, b_u) = w / s, PANEL_BARS_PLOT["L"], PANEL_BARS_PLOT["TB"]   # (gutter less 20, to the viewBox's edge)
        return _box(x + l_u * s, y + (top + t_u) * s, (vw - l_u) * s, (b_u - t_u) * s)
    vw, l_u, r_u = w / s, LAND_PLOT["L"] * LAND_VIEWBOX[0], LAND_PLOT["R"] * LAND_VIEWBOX[0]
    if band > 0 and page is not None:
        r_u = longform_panel_right_u(page, spec_panel or {}, s)
    return _box(x + l_u * s, y + (top + LAND_PLOT["T"] * LAND_VIEWBOX[1]) * s,
                (vw - l_u - r_u) * s, (LAND_PLOT["B"] - LAND_PLOT["T"]) * LAND_VIEWBOX[1] * s)


def panel_boxes(spec: dict, chart: dict, aspect: str, floor: float | None = None) -> list[dict]:
    """Each panel's HOME box and its plot, stage px, estimated from the page's chart box."""
    panels = spec.get(PANELS_KEY) or []
    region = _panels_region(spec, chart, aspect, floor)
    out = []
    for p, b in zip(panels, panel_home_boxes(len(panels), region, aspect)):
        out.append({"box": _box(*b), "plot": _panel_plot(b, p, panel_band(spec), spec) if aspect == "16:9" else
                    _box(b[0] + PORTRAIT_PLOT["L"], b[1] + PORTRAIT_PLOT["T"], b[2] - PORTRAIT_PLOT["L"] - PORTRAIT_PLOT["R"],
                         b[3] - PORTRAIT_PLOT["T"] - PORTRAIT_PLOT["B"])})
    return out


def _union(boxes: list[dict]) -> dict:
    x0, y0 = min(b["x"] for b in boxes), min(b["y"] for b in boxes)
    x1, y1 = max(b["x"] + b["w"] for b in boxes), max(b["y"] + b["h"] for b in boxes)
    return _box(x0, y0, x1 - x0, y1 - y0)


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
TAG_BOXES_KEY = "tag_boxes"   # P69 T6d: on a MEASURED full-stage page, each end tag at its drawn rect (the fixture's own)
TAG_INK_KEY = "tag_ink"       # REVIEW-P69-LANE-B-MERGE-4 MN3: ... and, on the entry, the tags those rects were measured for (`tag_ink`)
# P72 T15 (R26-253, R26-270): `page_boxes` carries EVERY text box the page writes, and `text_boxes` names them all.
BASIS_BOX = "basis"           # the basis label (`axes.ylabel`): as drawn on a measured page, else `basis_strip`'s estimate
BAR_NAMES_KEY = "bar_names"   # each bar's name as drawn, {x, y, w, h, lines} - a MEASURED page only (the wrap is the player's)
BASIS_LINE_PX = 36            # the estimate's one tick-label line where the page reports no measured x tick band
INK_KEYS = ("builder", "title", "sub", "source", "quiet_zone")
# Kept as a descriptive alias for callers that name the variant.  The fixture's
# actual key is the main lane's geometry key, ``16:9|full_stage``.
FULL_STAGE_VARIANT = "full_stage"
_PLAYER_TEMPLATE = _REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
_PLAYER_ENGINE = _REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
_PLAYER_SHA_CACHE: tuple[tuple[int, int, int, int], str] | None = None
# R26-235: a page's boxes are a function of its ink AND of the geometry that ink is drawn in. The ink
# is the entry's key (`page_ink_key`); the geometry is the ASPECT, which is the level the fixture has
# always been keyed at - and at 16:9 there are now TWO geometries, because a page the compiler stamps
# `full_stage` puts the same ink in `_landscape_full_boxes` instead of `_landscape_boxes`. So the
# geometry key gains the flag rather than the ink key: `16:9` and `16:9|full_stage` are measured
# separately and a page is served the one it is drawn in. (The flag stays OUT of `page_ink_key` for
# the reason R26-205 found the hard way: the key does not know the aspect, so a caller that stamps a
# page with the compiler's `ASPECT` unset and then asks at 9:16 would re-key every portrait page it
# has - `test_dock_over_build.py` caught exactly that. A KEY the aspect is already in cannot.)
FULL_STAGE_SUFFIX = f"|{FULL_STAGE_VARIANT}"


def box_key(spec: dict, aspect: str) -> str:
    """The fixture key this page's boxes are measured under: the aspect, plus the full-stage flag when
    this page takes the whole stage at it (R26-235). `9:16` and an unstamped 16:9 page are unchanged,
    so every entry measured before this row still answers for the page it measured."""
    return f"{aspect}{FULL_STAGE_SUFFIX}" if full_stage(spec, aspect) else aspect


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
    for k in (SOURCE_LINES_KEY, TITLE_STYLE_KEY):   # P71 T30: the two-line source and the capsule move boxes (keyed only when named)
        if spec.get(k):
            ink[k] = spec[k]
    if spec.get("builder") == PANELS:   # P69 T8b: the panel count lays the boxes out (keyed only here: every other key stands)
        ink["panels_n"] = len(spec.get(PANELS_KEY) or [])
        kinds = [str(p.get("builder") or PANEL_LINE) for p in spec.get(PANELS_KEY) or [] if isinstance(p, dict)]
        if PANEL_BARS in kinds:   # P69 T8d: a bars panel's plot is the bars builder's - keyed only when a page has one
            ink["panel_builders"] = kinds
    # Keep the absent-profile fingerprint byte-compatible; only an opted-in geometry is a new ink
    # variant.  A profile's value must still be keyed because it changes the chart/viewBox and boxes.
    readability = (spec.get("axes") or {}).get("readability")
    if readability is not None:
        ink["readability"] = readability
    for key in ("type_scale", "tag_form", "tag_room", "key", "key_px", "key_w", "key_h", "state_ink"):   # P69 T8: the long form's preset, end-tag form and (N2) its states' tag room move its boxes; T10: its key's names; M1: its states' key band
        if (spec.get("axes") or {}).get(key) is not None:
            ink[key] = spec["axes"][key]
    if "left_gutter" in (spec.get("axes") or {}):
        ink["left_gutter"] = spec["axes"]["left_gutter"]
    if ((spec.get("form") or {}).get("kind")) == "gauge":   # P70 T3: a gauge's plot is its capsules, not the bars' - keyed only on a gauge
        ink["form"] = "gauge" + (":h" if (spec.get("form") or {}).get("dir") == "h" else "")   # P72 T6: a lying capsule's plot is its own
    if isinstance(spec.get(SCHEMATIC_KEY), dict):   # P70 T2: no tick column and the tag - keyed only on a schematic page
        ink[SCHEMATIC_KEY] = True
    if isinstance(spec.get(Y2_KEY), dict):   # P71 T13: the right column's words and the data that sizes it - keyed only on a y2 page
        ink[Y2_KEY] = {"header": spec[Y2_KEY].get("header"), "unit": spec[Y2_KEY].get("unit"), "extent": y2_extent(spec)}
    blob = json.dumps(ink, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def tag_ink(spec: dict) -> list[list]:
    """REVIEW-P69-LANE-B-MERGE-4 MN3: the fingerprint of a page's END TAGS - `[label, name, last value]` for every live
    series that writes one, in the spec's order. The one measured thing the DATA moves: an end tag stands at its line's
    last value and reads its label, so `tag_boxes` (P69 T6d) are served only to a page whose tags match the ones they
    were measured for; `page_ink_key` stays the key for every other box. Pure.

    P69 fixture-H: a tag stands at its last value IN THE PAGE'S Y DOMAIN, so a DECLARED `axes.domain` is part of
    where it lands - Steel and Paper H draws the golden's own ink at `domain=80,277` (the born domain, held until its
    rescale), at `[95, 1138.74]` and at the auto domain, three tag geometries under one ink. A declared domain joins
    each tag's fingerprint as a fourth member; a page that declares none keeps the three-member fingerprint, so every
    entry measured before this row still answers for the page it measured."""
    domain = (spec.get("axes") or {}).get("domain")
    try:
        scale = [round(float(v), 6) for v in domain] if isinstance(domain, (list, tuple)) and len(domain) == 2 else None
    except (TypeError, ValueError):
        scale = [str(v) for v in domain]   # an unreadable declared domain still keys the tags apart; never dropped
    out = []
    for s in spec.get("series") or []:
        if not isinstance(s, dict) or s.get("muted"):
            continue
        label, name = str(s.get("label") or "").strip(), str(s.get("name") or "").strip()
        if not (label or name):
            continue
        pts = s.get("pts") or []
        last = pts[-1][1] if pts and isinstance(pts[-1], (list, tuple)) and len(pts[-1]) > 1 else None
        try:
            last = round(float(last), 6)
        except (TypeError, ValueError):
            last = None if last is None else str(last)
        out.append([label, name, last] + ([scale] if scale is not None else []))
    return out


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


def _fixture_document(path: Path | None = None) -> dict:
    """The decoded fixture document, including its player freshness marker."""
    p = Path(path or PAGE_BOXES_FIXTURE)
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return {}
    return _doc(str(p), mtime)


def _player_sha256() -> str | None:
    """Hash both player files once per file-mtime tuple, ignoring checkout line endings."""
    global _PLAYER_SHA_CACHE
    try:
        template = _PLAYER_TEMPLATE.stat()
        engine = _PLAYER_ENGINE.stat()
    except OSError:
        return None
    key = (template.st_mtime_ns, template.st_size, engine.st_mtime_ns, engine.st_size)
    if _PLAYER_SHA_CACHE is not None and _PLAYER_SHA_CACHE[0] == key:
        return _PLAYER_SHA_CACHE[1]
    try:
        template = _PLAYER_TEMPLATE.read_bytes().replace(b"\r\n", b"\n")
        engine = _PLAYER_ENGINE.read_bytes().replace(b"\r\n", b"\n")
        digest = hashlib.sha256(template + engine).hexdigest()
    except OSError:
        return None
    _PLAYER_SHA_CACHE = (key, digest)
    return digest


def _full_stage_fixture_is_fresh(path: Path | None = None) -> bool:
    marker = _fixture_document(path).get("player_sha256")
    current = _player_sha256()
    return isinstance(marker, str) and current is not None and marker == current


def _valid_full_stage_entry(entry: object, ink: str) -> bool:
    boxes = entry.get("boxes") if isinstance(entry, dict) else None

    def finite_real(value: object) -> bool:
        if not isinstance(value, Real) or isinstance(value, bool):
            return False
        try:
            return math.isfinite(value)
        except (OverflowError, TypeError):
            return False

    def valid_box(value: object) -> bool:
        if not isinstance(value, dict):
            return False
        if not all(dimension in value for dimension in ("x", "y", "w", "h")):
            return False
        return (finite_real(value["x"]) and finite_real(value["y"])
                and finite_real(value["w"]) and value["w"] >= 0
                and finite_real(value["h"]) and value["h"] >= 0)

    return (isinstance(entry, dict) and entry.get("ink") == ink
            and entry.get("full_stage") is True
            and isinstance(boxes, dict)
            and all(valid_box(boxes.get(key)) for key in BOX_KEYS))


def fixture(path: Path | None = None) -> dict:
    """builder -> aspect -> entry, from `assets/page-boxes.v1.json` (or `path`): ONE representative
    page per builder, the fallback for any page carrying that representative's ink."""
    return _section("builders", path)


def measured_pages(path: Path | None = None) -> dict:
    """ink key -> aspect -> entry: the pages a PROJECT's compiled timeline named, measured one by
    one (`measure_page_boxes.py --project`). A builder has one representative but an episode has as
    many pages as it writes titles, so the pages an episode actually compiles are keyed by ink."""
    return _section("pages", path)


def measured_profiles(path: Path | None = None) -> dict:
    """`<builder>|longform:<preset>` -> geometry -> entry: each profiled builder's representative measured under the
    long form at every preset (REVIEW-P69-LANE-B-MERGE-2 N3, `measure_page_boxes.build_profiles`)."""
    return _section("profiles", path)


def _profile_entry(ink: str, geometry: str) -> dict | None:
    """The `profiles` entry whose ink is this page's own in this geometry, or None."""
    for by_geometry in measured_profiles().values():
        got = by_geometry.get(geometry) if isinstance(by_geometry, dict) else None
        if isinstance(got, dict) and got.get("ink") == ink:
            return got
    return None


def _serves_other_tags(entry: dict, other: dict | None, spec: dict) -> bool:
    """True when `entry` measured end tags that are not this page's (`tag_ink`) while `other` - the same ink in the
    same geometry - measured exactly this page's. Pure."""
    if not isinstance(other, dict) or other is entry:
        return False
    own = tag_ink(spec)
    return entry.get(TAG_INK_KEY) is not None and entry.get(TAG_INK_KEY) != own and other.get(TAG_INK_KEY) == own


def _builder_entry(builder: str, geometry: str, ink: str) -> dict | None:
    """The builder representative's entry in this geometry. P69 T8d: a builder may file a SECOND representative
    (`<builder>+<shape>` - `panels+bars`, the mixed quad); the one whose ink is this page's answers, else the builder's
    own (as before, so every ink it never measured falls through exactly as it did)."""
    fx = fixture()
    own = fx.get(builder)
    own = own.get(geometry) if isinstance(own, dict) else None
    if isinstance(own, dict) and own.get("ink") == ink:
        return own
    for name in sorted(n for n in fx if n.startswith(builder + REPRESENTATIVE_SEP)):
        got = fx[name].get(geometry) if isinstance(fx[name], dict) else None
        if isinstance(got, dict) and got.get("ink") == ink:
            return got
    return own


def measured_entry(spec: dict, aspect: str) -> dict | None:
    """The fixture entry that measured THIS page's ink at this aspect, or None.

    The ink-keyed project page is tried first, then its builder representative. The entry is used
    only when its `ink` is this page's own, and only
    when it was measured in the GEOMETRY this page is drawn in (`box_key`: R26-235, a full-stage 16:9
    page lays out nothing like the same ink in the old landscape box, so the two are measured apart).
    An entry is also refused when its own `full_stage` flag disagrees with the key it is filed under -
    the fixture is a measurement, and a measurement that has to be reinterpreted is not one."""
    key = page_ink_key(spec)
    full = full_stage(spec, aspect)
    geometry = box_key(spec, aspect)
    page_entries = measured_pages().get(key)
    entry = page_entries.get(geometry) if isinstance(page_entries, dict) else None
    builder_entry = _builder_entry(str(spec.get("builder")), geometry, key)   # P69 T8d: or its second representative
    if not (isinstance(builder_entry, dict) and builder_entry.get("ink") == key):
        builder_entry = _profile_entry(key, geometry) or builder_entry   # N3: a longform representative, by its ink
    if not isinstance(entry, dict):
        entry = builder_entry
    elif _serves_other_tags(entry, builder_entry, spec):
        # P69 fixture-H: a project page and the builder's representative can share an INK and still draw their tags
        # (and their data) apart - H draws the golden's own ink in a declared domain. The entry measured on THIS
        # page's own tags is the one that measured this page; the other one's rects are another page's.
        entry = builder_entry
    if full and not _valid_full_stage_entry(entry, key):
        # A project-specific page may be malformed while its builder
        # representative is still a valid measured fallback.  Validate both
        # candidates before serving either one.
        entry = builder_entry
        if not _valid_full_stage_entry(entry, key):
            return None
    if not isinstance(entry, dict) or entry.get("ink") != key or bool(entry.get("full_stage")) != full:
        return None
    return entry


def measured_boxes(spec: dict, aspect: str) -> dict | None:
    """The player's own boxes for THIS page's ink, or None when nothing on file measured it."""
    entry = measured_entry(spec, aspect)
    boxes = (entry or {}).get("boxes")
    if not isinstance(boxes, dict) or not all(k in boxes for k in BOX_KEYS):
        return None
    out = {k: dict(boxes[k]) for k in BOX_KEYS}
    if isinstance(boxes.get(KEY_BOX), dict):   # P69 T10: a longform page's key rail, when it was measured with one
        out[KEY_BOX] = dict(boxes[KEY_BOX])
    if isinstance(entry.get(SCHEMATIC_BOX), dict):   # P70 T2: a schematic's tag, as drawn (beside the six, as panels are)
        out[SCHEMATIC_BOX] = dict(entry[SCHEMATIC_BOX])
    if isinstance(entry.get(Y2_BOX), dict):   # P71 T13: the right axis's words, as drawn
        out[Y2_BOX] = dict(entry[Y2_BOX])
    if isinstance(entry.get(BASIS_BOX), dict):   # P72 T15 (R26-253): the basis label, as drawn
        out[BASIS_BOX] = dict(entry[BASIS_BOX])
    if isinstance(entry.get(BAR_NAMES_KEY), list):   # P72 T15 (R26-270): each bar's name, as drawn
        out[BAR_NAMES_KEY] = [dict(b) for b in entry[BAR_NAMES_KEY] if isinstance(b, dict)]
    if (isinstance(boxes.get(TAG_BOXES_KEY), list) and boxes[TAG_BOXES_KEY]   # P69 T6d: its end tags, each as drawn -
            and entry.get(TAG_INK_KEY) == tag_ink(spec)):                      # MN3: only for the tags they were drawn for
        out[TAG_BOXES_KEY] = [dict(b) for b in boxes[TAG_BOXES_KEY] if isinstance(b, dict)]
    if isinstance(entry.get(PANELS_KEY), list) and entry[PANELS_KEY]:   # P69 T8b: each panel's home box and plot, as drawn
        out[PANELS_KEY] = [{k: dict(v) for k, v in p.items() if isinstance(v, dict)} for p in entry[PANELS_KEY] if isinstance(p, dict)]
    return out


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


def basis_strip(plot: dict, axis: dict | None) -> dict:
    """The basis label's LINE: the plot's top strip, one tick-label line high (the measured x tick band's height, else
    BASIS_LINE_PX), across the plot's width - where `page_boxes` folds the label into the plot, and so the label's box on
    a page nothing measured. Measured on the served full-stage page 2026-09-22: the label (151, 208, 435 x 33) inside
    the strip (151, 208, 947 x 36). Pure."""
    h = ((axis or {}).get("x") or {}).get("h") or BASIS_LINE_PX
    return {"x": plot["x"], "y": plot["y"], "w": plot["w"], "h": h}


def text_boxes(boxes: dict) -> list[tuple[str, dict]]:
    """P72 T15: EVERY page text box `page_boxes` carries, as (name, stage-px rect), in one order - the title, the sub,
    the source line, the badge rail, the key rail, the basis label, both tick bands, the end tags as drawn (else the
    names' column), the schematic's tag, the right axis's words, each bar's name. The names are the placer's own
    findings' names. A box that is absent or empty is left out. Pure."""
    ok = lambda b: isinstance(b, dict) and b.get("w", 0) > 0 and b.get("h", 0) > 0   # noqa: E731
    out = [(k, dict(boxes[k])) for k in ("title", "sub", "source", "rail", KEY_BOX) if ok(boxes.get(k))]
    if ok(boxes.get(BASIS_BOX)):
        out.append(("the basis label", dict(boxes[BASIS_BOX])))
    axis = boxes.get("axis") or {}
    out += [(f"the {k} axis", dict(axis[k])) for k in ("x", "y") if ok(axis.get(k))]
    if boxes.get(TAG_BOXES_KEY):
        out += [("an end tag", dict(b)) for b in boxes[TAG_BOXES_KEY] if ok(b)]
    elif ok(boxes.get(TAGS_KEY)):
        out.append(("the end names", dict(boxes[TAGS_KEY])))
    for key, name in ((SCHEMATIC_BOX, "the schematic tag"), (Y2_BOX, "the right axis")):
        if ok(boxes.get(key)):
            out.append((name, dict(boxes[key])))
    out += [("a bar name", {k: b[k] for k in ("x", "y", "w", "h")}) for b in boxes.get(BAR_NAMES_KEY) or [] if ok(b)]
    return out


# R26-270: a bar's name - on two lines where lpWrapBarLabel wrapped it - stands under the plot, above the source foot and
# (at 16:9 on a full-stage page) level with the anchored caption's band. Nothing measured it against either. A name may
# sit flush against either; a pixel into one is a finding.


def bar_name_findings(boxes: dict) -> list[str]:
    """R26-270 (s106 - advice, never a refusal): one WARN, with its numbers, per bar name whose drawn box runs into the
    page's source line or into the anchored caption's band. [] on a page with no measured names. Pure."""
    out = []
    bands = [("the source line", boxes.get("source")), ("the caption band", boxes.get("caption_anchor"))]
    for b in boxes.get(BAR_NAMES_KEY) or []:
        if not isinstance(b, dict):
            continue
        for what, r in bands:
            if not isinstance(r, dict):
                continue
            dx = min(b["x"] + b["w"], r["x"] + r["w"]) - max(b["x"], r["x"])
            dy = min(b["y"] + b["h"], r["y"] + r["h"]) - max(b["y"], r["y"])
            if dx > 0 and dy > 0:
                lines = int(b.get("lines") or 1)
                out.append(f"a bar name [{b['x']}, {b['y']}, {b['w']}, {b['h']}] ({lines} line{'s' if lines > 1 else ''}) "
                           f"runs {dy:.0f} px into {what} [{r['x']}, {r['y']}, {r['w']}, {r['h']}] - shorten the name, "
                           "or give the page's foot room (R26-270)")
    return out


def page_boxes(spec: dict, aspect: str = "16:9") -> dict:
    """Where this page puts its ink, in STAGE pixels (E45 §1).

    Keys: ``stage``/``safe``/``caption_anchor`` (the frame's own bands) and ``title``/``sub``/
    ``chart``/``plot``/``source``/``rail`` (the page's), each ``{x, y, w, h}``; ``quiet_zone``
    passes the spec's declared side through. ``plot`` is the DATA box plus the ink that lives
    inside it - the basis label above it (``axes.ylabel``) and the x tick labels below the axis -
    because a card over either of them covers the chart just as surely. P72 T15: ``basis`` (the basis label's own box - as
    drawn on a measured page, else `basis_strip`) and, on a measured page, ``bar_names`` (each bar's name as drawn, with
    the ``lines`` it took); `text_boxes` names every text box the page carries.

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
    floor = boxes.pop("_floor", None)
    if spec.get("builder") == PANELS:   # P69 T8b: the chart is the panels' box (to the safe edge); the plot every panel's box
        rx, ry, rw, _rh = _panels_region(spec, boxes["chart"], aspect)
        boxes["chart"] = _box(rx, ry, rw, boxes["chart"]["h"])
        boxes[PANELS_KEY] = panel_boxes(spec, boxes["chart"], aspect, floor)
        boxes["plot"] = _union([p["box"] for p in boxes[PANELS_KEY]])
        boxes.pop(TAGS_KEY, None)   # no page-wide end-tag column: every panel's tags stand inside its own box
    # P70 T9: a page that made room for a chapter pill was never measured with its room - its estimate stands
    measured = None if spec.get(CHAPTER_ROOM_KEY) else measured_boxes(spec, aspect)
    if measured:                      # the player's own numbers for this ink win over every estimate above
        tags = boxes.get(TAGS_KEY)    # ... except the end tag column, which the fixture does not measure as a column
        boxes.update(measured)
        drawn = boxes.pop(TAG_BOXES_KEY, None)
        if tags is not None:
            boxes[TAGS_KEY] = tags
            if drawn:   # P69 T6d: ... and beside it the tags AS DRAWN, each at its rect (the stamp's ring fits around these)
                boxes[TAG_BOXES_KEY] = drawn
        boxes.update(measured_room(spec, aspect))   # E65: the plot's empty room and the axis bands travel with them
        if spec.get("builder") == "tiers":   # the tier bands are a law over the PLOT: re-cut them on the measured one
            boxes["bands"] = tier_bands(boxes["plot"], len(spec.get("tiers") or []))
        if spec.get("builder") == PANELS and not measured.get(PANELS_KEY):   # the panels re-cut on the measured chart
            boxes[PANELS_KEY] = panel_boxes(spec, boxes["chart"], aspect, floor)
    if isinstance(spec.get(SCHEMATIC_KEY), dict) and not isinstance(boxes.get(SCHEMATIC_BOX), dict):
        boxes[SCHEMATIC_BOX] = schematic_tag_box(boxes["plot"])   # P70 T2: s109 (1)'s tag, estimated where it is not measured
    if isinstance(spec.get(Y2_KEY), dict) and not isinstance(boxes.get(Y2_BOX), dict):   # P71 T13: the right axis, estimated:
        y2box = y2_axis_box(spec, boxes["plot"], aspect)                                  # its column comes OUT of the plot
        plot = boxes["plot"]
        boxes["plot"] = _box(plot["x"], plot["y"], max(0.0, plot["w"] - y2box["w"]), plot["h"])
        boxes[Y2_BOX] = dict(y2box, x=boxes["plot"]["x"] + boxes["plot"]["w"])
    if (spec.get("axes") or {}).get("ylabel") and not isinstance(boxes.get(BASIS_BOX), dict):   # P72 T15: the basis
        boxes[BASIS_BOX] = basis_strip(boxes["plot"], boxes.get("axis"))                         # label, estimated
    sx, sy, sw, sh = SAFE_BOX[aspect]
    cx, cy, cw, ch = CAPTION_ANCHOR[aspect]
    out = {"aspect": aspect, "stage": _box(0, 0, w_s, h_s), "safe": _box(sx, sy, sw, sh),
           "caption_anchor": _box(cx, cy, cw, ch), "quiet_zone": spec.get("quiet_zone"),
           "measured": bool(measured), **boxes}
    if full_stage(spec, aspect):
        out[FULL_STAGE_BANDS_KEY] = _full_stage_bands(w_s, h_s)
    return out


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
        return "share" if series.get("peel") is not None or share_solid(series) else "treemap"   # P69 T48: a donut / 3D pie is a share page
    return None


# P69 T10c (the operator, 2026-09-22, on row 7's thrown Bravos card: "Those charts still seem tough to read to me" and
# "Evidence cards that are using charts need to use the whole card and use bigger fonts and thicker lines"): the CARD
# profile. `chart_card.render_card` rendered the FULL ledger page and shrank it to the dock's width, so every word
# shrank with the card (a 26 px tick read at 9 px on row 7's 653-px card). Under `readability: card` the page is laid
# out FOR THE CARD'S OWN DISPLAYED BOX (`axes.card_w` x `axes.card_h`, stage px) - drawn on the stage at the card's
# scale (CARD K = stage width / card width) so that, shown at the card's size, every size below is what it says:
#   CARD_TYPE_PX   every word (title, ticks, end badges, values, the source) at this many DISPLAYED px, the E99 s90
#                  phone floor at the card's size: 12 phone px on a 16:9 frame played 390 px wide is 12 x 1920 / 390 =
#                  59.08 stage px (test_longform_profile.PHONE_FLOOR / PHONE_W) - the floor itself (at 60 the title of
#                  row 7's card wraps by 4 px, and a second title line costs the plot a fifth of the card);
#   CARD_STROKE_X  every line and its tip at this many times the full page's own stroke, as displayed;
#   CARD_PAD_PX    the card's only margin (displayed px): the plot runs edge to edge inside it - no page margins, no
#                  caption bands, no sub, no y label, no badge rail, no key;
# end tags reduced to their short badge (the value, in its line's ink), the x ticks to the two ends (the minor ones
# dropped), the source to its first clause on one line - or none, when it will not fit, or when the plot would keep less
# than its room (the engine's LP_CARD.PLOT_MIN, or a line card's end badges stacked a line apart). The card keeps its
# TITLE and its NUMBER.
# It is the long form's look (the flat ground, the panel, Inter) - a card of a long-form page. NOT a row option: only
# `chart_card` sets it, and a row that names `readability=card` is refused as an unknown profile.
CARD = "card"
CARD_BUILDERS = ("dense-line", "story")
CARD_PHONE_FLOOR, CARD_PHONE_W = 12.0, 390   # E99 s90's floor, measured the T17 way (phone px = stage px x 390 / 1920)
CARD_TYPE_PX = CARD_PHONE_FLOOR * 1920 / CARD_PHONE_W   # 59.08: the floor itself (the engine's LP_CARD.TYPE_PX)
CARD_STROKE_X = 2.0
CARD_PAD_PX = 8.0   # the engine's LP_CARD.PAD_PX
CARD_SOURCE_CUTS = (" - ", "; ", ", ", " (")   # the source's first clause ends at the first of these
# THE NAMES A VALUE CANNOT CARRY (the parent's frame read of the first card, 2026-09-23: "+21%" grey and "+21%" blue
# "are indistinguishable except by colour - a viewer cannot tell the S&P from mega-cap"). On a card the end-tag
# shortening stops at the BADGE for every tag whose value another tag also shows: the value keeps the floor and a SHORT
# NAME rides it as the badge's chip - the series' own inline badge label (the page's key word for that line: E99 s90),
# cut to its first word when the first words still tell the lines apart. Never an invented word. The name's size is
# FITTED so the widest named tag takes at most CARD_TAG_ROOM of the card (the plot keeps the rest), never under
# CARD_NAME_MIN of the floor; a value no other tag shows names its line already (with its ink) and stays a value.
CARD_TAG_ROOM = 0.5
CARD_NAME_MIN = 0.5
CARD_TAG_EM = (0.68, 0.64)   # the engine's LP_LONGFORM.TAG_EM (NAME, CHIP): ems per character of a value / a chip
CARD_CHIP_DX_PX = 4.0        # the chip's gap after its value, displayed px (the engine's CHIP_DX_PX 12 at the card's ~3x)


def card_names(page: dict) -> dict[int, str]:
    """{series index: short name} for every live line whose end value another line's also shows. Pure."""
    live = [(i, s) for i, s in enumerate(page.get("series") or []) if isinstance(s, dict) and not s.get("muted")]
    vals = [str(s.get("label") or "").strip() for _i, s in live]
    dup = {v for v in vals if v and vals.count(v) > 1}
    if not dup:
        return {}
    by_col = {BADGE_ACCENT_COL.get(b.get("accent")): str(b.get("label") or "").strip()
              for b in page.get("badges") or [] if isinstance(b, dict) and b.get("inline")}
    full = {i: (by_col.get(s.get("color")) or str(s.get("name") or "").strip()) for i, s in live
            if str(s.get("label") or "").strip() in dup}
    out = {}
    for v in dup:
        group = {i: n for i, n in full.items() if str(page["series"][i].get("label") or "").strip() == v}
        first = {i: (n.split() or [""])[0] for i, n in group.items()}
        use = first if len(set(first.values())) == len(first) and all(first.values()) else group
        out.update(use)
    return {i: n for i, n in out.items() if n}


def card_chip_px(page: dict, names: dict[int, str], card_w: float) -> float:
    """The short names' size in DISPLAYED px: the floor, or less so the widest named tag fits CARD_TAG_ROOM of the
    card - never under CARD_NAME_MIN of the floor."""
    ev, ec = CARD_TAG_EM
    room = CARD_TAG_ROOM * float(card_w)
    fit = min((room - len(str(page["series"][i].get("label") or "")) * ev * CARD_TYPE_PX - CARD_CHIP_DX_PX) / (len(n) * ec)
              for i, n in names.items())
    return round(max(CARD_NAME_MIN * CARD_TYPE_PX, min(CARD_TYPE_PX, fit)), 2)


def card_floor_px(stage_w: int = 1920) -> float:
    """E99 s90's phone floor in DISPLAYED stage px: the size that reads 12 px on a 390-px-wide phone."""
    return CARD_PHONE_FLOOR * stage_w / CARD_PHONE_W


def card_error(page: dict, card_w: float, card_h: float, aspect: str | None = "16:9") -> str | None:
    """Can THIS page be drawn as a card of this displayed box? The message, or None. Pure."""
    builder = str(page.get("builder") or "?")
    if builder not in CARD_BUILDERS:
        return (f"readability={CARD!r} is drawn by the {' and '.join(CARD_BUILDERS)} builders (a line card and a bars "
                f"card); this page uses {builder!r}")
    if aspect not in (None, "16:9"):
        return f"readability={CARD!r} is a 16:9 page's card (the long form's); a {aspect} card keeps its own page"
    if not (float(card_w) > 0 and float(card_h) > 0):
        return f"readability={CARD!r} needs the card's displayed box in stage px (card_w, card_h); got {card_w!r} x {card_h!r}"
    return None


def card_source(source: str, card_w: float, stage_w: int = 1920) -> str:
    """The card's one short source line: the source's first clause, when it fits one line inside the card's margins at
    CARD_TYPE_PX - else nothing (the page the card becomes carries the whole citation)."""
    text = str(source or "").strip()
    for cut in CARD_SOURCE_CUTS:
        if cut in text:
            text = text.split(cut, 1)[0].strip()
    k = stage_w / float(card_w)
    room = stage_w - 2 * CARD_PAD_PX * k
    return text if text and longform_text_px(text, "source", CARD_TYPE_PX * k) <= room else ""


def apply_card(page: dict, card_w: float, card_h: float, stage_w: int = 1920) -> dict:
    """Stamp the CARD profile on a page spec, in place (returned for chaining): the displayed box, the value-only end
    tags, the two end x ticks, no sub / y label / badges / key, the short source. ValueError when it cannot be one."""
    err = card_error(page, card_w, card_h)
    if err:
        raise ValueError(err)
    axes = page.setdefault("axes", {})
    for key in ("type_scale", "tag_form", "tag_room", "key", "key_px", "ylabel", "card_chip_px"):
        axes.pop(key, None)
    axes.update({"readability": CARD, "card_w": round(float(card_w), 2), "card_h": round(float(card_h), 2)})
    names = card_names(page) if page.get("builder") == "dense-line" else {}   # read before the badges are cleared
    if page.get("builder") == "dense-line":
        axes["tag_form"] = "value"
    if names:   # the shortening stops at the badge: the value and its short name
        axes["tag_form"] = "badge"
        axes["card_chip_px"] = card_chip_px(page, names, card_w)
        for i, n in names.items():
            page["series"][i]["card_name"] = n
    xt = axes.get("xticks")
    if isinstance(xt, list) and len(xt) > 2:
        axes["xticks"] = [xt[0], xt[-1]]
    page["sub"] = ""
    page["badges"] = []
    page["source"] = card_source(page.get("source") or "", card_w, stage_w)
    return page


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
